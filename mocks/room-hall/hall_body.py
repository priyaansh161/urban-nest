# ================================================================ THE HALL (living + dining), see LAYOUT.md
# (assembled into build_hall_v1.py by assemble.py: the kitchen's helpers above, this body, the bake/export tail below)

def tile_image():
    """One 80 cm warm-ivory vitrified tile: soft clouding and faint drifting veins (no grout: that is geometry)."""
    S = 1024; c1 = noise(S, S, 3, 40); c2 = noise(S, S, 4, 10); c3 = noise(S, S, 5, 2)
    y, x = np.mgrid[0:S, 0:S] / S
    vein = np.exp(-((np.sin((x * 1.3 + y * 0.6 + 0.25 * c1) * 9)) ** 2) / 0.004) * 0.5
    base = np.array([0.86, 0.82, 0.74])
    rgb = base[None, None, :] * (1 + 0.035 * c1[..., None] + 0.02 * c2[..., None] + 0.012 * c3[..., None]) - 0.03 * vein[..., None]
    return SL.img('tile_col', np.clip(rgb, 0, 1), TMP)

def outside_image():
    """Evening-gold daylight over Noida from a high floor: pale sky, rows of towers, a haze, no ground (we are up high)."""
    Hh, Ww = 768, 1400; v, u = np.mgrid[0:Hh, 0:Ww]; v = 1 - v / Hh; u = u / Ww
    sky = np.array([0.95, 0.88, 0.76]) * (1 - v[..., None]) * 0.6 + np.array([0.66, 0.78, 0.92]) * (0.4 + 0.6 * v[..., None])
    rgb = sky.copy(); r_ = np.random.default_rng(11)
    for k in range(16):
        cx = r_.uniform(0, 1); w_ = r_.uniform(0.03, 0.07); top = r_.uniform(0.30, 0.62); far = r_.uniform(0.35, 0.9)
        m_ = (abs(u - cx) < w_ / 2) & (v < top)
        col = np.array([0.90, 0.86, 0.80]) * (0.75 + 0.15 * r_.random())
        win = ((np.floor(v * 140) % 3) == 0) & ((np.floor((u - cx) * 600) % 4) < 2)
        t_ = np.where(win[..., None], col * 0.6, col); t_ = t_ * (1 - far * 0.55) + sky * far * 0.55
        rgb = np.where(m_[..., None], t_, rgb)
    return SL.img('outside_col', np.clip(rgb, 0, 1), TMP)

def rug_image():
    S = 1024; y, x = np.mgrid[0:S, 0:S] / S; n = noise(S, S, 21, 1); n2 = noise(S, S, 22, 30)
    base = np.array([0.80, 0.76, 0.70]) * (1 + 0.04 * n2[..., None] + 0.05 * n[..., None])
    border = (np.minimum(np.minimum(x, 1 - x), np.minimum(y, 1 - y)) < 0.05)
    line = (np.abs(np.minimum(np.minimum(x, 1 - x), np.minimum(y, 1 - y)) - 0.075) < 0.006)
    dia = (np.abs(((x * 6 + y * 6) % 1) - 0.5) < 0.02) | (np.abs(((x * 6 - y * 6) % 1) - 0.5) < 0.02)
    rgb = np.where((border | line)[..., None], np.array([0.38, 0.36, 0.33]) * (1 + 0.05 * n[..., None]), base)
    rgb = np.where((dia & ~border)[..., None], rgb * 0.9, rgb)
    return SL.img('rug_col', np.clip(rgb, 0, 1), TMP)

LAM = (0.60, 0.41, 0.23)
# v2 (19 Nov): every wood is the crisp oak_veneer_03 scan (grain turned to run along v like the old walnut), recoloured per
# finish; floor = Marble021 scan as an 80 cm marble-look vitrified tile; ceilings get a faint plaster; fabrics = linen scan.
OAKD = 'oak_veneer_03/oak_veneer_03_diff_2k.jpg'; OAKN = 'oak_veneer_03/oak_veneer_03_nor_gl_2k.jpg'; OAKR = 'oak_veneer_03/oak_veneer_03_rough_2k.jpg'
LIN = 'rough_linen/rough_linen_diff_2k.jpg'; LINN = 'rough_linen/rough_linen_nor_gl_2k.jpg'
PLD = 'beige_wall_001/beige_wall_001_diff_2k.jpg'; PLN = 'beige_wall_001/beige_wall_001_nor_gl_2k.jpg'
def wood(name, col, contrast, rough=0.45):
    return pbr(name, scan_img(OAKD, 2048, recolour=col, contrast=contrast, rot90=True), scan_img(OAKN, 1024, False, rot90=True), None, rough=rough, nstr=0.35)
