# Showcase bathroom v3: Indian-society layout (vanity | shower | toilet), detailed textures,
# lighting BAKED into the walls/floor as vertex colours (so the web viewer needs no realtime shadows),
# and a mirror that shows a real render of the room.
#   blender -b -P build_bath_v3.py -- <out dir>
# Metres. Room x -1.8..1.8, y -1.3..1.3 (front open), z 0..2.7. glTF export turns this into Y-up.
import bpy, math, sys, random, os, tempfile
import numpy as np
from mathutils import Vector

OUT = sys.argv[sys.argv.index('--') + 1]
TMP = tempfile.mkdtemp(prefix='bath_tex_')
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
rng = np.random.default_rng(11)
rnd = random.Random(5)

X0, X1, Y0, Y1, H = -1.8, 1.8, -1.3, 1.3, 2.7
XP = -0.2
STEP = 0.08          # shell grid spacing (the baked light resolution)

# ---------------------------------------------------------------- textures
def smooth_noise(n, size):
    g = rng.random((n + 1, n + 1))
    xs = np.linspace(0, n, size, endpoint=False); i = xs.astype(int); f = xs - i; f = f * f * (3 - 2 * f)
    rows = g[i] * (1 - f)[:, None] + g[i + 1] * f[:, None]
    return rows[:, i] * (1 - f)[None, :] + rows[:, i + 1] * f[None, :]

def save_img(name, arr):
    size = arr.shape[0]
    img = bpy.data.images.new(name, size, size, alpha=False)
    rgba = np.ones((size, size, 4), dtype=np.float32); rgba[..., :3] = np.clip(arr, 0, 1)
    img.pixels.foreach_set(rgba.ravel())
    path = os.path.join(TMP, name + '.png')
    img.filepath_raw = path; img.file_format = 'PNG'; img.save()
    out = bpy.data.images.load(path); out.pack()
    return out

def stone_tile_sheet(name, base, veins=0.05, tone=0.05, S=2048):
    """2x2 large-format stone tiles: veining, mottling, speckle, grout and soft edge shading."""
    T = S // 2
    n1, n2, n3 = smooth_noise(5, S), smooth_noise(22, S), smooth_noise(140, S)
    yy, xx = np.mgrid[0:S, 0:S] / S
    vein = np.sin((xx * 7 + yy * 3 + n1 * 3.2) * 6.283) * 0.5 + 0.5
    vein = np.clip((vein - 0.82) * 5, 0, 1) * (n2 > 0.45)
    v = 1 + 0.07 * (n1 - .5) * 2 + 0.04 * (n2 - .5) * 2 + 0.03 * (n3 - .5) * 2 - veins * vein
    v = v + rng.normal(0, 0.007, (S, S))
    v = v * np.kron(1 + rng.uniform(-tone, tone, (2, 2)), np.ones((T, T)))
    idx = np.arange(S) % T
    d = np.minimum(idx, T - idx).astype(float)
    edge = np.exp(-d / 22.0)
    v = v * (1 - 0.07 * np.maximum(edge[:, None], edge[None, :]))
    arr = np.array(base)[None, None, :] * v[..., None]
    gm = (d < 5)[:, None] | (d < 5)[None, :]
    arr[gm] = np.array(base) * 0.58
    return save_img(name, arr)

def wood_sheet(name, base, S=1024):
    streak = np.repeat(rng.random(S)[:, None], S, axis=1) * 0.45 + smooth_noise(160, S) * 0.35 + smooth_noise(30, S) * 0.2
    ring = np.sin((np.arange(S)[:, None] / S * 38 + smooth_noise(6, S) * 4) * 6.283) * 0.5 + 0.5
    v = 0.80 + 0.30 * (streak - .5) + 0.10 * (ring - .5) + 0.08 * (smooth_noise(4, S) - .5)
    return save_img(name, np.array(base)[None, None, :] * v[..., None])

def counter_sheet(name, base, S=1024):
    n1, n3 = smooth_noise(6, S), smooth_noise(180, S)
    v = 1 + 0.03 * (n1 - .5) * 2 + 0.05 * (n3 - .5) * 2
    flecks = (smooth_noise(230, S) > 0.80) * 0.14
    return save_img(name, np.array(base)[None, None, :] * (v - flecks)[..., None])

