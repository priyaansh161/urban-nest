# Staging decor shared by the room builds (Nov 2026): no dots, no product links, just the props that make a room
# look lived in (trays, plants, vases, slippers...). Everything is built from code: lathed ceramics, leaf strips,
# small generated images. Nothing here is lightmapped; the props are lit live in the viewer like the products, and
# they stand in the room during the bake so their shadows land in the lightmaps of the surfaces under them.
import bpy, bmesh, math, os, random
import numpy as np
from mathutils import Vector, Matrix

_IMG = {}


def img(name, rgb, out_dir, alpha=None):
    """A packed PNG from an HxWx3 sRGB array (0..1); alpha optional HxW."""
    h, w = rgb.shape[:2]
    a = np.ones((h, w, 4), np.float32); a[..., :3] = rgb
    if alpha is not None: a[..., 3] = alpha
    im = bpy.data.images.new(name, w, h, alpha=alpha is not None)
    im.colorspace_settings.name = 'Non-Color'          # the numbers are written as they are (already sRGB)
    im.pixels.foreach_set(a[::-1].ravel())               # row 0 = top of the picture
    path = os.path.join(out_dir, name + '.png'); im.filepath_raw = path; im.file_format = 'PNG'; im.save()
    im2 = bpy.data.images.load(path); im2.pack(); _IMG[name] = im2
    return im2


def mat(name, color, rough=0.5, metal=0.0, image=None, alpha_blend=False, transmission=0.0, sheen=0.0, normal=None, nstrength=1.0):
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = tuple(color[:3]) + (1,)
    b.inputs['Roughness'].default_value = rough; b.inputs['Metallic'].default_value = metal
    if transmission: b.inputs['Transmission Weight'].default_value = transmission
    if sheen: b.inputs['Sheen Weight'].default_value = sheen
    if image is not None:
        t = m.node_tree.nodes.new('ShaderNodeTexImage'); t.image = image
        m.node_tree.links.new(t.outputs['Color'], b.inputs['Base Color'])
        if alpha_blend:
            m.node_tree.links.new(t.outputs['Alpha'], b.inputs['Alpha'])
            m.blend_method = 'CLIP' if hasattr(m, 'blend_method') else None
    if normal is not None:                               # surface relief (weave, grain, ribs) that catches the light
        t = m.node_tree.nodes.new('ShaderNodeTexImage'); t.image = normal
        nm = m.node_tree.nodes.new('ShaderNodeNormalMap'); nm.inputs['Strength'].default_value = nstrength
        m.node_tree.links.new(t.outputs['Color'], nm.inputs['Color']); m.node_tree.links.new(nm.outputs['Normal'], b.inputs['Normal'])
    m.use_backface_culling = False
    return m


def normal_img(name, height, out_dir, strength=1.0):
    """An OpenGL normal map (tiling) from an HxW height field, 0..1 (row 0 = top of the picture)."""
    dx = (np.roll(height, -1, 1) - np.roll(height, 1, 1)) * strength
    dy = (np.roll(height, 1, 0) - np.roll(height, -1, 0)) * strength      # +y up the picture
    n = np.stack([-dx, -dy, np.ones_like(height)], -1); n /= np.linalg.norm(n, axis=-1, keepdims=True)
    return img(name, n * 0.5 + 0.5, out_dir)


def blur(a, r):
    """Box blur (wrapping) of an HxW array, twice: soft, cheap, tiling."""
    for ax in (0, 1):
        for _ in range(2):
            a = sum(np.roll(a, s, ax) for s in range(-r, r + 1)) / (2 * r + 1)
    return a


def link(o):
    bpy.context.scene.collection.objects.link(o); return o


def mesh_obj(name, verts, faces, m, uvs=None, smooth=True):
    me = bpy.data.meshes.new(name); me.from_pydata([tuple(v) for v in verts], [], [tuple(f) for f in faces])
    if uvs is not None:
        uv = me.uv_layers.new(name='UVMap')
        for p in me.polygons:
            for li, vi in zip(p.loop_indices, p.vertices): uv.data[li].uv = uvs[vi]
    if smooth: me.shade_smooth()
    me.materials.append(m)
    return link(bpy.data.objects.new(name, me))


def lathe(name, prof, m, seg=40, cap=True, u_scale=1.0):
    """Revolve a profile [(r, z), ...] (bottom to top) round z. UV: u round, v along the profile."""
    n = len(prof); V, F, UV = [], [], []
    L = np.concatenate([[0], np.cumsum([math.dist(prof[i], prof[i + 1]) for i in range(n - 1)])]); L = L / max(L[-1], 1e-6)
    for s in range(seg + 1):
        a = 2 * math.pi * s / seg
        for i, (r, z) in enumerate(prof): V.append((r * math.cos(a), r * math.sin(a), z)); UV.append((s / seg * u_scale, L[i]))
    for s in range(seg):
        for i in range(n - 1):
            p = s * n + i; F.append((p, p + n, p + n + 1, p + 1))
    o = mesh_obj(name, V, F, m, UV)
    bm = bmesh.new(); bm.from_mesh(o.data); bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-6); bm.to_mesh(o.data); bm.free()
    return o


