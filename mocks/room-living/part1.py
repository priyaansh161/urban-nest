# Living room "The Heritage Lounge", laid out from mocks/room-refs/living2/lounge-v1.jpg (see LAYOUT.md).
# Same pipeline as the bedroom (build_bedroom_v1.py): grid shells + scanned textures, every built surface gets an image
# lightmap from one Cycles bake, products in placements.json stand in for the bake and are removed before export.
#   blender -b -P build_living_v1.py -- <room-living dir> [quick]
# Metres: x -2.6..2.6 (left..right), y -2.1..2.1 (front wall .. back wall), z 0..3.0. Blender y = -three.js z.
import bpy, bmesh, math, sys, os, tempfile, json
import numpy as np
from mathutils import Vector

ARGS = sys.argv[sys.argv.index('--') + 1:]
OUT = os.path.abspath(ARGS[0]); QUICK = 'quick' in ARGS
TMP = tempfile.mkdtemp(prefix='liv1_')
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
X0, X1, Y0, Y1, H = -2.6, 2.6, -2.1, 2.1, 3.0
STEP = 0.08
WARM = (1.0, 0.80, 0.55)
rng = np.random.default_rng(11)
sys.path.insert(0, os.path.join(OUT, '..'))
import staging_lib as SL

# ---------------------------------------------------------------- materials
def mat(name, color, rough=0.5, metal=0.0, emit=None, alpha=None):
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = color; b.inputs['Roughness'].default_value = rough; b.inputs['Metallic'].default_value = metal
    if emit: b.inputs['Emission Color'].default_value = emit[0]; b.inputs['Emission Strength'].default_value = emit[1]
    if alpha is not None:
        b.inputs['Alpha'].default_value = alpha
        try: m.surface_render_method = 'BLENDED'
        except Exception: pass
    return m

TEXDIR = os.path.join(OUT, 'textures')
def scan_img(rel, size, colour=True, tint=None, recolour=None, contrast=1.0):
    img = bpy.data.images.load(os.path.join(TEXDIR, rel))
    if max(img.size) > size: img.scale(size, size)
    if tint or recolour or contrast != 1.0:
        px = np.array(img.pixels[:], dtype=np.float32).reshape(-1, 4)
        if recolour:     # keep the weave, change the colour: luminance (mean 1, softened) times the new colour
            l = px[:, :3] @ np.array([0.2126, 0.7152, 0.0722], dtype=np.float32); l = 1 + (l / max(1e-4, l.mean()) - 1) * contrast
            px[:, :3] = l[:, None] * np.array(recolour, dtype=np.float32)
        elif contrast != 1.0: m_ = px[:, :3].mean(0); px[:, :3] = m_ + (px[:, :3] - m_) * contrast   # the nubs of a bouclé read at room distance
        if tint: px[:, :3] *= np.array(tint, dtype=np.float32)
        px[:, :3] = np.clip(px[:, :3], 0, 1); img.pixels.foreach_set(px.ravel())
    if not colour: img.colorspace_settings.name = 'Non-Color'
    img.pack(); return img

def pbr(name, color_img, normal_img, rough_img, rough=None):
    """A material from a colour image, an OpenGL normal map and a roughness image (or a flat roughness)."""
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree; b = nt.nodes['Principled BSDF']
    tc = nt.nodes.new('ShaderNodeTexImage'); tc.image = color_img; nt.links.new(tc.outputs['Color'], b.inputs['Base Color'])
    if rough_img:
        tr = nt.nodes.new('ShaderNodeTexImage'); tr.image = rough_img; nt.links.new(tr.outputs['Color'], b.inputs['Roughness'])
    else: b.inputs['Roughness'].default_value = rough
    tn = nt.nodes.new('ShaderNodeTexImage'); tn.image = normal_img
    nm = nt.nodes.new('ShaderNodeNormalMap'); nt.links.new(tn.outputs['Color'], nm.inputs['Color']); nt.links.new(nm.outputs['Normal'], b.inputs['Normal'])
    return m

