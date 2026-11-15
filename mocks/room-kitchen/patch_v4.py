# v4 changes to build_kitchen_v1.py (his review #2, 15 Nov): the open drawer shows a real dark cavity behind it, the sink is
# an open bowl (walls + floor, the boolean bowl came out solid), the apron's hook goes with the apron, the spatula lies in
# the Primeway's dish, fuller window plants, and a false ceiling (dropped band, cove glow, downlights in the band).
p = 'build_kitchen_v1.py'; s = open(p, encoding='utf8').read()
def R(a, b):
    global s
    if a not in s: raise SystemExit('missing: ' + a[:90])
    s = s.replace(a, b)

# ---- the open drawer's cavity: cut the carcass as well as the front, line the hole in near-black
R("base.append(bx('Drawer Cavity', RX + 0.019, RX + 0.021, DR['y0'], DR['y1'], DR['z0'], DR['z1'], M['gap']))", "")
R("""    if f_.name.startswith('Front') and abs(f_.location.x - (RX + 0.01)) < 0.02 and f_.dimensions.y > 3.0:   # cut the open drawer's mouth in the right-run front
        cut(f_, box('cut', (RX + 0.01, (DR['y0'] + DR['y1']) / 2, (DR['z0'] + DR['z1']) / 2), (0.06, DR['y1'] - DR['y0'], DR['z1'] - DR['z0']), M['gap']))""",
"""    if f_.name.startswith(('Front', 'Carcass')) and f_.dimensions.y > 3.0 and f_.location.x > RX - 0.05:   # the right run: open the drawer's mouth and the space behind it
        cut(f_, box('cut', (RX + 0.27, (DR['y0'] + DR['y1']) / 2, (DR['z0'] + DR['z1']) / 2), (0.56, DR['y1'] - DR['y0'], DR['z1'] - DR['z0']), M['gap']))
M['cavity'] = mat('Cabinet Cavity', (0.025, 0.025, 0.03, 1), 0.8)
base += [bx('Cavity Top', RX + 0.02, RX + 0.55, DR['y0'], DR['y1'], DR['z1'], DR['z1'] + 0.006, M['cavity']),
         bx('Cavity Back', RX + 0.54, RX + 0.55, DR['y0'], DR['y1'], DR['z0'], DR['z1'], M['cavity']),
         bx('Cavity Side', RX + 0.02, RX + 0.55, DR['y0'] - 0.006, DR['y0'], DR['z0'], DR['z1'], M['cavity']),
         bx('Cavity Side', RX + 0.02, RX + 0.55, DR['y1'], DR['y1'] + 0.006, DR['z0'], DR['z1'], M['cavity']),
         bx('Cavity Floor', RX + 0.02, RX + 0.55, DR['y0'], DR['y1'], DR['z0'] - 0.006, DR['z0'], M['cavity'])]""")

# ---- the sink: an open bowl built from its walls and floor
R("""bowl = box('Sink Bowl', (SINK[0], SINK[1], (SZ + 0.862) / 2 - 0.006), (SINK[2] + 0.02, SINK[3] + 0.02, 0.862 - SZ + 0.012), M['sinksteel'], 0.03, segs=6)
inner = box('cut', (SINK[0], SINK[1], (SZ + 0.95) / 2), (SINK[2], SINK[3], 0.95 - SZ), M['sinksteel'], 0.025, segs=6); cut(bowl, inner)
sk.append(bowl)""",
"""M['sinkfloor'] = mat('Sink Floor Steel', (0.20, 0.205, 0.22, 1), 0.4)
T_ = 0.008
sk += [bx('Sink Floor', SX0, SX1, SY0, SY1, SZ - T_, SZ, M['sinkfloor'], 0.002),
       bx('Sink Wall L', SX0 - T_, SX0, SY0 - T_, SY1 + T_, SZ - T_, 0.875, M['sinksteel']), bx('Sink Wall R', SX1, SX1 + T_, SY0 - T_, SY1 + T_, SZ - T_, 0.875, M['sinksteel']),
       bx('Sink Wall F', SX0, SX1, SY0 - T_, SY0, SZ - T_, 0.875, M['sinksteel']), bx('Sink Wall B', SX0, SX1, SY1, SY1 + T_, SZ - T_, 0.875, M['sinksteel'])]
for (xa, ya) in ((SX0, SY0), (SX1, SY0), (SX0, SY1), (SX1, SY1)):          # soft inside corners
    sk.append(cyl('Sink Corner', (xa, ya, (SZ + 0.875) / 2), 0.012, 0.875 - SZ, M['sinksteel'], seg=16))""")