def box(name, loc, dim, m, bevel=0.0, segs=2):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc); o = bpy.context.object; o.name = name; o.scale = dim
    bpy.ops.object.transform_apply(scale=True)
    if bevel:
        md = o.modifiers.new('B', 'BEVEL'); md.width = bevel; md.segments = segs
        bpy.ops.object.modifier_apply(modifier='B')
    o.data.materials.append(m); return o


def cyl(name, loc, r, h, m, seg=24):
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=h, vertices=seg, location=loc); o = bpy.context.object; o.name = name
    o.data.materials.append(m); return o


def tube(name, pts, radii, m, seg=8):
    """A tube along points with a radius per point (stems, trunks, twigs)."""
    pts = [Vector(p) for p in pts]; V, F = [], []
    for i, p in enumerate(pts):
        t = (pts[min(i + 1, len(pts) - 1)] - pts[max(i - 1, 0)]).normalized()
        a = t.orthogonal().normalized(); b = t.cross(a)
        for s in range(seg):
            ang = 2 * math.pi * s / seg; V.append(p + radii[i] * (math.cos(ang) * a + math.sin(ang) * b))
    for i in range(len(pts) - 1):
        for s in range(seg):
            F.append((i * seg + s, i * seg + (s + 1) % seg, (i + 1) * seg + (s + 1) % seg, (i + 1) * seg + s))
    return mesh_obj(name, V, F, m)


def join(objs, name):
    objs = [o for o in objs if o]
    bpy.ops.object.select_all(action='DESELECT')
    for o in objs: o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]; bpy.ops.object.join()
    o = bpy.context.object; o.name = name; return o


def place(o, loc, rz=0.0):
    o.rotation_euler.z = rz; o.location = loc
    bpy.ops.object.select_all(action='DESELECT'); o.select_set(True); bpy.context.view_layer.objects.active = o
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True); return o


def leaf_strip(V, F, UV, base, up, side, length, width, n=8, curl=0.0, twist=0.0, droop=0.0, shape=None):
    """Append one leaf: a strip from base along `up`, bending by `droop` toward `side`'s normal. UV u across, v along."""
    up = Vector(up).normalized(); side = Vector(side).normalized(); nrm = up.cross(side).normalized()
    shape = shape or (lambda t: math.sin(math.pi * min(1, t * 1.05)) ** 0.7)
    o = len(V)
    for i in range(n + 1):
        t = i / n
        c = Vector(base) + up * length * t + nrm * droop * length * t * t
        tw = twist * t; sd = side * math.cos(tw) + nrm * math.sin(tw)
        w = width * shape(t) / 2
        for k, u in ((-1, 0.0), (0, 0.5), (1, 1.0)):
            V.append(c + sd * w * k + nrm * curl * width * (abs(k) - 0.5)); UV.append((u, t))
    for i in range(n):
        p = o + i * 3
        F.append((p, p + 1, p + 4, p + 3)); F.append((p + 1, p + 2, p + 5, p + 4))


def disc_leaf(V, F, UV, centre, nrm, r, seg=8, tilt_axis=None):
    """A round eucalyptus-like leaf, slightly cupped."""
    nrm = Vector(nrm).normalized(); a = nrm.orthogonal().normalized(); b = nrm.cross(a)
    o = len(V); V.append(Vector(centre) - nrm * r * 0.08); UV.append((0.5, 0.5))
    for s in range(seg):
        ang = 2 * math.pi * s / seg
        V.append(Vector(centre) + r * (math.cos(ang) * a + math.sin(ang) * b) + nrm * r * 0.06); UV.append((0.5 + 0.5 * math.cos(ang), 0.5 + 0.5 * math.sin(ang)))
    for s in range(seg): F.append((o, o + 1 + s, o + 1 + (s + 1) % seg))


def noise_img(h, w, base, amp, seed, blobs=8):
    rng = np.random.default_rng(seed)
    low = rng.normal(0, 1, (max(2, h // blobs), max(2, w // blobs)))
    low = np.kron(low, np.ones((blobs, blobs)))[:h, :w]
    for ax in (0, 1):                                       # soften the blocks: a box blur the size of a blob, twice
        for _ in range(2):
            c = np.cumsum(np.pad(low, [(blobs, blobs) if a == ax else (0, 0) for a in (0, 1)], mode='wrap'), axis=ax)
            low = ((np.take(c, range(blobs * 2, c.shape[ax]), axis=ax) - np.take(c, range(0, c.shape[ax] - blobs * 2), axis=ax)) / (2 * blobs))
            low = np.take(low, range(0, (h, w)[ax]), axis=ax)
    a = np.ones((h, w, 3)) * np.array(base)[None, None, :]
    return np.clip(a + amp * low[..., None] + rng.normal(0, amp * 0.25, (h, w, 1)), 0, 1)
