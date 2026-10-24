# Bathroom v5, laid out from the reference photo (Gemini 2D render of the Quiet Bath):
#   back wall, left -> right:  VANITY (wall-hung walnut, undermount sink, backlit rect mirror)
#                              TOILET (one-piece) + two paper holders
#                              frameless GLASS PANEL at right angles to the wall (black clamps)
#                              SHOWER (chrome rain column) + black niche on the right wall
#   left wall: walnut DOOR.  White marble walls, dark veined stone floor, flat ceiling with downlights, no window.
#   blender -b -P build_bath_v5.py -- <out dir>
# Metres. x -2.2..2.2 (left..right), y -1.4..1.4 (front open .. back wall), z 0..2.7.
import bpy, math, sys, os, tempfile
import numpy as np
from mathutils import Vector

OUT = sys.argv[sys.argv.index('--') + 1]
TMP = tempfile.mkdtemp(prefix='bath5_')
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
rng = np.random.default_rng(31)
X0, X1, Y0, Y1, H = -2.2, 2.2, -1.4, 1.4, 2.7
STEP = 0.08
VX = -1.35            # vanity centre (x)
TX = 0.10             # toilet centre (x)
GX = 1.10             # glass panel (x)
SX = 1.65             # shower column (x)

# ---------------------------------------------------------------- textures
def sn(n, size):
    g = rng.random((n + 1, n + 1))
    xs = np.linspace(0, n, size, endpoint=False); i = xs.astype(int); f = xs - i; f = f * f * (3 - 2 * f)
    rows = g[i] * (1 - f)[:, None] + g[i + 1] * f[:, None]
    return rows[:, i] * (1 - f)[None, :] + rows[:, i + 1] * f[None, :]

def save_img(name, arr):
    size = arr.shape[0]
    img = bpy.data.images.new(name, size, size, alpha=False)
    rgba = np.ones((size, size, 4), dtype=np.float32); rgba[..., :3] = np.clip(arr, 0, 1)
    img.pixels.foreach_set(rgba.ravel())
    path = os.path.join(TMP, name + '.png'); img.filepath_raw = path; img.file_format = 'PNG'; img.save()
    out = bpy.data.images.load(path); out.pack(); return out

def marble_sheet(name, base, vein, strength, freq, angle, S=2048, seam=2, slab=1024):
    """Large marble slabs. Veins are long sweeping lines along one diagonal, gently bent by low-frequency
    noise (a small bend, so they never close into loops), fading in and out along their length, with a soft
    grey halo; a few thinner cross-veins; cloudy grey drifts; faint slab seams."""
    yy, xx = np.mgrid[0:S, 0:S] / S
    bend = sn(2, S) * 0.6 + sn(5, S) * 0.3 + sn(13, S) * 0.15 + sn(40, S) * 0.05
    p1 = 2 * np.pi * freq * (xx * math.cos(angle) + yy * math.sin(angle)) + 4.0 * bend
    s1 = np.sin(p1) ** 2
    fade1 = np.clip((sn(4, S) - 0.25) * 2.2, 0, 1)
    v1 = (np.exp(-s1 / 0.0035) + 0.28 * np.exp(-s1 / 0.05)) * fade1
    bend2 = sn(4, S) * 0.7 + sn(11, S) * 0.3
    p2 = 2 * np.pi * freq * 2.4 * (xx * math.cos(angle + 0.9) + yy * math.sin(angle + 0.9)) + 5.0 * bend2
    v2 = np.exp(-np.sin(p2) ** 2 / 0.0012) * 0.5 * np.clip((sn(3, S) - 0.45) * 3, 0, 1)
    cloud = 0.06 * (sn(3, S) - .5) * 2 + 0.03 * (sn(12, S) - .5) * 2
    k = np.clip(strength * (v1 + v2), 0, 1)[..., None]
    arr = np.array(base)[None, None, :] * (1 + cloud)[..., None] * (1 - k) + np.array(vein)[None, None, :] * k
    idx = np.arange(S) % slab; edge = (idx < seam) | (idx >= slab - seam)
    arr[edge[:, None] | edge[None, :]] *= 0.9
    return save_img(name, arr)

