# P-Plus stainless basting brush (71a93adf), 21.5 cm, from its listing photos: a one-piece brushed-steel handle (pear-shaped
# end with a split ring through it, long slim waist, a narrow neck flaring into a flat spade socket), a black silicone head:
# a rounded collar and two staggered rows of round silicone strands with rounded tips.   blender -b -P basting_brush.py -- <out>
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from klib import *

reset()
ZC = 0.0048
def loft(name, secs, m, N=64, ustep=0.05):
    """secs: (x, width_y, thick_z, n) superellipse sections along x, closed with end points; UV u = x/ustep (along), v around."""
    bm = bmesh.new(); uvl = bm.loops.layers.uv.new('UV'); rings = []
    for x, w, t, n in secs:
        rings.append([bm.verts.new((x, y, ZC + z)) for y, z in superellipse(w / 2, t / 2, n, N)])
    for i in range(len(rings) - 1):
        for k in range(N):
            k1 = (k + 1) % N; f = bm.faces.new((rings[i][k], rings[i][k1], rings[i + 1][k1], rings[i + 1][k]))
            for lp, (ii, kk) in zip(f.loops, ((i, k), (i, k + 1), (i + 1, k + 1), (i + 1, k))): lp[uvl].uv = (secs[ii][0] / ustep, kk / N)
    c0 = bm.verts.new((secs[0][0] - 0.0012, 0, ZC)); c1 = bm.verts.new((secs[-1][0], 0, ZC))
    for k in range(N):
        bm.faces.new((c0, rings[0][(k + 1) % N], rings[0][k])); bm.faces.new((c1, rings[-1][k], rings[-1][(k + 1) % N]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return mesh_obj(name, bm, [m])

STEEL = brushed_steel('Brushed Steel', 'u', 0.3, (0.80, 0.80, 0.79))
SIL = pmat('Black Silicone', (0.035, 0.035, 0.038), 0.42)
H = [(0.0000, 0.0050, 0.0036, 2.0), (0.0010, 0.0100, 0.0072, 2.0), (0.0030, 0.0145, 0.0098, 2.1), (0.0070, 0.0175, 0.0112, 2.2),
     (0.0140, 0.0190, 0.0118, 2.2), (0.0220, 0.0188, 0.0116, 2.2), (0.0350, 0.0175, 0.0110, 2.2), (0.0550, 0.0152, 0.0100, 2.2),
     (0.0800, 0.0130, 0.0092, 2.2), (0.1020, 0.0116, 0.0086, 2.25), (0.1180, 0.0108, 0.0082, 2.3), (0.1260, 0.0106, 0.0080, 2.35)]
for i in range(1, 13):
    t = i / 12; x = 0.1260 + 0.032 * t
    H.append((x, 0.0106 + (0.0365 - 0.0106) * t ** 1.7, 0.0080 - 0.0004 * t, 2.35 + 2.1 * t))
H += [(0.1615, 0.0366, 0.0076, 4.45), (0.1640, 0.0362, 0.0072, 4.45)]
h = loft('Handle', H, STEEL, N=96)
hole = cutter_cyl(0.0022, 0.03, (0.0048, 0, ZC), v=32); cut(h, hole)
bpy.ops.mesh.primitive_torus_add(major_radius=0.0098, minor_radius=0.0011, major_segments=96, minor_segments=16, location=(-0.0046, 0, ZC), rotation=(math.pi / 2, 0, 0))
ring = bpy.context.object; ring.data.materials.append(pmat('Ring Steel', (0.86, 0.86, 0.85), 0.18, 1.0)); P.append(ring)
# silicone collar: a rounded band that the steel spade plugs into
col = loft('Collar', [(0.1626, 0.0372, 0.0084, 4.4), (0.1638, 0.0382, 0.0092, 4.4), (0.1712, 0.0382, 0.0092, 4.4), (0.1724, 0.0372, 0.0084, 4.4)], SIL, N=96)
# strands: two staggered rows, round, slightly tapered, rounded tips, a gentle fan and droop
rng = np.random.default_rng(7)
for row, (dz, n) in enumerate(((0.0019, 16), (-0.0019, 15))):
    for i in range(n):
        y = (i - (n - 1) / 2) * 0.00228 + (0.00114 if row else 0)
        L = 0.0435 + rng.uniform(-0.0015, 0.0015); fan = y * 0.12; droop = -0.0006 - abs(y) * 0.02
        x0 = 0.1715; path = [(x0, y, ZC + dz), (x0 + L * 0.5, y + fan * 0.5, ZC + dz + droop * 0.3), (x0 + L, y + fan, ZC + dz + droop)]
        r0 = 0.00108; s = sweep('Strand', path, SIL, profile=[(r0 * math.cos(2 * math.pi * k / 20), r0 * math.sin(2 * math.pi * k / 20)) for k in range(20)],
                                 n=6, scale_fn=lambda t: (1 - 0.22 * t, 1 - 0.22 * t))
        bpy.ops.mesh.primitive_uv_sphere_add(radius=r0 * 0.78, segments=20, ring_count=10, location=path[-1]); tip = bpy.context.object
        tip.data.materials.append(SIL); P.append(tip)
finish('basting_brush', 'P-Plus Stainless Steel Silicone Basting Brush', view=(0.35, -1, 0.9))
print('DONE')