M = {
    'wall': pbr('Warm White Paint', scan_img('beige_wall_001/beige_wall_001_diff_2k.jpg', 1024, recolour=(0.91, 0.88, 0.82), contrast=0.25),
                scan_img('beige_wall_001/beige_wall_001_nor_gl_2k.jpg', 1024, False), None, rough=0.85, nstr=0.4),
    'accent': pbr('Sage Accent Paint', scan_img('beige_wall_001/beige_wall_001_diff_2k.jpg', 1024, recolour=(0.62, 0.66, 0.58), contrast=0.25),
                  scan_img('beige_wall_001/beige_wall_001_nor_gl_2k.jpg', 1024, False), None, rough=0.85, nstr=0.4),
    'ceiling': pbr('Ceiling Plaster', scan_img(PLD, 1024, recolour=(0.93, 0.92, 0.89), contrast=0.12), scan_img(PLN, 1024, False), None, rough=0.9, nstr=0.15),
    'tile': pbr('Ivory Marble Vitrified Tile', scan_img('Marble021/Marble021_2K-JPG_Color.jpg', 2048, recolour=(0.90, 0.87, 0.81), contrast=1.1),
                scan_img('Marble021/Marble021_2K-JPG_NormalGL.jpg', 1024, False), None, rough=0.1, nstr=0.12),
    'grout': mat('Grout', (0.68, 0.63, 0.55, 1), 0.7),
    'marble': pbr('Grey Marble', scan_img('Marble019/Marble019_2K-JPG_Color.jpg', 2048, recolour=(0.80, 0.78, 0.76), contrast=1.6),
                  scan_img('Marble019/Marble019_2K-JPG_NormalGL.jpg', 1024, False), None, rough=0.15, nstr=0.3),
    'whitemarble': pbr('White Marble', scan_img('Marble019/Marble019_2K-JPG_Color.jpg', 1024, tint=(1.04, 1.03, 1.02)), None, None, rough=0.15),
    'quartz': pbr('White Quartz', scan_img('Marble019/Marble019_2K-JPG_Color.jpg', 1024, tint=(1.03, 1.02, 1.0), contrast=0.55), None, None, rough=0.18),
    'oak': wood('Oak Laminate', (0.64, 0.45, 0.28), 1.35),
    'teak': wood('Teak Veneer', (0.42, 0.25, 0.12), 1.3, 0.4),
    'walnut': wood('Walnut Table', (0.32, 0.19, 0.10), 1.25, 0.35),
    'navy': mat('Charcoal Navy Matte', (0.020, 0.027, 0.048, 1), 0.55),
    'gap': mat('Shutter Gap', (0.02, 0.02, 0.025, 1), 0.8),
    'gypsum': pbr('Gypsum White', scan_img(PLD, 1024, recolour=(0.94, 0.93, 0.90), contrast=0.1), scan_img(PLN, 1024, False), None, rough=0.85, nstr=0.12),
    'alu': mat('Dark Grey Aluminium', (0.10, 0.10, 0.11, 1), 0.4),
    'glass': mat('Glass', (0.85, 0.90, 0.92, 1), 0.02, alpha=0.08),
    'bronzeglass': mat('Bronze Glass', (0.20, 0.15, 0.10, 1), 0.05, alpha=0.45),
    'mirror': mat('Mirror', (0.70, 0.72, 0.74, 1), 0.03, 1.0),
    'matblack': mat('Matte Black', (0.02, 0.02, 0.022, 1), 0.45),
    'tvblack': mat('TV Screen', (0.008, 0.009, 0.011, 1), 0.08),
    'brass': mat('Brass (lightmapped look)', (0.70, 0.50, 0.22, 1), 0.35),
    'steel': mat('Steel (painted)', (0.40, 0.41, 0.43, 1), 0.32),
    'white': mat('Matte White', (0.92, 0.92, 0.90, 1), 0.5),
    'fabric': pbr('Linen Upholstery', scan_img(LIN, 1024, recolour=(0.86, 0.82, 0.74), contrast=1.2), scan_img(LINN, 1024, False), None, rough=0.9, nstr=0.8),
    'cushion': SL.mat('Rust Cushion', (0.62, 0.30, 0.16), 0.9, sheen=0.4),
    'drape': pbr('Taupe Linen Drape', scan_img(LIN, 1024, recolour=(0.60, 0.53, 0.44), contrast=1.3), scan_img(LINN, 1024, False), None, rough=0.92, nstr=0.9),
    'runner': pbr('Linen Runner', scan_img(LIN, 1024, recolour=(0.80, 0.74, 0.64), contrast=1.2), scan_img(LINN, 1024, False), None, rough=0.9, nstr=0.8),
    'marigold': mat('Marigold', (0.95, 0.42, 0.04, 1), 0.7),
    'mango': mat('Mango Leaf', (0.10, 0.30, 0.06, 1), 0.5),
    'book1': mat('Book Cloth Sage', (0.42, 0.47, 0.38, 1), 0.8), 'book2': mat('Book Cloth Ochre', (0.70, 0.52, 0.24, 1), 0.8),
    'pages': mat('Book Pages', (0.92, 0.89, 0.82, 1), 0.9),
    'sheer': SL.mat('Sheer', (0.95, 0.94, 0.90), 0.9, alpha_blend=True),
    'rug': SL.mat('Living Rug', (0.80, 0.76, 0.70), 0.95, image=rug_image()),
    'coir': mat('Coir Mat', (0.45, 0.32, 0.18, 1), 0.95),
    'leaf': mat('Leaf', (0.13, 0.32, 0.09, 1), 0.5),
    'terracotta': mat('Terracotta', (0.58, 0.30, 0.18, 1), 0.8),
    'planter': mat('Charcoal Planter', (0.12, 0.12, 0.12, 1), 0.6),
    'soil': mat('Potting Soil', (0.10, 0.07, 0.05, 1), 0.95),
    'cove': mat('Cove Glow', (1, .88, .7, 1), 0.5, 0.0, emit=((1, .80, .55, 1), 3.0)),
    'led': mat('LED Strip', (1, 0.9, 0.75, 1), 0.5, emit=((1.0, 0.85, 0.62, 1), 6.0)),
    'dl': mat('Downlight Lens', (0.02, 0.02, 0.02, 1), 0.3, emit=((1.0, 0.86, 0.66, 1), 10.0)),
    'dltrim': mat('Downlight Trim', (0.92, 0.92, 0.90, 1), 0.4),
    'switch': mat('Switch Plate', (0.95, 0.95, 0.94, 1), 0.3),
    'crockery': mat('White Crockery', (0.95, 0.95, 0.93, 1), 0.15),
    'diya': mat('Diya Flame', (1, 0.7, 0.3, 1), 0.5, emit=((1.0, 0.65, 0.25, 1), 8.0)),
}
OUTSIDE = SL.mat('Outside Day', (0.8, 0.85, 0.9), 1.0, image=outside_image())
_ob = OUTSIDE.node_tree.nodes['Principled BSDF']
for nd in list(OUTSIDE.node_tree.nodes):
    if nd.type == 'TEX_IMAGE': OUTSIDE.node_tree.links.new(nd.outputs['Color'], _ob.inputs['Emission Color'])
_ob.inputs['Emission Strength'].default_value = 1.4; _ob.inputs['Base Color'].default_value = (0, 0, 0, 1)

LMX, LMRES = [], {}
def lm(o, res=1024): LMX.append(o); LMRES[o.name] = res; return o

# ---------------------------------------------------------------- shell
NC = lambda l: max(1, round(l / STEP))
DUW = (X1 - X0) / NC(X1 - X0); DUD = (Y1 - Y0) / NC(Y1 - Y0); DZ = H / NC(H)
def hx(a, b, z1): return (round((a - X0) / DUW), round((b - X0) / DUW), 0, round(z1 / DZ))      # a hole in a wall that runs along x
def hy(a, b, z1): return (round((a - Y0) / DUD), round((b - Y0) / DUD), 0, round(z1 / DZ))      # ... along y
BAL = hx(-1.25, 1.25, 2.45); BX0, BX1, BZ1 = X0 + BAL[0] * DUW, X0 + BAL[1] * DUW, BAL[3] * DZ
KIT = hy(2.45, 3.35, 2.25); KY0, KY1, KZ1 = Y0 + KIT[0] * DUD, Y0 + KIT[1] * DUD, KIT[3] * DZ      # the kitchen at the back, by the dining
PAS = hy(-0.75, 0.25, 2.25); PY0, PY1, PZ1 = Y0 + PAS[0] * DUD, Y0 + PAS[1] * DUD, PAS[3] * DZ
floor = grid('Floor', (X0, Y0, 0), (X1 - X0, 0, 0), (0, Y1 - Y0, 0), M['tile'], tile=0.8)
def tile_uv(ob, T=0.8, seed=5, ox0=0.0, oy0=None):
    me = ob.data; uv = me.uv_layers['UV']; r = np.random.default_rng(seed); cache = {}
    oy0 = Y0 if oy0 is None else oy0
    for poly in me.polygons:
        cx = sum(me.vertices[v].co.x for v in poly.vertices) / len(poly.vertices); cy = sum(me.vertices[v].co.y for v in poly.vertices) / len(poly.vertices)
        key = (int(math.floor((cx + 0.4 - ox0) / T)), int(math.floor((cy - oy0) / T)))
        if key not in cache: cache[key] = (int(r.integers(0, 4)), bool(r.integers(0, 2)), float(r.random()) * 0.3, float(r.random()) * 0.3)
        k, flip, ox, oy = cache[key]
        for li, vi in zip(poly.loop_indices, poly.vertices):
            co = me.vertices[vi].co; u = (co.x + 0.4 - ox0 - key[0] * T) / T; v = (co.y - oy0 - key[1] * T) / T
            if flip: u = 1 - u
            for _ in range(k): u, v = 1 - v, u
            uv.data[li].uv = (u * 0.7 + ox, v * 0.7 + oy)
