# Indian-society bathroom, three zones: vanity (grey tile) | shower + toilet wet area (beige stone).
# Blender 5.2 headless:  blender -b -P build_bath_v2.py -- <out dir>
# Units are metres. Room: x -1.8..1.8 (3.6), y -1.3..1.3 (2.6, front wall left open), z 0..2.7.
import bpy, math, sys
import numpy as np
from mathutils import Vector

OUT = sys.argv[sys.argv.index('--') + 1]
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
rng = np.random.default_rng(7)

X0, X1, Y0, Y1, H = -1.8, 1.8, -1.3, 1.3, 2.7
XP = -0.2   # zone split: vanity side | wet side

# ---------- generated texture sheets (real images, so glTF can carry them) ----------
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
    path = OUT + '/tex_' + name + '.png'
    img.filepath_raw = path; img.file_format = 'PNG'; img.save()
    out = bpy.data.images.load(path); out.pack()
    return out

def tile_sheet(name, base, tone=0.05):
    S = 1024; T = 512
    n1, n2 = smooth_noise(6, S), smooth_noise(40, S)
    v = 1 + 0.07 * (n1 - .5) * 2 + 0.035 * (n2 - .5) * 2 + rng.normal(0, 0.006, (S, S))
    tt = 1 + rng.uniform(-tone, tone, (2, 2))
    v = v * np.kron(tt, np.ones((T, T)))
    arr = np.array(base)[None, None, :] * v[..., None]
    idx = np.arange(S) % T
    edge = (idx < 3) | (idx >= T - 3)
    g = edge[:, None] | edge[None, :]
    arr[g] = np.array(base) * 0.62
    return save_img(name, arr)

def wood_sheet(name, base):
    S = 512
    streak = np.repeat(rng.random(S)[:, None], S, axis=1) * 0.5 + smooth_noise(90, S) * 0.5
    low = smooth_noise(4, S)
    v = 0.86 + 0.28 * (streak - .5) + 0.10 * (low - .5)
    return save_img(name, np.array(base)[None, None, :] * v[..., None])

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

grey_img = tile_sheet('grey_tile', (0.62, 0.62, 0.60))
beige_img = tile_sheet('beige_stone', (0.80, 0.66, 0.48))
oak_img = wood_sheet('oak', (0.74, 0.55, 0.34))
M = {
    'grey': img_mat('Grey Tile', grey_img, 0.5),
    'beige': img_mat('Beige Stone', beige_img, 0.55),
    'oak': img_mat('Oak', oak_img, 0.5),
    'ceiling': mat('Ceiling', (0.93, 0.92, 0.90, 1), 0.9),
    'stone': mat('Counter Stone', (0.88, 0.86, 0.82, 1), 0.3),
    'white': mat('Gloss Ceramic', (0.96, 0.96, 0.95, 1), 0.06),
    'brass': mat('Bronze Brass', (0.62, 0.44, 0.22, 1), 0.3, 1.0),
    'black': mat('Black Metal', (0.025, 0.025, 0.025, 1), 0.4, 0.8),
    'glass': mat('Glass', (0.85, 0.95, 0.95, 1), 0.04, 0.0, alpha=0.14),
    'mirror': mat('Mirror', (0.66, 0.70, 0.73, 1), 0.08, 0.6),
    'rug': mat('Cream Rug', (0.86, 0.80, 0.70, 1), 1.0),
    'glow': mat('Warm Glow', (1, .8, .55, 1), 0.5, 0.0, emit=((1, .72, .4, 1), 3.0)),
    'sky': mat('Sky', (1, 1, 1, 1), 1.0, 0.0, emit=((.85, .92, 1, 1), 2.0)),
    'bulb': mat('Bulb', (1, .85, .6, 1), 0.3, 0.0, emit=((1, .8, .5, 1), 6.0)),
}

# ---------- helpers ----------
def quad(name, p, m, tile=1.2):
    """p = 4 points, bottom-left, bottom-right, top-right, top-left as seen from inside."""
    me = bpy.data.meshes.new(name); me.from_pydata([tuple(v) for v in p], [], [(0, 1, 2, 3)])
    ob = bpy.data.objects.new(name, me); scene.collection.objects.link(ob)
    uv = me.uv_layers.new(name='UV')
    u = (Vector(p[1]) - Vector(p[0])).length / tile; v = (Vector(p[3]) - Vector(p[0])).length / tile
    for li, (a, b) in enumerate([(0, 0), (u, 0), (u, v), (0, v)]): uv.data[li].uv = (a, b)
    ob.data.materials.append(m)
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

