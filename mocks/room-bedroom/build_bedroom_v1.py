# Bedroom v1, laid out from his standard design (mocks/room-refs/bedroom/bedroom-v1.jpg) and the approved blockout:
#   back wall: pale-oak FLUTED PANEL behind a bouclé QUEEN BED (draped duvet, teal throw, pillows, open book), the
#              piano canvas above it, a fluted nightstand each side (products)
#   left wall: WINDOW with sheer curtains on a black rod (garden beyond), the floor lamps (products)
#   right wall: walnut DRESSER (vase + sculpture on it, products), then the opening to a WALK-IN closet
#   front wall: the bedroom door (walnut). The room is closed on all four sides: the viewer's camera stays inside,
#               so a look toward the window or the dresser never shows the room's open edge
#   floor: honey oak, with the GLOY shaggy rug (built here, from the listing's close-up photo) under the bed's foot
# Built like the Quiet Bath v7: scanned CC0 materials (textures/: Poly Haven), every built surface gets an image
# lightmap from one Cycles bake, the products in placements.json stand in for the bake (real shadows) and are
# removed before export (the viewer places them). The duvet and throw are draped with Blender's cloth simulation.
#   blender -b -P build_bedroom_v1.py -- <room-bedroom dir> [quick]
# quick: no bake, a fast Cycles preview of the shapes only. Metres: x -2.1..2.1 (left..right), y -1.9..1.9
# (front open .. back wall), z 0..2.8.
import bpy, bmesh, math, sys, os, tempfile, json
import numpy as np
from mathutils import Vector

ARGS = sys.argv[sys.argv.index('--') + 1:]
OUT = os.path.abspath(ARGS[0]); QUICK = 'quick' in ARGS
TMP = tempfile.mkdtemp(prefix='bed1_')
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
X0, X1, Y0, Y1, H = -2.1, 2.1, -1.9, 1.9, 2.8
STEP = 0.08
WARM = (1.0, 0.86, 0.68)
rng = np.random.default_rng(7)

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

def ph(name, a, size=2048, tint=None, recolour=None, contrast=1.0):
    """Poly Haven scan set textures/<a>/<a>_{diff,nor_gl,rough}_2k.jpg"""
    f = lambda k: '%s/%s_%s_2k.jpg' % (a, a, k)
    return pbr(name, scan_img(f('diff'), size, tint=tint, recolour=recolour, contrast=contrast), scan_img(f('nor_gl'), 1024, False), scan_img(f('rough'), 512, False))

LINEN = lambda name, c: ph(name, 'rough_linen', 1024, recolour=c, contrast=1.3)
M = {
    'wall': ph('Plaster Wall', 'beige_wall_001', tint=(1.03, 0.99, 0.93)),
    'floor': ph('Oak Floor', 'laminate_floor_03', tint=(1.06, 1.02, 0.97)),
    'slat': ph('Oak Slat', 'oak_veneer_03', 1024, tint=(0.98, 0.88, 0.74)),
    'walnut': pbr('Walnut', scan_img('walnut_veneer/walnut_veneer_Diffuse_2k.jpg', 1024, tint=(0.62, 0.48, 0.38)),
                  scan_img('walnut_veneer/walnut_veneer_nor_gl_2k.jpg', 1024, False), scan_img('walnut_veneer/walnut_veneer_Rough_2k.jpg', 512, False)),
    'boucle': ph('Boucle', 'curly_teddy_natural', 1024, tint=(1.02, 1.0, 0.96), contrast=1.7),
    'linen': LINEN('White Linen', (0.94, 0.93, 0.90)),
    'teal': LINEN('Teal Linen', (0.07, 0.26, 0.28)),
    'terra': LINEN('Terracotta Linen', (0.62, 0.30, 0.20)),
    'cream': LINEN('Cream Linen', (0.90, 0.85, 0.76)),
    'sheer': LINEN('Sheer Linen', (0.95, 0.93, 0.88)),
    'ceiling': mat('Ceiling', (0.95, 0.94, 0.92, 1), 0.95),
    'frame': mat('Window Frame', (0.93, 0.93, 0.92, 1), 0.35),
    'glass': mat('Glass', (0.85, 0.95, 0.95, 1), 0.04, 0.0, alpha=0.10),
    'blackmat': mat('Matte Black', (0.025, 0.025, 0.027, 1), 0.7),
    'chrome': mat('Chrome', (0.84, 0.85, 0.87, 1), 0.15, 1.0),
    'paper': mat('Paper', (0.93, 0.91, 0.86, 1), 0.9),
    'cover': mat('Book Cover', (0.55, 0.22, 0.16, 1), 0.6),
    'glow': mat('Warm Glow', (1, .85, .65, 1), 0.5, 0.0, emit=((1, .78, .5, 1), 2.0)),
}

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