tile_uv(floor)
grid('Ceiling', (X0, Y1, H), (X1 - X0, 0, 0), (0, -(Y1 - Y0), 0), M['ceiling'], tile=3.0)
grid('Back Wall', (X0, Y1, 0), (X1 - X0, 0, 0), (0, 0, H), M['wall'], tile=3.0, holes=[BAL])
grid('Left Wall', (X0, Y0, 0), (0, Y1 - Y0, 0), (0, 0, H), M['wall'], tile=3.0, holes=[KIT, PAS])
grid('Right Wall', (X1, Y1, 0), (0, -(Y1 - Y0), 0), (0, 0, H), M['wall'], tile=3.0)
grid('Front Wall', (X1, Y0, 0), (-(X1 - X0), 0, 0), (0, 0, H), M['wall'], tile=3.0)
gl = [box('Grout', (-0.4 + 0.8 * k, 0, 0.0008), (0.004, Y1 - Y0, 0.0016), M['grout']) for k in range(-3, 4) if X0 < -0.4 + 0.8 * k < X1]
gl += [box('Grout', (0, Y0 + 0.8 * k, 0.0008), (X1 - X0, 0.004, 0.0016), M['grout']) for k in range(1, 10) if Y0 + 0.8 * k < Y1]
grout = join(gl, 'LM_Grout'); world_uv(grout, 1.0); lm(grout, 1024)

# skirting (8 cm tile strip) round the walls, broken at the openings and behind the built-ins
SK = 0.08; sk = []
def skx(a, b, y, s): sk.append(bx('Skirting', a, b, y - (0.012 if s > 0 else 0), y + (0.012 if s < 0 else 0), 0, SK, M['tile']))
def sky_(a, b, x, s): sk.append(bx('Skirting', x - (0.012 if s > 0 else 0), x + (0.012 if s < 0 else 0), a, b, 0, SK, M['tile']))
skx(X0, BX0, Y1, 1); skx(BX1, X1, Y1, 1)
skx(X0, 0.48, Y0, -1)
for a, b in ((Y0, PY0), (PY1, KY0), (KY1, Y1)): sky_(a, b, X0, -1)
for a, b in ((-2.88, -2.67), (-0.43, 0.93), (2.57, Y1)): sky_(a, b, X1, 1)
skirt = join(sk, 'LM_Skirting'); world_uv(skirt, 1.0); lm(skirt, 512)

# ---------------------------------------------------------------- openings: kitchen and passage (plaster reveals), beyond-rooms
T_ = 0.15
op = []
for a, b, z1 in ((KY0, KY1, KZ1), (PY0, PY1, PZ1)):
    op += [bx('Jamb', X0 - T_, X0, a - 0.005, a, 0, z1, M['wall']), bx('Jamb', X0 - T_, X0, b, b + 0.005, 0, z1, M['wall']),
           bx('Head', X0 - T_, X0, a, b, z1, z1 + 0.005, M['wall'])]
# the balcony door's reveal (20 cm wall)
op += [bx('Reveal', BX0 - 0.005, BX0, Y1, Y1 + 0.2, 0, BZ1, M['wall']), bx('Reveal', BX1, BX1 + 0.005, Y1, Y1 + 0.2, 0, BZ1, M['wall']),
       bx('Reveal', BX0, BX1, Y1, Y1 + 0.2, BZ1, BZ1 + 0.005, M['wall'])]
opening = join(op, 'LM_Openings'); world_uv(opening, 3.0); lm(opening, 512)
# kitchen beyond (the Oak Kitchen's look: navy bases, quartz, oak uppers), 2 m deep
KX = X0 - 2.0
kf = grid('Kitchen Floor', (KX, KY0 - 0.6, 0), (X0 - KX, 0, 0), (0, KY1 - KY0 + 1.2, 0), M['tile'], tile=0.8); tile_uv(kf, seed=7)
grid('Kitchen Back', (KX, KY1 + 0.6, 0), (0, -(KY1 - KY0 + 1.2), 0), (0, 0, H), M['wall'], tile=3.0).data.flip_normals()
grid('Kitchen Side A', (KX, KY0 - 0.6, 0), (X0 - T_ - KX, 0, 0), (0, 0, H), M['wall'], tile=3.0).data.flip_normals()
grid('Kitchen Side B', (X0 - T_, KY1 + 0.6, 0), (-(X0 - T_ - KX), 0, 0), (0, 0, H), M['wall'], tile=3.0).data.flip_normals()
grid('Kitchen Ceiling', (KX, KY1 + 0.6, H), (X0 - KX, 0, 0), (0, -(KY1 - KY0 + 1.2), 0), M['ceiling'], tile=3.0)
kp = [bx('K Base', KX, KX + 0.60, KY0 - 0.6, KY1 + 0.6, 0.10, 0.86, M['navy']), bx('K Plinth', KX, KX + 0.55, KY0 - 0.6, KY1 + 0.6, 0, 0.10, M['matblack']),
      bx('K Top', KX, KX + 0.62, KY0 - 0.6, KY1 + 0.6, 0.86, 0.90, M['quartz']), bx('K Splash', KX, KX + 0.012, KY0 - 0.6, KY1 + 0.6, 0.90, 1.50, M['whitemarble']),
      bx('K Upper', KX, KX + 0.35, KY0 - 0.6, KY1 + 0.6, 1.52, 2.25, M['oak'])]
for yy in (KY0 - 0.15, KY0 + 0.45, KY1 + 0.15):
    kp.append(bx('K Gap', KX + 0.60, KX + 0.603, yy - 0.002, yy + 0.002, 0.12, 0.84, M['gap'])); kp.append(bx('K Gap', KX + 0.35, KX + 0.353, yy - 0.002, yy + 0.002, 1.53, 2.24, M['gap']))
kit = join(kp, 'LM_KitchenGlimpse'); world_uv(kit, 1.2); lm(kit, 1024)
# passage beyond: a 1 m corridor, 1.6 m deep, a white bedroom door at its end
CX = X0 - 1.6
cf = grid('Corridor Floor', (CX, PY0, 0), (X0 - CX, 0, 0), (0, PY1 - PY0, 0), M['tile'], tile=0.8); tile_uv(cf, seed=8)
grid('Corridor End', (CX, PY1, 0), (0, -(PY1 - PY0), 0), (0, 0, H), M['wall'], tile=3.0).data.flip_normals()
grid('Corridor Side A', (CX, PY0, 0), (X0 - T_ - CX, 0, 0), (0, 0, H), M['wall'], tile=3.0).data.flip_normals()
grid('Corridor Side B', (X0 - T_, PY1, 0), (-(X0 - T_ - CX), 0, 0), (0, 0, H), M['wall'], tile=3.0).data.flip_normals()
grid('Corridor Ceiling', (CX, PY1, H), (X0 - CX, 0, 0), (0, -(PY1 - PY0), 0), M['ceiling'], tile=3.0)
pc_ = (PY0 + PY1) / 2
cd = [bx('Bed Door Frame', CX, CX + 0.04, pc_ - 0.50, pc_ + 0.50, 0, 2.18, M['white']), bx('Bed Door', CX + 0.01, CX + 0.045, pc_ - 0.44, pc_ + 0.44, 0.01, 2.12, M['white']),
      bx('Bed Door Handle', CX + 0.045, CX + 0.07, pc_ + 0.30, pc_ + 0.40, 1.04, 1.06, M['steel'])]
cdoor = join(cd, 'LM_BedDoor'); world_uv(cdoor, 2.0); lm(cdoor, 512)

