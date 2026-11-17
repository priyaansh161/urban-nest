# "Encasa XO Leather Dining Table Mats, Olive" (f28ded20): a set of four 42 x 30 cm placemats and four 9 cm coasters
# in grey-olive PU leather (suede-feel, matte, faintly mottled), soft rounded corners, about 2 mm thick.
# Laid out as the listing's cover: the four mats fanned down-right one on another, the coasters in a row in front.
#   blender -b -P mats.py -- <outdir>
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'room-kitchen', 'products'))
from klib import *

reset()
N = 1024
mott = tile_noise(N, N, 18, 18, seed=5); fine = tile_noise(N, N, 260, 260, seed=6)
base = np.array((0.26, 0.295, 0.26))
col = base[None, None, :] * (0.92 + 0.10 * mott[..., None] + 0.05 * fine[..., None])
LE = tex_mat('Olive PU Leather', np_img('leather', np.clip(col, 0, 1)), 0.78, 0.0, np_img('leather n', height_to_normal(0.7 * fine + 0.3 * mott, 1.2), noncolor=True), 0.25)
def piece(w, d, r, x, y, z):
    o = slab('Mat', [(px + x, py + y) for px, py in rrect(w, d, r, 10)], z, z + 0.0018, LE, bevel=0.0006, bseg=2)
    planar_uv(o, 0.30, 0.30); return o
for k in range(4):                                   # back mat first, each next one lower-right and on top
    piece(0.42, 0.30, 0.012, -0.075 + 0.05 * k, 0.07 - 0.048 * k, 0.0018 * k)
for k in range(4):
    piece(0.09, 0.09, 0.012, -0.21 + 0.115 * k + (0.03 if k else 0), -0.26, 0)
finish('mats', 'Encasa XO Olive Leather Placemats, Set of 4', view=(0.0, -0.6, 1.0))
print('DONE')