# ---------------------------------------------------------------- shell
# Left wall: the window is a hole of faces 8..24 across, 9..28 up (y -1.267..0.079, z 0.72..2.32). Right wall (its
# faces count from the back): the walk-in opening is faces 1..11 across, 0..25 up (y 0.95..1.821, z 0..2.08).
DU = (Y1 - Y0) / round((Y1 - Y0) / STEP)
WY0, WY1, WZ0, WZ1 = Y0 + 8 * DU, Y0 + 25 * DU, 0.72, 2.32
DY0, DY1, DZ1 = Y1 - 12 * DU, Y1 - 1 * DU, 2.08
grid('Floor', (X0, Y0, 0), (X1 - X0, 0, 0), (0, Y1 - Y0, 0), M['floor'], tile=2.08)
grid('Ceiling', (X0, Y1, H), (X1 - X0, 0, 0), (0, -(Y1 - Y0), 0), M['ceiling'], tile=3.0)
grid('Back Wall', (X0, Y1, 0), (X1 - X0, 0, 0), (0, 0, H), M['wall'], tile=3.0)
grid('Left Wall', (X0, Y0, 0), (0, Y1 - Y0, 0), (0, 0, H), M['wall'], tile=3.0, holes=[(8, 25, 9, 29)])
grid('Right Wall', (X1, Y1, 0), (0, -(Y1 - Y0), 0), (0, 0, H), M['wall'], tile=3.0, holes=[(1, 12, 0, 26)])
grid('Front Wall', (X1, Y0, 0), (-(X1 - X0), 0, 0), (0, 0, H), M['wall'], tile=3.0)
# drop ceiling: a 12 cm frame, 45 cm wide, round the room; a warm LED cove washes up into the raised centre
FD, FW = 0.12, 0.45
HD = H - FD
grid('Drop Left Under', (X0, Y1, HD), (FW, 0, 0), (0, -(Y1 - Y0), 0), M['ceiling'], tile=3.0)
grid('Drop Right Under', (X1 - FW, Y1, HD), (FW, 0, 0), (0, -(Y1 - Y0), 0), M['ceiling'], tile=3.0)
grid('Drop Back Under', (X0 + FW, Y1, HD), (X1 - X0 - 2 * FW, 0, 0), (0, -FW, 0), M['ceiling'], tile=3.0)
grid('Drop Left Face', (X0 + FW, Y0, HD), (0, Y1 - Y0, 0), (0, 0, FD), M['ceiling'], tile=3.0)
grid('Drop Right Face', (X1 - FW, Y1, HD), (0, -(Y1 - Y0), 0), (0, 0, FD), M['ceiling'], tile=3.0)
grid('Drop Back Face', (X0 + FW, Y1 - FW, HD), (X1 - X0 - 2 * FW, 0, 0), (0, 0, FD), M['ceiling'], tile=3.0)
grid('Drop Front Under', (X0 + FW, Y0 + FW, HD), (X1 - X0 - 2 * FW, 0, 0), (0, -FW, 0), M['ceiling'], tile=3.0)
grid('Drop Front Face', (X1 - FW, Y0 + FW, HD), (-(X1 - X0 - 2 * FW), 0, 0), (0, 0, FD), M['ceiling'], tile=3.0)
GW = 0.025
box('Cove Glow Left', (X0 + FW + 0.02, 0, H - 0.01), (GW, Y1 - Y0 - 0.05, 0.01), M['glow'])
box('Cove Glow Right', (X1 - FW - 0.02, 0, H - 0.01), (GW, Y1 - Y0 - 0.05, 0.01), M['glow'])
box('Cove Glow Back', (0, Y1 - FW - 0.02, H - 0.01), (X1 - X0 - 2 * FW - 0.05, GW, 0.01), M['glow'])
box('Cove Glow Front', (0, Y0 + FW + 0.02, H - 0.01), (X1 - X0 - 2 * FW - 0.05, GW, 0.01), M['glow'])
# the walk-in closet beyond the right wall: x 2.1..3.3, y 0..1.9, ceiling 2.6
CX1, CY0, CH = 3.3, 0.0, 2.6
grid('Closet Floor', (X1, CY0, 0), (CX1 - X1, 0, 0), (0, Y1 - CY0, 0), M['floor'], tile=2.08)
grid('Closet Ceiling', (X1, Y1, CH), (CX1 - X1, 0, 0), (0, -(Y1 - CY0), 0), M['ceiling'], tile=3.0)
grid('Closet Far Wall', (CX1, Y1, 0), (0, -(Y1 - CY0), 0), (0, 0, CH), M['wall'], tile=3.0)
grid('Closet Back Wall', (X1, Y1, 0), (CX1 - X1, 0, 0), (0, 0, CH), M['wall'], tile=3.0)
grid('Closet Front Wall', (CX1, CY0, 0), (-(CX1 - X1), 0, 0), (0, 0, CH), M['wall'], tile=3.0)

# ---------------------------------------------------------------- walk-in: casing, reveal, rail of clothes, shelf
WT = 0.12   # wall thickness shown in the openings
parts = [box('Reveal', (X1 + WT / 2, DY0 - 0.005, DZ1 / 2), (WT, 0.01, DZ1), M['wall']),
         box('Reveal', (X1 + WT / 2, DY1 + 0.005, DZ1 / 2), (WT, 0.01, DZ1), M['wall']),
         box('Reveal', (X1 + WT / 2, (DY0 + DY1) / 2, DZ1 + 0.005), (WT, DY1 - DY0 + 0.02, 0.01), M['wall'])]
world_uv(join(parts, 'Walk-in Reveal'), 3.0)
cas = [box('Casing', (X1 - 0.008, DY0 - 0.03, (DZ1 + 0.06) / 2), (0.016, 0.06, DZ1 + 0.06), M['walnut'], bevel=0.003),
       box('Casing', (X1 - 0.008, DY1 + 0.03, (DZ1 + 0.06) / 2), (0.016, 0.06, DZ1 + 0.06), M['walnut'], bevel=0.003),
       box('Casing', (X1 - 0.008, (DY0 + DY1) / 2, DZ1 + 0.03), (0.016, DY1 - DY0 + 0.12, 0.06), M['walnut'], bevel=0.003)]
closet = [join(cas, 'Casing'), cyl('Rail', (3.02, 0.95, 1.86), 0.012, 1.7, M['chrome'], rot=(math.pi / 2, 0, 0)),
          box('Closet Shelf', (3.05, 0.95, 2.12), (0.5, 1.88, 0.03), M['walnut'], bevel=0.003)]
GARMENT = [mat('Garment %d' % i, c + (1,), 0.85) for i, c in enumerate([(0.85, 0.82, 0.76), (0.20, 0.27, 0.36), (0.62, 0.55, 0.45),
           (0.93, 0.92, 0.89), (0.36, 0.40, 0.33), (0.12, 0.12, 0.13), (0.70, 0.42, 0.32), (0.55, 0.60, 0.66)])]