# ---------------------------------------------------------------- main door (teak, brass), door mat, switches, video phone
DX0, DX1 = 0.50, 1.55
dp = [bx('Door Frame L', DX0 - 0.07, DX0, Y0, Y0 + 0.05, 0, 2.25, M['teak']), bx('Door Frame R', DX1, DX1 + 0.07, Y0, Y0 + 0.05, 0, 2.25, M['teak']),
      bx('Door Frame T', DX0 - 0.07, DX1 + 0.07, Y0, Y0 + 0.05, 2.18, 2.25, M['teak']), bx('Door Leaf', DX0, DX1, Y0, Y0 + 0.04, 0.005, 2.18, M['teak'])]
for z in (0.55, 0.95, 1.35, 1.75): dp.append(bx('Door Groove', DX0 + 0.08, DX1 - 0.08, Y0 + 0.04, Y0 + 0.043, z - 0.004, z + 0.004, M['gap']))
dp += [bx('Door Handle Plate', DX0 + 0.06, DX0 + 0.10, Y0 + 0.04, Y0 + 0.05, 0.95, 1.20, M['brass']),
       bx('Door Handle', DX0 + 0.065, DX0 + 0.095, Y0 + 0.05, Y0 + 0.09, 1.00, 1.15, M['brass']),
       bx('Peephole', (DX0 + DX1) / 2 - 0.01, (DX0 + DX1) / 2 + 0.01, Y0 + 0.04, Y0 + 0.05, 1.50, 1.52, M['brass'])]
dp += [bx('Switch', DX0 - 0.30, DX0 - 0.14, Y0, Y0 + 0.012, 1.15, 1.27, M['switch'])]
dp += [bx('Switch', X0, X0 + 0.012, 0.35, 0.47, 1.15, 1.27, M['switch']), bx('Switch', X1 - 0.012, X1, 0.70, 0.86, 1.15, 1.27, M['switch'])]
dp += [bx('Video Phone', DX0 - 0.30, DX0 - 0.12, Y0, Y0 + 0.02, 1.40, 1.60, M['white']), bx('Video Phone Screen', DX0 - 0.28, DX0 - 0.14, Y0 + 0.02, Y0 + 0.022, 1.46, 1.57, M['tvblack'])]
door = join(dp, 'LM_MainDoor'); world_uv(door, 1.2, vertical_grain=True); lm(door, 1024)

# ---------------------------------------------------------------- balcony: sliding door, floor, railing, view
FD = 0.10
bp = []
bp += [bx('Bal Frame', BX0, BX1, Y1 + FD, Y1 + FD + 0.08, 0, 0.05, M['alu']), bx('Bal Frame', BX0, BX1, Y1 + FD, Y1 + FD + 0.08, BZ1 - 0.06, BZ1, M['alu']),
       bx('Bal Frame', BX0, BX0 + 0.06, Y1 + FD, Y1 + FD + 0.08, 0, BZ1, M['alu']), bx('Bal Frame', BX1 - 0.06, BX1, Y1 + FD, Y1 + FD + 0.08, 0, BZ1, M['alu'])]
PW = (BX1 - BX0 - 0.12) / 3
for k in range(3):
    a = BX0 + 0.06 + k * PW; b = a + PW; yy = Y1 + FD + (0.005 if k != 1 else 0.042)
    for xa, xb, za, zb in ((a, b, 0.05, 0.11), (a, b, BZ1 - 0.12, BZ1 - 0.06), (a, a + 0.05, 0.05, BZ1 - 0.06), (b - 0.05, b, 0.05, BZ1 - 0.06)):
        bp.append(bx('Bal Sash', xa, xb, yy, yy + 0.035, za, zb, M['alu']))
    bp.append(bx('Bal Handle', b - 0.09 if k == 0 else a + 0.07, b - 0.07 if k == 0 else a + 0.09, yy - 0.02, yy, 0.95, 1.20, M['alu']))
baldoor = join(bp, 'LM_BalconyDoor'); world_uv(baldoor, 1.0); lm(baldoor, 1024)
GLASS = []
for k in range(3):
    a = BX0 + 0.06 + k * PW; yy = Y1 + FD + (0.005 if k != 1 else 0.042)
    g_ = bx('Balcony Glass', a + 0.05, a + PW - 0.05, yy + 0.015, yy + 0.02, 0.11, BZ1 - 0.12, M['glass']); g_.visible_shadow = False; GLASS.append(g_)
BY1 = Y1 + 0.2 + 1.4
bf = grid('Balcony Floor Outside', (X0, Y1 + 0.2, -0.003), (X1 - X0, 0, 0), (0, 1.4, 0), M['tile'], tile=0.8); tile_uv(bf, seed=12)
grid('Balcony Ceiling Outside', (X0, BY1, H), (X1 - X0, 0, 0), (0, -1.4, 0), M['ceiling'], tile=3.0)
grid('Balcony Side L Outside', (X0, Y1 + 0.2, 0), (0, 1.4, 0), (0, 0, H), M['wall'], tile=3.0)
grid('Balcony Side R Outside', (X1, BY1, 0), (0, -1.4, 0), (0, 0, H), M['wall'], tile=3.0)
rl = [bx('Rail', X0, X1, BY1 - 0.05, BY1, 1.02, 1.06, M['steel']), bx('Rail Base', X0, X1, BY1 - 0.08, BY1, 0, 0.12, M['wall'])]
for xx in (-1.2, -0.4, 0.4, 1.2): rl.append(bx('Rail Post', xx - 0.02, xx + 0.02, BY1 - 0.05, BY1 - 0.01, 0.12, 1.02, M['steel']))
rail = join(rl, 'LM_Railing'); world_uv(rail, 1.0); lm(rail, 512)
rg = bx('Railing Glass', X0, X1, BY1 - 0.035, BY1 - 0.025, 0.12, 1.02, M['glass']); rg.visible_shadow = False
pl = bpy.data.meshes.new('Outside'); Vn = [(-9, BY1 + 7, -6), (9, BY1 + 7, -6), (9, BY1 + 7, 7), (-9, BY1 + 7, 7)]
pl.from_pydata(Vn, [], [(0, 1, 2, 3)]); uvl = pl.uv_layers.new(name='UV')
for li, uv_ in zip(range(4), ((0, 0), (1, 0), (1, 1), (0, 1))): uvl.data[li].uv = uv_
pl.materials.append(OUTSIDE); outside = bpy.data.objects.new('Outside View', pl); scene.collection.objects.link(outside)

# ---------------------------------------------------------------- TV wall (right wall, living): grey marble centre, fluted oak sides, floating console
TVC = -1.55; TV0, TV1 = TVC - 1.10, TVC + 1.10; MW = 0.65     # the living at the front: TV wall just past the shoe cabinet
tw = [bx('TV Marble', X1 - 0.02, X1, TVC - MW, TVC + MW, 0, 2.75, M['marble'])]
twf = [bx('Flute Back', X1 - 0.012, X1, TV0, TVC - MW, 0, 2.75, M['oak']), bx('Flute Back', X1 - 0.012, X1, TVC + MW, TV1, 0, 2.75, M['oak'])]
for a, b in ((TV0, TVC - MW), (TVC + MW, TV1)):
    y = a + 0.005
    while y + 0.03 <= b:
        twf.append(bx('Flute', X1 - 0.035, X1 - 0.012, y, y + 0.03, 0, 2.75, M['oak'])); y += 0.04