# ---- the apron and its hook go
R("STAGE.extend(hk)", "# (the apron left the room, 15 Nov: its hook goes too)")

# ---- the spatula: blade in the Primeway's dish (the dish is its +x end), handle resting on the hook tab, toward the aisle
R("M['neem'] = SL.mat('Neem Wood', (0.62, 0.42, 0.24), 0.55)", "M['neem'] = SL.mat('Neem Wood', (0.42, 0.26, 0.13), 0.5)")
R("spatula(1.02, -0.10, CT + 0.022, math.radians(-82))", "spatula(1.075, -0.07, CT + 0.016, math.pi, tilt=0.17)")

# ---- window plants: a tulsi bush and a snake plant, in proper terracotta pots with soil
R("pot_plant(WX0 + 0.15, Y1 + 0.05, WZ0, 0.20, 1); pot_plant(WX1 - 0.18, Y1 + 0.05, WZ0, 0.26, 2)", '''M['soil'] = mat('Potting Soil', (0.10, 0.07, 0.05, 1), 0.95)
_lv = np.mgrid[0:128, 0:64][0] / 128.0
M['tulsi'] = SL.mat('Tulsi Leaf', (0.16, 0.36, 0.10), 0.45, image=SL.img('tulsi_col', np.clip(np.array([0.13, 0.33, 0.08]) * (0.8 + 0.35 * _lv)[..., None] * (1 - 0.25 * (np.abs(np.mgrid[0:128, 0:64][1] / 64.0 - 0.5) < 0.03))[..., None], 0, 1), TMP))
_band = 0.5 + 0.5 * np.sin(np.mgrid[0:256, 0:64][0] / 256.0 * 60 + 2 * np.sin(np.mgrid[0:256, 0:64][1] / 64.0 * 6))
_edge = (np.abs(np.mgrid[0:256, 0:64][1] / 64.0 - 0.5) > 0.44)
M['snake'] = SL.mat('Snake Plant Leaf', (0.12, 0.30, 0.10), 0.4, image=SL.img('snake_col', np.clip(np.where(_edge[..., None], np.array([0.62, 0.62, 0.22]), np.array([0.07, 0.22, 0.08]) + np.array([0.10, 0.16, 0.08]) * _band[..., None]), 0, 1), TMP))
def pot(x, y, z, r=0.055, h=0.10):
    lathe('Pot', [(0, 0), (r * 0.72, 0), (r * 0.95, h * 0.85), (r * 1.08, h * 0.86), (r * 1.10, h), (r * 0.92, h), (r * 0.92, h * 0.9), (0, h * 0.9)], M['terracotta'], (x, y, z), seg=48)
    lathe('Soil', [(0, h * 0.86), (r * 0.9, h * 0.86), (0, h * 0.88)], M['soil'], (x, y, z), seg=32)
def leaf_quad(V, F, UV, base, d, side, L, W, curl=0.0, n=8):
    """An oval leaf from base along d, width across side, cupped by curl."""
    k0 = len(V)
    for i in range(n + 1):
        t = i / n; w = W * math.sin(math.pi * min(t * 1.05, 1.0)) ** 0.8
        c = base + d * (L * t) - Vector((0, 0, 1)) * (0.25 * L * t * t)
        for sgn in (-1, 0, 1):
            V.append(tuple(c + side * (sgn * w / 2) + Vector((0, 0, 1)) * (curl * w * (1 - abs(sgn))))); UV.append(((sgn + 1) / 2, t))
    for i in range(n):
        for j in range(2):
            a = k0 + i * 3 + j; F.append((a, a + 1, a + 4, a + 3))
def tulsi(x, y, z, seed=3):
    pot(x, y, z); r = np.random.default_rng(seed); V, F, UV = [], [], []; stems = []
    for k in range(7):
        a = r.uniform(0, 2 * math.pi); lean = r.uniform(0.15, 0.45); h = r.uniform(0.12, 0.20)
        top = Vector((x + lean * h * math.cos(a), y + lean * h * math.sin(a), z + 0.09 + h)); bot = Vector((x, y, z + 0.09))
        stems.append(SL.tube('Tulsi Stem', [bot, (bot + top) / 2 + Vector((0, 0, 0.01)), top], [0.0025, 0.002, 0.0015], M['tulsi'], seg=6))
        for j in range(9):
            t = 0.25 + 0.75 * j / 8; c = bot.lerp(top, t)
            for sgn in (-1, 1):
                b_ = a + sgn * math.pi / 2 + j * 0.9; d = Vector((math.cos(b_), math.sin(b_), 0.45)).normalized()
                leaf_quad(V, F, UV, c, d, Vector((-d.y, d.x, 0)).normalized(), 0.028 * (1.2 - 0.5 * t), 0.018 * (1.2 - 0.5 * t), curl=0.25)
    STAGE.append(SL.mesh_obj('Tulsi', V, F, M['tulsi'], UV)); STAGE.extend(stems)
def snake_plant(x, y, z, seed=5):
    pot(x, y, z, r=0.06, h=0.11); r = np.random.default_rng(seed); V, F, UV = [], [], []
    for k in range(9):
        a = r.uniform(0, 2 * math.pi); off = r.uniform(0.0, 0.03); base = Vector((x + off * math.cos(a), y + off * math.sin(a), z + 0.10))
        L = r.uniform(0.20, 0.34); lean = r.uniform(0.05, 0.25); d = Vector((lean * math.cos(a), lean * math.sin(a), 1)).normalized()
        side = Vector((-math.sin(a + 0.6), math.cos(a + 0.6), 0)); n = 10; k0 = len(V)
        for i in range(n + 1):
            t = i / n; w = 0.034 * (1 - t ** 3) + 0.002; c = base + d * (L * t)
            for sgn in (-1, 0, 1): V.append(tuple(c + side * (sgn * w / 2) + Vector((0, 0, 0)) - (Vector((-side.y, side.x, 0)) * 0.006 * (1 - abs(sgn))))); UV.append(((sgn + 1) / 2, t))
        for i in range(n):
            for j in range(2):
                q = k0 + i * 3 + j; F.append((q, q + 1, q + 4, q + 3))
    STAGE.append(SL.mesh_obj('Snake Plant', V, F, M['snake'], UV))
tulsi(WX0 + 0.16, Y1 + 0.05, WZ0); snake_plant(WX1 - 0.17, Y1 + 0.05, WZ0)''')

