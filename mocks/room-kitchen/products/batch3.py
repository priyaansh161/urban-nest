# HomeWiz garlic press (b46a7d38, 16 x 4 cm), Nestasia coconut opener (b4867f61, 17 x 10 cm), HOMEZE silicone sink mat
# (1b0130dd, 30 x 10 x 2 cm), from their listing photos.   blender -b -P batch3.py -- <outdir> [garlic_press|coconut_opener|sink_mat]
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from klib import *
args = sys.argv[sys.argv.index('--') + 1:]
WHICH = args[1].split(',') if len(args) > 1 else ['garlic_press', 'coconut_opener', 'sink_mat']
CHROME = lambda: pmat('Polished Steel', (0.88, 0.88, 0.87), 0.09, 1.0)

def oval(a, b, n=2.3): return superellipse(a, b, n, 48)

def garlic_press():
    # 16 x 4 cm: a short chamber with a rolled lip at the left, the pivot above its left edge; the lever and the lower handle are
    # flat bars on edge (tall, thin), waved like the photo and curling up at the tips; holes in the chamber floor.
    reset(); S = CHROME()
    lathe('Chamber', [(0, 0.0035), (0.0132, 0.0035), (0.0140, 0.0040), (0.0160, 0.0255), (0.0178, 0.0270), (0.0184, 0.0282), (0.0176, 0.0291),
                      (0.0168, 0.0287), (0.0150, 0.0050), (0.0146, 0.0012), (0.0132, 0.0), (0, 0.0)], [S], seg=160, closed=True)
    DK = pmat('Hole', (0.02, 0.02, 0.02), 0.6)
    for i in range(-5, 6):
        for j in range(-5, 6):
            x, y = i * 0.0024, j * 0.0024 + (0.0012 if i % 2 else 0)
            if x * x + y * y < 0.0125 ** 2: cyl(0.00065, 0.0004, (x, y, -0.00005), DK, v=12)
    ED = 0.0042
    def bar(name, pts, h0, h1, tip):
        def sc(t):                                       # cast look: deep near the pivot, waisted, swelling into a flat tip
            h = h0 * (1 - t) ** 1.6 + h1 + 0.0022 * math.exp(-((t - 0.88) / 0.08) ** 2)
            return (h, ED * (0.85 + 0.45 * t))
        sweep(name, pts, S, profile=superellipse(1.0, 1.0, 2.2, 64), twist_up=(0, 0, 1), n=20, scale_fn=sc)
    for y in (-0.0098, 0.0098):
        slab('Lug', rrect(0.014, 0.0026, 0.0010, 4), 0.020, 0.040, S, bevel=0.0005).location = (-0.0200, y, 0)
        cyl(0.0042, 0.0016, (-0.0240, y + (0.0021 if y > 0 else -0.0021), 0.0350), S, rot=(math.pi / 2, 0, 0), v=48, bev=0.0005)
    cyl(0.0022, 0.024, (-0.0240, 0, 0.0350), S, rot=(math.pi / 2, 0, 0), v=32)
    cyl(0.0135, 0.0050, (0, 0, 0.0300), S, v=96, bev=0.0010)
    bar('Lever', [(-0.026, 0, 0.0350), (-0.010, 0, 0.0365), (0.010, 0, 0.0350), (0.035, 0, 0.0320), (0.060, 0, 0.0330), (0.090, 0, 0.0370),
                  (0.118, 0, 0.0395), (0.138, 0, 0.0420), (0.150, 0, 0.0452), (0.157, 0, 0.0485)], 0.0085, 0.0028, 1)
    bar('Handle', [(0.0160, 0, 0.0240), (0.035, 0, 0.0225), (0.060, 0, 0.0170), (0.085, 0, 0.0130), (0.110, 0, 0.0125), (0.132, 0, 0.0145),
                   (0.150, 0, 0.0185), (0.158, 0, 0.0225)], 0.0075, 0.0026, 1)
    finish('garlic_press', 'HomeWiz Steel Garlic Crusher', view=(0.15, -1, 0.35))

