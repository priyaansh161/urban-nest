# Vase fillers (a vase is never shown empty): white calla lilies with silver-dollar eucalyptus.
# Real shapes instead of blobs: a rolled spathe that wraps at the base and opens to a pointed lip, a yellow
# spadix, smooth tapering stems, and round cupped eucalyptus leaves in opposite pairs on arching sprigs.
# Base at the origin, 0.44 m tall (the viewer scales it to each vase).
#   blender -b -P make_flowers.py -- <out dir>     -> flowers.glb (tall bunch), flowers_small.glb (cistern vase)
import bpy, sys, os, math, random, tempfile
import numpy as np
from mathutils import Vector, Matrix
out = sys.argv[sys.argv.index('--') + 1]
TMP = tempfile.mkdtemp(prefix='flowers_')

def pmat(name, color, rough, img=None):
    m = bpy.data.materials.new(name); m.use_nodes = True; b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = color; b.inputs['Roughness'].default_value = rough
    if img:
        t = m.node_tree.nodes.new('ShaderNodeTexImage'); t.image = img; m.node_tree.links.new(t.outputs['Color'], b.inputs['Base Color'])
    return m

def spathe_img():
    """Calla spathe colour along its length: green at the stem, white by a third of the way up."""
    H = 128; v = np.linspace(0, 1, H)
    k = np.clip((v - 0.02) / 0.30, 0, 1); k = k * k * (3 - 2 * k)
    col = np.array([0.42, 0.58, 0.26])[None, :] * (1 - k[:, None]) + np.array([0.97, 0.96, 0.92])[None, :] * k[:, None]
    arr = np.ones((H, 4, 4), dtype=np.float32); arr[..., :3] = col[:, None, :]
    img = bpy.data.images.new('spathe', 4, H, alpha=False); img.pixels.foreach_set(arr.ravel())
    p = os.path.join(TMP, 'spathe.png'); img.filepath_raw = p; img.file_format = 'PNG'; img.save()
    i2 = bpy.data.images.load(p); i2.pack(); return i2

def link(o): bpy.context.scene.collection.objects.link(o); return o

def mesh_obj(name, verts, faces, m, uvs=None):
    me = bpy.data.meshes.new(name); me.from_pydata(verts, [], faces)
    if uvs:
        uv = me.uv_layers.new(name='UVMap')   # same name as the converted stems' UVs, so joining keeps one map
        for poly in me.polygons:
            for li, vi in zip(poly.loop_indices, poly.vertices): uv.data[li].uv = uvs[vi]
    me.materials.append(m); o = link(bpy.data.objects.new(name, me))
    for p in me.polygons: p.use_smooth = True
    return o

def stem(name, pts, r0, r1, m):
    """Tapering tube along a polyline (a curve, converted to mesh at the end)."""
    cu = bpy.data.curves.new(name, 'CURVE'); cu.dimensions = '3D'; cu.bevel_depth = 1.0; cu.bevel_resolution = 2; cu.use_fill_caps = True
    sp = cu.splines.new('POLY'); sp.points.add(len(pts) - 1)
    for i, (p, q) in enumerate(zip(sp.points, pts)):
        p.co = (q.x, q.y, q.z, 1); p.radius = r0 + (r1 - r0) * i / (len(pts) - 1)
    cu.materials.append(m); return link(bpy.data.objects.new(name, cu))

def bez(p0, p1, p2, n=28):
    return [p0 * (1 - t) ** 2 + p1 * 2 * (1 - t) * t + p2 * t * t for t in (i / n for i in range(n + 1))]

def frame(axis, front):
    """Rotation taking local +z to axis and local -y to (the part of) front perpendicular to it."""
    z = axis.normalized(); f = front - z * front.dot(z)
    if f.length < 1e-6: f = Vector((0, -1, 0)) - z * (-z.y)
    y = -f.normalized(); x = y.cross(z)
    return Matrix((x, y, z)).transposed()