def img_mat(name, img, rough=0.5, metal=0.0):
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree; b = nt.nodes['Principled BSDF']
    tex = nt.nodes.new('ShaderNodeTexImage'); tex.image = img
    nt.links.new(tex.outputs['Color'], b.inputs['Base Color'])
    b.inputs['Roughness'].default_value = rough; b.inputs['Metallic'].default_value = metal
    return m

def mat(name, color, rough=0.5, metal=0.0, emit=None, alpha=None):
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = color
    b.inputs['Roughness'].default_value = rough; b.inputs['Metallic'].default_value = metal
    if emit:
        b.inputs['Emission Color'].default_value = emit[0]; b.inputs['Emission Strength'].default_value = emit[1]
    if alpha is not None:
        b.inputs['Alpha'].default_value = alpha
        try: m.surface_render_method = 'BLENDED'
        except Exception: pass
    return m

M = {
    'grey': img_mat('Grey Stone Tile', stone_tile_sheet('grey_tile', (0.60, 0.60, 0.58), 0.05), 0.45),
    'beige': img_mat('Beige Stone Tile', stone_tile_sheet('beige_stone', (0.80, 0.66, 0.48), 0.06), 0.5),
    'oak': img_mat('Oak', wood_sheet('oak', (0.74, 0.55, 0.34)), 0.5),
    'stone': img_mat('Counter Stone', counter_sheet('counter', (0.90, 0.88, 0.84)), 0.3),
    'ceiling': mat('Ceiling', (0.93, 0.92, 0.90, 1), 0.95),
    'white': mat('Gloss Ceramic', (0.96, 0.96, 0.95, 1), 0.06),
    'brass': mat('Bronze Brass', (0.62, 0.44, 0.22, 1), 0.3, 1.0),
    'black': mat('Black Metal', (0.025, 0.025, 0.025, 1), 0.4, 0.8),
    'glass': mat('Glass', (0.85, 0.95, 0.95, 1), 0.04, 0.0, alpha=0.14),
    'rug': mat('Cream Rug', (0.86, 0.80, 0.70, 1), 1.0),
    'towel': mat('Towel', (0.82, 0.74, 0.62, 1), 1.0),
    'towel2': mat('Towel Sage', (0.55, 0.62, 0.52, 1), 1.0),
    'leaf': mat('Leaf', (0.16, 0.30, 0.11, 1), 0.6),
    'stem': mat('Stem', (0.25, 0.30, 0.14, 1), 0.7),
    'pot': mat('Matte Pot', (0.80, 0.77, 0.72, 1), 0.8),
    'glow': mat('Warm Glow', (1, .8, .55, 1), 0.5, 0.0, emit=((1, .72, .4, 1), 3.0)),
    'sky': mat('Sky', (1, 1, 1, 1), 1.0, 0.0, emit=((.85, .92, 1, 1), 2.5)),
    'bulb': mat('Bulb', (1, .85, .6, 1), 0.3, 0.0, emit=((1, .8, .5, 1), 6.0)),
    'paper': mat('Paper', (0.95, 0.95, 0.93, 1), 0.9),
}

# ---------------------------------------------------------------- helpers
SHELL = []   # (object, nx, ny): surfaces that get baked light

