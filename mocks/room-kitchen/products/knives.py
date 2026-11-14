# "Green Knife Set" (c65af49f): paring, chef and slicing knives, from the listing photo (scaled from the chef's ~33 cm):
# champagne-coated blades (straight spine, the edge curving up to the tip), a beige collar over each heel, light rubberwood
# handles widening toward the end, a thin green cap on each end. Lying flat side by side as in the photo.
#   blender -b -P knives.py -- <outdir>
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from klib import *

reset()
BLADE = pmat('Champagne Coated Steel', (0.90, 0.82, 0.68), 0.36, 0.35)
COLLAR = pmat('Beige Collar', (0.86, 0.80, 0.66), 0.4)
CAP = pmat('Green End Cap', (0.42, 0.55, 0.25), 0.5)
WOOD = wood('Rubberwood', (0.52, 0.34, 0.19), (0.80, 0.60, 0.40), 0.55, contrast=0.6)
HT = 0.0085                                                     # half the handle's thickness: the knives lie on their side
def knife(x0, bl, bw, hl, hw, flip=False):
    s = -1 if flip else 1
    pts = []
    for k in range(41):                                         # spine: straight, dropping a touch into the tip
        t = k / 40; pts.append((s * (bw / 2 - bw * 0.22 * max(0, (t - 0.82) / 0.18) ** 2), t * bl))
    for k in range(40, -1, -1):                                 # edge: straight at the heel, sweeping up to the tip
        t = k / 40; pts.append((s * (-bw / 2 + bw * 0.78 * t ** 2.6), t * bl))
    if flip: pts.reverse()
    b = slab('Blade', [(x0 + x, y) for x, y in pts], HT - 0.0009, HT + 0.0009, BLADE, bevel=0.0006, bseg=2)
    slab('Collar', rrect(bw + 0.003, 0.018, 0.004, 6), HT - 0.0055, HT + 0.0055, COLLAR, bevel=0.002).location = (x0, 0.004, 0)
    sweep('Handle', [(x0, -0.006, HT), (x0, -hl * 0.5, HT), (x0, -hl, HT)], WOOD, profile=superellipse(hw / 2, HT, 2.6, 40), twist_up=(0, 0, 1), n=24,
          scale_fn=lambda t: (0.86 + 0.14 * t ** 0.8, 0.88 + 0.12 * t))
    h = P[-1]; planar_uv(h, 0.15, 0.15, axes='xy')
    slab('Cap', superellipse(hw / 2 * 0.98, HT * 0.98, 2.6, 40), 0, 0.003, CAP, bevel=0.0008)
    c = P[-1]; c.matrix_world = Matrix.Translation((x0, -hl - 0.0005, HT)) @ Matrix.Rotation(math.pi / 2, 4, 'X')
knife(-0.075, 0.082, 0.019, 0.113, 0.021, flip=True)            # paring
knife(0.0, 0.190, 0.047, 0.124, 0.029)                           # chef
knife(0.072, 0.183, 0.034, 0.122, 0.027)                         # slicer
finish('knives', 'Green Knife Set of 3', view=(0.0, -0.35, 1.0))
print('DONE')
