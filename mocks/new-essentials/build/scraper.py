# "Clazkit Stainless Steel Scraper | Dough Cutter" (a81fa1ef), from its listing photos: a D-shaped brushed-steel blade
# (14 cm along the straight cutting edge, 11 cm tall, the top a wide arc), a soft black rubber grip wrapped over the
# middle of the arc, and the print in grey: an inch ruler (0-5, ticks every 1/8) along the edge, the cup/floz/tbsp/ml
# table above it and the CLazkit name under the grip. Standing on its edge, as in the photos.
#   blender -b -P scraper.py -- <outdir>
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'room-kitchen', 'products'))
from klib import *

reset()
ST = pmat('Satin Stainless', (0.86, 0.86, 0.85), 0.36, 1.0)       # the photo's blade is soft satin, the brushing barely shows
RB = pmat('Black Rubber Grip', (0.035, 0.035, 0.037), 0.62)
INK = pmat('Etched Print', (0.30, 0.30, 0.31), 0.5, 0.4)
W, H, T = 0.140, 0.110, 0.0010
# blade outline in the x-z plane: straight bottom edge, short straight sides, an arc over the top
pts = [(-W / 2, 0.0), (W / 2, 0.0), (W / 2, 0.035)]
R_ = (W / 2) ** 2 / (2 * (H - 0.035)) + (H - 0.035) / 2           # arc through both side tops and the crown
cz = H - R_
a0 = math.atan2(0.035 - cz, W / 2)
for k in range(1, 48): a = a0 + (math.pi - 2 * a0) * k / 48; pts.append((R_ * math.cos(a), cz + R_ * math.sin(a)))
pts.append((-W / 2, 0.035))
b = slab('Blade', pts, -T / 2, T / 2, ST, bevel=0.0003, bseg=1); b.rotation_euler = (math.pi / 2, 0, 0)
bpy.context.view_layer.update(); planar_uv(b, 0.15, 0.15, axes='xz')
# grip: a rubber bar swept along the arc between about 30 and 70 percent of the width, squashed over the edge
arc = []
for k in range(25):
    x = -0.040 + 0.080 * k / 24; z = cz + math.sqrt(max(R_ ** 2 - x * x, 0)) - 0.004; arc.append((x, 0, z))
sweep('Grip', arc, RB, profile=superellipse(0.0105, 0.0085, 2.4, 40), twist_up=(0, 1, 0), n=24,
      scale_fn=lambda t: (0.25 + 0.75 * math.sin(math.pi * t) ** 0.3, 0.30 + 0.70 * math.sin(math.pi * t) ** 0.3))   # rounded off at both ends
# print on the face toward -y
def ink(txt, size, x, z): text_mesh(txt, size, INK, Matrix.Translation((x, -T / 2 - 0.00006, z)) @ Matrix.Rotation(math.pi / 2, 4, 'X'), ext=0.00004)
IN = 0.0254
x0 = -2.5 * IN
for k in range(41):                                                     # ruler: 1/8 inch ticks, numbers on the inches
    L = 0.012 if k % 8 == 0 else (0.008 if k % 4 == 0 else 0.0045)
    o = slab('Tick', [(-0.00025, 0), (0.00025, 0), (0.00025, L), (-0.00025, L)], 0, 0.00004, INK)
    o.rotation_euler = (math.pi / 2, 0, 0); o.location = (x0 + k * IN / 8, -T / 2 - 0.00002, 0.004)
    if k % 8 == 0: ink(str(k // 8), 0.0045, x0 + k * IN / 8, 0.020)
o = slab('Rule', [(x0, 0), (x0 + 5 * IN, 0), (x0 + 5 * IN, 0.0004), (x0, 0.0004)], 0, 0.00004, INK); o.rotation_euler = (math.pi / 2, 0, 0); o.location = (0, -T / 2 - 0.00002, 0.0155)
rows = [('Measure        Equivalent', 0.067), ('cup  =  floz  =  tbsp  =   ml', 0.060), ('1        8        16       237', 0.053),
        ('1/2      4         8       118', 0.045), ('1/4     2.7    5+1tsp   79', 0.037), ('1/5      2         4        59', 0.029)]
for t, z in rows: ink(t, 0.0040, 0.006, z)
for z in (0.049, 0.041, 0.033):
    o = slab('Line', [(-0.018, 0), (0.030, 0), (0.030, 0.0003), (-0.018, 0.0003)], 0, 0.00004, INK); o.rotation_euler = (math.pi / 2, 0, 0); o.location = (0, -T / 2 - 0.00002, z)
ink('CLazkit', 0.0065, 0.0, 0.080)
finish('scraper', 'Clazkit Stainless Steel Dough Scraper', view=(0.25, -1, 0.25))
print('DONE')
