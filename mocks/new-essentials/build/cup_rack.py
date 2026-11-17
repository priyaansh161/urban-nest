# "NH10 DESIGNS Stainless Steel Cup Rack" (8c9545a0), from its listing photos: a 12-mug tree in bright stainless wire.
# Two inverted-U frames stand one behind the other, half overlapped, on a rectangular wire base with two cross bars.
# Three tiers of V-shaped hooks: at each tier one V on each frame, the arms rising 45 degrees to a ball on each tip,
# the two V's turned opposite ways so the four balls ring the tree. About 37 cm tall on a 12 x 12 cm base.
#   blender -b -P cup_rack.py -- <outdir>
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'room-kitchen', 'products'))
from klib import *

reset()
ST = pmat('Polished Stainless Steel', (0.86, 0.86, 0.85), 0.16, 1.0)
R = 0.0024                                   # wire radius (about 5 mm wire)
def rod(pts): sweep('Wire', pts, ST, r=R, smooth=False)
def ball(p): bpy.ops.mesh.primitive_uv_sphere_add(radius=0.0085, location=p, segments=32, ring_count=16); o = bpy.context.object; o.data.materials.append(ST); P.append(o)
H = 0.37
# base: a 12 x 12 cm loop, the corners rounded, and two bars across it under the frames
BX, BY, rc = 0.062, 0.058, 0.010
loop = []
for cx, cy, a0 in ((BX - rc, BY - rc, 0), (-BX + rc, BY - rc, 90), (-BX + rc, -BY + rc, 180), (BX - rc, -BY + rc, 270)):
    for k in range(7):
        a = math.radians(a0 + 90 * k / 6); loop.append((cx + rc * math.cos(a), cy + rc * math.sin(a), R))
sweep('Base', loop, ST, r=R, smooth=False, closed=True)
for y in (-0.014, 0.014): rod([(-BX + 0.004, y, R * 2.6), (BX - 0.004, y, R * 2.6)])
# two inverted-U frames: front (y -0.014) to the left, back (y +0.014) to the right
FR = [(-0.034, 0.012, -0.014), (-0.012, 0.034, 0.014)]
for x0, x1, y in FR:
    r2 = 0.008; top = H - R
    pts = [(x0, y, R * 3.5), (x0, y, top - r2)]
    for k in range(1, 6): a = math.radians(180 - 90 * k / 6); pts.append((x0 + r2 + r2 * math.cos(a), y, top - r2 + r2 * math.sin(a)))
    pts += [(x0 + r2, y, top), (x1 - r2, y, top)]
    for k in range(1, 6): a = math.radians(90 - 90 * k / 6); pts.append((x1 - r2 + r2 * math.cos(a), y, top - r2 + r2 * math.sin(a)))
    pts += [(x1, y, top - r2), (x1, y, R * 3.5)]
    rod(pts)
# the hooks: per tier a V on the front frame's left leg and one on the back frame's right leg, turned opposite ways
ARM = 0.095
for zv in (0.085, 0.195, 0.305):
    for (lx, ly, turn) in ((FR[0][0], FR[0][2], 1), (FR[1][1], FR[1][2], -1)):
        v = Vector((lx, ly, zv))
        for side in (-1, 1):
            ang = math.radians(62 * turn) + (0 if side < 0 else math.pi)
            d = Vector((math.cos(ang), math.sin(ang), 0)) * math.cos(math.radians(52)) + Vector((0, 0, math.sin(math.radians(52))))
            tip = v + d * ARM
            rod([tuple(v), tuple(tip)]); ball(tuple(tip + d * 0.006))
finish('cup_rack', 'NH10 Stainless Steel Cup Rack', view=(0.55, -1, 0.35))
print('DONE')