def calla(name, base, axis, front, L, R, m_spathe, m_spadix):
    NU, NV = 30, 40; verts, uvs = [], []
    for i in range(NU + 1):
        u = i / NU; span = math.pi * (1.10 - 0.32 * u)              # wraps past itself at the base, opens toward the top
        for j in range(NV + 1):
            v = j / NV; th = (v - 0.5) * 2 * span
            back = max(0.0, math.cos(th / 2)) ** 4                   # 1 at the back of the spathe, 0 at its two edges
            r = R * (0.10 + 0.90 * u ** 1.3) * (1 + 0.04 * th / math.pi)
            r += R * 0.65 * max(0.0, (u - 0.55) / 0.45) ** 2 * (0.35 + 0.65 * back)   # the lip flares out
            r += R * 0.9 * u ** 6 * back ** 2                                          # and the tip curls back
            z = L * u * (1 + 0.45 * back * u ** 3)                                     # back rises to a point, front dips
            verts.append(Vector((r * math.sin(th), r * math.cos(th), z))); uvs.append((v, u))
    faces = [(i * (NV + 1) + j, i * (NV + 1) + j + 1, (i + 1) * (NV + 1) + j + 1, (i + 1) * (NV + 1) + j) for i in range(NU) for j in range(NV)]
    rot = frame(axis, front)
    o = mesh_obj(name, [tuple(base + rot @ p) for p in verts], faces, m_spathe, uvs)
    sd = o.modifiers.new('t', 'SOLIDIFY'); sd.thickness = 0.0012; sd.offset = 0
    bpy.context.view_layer.objects.active = o; bpy.ops.object.modifier_apply(modifier=sd.name)
    bpy.ops.mesh.primitive_uv_sphere_add(segments=12, ring_count=8)
    sx = bpy.context.active_object; sx.name = name + ' spadix'
    sx.scale = (R * 0.17, R * 0.17, L * 0.27); sx.matrix_world = Matrix.Translation(base + rot @ Vector((0, R * 0.12, L * 0.30))) @ rot.to_4x4() @ Matrix.Diagonal((R * 0.17, R * 0.17, L * 0.27, 1))
    sx.data.materials.append(m_spadix); bpy.ops.object.shade_smooth()
    return [o, sx]

def leaf(c, s, t, R, cup, m, name):
    """Round cupped leaf in the plane of s (out from the stem) and t (along it)."""
    n = s.cross(t).normalized(); N = 14; verts = [c + n * (-cup * R * 0.1)]
    for k in range(N):
        a = 2 * math.pi * k / N; ca, sa = math.cos(a), math.sin(a)
        verts.append(c + s * (R * 1.04 * ca) + t * (R * sa) + n * (cup * R * (ca * ca + sa * sa) * 0.35))
    return mesh_obj(name, [tuple(v) for v in verts], [(0, 1 + k, 1 + (k + 1) % N) for k in range(N)], m)

def eucalyptus(name, rnd, ang, lean, top, droop, m_leaf, m_stem):
    out_ = Vector((math.cos(ang), math.sin(ang), 0))
    p0 = Vector((math.cos(ang) * 0.004, math.sin(ang) * 0.004, 0))
    p1 = out_ * lean * 0.45 + Vector((0, 0, top * 0.95))
    p2 = out_ * lean + Vector((0, 0, top - droop))
    pts = bez(p0, p1, p2, 40)
    parts = [stem(name + ' stem', pts, 0.0018, 0.0009, m_stem)]
    acc = [0.0]
    for a, b in zip(pts, pts[1:]): acc.append(acc[-1] + (b - a).length)
    total = acc[-1]; d = total * 0.40; node = 0; side = Vector((0, 0, 1)).cross(out_).normalized()
    while d < total - 0.004:
        k = next(i for i, x in enumerate(acc) if x >= d); t = (pts[min(k, len(pts) - 1)] - pts[max(k - 1, 0)]).normalized()
        frac = d / total; R = 0.021 - 0.010 * frac
        s0 = (side if node % 2 == 0 else t.cross(side)).normalized()
        s0 = (s0 - t * s0.dot(t)).normalized()
        for sgn in (1, -1):
            s = (s0 * sgn); tw = Matrix.Rotation(rnd.uniform(-0.35, 0.35), 3, s)
            tt = tw @ t
            parts.append(leaf(pts[k] + s * R * 0.92 + tt * R * 0.25, s, tt, R, rnd.uniform(0.6, 1.0), m_leaf, name + ' leaf'))
        node += 1; d += 0.026 - 0.008 * frac
    return parts

