# The PharmVials sample counter as an interactive room for the Urban Nest viewer (30 Oct 2026).
# The three approved stations are appended from their .blend files (vial_station / label_station /
# blister_station), spaced along one counter like the Quiet Bath's zones, inside a closed room (floor, four
# walls, ceiling with light panels) so the camera never sees an open edge. Writes:
#   pharmacy.glb       the whole room, every product inside it (the viewer's "inRoom" products)
#   placements.json    one entry per PharmVials product (products.json from fetch_products.mjs): the mesh its dot
#                      sits on, where the dot goes, and a camera viewpoint chosen to show it clearly
#   blender -b -P build_pharmacy.py
import bpy, sys, os, math, json, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import importlib, pv_lib, pv_paper; importlib.reload(pv_lib); importlib.reload(pv_paper)
from pv_lib import principled, image_material, HERE
from pv_paper import _rb
from mathutils import Vector

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
SET = {'Counter top', 'Backsplash', 'cam', 'Key panel', 'Window', 'Fill', 'Plane'}

def bring(blend, dx):
    """Append a station's objects (not its set, lights or camera) and slide them dx along the counter."""
    with bpy.data.libraries.load(os.path.join(HERE, blend)) as (src, dst):
        dst.objects = [n for n in src.objects if n not in SET]
    got = [o for o in dst.objects if o is not None]
    for o in got: sc.collection.objects.link(o)
    for o in got:
        if o.parent is None: o.location.x += dx
    return got

# zones left to right, with clear space between them (the wall render had them crowding)
VIAL = bring('vial_station.blend', -1.45)
LABEL = bring('label_station.blend', -0.3)
BLISTER = bring('blister_station.blend', 1.15)       # the machine comes with it, on the floor at the end

# ---- the set (counter top at z 0, floor at z -0.9; lifted to the floor at the end)
quartz = principled('Quartz', (0.8, 0.8, 0.78), rough=0.22)
white = principled('Cabinet white', (0.9, 0.9, 0.89), rough=0.4)
wallm = principled('Wall sage', (0.6, 0.69, 0.6), rough=0.85)          # pale sage: calm, and the amber and blue vials stand out
steel = principled('Brushed steel', (0.7, 0.7, 0.7), rough=0.3, metallic=1.0)
X0, X1 = -2.35, 1.7
RX0, RX1, RY0, RY1, FZ, CZ = -2.45, 3.5, -2.7, 0.37, -0.9, 1.8   # room walls, floor and ceiling heights
set_objs = []
def S(*a): o = _rb(*a); set_objs.append(o); return o
S('Counter top', ((X0 + X1) / 2, 0.0, -0.02), (X1 - X0, 0.7, 0.04), quartz, 0.003, 3)
S('Base cabinets', ((X0 + X1) / 2, 0.02, -0.47), (X1 - X0 - 0.02, 0.62, 0.86), white, 0.004, 3)
n = 7
for i in range(n):
    x = X0 + (i + 0.5) * (X1 - X0) / n
    S('Door', (x, -0.295, -0.5), ((X1 - X0) / n - 0.02, 0.012, 0.74), white, 0.003, 3)
    S('Handle', (x, -0.305, -0.18), (0.16, 0.012, 0.012), steel, 0.004, 3)
S('Wall cabinets', ((X0 + X1) / 2, 0.19, 1.05), (X1 - X0, 0.34, 0.7), white, 0.004, 3)
for i in range(n):
    x = X0 + (i + 0.5) * (X1 - X0) / n
    S('Upper door', (x, 0.015, 1.05), ((X1 - X0) / n - 0.02, 0.012, 0.68), white, 0.003, 3)