def wood_sheet(name, base, S=1024, vertical=False):
    streak = np.repeat(rng.random(S)[:, None], S, axis=1) * 0.45 + sn(170, S) * 0.35 + sn(30, S) * 0.2
    ring = np.sin((np.arange(S)[:, None] / S * 30 + sn(6, S) * 4) * 6.283) * 0.5 + 0.5
    v = 0.80 + 0.30 * (streak - .5) + 0.12 * (ring - .5) + 0.08 * (sn(4, S) - .5)
    arr = np.array(base)[None, None, :] * v[..., None]
    return save_img(name, arr.transpose(1, 0, 2) if vertical else arr)

def fur_sheet(name, base, S=512):
    v = 0.62 + 0.55 * sn(170, S) + 0.12 * (sn(14, S) - .5)
    return save_img(name, np.array(base)[None, None, :] * v[..., None])

def rubber_sheet(name, base, S=512):
    yy, xx = np.mgrid[0:S, 0:S] / S
    u = (xx * 14) % 1 - 0.5; w = (yy * 8) % 1 - 0.5
    d = np.sqrt(u * u + (w * 1.0) ** 2)
    hole = (d < 0.27).astype(float); ring = ((d >= 0.27) & (d < 0.33)).astype(float)
    v = 1 - 0.30 * hole + 0.06 * ring + 0.02 * (sn(60, S) - .5)
    return save_img(name, np.array(base)[None, None, :] * v[..., None])

def img_mat(name, img, rough=0.5, metal=0.0):
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree; b = nt.nodes['Principled BSDF']
    tex = nt.nodes.new('ShaderNodeTexImage'); tex.image = img
    nt.links.new(tex.outputs['Color'], b.inputs['Base Color'])
    b.inputs['Roughness'].default_value = rough; b.inputs['Metallic'].default_value = metal; return m

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

M = {
    'marble': img_mat('White Marble', marble_sheet('marble', (0.93, 0.93, 0.91), (0.40, 0.40, 0.42), 0.85, 1.3, -0.9), 0.18),
    'floor': img_mat('Dark Stone', marble_sheet('floorstone', (0.27, 0.27, 0.28), (0.58, 0.58, 0.60), 0.45, 0.9, 0.3, seam=3), 0.3),
    'walnut': img_mat('Walnut', wood_sheet('walnut', (0.50, 0.31, 0.17)), 0.45),
    'walnut_v': img_mat('Walnut Door', wood_sheet('walnut_v', (0.46, 0.27, 0.14), vertical=True), 0.4),
    'fur': img_mat('Sage Mat', fur_sheet('sage', (0.55, 0.66, 0.52)), 1.0),
    'rubber': img_mat('Shower Mat', rubber_sheet('rubber', (0.66, 0.72, 0.78)), 0.8),
    'ceiling': mat('Ceiling', (0.95, 0.95, 0.94, 1), 0.95),
    'quartz': mat('Quartz', (0.95, 0.95, 0.94, 1), 0.2),
    'white': mat('Ceramic', (0.96, 0.96, 0.95, 1), 0.08),
    'chrome': mat('Chrome', (0.84, 0.85, 0.87, 1), 0.12, 1.0),
    'black': mat('Black Metal', (0.02, 0.02, 0.02, 1), 0.4, 0.8),
    'blackmat': mat('Matte Black', (0.025, 0.025, 0.027, 1), 0.7),
    'glass': mat('Glass', (0.85, 0.95, 0.95, 1), 0.04, 0.0, alpha=0.13),
    'cream': mat('Cream Ceramic', (0.84, 0.80, 0.72, 1), 0.5),
    'amber': mat('Amber Glass', (0.28, 0.14, 0.05, 1), 0.2),
    'paper': mat('Paper', (0.95, 0.95, 0.93, 1), 0.9),
    'reed': mat('Reed', (0.72, 0.55, 0.32, 1), 0.8),
    'glow': mat('Warm Glow', (1, .85, .65, 1), 0.5, 0.0, emit=((1, .78, .5, 1), 2.0)),
    'bulb': mat('Downlight', (1, .9, .75, 1), 0.3, 0.0, emit=((1, .85, .6, 1), 6.0)),
}