y = 0.18
for i in range(16):
    hgt = 0.65 + 0.35 * rng.random(); g = box('Garment', (3.02, y, 1.84 - hgt / 2), (0.44, 0.035 + 0.02 * rng.random(), hgt), GARMENT[int(rng.integers(len(GARMENT)))], bevel=0.012)
    g.rotation_euler.z = (rng.random() - 0.5) * 0.12; closet.append(g); y += 0.095
for i, c in enumerate([(0.75, 0.70, 0.62), (0.25, 0.30, 0.32), (0.85, 0.83, 0.78)]):     # folded stacks on the shelf
    closet.append(box('Folded', (3.08, 0.35 + 0.5 * i, 2.135 + 0.06), (0.32, 0.36, 0.12), mat('Folded %d' % i, c + (1,), 0.9), bevel=0.02))
for o in closet: o.select_set(False)
closet = join(closet, 'LM_Closet')
world_uv(closet, 1.8, swap=True)

# ---------------------------------------------------------------- window (left wall): reveal, white frame, glass, garden
WY, WZ = (WY0 + WY1) / 2, (WZ0 + WZ1) / 2
WT2 = 0.20
win = [box('Reveal', (X0 - WT2 / 2, WY0 - 0.005, WZ), (WT2, 0.01, WZ1 - WZ0), M['wall']),
       box('Reveal', (X0 - WT2 / 2, WY1 + 0.005, WZ), (WT2, 0.01, WZ1 - WZ0), M['wall']),
       box('Reveal', (X0 - WT2 / 2, WY, WZ1 + 0.005), (WT2, WY1 - WY0 + 0.02, 0.01), M['wall']),
       box('Sill', (X0 - WT2 / 2 + 0.02, WY, WZ0 - 0.012), (WT2 + 0.04, WY1 - WY0 + 0.06, 0.024), M['frame'], bevel=0.004)]
world_uv(win[0], 3.0); world_uv(win[1], 3.0); world_uv(win[2], 3.0)
FX, FT, FDp = X0 - 0.11, 0.06, 0.07
win += [box('Frame', (FX, WY0 + FT / 2, WZ), (FDp, FT, WZ1 - WZ0), M['frame'], bevel=0.004),
        box('Frame', (FX, WY1 - FT / 2, WZ), (FDp, FT, WZ1 - WZ0), M['frame'], bevel=0.004),
        box('Frame', (FX, WY, WZ0 + FT / 2), (FDp, WY1 - WY0, FT), M['frame'], bevel=0.004),
        box('Frame', (FX, WY, WZ1 - FT / 2), (FDp, WY1 - WY0, FT), M['frame'], bevel=0.004),
        box('Mullion', (FX, WY - 0.12, WZ), (FDp, 0.07, WZ1 - WZ0), M['frame'], bevel=0.004)]
# curtain rod (black, the length of the window and both curtains) with two brackets
RZ = 2.60
win += [cyl('Rod', (X0 + 0.12, -0.62, RZ), 0.012, 2.6, M['blackmat'], rot=(math.pi / 2, 0, 0)),
        cyl('Rod End', (X0 + 0.12, -1.93 + 0.02, RZ), 0.02, 0.04, M['blackmat'], rot=(math.pi / 2, 0, 0)),
        cyl('Rod End', (X0 + 0.12, 0.69, RZ), 0.02, 0.04, M['blackmat'], rot=(math.pi / 2, 0, 0))]
for yy in (-1.75, 0.55): win.append(box('Bracket', (X0 + 0.06, yy, RZ), (0.12, 0.015, 0.02), M['blackmat']))
for o in win: o.select_set(False)
window = join(win, 'LM_Window')
box('Window Glass', (FX, WY, WZ), (0.006, WY1 - WY0 - 0.04, WZ1 - WZ0 - 0.04), M['glass'])
# the garden: a soft-focus picture on a lit plane 1.2 m outside (sky at the top, greens below)
gh, gw = 192, 256
yy_, xx_ = np.mgrid[0:gh, 0:gw] / np.array([gh, gw])[:, None, None]
img = np.stack([0.80 + 0.15 * yy_, 0.86 + 0.10 * yy_, 0.84 + 0.14 * yy_], -1)          # pale sky, brighter at the top (row 0 = bottom)
for _ in range(70):
    cx_, cy_, r_ = rng.random(), rng.random() * 0.75, 0.05 + 0.12 * rng.random()
    g_ = np.exp(-((xx_ - cx_) ** 2 + (yy_ - cy_) ** 2) / (2 * r_ * r_))[..., None]
    col = np.array([0.20 + 0.15 * rng.random(), 0.36 + 0.2 * rng.random(), 0.16 + 0.1 * rng.random()])
    img = img * (1 - 0.55 * g_) + col * 0.55 * g_
garden = save_img('garden', np.clip(img, 0, 1))
gm = bpy.data.materials.new('Garden'); gm.use_nodes = True; nt = gm.node_tree; b = nt.nodes['Principled BSDF']
t = nt.nodes.new('ShaderNodeTexImage'); t.image = garden; nt.links.new(t.outputs['Color'], b.inputs['Base Color']); nt.links.new(t.outputs['Color'], b.inputs['Emission Color'])
b.inputs['Emission Strength'].default_value = 1.0
gme = bpy.data.meshes.new('Garden'); gx_ = X0 - 1.2
gme.from_pydata([(gx_, WY - 2, -0.2), (gx_, WY + 2, -0.2), (gx_, WY + 2, 3.0), (gx_, WY - 2, 3.0)], [], [(0, 1, 2, 3)])
gme.uv_layers.new(name='UV').data.foreach_set('uv', [0, 0, 1, 0, 1, 1, 0, 1])
gp = bpy.data.objects.new('Garden', gme); scene.collection.objects.link(gp); gme.materials.append(gm)

