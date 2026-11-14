# Wood Chop mango wood chopping board (53d21ba3), 38 x 20 x 2.5 cm, no sleeve. The face is the board's own grain lifted from the
# listing's straight-on photo (the parts above and below the sleeve, feathered together where the sleeve was), so it is this
# board's figure and colour; softly rounded corners and edges; the black powder-coated strap handle on the end.
#   blender -b -P chopping_board.py -- <outdir>
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from klib import *

reset()
L, Wd, T = 0.38, 0.20, 0.025
im = bpy.data.images.load(os.path.join(HERE, 'src', '53d21ba3', '0.webp')); IW, IH = im.size
px = np.empty(IW * IH * 4, np.float32); im.pixels.foreach_get(px); px = px.reshape(IH, IW, 4)[::-1, :, :3]   # row 0 = photo top
X0, X1 = 92, 642
top = px[92:296, X0:X1]; bot = px[668:968, X0:X1]
F = 70
def xfade(p, q):
    w_ = np.linspace(0, 1, F)[:, None, None] ** 1.0; w_ = w_ * w_ * (3 - 2 * w_)
    return np.concatenate([p[:-F], p[-F:] * (1 - w_) + q[:F] * w_, q[F:]], 0)
face = xfade(xfade(top, bot[:, ::-1]), bot)                            # three real stretches of this board, softly joined
rows = np.linspace(0, face.shape[0] - 1, 876)                          # to the board's true proportions (grain stretches lengthwise)
face = face[np.round(rows).astype(int)]
g = face.mean(axis=2, keepdims=True); face = np.clip(g + (face - g) * 1.35, 0, 1) * 0.92  # back to the photo's warm orange
img = np_img('mango face', face[::-1].copy())                         # back to bottom-up for Blender
nrm_h = face.mean(axis=2); nrm_h = (nrm_h - nrm_h.min()) / (nrm_h.max() - nrm_h.min())
MANGO = tex_mat('Mango Wood', img, 0.55, 0.0, np_img('mango nrm', height_to_normal(nrm_h[::-1].copy(), 1.5), noncolor=True), 0.25)
b = slab('Board', rrect(L, Wd, 0.012, 12), 0, T, MANGO, bevel=0.0035, bseg=4)
planar_uv(b, Wd, L, axes='yx')
uv = b.data.uv_layers.active.data
me = b.data
for p in me.polygons:                                                  # sides: grain runs along the length, not smeared
    n = p.normal
    if abs(n.z) > 0.6: continue
    for li, vi in zip(p.loop_indices, p.vertices):
        c = me.vertices[vi].co
        if abs(n.y) >= abs(n.x): uv[li].uv = (0.15 + 0.12 * c.z / T + (0.5 if n.y > 0 else 0), c.x / L + 0.5)
        else: uv[li].uv = (c.y / Wd + 0.5, 0.3 + 0.12 * c.z / T)
BLK = pmat('Black Powder Coat', (0.03, 0.03, 0.032), 0.45, 0.4)
half = [(L / 2 - 0.0005, -0.050), (L / 2 + 0.006, -0.050), (L / 2 + 0.014, -0.046), (L / 2 + 0.020, -0.038), (L / 2 + 0.022, -0.026), (L / 2 + 0.022, 0.0)]
path = [(x, y, T / 2) for x, y in half] + [(x, -y, T / 2) for x, y in reversed(half[:-1])]
sweep('Handle', path, BLK, profile=superellipse(0.0045, 0.0018, 4.0, 40), twist_up=(0, 0, 1), n=10)
for y in (-0.052, 0.052):
    slab('Foot', rrect(0.003, 0.018, 0.0012, 4), T / 2 - 0.0065, T / 2 + 0.0065, BLK, bevel=0.0006).location = (L / 2 + 0.0015, y, 0)
    cyl(0.0022, 0.0012, (L / 2 + 0.0035, y, T / 2), pmat('Screw', (0.55, 0.55, 0.55), 0.3, 1.0), rot=(0, math.pi / 2, 0), v=24)
finish('chopping_board', 'Wood Chop Mango Wood Chopping Board', view=(0.35, -1, 0.8))
print('DONE')
