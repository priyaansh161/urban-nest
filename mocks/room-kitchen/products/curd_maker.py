# HomeWiz 1100 ml hung curd maker (b4bd8136), 10 x 8.5 x 18.5 cm, from its Amazon photos: a tall clear container with big rounded
# corners and a thick clear base; a clear lid with a rim and a white vent button; the white inner strainer hanging in the top
# two-thirds, two tall stainless-mesh windows on each long side and one on each end.   blender -b -P curd_maker.py -- <outdir>
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from klib import *

reset()
CLR = see_through('Clear Plastic', (0.90, 0.94, 0.97), 0.13, 0.03, coat=1.0)
WHT = pmat('White PP', (0.94, 0.94, 0.93), 0.35)
N = 256; yy, xx = np.mgrid[0:N, 0:N]
wire = ((xx % 4) < 1) | ((yy % 4) < 1)
mcol = np.where(wire, 0.80, 0.90)[..., None] * np.ones(3) + 0.03 * tile_noise(N, N, 20, 20, seed=2)[..., None]
MESH = tex_mat('Steel Mesh', np_img('mesh', np.clip(mcol, 0, 1)), 0.45, 0.35, np_img('mesh nrm', height_to_normal(wire.astype(float), 1.0), noncolor=True), 0.4)
MESH.use_backface_culling = False
def box_shell(name, w, d, r, z0, z1, t, m, floor=True, bot_t=None):
    o = slab(name, rrect(w, d, r, 14), z0, z1, m, bevel=0.0015, bseg=3)
    cut(o, slab('c', rrect(w - 2 * t, d - 2 * t, max(r - t, 0.002), 14), z0 + (bot_t or t), z1 + 0.05, None, bevel=0, keep=False))
    return o
box_shell('Container', 0.100, 0.085, 0.016, 0.0, 0.168, 0.0018, CLR, bot_t=0.006)
sl = slab('Seal', rrect(0.1006, 0.0856, 0.0163, 14), 0.1660, 0.1675, pmat('Seal', (0.55, 0.30, 0.22), 0.6), bevel=0)
cut(sl, slab('c', rrect(0.0966, 0.0816, 0.0145, 14), 0.160, 0.170, None, bevel=0, keep=False))
slab('Lid Rim', rrect(0.1012, 0.0862, 0.0166, 14), 0.1675, 0.1765, CLR, bevel=0.0018)
slab('Lid', rrect(0.097, 0.082, 0.014, 14), 0.1765, 0.1795, CLR, bevel=0.0012)
lathe('Vent', [(0, 0.1795), (0.0085, 0.1795), (0.0088, 0.1825), (0.0080, 0.1845), (0.0050, 0.1852), (0, 0.1853)], [WHT], seg=64).location = (-0.031, -0.024, 0)
# strainer: rim hanging on the container, body from 0.060 to the top, mesh windows
st = box_shell('Strainer', 0.093, 0.078, 0.013, 0.050, 0.166, 0.0020, WHT, bot_t=0.003)
slab('Strainer Rim', rrect(0.1005, 0.0855, 0.0170, 14), 0.1615, 0.1665, WHT, bevel=0.001)
wins = []
for x in (-0.020, 0.020):
    wins.append(cutter_box((x, 0, 0.104), (0.026, 0.2, 0.084)))
wins.append(cutter_box((0, 0, 0.104), (0.2, 0.040, 0.084)))
cut(st, join_cutters(wins))
for x in (-0.020, 0.020):
    for y in (-0.0378, 0.0378):
        bpy.ops.mesh.primitive_plane_add(size=1, location=(x, y, 0.104), rotation=(math.pi / 2, 0, 0)); p = bpy.context.object
        p.scale = (0.0262, 0.0842, 1); bpy.ops.object.transform_apply(scale=True, rotation=True); p.data.materials.append(MESH); P.append(p)
        planar_uv(p, 0.012, 0.012, axes='xz')
for x in (-0.0453, 0.0453):
    bpy.ops.mesh.primitive_plane_add(size=1, location=(x, 0, 0.104), rotation=(math.pi / 2, 0, math.pi / 2)); p = bpy.context.object
    p.scale = (0.0402, 0.0842, 1); bpy.ops.object.transform_apply(scale=True, rotation=True); p.data.materials.append(MESH); P.append(p)
    planar_uv(p, 0.012, 0.012, axes='yz')
text_mesh('HomeWiz', 0.0085, WHT, Matrix.Translation((0, -0.04275, 0.020)) @ Matrix.Rotation(math.pi / 2, 4, 'X'), ext=0.00005)
finish('curd_maker', 'HomeWiz Hung Curd Maker 1100 ml', view=(0.35, -1, 0.45))
print('DONE')