# ---------------------------------------------------------------- sheer curtains, pleated, either side of the window
def curtain(name, ya, yb, folds, x=X0 + 0.12):
    nx, nz = 120, 40; zt, zb = RZ - 0.03, 0.01
    verts, uvs = [], []
    for j in range(nz + 1):
        f = j / nz; z = zb + (zt - zb) * f
        for i in range(nx + 1):
            s = i / nx; amp = 0.035 * (1.15 - 0.3 * f)                # folds a little deeper at the hem
            verts.append((x + amp * math.sin(2 * math.pi * folds * s), ya + (yb - ya) * s, z))
            uvs.append((s * (yb - ya) * 1.7 / 0.27, z / 0.27))
    faces = [(j * (nx + 1) + i, j * (nx + 1) + i + 1, (j + 1) * (nx + 1) + i + 1, (j + 1) * (nx + 1) + i) for j in range(nz) for i in range(nx)]   # facing the room (+x)
    me = bpy.data.meshes.new(name); me.from_pydata(verts, [], faces)
    uv = me.uv_layers.new(name='UV')
    for poly in me.polygons:
        for li, vi in zip(poly.loop_indices, poly.vertices): uv.data[li].uv = uvs[vi]
    ob = bpy.data.objects.new(name, me); scene.collection.objects.link(ob); me.materials.append(M['sheer']); smooth(ob)
    return ob
curtains = join([curtain('Curtain', -1.88, -1.20, 6), curtain('Curtain', 0.02, 0.68, 6)], 'LM_Curtains')

# ---------------------------------------------------------------- fluted oak panel behind the bed
PW, PH = 2.6, 2.5
DRX = 1.40   # the door's centre (x) on the front wall
panel = [box('Panel Back', (0, Y1 - 0.006, PH / 2), (PW, 0.012, PH), M['slat'])]
n = int(PW / 0.045); x = -(n - 1) * 0.045 / 2
for i in range(n):
    panel.append(box('Slat', (x + i * 0.045, Y1 - 0.012 - 0.011, PH / 2), (0.03, 0.022, PH), M['slat'], bevel=0.004, segs=2))
panel = join(panel, 'LM_Panel'); world_uv(panel, 1.0, swap=True)

# skirting (walnut) where the walls meet the floor, not behind the panel or across the walk-in
sk = [box('Skirting', (-(X1 + PW / 2) / 2, Y1 - 0.006, 0.04), (X1 - PW / 2, 0.012, 0.08), M['walnut']),
      box('Skirting', ((X1 + PW / 2) / 2, Y1 - 0.006, 0.04), (X1 - PW / 2, 0.012, 0.08), M['walnut']),
      box('Skirting', (X0 + 0.006, 0, 0.04), (0.012, Y1 - Y0, 0.08), M['walnut']),
      box('Skirting', (X1 - 0.006, (Y0 + DY0) / 2, 0.04), (0.012, DY0 - Y0, 0.08), M['walnut']),
      box('Skirting', ((X0 + DRX - 0.5) / 2, Y0 + 0.006, 0.04), (DRX - 0.5 - X0, 0.012, 0.08), M['walnut']),
      box('Skirting', ((DRX + 0.5 + X1) / 2, Y0 + 0.006, 0.04), (X1 - DRX - 0.5, 0.012, 0.08), M['walnut'])]
skirting = join(sk, 'LM_Skirting'); world_uv(skirting, 1.8, swap=True)

# ---------------------------------------------------------------- the bedroom door (front wall, right), closed
dd = [box('Door Leaf', (DRX, Y0 + 0.024, 1.03), (0.88, 0.04, 2.05), M['walnut'], bevel=0.003)]
world_uv(dd[0], 1.8)
dd += [box('Door Casing', (DRX - 0.47, Y0 + 0.01, 1.07), (0.06, 0.02, 2.14), M['walnut'], bevel=0.003),
       box('Door Casing', (DRX + 0.47, Y0 + 0.01, 1.07), (0.06, 0.02, 2.14), M['walnut'], bevel=0.003),
       box('Door Casing', (DRX, Y0 + 0.01, 2.11), (1.0, 0.02, 0.06), M['walnut'], bevel=0.003),
       cyl('Door Rose', (DRX - 0.36, Y0 + 0.05, 1.0), 0.026, 0.012, M['chrome'], rot=(math.pi / 2, 0, 0)),
       box('Door Lever', (DRX - 0.29, Y0 + 0.075, 1.0), (0.13, 0.05, 0.018), M['chrome'], bevel=0.005)]
door = join(dd, 'LM_Door')

# ---------------------------------------------------------------- the bed: bouclé frame + headboard, walnut legs, mattress
BW, BL = 1.78, 2.15
BY0 = Y1 - 0.06 - BL                                     # foot of the frame (y -0.31)
bed = [box('Bed Base', (0, BY0 + BL / 2, 0.26), (BW, BL, 0.28), M['boucle'], bevel=0.05, segs=5),
       box('Headboard', (0, Y1 - 0.12, 0.70), (BW, 0.12, 1.16), M['boucle'], bevel=0.05, segs=5)]
world_uv(bed[0], 0.3); world_uv(bed[1], 0.3)
for lx in (-0.74, 0.74):
    for ly in (BY0 + 0.12, Y1 - 0.25): bed.append(cyl('Leg', (lx, ly, 0.06), 0.032, 0.12, M['walnut'], r2=0.024, seg=20))
mattress = box('Mattress', (0, Y1 - 0.18 - 1.0, 0.51), (1.62, 2.0, 0.22), M['linen'], bevel=0.035, segs=4)
world_uv(mattress, 0.27)
bed_parts = bed + [mattress]

