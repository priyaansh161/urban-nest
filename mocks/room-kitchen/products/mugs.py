# SHAY teal coffee mugs (04283da4), 8.5 x 9.5 cm, 300 ml, from the Amazon photos: a soft U-shaped porcelain mug, widest just below
# the rim, glossy teal outside, glossy coffee-brown inside and on the rim, an unglazed foot ring, an ear-shaped C handle.
# Two of the set, as they'd sit together.   blender -b -P mugs.py -- <outdir>
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from klib import *

reset()
TEAL = pmat('Teal Glaze', (0.06, 0.30, 0.32), 0.12, coat=1.0, coat_rough=0.03)
BROWN = pmat('Coffee Brown Glaze', (0.66, 0.36, 0.13), 0.14, coat=1.0, coat_rough=0.03)
CLAY = pmat('Unglazed Porcelain', (0.86, 0.80, 0.72), 0.75)
# outer wall (teal) up to the rim, rim + inside (brown), foot (clay); a thin wall with a rounded lip
PROF = [(0, 0.0030), (0.0220, 0.0028), (0.0272, 0.0000), (0.0298, 0.0002), (0.0310, 0.0022),          # foot ring (clay)
        (0.0328, 0.0055), (0.0362, 0.0140), (0.0392, 0.0280), (0.0415, 0.0460), (0.0428, 0.0650), (0.0432, 0.0820), (0.0430, 0.0925),  # wall (teal)
        (0.0425, 0.0945), (0.0417, 0.0953), (0.0408, 0.0948),                                                                   # rim (brown)
        (0.0405, 0.0925), (0.0407, 0.0820), (0.0403, 0.0650), (0.0390, 0.0460), (0.0366, 0.0280), (0.0334, 0.0150), (0.0260, 0.0080), (0, 0.0068)]
MID = [0] * 5 + [1] * 7 + [2] * 11
def mug(x, y, rz):
    m = lathe('Mug', PROF, [CLAY, TEAL, BROWN], midx=MID, seg=192)
    h = sweep('Handle', [(0.0360, 0, 0.0815), (0.0440, 0, 0.0842), (0.0540, 0, 0.0868), (0.0650, 0, 0.0830), (0.0720, 0, 0.0710),
                         (0.0735, 0, 0.0560), (0.0705, 0, 0.0430), (0.0640, 0, 0.0335), (0.0560, 0, 0.0290), (0.0470, 0, 0.0262), (0.0360, 0, 0.0240)], TEAL,
              profile=superellipse(0.0072, 0.0050, 2.4, 64), twist_up=(0, 1, 0), n=14,
              scale_fn=lambda t: ((1 - 0.12 * t) * (1 + 0.28 * max(0, 1 - t / 0.16) + 0.22 * max(0, (t - 0.84) / 0.16)), (1 - 0.08 * t) * (1 + 0.2 * max(0, 1 - t / 0.16) + 0.15 * max(0, (t - 0.84) / 0.16))))
    cut(m, h, op='UNION')                                     # the handle fused into the wall
    cav = lathe('Cavity', [(0, 0.0069), (0.0258, 0.0081), (0.0332, 0.0151), (0.0364, 0.0281), (0.0388, 0.0461), (0.0401, 0.0651),
                           (0.0405, 0.0821), (0.04035, 0.0925), (0.04035, 0.1300), (0, 0.1300)], [BROWN], seg=192)
    cut(m, cav)                                               # nothing pokes into the inside
    m.matrix_world = Matrix.Translation((x, y, 0)) @ Matrix.Rotation(rz, 4, 'Z')
mug(-0.052, 0.012, math.radians(205))
mug(0.050, -0.010, math.radians(-30))
finish('mugs', 'SHAY Teal Coffee Mugs', view=(0.25, -1, 0.45))
print('DONE')