led = principled('LED strip', (1, 0.95, 0.85), rough=0.5)
led.node_tree.nodes['Principled BSDF'].inputs['Emission Color'].default_value = (1, 0.93, 0.82, 1)
led.node_tree.nodes['Principled BSDF'].inputs['Emission Strength'].default_value = 3
S('Under-cabinet light', ((X0 + X1) / 2, 0.08, 0.695), (X1 - X0 - 0.1, 0.03, 0.006), led, 0.002, 2)
# the room itself
floorm = principled('Floor vinyl', (0.46, 0.47, 0.47), rough=0.45)
ceilm = principled('Ceiling', (0.93, 0.93, 0.92), rough=0.9)
W, D = RX1 - RX0, RY1 - RY0
S('Shell floor', ((RX0 + RX1) / 2, (RY0 + RY1) / 2, FZ - 0.01), (W, D, 0.02), floorm, 0.001, 1)
S('Shell ceiling', ((RX0 + RX1) / 2, (RY0 + RY1) / 2, CZ + 0.01), (W, D, 0.02), ceilm, 0.001, 1)
S('Shell wall back', ((RX0 + RX1) / 2, RY1 + 0.01, (FZ + CZ) / 2), (W, 0.02, CZ - FZ), wallm, 0.001, 1)
S('Shell wall front', ((RX0 + RX1) / 2, RY0 - 0.01, (FZ + CZ) / 2), (W, 0.02, CZ - FZ), wallm, 0.001, 1)
S('Shell wall left', (RX0 - 0.01, (RY0 + RY1) / 2, (FZ + CZ) / 2), (0.02, D, CZ - FZ), wallm, 0.001, 1)
S('Shell wall right', (RX1 + 0.01, (RY0 + RY1) / 2, (FZ + CZ) / 2), (0.02, D, CZ - FZ), wallm, 0.001, 1)
S('Skirting', ((RX0 + RX1) / 2, RY1 - 0.005, FZ + 0.05), (W, 0.012, 0.1), white, 0.002, 2)
panel = principled('Ceiling panel', (1, 0.98, 0.95), rough=0.5)
panel.node_tree.nodes['Principled BSDF'].inputs['Emission Color'].default_value = (1, 0.97, 0.92, 1)
panel.node_tree.nodes['Principled BSDF'].inputs['Emission Strength'].default_value = 4
for x in (-1.6, -0.2, 1.2, 2.6):
    S('Ceiling light', (x, -0.6, CZ - 0.005), (0.6, 0.6, 0.01), panel, 0.004, 2)

# the plant is gone (its leaves read as cartoon circles; light cannot fix shape). In its place, things every
# dispensary has: the dispensing computer, colour-coded prescription baskets, a clock, a tiled backsplash.
def drop(obj):
    for c in list(obj.children_recursive) + [obj]: bpy.data.objects.remove(c, do_unlink=True)
plant = next(o for o in BLISTER if o.parent is None and re.sub(r'\.\d{3}$', '', o.name) == 'Plant')
gone = {plant.name} | {c.name for c in plant.children_recursive}
BLISTER[:] = [o for o in BLISTER if o.name not in gone]           # before removal: a removed object cannot be asked its name
drop(plant)
from pv_staging import wall_clock
import pv_refine2; importlib.reload(pv_refine2)
from pv_refine2 import rx_baskets                                 # the moulded tubs, not the block version
import pv_refine; importlib.reload(pv_refine)
pv_refine.computer(loc=(-0.88, 0.16, 0), rot=0.12)              # the detailed one (pv_refine), not the block version
rx_baskets(loc=(X0 + 0.2, 0.08, 0), rot=0.05)
wall_clock(loc=(RX0 + 0.02, -0.9, 1.25), rot=-math.pi / 2)
# backsplash: small white tiles with pale grout, between the counter and the wall cabinets
import numpy as np
TW, TH = 0.15, 0.075                                                   # 15 x 7.5 cm brick-laid tiles
img = np.ones((256, 512, 3), dtype=np.float32) * np.array([0.93, 0.93, 0.91])
for r in range(8):
    y = r * 32; img[y:y + 2, :] = 0.78
    off = 0 if r % 2 else 64
    for c in range(5): img[y:y + 32, (off + c * 128) % 512:(off + c * 128) % 512 + 2] = 0.78
