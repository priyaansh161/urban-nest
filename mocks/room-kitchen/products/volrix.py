# VOLRIX 500 ml 2-in-1 oil sprayer / pourer (b16d9948), cream version as on the listing, from its Amazon photos (8 x 18.5 cm):
# a borosilicate bottle that narrows slightly upward, thick base, oil to about 60 %; a cream PP head with a gravity flap and a
# lever tab on top, a round spray nozzle on the side, an L-shaped handle; the clear suction straw with its filter inside.
#   blender -b -P volrix.py -- <outdir>
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from klib import *

reset()
GLASS = see_through('Borosilicate Glass', (0.90, 0.95, 0.94), 0.16, 0.02, coat=1.0)
OIL = see_through('Oil', (0.95, 0.62, 0.0), 0.86, 0.03, glow=(0.55, 0.30, 0.0))
CREAM = pmat('Cream PP', (0.92, 0.90, 0.85), 0.32, coat=0.2)
STRAW = see_through('Straw', (0.95, 0.95, 0.93), 0.45, 0.1)
DARK = pmat('Nozzle Hole', (0.05, 0.05, 0.05), 0.6)
def r_at(z): return 0.0400 - (0.0400 - 0.0352) * (z - 0.008) / (0.124 - 0.008)
lathe('Bottle', [(0, 0.0062), (0.020, 0.0058), (0.0330, 0.0040), (0.0372, 0.0010), (0.0390, 0.0), (0.0398, 0.0025), (0.0400, 0.0080),
                 (r_at(0.06), 0.06), (0.0352, 0.1240), (0.0336, 0.1265), (0.0318, 0.1275), (0.0318, 0.1330), (0.0296, 0.1330), (0.0296, 0.1270),
                 (r_at(0.124) - 0.0025, 0.1220), (r_at(0.06) - 0.0025, 0.06), (0.0375, 0.0085), (0.0360, 0.0068), (0.020, 0.0064), (0, 0.0066)], [GLASS], seg=192)
lathe('Oil', [(0, 0.0068), (0.0358, 0.0068), (0.0372, 0.0082), (r_at(0.06) - 0.0028, 0.06), (r_at(0.098) - 0.0028, 0.0980), (r_at(0.099) - 0.0031, 0.0986),
              (0.030, 0.0983), (0, 0.0982)], [OIL], seg=192)
# head: a cylinder with a softly rounded top
lathe('Head', [(0.0320, 0.1255), (0.0352, 0.1258), (0.0358, 0.1268), (0.0358, 0.1660), (0.0354, 0.1688), (0.0342, 0.1708), (0.0322, 0.1720),
               (0.0290, 0.1726), (0, 0.1726), (0, 0.1300), (0.0320, 0.1300)], [CREAM], seg=192, closed=True)
lathe('Head Band', [(0.0359, 0.1305), (0.0362, 0.1308), (0.0362, 0.1318), (0.0359, 0.1321)], [CREAM], seg=192, closed=True)
# L-shaped handle on the left
sweep('Handle', [(-0.032, 0, 0.1625), (-0.046, 0, 0.1630), (-0.057, 0, 0.1615), (-0.0632, 0, 0.1560), (-0.0645, 0, 0.1460), (-0.0645, 0, 0.1180),
                 (-0.0640, 0, 0.1100)], CREAM, profile=superellipse(0.0078, 0.0052, 3.0, 64), twist_up=(0, 1, 0), n=12)
bpy.ops.mesh.primitive_uv_sphere_add(radius=1, segments=48, ring_count=24, location=(-0.0640, 0, 0.1102)); e = bpy.context.object
e.scale = (0.0052, 0.0078, 0.0035); e.data.materials.append(CREAM); P.append(e)
# lever tab over the handle, and the gravity flap on top
sweep('Lever', [(-0.004, 0, 0.1735), (-0.018, 0, 0.1760), (-0.030, 0, 0.1810), (-0.035, 0, 0.1835)], CREAM,
      profile=superellipse(0.0085, 0.0024, 3.2, 48), twist_up=(0, 1, 0), n=10, scale_fn=lambda t: (1 - 0.15 * t, 1))
f = slab('Flap', rrect(0.026, 0.030, 0.008, 10), 0.0, 0.0065, CREAM, bevel=0.0018)
f.matrix_world = Matrix.Translation((0.014, 0, 0.1738)) @ Matrix.Rotation(math.radians(-14), 4, 'Y') @ Matrix.Translation((-0.013, 0, -0.002))
cyl(0.0030, 0.012, (0.006, 0, 0.1752), CREAM, rot=(math.pi / 2, 0, 0), v=32)
# spray nozzle on the right, with its hole
cyl(0.0068, 0.0070, (0.0378, 0, 0.1580), CREAM, rot=(0, math.pi / 2, 0), v=64, bev=0.0012)
cyl(0.0016, 0.0016, (0.0413, 0, 0.1580), DARK, rot=(0, math.pi / 2, 0), v=24)
# suction straw and filter inside
sweep('Straw', [(0.000, 0.002, 0.1300), (0.002, 0.004, 0.0900), (0.010, 0.010, 0.0450), (0.018, 0.014, 0.0180)], STRAW, r=0.0021, n=10)
lathe('Filter', [(0, 0.0070), (0.0052, 0.0070), (0.0055, 0.0085), (0.0055, 0.0175), (0.0030, 0.0190), (0, 0.0190)], [pmat('Filter', (0.75, 0.75, 0.73), 0.5)], seg=48)[0:0] if False else None
fo = P[-1]; fo.location = (0.018, 0.014, 0)
finish('volrix', 'VOLRIX 500 ml 2-in-1 Glass Oil Dispenser', view=(0.25, -1, 0.3))
print('DONE')
