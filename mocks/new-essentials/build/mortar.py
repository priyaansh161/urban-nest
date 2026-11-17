# "Granite Mortar and Pestle Set (4 Inch)" (8bcde770), from its listing photos: grey granite, a 10.2 cm drum 7.6 cm
# tall with a rounded rim band (a groove under it), a groove and a soft bulge at the foot, a deep bowl; the pestle,
# 12.7 cm, standing beside it: a body widening to the grinding end, a neck groove and a rounded knob.
# The granite is made, not photographed: tileable irregular grains (light grey, mid grey, near-black, warm beige, a few
# white) at about 1.5-3 mm, with a faint relief between grains, sealed (semi-gloss) like the photo.
#   blender -b -P mortar.py -- <outdir>
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'room-kitchen', 'products'))
from klib import *

reset()
N, M_ = 1024, 85                                   # texture px; grain cells per 6 cm tile (~0.7 mm, clumped by the warp)
rng = np.random.default_rng(7)
COLS = np.array([(0.74, 0.73, 0.71), (0.56, 0.56, 0.55), (0.22, 0.22, 0.23), (0.66, 0.60, 0.51), (0.90, 0.89, 0.87), (0.40, 0.40, 0.41)])
PROB = np.array([0.27, 0.22, 0.17, 0.15, 0.06, 0.13])
cls = rng.choice(len(COLS), size=(M_, M_), p=PROB)
dy, dx = tile_noise(N, N, 150, 150, seed=1) - 0.5, tile_noise(N, N, 150, 150, seed=2) - 0.5     # warp: irregular grain shapes
ii, jj = np.meshgrid(np.arange(N), np.arange(N), indexing='ij')
si = ((ii + dy * 34) * M_ / N).astype(int) % M_; sj = ((jj + dx * 34) * M_ / N).astype(int) % M_
c = cls[si, sj]
col = COLS[c] * (0.94 + 0.12 * tile_noise(N, N, 200, 200, seed=3)[..., None])
lum = col @ np.array([0.3, 0.59, 0.11])
hm = 0.6 * lum + 0.4 * tile_noise(N, N, 140, 140, seed=4)
GR = tex_mat('Grey Granite', np_img('granite', np.clip(col, 0, 1)), 0.42, 0.0, np_img('granite n', height_to_normal(hm, 3.0), noncolor=True), 0.35)
# mortar
prof = [(0, 0), (0.044, 0), (0.0495, 0.003), (0.051, 0.008), (0.0505, 0.013), (0.0488, 0.016), (0.0495, 0.019),
        (0.0498, 0.030), (0.0498, 0.050), (0.0485, 0.053), (0.048, 0.055), (0.050, 0.057), (0.0512, 0.062), (0.0512, 0.070),
        (0.0495, 0.0745), (0.046, 0.076), (0.039, 0.076), (0.0365, 0.074), (0.035, 0.068), (0.031, 0.052), (0.022, 0.038),
        (0.010, 0.032), (0, 0.031)]
lathe('Mortar', prof, [GR], seg=160, uvs=(5, 16.7), smooth_prof=6)
# pestle, standing to the right
pp = [(0, 0), (0.014, 0.0), (0.0185, 0.004), (0.0195, 0.012), (0.0185, 0.050), (0.0165, 0.090), (0.0158, 0.097),
      (0.0145, 0.101), (0.0165, 0.105), (0.0178, 0.110), (0.0178, 0.120), (0.015, 0.1255), (0.008, 0.127), (0, 0.127)]
p = lathe('Pestle', pp, [GR], seg=96, uvs=(2, 16.7), smooth_prof=6); p.location = (0.082, 0.004, 0)
finish('mortar', 'Granite Mortar and Pestle Set', view=(0.15, -1, 0.45))
print('DONE')
