# Vial station of the PharmVials sample counter, first look (30 Oct 2026). Amber and blue child-resistant
# vials in 6, 8, 13, 20 and 40 DR grouped as on their site (photo 11), snap-cap vials beside them, and at the
# front the work itself: a counting tray of capsules, an open vial being filled, a finished labelled vial.
#   blender -b -P vial_station.py -- <out.png> [samples]
import bpy, sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import importlib, pv_lib, pv_staging; importlib.reload(pv_lib); importlib.reload(pv_staging)
from pv_lib import *
from pv_staging import *
from mathutils import Vector

argv = sys.argv[sys.argv.index('--') + 1:]
OUT = argv[0]; SAMPLES = int(argv[1]) if len(argv) > 1 else 200
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene

# ---- counter and wall: white quartz top, pale warm-grey backsplash
quartz = principled('Quartz', (0.8, 0.8, 0.78), rough=0.22)
wallm = principled('Wall', (0.66, 0.64, 0.6), rough=0.8)
def slab(n, c, s, m):
    bpy.ops.mesh.primitive_cube_add(size=1, location=c); o = bpy.context.active_object; o.name = n; o.scale = s
    b = o.modifiers.new('b', 'BEVEL'); b.width = 0.003; b.segments = 3; o.data.materials.append(m); return o
slab('Counter top', (0, 0, -0.02), (1.8, 0.7, 0.04), quartz)
slab('Backsplash', (0, 0.36, 0.4), (1.8, 0.02, 0.84), wallm)

# ---- the vial range, grouped by colour and closure; shifted left (31 Oct) to give the bigger scale its room
import pv_photo, pv_refine2; importlib.reload(pv_refine2); importlib.reload(pv_photo)
cluster = [(40, (0.00, 0.06)), (20, (0.075, 0.035)), (13, (-0.06, 0.01)), (8, (0.02, -0.01)), (6, (0.07, -0.035))]
for gx, colour in ((-0.33, 'amber'), (-0.13, 'blue')):
    for dr, (x, y) in cluster:
        vial('Vial %s %d CR' % (colour, dr), dr, colour, 'cr', loc=(gx + x, 0.17 + y, 0), rot=x * 7)
for i, (dr, colour) in enumerate([(13, 'amber'), (13, 'blue'), (20, 'amber'), (40, 'blue')]):
    vial('Vial %s %d snap' % (colour, dr), dr, colour, 'snap', loc=(0.0 + (i % 2) * 0.062, 0.215 - (i // 2) * 0.06, 0))

# ---- the work at the front, every piece standing clear of its neighbours
amox = (principled('Gelatin maroon', (0.32, 0.03, 0.05), rough=0.12, coat=0.6), principled('Gelatin mustard', (0.86, 0.58, 0.1), rough=0.12, coat=0.6))
TX, TY, TR = -0.22, -0.07, 0.08
tray = pv_refine2.counting_tray(loc=(TX, TY, 0), rot=TR)
pill_cutter(loc=(-0.04, -0.01, 0), rot=0.5)
pv_photo.digital_scale(loc=(0.21, 0.1, 0), rot=-0.1)            # stops short of the keyboard
pv_refine2.weighing_boats(loc=(0.21, -0.16, 0), rot=0.4, n=3)
import random; rnd = random.Random(4)
for i in range(11):                                              # capsules on the tray floor, right of the channel wall
    dx, dy = rnd.uniform(-0.04, 0.08), rnd.uniform(-0.034, 0.034)
    capsule('Capsule on tray', amox, loc=(TX + dx * math.cos(TR) - dy * math.sin(TR), TY + dx * math.sin(TR) + dy * math.cos(TR), 0.0022 + 0.0042),
            rot=(math.pi / 2, 0, rnd.uniform(0, 6.28)))
open_v = vial('Vial being filled', 20, 'amber', 'cr', loc=(0.04, -0.11, 0), cap_off=(0.095, -0.15, True))
fill_vial(open_v, 20, 12, amox, seed=2)
done = vial('Finished Rx', 40, 'amber', 'cr', loc=(0.058, -0.035, 0), rot=0)
fill_vial(done, 40, 21, amox, seed=5)
label_wrap(done, 40, os.path.join(TEX, 'rx_label_amox.png'), frac=0.62, rot=-1.2)
omep = (principled('Gelatin purple', (0.3, 0.1, 0.42), rough=0.12, coat=0.6), principled('Gelatin pink', (0.9, 0.55, 0.62), rough=0.12, coat=0.6))
done2 = vial('Finished Rx blue', 13, 'blue', 'cr', loc=(0.135, -0.09, 0))
fill_vial(done2, 13, 9, omep, seed=8)
label_wrap(done2, 13, os.path.join(TEX, 'rx_label_omep.png'), frac=0.7, rot=-1.15)

# ---- light: a big soft panel overhead-front, a window from the left, a cool fill from the right
def area(n, loc, size, power, target, color=(1, 1, 1)):
    l = bpy.data.lights.new(n, 'AREA'); l.size = size[0]; l.shape = 'RECTANGLE'; l.size_y = size[1]
    l.energy = power; l.color = color
    o = bpy.data.objects.new(n, l); sc.collection.objects.link(o); o.location = loc
    o.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler(); return o
area('Key panel', (0.1, -0.55, 0.85), (1.0, 0.6), 22, (0, 0.05, 0), (1.0, 0.96, 0.9))
area('Window', (-1.1, 0.05, 0.55), (0.8, 1.0), 14, (0, 0.05, 0.05), (1.0, 0.96, 0.9))
area('Fill', (1.0, -0.3, 0.4), (0.6, 0.6), 4, (0, 0.05, 0.05), (0.9, 0.95, 1.0))
w = bpy.data.worlds.new('w'); sc.world = w; w.use_nodes = True
w.node_tree.nodes['Background'].inputs['Color'].default_value = (0.82, 0.8, 0.76, 1)
w.node_tree.nodes['Background'].inputs['Strength'].default_value = 0.12

# ---- camera: at a pharmacist's eye height, leaning in over the counter
cd = bpy.data.cameras.new('cam'); cam = bpy.data.objects.new('cam', cd); sc.collection.objects.link(cam); sc.camera = cam
cd.lens = 50; cam.location = (-0.01, -0.64, 0.28)
cam.rotation_euler = (Vector((0.0, 0.06, 0.03)) - cam.location).to_track_quat('-Z', 'Y').to_euler()
cd.dof.use_dof = True; cd.dof.focus_distance = (Vector((0.1, -0.03, 0.04)) - cam.location).length; cd.dof.aperture_fstop = 5.6

# ---- render: Cycles, enough bounces for light to pass through two walls of amber plastic
sc.render.engine = 'CYCLES'; cy = sc.cycles; cy.device = 'CPU'
cy.samples = SAMPLES; cy.use_denoising = True; cy.max_bounces = 16; cy.transmission_bounces = 16
cy.glossy_bounces = 8; cy.transparent_max_bounces = 16; cy.blur_glossy = 1.0; cy.caustics_reflective = False
sc.view_settings.view_transform = 'AgX'; sc.view_settings.look = 'AgX - Medium High Contrast'
sc.render.resolution_x, sc.render.resolution_y = 1600, 900
sc.render.filepath = OUT; bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(HERE, 'vial_station.blend'))
print('DONE')
