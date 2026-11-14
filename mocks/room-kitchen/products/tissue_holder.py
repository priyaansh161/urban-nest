# Vintageware wooden kitchen roll holder (7419de18), 13 cm wide x 32.5 cm tall, from its Amazon photos: a turned walnut-stained
# base (rounded ogee edge), a slim dowel, a turned finial (neck, bead, rounded cap); with a quilted kitchen roll on it
# (embossed diamond quilting with a small motif in each diamond).   blender -b -P tissue_holder.py -- <outdir>
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from klib import *

reset()
W = wood('Walnut Stain', (0.20, 0.09, 0.035), (0.46, 0.24, 0.11), 0.35, contrast=0.55, along='v')
lathe('Base', [(0, 0.0), (0.0600, 0.0), (0.0640, 0.0012), (0.0652, 0.0040), (0.0650, 0.0100), (0.0638, 0.0150), (0.0610, 0.0190),
               (0.0560, 0.0215), (0.0470, 0.0232), (0.0300, 0.0240), (0.0150, 0.0246), (0.0118, 0.0262), (0.0110, 0.0280), (0, 0.0280)], [W], seg=192, uvs=(3, 8))
lathe('Dowel', [(0, 0.027), (0.0100, 0.027), (0.0100, 0.2950), (0, 0.2950)], [W], seg=96, uvs=(1, 3))
lathe('Finial', [(0, 0.2930), (0.0085, 0.2930), (0.0080, 0.2980), (0.0068, 0.3010), (0.0080, 0.3030), (0.0115, 0.3045), (0.0120, 0.3060),
                 (0.0112, 0.3075), (0.0095, 0.3085), (0.0130, 0.3110), (0.0150, 0.3150), (0.0152, 0.3190), (0.0140, 0.3225), (0.0110, 0.3250),
                 (0.0060, 0.3264), (0, 0.3268)], [W], seg=128, uvs=(1, 6))
# quilted paper: a height map (diamond seams + a little 4-petal motif in each diamond) -> colour shading + normal map
N = 1024; yy, xx = np.mgrid[0:N, 0:N] / N
u = (xx + yy) * 9; v = (xx - yy) * 9
fu, fv = u % 1 - 0.5, v % 1 - 0.5
seam = np.exp(-(np.minimum(np.abs(fu), np.abs(fv)) / 0.035) ** 2)                 # pressed seams
rr = np.hypot(fu, fv); th = np.arctan2(fv, fu)
motif = np.exp(-((rr - 0.17 - 0.06 * np.cos(4 * th)) / 0.03) ** 2) * (rr < 0.3)   # small flower
puff = 1 - (np.maximum(np.abs(fu), np.abs(fv)) * 2) ** 3                           # pillowy diamonds
hm = np.clip(0.6 * puff - 0.9 * seam - 0.45 * motif, -1, 1); hm = (hm - hm.min()) / (hm.max() - hm.min())
shade = 0.90 + 0.08 * hm
PAPER = tex_mat('Kitchen Roll', np_img('roll', np.dstack([shade, shade, shade * 0.99])), 0.92, 0.0, np_img('roll nrm', height_to_normal(hm, 6.0), noncolor=True), 0.7)
TOP = pmat('Roll Edge', (0.95, 0.95, 0.94), 0.95); CORE = pmat('Card Core', (0.62, 0.45, 0.28), 0.85)
lathe('Roll', [(0.0205, 0.0290), (0.0570, 0.0290), (0.0584, 0.0300), (0.0590, 0.0320), (0.0590, 0.2590), (0.0584, 0.2610), (0.0570, 0.2620),
               (0.0205, 0.2620)], [TOP, PAPER, CORE], midx=[0, 0, 1, 1, 1, 0, 0, 2], closed=True, seg=192, uvs=(3, 4.3))
finish('tissue_holder', 'Vintageware Wooden Kitchen Tissue Roll Holder', view=(0.3, -1, 0.35))
print('DONE')
