# Rangchhelo tissue box cover (194251f4): 24 cm long, ~12.5 deep (the photo: the listing's 9 cm width does not match it),
# 9 cm tall. Glossy white body with softly rounded corners, a light oak lid sitting in it with a stadium slot, a beige tissue
# pulled up through the slot.   blender -b -P tissue_box.py -- <outdir>
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from klib import *

reset()
L, D, Hh = 0.24, 0.125, 0.09
WHITE = pmat('Glossy White PP', (0.93, 0.93, 0.92), 0.2, coat=0.4)
OAK = wood('Light Oak', (0.56, 0.38, 0.21), (0.84, 0.66, 0.45), 0.5, contrast=0.55)
TISSUE = pmat('Beige Tissue', (0.93, 0.82, 0.62), 0.9)
b = slab('Body', rrect(L, D, 0.016, 10), 0, Hh - 0.008, WHITE, bevel=0.006, bseg=4)
cut(b, slab('c', rrect(L - 0.006, D - 0.006, 0.013, 10), 0.004, Hh, None, bevel=0, keep=False))
lid = slab('Lid', rrect(L - 0.001, D - 0.001, 0.0155, 10), Hh - 0.010, Hh, OAK, bevel=0.0015, bseg=2)
cut(lid, slab('slot', rrect(0.125, 0.036, 0.018, 12), Hh - 0.02, Hh + 0.01, None, bevel=0, keep=False))
planar_uv(lid, 0.30, 0.30)
slab('Stack', rrect(L - 0.012, D - 0.012, 0.010, 8), 0.004, Hh - 0.016, TISSUE, bevel=0.002)     # the tissues inside, seen through the slot
bm = bmesh.new(); uvl = bm.loops.layers.uv.new('UV'); NU, NH = 48, 36; rows = []
for j in range(NH + 1):                                         # the pulled sheet: wide along the box, crumpled, folding over at the top
    h = j / NH; row = []
    for i in range(NU + 1):
        u = i / NU * 2 - 1; w = 0.048 + 0.010 * h
        y = 0.003 * math.sin(u * 4 + h * 5) * (0.3 + h) + 0.0012 * math.sin(u * 11 - h * 9) * h + 0.012 * h * h - 0.004 * (1 - u * u) * h
        z = Hh - 0.012 + 0.085 * h - 0.012 * h ** 3 * (0.5 + 0.5 * math.sin(u * 3))
        row.append(bm.verts.new((u * w + 0.003 * math.sin(h * 11), y, z)))
    rows.append(row)
for j in range(NH):
    for i in range(NU):
        f = bm.faces.new((rows[j][i], rows[j][i + 1], rows[j + 1][i + 1], rows[j + 1][i]))
        for lp in f.loops: lp[uvl].uv = (lp.vert.co.x * 8, lp.vert.co.z * 8)
bmesh.ops.solidify(bm, geom=bm.faces[:], thickness=0.0006)
mesh_obj('Tissue', bm, [TISSUE])
finish('tissue_box', 'Rangchhelo Wood Lid Tissue Box', view=(0.45, -1, 0.6))
print('DONE')