def bunch(fname, seed, callas, sprigs):
    bpy.ops.wm.read_factory_settings(use_empty=True); rnd = random.Random(seed)
    m_sp = pmat('Calla', (1, 1, 1, 1), 0.45, spathe_img())
    m_sx = pmat('Spadix', (0.93, 0.70, 0.16, 1), 0.7)
    m_st = pmat('Calla Stem', (0.20, 0.38, 0.11, 1), 0.4)
    m_lf = pmat('Eucalyptus Leaf', (0.34, 0.46, 0.43, 1), 0.65)
    m_es = pmat('Eucalyptus Stem', (0.40, 0.33, 0.24, 1), 0.6)
    parts = []
    front = Vector((0, -1, 0))                                   # Blender -y = the room (three.js +z)
    for i, (ang, lean, h, L) in enumerate(callas):
        dirx = Vector((math.cos(ang), math.sin(ang), 0))
        head = dirx * lean + Vector((0, 0, h))
        p0 = dirx * 0.004; p1 = dirx * lean * 0.35 + Vector((0, 0, h * 0.55))
        pts = bez(p0, p1, head, 36)
        parts.append(stem('Calla Stem', pts, 0.0034, 0.0028, m_st))
        axis = (head - pts[-4]).normalized().lerp((dirx + front * 0.8).normalized(), 0.35)
        parts += calla('Calla', head - axis * 0.004, axis, (dirx * 0.6 + front).normalized(), L, L * 0.30, m_sp, m_sx)
    for i, (ang, lean, top, droop) in enumerate(sprigs):
        parts += eucalyptus('Eucalyptus', rnd, ang, lean, top, droop, m_lf, m_es)
    bpy.ops.object.select_all(action='DESELECT')
    for o in parts:
        if o.type == 'CURVE': o.select_set(True)
    bpy.context.view_layer.objects.active = [o for o in parts if o.type == 'CURVE'][0]
    bpy.ops.object.convert(target='MESH')
    obs = [o for o in bpy.context.scene.objects if o.type == 'MESH']
    bpy.ops.object.select_all(action='DESELECT')
    for o in obs: o.select_set(True)
    bpy.context.view_layer.objects.active = obs[0]; bpy.ops.object.join(); fl = bpy.context.active_object; fl.name = 'Flowers'
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    zmax = max(v.co.z for v in fl.data.vertices); fl.scale = (0.44 / zmax,) * 3
    bpy.ops.object.transform_apply(scale=True)
    p = os.path.join(out, fname)
    bpy.ops.export_scene.gltf(filepath=p, export_format='GLB', export_apply=True, export_image_format='AUTO',
                              export_draco_mesh_compression_enable=True, export_draco_mesh_compression_level=6)
    print('FLOWERS', fname, len(fl.data.polygons), 'faces', round(os.path.getsize(p) / 1e3), 'KB')
    return fl

# (angle round the vase, lean out, head height, spathe length) and (angle, lean, top, droop at the tip)
bunch('flowers.glb', 7,
      [(-1.75, 0.030, 0.340, 0.100), (2.55, 0.080, 0.290, 0.092), (0.45, 0.085, 0.305, 0.095), (4.1, 0.050, 0.250, 0.086)],
      [(-0.6, 0.19, 0.30, 0.09), (1.4, 0.17, 0.33, 0.07), (3.3, 0.20, 0.27, 0.10), (-2.4, 0.16, 0.25, 0.07), (5.0, 0.14, 0.32, 0.06)])
bunch('flowers_small.glb', 11,
      [(-1.9, 0.030, 0.33, 0.105), (0.9, 0.075, 0.28, 0.095)],
      [(-0.5, 0.18, 0.27, 0.08), (2.4, 0.17, 0.30, 0.07), (3.9, 0.15, 0.24, 0.07)])
