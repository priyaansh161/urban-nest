# "Misamo Oil Sprayer, 220 ml Glass, Black" (0d39c328), from its listing photos (21 cm tall, 5.5 cm wide): a clear
# straight glass bottle (11.8 cm) a third full of golden oil, a clear straw curving down to the bottom, and a glossy
# black trigger head (9.2 cm): an hourglass body, oval in plan, flaring to a flat top with the nozzle at the front and
# the trigger lever hooked down in front of it.
#   blender -b -P oil_sprayer.py -- <outdir>
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'room-kitchen', 'products'))
from klib import *

reset()
GL = see_through('Clear Glass', (0.94, 0.96, 0.95), 0.08, 0.02, coat=0.3)
OIL = see_through('Olive Oil', (0.96, 0.70, 0.04), 0.90, 0.05, glow=(0.50, 0.33, 0.0))
STRAW = see_through('Straw', (0.95, 0.95, 0.92), 0.35, 0.1)
BK = pmat('Gloss Black Plastic', (0.025, 0.025, 0.027), 0.14, coat=0.5)
R, HG, HT = 0.0275, 0.118, 0.210
# glass: thin straight walls, a thick base
lathe('Bottle', [(0, 0), (R - 0.002, 0), (R, 0.002), (R, HG), (R - 0.002, HG), (R - 0.002, 0.006), (0, 0.006)], [GL], seg=96, uvs=(1, 1))
lathe('Oil', [(0, 0.006), (R - 0.0024, 0.006), (R - 0.0024, 0.069), (0, 0.069)], [OIL], seg=96)
sweep('Straw', [(0.004, 0.0, HG - 0.002), (0.002, 0.003, 0.07), (-0.004, 0.006, 0.03), (-0.008, 0.004, 0.009)], STRAW, r=0.0018, n=16)
# head: a lathe squashed to an oval, front toward -x
hp = [(0, HG), (R, HG), (R, HG + 0.006), (0.0262, HG + 0.012), (0.0225, HG + 0.035), (0.0195, HG + 0.055), (0.0205, HG + 0.070),
      (0.0235, HG + 0.083), (0.0245, HT - 0.002), (0.022, HT), (0, HT)]
h = lathe('Head', hp, [BK], seg=96, smooth_prof=4); h.scale = (1.0, 0.82, 1.0)
# the band where the head meets the glass
lathe('Collar', [(R + 0.0003, HG - 0.001), (R + 0.0003, HG + 0.003)], [BK], seg=96)
# trigger lever: a curved paddle hanging down in front, from the top front corner
lever = [(-0.019, 0, HT - 0.014), (-0.026, 0, HT - 0.024), (-0.034, 0, HT - 0.036), (-0.038, 0, HT - 0.041)]   # short, angled out
sweep('Lever', lever, BK, profile=superellipse(0.0035, 0.0105, 3.0, 32), twist_up=(0, 1, 0), n=20)
# nozzle: a small boss on the front face near the top
nz = cyl(0.0042, 0.004, (-0.0235, 0, HT - 0.010), BK, rot=(0, math.pi / 2, 0), v=32)
dark = pmat('Nozzle Hole', (0.005, 0.005, 0.005), 0.6); cyl(0.0012, 0.0006, (-0.0258, 0, HT - 0.010), dark, rot=(0, math.pi / 2, 0), v=16)
finish('oil_sprayer', 'Misamo Glass Oil Sprayer 220 ml', view=(-0.6, -1, 0.25))
print('DONE')
