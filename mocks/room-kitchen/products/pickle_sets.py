# The two pickle-jar listings as the SETS they are sold as. Meshy made one jar of each well (painted village jar with its
# spoon; the D'Maiolica red jar with the deer band) but not the set, so the jars are Meshy's and the rest is built here:
#   pickle_spoons (ace72caf): two painted jars in a dark mango-wood tray, a black rod between them with a cane-wrapped grip
#   dmaiolica    (c02bca89): the pair of 1000 ml jars side by side
#   blender -b -P pickle_sets.py -- <outdir> [pickle_spoons|dmaiolica]
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from klib import *
args = sys.argv[sys.argv.index('--') + 1:]
WHICH = args[1].split(',') if len(args) > 1 else ['pickle_spoons', 'dmaiolica']
SRC = os.path.abspath(os.path.join(HERE, '..', '..', '..', 'models', 'source'))

def meshy(raw, height):
    """One Meshy model, joined, standing on z = 0, centred, scaled to `height`."""
    before = set(bpy.data.objects); bpy.ops.import_scene.gltf(filepath=os.path.join(SRC, raw))
    new = [o for o in bpy.data.objects if o not in before]; ms = [o for o in new if o.type == 'MESH']
    bpy.ops.object.select_all(action='DESELECT')
    for o in ms: o.select_set(True)
    bpy.context.view_layer.objects.active = ms[0]
    if len(ms) > 1: bpy.ops.object.join()
    o = bpy.context.view_layer.objects.active; bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    for e in new:
        if e != o and e.name in bpy.data.objects: bpy.data.objects.remove(e)
    co = np.array([v.co[:] for v in o.data.vertices]); lo, hi = co.min(0), co.max(0); s = height / (hi[2] - lo[2])
    body = co[co[:, 2] < lo[2] + 0.45 * (hi[2] - lo[2])]                # the jar body only (the spoon sticks out higher up)
    blo, bhi = body.min(0), body.max(0)
    c = np.array([(blo[0] + bhi[0]) / 2, (blo[1] + bhi[1]) / 2, lo[2]])
    o.data.vertices.foreach_set('co', ((co - c) * s).ravel()); o.data.update()
    return o, (bhi - blo) * s

def twin(o, w, gap, rot=(0.0, 0.0)):
    """o and a linked copy side by side along x, `gap` between them; each turned about z by rot."""
    o.rotation_mode = "XYZ"; b = o.copy(); bpy.context.scene.collection.objects.link(b); b.rotation_mode = "XYZ"
    o.location.x = -(w + gap) / 2; b.location.x = (w + gap) / 2; o.rotation_euler.z, b.rotation_euler.z = rot
    P.extend([o, b]); return o, b

def pickle_spoons():
    reset()
    jar, d = meshy('pickle-jar-with-spoons-achar-jar-set-for-dining-table-raw.glb', 0.125)
    dia = min(d[0], d[1]); TW, TD, TH, T = 2 * dia + 0.056, dia + 0.030, 0.042, 0.008
    WOOD = wood('Mango Wood', (0.17, 0.09, 0.05), (0.42, 0.25, 0.13), 0.5, contrast=0.7)
    tray = slab('Tray', rrect(TW, TD, 0.006, 6), 0, TH, WOOD, bevel=0.002)
    cut(tray, slab('c', rrect(TW - 2 * T, TD - 2 * T, 0.003, 6), T, TH + 0.01, None, bevel=0, keep=False))
    box_uv = lambda o_: [setattr(l, 'uv', (0, 0)) for l in []]
    planar_uv(tray, 0.25, 0.25)
    for o_ in (jar,): o_.location.z = T
    a, b = twin(jar, d[0], 0.026, (math.radians(105), math.radians(90)))
    a.location.z = b.location.z = T
    IRON = pmat('Black Iron', (0.03, 0.03, 0.03), 0.4, 0.6); CANE = pmat('Cane Wrap', (0.66, 0.47, 0.24), 0.6)
    slab('Rod Plate', rrect(0.020, 0.050, 0.003, 4), T, T + 0.004, IRON, bevel=0.001)
    for y in (-0.016, 0.016): cyl(0.0022, 0.002, (0, y, T + 0.005), pmat('Screw', (0.5, 0.5, 0.5), 0.3, 1.0), v=16)
    cyl(0.0032, 0.200, (0, 0, T + 0.100), IRON, v=24)
    for k in range(34):                                          # the cane grip: wrapped turns, slightly proud of each other
        cyl(0.0058 + 0.0004 * (k % 2), 0.0021, (0, 0, T + 0.135 + k * 0.002), CANE, v=24, bev=0.0004)
    lathe('Rod Cap', [(0, 0), (0.0045, 0), (0.0045, 0.004), (0.0, 0.006)], [IRON], seg=24); P[-1].location = (0, 0, T + 0.20)
    finish('pickle_spoons', 'Painted Pickle Jars with Spoons and Tray', view=(0.2, -1, 0.5))

def dmaiolica():
    reset()
    jar, d = meshy('d-maiolica-ceramic-handmade-pickle-jars-in-1000ml-set-of-2-f-raw.glb', 0.175)
    twin(jar, d[0], 0.015, (0.0, math.radians(40)))
    finish('dmaiolica', "D'Maiolica Handmade Pickle Jars, Set of 2", view=(0.2, -1, 0.35))

for k in WHICH: globals()[k]()
print('DONE')