tile = bpy.data.images.new('Backsplash tile', 512, 256); rgba = np.ones((256, 512, 4), np.float32); rgba[..., :3] = img
tile.pixels.foreach_set(rgba.ravel()); tile.filepath_raw = os.path.join(HERE, 'tex', 'backsplash_tile.png'); tile.file_format = 'PNG'; tile.save()
tm = bpy.data.materials.new('Backsplash tile'); tm.use_nodes = True
tx = tm.node_tree.nodes.new('ShaderNodeTexImage'); tx.image = tile
tm.node_tree.links.new(tx.outputs['Color'], tm.node_tree.nodes['Principled BSDF'].inputs['Base Color'])
tm.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value = 0.25
w_, h_ = X1 - X0, 0.7
bs = bpy.data.meshes.new('LM_Backsplash'); bs.from_pydata([(X0, 0.354, 0), (X1, 0.354, 0), (X1, 0.354, h_), (X0, 0.354, h_)], [], [(0, 1, 2, 3)])
uvl = bs.uv_layers.new(name='UV')
for i, (u, v) in enumerate([(0, 0), (w_ / (4 * TW), 0), (w_ / (4 * TW), h_ / (8 * TH)), (0, h_ / (8 * TH))]): uvl.data[i].uv = (u, v)
bso = bpy.data.objects.new('LM_Backsplash', bs); sc.collection.objects.link(bso); bs.materials.append(tm); set_objs.append(bso)


# ---- realism pass (31 Oct 2026, "mushy, cartoonish"): see pv_refine.py
import pv_refine; importlib.reload(pv_refine)
from pv_refine import crisp, box_uv, roll_ends, pill_cutter as cutter2, computer as computer2, vial_box, rx_sign
# the pill cutter, rebuilt in its real pill shape where the old one stood
old = next(o for o in VIAL if o.parent is None and re.sub(r'\.\d{3}$', '', o.name) == 'Pill cutter')
at, turn = old.location.copy(), old.rotation_euler.z
gone = {old.name} | {c.name for c in old.children_recursive}
VIAL[:] = [o for o in VIAL if o.name not in gone]; drop(old)
VIAL.append(cutter2(loc=at, rot=turn))
# the PharmVials box of 13 DR vials on the floor at the left end; the Rx Pickup sign on the left wall above the baskets
vial_box(loc=(X0 + 0.24, -0.62, -0.9), rot=0.25)       # its open flap cleared the left wall
rx_sign(loc=(RX0 + 0.02, 0.0 - 0.15, 0.55), rot=-math.pi / 2)
# batch 2: the counting tray and weighing boats rebuilt (pv_refine2), standing exactly where the old ones stood
import pv_refine2; importlib.reload(pv_refine2)
def swap(pool, name, make):
    for old in [o for o in pool if o.parent is None and re.sub(r'\.\d{3}$', '', o.name) == name]:
        at, turn = old.location.copy(), old.rotation_euler.z
        gone = {old.name} | {c.name for c in old.children_recursive}
        pool[:] = [o for o in pool if o.name not in gone]; drop(old)
        pool.append(make(at, turn))
swap(VIAL, 'Counting tray', lambda at, r: pv_refine2.counting_tray(loc=at, rot=r))
swap(VIAL, 'Weighing boats', lambda at, r: pv_refine2.weighing_boats(loc=at, rot=r, n=3))
for sc_ in [o for o in VIAL if o.parent is None and re.sub(r'\.\d{3}$', '', o.name) == 'Digital scale']:
    for ch in [c for c in sc_.children if re.sub(r'\.\d{3}$', '', c.name) == 'Weighing boats']:
        at = ch.matrix_world.translation.copy(); gone = {ch.name} | {c.name for c in ch.children_recursive}
        VIAL[:] = [o for o in VIAL if o.name not in gone]; drop(ch)
        pv_refine2.weighing_boats(loc=at, rot=sc_.rotation_euler.z, n=1, tablets=6)