# ---------------------------------------------------------------- helpers
SHELL = []
def grid(name, origin, u, v, m, tile=2.4, holes=()):
    """A flat surface of STEP-sized quads (u x v points into the room) with texture UVs at real scale and a 0..1 lightmap
    UV. holes: (i0, i1, j0, j1) face ranges left out (the window and the walk-in opening)."""
    origin, u, v = Vector(origin), Vector(u), Vector(v)
    ul, vl = u.length, v.length; nx, ny = max(1, round(ul / STEP)), max(1, round(vl / STEP))
    verts = [tuple(origin + u * (i / nx) + v * (j / ny)) for j in range(ny + 1) for i in range(nx + 1)]
    faces = [(j * (nx + 1) + i, j * (nx + 1) + i + 1, (j + 1) * (nx + 1) + i + 1, (j + 1) * (nx + 1) + i) for j in range(ny) for i in range(nx)
             if not any(i0 <= i < i1 and j0 <= j < j1 for i0, i1, j0, j1 in holes)]
    me = bpy.data.meshes.new('Shell_' + name); me.from_pydata(verts, [], faces)
    uv = me.uv_layers.new(name='UV')
    for poly in me.polygons:
        for li, vi in zip(poly.loop_indices, poly.vertices):
            uv.data[li].uv = ((vi % (nx + 1)) * ul / nx / tile, (vi // (nx + 1)) * vl / ny / tile)
    lm = me.uv_layers.new(name='LM')
    for poly in me.polygons:
        for li, vi in zip(poly.loop_indices, poly.vertices):
            lm.data[li].uv = ((vi % (nx + 1)) / nx, (vi // (nx + 1)) / ny)
    me.uv_layers.active = lm
    ob = bpy.data.objects.new('Shell_' + name, me); scene.collection.objects.link(ob); me.materials.append(m)
    SHELL.append((ob, ul, vl)); return ob

def box(name, loc, dim, m, bevel=0.0, rot=(0, 0, 0), segs=3):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc, rotation=rot)
    o = bpy.context.active_object; o.name = name; o.scale = dim
    bpy.ops.object.transform_apply(scale=True); o.data.materials.append(m)
    if bevel:
        bv = o.modifiers.new('Bevel', 'BEVEL'); bv.width = bevel; bv.segments = segs; bpy.ops.object.modifier_apply(modifier=bv.name)
    return o

def cyl(name, loc, r, h, m, rot=(0, 0, 0), seg=32, r2=None):
    if r2 is None: bpy.ops.mesh.primitive_cylinder_add(vertices=seg, radius=r, depth=h, location=loc, rotation=rot)
    else: bpy.ops.mesh.primitive_cone_add(vertices=seg, radius1=r, radius2=r2, depth=h, location=loc, rotation=rot)
    o = bpy.context.active_object; o.name = name; o.data.materials.append(m); bpy.ops.object.shade_smooth(); return o

def join(objs, name):
    bpy.ops.object.select_all(action='DESELECT')
    for o in objs: o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]; bpy.ops.object.join(); bpy.context.active_object.name = name
    return bpy.context.active_object

def apply_all(o):
    bpy.ops.object.select_all(action='DESELECT'); o.select_set(True); bpy.context.view_layer.objects.active = o
    for md in list(o.modifiers): bpy.ops.object.modifier_apply(modifier=md.name)

def smooth(o):
    o.data.polygons.foreach_set('use_smooth', [True] * len(o.data.polygons)); o.data.update()

def world_uv(o, tile, swap=False):
    """Texture UVs from world position, projected along each face's main axis (real scale, straight grain).
    swap turns the texture 90 degrees."""
    me = o.data; uv = me.uv_layers[0] if me.uv_layers else me.uv_layers.new(name='UVMap'); mw = o.matrix_world
    for poly in me.polygons:
        ax = max(range(3), key=lambda i: abs(poly.normal[i]))
        for li, vi in zip(poly.loop_indices, poly.vertices):
            p = mw @ me.vertices[vi].co
            a, b = ((p.y, p.z), (p.x, p.z), (p.x, p.y))[ax]
            uv.data[li].uv = (b / tile, a / tile) if swap else (a / tile, b / tile)

def bounds(objs):
    mn = Vector((1e9,) * 3); mx = Vector((-1e9,) * 3)
    for o in objs:
        if o.type != 'MESH': continue
        for c in o.bound_box:
            w = o.matrix_world @ Vector(c)
            for i in range(3): mn[i] = min(mn[i], w[i]); mx[i] = max(mx[i], w[i])
    return mn, mx

def import_glb(path):
    before = set(bpy.data.objects); bpy.ops.import_scene.gltf(filepath=path)
    return [o for o in bpy.data.objects if o not in before]

def place(d):
    """The viewer's placeItem() in Blender (see the Quiet Bath build). three.js (x, y, z) is Blender (x, -z, y)."""
    new = import_glb(os.path.join(OUT, 'products', d['file']))
    root = bpy.data.objects.new('Place ' + d['name'], None); scene.collection.objects.link(root)
    inner = bpy.data.objects.new('Place inner', None); scene.collection.objects.link(inner); inner.parent = root
    for o in new:
        if o.parent is None: o.parent = inner
    bpy.context.view_layer.update(); mn, mx = bounds(new); sz = mx - mn
    s = d['length'] / max(sz.x, sz.y) if 'length' in d else d['height'] / sz.z
    inner.scale = (s, s, s); bpy.context.view_layer.update(); mn, mx = bounds(new); c = (mn + mx) / 2
    inner.location -= Vector((c.x, c.y, mx.z if d.get('hang') else mn.z)); body_h = mx.z - mn.z   # hang: placed by its top (ceiling pieces)
    x, y, z = d['pos']; root.location = (x, -z, y); root.rotation_euler.z = d.get('rotY', 0)
    if 'alignBack' in d:
        bpy.context.view_layer.update(); mn, mx = bounds(new); root.location.y += -d['alignBack'] - mx.y
    if 'alignLeft' in d:
        bpy.context.view_layer.update(); mn, mx = bounds(new); root.location.x += d['alignLeft'] - mn.x
    if 'alignRight' in d:
        bpy.context.view_layer.update(); mn, mx = bounds(new); root.location.x += d['alignRight'] - mx.x
    made = new + [root, inner]
    if d.get('flowers'):
        fnew = import_glb(os.path.join(OUT, 'products', d['flowers']))
        fl = bpy.data.objects.new('Place flowers', None); scene.collection.objects.link(fl); fl.parent = root
        for o in fnew:
            if o.parent is None: o.parent = fl
        fl.location = (0, 0, body_h - 0.03); fl.scale = ((d.get('flowerHeight') or 0.36) / 0.44,) * 3; fl.rotation_euler.z = -d.get('rotY', 0)
        made += fnew + [fl]
    bpy.context.view_layer.update(); return made

def world_points(objs):
    out = []
    for o in objs:
        if o.type != 'MESH' or not len(o.data.vertices): continue
        a = np.empty(len(o.data.vertices) * 3, np.float32); o.data.vertices.foreach_get('co', a)
        mw = np.array(o.matrix_world, dtype=np.float32); out.append(a.reshape(-1, 3) @ mw[:3, :3].T + mw[:3, 3])
    return np.concatenate(out)

LM = []
def lightmap_prep(o, res, new_uv=True):
    """Own lightmap UV layout (or the active one) + a float image every material of o bakes into (materials copied)."""
    me = o.data; me.uv_layers[0].active_render = True
    w, h = res if isinstance(res, tuple) else (res, res)
    if new_uv:
        lm = me.uv_layers.new(name='LM'); me.uv_layers.active = lm
        bpy.ops.object.select_all(action='DESELECT'); o.select_set(True); bpy.context.view_layer.objects.active = o
        bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.uv.smart_project(angle_limit=math.radians(60), island_margin=0.006)
        bpy.ops.object.mode_set(mode='OBJECT')
    img = bpy.data.images.new('LMF_' + o.name, w, h, alpha=False, float_buffer=True)
    for slot in o.material_slots:
        m = slot.material.copy(); m.name = 'LM ' + slot.material.name; slot.material = m
        t = m.node_tree.nodes.new('ShaderNodeTexImage'); t.image = img; t.name = 'LM_BAKE'; m.node_tree.nodes.active = t
    LM.append((o, img, me.uv_layers.active.name))

def gblur(a, sigma=1.5):
    r = 4; k = np.exp(-np.arange(-r, r + 1) ** 2 / (2 * sigma * sigma)); k /= k.sum()
    for axis in (0, 1):
        p = np.pad(a, [(r, r) if i == axis else (0, 0) for i in range(a.ndim)], mode='edge')
        a = sum(k[i] * np.take(p, range(i, i + a.shape[axis]), axis=axis) for i in range(2 * r + 1))
    return a

def wrap_blur(a, sigma):
    """Gaussian blur of a seamless 2-D image, wrapping round its edges (stays seamless)."""
    h, w = a.shape; fy = np.fft.fftfreq(h)[:, None]; fx = np.fft.fftfreq(w)[None, :]
    return np.real(np.fft.ifft2(np.fft.fft2(a) * np.exp(-2 * (math.pi * sigma) ** 2 * (fx * fx + fy * fy))))

def save_img(name, rgb, colour=True):
    h, w = rgb.shape[:2]; rgba = np.ones((h, w, 4), dtype=np.float32); rgba[..., :3] = rgb
    im = bpy.data.images.new(name, w, h, alpha=False); im.pixels.foreach_set(rgba.ravel())
    p = os.path.join(TMP, name + '.png'); im.filepath_raw = p; im.file_format = 'PNG'; im.save()
    out = bpy.data.images.load(p)
    if not colour: out.colorspace_settings.name = 'Non-Color'
    out.pack(); return out
