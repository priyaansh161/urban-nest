# Kmils 230 ml oil dispenser with brush (46c9cd64), 6.3 x 14.5 cm, from its listing photos: a straight borosilicate jar with a
# thick base, filled most of the way with golden oil; a white cap with a rounded shoulder and a teapot pour spout; a teal
# silicone disc and knob on top; the teal brush hanging inside (flat stem, flared head marked "Brush", seven flat strands).
#   blender -b -P kmils.py -- <outdir>
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from klib import *

reset()
GLASS = see_through('Borosilicate Glass', (0.90, 0.95, 0.94), 0.10, 0.02, coat=1.0)
OIL = see_through('Oil', (0.98, 0.78, 0.20), 0.42, 0.03, glow=(0.20, 0.12, 0.0))   # 20 Nov: lighter, half full, so the brush shows
WHITE = pmat('White Cap', (0.95, 0.95, 0.94), 0.28, coat=0.3)
TEAL = pmat('Teal Silicone', (0.10, 0.33, 0.37), 0.5)
# glass jar: thick base, rounded heel, 2.4 mm wall, a thread band under the cap
lathe('Jar', [(0, 0.0045), (0.012, 0.0042), (0.020, 0.0018), (0.0265, 0.0), (0.0298, 0.0008), (0.0312, 0.0030), (0.0315, 0.0065),
              (0.0315, 0.1000), (0.0302, 0.1003), (0.0302, 0.1045), (0.0291, 0.1050), (0.0291, 0.0068), (0.0285, 0.0062),
              (0.020, 0.0060), (0, 0.0062)], [GLASS], seg=192)
for z in (0.1011, 0.1027):
    lathe('Thread', [(0.0300, z), (0.0310, z + 0.0004), (0.0310, z + 0.0008), (0.0300, z + 0.0012)], [GLASS], seg=192, closed=True)
# oil with a meniscus
lathe('Oil', [(0, 0.0063), (0.0283, 0.0063), (0.0289, 0.0069), (0.0289, 0.0505), (0.0287, 0.0512), (0.025, 0.0508), (0, 0.0506)], [OIL], seg=192)
# cap: straight skirt, generous rounded shoulder, flat top ring
lathe('Cap', [(0.0293, 0.0990), (0.0330, 0.0990), (0.0334, 0.0994), (0.0334, 0.1110), (0.0331, 0.1145), (0.0322, 0.1175), (0.0305, 0.1205),
              (0.0280, 0.1232), (0.0245, 0.1253), (0.0200, 0.1266), (0.0160, 0.1270), (0.0080, 0.1270), (0, 0.1270), (0, 0.1060),
              (0.0293, 0.1060)], [WHITE], seg=192, closed=True)
# pour spout on the left: a short tapered lip, cut flat on top
sp = sweep('Spout', [(-0.018, 0, 0.1182), (-0.030, 0, 0.1192), (-0.0395, 0, 0.1205), (-0.0418, 0, 0.1212)], WHITE,
           profile=superellipse(0.0072, 0.0072, 2.6, 64), twist_up=(0, 0, 1), scale_fn=lambda t: (1 - 0.40 * t, 1 - 0.30 * t), n=12)
cut(sp, cutter_box((-0.034, 0, 0.1300), (0.04, 0.03, 0.012)))
cut(sp, cutter_cyl(0.0028, 0.03, (-0.033, 0, 0.1192), rot=(0, math.pi / 2 - 0.08, 0), v=32))
# teal disc (a low dome) and knob
lathe('Disc', [(0, 0.1268), (0.0158, 0.1268), (0.0160, 0.1276), (0.0150, 0.1290), (0.0110, 0.1302), (0.0060, 0.1307), (0, 0.1307)], [TEAL], seg=128)
lathe('Knob', [(0, 0.1300), (0.0060, 0.1300), (0.0060, 0.1450), (0.0058, 0.1465), (0.0050, 0.1477), (0.0034, 0.1485), (0, 0.1487)], [TEAL], seg=96)
# the brush inside: flat stem, flared head, seven flat strands
stem = slab('Stem', rrect(0.0120, 0.0042, 0.0018, 6), 0.0620, 0.1060, TEAL, bevel=0.0006)
head = []
for i in range(9):
    t = i / 8; z = 0.0620 - 0.0165 * t; w = 0.0120 + 0.0085 * t ** 1.4
    head.append((z, w))
bm = bmesh.new(); rings = []
for z, w in head: rings.append([bm.verts.new((x, y, z)) for x, y in rrect(w, 0.0062, 0.0018, 4)])
for a, b in zip(rings, rings[1:]):
    K = len(a)
    for k in range(K): bm.faces.new((a[k], a[(k + 1) % K], b[(k + 1) % K], b[k]))
bm.faces.new(rings[0]); bm.faces.new(rings[-1][::-1]); bmesh.ops.recalc_face_normals(bm, faces=bm.faces); hd = mesh_obj('Head', bm, [TEAL])
activate(hd); bv = hd.modifiers.new('b', 'BEVEL'); bv.width = 0.0007; bv.segments = 2; bv.limit_method = 'ANGLE'; bpy.ops.object.modifier_apply(modifier='b')
text_mesh('Brush', 0.0042, TEAL, Matrix.Translation((0, -0.0032, 0.0505)) @ Matrix.Rotation(math.pi / 2, 4, 'X'), ext=0.00025)
for i in range(7):
    x = (i - 3) * 0.00285
    s = slab('Strand', rrect(0.0019, 0.0017, 0.0006, 4), 0.0195, 0.0458, TEAL, bevel=0.0003)
    s.location.x = x
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.00085, segments=16, ring_count=8, location=(x, 0, 0.0196)); tip = bpy.context.object; tip.scale = (1.1, 1, 1)
    tip.data.materials.append(TEAL); P.append(tip)
finish('kmils', 'Kmils 230 ml Glass Oil Dispenser with Brush', view=(0.2, -1, 0.35))
print('DONE')