def sphere(name, loc, scale, m):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=48, ring_count=24, location=loc)
    o = bpy.context.active_object; o.name = name; o.scale = scale
    bpy.ops.object.transform_apply(scale=True); o.data.materials.append(m)
    bpy.ops.object.shade_smooth(); return o

def subtract(a, b):
    md = a.modifiers.new('cut', 'BOOLEAN'); md.operation = 'DIFFERENCE'; md.object = b
    bpy.context.view_layer.objects.active = a; bpy.ops.object.modifier_apply(modifier=md.name)
    bpy.data.objects.remove(b)

def join(objs, name):
    bpy.ops.object.select_all(action='DESELECT')
    for o in objs: o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]; bpy.ops.object.join()
    bpy.context.active_object.name = name; return bpy.context.active_object

# ---------- shell: single-sided surfaces, so the room can be orbited from outside ----------
quad('Floor Vanity Zone', [(X0, Y0, 0), (XP, Y0, 0), (XP, Y1, 0), (X0, Y1, 0)], M['grey'])
quad('Floor Wet Zone', [(XP, Y0, 0), (X1, Y0, 0), (X1, Y1, 0), (XP, Y1, 0)], M['beige'])
quad('Ceiling', [(X0, Y1, H), (X1, Y1, H), (X1, Y0, H), (X0, Y0, H)], M['ceiling'])
quad('Back Wall Vanity', [(X0, Y1, 0), (XP, Y1, 0), (XP, Y1, H), (X0, Y1, H)], M['grey'])
quad('Back Wall Wet', [(XP, Y1, 0), (X1, Y1, 0), (X1, Y1, H), (XP, Y1, H)], M['beige'])
quad('Left Wall', [(X0, Y0, 0), (X0, Y1, 0), (X0, Y1, H), (X0, Y0, H)], M['grey'])
wy0, wy1, wz0, wz1 = -0.45, 0.65, 1.15, 2.1   # window on the right wall
quad('Right Wall Below', [(X1, Y1, 0), (X1, Y0, 0), (X1, Y0, wz0), (X1, Y1, wz0)], M['beige'])
quad('Right Wall Above', [(X1, Y1, wz1), (X1, Y0, wz1), (X1, Y0, H), (X1, Y1, H)], M['beige'])
quad('Right Wall Front', [(X1, wy0, wz0), (X1, Y0, wz0), (X1, Y0, wz1), (X1, wy0, wz1)], M['beige'])
quad('Right Wall Back', [(X1, Y1, wz0), (X1, wy1, wz0), (X1, wy1, wz1), (X1, Y1, wz1)], M['beige'])
fr = []
fr.append(box('wf', (X1 - 0.03, (wy0 + wy1) / 2, wz0 + 0.02), (0.06, wy1 - wy0, 0.04), M['black']))
fr.append(box('wf', (X1 - 0.03, (wy0 + wy1) / 2, wz1 - 0.02), (0.06, wy1 - wy0, 0.04), M['black']))
fr.append(box('wf', (X1 - 0.03, wy0 + 0.02, (wz0 + wz1) / 2), (0.06, 0.04, wz1 - wz0), M['black']))
fr.append(box('wf', (X1 - 0.03, wy1 - 0.02, (wz0 + wz1) / 2), (0.06, 0.04, wz1 - wz0), M['black']))
join(fr, 'Window Frame')
box('Window Sky', (X1 + 0.1, (wy0 + wy1) / 2, (wz0 + wz1) / 2), (0.02, wy1 - wy0, wz1 - wz0), M['sky'])
box('Window Ledge', (X1 - 0.07, (wy0 + wy1) / 2, wz0 - 0.015), (0.14, wy1 - wy0 + 0.1, 0.03), M['stone'])
box('Ledge Glow', (X1 - 0.07, (wy0 + wy1) / 2, wz0 - 0.04), (0.12, wy1 - wy0, 0.012), M['glow'])
box('Cove Glow', (X1 - 0.08, 0, H - 0.05), (0.12, D := Y1 - Y0 - 0.1, 0.02), M['glow'])

# ---------- ZONE 1: vanity (wall-hung, ribbed oak, backlit mirror) ----------
VX, VY = -1.0, Y1 - 0.26
cab = box('Vanity Cabinet', (VX, VY, 0.56), (1.4, 0.5, 0.52), M['oak'], bevel=0.006)
ribs = []
for i in range(48):
    ribs.append(box('rib', (VX - 0.67 + i * 0.0285, VY - 0.255, 0.70), (0.016, 0.012, 0.20), M['oak']))