# the counter: speckled quartz at real scale; the roll ends: wound paper round a brown core
ct = next(o for o in set_objs if o.name == 'Counter top')
# a photo-scanned white marble SLAB (ambientCG Marble019, CC0; Poly Haven marble_01 was a tiled floor, grout lines and all): its own colour, roughness and relief, so the counter
# catches light like stone instead of looking printed
mm = image_material('Marble counter', os.path.join(HERE, 'scans', 'm19', 'Marble019_2K-JPG_Color.jpg'), rough=0.2)
nt_ = mm.node_tree; bsdf = nt_.nodes['Principled BSDF']
rt = nt_.nodes.new('ShaderNodeTexImage'); rt.image = bpy.data.images.load(os.path.join(HERE, 'scans', 'm19', 'Marble019_2K-JPG_Roughness.jpg')); rt.image.colorspace_settings.name = 'Non-Color'
nt_.links.new(rt.outputs['Color'], bsdf.inputs['Roughness'])
nm_ = nt_.nodes.new('ShaderNodeTexImage'); nm_.image = bpy.data.images.load(os.path.join(HERE, 'scans', 'm19', 'Marble019_2K-JPG_NormalGL.jpg')); nm_.image.colorspace_settings.name = 'Non-Color'
nmap = nt_.nodes.new('ShaderNodeNormalMap'); nmap.inputs['Strength'].default_value = 0.6
nt_.links.new(nm_.outputs['Color'], nmap.inputs['Color']); nt_.links.new(nmap.outputs['Normal'], bsdf.inputs['Normal'])
for s_ in ct.material_slots: s_.material = mm
box_uv(ct, 2.0)                                                  # the seamless slab scan spans 2 m
roll_ends()
# crisp edges on everything
crisp([o for o in sc.objects if o.type == 'MESH'])

# everything up by 0.9 m so the floor sits at 0, as in the other rooms
for o in list(sc.objects):
    if o.parent is None: o.location.z += 0.9

# ---- products: find each one in the scene, put its dot on top, and choose its camera
def base(nm): return re.sub(r'\.\d{3}$', '', nm)
def picks(test, pool):
    return [o for o in pool if test(base(o.name))]
def tree(objs):
    out = []
    for o in objs:
        out.append(o); out += list(o.children_recursive)
    return [o for o in out if o.type == 'MESH']
def bbox(meshes):
    lo = Vector((1e9,) * 3); hi = Vector((-1e9,) * 3)
    bpy.context.view_layer.update()
    for m in meshes:
        for c in m.bound_box:
            w = m.matrix_world @ Vector(c)
            for i in range(3): lo[i] = min(lo[i], w[i]); hi[i] = max(hi[i], w[i])
    return lo, hi
