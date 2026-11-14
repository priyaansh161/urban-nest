# True Decor sage-green enamel butter dish with lid (3bc04eb5), 17 x 11 x 8 cm, from its Amazon photos: a deep lid with straight
# sides, big rounded corners and a softly rounded top edge, a riveted stainless strap handle, the white "BEAUTIFUL HOME · BUTTER ·
# FOR EVERYDAY SMART LIVING" house emblem (taken off the straight-on product photo), on a flat tray with a flared rim.
#   blender -b -P butter_dish.py -- <outdir>
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from klib import *

reset()
G = pmat('Sage Enamel', (0.56, 0.68, 0.58), 0.22, coat=0.6, coat_rough=0.08)
STEEL = pmat('Handle Steel', (0.82, 0.82, 0.81), 0.22, 1.0)
def loft_rr(name, rings_spec, m, seg=10, cap_bottom=True, cap_top=True):
    bm = bmesh.new(); rings = []
    for w, d, r, z in rings_spec: rings.append([bm.verts.new((x, y, z)) for x, y in rrect(w, d, r, seg)])
    K = len(rings[0])
    for a, b in zip(rings, rings[1:]):
        for k in range(K): bm.faces.new((a[k], a[(k + 1) % K], b[(k + 1) % K], b[k]))
    if cap_bottom: bm.faces.new(rings[0][::-1])
    if cap_top:
        c = bm.verts.new((0, 0, rings_spec[-1][3]))
        for k in range(K): bm.faces.new((rings[-1][k], rings[-1][(k + 1) % K], c))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return mesh_obj(name, bm, [m])
# tray: flat floor, flared rim with a rolled lip
loft_rr('Tray', [(0.150, 0.090, 0.016, 0.0000), (0.156, 0.096, 0.018, 0.0012), (0.168, 0.108, 0.021, 0.0080), (0.172, 0.112, 0.022, 0.0105),
                 (0.1735, 0.1135, 0.0225, 0.0118), (0.1722, 0.1122, 0.0222, 0.0126), (0.1690, 0.1090, 0.0215, 0.0112), (0.1560, 0.0960, 0.0180, 0.0042),
                 (0.1500, 0.0900, 0.0165, 0.0030)], G, seg=12)
# lid: straight sides with a slight draft, a rounded top edge
LW, LD, LR, Z0, ZS, RT = 0.152, 0.095, 0.020, 0.0040, 0.0680, 0.0070
spec = [(LW, LD, LR, Z0), (LW, LD, LR, Z0 + 0.0015)]
for k in range(1, 7): t = k / 7; spec.append((LW - 0.0015 * t, LD - 0.0015 * t, LR, Z0 + (ZS - Z0) * t))
for k in range(0, 13):
    a = math.radians(90 * k / 12); inset = RT * (1 - math.cos(a)); spec.append((LW - 0.0015 - 2 * inset, LD - 0.0015 - 2 * inset, max(LR - inset, 0.004), ZS + RT * math.sin(a)))
loft_rr('Lid', spec, G, seg=12)
ZT = ZS + RT
# strap handle with riveted feet
path = [(-0.050, 0, ZT + 0.0016), (-0.040, 0, ZT + 0.0016), (-0.034, 0, ZT + 0.0040), (-0.029, 0, ZT + 0.0140), (-0.022, 0, ZT + 0.0270),
        (-0.011, 0, ZT + 0.0335), (0.0, 0, ZT + 0.0350)]
path = path + [(-x, y, z) for x, y, z in reversed(path[:-1])]
sweep('Handle', path, STEEL, profile=superellipse(0.0060, 0.0013, 4.0, 48), twist_up=(0, 1, 0), n=12)
for x in (-0.044, 0.044):
    lathe('Rivet', [(0, ZT + 0.0028), (0.0028, ZT + 0.0028), (0.0026, ZT + 0.0036), (0.0016, ZT + 0.0042), (0, ZT + 0.0044)], [STEEL], seg=32).location.x = x
# the emblem, lifted off the straight-on photo: white print -> alpha, over the lid front
im = bpy.data.images.load(os.path.join(HERE, 'amz', 'butter_dish', 'B0DS27N1V3-2.jpg')); W_, H_ = im.size
px = np.empty(W_ * H_ * 4, np.float32); im.pixels.foreach_get(px); px = px.reshape(H_, W_, 4)
x0, y0t, S = 545, 664, 460; crop = px[H_ - (y0t + S):H_ - y0t, x0:x0 + S, :3]
mn = crop.min(axis=2); a = np.clip((mn - 0.70) / 0.14, 0, 1)
yy, xx = np.mgrid[0:S, 0:S]; a *= (np.hypot(xx - S / 2, yy - S / 2) < S * 0.49)
dec = np.zeros((S, S, 4), np.float32); dec[..., :3] = (0.96, 0.96, 0.93); dec[..., 3] = a
print('EMBLEM alpha mean', float(a.mean()), 'max', float(a.max()), 'crop mean', float(crop.mean()))
DEC = tex_mat('Emblem Print', np_img('emblem', dec, alpha=True), 0.35, alpha=True)
DEC.use_backface_culling = True
try: DEC.surface_render_method = 'BLENDED'
except Exception: pass
SZ = S * (0.152 / 1090)                                  # photo scale: the lid is 1090 px wide
bpy.ops.mesh.primitive_plane_add(size=1, location=(0.0028, -(LD / 2) - 0.0002, 0.0355), rotation=(math.pi / 2, 0, 0))
pl = bpy.context.object; pl.scale = (SZ, SZ, 1); pl.data.materials.append(DEC); P.append(pl); print('PLANE', pl.name, tuple(round(v, 4) for v in pl.location), SZ)
finish('butter_dish', 'True Decor Butter Dish with Lid', view=(0.15, -1, 0.5))
print('DONE')