tvwall = join(tw, 'LM_TVMarble'); world_uv(tvwall, 1.6); lm(tvwall, 1024)
flutes = join(twf, 'LM_TVFlutes'); world_uv(flutes, 1.2, vertical_grain=True); lm(flutes, 2048)
CN0, CN1 = TVC - 0.95, TVC + 0.95
cs = [bx('Console', X1 - 0.44, X1 - 0.02, CN0, CN1, 0.24, 0.60, M['oak'])]
for yy in (CN0 + 0.70, CN0 + 1.40): cs.append(bx('Console Gap', X1 - 0.443, X1 - 0.44, yy - 0.002, yy + 0.002, 0.25, 0.59, M['gap']))
cs.append(bx('Console Groove', X1 - 0.443, X1 - 0.44, CN0 + 0.02, CN1 - 0.02, 0.53, 0.536, M['gap']))
console = join(cs, 'LM_Console'); world_uv(console, 1.2); lm(console, 1024)
glow = [bx('Console Glow', X1 - 0.40, X1 - 0.06, CN0 + 0.05, CN1 - 0.05, 0.236, 0.24, M['led'])]
tv = [bx('TV Body', X1 - 0.055, X1 - 0.025, TVC - 0.617, TVC + 0.617, 0.955, 1.665, M['matblack'], 0.004),
      bx('TV Screen', X1 - 0.0565, X1 - 0.055, TVC - 0.605, TVC + 0.605, 0.967, 1.653, M['tvblack']),
      bx('Soundbar', X1 - 0.13, X1 - 0.04, TVC - 0.45, TVC + 0.45, 0.60, 0.665, M['matblack'], 0.012)]
tvo = join(tv, 'LM_TV'); world_uv(tvo, 1.0); lm(tvo, 512)
# split AC high on the left wall, near the balcony
ac = [bx('AC Body', X0, X0 + 0.21, -3.40, -2.50, 2.25, 2.55, M['white'], 0.02), bx('AC Vent', X0 + 0.15, X0 + 0.212, -3.35, -2.55, 2.27, 2.30, M['matblack'])]
aco = join(ac, 'LM_AC'); world_uv(aco, 1.0); lm(aco, 256)
# sofa wall: painted picture-frame mouldings (a wide centre panel for the Gond set, two narrow ones), under the AC's line
mo = []; MOW, MOD = 0.03, 0.016
def frame_x(y0, y1, z0, z1):
    mo.extend([bx('Moulding', X0, X0 + MOD, y0, y1, z0, z0 + MOW, M['wall'], 0.004), bx('Moulding', X0, X0 + MOD, y0, y1, z1 - MOW, z1, M['wall'], 0.004),
               bx('Moulding', X0, X0 + MOD, y0, y0 + MOW, z0 + MOW, z1 - MOW, M['wall'], 0.004), bx('Moulding', X0, X0 + MOD, y1 - MOW, y1, z0 + MOW, z1 - MOW, M['wall'], 0.004)])
for y0, y1 in ((-3.80, -3.18), (-3.10, -1.55), (-1.47, -0.85)):
    frame_x(y0, y1, 0.95, 2.15); frame_x(y0, y1, 0.14, 0.86)
mould = join(mo, 'LM_Mouldings'); world_uv(mould, 3.0); lm(mould, 1024)
mo = [bx('Dado Rail', X0, X0 + 0.022, -3.88, -0.77, 0.885, 0.92, M['wall'], 0.006)]
dado = join(mo, 'LM_Dado'); world_uv(dado, 3.0); lm(dado, 256)

# ---------------------------------------------------------------- dining wall (right): shoe cabinet + round mirror by the door, crockery unit
sc = [bx('Shoe Cab', X1 - 0.35, X1, -3.80, -2.90, 0.15, 0.95, M['oak']), bx('Shoe Top', X1 - 0.36, X1, -3.81, -2.89, 0.95, 0.975, M['quartz']),
      bx('Shoe Gap', X1 - 0.353, X1 - 0.35, -3.352, -3.348, 0.16, 0.94, M['gap']), bx('Shoe Glow', X1 - 0.30, X1 - 0.05, -3.75, -2.95, 0.145, 0.15, M['led']),
      bx('Shoe Handle', X1 - 0.362, X1 - 0.35, -3.79, -2.91, 0.905, 0.935, M['alu']), bx('Shoe Edge', X1 - 0.351, X1 - 0.35, -3.80, -2.90, 0.15, 0.152, M['gap'])]
shoe = join(sc, 'LM_ShoeCab'); world_uv(shoe, 1.2); lm(shoe, 512)
CU0, CU1 = 0.95, 2.55; CD = 0.42
cu = [bx('CU Plinth', X1 - CD + 0.05, X1, CU0, CU1, 0, 0.10, M['matblack']), bx('CU Base', X1 - CD, X1, CU0, CU1, 0.10, 0.85, M['oak']),
      bx('CU Top', X1 - CD - 0.01, X1, CU0 - 0.01, CU1 + 0.01, 0.85, 0.875, M['quartz']), bx('CU Niche Back', X1 - 0.015, X1, CU0, CU1, 0.875, 1.25, M['whitemarble']),
      bx('CU Upper Box', X1 - 0.38, X1, CU0, CU1, 1.25, 1.27, M['oak']), bx('CU Upper Top', X1 - 0.38, X1, CU0, CU1, 2.18, 2.20, M['oak']),
      bx('CU Upper Back', X1 - 0.012, X1, CU0, CU1, 1.27, 2.18, M['oak']), bx('CU Side', X1 - 0.38, X1, CU0, CU0 + 0.02, 1.25, 2.20, M['oak']),
      bx('CU Side', X1 - 0.38, X1, CU1 - 0.02, CU1, 1.25, 2.20, M['oak']), bx('CU Mid', X1 - 0.38, X1, (CU0 + CU1) / 2 - 0.01, (CU0 + CU1) / 2 + 0.01, 1.25, 2.20, M['oak']),
      bx('CU Shelf', X1 - 0.36, X1 - 0.012, CU0 + 0.02, CU1 - 0.02, 1.70, 1.715, M['oak'])]
for yy in (CU0 + 0.4, (CU0 + CU1) / 2, CU1 - 0.4): cu.append(bx('CU Gap', X1 - CD - 0.003, X1 - CD, yy - 0.002, yy + 0.002, 0.11, 0.84, M['gap']))
cu.append(bx('CU Handle', X1 - CD - 0.012, X1 - CD, CU0 + 0.01, CU1 - 0.01, 0.79, 0.82, M['alu']))
cu += [bx('CU Glass Shelf Edge', X1 - 0.37, X1 - 0.012, CU0 + 0.02, CU1 - 0.02, 1.715, 1.718, M['gap'])]
for a, b in ((CU0 + 0.02, (CU0 + CU1) / 2 - 0.01), ((CU0 + CU1) / 2 + 0.01, CU1 - 0.02)):          # glass doors' oak frames
    for xa, xb, za, zb in ((a, b, 1.27, 1.32), (a, b, 2.13, 2.18), (a, a + 0.05, 1.27, 2.18), (b - 0.05, b, 1.27, 2.18)):
        cu.append(bx('CU Door Frame', X1 - 0.40, X1 - 0.38, xa, xb, za, zb, M['oak']))