# ---------------------------------------------------------------- bedding: cloth-draped duvet and throw
def drape(name, w, d, nx, ny, c, z, m, colliders, frames=60, bend=1.0, mass=0.3, tile=0.27):
    bpy.ops.mesh.primitive_grid_add(x_subdivisions=nx, y_subdivisions=ny, size=1, location=(c[0], c[1], z))
    o = bpy.context.active_object; o.name = name; o.scale = (w, d, 1); bpy.ops.object.transform_apply(scale=True)
    me = o.data; uv = me.uv_layers[0]
    for poly in me.polygons:
        for li, vi in zip(poly.loop_indices, poly.vertices):
            co = me.vertices[vi].co; uv.data[li].uv = (co.x / tile, co.y / tile)
    me.materials.append(m)
    for k in colliders:
        if not any(md.type == 'COLLISION' for md in k.modifiers): k.modifiers.new('Collision', 'COLLISION')
        k.collision.thickness_outer = 0.004; k.collision.cloth_friction = 10
    cl = o.modifiers.new('Cloth', 'CLOTH'); s = cl.settings
    s.quality = 8; s.mass = mass; s.bending_stiffness = bend; s.tension_stiffness = 20; s.compression_stiffness = 20; s.shear_stiffness = 10; s.air_damping = 2
    cl.collision_settings.distance_min = 0.006; cl.collision_settings.use_self_collision = False
    cl.point_cache.frame_start = 1; cl.point_cache.frame_end = frames
    scene.frame_start = 1; scene.frame_end = frames
    for f in range(1, frames + 1): scene.frame_set(f)
    bpy.context.view_layer.objects.active = o; o.select_set(True); bpy.ops.object.modifier_apply(modifier='Cloth')
    return o

def displace(o, tex, strength, coords='GLOBAL'):
    dm = o.modifiers.new('Displace', 'DISPLACE'); dm.texture = tex; dm.strength = strength; dm.mid_level = 0.5; dm.texture_coords = coords
    if coords == 'UV': dm.uv_layer = o.data.uv_layers[0].name
def clouds(name, size, depth=2):
    t = bpy.data.textures.new(name, 'CLOUDS'); t.noise_scale = size; t.noise_depth = depth; return t
CREASE = clouds('Creases', 0.07)
BILLOW = clouds('Billows', 0.3, 1)        # the soft rise and fall of a filled duvet
# the throw's quilting: stitched channels every 13.5 cm (two a linen tile), as a displacement image on its UVs
qy, qx = np.mgrid[0:256, 0:256] / 256.0
qd = np.minimum(np.abs((qx * 2) % 1 - 0.5), np.abs((qy * 2) % 1 - 0.5))
QUILT = bpy.data.textures.new('Quilt', 'IMAGE'); QUILT.image = save_img('quilt', np.repeat((1 - np.exp(-(qd / 0.018) ** 2))[..., None], 3, -1), False)

def thicken(o, t, sub=1, crease=0.012, quilt=0.0, billow=0.0):
    """Subdivide, crease (and quilt), then give the cloth its thickness."""
    ss = o.modifiers.new('Sub', 'SUBSURF'); ss.levels = sub; ss.render_levels = sub
    if billow: displace(o, BILLOW, billow)
    displace(o, CREASE, crease)
    if quilt: displace(o, QUILT, quilt, 'UV')
    if t: sm = o.modifiers.new('Solid', 'SOLIDIFY'); sm.thickness = t; sm.offset = 1
    apply_all(o); smooth(o); return o

duvet = thicken(drape('LM_Duvet', 1.98, 1.74, 64, 58, (0, 0.61), 0.74, M['linen'], [mattress, bed[0]], bend=2.0), 0.04, crease=0.02, billow=0.05)   # foot flush with the mattress, so the bouclé frame shows
throw = thicken(drape('LM_Throw', 2.08, 0.80, 72, 28, (0, 0.10), 0.86, M['teal'], [duvet, mattress, bed[0]], bend=0.6, mass=0.4), 0, sub=2, crease=0.012, quilt=0.005)
scene.frame_set(1)
for k in (mattress, bed[0], duvet):
    for md in [md for md in k.modifiers if md.type == 'COLLISION']: k.modifiers.remove(md)
bed = join(bed_parts, 'LM_Bed')

# ---------------------------------------------------------------- pillows and cushions (pinched seams, plump middles)
def pillow(name, W, D, T, m, n=40, tile=0.27):
    bm = bmesh.new(); top, bot = {}, {}
    for i in range(n + 1):
        for j in range(n + 1):
            s, t = -1 + 2 * i / n, -1 + 2 * j / n
            f = max(0.0, (1 - s ** 4) * (1 - t ** 4)) ** 0.5
            x, y = s * W / 2 * (1 - 0.06 * t * t), t * D / 2 * (1 - 0.06 * s * s)
            top[i, j] = bm.verts.new((x, y, T / 2 * f))
            bot[i, j] = top[i, j] if i in (0, n) or j in (0, n) else bm.verts.new((x, y, -T / 2 * f))
    for i in range(n):
        for j in range(n):
            bm.faces.new((top[i, j], top[i + 1, j], top[i + 1, j + 1], top[i, j + 1]))
            bm.faces.new((bot[i, j + 1], bot[i + 1, j + 1], bot[i + 1, j], bot[i, j]))
    uvl = bm.loops.layers.uv.new('UV')
    for fc in bm.faces:
        for l in fc.loops: l[uvl].uv = (l.vert.co.x / tile + (0.5 if l.vert.co.z < 0 else 0), l.vert.co.y / tile)
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new(name, me); scene.collection.objects.link(ob); me.materials.append(m)
    displace(ob, CREASE, 0.022); apply_all(ob); smooth(ob)
    return ob

MT = 0.62   # mattress top
def lean(o, D, T, deg, x, back, base):
    a = math.radians(deg); o.rotation_euler = (a, 0, 0)
    ye, ze = D * math.cos(a) + T * math.sin(a), D * math.sin(a) + T * math.cos(a)
    o.location = (x, back - ye / 2, base + ze / 2); return back - ye     # its front, for the next row
pil = []
for x in (-0.42, 0.42):
    p = pillow('Pillow', 0.68, 0.50, 0.18, M['linen']); f1 = lean(p, 0.50, 0.18, 74, x, Y1 - 0.16, MT - 0.02); pil.append(p)
for x, mm in ((-0.27, 'terra'), (0.27, 'teal')):
    p = pillow('Cushion', 0.45, 0.45, 0.15, M[mm]); f2 = lean(p, 0.45, 0.15, 68, x, f1 - 0.02, MT + 0.03); pil.append(p)
