# Label station of the PharmVials sample counter (30 Oct 2026): the thermal printer running out a Paxxol
# 4.625 x 2.125 in Rx label, Paxxol label rolls and 3.375 x 4.25 in receipt rolls round it, the patient's
# printed receipt on the counter, and a labelled vial to show where the label ends up.
#   blender -b -P label_station.py -- <out.png> [samples]
import bpy, sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import importlib, pv_lib, pv_paper, pv_staging; importlib.reload(pv_lib); importlib.reload(pv_paper); importlib.reload(pv_staging)
from pv_lib import *
from pv_paper import *
from pv_staging import *

argv = sys.argv[sys.argv.index('--') + 1:]
OUT = argv[0]; SAMPLES = int(argv[1]) if len(argv) > 1 else 200
bpy.ops.wm.read_factory_settings(use_empty=True)
stage()

LW, LOD, RW, ROD = 0.1175, 0.125, 0.0857, 0.11          # roll widths (4.625 in, 3.375 in) and outside diameters
LBL, RCP = os.path.join(TEX, 'roll_labels.png'), os.path.join(TEX, 'roll_receipts.png')

# printer, with today's label coming out of the slot and curling down
import pv_photo; importlib.reload(pv_photo)
printer, (ey, ez) = pv_photo.thermal_printer(loc=(0.0, 0.13, 0))     # the photo-dressed one (31 Oct)
y0 = 0.13 + ey
sheet('Printed label', os.path.join(TEX, 'label_sheet.png'), LW,
      [(y0, ez), (y0 - 0.025, ez - 0.002), (y0 - 0.042, ez - 0.008), (y0 - 0.055, ez - 0.02), (y0 - 0.06, ez - 0.03)])

# Paxxol label rolls to the left: one on its edge facing out, one lying flat, one behind
paper_roll('Label roll', LW, LOD, LBL, loc=(-0.2, 0.06, 0), standing=True, rot=0.35)
paper_roll('Label roll back', LW, LOD, LBL, loc=(-0.2, 0.25, 0), standing=True, rot=2.99)   # tail falls to the back, not over the printer

# receipt rolls to the right
paper_roll('Receipt roll', RW, ROD, RCP, loc=(0.2, 0.07, 0), standing=True, rot=-0.4)
paper_roll('Receipt roll flat', RW, ROD, RCP, loc=(0.3, 0.22, 0), standing=False, rot=0.5)

# the printed receipt for the bag, lying on the counter with its end lifting
sheet('Receipt', os.path.join(TEX, 'receipt.png'), RW,
      [(0.108, 0.011), (0.092, 0.0035), (0.075, 0.0004), (0.0, 0.0004)], loc=(0.16, -0.17, 0), rot=0.28)

label_tape(loc=(0.36, -0.2, 0), rot=0.3)                        # clear tape goes over the label to protect it

# gloves box dropped 31 Oct 2026: he found it ugly and the counter has enough products
syringes_in_cup(loc=(0.27, -0.1, 0))
pen_cup(loc=(-0.34, -0.09, 0))
sticky_notes(loc=(-0.22, -0.14, 0), rot=-0.2)

# where the label ends up: a filled 20 DR vial with its label on, and an empty one waiting
amox = (principled('Gelatin maroon', (0.32, 0.03, 0.05), rough=0.12, coat=0.6), principled('Gelatin mustard', (0.86, 0.58, 0.1), rough=0.12, coat=0.6))
v = vial('Labelled vial', 20, 'amber', 'cr', loc=(-0.12, -0.06, 0))
fill_vial(v, 20, 12, amox, seed=3)
label_wrap(v, 20, os.path.join(TEX, 'rx_label_amox.png'), frac=0.62, rot=-1.4)
vial('Empty vial', 20, 'amber', 'cr', loc=(-0.055, -0.1, 0), cap_off=(-0.01, -0.135, True))

shoot(OUT, SAMPLES, cam_loc=(0.0, -0.86, 0.42), target=(0.0, 0.05, 0.05), focus=(0.0, -0.04, 0.06))
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(HERE, 'label_station.blend'))
print('DONE')