join(ribs, 'Ribbed Drawer Front')
box('Drawer Line', (VX, VY - 0.253, 0.595), (1.38, 0.004, 0.006), M['brass'])
box('Drawer Split', (VX, VY - 0.253, 0.42), (0.005, 0.004, 0.25), M['brass'])
box('Vanity Top', (VX, VY - 0.01, 0.835), (1.5, 0.54, 0.035), M['stone'], bevel=0.004)
box('Vanity Underglow', (VX, VY - 0.02, 0.295), (1.3, 0.42, 0.01), M['glow'])
bowl = sphere('Vessel Basin', (VX, VY - 0.03, 0.93), (0.34, 0.21, 0.11), M['white'])
subtract(bowl, sphere('cut', (VX, VY - 0.03, 0.975), (0.31, 0.18, 0.10), M['white']))
cyl('Basin Spout', (VX, Y1 - 0.09, 1.15), 0.012, 0.18, M['brass'], rot=(math.pi / 2, 0, 0))
for dx in (-0.3, 0.3):
    cyl('Tap Plate', (VX + dx, Y1 - 0.015, 1.12), 0.04, 0.03, M['brass'], rot=(math.pi / 2, 0, 0))
cyl('Mirror Glow', (VX, Y1 - 0.045, 1.6), 0.51, 0.01, M['glow'], rot=(math.pi / 2, 0, 0))
cyl('Mirror', (VX, Y1 - 0.055, 1.6), 0.46, 0.012, M['mirror'], rot=(math.pi / 2, 0, 0))
cyl('Mirror Frame', (VX, Y1 - 0.052, 1.6), 0.472, 0.012, M['black'], rot=(math.pi / 2, 0, 0))
# pendant light
cyl('Pendant Cord', (-1.62, 0.85, (H + 1.75) / 2), 0.004, H - 1.75, M['brass'])
cyl('Pendant Glass', (-1.62, 0.85, 1.62), 0.075, 0.2, M['glass'])
sphere('Pendant Bulb', (-1.62, 0.85, 1.6), (0.03, 0.03, 0.045), M['bulb'])
# towel ring + towel
cyl('Towel Ring', (X0 + 0.04, 0.35, 1.25), 0.04, 0.03, M['brass'], rot=(0, math.pi / 2, 0))
box('Towel', (X0 + 0.025, 0.35, 0.95), (0.03, 0.26, 0.55), mat('Towel', (0.82, 0.74, 0.62, 1), 1.0), bevel=0.008)
box('Floor Rug', (-1.0, -0.45, 0.01), (1.1, 0.65, 0.02), M['rug'], bevel=0.008)

# ---------- ZONE 2: shower (glass partition, rain head, niche, drain) ----------
box('Glass Partition', (XP, 0.45, 1.05), (0.012, 1.7, 2.1), M['glass'])
box('Partition Frame Top', (XP, 0.45, 2.1), (0.025, 1.7, 0.025), M['black'])
box('Partition Frame Front', (XP, -0.4, 1.05), (0.025, 0.025, 2.1), M['black'])
box('Partition Foot', (XP, 0.45, 0.012), (0.03, 1.7, 0.024), M['black'])
SX = 0.5
cyl('Shower Riser', (SX, Y1 - 0.04, 2.25), 0.012, 0.3, M['brass'])
cyl('Shower Arm', (SX, Y1 - 0.2, 2.4), 0.012, 0.34, M['brass'], rot=(math.pi / 2, 0, 0))
cyl('Rain Head', (SX, Y1 - 0.42, 2.37), 0.14, 0.02, M['brass'])
cyl('Mixer Plate', (SX + 0.3, Y1 - 0.015, 1.15), 0.05, 0.03, M['brass'], rot=(math.pi / 2, 0, 0))
cyl('Mixer Knob', (SX + 0.3, Y1 - 0.04, 1.15), 0.02, 0.03, M['black'], rot=(math.pi / 2, 0, 0))
cyl('Hand Shower Bar', (SX + 0.52, Y1 - 0.04, 1.55), 0.01, 0.75, M['brass'])
cyl('Hand Shower', (SX + 0.52, Y1 - 0.09, 1.5), 0.018, 0.2, M['black'])
box('Niche Shelf', (SX - 0.1, Y1 - 0.06, 1.05), (0.75, 0.12, 0.03), M['stone'])
box('Niche Glow', (SX - 0.1, Y1 - 0.06, 1.55), (0.73, 0.1, 0.012), M['glow'])
box('Floor Drain', (0.35, 0.12, 0.004), (0.9, 0.045, 0.008), M['brass'])

