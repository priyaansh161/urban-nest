# Blister station of the PharmVials sample counter (30 Oct 2026): the blister-filling machine standing at the
# end of the counter; on the counter an open Paxxol Jumbo card being filled (Rx label on its left panel),
# a Twin card half open, closed Jumbo and Tri-Fold cards, the filling tray and the red seal roller.
#   blender -b -P blister_station.py -- <out.png> [samples]
import bpy, sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import importlib, pv_lib, pv_paper, pv_blister
import pv_staging
for m in (pv_lib, pv_paper, pv_blister, pv_staging): importlib.reload(m)
from pv_lib import *
from pv_paper import stage, shoot, sheet
from pv_blister import *
from pv_staging import sanitizer, plant

argv = sys.argv[sys.argv.index('--') + 1:]
OUT = argv[0]; SAMPLES = int(argv[1]) if len(argv) > 1 else 200
bpy.ops.wm.read_factory_settings(use_empty=True)
stage()
# the counter stops where the machine stands; the machine stands on the floor (counter top at 0, floor at -0.9)
top = bpy.data.objects['Counter top']; top.scale.x = 0.805; top.location.x = -0.9 + 1.8 * 0.805 / 2         # counter ends at x 0.55, clear of the machine
wall = bpy.data.objects['Backsplash']; wall.scale = (3.4, 0.02, 2.4); wall.location = (0.4, 0.36, 0.3)
blister_machine(loc=(1.3, -0.14, -0.9), rot=0.0)      # square to the back wall: at an angle its corner ran into it
floor = principled('Floor', (0.62, 0.62, 0.6), rough=0.4)
bpy.ops.mesh.primitive_plane_add(size=4, location=(0, 0, -0.9)); bpy.context.active_object.data.materials.append(floor)

# the open Jumbo card, being filled row by row (16 of 28 doses in), Rx label stuck on its left panel
j = book('Jumbo open', 'pax_label_panel.png', 'pax_grid_jumbo.png', 'pax_grid_jumbo.json', JW, JH, open_deg=180, filled=16, seed=3,
         loc=(-0.07, -0.25, 0), rot=0.06)
sheet('Rx label on card', os.path.join(TEX, 'label_sheet.png'), 0.1175,
      [(0.0, 0.0012), (-0.054, 0.0012)], loc=(-0.07 - 0.115, -0.25 + 0.2, 0), rot=0.06)
# a Twin card standing half open, closed Jumbo and Tri-Fold cards stacked at the back
book('Twin', 'pax_label_panel_narrow.png', 'pax_grid_twin.png', 'pax_grid_twin.json', TW, JH, open_deg=125, filled=14, seed=5,
     cover='pax_cover_twin.png', loc=(-0.6, -0.22, 0), rot=0.35)
book('Tri-Fold closed', 'pax_label_panel.png', 'pax_grid_trifold.png', 'pax_grid_trifold.json', JW, JH, open_deg=0, filled=28, seed=7,
     cover='pax_cover_trifold.png', loc=(0.27, 0.0, 0), rot=-0.12)
book('Jumbo closed', 'pax_label_panel.png', 'pax_grid_jumbo.png', 'pax_grid_jumbo.json', JW, JH, open_deg=0, filled=28, seed=9,
     cover='pax_cover_jumbo.png', loc=(0.24, 0.02, 0.0135), rot=0.1)
filling_tray(loc=(-0.4, 0.17, 0), rot=0.1)
seal_roller(loc=(-0.17, 0.22, 0), rot=-0.5)
sanitizer(loc=(0.05, 0.27, 0))
plant(loc=(-0.78, 0.22, 0))

shoot(OUT, SAMPLES, cam_loc=(-0.25, -2.5, 1.0), target=(0.55, 0.05, 0.35), focus=(0.0, -0.12, 0.01), lens=32, fstop=8)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(HERE, 'blister_station.blend'))
print('DONE')
