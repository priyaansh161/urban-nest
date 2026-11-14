# CANWAY kitchen floor runner (258b0233), the 120 x 40 cm piece of the set: its wood-plank print straightened out of the
# listing photo (the photo's light sheen evened out row by row), a soft flat face, a thin dark rubber back, rounded corners.
#   blender -b -P canway_mat.py -- <outdir>
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from klib import *

reset()
W, D = 0.40, 1.20
pr = bpy.data.images.load(os.path.join(HERE, 'ref', 'canway_print.png'))
N = 512; n_ = tile_noise(N, N, 60, 60, seed=4)
TOP = tex_mat('Plank Print', pr, 0.7, 0.0, np_img('canway felt', height_to_normal(n_, 1.2), noncolor=True), 0.2)
RUB = pmat('Dark Rubber Back', (0.04, 0.035, 0.03), 0.8)
slab('Back', rrect(W, D, 0.028, 12), 0, 0.0015, RUB, bevel=0.0004)
top = slab('Face', rrect(W - 0.004, D - 0.004, 0.026, 12), 0.0015, 0.006, TOP, bevel=0.0015, bseg=3)
planar_uv(top, W, D)
finish('canway_mat', 'CANWAY Wood Print Kitchen Runner', view=(0.3, -1, 1.2))
print('DONE')