# ---------- ZONE 3: wall-hung toilet ----------
TXc = 1.35
sphere('WC Bowl', (TXc, Y1 - 0.30, 0.40), (0.19, 0.30, 0.20), M['white'])
box('WC Back', (TXc, Y1 - 0.09, 0.42), (0.36, 0.17, 0.34), M['white'], bevel=0.07)
sphere('WC Seat', (TXc, Y1 - 0.31, 0.585), (0.205, 0.285, 0.022), M['white'])
box('Flush Plate', (TXc, Y1 - 0.012, 1.0), (0.22, 0.02, 0.14), M['black'], bevel=0.004)
box('Flush Button A', (TXc - 0.045, Y1 - 0.024, 1.0), (0.07, 0.01, 0.05), M['brass'], bevel=0.003)
box('Flush Button B', (TXc + 0.045, Y1 - 0.024, 1.0), (0.07, 0.01, 0.05), M['brass'], bevel=0.003)
cyl('Paper Holder', (X1 - 0.07, 0.85, 0.85), 0.055, 0.1, mat('Paper', (0.95, 0.95, 0.93, 1), 0.9), rot=(0, math.pi / 2, 0))
box('Paper Bracket', (X1 - 0.02, 0.85, 0.85), (0.04, 0.04, 0.02), M['brass'])

# ---------- lights ----------
def area(name, loc, size, energy, color, rot, size_y=None):
    ld = bpy.data.lights.new(name, 'AREA'); ld.energy = energy; ld.color = color; ld.shape = 'RECTANGLE'
    ld.size = size; ld.size_y = size_y or size
    lo = bpy.data.objects.new(name, ld); lo.location = loc; lo.rotation_euler = rot; scene.collection.objects.link(lo)
area('Window', (X1 - 0.2, 0.1, 1.6), 1.0, 110, (0.85, 0.92, 1.0), (0, math.radians(-90), 0), 0.9)
area('Cove', (X1 - 0.1, 0, H - 0.08), 2.4, 28, (1.0, 0.72, 0.45), (0, math.radians(120), 0), 0.15)
area('Mirror', (VX, Y1 - 0.25, 1.6), 0.8, 22, (1.0, 0.8, 0.62), (math.radians(90), 0, 0), 0.8)
area('Underglow', (VX, VY, 0.25), 1.2, 14, (1.0, 0.7, 0.4), (0, 0, 0), 0.4)
area('Niche', (SX - 0.1, Y1 - 0.2, 1.5), 0.7, 8, (1.0, 0.72, 0.45), (math.radians(90), 0, 0), 0.1)
area('Fill', (-0.2, -0.7, 2.55), 2.4, 12, (1.0, 0.95, 0.9), (math.radians(180), 0, 0), 1.6)
world = bpy.data.worlds.new('W'); scene.world = world; world.use_nodes = True
world.node_tree.nodes['Background'].inputs['Color'].default_value = (0.05, 0.05, 0.06, 1)
world.node_tree.nodes['Background'].inputs['Strength'].default_value = 0.3

# ---------- camera ----------
cam_d = bpy.data.cameras.new('Cam'); cam_d.lens = 17
cam = bpy.data.objects.new('Cam', cam_d); scene.collection.objects.link(cam)
cam.location = (-1.25, Y0 + 0.02, 1.5)
cam.rotation_euler = (Vector((0.0, Y1, 1.1)) - cam.location).to_track_quat('-Z', 'Y').to_euler()
scene.camera = cam

scene.render.engine = 'CYCLES'; scene.cycles.device = 'CPU'; scene.cycles.samples = 64; scene.cycles.use_denoising = True
scene.view_settings.view_transform = 'AgX'
scene.render.resolution_x, scene.render.resolution_y = 1536, 1024
scene.render.filepath = OUT + '/bath_v2_preview.png'
bpy.ops.render.render(write_still=True)
bpy.ops.export_scene.gltf(filepath=OUT + '/bath_v2.glb', export_format='GLB', export_apply=True, export_cameras=False,
                          export_lights=False, export_image_format='JPEG', export_jpeg_quality=82)
bpy.ops.wm.save_as_mainfile(filepath=OUT + '/bath_v2.blend')
print('DONE')