def coconut_opener():
    # lying flat: the T-bar with black rubber grips, a round neck, then the long spear blade, dished down the middle with a spine
    reset(); S = CHROME(); RUB = pmat('Black Rubber Grip', (0.03, 0.03, 0.03), 0.6)
    ZC = 0.0072
    cyl(0.0050, 0.066, (0, 0, ZC), S, rot=(math.pi / 2, 0, 0), v=64)
    for y in (-0.039, 0.039):
        lathe('Grip', [(0, -0.009), (0.0062, -0.009), (0.0071, -0.0075), (0.0072, 0.0075), (0.0062, 0.0092), (0.0030, 0.0098), (0, 0.0098)], [RUB], seg=64)
        g = P[-1]; g.matrix_world = Matrix.Translation((0, y, ZC)) @ Matrix.Rotation(math.pi / 2 if y > 0 else -math.pi / 2, 4, 'X')
    sweep('Neck', [(0.0, 0, ZC), (0.012, 0, ZC), (0.026, 0, ZC)], S, r=0.0042, n=6)
    lathe('Collar', [(0, 0.0), (0.0052, 0.0), (0.0056, 0.003), (0.0050, 0.006), (0, 0.006)], [S], seg=48)
    c = P[-1]; c.matrix_world = Matrix.Translation((0.024, 0, ZC)) @ Matrix.Rotation(math.pi / 2, 4, 'Y')
    X0, X1 = 0.026, 0.168
    def w(x):
        t = (x - X0) / (X1 - X0)
        return 0.0045 + 0.0080 * math.sin(min(t / 0.28, 1) * math.pi / 2) if t < 0.28 else 0.0125 * (1 - (t - 0.28) / 0.72) ** 0.9 + 0.0002
    def z(x, y):
        v = abs(y) / max(w(x), 1e-5)
        return ZC - 0.0006 + 0.0040 * v * v - 0.0008 * math.exp(-(y / 0.0012) ** 2) * (1 if x > 0.04 else 0)
    shell('Blade', list(np.linspace(X0, X1, 260)), w, z, 0.0011, S, nv=48)
    text_mesh('NESTASIA', 0.0032, pmat('Etch', (0.45, 0.45, 0.45), 0.5, 0.8), Matrix.Translation((0.060, 0, ZC + 0.0004)), ext=0.00002)
    finish('coconut_opener', 'Nestasia Stainless Steel Coconut Opener', view=(0.3, -1, 0.9))

def sink_mat():
    # a grey silicone tray: rounded rim, chevron drain ridges, a pour spout in the front edge, satin silicone
    reset(); G = pmat('Grey Silicone', (0.36, 0.37, 0.39), 0.6)
    b = slab('Tray', rrect(0.300, 0.100, 0.018, 12), 0, 0.016, G, bevel=0.003, bseg=4)
    cut(b, slab('cut', rrect(0.288, 0.088, 0.013, 12), 0.0040, 0.05, None, bevel=0, keep=False))
    sp = cutter_box((-0.105, -0.047, 0.0145), (0.032, 0.020, 0.012)); cut(b, sp)
    lip = slab('Spout', rrect(0.032, 0.016, 0.006, 8), 0.0, 0.0045, G, bevel=0.0012); lip.location = (-0.105, -0.056, 0)
    ang = math.radians(35); L2 = 0.016
    for i in range(-4, 5):
        for s_, yc in ((1, 0.019), (-1, -0.019)):
            x0 = i * 0.030 + (0.015 if s_ < 0 else 0)
            if abs(x0) > 0.125: continue
            d = Vector((math.cos(ang), s_ * math.sin(ang), 0)) * L2
            p = [(x0 - d.x, yc - d.y, 0.0050), (x0 + d.x, yc + d.y, 0.0050)]
            sweep('Ridge', p, G, profile=superellipse(0.0016, 0.0013, 2.4, 24), twist_up=(0, 0, 1), smooth=False, n=1)
            for e_ in (p[0], p[1]):
                bpy.ops.mesh.primitive_uv_sphere_add(radius=1, segments=16, ring_count=8, location=e_); c = bpy.context.object
                c.scale = (0.0013, 0.0013, 0.0016); c.data.materials.append(G); P.append(c)
    finish('sink_mat', 'HOMEZE Silicone Sink Drainer Mat', view=(0.3, -1, 0.9))

for k in WHICH: globals()[k]()
print('DONE')