p = pillow('Lumbar', 0.56, 0.30, 0.13, M['cream']); lean(p, 0.30, 0.13, 62, 0, f2 - 0.03, MT + 0.05); pil.append(p)
for p in pil: p.select_set(False)
pillows = join(pil, 'LM_Pillows')
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

# ---------------------------------------------------------------- an open book on the throw
bpy.context.view_layer.update()
dg = bpy.context.evaluated_depsgraph_get()
hit, loc, *_ = scene.ray_cast(dg, Vector((-0.28, 0.18, 2.0)), Vector((0, 0, -1)))
bz = loc.z if hit else MT + 0.06
bk = [box('Book Cover', (0, 0, 0.002), (0.31, 0.215, 0.004), M['cover'], bevel=0.001)]
for sgn in (-1, 1):
    pg = box('Pages', (sgn * 0.074, 0, 0.011), (0.142, 0.205, 0.014), M['paper'], bevel=0.003)
    pg.rotation_euler.y = -sgn * math.radians(6); bk.append(pg)
book = join(bk, 'LM_Book'); book.location = (-0.28, 0.18, bz); book.rotation_euler.z = 0.22
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

# ---------------------------------------------------------------- walnut dresser on the right wall
DX0, DXB, DYa, DYb = 1.60, X1, -0.85, 0.80
dr = [box('Dresser Body', ((DX0 + DXB) / 2, (DYa + DYb) / 2, 0.445), (DXB - DX0, DYb - DYa, 0.69), M['walnut'], bevel=0.003),
      box('Dresser Top', ((DX0 - 0.01 + DXB) / 2, (DYa + DYb) / 2, 0.805), (DXB - DX0 + 0.01, DYb - DYa + 0.02, 0.03), M['walnut'], bevel=0.003)]
for o in dr: world_uv(o, 1.8, swap=True)
dr += [box('Plinth', ((DX0 + 0.05 + DXB) / 2, (DYa + DYb) / 2, 0.05), (DXB - DX0 - 0.05, DYb - DYa - 0.08, 0.10), M['blackmat']),
       box('Groove', (DX0 - 0.002, (DYa + DYb) / 2, 0.445), (0.006, 0.006, 0.69), M['blackmat'])]
for zz in (0.33, 0.56): dr.append(box('Groove', (DX0 - 0.002, (DYa + DYb) / 2, zz), (0.006, DYb - DYa, 0.006), M['blackmat']))
for zz in (0.32, 0.55, 0.78):           # finger-pull shadow lines under each drawer's top edge
    for yc in ((DYa + (DYa + DYb) / 2) / 2, (DYb + (DYa + DYb) / 2) / 2): dr.append(box('Pull', (DX0 - 0.004, yc, zz - 0.012), (0.01, 0.16, 0.008), M['walnut'], bevel=0.002))
dresser = join(dr, 'LM_Dresser')

