# Wooden spatula rest (2759a7b9), acacia, 11.9 x 11.4 x 1.8 cm, from its Amazon photos: a spatula-head outline (slightly wider at
# the back, a shallow concave front edge where the handle leaves), a scooped dish that rises into a thick rounded back roll,
# rounded edges, flat underside; carved-wood grain: the growth rings show as contours that follow the dish.
#   blender -b -P wood_rest.py -- <outdir>
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from klib import *

reset()
XF, XB = -0.0570, 0.0570
def w(x): return 0.0575 - 0.0100 * math.exp(-((x - 0.028) / 0.022) ** 2) - 0.0030 * smoothstep((x - 0.030) / 0.03)
def xfront(yn): return XF + 0.0060 * (1 - yn * yn)
def ztop(x, y):
    t = 0.0120 + 0.0060 * smoothstep((x - 0.010) / 0.040)                 # front rim, thick back roll
    dish = 0.0085 * math.exp(-((x + 0.006) / 0.040) ** 4 - (y / (w(x) - 0.010)) ** 4)
    z = t - dish
    eb = 0.0075; db = XB - x                                               # back edge rolls over
    if db < eb: z -= eb - math.sqrt(max(eb * eb - (eb - db) ** 2, 0))
    es = 0.0035; ds = w(x) - abs(y)                                        # side and front edges rounded
    if ds < es: z -= es - math.sqrt(max(es * es - (es - ds) ** 2, 0))
    df = x - xfront(y / w(x))
    if df < es: z -= es - math.sqrt(max(es * es - (es - df) ** 2, 0))
    return max(z, 0.0012)
NS, NV = 160, 120
bm = bmesh.new(); uvl = bm.loops.layers.uv.new('UV'); top, bot = [], []
for i in range(NS + 1):
    s = i / NS; rt, rb = [], []
    for j in range(NV + 1):
        vn = -1 + 2 * j / NV; vv = math.sin(vn * math.pi / 2)
        x0 = xfront(vv); x = x0 + (XB - x0) * (0.5 - 0.5 * math.cos(math.pi * s)); y = vv * w(x)
        rt.append(bm.verts.new((x, y, ztop(x, y)))); rb.append(bm.verts.new((x, y, 0.0)))
    top.append(rt); bot.append(rb)
def face(vs):
    f = bm.faces.new(vs); f.normal_update(); side = abs(f.normal.z) < 0.5
    for lp in f.loops:
        c = lp.vert.co
        lp[uvl].uv = ((c.x + c.y) / 0.30 + 0.5, c.z / 0.30 + 0.2) if side else (c.x / 0.30 + 0.5, c.y / 0.30 + 0.5)
for i in range(NS):
    for j in range(NV):
        face((top[i][j], top[i + 1][j], top[i + 1][j + 1], top[i][j + 1])); face((bot[i][j], bot[i][j + 1], bot[i + 1][j + 1], bot[i + 1][j]))
    face((top[i][0], bot[i][0], bot[i + 1][0], top[i + 1][0])); face((top[i][NV], top[i + 1][NV], bot[i + 1][NV], bot[i][NV]))
for j in range(NV):
    face((top[0][j], top[0][j + 1], bot[0][j + 1], bot[0][j])); face((top[NS][j], bot[NS][j], bot[NS][j + 1], top[NS][j + 1]))
bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-7); bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
ACACIA = wood('Acacia', (0.36, 0.21, 0.12), (0.66, 0.45, 0.30), 0.45, contrast=0.75)
mesh_obj('Rest', bm, [ACACIA])
finish('wood_rest', 'Wooden Spatula Rest', view=(0.35, -1, 0.85))
print('DONE')