# ---------------------------------------------------------------- helpers
SHELL = []
def grid(name, origin, u, v, m, tile=2.4):
    origin, u, v = Vector(origin), Vector(u), Vector(v)
    ul, vl = u.length, v.length; nx, ny = max(1, round(ul / STEP)), max(1, round(vl / STEP))
    verts = [tuple(origin + u * (i / nx) + v * (j / ny)) for j in range(ny + 1) for i in range(nx + 1)]
    faces = [(j * (nx + 1) + i, j * (nx + 1) + i + 1, (j + 1) * (nx + 1) + i + 1, (j + 1) * (nx + 1) + i) for j in range(ny) for i in range(nx)]
    me = bpy.data.meshes.new('Shell_' + name); me.from_pydata(verts, [], faces)
    uv = me.uv_layers.new(name='UV')
    for poly in me.polygons:
        for li, vi in zip(poly.loop_indices, poly.vertices):
            uv.data[li].uv = ((vi % (nx + 1)) * ul / nx / tile, (vi // (nx + 1)) * vl / ny / tile)
    ob = bpy.data.objects.new('Shell_' + name, me); scene.collection.objects.link(ob); me.materials.append(m)
    me.color_attributes.active_color = me.color_attributes.new('Col', 'FLOAT_COLOR', 'POINT')
    SHELL.append((ob, nx, ny)); return ob

def box(name, loc, dim, m, bevel=0.0, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc, rotation=rot)
    o = bpy.context.active_object; o.name = name; o.scale = dim
    bpy.ops.object.transform_apply(scale=True); o.data.materials.append(m)
    if bevel:
        bv = o.modifiers.new('Bevel', 'BEVEL'); bv.width = bevel; bv.segments = 3; bpy.ops.object.modifier_apply(modifier=bv.name)
    return o

def cyl(name, loc, r, h, m, rot=(0, 0, 0), seg=32):
    bpy.ops.mesh.primitive_cylinder_add(vertices=seg, radius=r, depth=h, location=loc, rotation=rot)
    o = bpy.context.active_object; o.name = name; o.data.materials.append(m); bpy.ops.object.shade_smooth(); return o

def subtract(a, b):
    md = a.modifiers.new('cut', 'BOOLEAN'); md.operation = 'DIFFERENCE'; md.object = b
    bpy.context.view_layer.objects.active = a; bpy.ops.object.modifier_apply(modifier=md.name); bpy.data.objects.remove(b)

def join(objs, name):
    bpy.ops.object.select_all(action='DESELECT')
    for o in objs: o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]; bpy.ops.object.join(); bpy.context.active_object.name = name
    return bpy.context.active_object

def rrect(name, plane, c, w, h, r, m, uvs=True):
    """Rounded-rectangle face. plane 'xz' faces -y (a wall facing the room); plane 'xy' faces +z (lies on the floor)."""
    pts = []; N = 8
    for cx, cy, a0 in [(w / 2 - r, h / 2 - r, 0), (-w / 2 + r, h / 2 - r, 90), (-w / 2 + r, -h / 2 + r, 180), (w / 2 - r, -h / 2 + r, 270)]:
        for k in range(N + 1):
            a = math.radians(a0 + 90 * k / N); pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    verts = [(c[0], c[1], c[2])] + [((c[0] + px) if plane == 'xz' else (c[0] + px), c[1] if plane == 'xz' else c[1] + py, (c[2] + py) if plane == 'xz' else c[2]) for px, py in pts]
    n = len(pts); me = bpy.data.meshes.new(name)
    me.from_pydata(verts, [], [(0, 1 + k, 1 + (k + 1) % n) for k in range(n)])
    uv = me.uv_layers.new(name='UV')
    for poly in me.polygons:
        for li, vi in zip(poly.loop_indices, poly.vertices):
            vx, vy, vz = verts[vi]; a, b = (vx - c[0], vz - c[2]) if plane == 'xz' else (vx - c[0], vy - c[1])
            uv.data[li].uv = (0.5 + a / w, 0.5 + b / h)
    ob = bpy.data.objects.new(name, me); scene.collection.objects.link(ob); me.materials.append(m); return ob

# ---------------------------------------------------------------- shell (baked light)
grid('Floor', (X0, Y0, 0), (X1 - X0, 0, 0), (0, Y1 - Y0, 0), M['floor'])
grid('Ceiling', (X0, Y1, H), (X1 - X0, 0, 0), (0, -(Y1 - Y0), 0), M['ceiling'], tile=3.0)
grid('Back Wall', (X0, Y1, 0), (X1 - X0, 0, 0), (0, 0, H), M['marble'])
grid('Left Wall', (X0, Y0, 0), (0, Y1 - Y0, 0), (0, 0, H), M['marble'])
# Right wall is ONE baked surface (so its light is continuous); the niche opening is cut out of it after
# the bake, along existing grid lines: y 1.00..0.68 (columns 5-9), z rows 12-17.
right = grid('Right Wall', (X1, Y1, 0), (0, -(Y1 - Y0), 0), (0, 0, H), M['marble'])
_dz = H / round(H / STEP)
ny0, ny1, nz0, nz1 = Y1 - 9 * 0.08, Y1 - 5 * 0.08, 12 * _dz, 17 * _dz
NY, NZ = (ny0 + ny1) / 2, (nz0 + nz1) / 2
# False ceiling: a 10 cm drop frame, 45 cm wide, round the left, back and right walls; a warm LED cove washes
# up into the raised centre; downlights sit in the frame. All frame faces are baked like the walls.
FD, FW = 0.10, 0.45
HD = H - FD
grid('Drop Left Under', (X0, Y1, HD), (FW, 0, 0), (0, -(Y1 - Y0), 0), M['ceiling'], tile=3.0)
grid('Drop Right Under', (X1 - FW, Y1, HD), (FW, 0, 0), (0, -(Y1 - Y0), 0), M['ceiling'], tile=3.0)
grid('Drop Back Under', (X0 + FW, Y1, HD), (X1 - X0 - 2 * FW, 0, 0), (0, -FW, 0), M['ceiling'], tile=3.0)
grid('Drop Left Face', (X0 + FW, Y0, HD), (0, Y1 - Y0, 0), (0, 0, FD), M['ceiling'], tile=3.0)
grid('Drop Right Face', (X1 - FW, Y1, HD), (0, -(Y1 - Y0), 0), (0, 0, FD), M['ceiling'], tile=3.0)
grid('Drop Back Face', (X0 + FW, Y1 - FW, HD), (X1 - X0 - 2 * FW, 0, 0), (0, 0, FD), M['ceiling'], tile=3.0)
GW = 0.025
box('Cove Glow Left', (X0 + FW + 0.02, 0, H - 0.01), (GW, Y1 - Y0 - 0.05, 0.01), M['glow'])
box('Cove Glow Right', (X1 - FW - 0.02, 0, H - 0.01), (GW, Y1 - Y0 - 0.05, 0.01), M['glow'])
box('Cove Glow Back', (0, Y1 - FW - 0.02, H - 0.01), (X1 - X0 - 2 * FW - 0.05, GW, 0.01), M['glow'])
box('Shadow Gap', (0, Y1 - 0.006, HD - 0.008), (X1 - X0, 0.012, 0.016), M['blackmat'])     # thin reveal where the frame meets the back wall
DOWNLIGHTS = [(VX, Y1 - FW / 2), (TX, Y1 - FW / 2), (SX, Y1 - FW / 2), (X0 + FW / 2, 0.15), (X0 + FW / 2, -0.85), (X1 - FW / 2, 0.15), (X1 - FW / 2, -0.85)]
for sx, sy in DOWNLIGHTS: cyl('Downlight', (sx, sy, HD - 0.006), 0.045, 0.012, M['bulb'], seg=24)

# ---------------------------------------------------------------- DOOR (left wall)
DY = -0.45
box('Door Leaf', (X0 + 0.045, DY, 1.04), (0.045, 0.90, 2.05), M['walnut_v'], bevel=0.003)
for zz in (0.62, 1.34): box('Door Groove', (X0 + 0.069, DY, zz), (0.004, 0.88, 0.006), M['blackmat'])
frame = [box('df', (X0 + 0.03, DY - 0.475, 1.06), (0.06, 0.05, 2.12), M['blackmat']),
         box('df', (X0 + 0.03, DY + 0.475, 1.06), (0.06, 0.05, 2.12), M['blackmat']),
         box('df', (X0 + 0.03, DY, 2.10), (0.06, 1.0, 0.05), M['blackmat'])]
join(frame, 'Door Frame')
cyl('Door Rose', (X0 + 0.075, DY + 0.36, 1.0), 0.026, 0.012, M['chrome'], rot=(0, math.pi / 2, 0))
box('Door Lever', (X0 + 0.10, DY + 0.28, 1.0), (0.05, 0.13, 0.018), M['chrome'], bevel=0.005)

# ---------------------------------------------------------------- ZONE 1: VANITY
cab = box('Vanity Cabinet', (VX, Y1 - 0.25, 0.56), (1.30, 0.50, 0.52), M['walnut'], bevel=0.004)
subtract(cab, box('cut', (VX, Y1 - 0.30, 0.80), (0.52, 0.34, 0.20), M['white']))
box('Door Gap', (VX - 0.15, Y1 - 0.502, 0.56), (0.005, 0.004, 0.52), M['blackmat'])
box('Drawer Gap', (VX + 0.25, Y1 - 0.502, 0.56), (0.80, 0.004, 0.005), M['blackmat'])
box('Cabinet Shadow Gap', (VX, Y1 - 0.502, 0.82), (1.30, 0.004, 0.005), M['blackmat'])
counter = box('Vanity Top', (VX, Y1 - 0.27, 0.835), (1.36, 0.54, 0.03), M['quartz'], bevel=0.003)
subtract(counter, box('cut', (VX, Y1 - 0.30, 0.835), (0.50, 0.32, 0.2), M['white']))
bw = box('Sink Shell', (VX, Y1 - 0.30, 0.77), (0.52, 0.34, 0.16), M['white'], bevel=0.004)
subtract(bw, box('cut', (VX, Y1 - 0.30, 0.80), (0.48, 0.30, 0.16), M['white']))
cyl('Drain', (VX, Y1 - 0.30, 0.722), 0.022, 0.006, M['chrome'])
cyl('Faucet Base', (VX, Y1 - 0.09, 0.865), 0.024, 0.03, M['chrome'])
cyl('Faucet Stem', (VX, Y1 - 0.09, 0.93), 0.013, 0.14, M['chrome'])
cyl('Faucet Spout', (VX, Y1 - 0.165, 0.995), 0.011, 0.15, M['chrome'], rot=(math.pi / 2, 0, 0))
cyl('Faucet Tip', (VX, Y1 - 0.235, 0.97), 0.012, 0.05, M['chrome'])
cyl('Faucet Lever', (VX + 0.035, Y1 - 0.09, 0.945), 0.007, 0.07, M['chrome'], rot=(0, math.pi / 2, 0))
# counter dressing (cups, soap)
for xx in (-1.88, -1.77): cyl('Tumbler', (xx, Y1 - 0.12, 0.895), 0.033, 0.09, M['cream'])
cyl('Soap Bottle', (-0.96, Y1 - 0.12, 0.92), 0.030, 0.14, M['cream']); cyl('Soap Pump', (-0.96, Y1 - 0.12, 1.0), 0.008, 0.04, M['chrome'])
# mirror: rounded rectangle with a glow behind and a real render of the room in front
rrect('Mirror Glow', 'xz', (VX, Y1 - 0.012, 1.45), 1.00, 0.72, 0.09, M['glow'])
mirror = rrect('Mirror_Reflection', 'xz', (VX, Y1 - 0.030, 1.45), 0.90, 0.62, 0.07, M['white'])

# ---------------------------------------------------------------- ZONE 2: TOILET (the Meshy toilet is placed in the viewer)
PROXIES = [box('Proxy Toilet', (TX, Y1 - 0.385, 0.39), (0.38, 0.77, 0.78), M['white'], bevel=0.05)]
cyl('Reed Bottle', (TX - 0.10, Y1 - 0.12, 0.78 + 0.045), 0.03, 0.09, M['amber'])
for i, a in enumerate(range(-2, 3)):
    cyl('Reed', (TX - 0.10 + a * 0.012, Y1 - 0.12, 0.78 + 0.16), 0.0025, 0.2, M['reed'], rot=(a * 0.07, 0, a * 0.05), seg=6)
for hx, roll in ((0.52, True), (0.95, False)):
    box('Holder Plate', (hx - 0.07, Y1 - 0.012, 0.72), (0.03, 0.022, 0.05), M['chrome'])
    cyl('Holder Bar', (hx, Y1 - 0.06, 0.72), 0.007, 0.15, M['chrome'], rot=(0, math.pi / 2, 0))
    box('Holder End', (hx + 0.075, Y1 - 0.04, 0.72), (0.012, 0.05, 0.03), M['chrome'])
    if roll: cyl('Paper Roll', (hx - 0.01, Y1 - 0.06, 0.72), 0.055, 0.10, M['paper'], rot=(0, math.pi / 2, 0))

# ---------------------------------------------------------------- GLASS PANEL + ZONE 3: SHOWER
box('Glass Panel', (GX, 0.70, 1.02), (0.010, 1.40, 2.00), M['glass'])
for zz in (0.35, 1.65): box('Panel Clamp', (GX, Y1 - 0.035, zz), (0.045, 0.07, 0.12), M['blackmat'])
box('Panel Foot Clamp', (GX, 0.05, 0.05), (0.04, 0.05, 0.08), M['blackmat'])
PROXIES.append(box('Proxy Shower Pole', (SX, Y1 - 0.03, 1.15), (0.05, 0.05, 2.1), M['black']))
PROXIES.append(box('Proxy Shower Head', (SX, Y1 - 0.34, 2.14), (0.30, 0.62, 0.04), M['black']))
box('Floor Drain', (SX, 0.35, 0.004), (0.7, 0.045, 0.008), M['chrome'])
# black niche recessed 10 cm into the right wall, with bottles on its floor. Its boxes start 1 mm behind the
# wall plane so no face of theirs lies in the wall surface (that flickered).
ND, E = 0.10, 0.001
nb = [box('n', (X1 + ND + 0.005, NY, NZ), (0.01, ny1 - ny0 + 0.02, nz1 - nz0 + 0.02), M['blackmat']),
      box('n', (X1 + E + ND / 2, NY, nz0 - 0.005), (ND, ny1 - ny0 + 0.02, 0.01), M['blackmat']), box('n', (X1 + E + ND / 2, NY, nz1 + 0.005), (ND, ny1 - ny0 + 0.02, 0.01), M['blackmat']),
      box('n', (X1 + E + ND / 2, ny0 - 0.005, NZ), (ND, 0.01, nz1 - nz0), M['blackmat']), box('n', (X1 + E + ND / 2, ny1 + 0.005, NZ), (ND, 0.01, nz1 - nz0), M['blackmat'])]
join(nb, 'Niche')
box('Niche Glow', (X1 + ND / 2, NY, nz1 - 0.008), (ND - 0.02, ny1 - ny0 - 0.03, 0.006), M['glow'])
cyl('Niche Bottle', (X1 + 0.05, NY - 0.09, nz0 + 0.09), 0.026, 0.18, M['blackmat'])
cyl('Niche Pump', (X1 + 0.05, NY - 0.09, nz0 + 0.20), 0.007, 0.04, M['chrome'])
cyl('Niche Jar', (X1 + 0.05, NY + 0.03, nz0 + 0.02), 0.035, 0.04, M['cream'])
cyl('Niche Vial', (X1 + 0.05, NY + 0.11, nz0 + 0.06), 0.022, 0.12, M['amber'])

# ---------------------------------------------------------------- mats
rug_mat = box('Mat Vanity Zone (see viewer rug)', (VX, 0.55, -5), (0.1, 0.1, 0.01), M['fur'])   # parked off-scene; the teal rug is placed in the viewer
bpy.data.objects.remove(rug_mat)
tm = box('Toilet Mat', (TX, 0.62, 0.014), (0.62, 0.50, 0.028), M['fur'], bevel=0.012)
subtract(tm, cyl('cut', (TX, 1.02, 0.014), 0.20, 0.2, M['fur'], seg=48))
# the shower mat is the Essentials PVC mat (staging/shower_mat.glb), placed in the viewer

# ---------------------------------------------------------------- lights
def area(name, loc, sx, sy, energy, color, rot):
    ld = bpy.data.lights.new(name, 'AREA'); ld.energy = energy; ld.color = color; ld.shape = 'RECTANGLE'; ld.size = sx; ld.size_y = sy
    lo = bpy.data.objects.new(name, ld); lo.location = loc; lo.rotation_euler = rot; scene.collection.objects.link(lo)
WARM = (1.0, 0.86, 0.68)
for sx, sy in DOWNLIGHTS:
    ld = bpy.data.lights.new('Spot', 'SPOT'); ld.energy = 120; ld.color = WARM; ld.spot_size = math.radians(88); ld.spot_blend = 0.75; ld.shadow_soft_size = 0.05
    lo = bpy.data.objects.new('Spot', ld); lo.location = (sx, sy, HD - 0.03); scene.collection.objects.link(lo)
area('Cove L', (X0 + FW + 0.05, 0, H - 0.02), 0.12, Y1 - Y0 - 0.1, 30, WARM, (0, math.radians(-35), 0))
area('Cove R', (X1 - FW - 0.05, 0, H - 0.02), 0.12, Y1 - Y0 - 0.1, 30, WARM, (0, math.radians(35), 0))
area('Cove B', (0, Y1 - FW - 0.05, H - 0.02), X1 - X0 - 2 * FW, 0.12, 30, WARM, (math.radians(-35), 0, 0))
area('Mirror Light', (VX, Y1 - 0.12, 1.45), 0.95, 0.65, 18, WARM, (math.radians(90), 0, 0))
area('Fill', (0, -0.2, H - 0.05), 4.0, 2.2, 22, (1.0, 0.95, 0.9), (math.radians(180), 0, 0))
world = bpy.data.worlds.new('W'); scene.world = world; world.use_nodes = True
world.node_tree.nodes['Background'].inputs['Color'].default_value = (0.05, 0.05, 0.06, 1); world.node_tree.nodes['Background'].inputs['Strength'].default_value = 0.3

# ---------------------------------------------------------------- bake light into the shell
scene.render.engine = 'CYCLES'; scene.cycles.device = 'CPU'; scene.cycles.samples = 300
bpy.ops.object.select_all(action='DESELECT')
for ob, _, _ in SHELL: ob.select_set(True)
bpy.context.view_layer.objects.active = SHELL[0][0]; scene.render.bake.target = 'VERTEX_COLORS'
try: bpy.ops.object.bake(type='DIFFUSE', pass_filter={'DIRECT', 'INDIRECT'}, target='VERTEX_COLORS')
except TypeError: bpy.ops.object.bake(type='DIFFUSE', pass_filter={'DIRECT', 'INDIRECT'})
def blur(a):
    h, w = a.shape[:2]; p = np.pad(a, ((1, 1), (1, 1), (0, 0)), mode='edge')
    return sum(p[dy:dy + h, dx:dx + w] for dy in range(3) for dx in range(3)) / 9.0
cols = []
for ob, nx, ny in SHELL:
    at = ob.data.color_attributes['Col']; buf = np.zeros(len(ob.data.vertices) * 4, dtype=np.float32); at.data.foreach_get('color', buf)
    cols.append(blur(blur(buf.reshape(ny + 1, nx + 1, 4)[..., :3])))
lum = np.concatenate([c.reshape(-1, 3) for c in cols]) @ np.array([0.2126, 0.7152, 0.0722])
gain = 0.92 / max(1e-4, np.percentile(lum, 97)); print('BAKE gain', round(float(gain), 3), 'p50', round(float(np.percentile(lum, 50)), 3))
for (ob, nx, ny), a in zip(SHELL, cols):
    rgba = np.ones((ny + 1, nx + 1, 4), dtype=np.float32); rgba[..., :3] = np.clip(a * gain, 0, 1)
    ob.data.color_attributes['Col'].data.foreach_set('color', rgba.ravel()); ob.data.update()
for pr in PROXIES: bpy.data.objects.remove(pr)
# now open the niche: delete the right-wall faces inside the opening (the light stays continuous round it)
import bmesh
bm = bmesh.new(); bm.from_mesh(right.data)
gone = [f for f in bm.faces if ny0 < f.calc_center_median().y < ny1 and nz0 < f.calc_center_median().z < nz1]
bmesh.ops.delete(bm, geom=gone, context='FACES'); bm.to_mesh(right.data); bm.free(); right.data.update()
print('NICHE faces removed', len(gone))

# ---------------------------------------------------------------- mirror texture: render the room from the mirror, flip, apply
refl_d = bpy.data.cameras.new('Refl'); refl_d.lens = 24
refl = bpy.data.objects.new('Refl', refl_d); scene.collection.objects.link(refl)
refl.location = (VX, Y1 - 0.08, 1.42); refl.rotation_euler = (Vector((-2.0, -0.6, 1.15)) - refl.location).to_track_quat('-Z', 'Y').to_euler()   # looks toward the door, as in the reference
scene.camera = refl; mirror.hide_render = True
fw = grid('Front Temp', (X1, Y0 - 0.01, 0), (-(X1 - X0), 0, 0), (0, 0, H), M['marble']); SHELL.pop()
fw.data.color_attributes['Col'].data.foreach_set('color', np.tile([0.5, 0.48, 0.45, 1.0], len(fw.data.vertices)).astype(np.float32))
scene.render.resolution_x = 900; scene.render.resolution_y = 620
scene.cycles.samples = 96; scene.cycles.use_denoising = True
scene.render.filepath = os.path.join(TMP, 'refl.png'); bpy.ops.render.render(write_still=True)
ri = bpy.data.images.load(os.path.join(TMP, 'refl.png')); w, h = ri.size
px = np.array(ri.pixels[:], dtype=np.float32).reshape(h, w, 4)[:, ::-1, :]
mi = bpy.data.images.new('mirror_reflection', w, h, alpha=False); mi.pixels.foreach_set(np.ascontiguousarray(px).ravel())
mp = os.path.join(TMP, 'mirror_reflection.png'); mi.filepath_raw = mp; mi.file_format = 'PNG'; mi.save()
mi2 = bpy.data.images.load(mp); mi2.pack()
mm = mirror.data.materials[0]; mm.name = 'Mirror'; nt = mm.node_tree; b = nt.nodes['Principled BSDF']
t = nt.nodes.new('ShaderNodeTexImage'); t.image = mi2; nt.links.new(t.outputs['Color'], b.inputs['Base Color']); nt.links.new(t.outputs['Color'], b.inputs['Emission Color'])
b.inputs['Emission Strength'].default_value = 0.35; b.inputs['Roughness'].default_value = 0.1
mirror.hide_render = False; bpy.data.objects.remove(fw)

# ---------------------------------------------------------------- previews: front (like the reference) and plan (to check the layout)
scene.view_settings.view_transform = 'AgX'; scene.render.resolution_x, scene.render.resolution_y = 1800, 760; scene.cycles.samples = 96
cam_d = bpy.data.cameras.new('Cam'); cam_d.lens = 15
cam = bpy.data.objects.new('Cam', cam_d); scene.collection.objects.link(cam)
cam.location = (0.0, Y0 + 0.05, 1.45); cam.rotation_euler = (Vector((0.0, Y1, 1.2)) - cam.location).to_track_quat('-Z', 'Y').to_euler()
scene.camera = cam; scene.render.filepath = OUT + '/bath_v5_front.png'; bpy.ops.render.render(write_still=True)
ceil = [o for o, _, _ in SHELL if o.name == 'Shell_Ceiling'][0]; ceil.hide_render = True
pd = bpy.data.cameras.new('Plan'); pd.type = 'ORTHO'; pd.ortho_scale = 5.2
pc = bpy.data.objects.new('Plan', pd); scene.collection.objects.link(pc); pc.location = (0, 0, 8); pc.rotation_euler = (0, 0, 0)
scene.camera = pc; scene.render.resolution_x = scene.render.resolution_y = 900; scene.render.filepath = OUT + '/bath_v5_plan.png'; bpy.ops.render.render(write_still=True)
ceil.hide_render = False

kw = dict(filepath=OUT + '/bath_v5.glb', export_format='GLB', export_apply=True, export_cameras=False, export_lights=False, export_image_format='JPEG', export_jpeg_quality=85)
try: bpy.ops.export_scene.gltf(export_vertex_color='ACTIVE', **kw)
except TypeError: bpy.ops.export_scene.gltf(**kw)
bpy.ops.wm.save_as_mainfile(filepath=OUT + '/bath_v5.blend'); print('DONE')