# ---------------------------------------------------------------- the GLOY shaggy rug, from its close-up photo
src = bpy.data.images.load(os.path.join(OUT, 'source/gloy/3.webp'))
w0, h0 = src.size; a = np.array(src.pixels[:], dtype=np.float32).reshape(h0, w0, 4)[..., :3]
c0 = int(min(w0, h0) * 0.9); a = a[(h0 - c0) // 2:(h0 - c0) // 2 + c0, (w0 - c0) // 2:(w0 - c0) // 2 + c0]
sq = bpy.data.images.new('gloy_sq', c0, c0, alpha=False); rgba = np.ones((c0, c0, 4), np.float32); rgba[..., :3] = a; sq.pixels.foreach_set(rgba.ravel())
sq.scale(1024, 1024); a = np.array(sq.pixels[:], dtype=np.float32).reshape(1024, 1024, 4)[..., :3]
ramp = np.clip(np.minimum(np.arange(1024), 1023 - np.arange(1024)) / 256.0, 0, 1)        # seamless: blend in a half-shifted copy at the edges
wgt = (ramp[:, None] * ramp[None, :])[..., None]
rug_col = a * wgt + np.roll(a, (512, 512), (0, 1)) * (1 - wgt)
lum = rug_col @ np.array([0.2126, 0.7152, 0.0722], dtype=np.float32)
hn = wrap_blur(lum, 1.2); gx = (np.roll(hn, -1, 1) - np.roll(hn, 1, 1)) * 6; gy = (np.roll(hn, -1, 0) - np.roll(hn, 1, 0)) * 6
nrm = np.stack([-gx, -gy, np.ones_like(gx)], -1); nrm /= np.linalg.norm(nrm, axis=-1, keepdims=True)
rug_mat = pbr('GLOY Shaggy Pile', save_img('gloy_pile', np.clip(rug_col, 0, 1)), save_img('gloy_pile_n', nrm * 0.5 + 0.5, False), None, rough=0.95)
hbig = wrap_blur(lum, 14); hbig = (hbig - hbig.min()) / max(1e-4, np.ptp(hbig))
RW, RD, RCX, RCY, RT = 2.6, 1.8, 0.0, -0.35, 0.14
nx, ny = int(RW / 0.01), int(RD / 0.01)
X, Y = np.meshgrid(np.linspace(-RW / 2, RW / 2, nx + 1), np.linspace(-RD / 2, RD / 2, ny + 1))
UVX, UVY = X / RT, Y / RT
r = 0.10; dx, dy = np.abs(X) - (RW / 2 - r), np.abs(Y) - (RD / 2 - r)          # rounded corners: corner squares onto quarter discs
cor = (dx > 0) & (dy > 0); f = np.where(cor, np.maximum(dx, dy) / np.maximum(np.hypot(dx, dy), 1e-9), 1)
X = np.where(cor, np.sign(X) * (RW / 2 - r + dx * f), X); Y = np.where(cor, np.sign(Y) * (RD / 2 - r + dy * f), Y)
hs = hbig[(UVY * 1024).astype(int) % 1024, (UVX * 1024).astype(int) % 1024]
I, J = np.meshgrid(np.arange(nx + 1), np.arange(ny + 1)); e = np.minimum(np.minimum(I, nx - I), np.minimum(J, ny - J))
Z = (0.022 + 0.016 * (hs - 0.5)) * np.select([e == 0, e == 1, e == 2], [0.2, 0.6, 0.85], 1.0)
V = np.stack([X + RCX, Y + RCY, Z], -1).reshape(-1, 3)
q = (J[:-1, :-1] * (nx + 1) + I[:-1, :-1]).ravel()
F = np.stack([q, q + 1, q + nx + 2, q + nx + 1], -1)
me = bpy.data.meshes.new('LM_Rug'); me.from_pydata(V.tolist(), [], F.tolist())
li = np.array([lp.vertex_index for lp in me.loops])
uv = me.uv_layers.new(name='UV'); uv.data.foreach_set('uv', np.stack([UVX.ravel()[li], UVY.ravel()[li]], -1).ravel().astype(np.float32))
lm = me.uv_layers.new(name='LM'); lm.data.foreach_set('uv', np.stack([I.ravel()[li] / nx, J.ravel()[li] / ny], -1).ravel().astype(np.float32))
me.uv_layers.active = lm
rug = bpy.data.objects.new('LM_Rug', me); scene.collection.objects.link(rug); me.materials.append(rug_mat); smooth(rug)

# ---------------------------------------------------------------- products: shadow casters for the bake, lamps lit
PL = json.load(open(os.path.join(OUT, 'placements.json')))
CASTERS, LAMPS = [], []
for d in PL['staging'] + PL['products']:
    if 'file' not in d: continue
    made = place(d); CASTERS += made
    if not d.get('light'): continue
    p = world_points(made); zmin, zmax = p[:, 2].min(), p[:, 2].max()
    if d['light'].get('arm'):           # arc lamp: the shade is the part of the top farthest from the pole
        base = p[p[:, 2] < zmin + 0.05][:, :2].mean(0); top = p[p[:, 2] > zmax - 0.2 * (zmax - zmin)]
        dist = np.linalg.norm(top[:, :2] - base, axis=1); sh = top[dist > dist.max() * 0.6]
        c = sh.mean(0); c[2] = sh[:, 2].min() - 0.03
    else:                               # a shade on top: walk down from the top while it stays wide; light just below it
        ax = p[p[:, 2] > zmax - 0.02][:, :2].mean(0); rad = lambda z0: np.linalg.norm(p[(p[:, 2] > z0) & (p[:, 2] <= z0 + 0.01)][:, :2] - ax, axis=1)
        r0 = np.linalg.norm(p[p[:, 2] > zmax - 0.04][:, :2] - ax, axis=1).max(); z = zmax - 0.03
        while z > zmin and len(rad(z - 0.01)) and rad(z - 0.01).max() > 0.5 * r0: z -= 0.01
        c = np.array([ax[0], ax[1], z - 0.03])
    LAMPS.append((d['name'], d['light']['w'], c)); print('LAMP', d['name'], [round(float(v), 3) for v in c])

for o in (bed, duvet, throw, pillows, panel, dresser, closet): print('TRIS', o.name, sum(len(pg.vertices) - 2 for pg in o.data.polygons))
lightmap_prep(bed, 2048); lightmap_prep(duvet, 2048); lightmap_prep(throw, 1024); lightmap_prep(pillows, 1024)
lightmap_prep(panel, 2048); lightmap_prep(dresser, 1024); lightmap_prep(window, 1024); lightmap_prep(curtains, 1024)
lightmap_prep(skirting, 512); lightmap_prep(door, 1024); lightmap_prep(closet, 1024); lightmap_prep(book, 256); lightmap_prep(rug, (1024, 712), new_uv=False)
for ob, ul, vl in SHELL:
    d = 0.009 if 'Ceiling' in ob.name or 'Closet' in ob.name else 0.0045
    lightmap_prep(ob, (max(16, min(1024, round(ul / d))), max(16, min(1024, round(vl / d)))), new_uv=False)

# ---------------------------------------------------------------- lights
def area(name, loc, sx, sy, energy, color, rot):
    ld = bpy.data.lights.new(name, 'AREA'); ld.energy = energy; ld.color = color; ld.shape = 'RECTANGLE'; ld.size = sx; ld.size_y = sy
    lo = bpy.data.objects.new(name, ld); lo.location = loc; lo.rotation_euler = rot; scene.collection.objects.link(lo)
area('Daylight', (X0 - 0.25, WY, WZ), WZ1 - WZ0 - 0.1, WY1 - WY0 - 0.1, 420, (1.0, 0.97, 0.93), (0, math.radians(-90), 0))
area('Cove L', (X0 + FW + 0.05, 0, H - 0.02), 0.12, Y1 - Y0 - 0.1, 35, WARM, (0, math.radians(-35), 0))
area('Cove R', (X1 - FW - 0.05, 0, H - 0.02), 0.12, Y1 - Y0 - 0.1, 35, WARM, (0, math.radians(35), 0))
area('Cove B', (0, Y1 - FW - 0.05, H - 0.02), X1 - X0 - 2 * FW, 0.12, 35, WARM, (math.radians(-35), 0, 0))
area('Cove F', (0, Y0 + FW + 0.05, H - 0.02), X1 - X0 - 2 * FW, 0.12, 35, WARM, (math.radians(35), 0, 0))
area('Fill', (0, -0.6, H - 0.05), 3.5, 2.2, 22, (1.0, 0.95, 0.9), (0, 0, 0))
area('Closet Light', (2.7, 0.95, CH - 0.02), 0.8, 1.6, 30, WARM, (0, 0, 0))
for name, w, c in LAMPS:
    ld = bpy.data.lights.new('Lamp', 'POINT'); ld.energy = w; ld.color = WARM; ld.shadow_soft_size = 0.04
    lo = bpy.data.objects.new('Lamp ' + name, ld); lo.location = Vector(c.tolist()); scene.collection.objects.link(lo)
world = bpy.data.worlds.new('W'); scene.world = world; world.use_nodes = True
world.node_tree.nodes['Background'].inputs['Color'].default_value = (0.05, 0.05, 0.06, 1); world.node_tree.nodes['Background'].inputs['Strength'].default_value = 0.3

# ---------------------------------------------------------------- bake light into every lightmap
scene.render.engine = 'CYCLES'; scene.cycles.device = 'CPU'
if not QUICK:
    scene.cycles.samples = 192
    scene.render.bake.target = 'IMAGE_TEXTURES'; scene.render.bake.margin = 8; scene.render.bake.use_clear = True
    bpy.ops.object.select_all(action='DESELECT')
    for o, _, _ in LM: o.select_set(True)
    bpy.context.view_layer.objects.active = LM[0][0]
    bpy.ops.object.bake(type='DIFFUSE', pass_filter={'DIRECT', 'INDIRECT'}, margin=8, use_clear=True)
    BAKED = {}
    for o, img, uvn in LM:
        w, h = img.size; BAKED[o.name] = gblur(np.array(img.pixels[:], dtype=np.float32).reshape(h, w, 4)[..., :3])
    room_names = {ob.name for ob, _, _ in SHELL if 'Closet' not in ob.name and 'Drop' not in ob.name}   # the cove-lit band may clip; the walls set the gain
    lum = np.concatenate([BAKED[n].reshape(-1, 3) for n in room_names]) @ np.array([0.2126, 0.7152, 0.0722])
    gain = 0.92 / max(1e-4, np.percentile(lum, 97)); print('BAKE gain', round(float(gain), 3), 'p50', round(float(np.percentile(lum, 50)), 3))
    LM_IMG = {}
    for o, img, uvn in LM:
        a = np.clip(BAKED[o.name] * gain, 0, 1); h, w = a.shape[:2]
        a = np.where(a <= 0.0031308, a * 12.92, 1.055 * np.power(a, 1 / 2.4) - 0.055)
        LM_IMG[o.name] = save_img('LM_' + o.name, a)
        print('LIGHTMAP', o.name, w, 'px, mean', round(float(a.mean()), 3))

# ---------------------------------------------------------------- previews: front (like the reference) and plan
scene.view_settings.view_transform = 'AgX'; scene.cycles.samples = 48 if QUICK else 96; scene.cycles.use_denoising = True
cam_d = bpy.data.cameras.new('Cam'); cam_d.lens = 18
cam = bpy.data.objects.new('Cam', cam_d); scene.collection.objects.link(cam)
cam.location = (0.0, Y0 + 0.15, 1.35); cam.rotation_euler = (Vector((0.0, Y1, 1.15)) - cam.location).to_track_quat('-Z', 'Y').to_euler()
tag = 'quick' if QUICK else 'v1'
scene.camera = cam; scene.render.resolution_x, scene.render.resolution_y = (1400, 780) if QUICK else (1800, 1000)
scene.render.filepath = OUT + '/bedroom_%s_front.png' % tag; bpy.ops.render.render(write_still=True)
cam.location = (1.3, -1.5, 1.15); cam_d.lens = 26; cam.rotation_euler = (Vector((-0.3, 0.7, 0.45)) - cam.location).to_track_quat('-Z', 'Y').to_euler()
scene.render.filepath = OUT + '/bedroom_%s_detail.png' % tag; bpy.ops.render.render(write_still=True)
hide = [o for o, _, _ in SHELL if 'Ceiling' in o.name or 'Drop' in o.name] + [o for o in bpy.data.objects if o.name.startswith('Cove Glow')]
for o in hide: o.hide_render = True
pd = bpy.data.cameras.new('Plan'); pd.type = 'ORTHO'; pd.ortho_scale = 5.6
pc = bpy.data.objects.new('Plan', pd); scene.collection.objects.link(pc); pc.location = (0.6, 0, 8); pc.rotation_euler = (0, 0, 0)
scene.camera = pc; scene.render.resolution_x = scene.render.resolution_y = 900; scene.render.filepath = OUT + '/bedroom_%s_plan.png' % tag; bpy.ops.render.render(write_still=True)
for o in hide: o.hide_render = False
if QUICK: print('DONE quick'); sys.exit(0)

# ---------------------------------------------------------------- export: products out (the viewer places them), lightmaps in as emissive
for o in CASTERS: bpy.data.objects.remove(o)
for o, _, uvn in LM:
    for slot in o.material_slots:
        nt = slot.material.node_tree; b = nt.nodes['Principled BSDF']
        nt.nodes.remove(nt.nodes['LM_BAKE'])
        for n_ in list(nt.nodes):
            if n_.type == 'TEX_IMAGE' and not n_.inputs['Vector'].is_linked and uvn != o.data.uv_layers[0].name:
                um = nt.nodes.new('ShaderNodeUVMap'); um.uv_map = o.data.uv_layers[0].name; nt.links.new(um.outputs['UV'], n_.inputs['Vector'])
        t = nt.nodes.new('ShaderNodeTexImage'); t.image = LM_IMG[o.name]
        um = nt.nodes.new('ShaderNodeUVMap'); um.uv_map = uvn; nt.links.new(um.outputs['UV'], t.inputs['Vector'])
        nt.links.new(t.outputs['Color'], b.inputs['Emission Color']); b.inputs['Emission Strength'].default_value = 1.0
    o.data.uv_layers.active = o.data.uv_layers[0]

kw = dict(filepath=OUT + '/bedroom_v1.glb', export_format='GLB', export_apply=True, export_cameras=False, export_lights=False, export_image_format='JPEG', export_jpeg_quality=85)
bpy.ops.export_scene.gltf(**kw)
bpy.ops.wm.save_as_mainfile(filepath=OUT + '/bedroom_v1.blend'); print('DONE', round(os.path.getsize(OUT + '/bedroom_v1.glb') / 1e6, 2), 'MB')