roots = lambda pool: [o for o in pool if o.parent is None]
FIND = {
    'amber_cr': lambda: picks(lambda n: re.fullmatch(r'Vial amber \d+ CR', n), VIAL),
    'blue_cr':  lambda: picks(lambda n: re.fullmatch(r'Vial blue \d+ CR', n), VIAL),
    'snap':     lambda: picks(lambda n: re.fullmatch(r'Vial (amber|blue) \d+ snap', n), VIAL),
    'cutter':   lambda: picks(lambda n: n == 'Pill cutter', roots(VIAL)),
    'scale':    lambda: picks(lambda n: n == 'Digital scale', roots(VIAL)),
    'boats':    lambda: picks(lambda n: n == 'Weighing boats', roots(VIAL)),
    'label':    lambda: picks(lambda n: n in ('Printed label', 'Thermal printer', 'Label roll'), roots(LABEL)),   # the printer, its label, one roll
    'receipt':  lambda: picks(lambda n: n in ('Receipt', 'Receipt roll'), roots(LABEL)),
    'tape':     lambda: picks(lambda n: n == 'Clear label tape', roots(LABEL)),
    'syringes': lambda: picks(lambda n: n == 'Syringe cup', roots(LABEL)),
    'gloves':   lambda: picks(lambda n: n == 'Gloves box', roots(LABEL)),
    'jumbo':    lambda: picks(lambda n: n in ('Jumbo open', 'Rx label on card'), roots(BLISTER)),
    'twin':     lambda: picks(lambda n: n == 'Twin', roots(BLISTER)),
    'trifold':  lambda: picks(lambda n: n in ('Tri-Fold closed', 'Jumbo closed'), roots(BLISTER)),
    'tray':     lambda: picks(lambda n: n == 'Filling tray', roots(BLISTER)),
    'roller':   lambda: picks(lambda n: n == 'Seal roller', roots(BLISTER)),
}
g = lambda v: [round(v.x, 3), round(v.z, 3), round(-v.y, 3)]      # Blender (z up) -> glTF (y up)
items = json.load(open(os.path.join(HERE, 'products.json')))
products = []
for it in items:
    meshes = tree(FIND[it['key']]())
    if not meshes: print('NOT FOUND', it['key']); continue
    lo, hi = bbox(meshes); c = (lo + hi) / 2; size = hi - lo
    dot = c.copy(); dot.z = hi.z + 0.03
    if it['key'] == 'label':                                   # the dot on the label roll, not the group's middle (the printer's corner)
        rl, rh = bbox(tree(picks(lambda n: n == 'Label roll', roots(LABEL)))); dot = (rl + rh) / 2; dot.z = rh.z + 0.03
    # camera: in front of the counter and above, far enough to frame the whole group, looking down at it
    # (never from counter level, never from behind or under anything); flat cards are looked down on steeply
    span = max(size.x, size.y, size.z)
    dist = min(max(span * 1.35 + 0.16, 0.3), 1.2)          # close: the product fills the view beside its card
    flat = size.z < 0.04 and max(size.x, size.y) > 0.15
    pos = Vector((c.x - 0.04, c.y - dist * (0.55 if flat else 0.82), c.z + dist * (0.85 if flat else 0.55)))
    # the mesh the dot belongs to: the biggest one in the group
    node = max(meshes, key=lambda m: m.dimensions.x * m.dimensions.y * m.dimensions.z)
    products.append({**{k: it[k] for k in ('name', 'tag', 'desc', 'specs', 'link')}, 'inRoom': True,
                     'node': re.sub(r'[\[\].:/]', '', re.sub(r'\s', '_', node.name)),   # as three.js's GLTFLoader renames it
                     'dotAt': g(dot),
                     'view': {'pos': g(pos), 'target': g(c)}})
    print('product', it['key'], '->', node.name, 'size cm', [round(v * 100) for v in size])

# ---- bake: the room's light and shadows into lightmaps, as the Sunday Bedroom does (build_bedroom_v1.py). The set
# (walls, floor, ceiling, cabinets, counter, backsplash, the machine's cabinet) is joined into a few LM_/Shell_
# meshes, each with its own lightmap UV and image; the products stay lit live in the viewer but stand in the bake,
# so their shadows land on the counter. Light: the four ceiling panels (as area lights) and the cabinet strip.
#   blender -b -P build_pharmacy.py -- quick     skips the bake (layout check, a minute)
QUICK = 'quick' in sys.argv
import numpy as np
TMP = os.path.join(HERE, 'lm'); os.makedirs(TMP, exist_ok=True)
ACT = lambda o: (bpy.ops.object.select_all(action='DESELECT'), o.select_set(True), setattr(bpy.context.view_layer.objects, 'active', o))

def solid(o):
    """Free of its parent, modifiers applied: ready to join."""
    ACT(o); bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM'); bpy.ops.object.convert(target='MESH')
def join(objs, name):
    objs = [o for o in objs if alive(o) and o.type == 'MESH']
    for o in objs: solid(o)
    bpy.ops.object.select_all(action='DESELECT')
    for o in objs: o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
    if len(objs) > 1: bpy.ops.object.join()
    j = bpy.context.view_layer.objects.active; j.name = name; j.data.name = name
    return j