# ---- false ceiling: a 15 cm gypsum band all round, a raised centre over the aisle with a warm cove glow, downlights in the band
R("DL = [(-0.30, -0.95), (-0.30, 0.45), (0.45, -0.95), (0.45, 0.45), (0.10, 1.25)]",
"""FC = dict(x0=-0.50, x1=0.62, y0=-1.15, y1=0.82, drop=0.15)       # the raised centre (over the aisle)
M['gypsum'] = mat('Gypsum White', (0.94, 0.93, 0.90, 1), 0.85)
fz = H - FC['drop']
fc = [bx('FC Band', X0, FC['x0'], Y0, Y1, fz, H, M['gypsum']), bx('FC Band', FC['x1'], X1, Y0, Y1, fz, H, M['gypsum']),
      bx('FC Band', FC['x0'], FC['x1'], Y0, FC['y0'], fz, H, M['gypsum']), bx('FC Band', FC['x0'], FC['x1'], FC['y1'], Y1, fz, H, M['gypsum'])]
fc += [bx('FC Lip', FC['x0'], FC['x0'] + 0.06, FC['y0'], FC['y1'], fz - 0.04, fz, M['gypsum']), bx('FC Lip', FC['x1'] - 0.06, FC['x1'], FC['y0'], FC['y1'], fz - 0.04, fz, M['gypsum']),
       bx('FC Lip', FC['x0'] + 0.06, FC['x1'] - 0.06, FC['y0'], FC['y0'] + 0.06, fz - 0.04, fz, M['gypsum']), bx('FC Lip', FC['x0'] + 0.06, FC['x1'] - 0.06, FC['y1'] - 0.06, FC['y1'], fz - 0.04, fz, M['gypsum'])]
falsec = join(fc, 'LM_FalseCeiling'); world_uv(falsec, 3.0); lm(falsec, 2048)
M['cove'] = mat('Cove Glow', (1, .88, .7, 1), 0.5, 0.0, emit=((1, .80, .55, 1), 3.0))
CG = [bx('Cove Glow', FC['x0'] + 0.08, FC['x0'] + 0.10, FC['y0'] + 0.1, FC['y1'] - 0.1, H - 0.012, H - 0.004, M['cove']),
      bx('Cove Glow', FC['x1'] - 0.10, FC['x1'] - 0.08, FC['y0'] + 0.1, FC['y1'] - 0.1, H - 0.012, H - 0.004, M['cove']),
      bx('Cove Glow', FC['x0'] + 0.1, FC['x1'] - 0.1, FC['y0'] + 0.08, FC['y0'] + 0.10, H - 0.012, H - 0.004, M['cove']),
      bx('Cove Glow', FC['x0'] + 0.1, FC['x1'] - 0.1, FC['y1'] - 0.10, FC['y1'] - 0.08, H - 0.012, H - 0.004, M['cove'])]
DLZ = fz                                                            # downlights sit in the band's underside
DL = [(0.80, -0.95), (0.80, -0.20), (0.80, 0.55), (-0.25, 1.02), (0.40, 1.02), (-0.68, -1.30), (-0.68, 0.40)]""")
R("    cyl('DLTrim%d' % i_, (x_, y_, H - 0.004), 0.06, 0.008, M['dltrim']); cyl('DLLens%d' % i_, (x_, y_, H - 0.009), 0.042, 0.006, M['dl'])",
  "    cyl('DLTrim%d' % i_, (x_, y_, DLZ - 0.004), 0.05, 0.008, M['dltrim']); cyl('DLLens%d' % i_, (x_, y_, DLZ - 0.009), 0.035, 0.006, M['dl'])")