crock = join(cu, 'LM_Crockery'); world_uv(crock, 1.2); lm(crock, 2048)
for a, b in ((CU0 + 0.07, (CU0 + CU1) / 2 - 0.06), ((CU0 + CU1) / 2 + 0.06, CU1 - 0.07)):
    g_ = bx('CU Glass', X1 - 0.395, X1 - 0.39, a, b, 1.32, 2.13, M['bronzeglass']); g_.visible_shadow = False; GLASS.append(g_)
glow += [bx('CU Glow', X1 - 0.30, X1 - 0.05, CU0 + 0.05, CU1 - 0.05, 1.245, 1.25, M['led'])]

# ---------------------------------------------------------------- mandir on the left wall (between kitchen and passage): drawer unit, temple box, arch glow
MY0, MY1 = 1.15, 2.05; MC = (MY0 + MY1) / 2
md = [bx('Mandir Drawers', X0, X0 + 0.40, MY0, MY1, 0.30, 0.70, M['teak']), bx('Mandir Drawer Gap', X0 + 0.40, X0 + 0.403, MY0 + 0.02, MY1 - 0.02, 0.499, 0.503, M['gap']),
      bx('Mandir Base', X0, X0 + 0.32, MY0 + 0.08, MY1 - 0.08, 1.00, 1.04, M['teak']), bx('Mandir Top', X0, X0 + 0.34, MY0 + 0.06, MY1 - 0.06, 1.80, 1.86, M['teak']),
      bx('Mandir Side', X0, X0 + 0.32, MY0 + 0.08, MY0 + 0.12, 1.04, 1.80, M['teak']), bx('Mandir Side', X0, X0 + 0.32, MY1 - 0.12, MY1 - 0.08, 1.04, 1.80, M['teak']),
      bx('Mandir Back', X0, X0 + 0.012, MY0 + 0.12, MY1 - 0.12, 1.04, 1.80, M['white']),
      bx('Mandir Pillar', X0 + 0.30, X0 + 0.34, MY0 + 0.08, MY0 + 0.12, 1.04, 1.80, M['brass']), bx('Mandir Pillar', X0 + 0.30, X0 + 0.34, MY1 - 0.12, MY1 - 0.08, 1.04, 1.80, M['brass'])]
mandir = join(md, 'LM_Mandir'); world_uv(mandir, 1.0, vertical_grain=True); lm(mandir, 1024)
glow += [bx('Mandir Glow', X0 + 0.02, X0 + 0.30, MY0 + 0.13, MY1 - 0.13, 1.795, 1.80, M['led'])]
# v2 mandir detail: a backlit CNC jaali (overlapping-circle lotus lattice in teak over warm light) behind the idol
def jaali_image():
    S = 1024; y, x = np.mgrid[0:S, 0:S] / S * 4.0                       # 4 x 4 repeats of the lattice
    fx, fy = x % 1 - 0.5, y % 1 - 0.5; r = np.sqrt(fx * fx + fy * fy)
    lattice = np.zeros((S, S), bool)
    for cx_, cy_ in ((0, 0), (0.5, 0), (-0.5, 0), (0, 0.5), (0, -0.5)):    # petals: circles of r 0.5 centred on the cell's edges
        d = np.sqrt((fx - cx_) ** 2 + (fy - cy_) ** 2); lattice |= np.abs(d - 0.5) < 0.035
    lattice |= np.abs(r - 0.12) < 0.03                                    # a small ring at every flower's heart
    edge = np.minimum(np.minimum(x, 4 - x), np.minimum(y, 4 - y)) < 0.12  # solid border
    wood_ = np.array([0.30, 0.17, 0.08]); light = np.array([1.0, 0.86, 0.62])
    rgb = np.where((lattice | edge)[..., None], wood_ * 0.25, light)
    return SL.img('jaali_col', np.clip(rgb, 0, 1), TMP)
JAALI = mat('Jaali Backlit', (0, 0, 0, 1), 0.6)
_jb = JAALI.node_tree.nodes['Principled BSDF']; _jt = JAALI.node_tree.nodes.new('ShaderNodeTexImage'); _jt.image = jaali_image()
JAALI.node_tree.links.new(_jt.outputs['Color'], _jb.inputs['Emission Color']); _jb.inputs['Emission Strength'].default_value = 2.2
_jo = bx('Mandir Jaali', X0 + 0.012, X0 + 0.016, MY0 + 0.12, MY1 - 0.12, 1.08, 1.795, JAALI); world_uv(_jo, 0.56); glow.append(_jo)   # 14 cm flowers
for g_ in glow: g_.visible_shadow = False

# ---------------------------------------------------------------- false ceiling: band at 2.75, recessed trays with coves (living, dining), downlights
FZ = H - 0.25
LIV = (-1.15, 1.15, -3.35, -0.55); DIN = (-0.95, 0.75, 0.95, 3.10)
fc = []
for y0, y1 in ((Y0, LIV[2]), (LIV[3], DIN[2]), (DIN[3], Y1)): fc.append(bx('FC Band', X0, X1, y0, y1, FZ, H, M['gypsum']))
for t in (LIV, DIN):
    fc += [bx('FC Band', X0, t[0], t[2], t[3], FZ, H, M['gypsum']), bx('FC Band', t[1], X1, t[2], t[3], FZ, H, M['gypsum'])]
    # v2: the lips no longer overlap at the corners (the overlap baked black squares into every tray corner)
    fc += [bx('FC Lip', t[0], t[0] + 0.05, t[2] + 0.05, t[3] - 0.05, FZ - 0.03, FZ, M['gypsum']), bx('FC Lip', t[1] - 0.05, t[1], t[2] + 0.05, t[3] - 0.05, FZ - 0.03, FZ, M['gypsum']),
           bx('FC Lip', t[0], t[1], t[2], t[2] + 0.05, FZ - 0.03, FZ, M['gypsum']), bx('FC Lip', t[0], t[1], t[3] - 0.05, t[3], FZ - 0.03, FZ, M['gypsum'])]
falsec = join(fc, 'LM_FalseCeiling'); world_uv(falsec, 3.0); lm(falsec, 2048)
# a 15 mm shadow gap where the false ceiling meets every wall (the finished-gypsum look), dark, not lit
sg = [bx('FC Shadow Gap', X0, X0 + 0.012, Y0, Y1, FZ - 0.018, FZ, M['gap']), bx('FC Shadow Gap', X1 - 0.012, X1, Y0, Y1, FZ - 0.018, FZ, M['gap']),
      bx('FC Shadow Gap', X0 + 0.012, X1 - 0.012, Y0, Y0 + 0.012, FZ - 0.018, FZ, M['gap']), bx('FC Shadow Gap', X0 + 0.012, BX0, Y1 - 0.012, Y1, FZ - 0.018, FZ, M['gap']),
      bx('FC Shadow Gap', BX1, X1 - 0.012, Y1 - 0.012, Y1, FZ - 0.018, FZ, M['gap'])]
sgap = join(sg, 'LM_ShadowGap'); world_uv(sgap, 1.0); lm(sgap, 256)
CG = []
for t in (LIV, DIN):
    CG += [bx('Cove Glow', t[0] + 0.07, t[0] + 0.09, t[2] + 0.1, t[3] - 0.1, H - 0.012, H - 0.004, M['cove']), bx('Cove Glow', t[1] - 0.09, t[1] - 0.07, t[2] + 0.1, t[3] - 0.1, H - 0.012, H - 0.004, M['cove']),
           bx('Cove Glow', t[0] + 0.1, t[1] - 0.1, t[2] + 0.07, t[2] + 0.09, H - 0.012, H - 0.004, M['cove']), bx('Cove Glow', t[0] + 0.1, t[1] - 0.1, t[3] - 0.09, t[3] - 0.07, H - 0.012, H - 0.004, M['cove'])]