def grid(name, origin, u, v, m, tile=1.2):
    """Subdivided single-sided surface. u = along the bottom edge, v = up; normal = u x v (faces into the room)."""
    origin, u, v = Vector(origin), Vector(u), Vector(v)
    ul, vl = u.length, v.length
    nx, ny = max(1, round(ul / STEP)), max(1, round(vl / STEP))
    verts = [tuple(origin + u * (i / nx) + v * (j / ny)) for j in range(ny + 1) for i in range(nx + 1)]
    faces = [(j * (nx + 1) + i, j * (nx + 1) + i + 1, (j + 1) * (nx + 1) + i + 1, (j + 1) * (nx + 1) + i)
             for j in range(ny) for i in range(nx)]
    me = bpy.data.meshes.new('Shell_' + name); me.from_pydata(verts, [], faces)
    uv = me.uv_layers.new(name='UV')
    for poly in me.polygons:
        for li, vi in zip(poly.loop_indices, poly.vertices):
            uv.data[li].uv = ((vi % (nx + 1)) * ul / nx / tile, (vi // (nx + 1)) * vl / ny / tile)
    ob = bpy.data.objects.new('Shell_' + name, me); scene.collection.objects.link(ob)
    me.materials.append(m)
    attr = me.color_attributes.new('Col', 'FLOAT_COLOR', 'POINT')
    me.color_attributes.active_color = attr
    SHELL.append((ob, nx, ny))
    return ob

def box(name, loc, dim, m, bevel=0.0, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc, rotation=rot)
    o = bpy.context.active_object; o.name = name; o.scale = dim
    bpy.ops.object.transform_apply(scale=True); o.data.materials.append(m)
    if bevel:
        bv = o.modifiers.new('Bevel', 'BEVEL'); bv.width = bevel; bv.segments = 3
        bpy.ops.object.modifier_apply(modifier=bv.name)
    return o

def cyl(name, loc, r, h, m, rot=(0, 0, 0), seg=40):
    bpy.ops.mesh.primitive_cylinder_add(vertices=seg, radius=r, depth=h, location=loc, rotation=rot)
    o = bpy.context.active_object; o.name = name; o.data.materials.append(m)
    bpy.ops.object.shade_smooth(); return o

def sphere(name, loc, scale, m, seg=48, rings=24, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=seg, ring_count=rings, location=loc, rotation=rot)
    o = bpy.context.active_object; o.name = name; o.scale = scale
    bpy.ops.object.transform_apply(scale=True); o.data.materials.append(m)
    bpy.ops.object.shade_smooth(); return o

def between(name, p0, p1, r, m, seg=10):
    p0, p1 = Vector(p0), Vector(p1); d = p1 - p0
    bpy.ops.mesh.primitive_cylinder_add(vertices=seg, radius=r, depth=d.length, location=(p0 + p1) / 2)
    o = bpy.context.active_object; o.name = name; o.rotation_euler = d.to_track_quat('Z', 'Y').to_euler()
    o.data.materials.append(m); return o

def subtract(a, b):
    md = a.modifiers.new('cut', 'BOOLEAN'); md.operation = 'DIFFERENCE'; md.object = b
    bpy.context.view_layer.objects.active = a; bpy.ops.object.modifier_apply(modifier=md.name)
    bpy.data.objects.remove(b)

def join(objs, name):
    bpy.ops.object.select_all(action='DESELECT')
    for o in objs: o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]; bpy.ops.object.join()
    bpy.context.active_object.name = name; return bpy.context.active_object

def plant(name, base, height, m_pot, pot_r, stems=8):
    parts = [cyl(name + ' pot', (base[0], base[1], base[2] + 0.07), pot_r, 0.14, m_pot, seg=24)]
    top = Vector((base[0], base[1], base[2] + 0.14))
    for k in range(stems):
        a = k * 2 * math.pi / stems + rnd.uniform(-0.3, 0.3); lean = rnd.uniform(0.12, 0.32) * height
        tip = top + Vector((math.cos(a) * lean, math.sin(a) * lean, height * rnd.uniform(0.75, 1.0)))
        parts.append(between('stem', top, tip, 0.004, M['stem'], seg=5))
        for t in (0.35, 0.5, 0.65, 0.8, 0.95):
            pt = top.lerp(tip, t)
            for side in (-1, 1):
                lf = sphere('leaf', pt + Vector((math.cos(a + side * 1.5) * 0.012, math.sin(a + side * 1.5) * 0.012, 0)),
                            (0.011, 0.0045, 0.03), M['leaf'], seg=8, rings=5,
                            rot=(rnd.uniform(-.5, .5), rnd.uniform(-.7, .7), a + side * 1.2))
                parts.append(lf)
    return join(parts, name)

# ---------------------------------------------------------------- shell (baked surfaces)
grid('Floor Vanity', (X0, Y0, 0), (XP - X0, 0, 0), (0, Y1 - Y0, 0), M['grey'])
grid('Floor Wet', (XP, Y0, 0), (X1 - XP, 0, 0), (0, Y1 - Y0, 0), M['beige'])
grid('Ceiling', (X0, Y1, H), (X1 - X0, 0, 0), (0, -(Y1 - Y0), 0), M['ceiling'], tile=3.0)
grid('Back Vanity', (X0, Y1, 0), (XP - X0, 0, 0), (0, 0, H), M['grey'])
grid('Back Wet', (XP, Y1, 0), (X1 - XP, 0, 0), (0, 0, H), M['beige'])
grid('Left Wall', (X0, Y0, 0), (0, Y1 - Y0, 0), (0, 0, H), M['grey'])
wy0, wy1, wz0, wz1 = -0.45, 0.65, 1.15, 2.1
grid('Right Below', (X1, Y1, 0), (0, -(Y1 - Y0), 0), (0, 0, wz0), M['beige'])
grid('Right Above', (X1, Y1, wz1), (0, -(Y1 - Y0), 0), (0, 0, H - wz1), M['beige'])
grid('Right Front', (X1, wy0, wz0), (0, -(wy0 - Y0), 0), (0, 0, wz1 - wz0), M['beige'])
grid('Right Back', (X1, Y1, wz0), (0, -(Y1 - wy1), 0), (0, 0, wz1 - wz0), M['beige'])
# window reveal (deep frame) so the opening has thickness
for nm, loc, dim in [('Reveal Top', (X1 + 0.06, (wy0 + wy1) / 2, wz1), (0.12, wy1 - wy0, 0.01)),
                     ('Reveal Bottom', (X1 + 0.06, (wy0 + wy1) / 2, wz0), (0.12, wy1 - wy0, 0.01)),
                     ('Reveal Front', (X1 + 0.06, wy0, (wz0 + wz1) / 2), (0.12, 0.01, wz1 - wz0)),
                     ('Reveal Back', (X1 + 0.06, wy1, (wz0 + wz1) / 2), (0.12, 0.01, wz1 - wz0))]:
    box(nm, loc, dim, M['beige'])
fr = [box('wf', (X1 - 0.03, (wy0 + wy1) / 2, wz0 + 0.02), (0.06, wy1 - wy0, 0.04), M['black']),
      box('wf', (X1 - 0.03, (wy0 + wy1) / 2, wz1 - 0.02), (0.06, wy1 - wy0, 0.04), M['black']),
      box('wf', (X1 - 0.03, wy0 + 0.02, (wz0 + wz1) / 2), (0.06, 0.04, wz1 - wz0), M['black']),
      box('wf', (X1 - 0.03, wy1 - 0.02, (wz0 + wz1) / 2), (0.06, 0.04, wz1 - wz0), M['black']),
      box('wf', (X1 - 0.03, (wy0 + wy1) / 2, (wz0 + wz1) / 2), (0.05, 0.03, wz1 - wz0), M['black'])]
join(fr, 'Window Frame')
sky = box('Window Sky', (X1 + 0.14, (wy0 + wy1) / 2, (wz0 + wz1) / 2), (0.02, wy1 - wy0 + 0.1, wz1 - wz0 + 0.1), M['sky'])
sky.visible_shadow = False
box('Window Ledge', (X1 - 0.07, (wy0 + wy1) / 2, wz0 - 0.015), (0.14, wy1 - wy0 + 0.1, 0.03), M['stone'], bevel=0.003)
box('Ledge Glow', (X1 - 0.07, (wy0 + wy1) / 2, wz0 - 0.04), (0.12, wy1 - wy0, 0.012), M['glow'])
box('Cove Glow', (X1 - 0.08, 0, H - 0.05), (0.12, Y1 - Y0 - 0.1, 0.02), M['glow'])
box('Cove Return', (0, Y1 - 0.08, H - 0.05), (X1 - X0 - 0.1, 0.12, 0.02), M['glow'])
for sx, sy in [(-1.0, 0.45), (-1.0, -0.45), (0.5, 0.5), (0.5, -0.4), (1.25, 0.6), (-1.5, 0.0)]:
    cyl('Downlight', (sx, sy, H - 0.006), 0.05, 0.012, M['bulb'], seg=24)

# ---------------------------------------------------------------- ZONE 1: vanity
VX, VY = -1.0, Y1 - 0.26
box('Vanity Cabinet', (VX, VY, 0.56), (1.4, 0.5, 0.52), M['oak'], bevel=0.006)
ribs = [box('rib', (VX - 0.67 + i * 0.0285, VY - 0.255, 0.70), (0.016, 0.012, 0.20), M['oak'], bevel=0.002) for i in range(48)]
join(ribs, 'Ribbed Drawer Front')
box('Drawer Line', (VX, VY - 0.253, 0.595), (1.38, 0.004, 0.006), M['brass'])
box('Drawer Split', (VX, VY - 0.253, 0.42), (0.005, 0.004, 0.25), M['brass'])
box('Vanity Top', (VX, VY - 0.01, 0.835), (1.5, 0.54, 0.035), M['stone'], bevel=0.004)
box('Vanity Underglow', (VX, VY - 0.02, 0.295), (1.3, 0.42, 0.01), M['glow'])
bowl = sphere('Vessel Basin', (VX, VY - 0.03, 0.93), (0.34, 0.21, 0.11), M['white'], seg=64, rings=32)
subtract(bowl, sphere('cut', (VX, VY - 0.03, 0.975), (0.31, 0.18, 0.10), M['white'], seg=64, rings=32))
cyl('Basin Spout', (VX, Y1 - 0.09, 1.15), 0.012, 0.18, M['brass'], rot=(math.pi / 2, 0, 0))
cyl('Spout Tip', (VX, Y1 - 0.175, 1.14), 0.012, 0.03, M['brass'], rot=(0, 0, 0))
for dx in (-0.3, 0.3):
    cyl('Tap Plate', (VX + dx, Y1 - 0.015, 1.12), 0.04, 0.03, M['brass'], rot=(math.pi / 2, 0, 0))
    cyl('Tap Knob', (VX + dx, Y1 - 0.04, 1.12), 0.016, 0.03, M['black'], rot=(math.pi / 2, 0, 0))
# round mirror: frame, glow ring, and a disc that will carry a real render of the room
cyl('Mirror Glow', (VX, Y1 - 0.045, 1.6), 0.51, 0.01, M['glow'], rot=(math.pi / 2, 0, 0))
cyl('Mirror Frame', (VX, Y1 - 0.052, 1.6), 0.472, 0.012, M['black'], rot=(math.pi / 2, 0, 0))
MR, MZ, MY = 0.46, 1.6, Y1 - 0.060
me = bpy.data.meshes.new('Mirror_Reflection'); N = 64
verts = [(VX, MY, MZ)] + [(VX + MR * math.cos(2 * math.pi * k / N), MY, MZ + MR * math.sin(2 * math.pi * k / N)) for k in range(N)]
me.from_pydata(verts, [], [(0, 1 + k, 1 + (k + 1) % N) for k in range(N)])
uvl = me.uv_layers.new(name='UV')
for poly in me.polygons:
    for li, vi in zip(poly.loop_indices, poly.vertices):
        x, _, z = verts[vi]; uvl.data[li].uv = (0.5 + (x - VX) / (2 * MR), 0.5 + (z - MZ) / (2 * MR))
mirror = bpy.data.objects.new('Mirror_Reflection', me); scene.collection.objects.link(mirror)
mirror_mat = mat('Mirror', (0.7, 0.72, 0.75, 1), 0.05, 0.0)
me.materials.append(mirror_mat)
# pendant
cyl('Pendant Cord', (-1.62, 0.85, (H + 1.75) / 2), 0.004, H - 1.75, M['brass'])
cyl('Pendant Cap', (-1.62, 0.85, 1.78), 0.015, 0.03, M['brass'])
cyl('Pendant Glass', (-1.62, 0.85, 1.62), 0.075, 0.2, M['glass'])
sphere('Pendant Bulb', (-1.62, 0.85, 1.6), (0.03, 0.03, 0.045), M['bulb'], seg=16, rings=10)
# towels + rail
cyl('Towel Bar', (X0 + 0.04, 0.30, 1.25), 0.008, 0.55, M['brass'], rot=(math.pi / 2, 0, 0))
for yy in (0.12, 0.48):
    box('Towel Bracket', (X0 + 0.025, yy, 1.25), (0.05, 0.015, 0.02), M['brass'])
box('Towel', (X0 + 0.04, 0.20, 0.97), (0.035, 0.20, 0.56), M['towel'], bevel=0.008)
box('Towel Sage', (X0 + 0.04, 0.45, 1.00), (0.035, 0.20, 0.50), M['towel2'], bevel=0.008)
box('Floor Rug', (-1.0, -0.45, 0.012), (1.1, 0.65, 0.024), M['rug'], bevel=0.008)
plant('Counter Plant', (-0.45, VY - 0.12, 0.853), 0.28, M['pot'], 0.045, stems=7)

# ---------------------------------------------------------------- ZONE 2: shower
box('Glass Partition', (XP, 0.45, 1.05), (0.012, 1.7, 2.1), M['glass'])
box('Partition Frame Top', (XP, 0.45, 2.1), (0.025, 1.7, 0.025), M['black'])
box('Partition Frame Front', (XP, -0.4, 1.05), (0.025, 0.025, 2.1), M['black'])
box('Partition Foot', (XP, 0.45, 0.012), (0.03, 1.7, 0.024), M['black'])
box('Partition Brace', (XP + 0.25, 0.45, 2.1), (0.5, 0.015, 0.015), M['black'])
SX = 0.5
cyl('Shower Riser', (SX, Y1 - 0.04, 2.25), 0.012, 0.3, M['brass'])
cyl('Shower Arm', (SX, Y1 - 0.2, 2.4), 0.012, 0.34, M['brass'], rot=(math.pi / 2, 0, 0))
cyl('Rain Head', (SX, Y1 - 0.42, 2.37), 0.14, 0.02, M['brass'], seg=64)
cyl('Rain Head Face', (SX, Y1 - 0.42, 2.358), 0.125, 0.004, M['black'], seg=64)
cyl('Mixer Plate', (SX + 0.3, Y1 - 0.015, 1.15), 0.05, 0.03, M['brass'], rot=(math.pi / 2, 0, 0))
cyl('Mixer Knob', (SX + 0.3, Y1 - 0.04, 1.15), 0.02, 0.03, M['black'], rot=(math.pi / 2, 0, 0))
cyl('Hand Shower Bar', (SX + 0.52, Y1 - 0.04, 1.55), 0.01, 0.75, M['brass'])
cyl('Hand Shower', (SX + 0.52, Y1 - 0.09, 1.5), 0.018, 0.2, M['black'])
cu = bpy.data.curves.new('Hose', 'CURVE'); cu.dimensions = '3D'; cu.bevel_depth = 0.007; cu.bevel_resolution = 3; cu.resolution_u = 10
sp = cu.splines.new('NURBS'); pts = [(0.52, 0.10, 1.40), (0.54, 0.12, 1.15), (0.57, 0.15, 0.92), (0.56, 0.19, 0.78), (0.50, 0.20, 0.74),
                                     (0.44, 0.17, 0.80), (0.42, 0.12, 0.92), (0.41, 0.06, 1.02), (0.40, 0.025, 1.08)]
sp.points.add(len(pts) - 1)
for p, (px, py, pz) in zip(sp.points, pts): p.co = (SX + px, Y1 - py, pz, 1)
sp.order_u = 4; sp.use_endpoint_u = True
hose = bpy.data.objects.new('Shower Hose', cu); scene.collection.objects.link(hose); cu.materials.append(M['black'])
bpy.context.view_layer.objects.active = hose; bpy.ops.object.convert(target='MESH')
box('Niche Shelf', (SX - 0.1, Y1 - 0.06, 1.05), (0.75, 0.12, 0.03), M['stone'], bevel=0.003)
box('Niche Glow', (SX - 0.1, Y1 - 0.06, 1.55), (0.73, 0.1, 0.012), M['glow'])
box('Floor Drain', (0.35, 0.12, 0.004), (0.9, 0.045, 0.008), M['brass'])
box('Shower Kerb', (0.4, -0.35, 0.012), (1.2, 0.012, 0.024), M['black'])

# ---------------------------------------------------------------- ZONE 3: toilet
TXc = 1.35
sphere('WC Bowl', (TXc, Y1 - 0.30, 0.40), (0.19, 0.30, 0.20), M['white'], seg=64, rings=32)
box('WC Back', (TXc, Y1 - 0.09, 0.42), (0.36, 0.17, 0.34), M['white'], bevel=0.07)
sphere('WC Seat', (TXc, Y1 - 0.31, 0.585), (0.205, 0.285, 0.022), M['white'], seg=64, rings=16)
box('Flush Plate', (TXc, Y1 - 0.012, 1.0), (0.22, 0.02, 0.14), M['black'], bevel=0.004)
box('Flush Button A', (TXc - 0.045, Y1 - 0.024, 1.0), (0.07, 0.01, 0.05), M['brass'], bevel=0.003)
box('Flush Button B', (TXc + 0.045, Y1 - 0.024, 1.0), (0.07, 0.01, 0.05), M['brass'], bevel=0.003)
cyl('Paper Roll', (X1 - 0.08, 0.85, 0.85), 0.055, 0.10, M['paper'], rot=(0, math.pi / 2, 0))
cyl('Paper Bar', (X1 - 0.07, 0.85, 0.85), 0.007, 0.13, M['brass'], rot=(0, math.pi / 2, 0))
box('Paper Bracket', (X1 - 0.02, 0.85, 0.85), (0.04, 0.04, 0.02), M['brass'])
plant('Ledge Plant', (X1 - 0.07, 0.38, wz0), 0.30, M['pot'], 0.05, stems=8)
plant('Floor Plant', (1.52, -1.05, 0), 0.75, M['pot'], 0.11, stems=10)

# ---------------------------------------------------------------- lights
def area(name, loc, size, energy, color, rot, size_y=None):
    ld = bpy.data.lights.new(name, 'AREA'); ld.energy = energy; ld.color = color; ld.shape = 'RECTANGLE'
    ld.size = size; ld.size_y = size_y or size
    lo = bpy.data.objects.new(name, ld); lo.location = loc; lo.rotation_euler = rot; scene.collection.objects.link(lo)
def spot(name, loc, energy):
    ld = bpy.data.lights.new(name, 'SPOT'); ld.energy = energy; ld.color = (1.0, 0.82, 0.62)
    ld.spot_size = math.radians(85); ld.spot_blend = 0.7; ld.shadow_soft_size = 0.05
    lo = bpy.data.objects.new(name, ld); lo.location = loc; scene.collection.objects.link(lo)
area('Sky', (X1 - 0.2, 0.1, 1.6), 1.0, 70, (0.85, 0.92, 1.0), (0, math.radians(-90), 0), 0.9)
ld = bpy.data.lights.new('Sun', 'SUN'); ld.energy = 4.0; ld.angle = math.radians(2.5); ld.color = (1.0, 0.93, 0.8)
sun = bpy.data.objects.new('Sun', ld); sun.rotation_euler = Vector((-0.78, 0.30, -0.5)).to_track_quat('-Z', 'Y').to_euler()
scene.collection.objects.link(sun)
area('Cove', (X1 - 0.1, 0, H - 0.08), 2.4, 30, (1.0, 0.72, 0.45), (0, math.radians(120), 0), 0.15)
area('Mirror', (VX, Y1 - 0.25, 1.6), 0.8, 24, (1.0, 0.8, 0.62), (math.radians(90), 0, 0), 0.8)
area('Underglow', (VX, VY, 0.25), 1.2, 16, (1.0, 0.7, 0.4), (0, 0, 0), 0.4)
area('Niche', (SX - 0.1, Y1 - 0.2, 1.5), 0.7, 9, (1.0, 0.72, 0.45), (math.radians(90), 0, 0), 0.1)
area('Fill', (-0.2, -0.7, 2.55), 2.4, 14, (1.0, 0.95, 0.9), (math.radians(180), 0, 0), 1.6)
for sx, sy in [(-1.0, 0.45), (-1.0, -0.45), (0.5, 0.5), (0.5, -0.4), (1.25, 0.6), (-1.5, 0.0)]:
    spot('Spot', (sx, sy, H - 0.03), 110)
world = bpy.data.worlds.new('W'); scene.world = world; world.use_nodes = True
world.node_tree.nodes['Background'].inputs['Color'].default_value = (0.05, 0.05, 0.06, 1)
world.node_tree.nodes['Background'].inputs['Strength'].default_value = 0.3

# ---------------------------------------------------------------- bake light into the shell (vertex colours)
scene.render.engine = 'CYCLES'; scene.cycles.device = 'CPU'
scene.cycles.samples = 300
bpy.ops.object.select_all(action='DESELECT')
for ob, _, _ in SHELL: ob.select_set(True)
bpy.context.view_layer.objects.active = SHELL[0][0]
scene.render.bake.target = 'VERTEX_COLORS'
try:
    bpy.ops.object.bake(type='DIFFUSE', pass_filter={'DIRECT', 'INDIRECT'}, target='VERTEX_COLORS')
except TypeError:
    bpy.ops.object.bake(type='DIFFUSE', pass_filter={'DIRECT', 'INDIRECT'})

def box_blur(a):
    h, w = a.shape[:2]; p = np.pad(a, ((1, 1), (1, 1), (0, 0)), mode='edge')
    return sum(p[dy:dy + h, dx:dx + w] for dy in range(3) for dx in range(3)) / 9.0

cols = []
for ob, nx, ny in SHELL:
    attr = ob.data.color_attributes['Col']; n = len(ob.data.vertices)
    buf = np.zeros(n * 4, dtype=np.float32); attr.data.foreach_get('color', buf)
    a = buf.reshape(ny + 1, nx + 1, 4)[..., :3]
    a = box_blur(box_blur(a)); cols.append(a)
allv = np.concatenate([c.reshape(-1, 3) for c in cols])
lum = allv @ np.array([0.2126, 0.7152, 0.0722])
gain = 0.92 / max(1e-4, np.percentile(lum, 97))
print('BAKE gain', round(float(gain), 3), 'p50', round(float(np.percentile(lum, 50)), 3))
for (ob, nx, ny), a in zip(SHELL, cols):
    a = np.clip(a * gain, 0, 1)
    rgba = np.ones((ny + 1, nx + 1, 4), dtype=np.float32); rgba[..., :3] = a
    ob.data.color_attributes['Col'].data.foreach_set('color', rgba.ravel())
    ob.data.update()

# ---------------------------------------------------------------- mirror: render the room from the mirror, flip, use as texture
cam_d = bpy.data.cameras.new('Refl'); cam_d.lens = 22; cam_d.sensor_width = 36
refl = bpy.data.objects.new('Refl', cam_d); scene.collection.objects.link(refl)
refl.location = (VX, Y1 - 0.1, MZ - 0.05)
refl.rotation_euler = (Vector((VX + 0.15, Y0, 1.25)) - refl.location).to_track_quat('-Z', 'Y').to_euler()
scene.camera = refl; mirror.hide_render = True
# temporary front wall so the mirror reflects a closed room (removed again before the preview and export)
_n = len(SHELL)
front_wall = grid('Front Temp', (X1, Y0 - 0.01, 0), (-(X1 - X0), 0, 0), (0, 0, H), M['beige'])
front_wall.data.color_attributes['Col'].data.foreach_set('color', np.tile([0.55, 0.50, 0.44, 1.0], len(front_wall.data.vertices)).astype(np.float32))
SHELL.pop()
scene.render.resolution_x = scene.render.resolution_y = 768
scene.cycles.samples = 96; scene.cycles.use_denoising = True
scene.render.filepath = os.path.join(TMP, 'refl.png'); bpy.ops.render.render(write_still=True)
ri = bpy.data.images.load(os.path.join(TMP, 'refl.png')); w, h = ri.size
px = np.array(ri.pixels[:], dtype=np.float32).reshape(h, w, 4)[:, ::-1, :]
mimg = bpy.data.images.new('mirror_reflection', w, h, alpha=False); mimg.pixels.foreach_set(np.ascontiguousarray(px).ravel())
mp = os.path.join(TMP, 'mirror_reflection.png'); mimg.filepath_raw = mp; mimg.file_format = 'PNG'; mimg.save()
mimg2 = bpy.data.images.load(mp); mimg2.pack()
nt = mirror_mat.node_tree; b = nt.nodes['Principled BSDF']; t = nt.nodes.new('ShaderNodeTexImage'); t.image = mimg2
nt.links.new(t.outputs['Color'], b.inputs['Base Color']); nt.links.new(t.outputs['Color'], b.inputs['Emission Color'])
b.inputs['Emission Strength'].default_value = 0.7
mirror.hide_render = False
bpy.data.objects.remove(front_wall)

# ---------------------------------------------------------------- preview render + export
cam_d2 = bpy.data.cameras.new('Cam'); cam_d2.lens = 17
cam = bpy.data.objects.new('Cam', cam_d2); scene.collection.objects.link(cam)
cam.location = (-1.25, Y0 + 0.02, 1.5)
cam.rotation_euler = (Vector((0.0, Y1, 1.1)) - cam.location).to_track_quat('-Z', 'Y').to_euler()
scene.camera = cam; scene.view_settings.view_transform = 'AgX'
scene.render.resolution_x, scene.render.resolution_y = 1536, 1024
scene.cycles.samples = 96
scene.render.filepath = OUT + '/bath_v3_preview.png'; bpy.ops.render.render(write_still=True)
kw = dict(filepath=OUT + '/bath_v3.glb', export_format='GLB', export_apply=True, export_cameras=False, export_lights=False,
          export_image_format='JPEG', export_jpeg_quality=85)
try:
    bpy.ops.export_scene.gltf(export_vertex_color='ACTIVE', **kw)
except TypeError:
    bpy.ops.export_scene.gltf(**kw)
bpy.ops.wm.save_as_mainfile(filepath=OUT + '/bath_v3.blend')
print('DONE')