R("for i_, (x_, y_) in enumerate(DL): spot('DL%d' % i_, (x_, y_, H - 0.02), (x_, y_, 0.0), 28, 85, 0.8)",
  """for i_, (x_, y_) in enumerate(DL): spot('DL%d' % i_, (x_, y_, DLZ - 0.02), (x_, y_, 0.0), 24, 80, 0.8)
for nm_, loc_, rot_, sx_, sy_ in (('Cove L', (FC['x0'] + 0.09, (FC['y0'] + FC['y1']) / 2, H - 0.02), (0, math.radians(-40), 0), 0.08, FC['y1'] - FC['y0'] - 0.2),
                                  ('Cove R', (FC['x1'] - 0.09, (FC['y0'] + FC['y1']) / 2, H - 0.02), (0, math.radians(40), 0), 0.08, FC['y1'] - FC['y0'] - 0.2),
                                  ('Cove F', ((FC['x0'] + FC['x1']) / 2, FC['y0'] + 0.09, H - 0.02), (math.radians(40), 0, 0), FC['x1'] - FC['x0'] - 0.2, 0.08),
                                  ('Cove B', ((FC['x0'] + FC['x1']) / 2, FC['y1'] - 0.09, H - 0.02), (math.radians(-40), 0, 0), FC['x1'] - FC['x0'] - 0.2, 0.08)):
    area(nm_, loc_, sx_, sy_, 18, (1.0, 0.82, 0.58), rot=rot_)""")
R("hide = [o for o, _, _ in SHELL if 'Ceiling' in o.name]", "hide = [o for o, _, _ in SHELL if 'Ceiling' in o.name] + [o for o in bpy.data.objects if o.name.startswith(('LM_FalseCeiling', 'Cove Glow'))]")
open(p, 'w', encoding='utf8').write(s); print('patched v4')