# a slim linear LED profile set into the band between the two trays, across the hall
CG.append(bx('Linear Profile', -1.05, 1.05, 0.18, 0.215, FZ - 0.003, FZ, M['led']))
CG += [bx('Linear Profile Trim', -1.06, 1.06, 0.172, 0.178, FZ - 0.004, FZ, M['alu']), bx('Linear Profile Trim', -1.06, 1.06, 0.217, 0.223, FZ - 0.004, FZ, M['alu'])]
for g_ in CG: g_.visible_shadow = False
DL = [(-1.45, -3.20), (-1.45, -2.15), (-1.45, -1.10), (1.45, -2.45), (1.45, -0.75), (-0.5, -0.25), (0.5, -0.25),
      (-1.35, 1.40), (-1.35, 2.70), (1.40, 1.20), (1.40, 2.30), (0.0, -3.62), (1.05, -3.62), (-0.6, 3.62), (0.6, 3.62)]
for i_, (x_, y_) in enumerate(DL):
    cyl('DLTrim%d' % i_, (x_, y_, FZ - 0.004), 0.05, 0.008, M['dltrim']); cyl('DLLens%d' % i_, (x_, y_, FZ - 0.009), 0.035, 0.006, M['dl'])

# ---------------------------------------------------------------- staging (no dot): dining table + chairs, rug, curtains, plants, door mat, crockery, mirror
STAGE = []
def lathe(name, prof, m, loc, seg=40):
    o = SL.lathe(name, prof, m, seg=seg); o.location = loc; STAGE.append(o); return o
def S(o): STAGE.append(o); return o
TX, TY = -0.15, 2.05
S(box('Table Top', (TX, TY, 0.74), (0.90, 1.80, 0.04), M['walnut'], 0.004))
for sx in (-1, 1):
    for sy in (-1, 1): S(box('Table Leg', (TX + sx * 0.37, TY + sy * 0.80, 0.36), (0.06, 0.06, 0.72), M['walnut'], 0.004))
S(box('Table Apron', (TX, TY, 0.68), (0.80, 1.66, 0.08), M['walnut'], 0.003))
for o in STAGE: world_uv(o, 1.2)
def chair(x, y, rz):
    from mathutils import Matrix
    parts = [box('Seat', (0, 0, 0.44), (0.46, 0.46, 0.08), M['fabric'], 0.02), box('Back', (0, 0.21, 0.72), (0.44, 0.06, 0.50), M['fabric'], 0.02)]
    for lx in (-0.19, 0.19):
        for ly in (-0.19, 0.19): parts.append(box('Chair Leg', (lx, ly, 0.20), (0.035, 0.035, 0.40), M['walnut'], 0.003))
    o = SL.join(parts, 'Dining Chair'); o.matrix_world = Matrix.Translation((x, y, 0)) @ Matrix.Rotation(rz, 4, 'Z'); STAGE.append(o)
    bpy.context.view_layer.update(); world_uv(o, 0.45)
for yy in (TY - 0.45, TY + 0.45):
    chair(TX - 0.62, yy, math.pi / 2); chair(TX + 0.62, yy, -math.pi / 2)        # v2: backs away from the table
chair(TX, TY - 1.17, math.pi); chair(TX, TY + 1.17, 0)
rn = S(box('Table Runner', (TX, TY, 0.762), (0.34, 1.50, 0.004), M['runner'], 0.0)); world_uv(rn, 0.4)
S(box('Runner Hem', (TX, TY - 0.75, 0.7585), (0.34, 0.006, 0.012), M['runner'], 0.0)); S(box('Runner Hem', (TX, TY + 0.75, 0.7585), (0.34, 0.006, 0.012), M['runner'], 0.0))
# living rug
rug = S(box('Rug', (0.0, -2.10, 0.006), (1.70, 2.40, 0.012), M['rug'], 0.004))
me = rug.data; uv = me.uv_layers[0] if me.uv_layers else me.uv_layers.new(name='UV')
for p in me.polygons:
    for li, vi in zip(p.loop_indices, p.vertices):
        co = me.vertices[vi].co; uv.data[li].uv = ((co.x + 0.85) / 1.70, (co.y + 3.30) / 2.40)
# coffee table (top at 0.382): two cloth-bound books beside the candle
for (bw, bd, bh, bz, rz, m_) in ((0.26, 0.19, 0.032, 0.382, 0.10, 'book1'), (0.22, 0.16, 0.026, 0.414, -0.12, 'book2')):
    S(box('Book', (0.44, -1.88, bz + bh / 2), (bw, bd, bh), M[m_], 0.002, rot=(0, 0, rz)))
    S(box('Book Pages', (0.44 + 0.004, -1.88, bz + bh / 2), (bw - 0.012, bd - 0.008, bh - 0.006), M['pages'], 0.0, rot=(0, 0, rz)))
# cushions on the sofa happen with the product; door mat
S(box('Door Mat', ((DX0 + DX1) / 2, Y0 + 0.40, 0.006), (0.80, 0.50, 0.012), M['coir'], 0.004))
# crockery behind the glass: plates standing, bowls, cups
for k in range(5): S(SL.lathe('Plate', [(0, 0), (0.12, 0), (0.13, 0.015), (0, 0.012)], M['crockery'], seg=32)).location = (X1 - 0.20, CU0 + 0.20 + k * 0.03, 1.40)
for o in STAGE[-5:]: o.rotation_euler = (math.pi / 2 - 0.15, 0, 0)
for k in range(3): lathe('Bowl', [(0, 0), (0.05, 0), (0.08, 0.06), (0.075, 0.06), (0.045, 0.006), (0, 0.006)], M['crockery'], (X1 - 0.20, CU1 - 0.55 + k * 0.17, 1.27))
for k in range(4): lathe('Cup', [(0, 0), (0.035, 0), (0.04, 0.08), (0.036, 0.08), (0.03, 0.006), (0, 0.006)], M['crockery'], (X1 - 0.20, CU0 + 0.15 + k * 0.12, 1.715))
for k in range(3): lathe('Glass Jar', [(0, 0), (0.06, 0), (0.06, 0.16), (0.045, 0.18), (0, 0.18)], M['bronzeglass'], (X1 - 0.20, CU1 - 0.55 + k * 0.17, 1.715))
# mandir: a brass diya with a flame, a small bell, a rangoli-red cloth on the base
lathe('Diya', [(0, 0), (0.03, 0), (0.04, 0.02), (0, 0.02)], M['brass'], (X0 + 0.22, MC + 0.18, 1.04))
S(SL.lathe('Flame', [(0, 0), (0.006, 0.004), (0.004, 0.02), (0, 0.03)], M['diya'], seg=12)).location = (X0 + 0.22, MC + 0.18, 1.06)
lathe('Bell', [(0, 0), (0.025, 0), (0.02, 0.03), (0.008, 0.045), (0, 0.05)], M['brass'], (X0 + 0.20, MC - 0.20, 1.04))
S(box('Mandir Cloth', (X0 + 0.17, MC, 1.0405), (0.28, 0.66, 0.002), mat('Red Cloth', (0.62, 0.08, 0.06, 1), 0.8), 0.0))
# v2: a white-marble step for the idol, a kalash, two hanging brass bells, a marigold-and-mango-leaf toran across the front
S(box('Mandir Step', (X0 + 0.135, MC, 1.06), (0.17, 0.30, 0.04), M['whitemarble'], 0.004))
lathe('Kalash', [(0, 0), (0.02, 0), (0.035, 0.03), (0.03, 0.06), (0.018, 0.075), (0.024, 0.085), (0, 0.085)], M['brass'], (X0 + 0.24, MC - 0.08, 1.04))
for yy in (MY0 + 0.20, MY1 - 0.20):
    S(SL.tube('Bell Chain', [(X0 + 0.25, yy, 1.795), (X0 + 0.25, yy, 1.66)], [0.0025, 0.0025], M['brass'], seg=6))
    lathe('Hanging Bell', [(0, 0), (0.032, 0), (0.03, 0.012), (0.022, 0.045), (0.010, 0.06), (0, 0.065)], M['brass'], (X0 + 0.25, yy, 1.60))
