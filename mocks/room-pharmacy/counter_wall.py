# The PharmVials sample counter as one wall, laid out like the Quiet Bath (one wall, distinct zones):
# vial station | label station | blister station, then the blister machine at the end. The stations are
# appended from their own .blend files (vial_station.blend, label_station.blend, blister_station.blend)
# so every product is exactly as approved; this file adds the long counter, cabinets under it, closed
# wall cabinets above, an LED strip, and the wide camera.
#   blender -b -P counter_wall.py -- <out.png> [samples]
import bpy, sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import importlib, pv_lib, pv_paper; importlib.reload(pv_lib); importlib.reload(pv_paper)
from pv_lib import principled, HERE
from pv_paper import shoot, _rb
from mathutils import Vector

argv = sys.argv[sys.argv.index('--') + 1:]
OUT = argv[0]; SAMPLES = int(argv[1]) if len(argv) > 1 else 200
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
SET = {'Counter top', 'Backsplash', 'cam', 'Key panel', 'Window', 'Fill', 'Plane'}

def bring(blend, dx):
    """Append a station's objects (not its set, lights or camera) and slide them dx along the wall."""
    with bpy.data.libraries.load(os.path.join(HERE, blend)) as (src, dst):
        dst.objects = [n for n in src.objects if n not in SET]
    for o in dst.objects:
        if o is None: continue
        sc.collection.objects.link(o)
    for o in dst.objects:
        if o is not None and o.parent is None: o.location.x += dx

bring('vial_station.blend', -1.25)
bring('label_station.blend', -0.2)
bring('blister_station.blend', 0.75)        # its machine comes with it, standing on the floor at the end

# ---- the set: one long counter on base cabinets, wall cabinets above, the wall, the floor
quartz = principled('Quartz', (0.8, 0.8, 0.78), rough=0.22)
white = principled('Cabinet white', (0.9, 0.9, 0.89), rough=0.4)
wallm = principled('Wall', (0.66, 0.64, 0.6), rough=0.8)
X0, X1 = -1.75, 1.3                                        # counter runs to the machine
_rb('Counter top', ((X0 + X1) / 2, 0.0, -0.02), (X1 - X0, 0.7, 0.04), quartz, 0.003, 3)
_rb('Base cabinets', ((X0 + X1) / 2, 0.02, -0.47), (X1 - X0 - 0.02, 0.62, 0.86), white, 0.004, 3)
for i in range(6):                                          # door and drawer fronts with handles
    x = X0 + 0.23 + i * (X1 - X0 - 0.05) / 6
    _rb('Door', (x, -0.295, -0.5), (0.43, 0.012, 0.74), white, 0.003, 3)
    _rb('Handle', (x, -0.305, -0.18), (0.16, 0.012, 0.012), principled('Brushed steel', (0.7, 0.7, 0.7), rough=0.3, metallic=1.0), 0.004, 3)
_rb('Wall', (0.0, 0.36, 0.5), (9.0, 0.02, 2.9), wallm, 0.002, 2)
_rb('Wall cabinets', ((X0 + X1) / 2, 0.19, 1.05), (X1 - X0, 0.34, 0.7), white, 0.004, 3)
for i in range(6):
    x = X0 + 0.23 + i * (X1 - X0 - 0.05) / 6
    _rb('Upper door', (x, 0.015, 1.05), (0.43, 0.012, 0.68), white, 0.003, 3)
strip = principled('LED strip', (1, 0.95, 0.85), rough=0.5)
strip.node_tree.nodes['Principled BSDF'].inputs['Emission Color'].default_value = (1, 0.93, 0.82, 1)
strip.node_tree.nodes['Principled BSDF'].inputs['Emission Strength'].default_value = 8
_rb('Under-cabinet light', ((X0 + X1) / 2, 0.08, 0.695), (X1 - X0 - 0.1, 0.03, 0.006), strip, 0.002, 2)
bpy.ops.mesh.primitive_plane_add(size=8, location=(0, 0, -0.9)); bpy.context.active_object.data.materials.append(principled('Floor', (0.62, 0.62, 0.6), rough=0.4))

# ---- light: a ceiling panel over the counter, daylight from the left, the cabinet strip does the rest
def area(n, loc, size, power, target, color=(1, 1, 1)):
    l = bpy.data.lights.new(n, 'AREA'); l.shape = 'RECTANGLE'; l.size = size[0]; l.size_y = size[1]; l.energy = power; l.color = color
    o = bpy.data.objects.new(n, l); sc.collection.objects.link(o); o.location = loc
    o.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
area('Ceiling panel', (-0.3, -1.0, 1.9), (2.8, 0.8), 70, (-0.3, 0.1, 0.0), (1.0, 0.97, 0.92))
area('Window', (-3.2, -0.6, 1.0), (1.2, 1.6), 45, (-0.5, 0.1, 0.2), (1.0, 0.96, 0.9))
w = bpy.data.worlds.new('w'); sc.world = w; w.use_nodes = True
w.node_tree.nodes['Background'].inputs['Color'].default_value = (0.82, 0.8, 0.76, 1)
w.node_tree.nodes['Background'].inputs['Strength'].default_value = 0.1

shoot(OUT, SAMPLES, cam_loc=(-2.1, -1.55, 0.62), target=(-0.15, 0.12, 0.12), focus=(-1.2, -0.05, 0.05), lens=26, fstop=11)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(HERE, 'counter_wall.blend'))
print('DONE')