def alive(o):                                                   # a join removes the pieces it swallowed
    try: o.name; return True
    except ReferenceError: return False
named = lambda pre: [o for o in set_objs if alive(o) and re.sub(r'\.\d{3}$', '', o.name).startswith(pre)]

if not QUICK:
    BAKE = [join(named('Counter top'), 'LM_Counter'),
            join(named('Base cabinets') + named('Door') + named('Handle'), 'LM_BaseCabinets'),
            join(named('Wall cabinets') + named('Upper door'), 'LM_WallCabinets'),
            join(named('Skirting'), 'LM_Skirting'), bso]
    for o in named('Shell'):
        o.name = 'Shell_' + o.name.split(' ', 1)[1].title().replace(' ', ''); solid(o); BAKE.append(o)
    # the machine's cabinet: everything of it except glass, lights, screen and the see-through canisters/cards
    mroot = next(o for o in bpy.data.objects if re.sub(r'\.\d{3}$', '', o.name) == 'Blister machine')
    LIVE = ('Machine glass', 'Edge LED', 'Interior light', 'Button orange', 'Status', 'Screen', 'Canister', 'Card', 'Smoke')
    parts = [mroot] + [c for c in mroot.children_recursive if c.type == 'MESH']
    keep_live = [c for c in parts if c.data.materials and any(m and m.name.startswith(LIVE) for m in c.data.materials)]
    for c in keep_live: ACT(c); bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')
    BAKE.append(join([p for p in parts if p not in keep_live], 'LM_Machine'))

    LM = []
    def prep(o, res):
        me = o.data
        if not me.uv_layers: me.uv_layers.new(name='UV')
        me.uv_layers[0].active_render = True
        lm = me.uv_layers.new(name='LM'); me.uv_layers.active = lm
        ACT(o); bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.uv.smart_project(angle_limit=math.radians(60), island_margin=0.004); bpy.ops.object.mode_set(mode='OBJECT')
        img = bpy.data.images.new('LMF_' + o.name, res, res, alpha=False, float_buffer=True)
        for slot in o.material_slots:
            m = slot.material.copy(); m.name = 'LM ' + slot.material.name; slot.material = m
            t = m.node_tree.nodes.new('ShaderNodeTexImage'); t.image = img; t.name = 'LM_BAKE'; m.node_tree.nodes.active = t
        LM.append((o, img))
    RES = {'LM_Counter': 2048, 'LM_BaseCabinets': 2048, 'LM_WallCabinets': 2048, 'LM_Machine': 2048, 'LM_Backsplash': 1024,
           'LM_Skirting': 512, 'Shell_Floor': 1024, 'Shell_Ceiling': 512}
    for o in BAKE: prep(o, RES.get(o.name, 1024))

    # the light: an area light under each ceiling panel, a dim world
    for x in (-1.6, -0.2, 1.2, 2.6):
        l = bpy.data.lights.new('Panel', 'AREA'); l.size = 0.6; l.energy = 90; l.color = (1, 0.97, 0.92)
        ob = bpy.data.objects.new('Panel light', l); sc.collection.objects.link(ob); ob.location = (x, -0.6, CZ + 0.9 - 0.02)
    sc.world = bpy.data.worlds.new('w'); sc.world.use_nodes = True
    sc.world.node_tree.nodes['Background'].inputs['Color'].default_value = (0.85, 0.85, 0.83, 1)
    sc.world.node_tree.nodes['Background'].inputs['Strength'].default_value = 0.15
    sc.render.engine = 'CYCLES'; sc.cycles.device = 'CPU'; sc.cycles.samples = 128
    sc.render.bake.target = 'IMAGE_TEXTURES'; sc.render.bake.margin = 8
    bpy.ops.object.select_all(action='DESELECT')
    for o, _ in LM: o.select_set(True)
    bpy.context.view_layer.objects.active = LM[0][0]
    print('BAKING', len(LM), 'lightmaps'); sys.stdout.flush()
    bpy.ops.object.bake(type='DIFFUSE', pass_filter={'DIRECT', 'INDIRECT'}, margin=8, use_clear=True)

    def gblur(a, sigma=1.5):
        r = 4; k = np.exp(-np.arange(-r, r + 1) ** 2 / (2 * sigma * sigma)); k /= k.sum()
        for axis in (0, 1):
            pad = [(r, r) if i == axis else (0, 0) for i in range(3)]
            p = np.pad(a, pad, mode='edge'); a = sum(k[i] * np.take(p, range(i, i + a.shape[axis]), axis=axis) for i in range(2 * r + 1))
        return a
    BAKED = {o.name: gblur(np.array(img.pixels[:], dtype=np.float32).reshape(img.size[1], img.size[0], 4)[..., :3]) for o, img in LM}
    walls = [n for n in BAKED if n.startswith('Shell_Wall')]
    lum = np.concatenate([BAKED[n].reshape(-1, 3) for n in walls]) @ np.array([0.2126, 0.7152, 0.0722])
    gain = 0.92 / max(1e-4, np.percentile(lum, 97)); print('BAKE gain', round(float(gain), 3))
    for o, img in LM:
        a = np.clip(BAKED[o.name] * gain, 0, 1); h, w = a.shape[:2]
        a = np.where(a <= 0.0031308, a * 12.92, 1.055 * np.power(a, 1 / 2.4) - 0.055)
        rgba = np.ones((h, w, 4), np.float32); rgba[..., :3] = a
        im = bpy.data.images.new('LM_' + o.name, w, h, alpha=False); im.pixels.foreach_set(rgba.ravel())
        p = os.path.join(TMP, 'LM_' + o.name + '.png'); im.filepath_raw = p; im.file_format = 'PNG'; im.save()
        out = bpy.data.images.load(p); out.pack()
        for slot in o.material_slots:
            nt = slot.material.node_tree; b = nt.nodes['Principled BSDF']
            nt.nodes.remove(nt.nodes['LM_BAKE'])
            for n_ in list(nt.nodes):                                        # base textures stay on the first UV
                if n_.type == 'TEX_IMAGE' and not n_.inputs['Vector'].is_linked:
                    um = nt.nodes.new('ShaderNodeUVMap'); um.uv_map = o.data.uv_layers[0].name; nt.links.new(um.outputs['UV'], n_.inputs['Vector'])
            t = nt.nodes.new('ShaderNodeTexImage'); t.image = out
            um = nt.nodes.new('ShaderNodeUVMap'); um.uv_map = 'LM'; nt.links.new(um.outputs['UV'], t.inputs['Vector'])
            nt.links.new(t.outputs['Color'], b.inputs['Emission Color']); b.inputs['Emission Strength'].default_value = 1.0
        o.data.uv_layers.active = o.data.uv_layers[0]
        print('LIGHTMAP', o.name, w, 'px, mean', round(float(a.mean()), 3)); sys.stdout.flush()

# ---- export: no cameras or lights; modifiers applied (bevels, card thickness)
for o in list(sc.objects):
    if o.type in ('CAMERA', 'LIGHT'): bpy.data.objects.remove(o)
tris = 0
dg = bpy.context.evaluated_depsgraph_get()
for o in sc.objects:
    if o.type == 'MESH':
        me = o.evaluated_get(dg).to_mesh(); tris += sum(len(p.vertices) - 2 for p in me.polygons); o.evaluated_get(dg).to_mesh_clear()
print('triangles', tris)
bpy.ops.export_scene.gltf(filepath=os.path.join(HERE, 'pharmacy.glb'), export_format='GLB', export_cameras=False,
                          export_lights=False, export_apply=True, export_yup=True, export_image_format='JPEG', export_jpeg_quality=88)
json.dump({'room': 'pharmacy-web.glb', 'products': products, 'staging': []}, open(os.path.join(HERE, 'placements.json'), 'w'), indent=1)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(HERE, 'pharmacy.blend'))
print('DONE', len(products), 'products')