def toran(x, ya, yb, ztop, sag, drops):
    """Marigold strings: one swag between ya and yb, and short hanging strands, built as one mesh of small spheres."""
    import bmesh
    bm = bmesh.new(); pts = []
    n = 28
    for k in range(n + 1):
        t = k / n; pts.append((x, ya + (yb - ya) * t, ztop - sag * 4 * t * (1 - t)))
    for k in range(drops + 1):
        t = k / drops; y0 = ya + (yb - ya) * t; z0 = ztop - sag * 4 * t * (1 - t)
        for j in range(1, 6): pts.append((x, y0, z0 - j * 0.022))
    for p in pts:
        m_ = Matrix.Translation(p); bmesh.ops.create_icosphere(bm, subdivisions=1, radius=0.012, matrix=m_)
    me = bpy.data.meshes.new('Toran'); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new('Marigold Toran', me); scene.collection.objects.link(o); me.materials.append(M['marigold']); STAGE.append(o)
    V, F, UV = [], [], []                                                # mango leaves between the strands
    for k in range(drops + 1):
        t = k / drops; y0 = ya + (yb - ya) * t; z0 = ztop - sag * 4 * t * (1 - t)
        SL.leaf_strip(V, F, UV, Vector((x + 0.004, y0 + 0.02, z0)), Vector((0.1, 0.15, -1)).normalized(), Vector((0, 1, 0)), 0.09, 0.022, droop=0.1)
    STAGE.append(SL.mesh_obj('Toran Leaves', V, F, M['mango'], UV))
from mathutils import Matrix
toran(X0 + 0.355, MY0 + 0.07, MY1 - 0.07, 1.785, 0.05, 6)
# curtains: taupe drapes gathered at both sides of the balcony door, sheers behind, on a black rod
def drape(x0, x1, y, ztop, zbot, folds, amp, m, name):
    NU, NV = 160, 40; V, F, UV = [], [], []
    for j in range(NV + 1):
        z = ztop - (ztop - zbot) * j / NV
        for i in range(NU + 1):
            t = i / NU; x = x0 + (x1 - x0) * t
            a_ = amp * (0.8 + 0.35 * math.sin(t * 7.3 + 1.1) * math.sin(t * 3.1)) * (1 + 0.25 * j / NV)
            V.append((x, y + a_ * math.sin(t * folds * 2 * math.pi), z)); UV.append(((x - x0) * 1.6 / 0.45, (ztop - z) / 0.45))
    for j in range(NV):
        for i in range(NU): F.append((j * (NU + 1) + i, j * (NU + 1) + i + 1, (j + 1) * (NU + 1) + i + 1, (j + 1) * (NU + 1) + i))
    o = SL.mesh_obj(name, V, F, m, UV); STAGE.append(o); return o
CY = Y1 - 0.10
drape(X0 + 0.04, X0 + 0.62, CY, FZ - 0.02, 0.0, 8, 0.045, M['drape'], 'Drape L'); drape(X1 - 0.62, X1 - 0.04, CY, FZ - 0.02, 0.0, 8, 0.045, M['drape'], 'Drape R')
sh1 = drape(X0 + 0.55, -0.50, CY + 0.06, FZ - 0.02, 0.0, 11, 0.03, M['sheer'], 'Sheer L'); sh2 = drape(0.50, X1 - 0.55, CY + 0.06, FZ - 0.02, 0.0, 11, 0.03, M['sheer'], 'Sheer R')
sh1.visible_shadow = False; sh2.visible_shadow = False
S(box('Curtain Track', (0, CY + 0.03, FZ - 0.008), (X1 - X0 - 0.04, 0.10, 0.016), M['alu'], 0.002))
# plants: a tall areca in a charcoal planter by the balcony door (right), two pots outside on the balcony
def areca(x, y, z, h=1.5, seed=4):
    lathe('Planter', [(0, 0), (0.15, 0), (0.19, 0.42), (0.20, 0.44), (0, 0.44)], M['planter'], (x, y, z), seg=48)
    lathe('Soil', [(0, 0.40), (0.185, 0.40), (0, 0.41)], M['soil'], (x, y, z), seg=32)
    r = np.random.default_rng(seed); V, F, UV = [], [], []
    for k in range(14):
        a = r.uniform(0, 2 * math.pi); lean = r.uniform(0.15, 0.5); L = r.uniform(0.6, 1.0) * h
        base = Vector((x + 0.03 * math.cos(a), y + 0.03 * math.sin(a), z + 0.42)); d = Vector((lean * math.cos(a), lean * math.sin(a), 1)).normalized()
        side = Vector((-math.sin(a), math.cos(a), 0))
        for j in range(16):                                                   # leaflets along the frond
            t = 0.15 + 0.85 * j / 15; c = base + d * (L * t) - Vector((0, 0, 0.18 * L * t * t))
            for sgn in (-1, 1):
                SL.leaf_strip(V, F, UV, c, (d * 0.3 + side * sgn + Vector((0, 0, -0.25))).normalized(), d, 0.22 * (1.1 - t), 0.022, droop=0.6)
    STAGE.append(SL.mesh_obj('Areca', V, F, M['leaf'], UV))
for xx in (-1.3, 1.3): lathe('Balcony Pot', [(0, 0), (0.12, 0), (0.16, 0.30), (0, 0.30)], M['terracotta'], (xx, BY1 - 0.30, 0))
for xx in (-1.3, 1.3):
    r = np.random.default_rng(int(xx * 10) + 50); V, F, UV = [], [], []
    for k in range(20):
        a = r.uniform(0, 2 * math.pi); up = Vector((r.uniform(0.2, 0.6) * math.cos(a), r.uniform(0.2, 0.6) * math.sin(a), 1)).normalized(); side = Vector((-math.sin(a), math.cos(a), 0))
        SL.leaf_strip(V, F, UV, Vector((xx, BY1 - 0.30, 0.30)), up, side, r.uniform(0.25, 0.45), r.uniform(0.04, 0.07), droop=r.uniform(0.3, 0.8))
    STAGE.append(SL.mesh_obj('Balcony Plant', V, F, M['leaf'], UV))
# cushions on the sofa (rust + linen) go in once the sofa is placed: by the product, see below
for o in STAGE: o.select_set(False)
