
# ---------------------------------------------------------------- furniture (built here, not for sale)
def bake_piece(parts, name, loc, rz, res=1024, tile=1.0):
    o = join(parts, name)
    bpy.ops.object.select_all(action='DESELECT'); o.select_set(True); bpy.context.view_layer.objects.active = o
    bpy.context.scene.cursor.location = (0, 0, 0); bpy.ops.object.origin_set(type='ORIGIN_CURSOR')   # the joined piece was built round the origin
    SL.place(o, loc, rz); world_uv(o, tile); lm(o); LMRES[o.name] = res; return o
LMRES = {}

def tufted(w, h, y0, z0, m, s=0.10, depth=0.04, res=0.026):
    """A diamond-tufted panel in the xz plane (front +y): puffy between the dimples. Returns the object and the dimple points."""
    nx, nz = max(2, int(w / res)), max(2, int(h / res)); V, F, UV = [], [], []
    def dist(x, z):
        a0, b0 = round(x / s), round(z / s); best = 9
        for a in (a0 - 1, a0, a0 + 1):
            for b in (b0 - 1, b0, b0 + 1):
                if (a + b) % 2 == 0: best = min(best, math.hypot(x - a * s, z - b * s))
        return best
    for j in range(nz + 1):
        for i in range(nx + 1):
            x = -w / 2 + w * i / nx; z = -h / 2 + h * j / nz
            hump = 1 - math.exp(-(dist(x, z) / (0.42 * s)) ** 2)
            V.append((x, y0 + depth * hump - depth * 0.4 * (1 - hump) * 0, z0 + z)); UV.append((x / 0.6, z / 0.6))
    for j in range(nz):
        for i in range(nx): F.append((j * (nx + 1) + i, (j + 1) * (nx + 1) + i, (j + 1) * (nx + 1) + i + 1, j * (nx + 1) + i + 1))   # normal toward +y (it faced the wall, and baked black)
    o = SL.mesh_obj('Tufting', V, F, m, UV)
    pts = [(a * s, b * s) for a in range(-12, 13) for b in range(-12, 13) if (a + b) % 2 == 0 and abs(a * s) < w / 2 - 0.05 and abs(b * s) < h / 2 - 0.04]
    return o, [(x, y0, z0 + z) for x, z in pts]

def sphere(name, loc, r, m, seg=8):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=seg, ring_count=max(4, seg // 2), radius=r, location=loc); o = bpy.context.active_object; o.name = name
    o.data.materials.append(m); bpy.ops.object.shade_smooth(); return o

def chester(L, D, nseat):
    P = []; arm = 0.22; Lm = M['leather']
    for sx in (-1, 1):
        for sy in (-1, 1): P.append(cyl('Leg', (sx * (L / 2 - 0.10), sy * (D / 2 - 0.10), 0.05), 0.04, 0.10, M['darkwood'], seg=12))
    P.append(box('Base', (0, 0, 0.20), (L, D, 0.20), Lm, bevel=0.03))
    iw = L - 2 * arm; sw = iw / nseat
    for k in range(nseat): P.append(box('Seat', (-iw / 2 + sw * (k + 0.5), 0.07, 0.385), (sw - 0.012, D - 0.26, 0.17), Lm, bevel=0.045, segs=4))
    P.append(box('Back', (0, -D / 2 + 0.11, 0.55), (L - 0.012, 0.22, 0.50), Lm, bevel=0.05))
    P.append(cyl('Roll', (0, -D / 2 + 0.115, 0.815), 0.085, L - 0.014, Lm, rot=(0, math.pi / 2, 0), seg=20))
    for sx in (-1, 1): P.append(sphere('RollEnd', (sx * (L / 2 - 0.007), -D / 2 + 0.115, 0.815), 0.085, Lm, 16))
    tp, dots = tufted(iw - 0.02, 0.40, -D / 2 + 0.225, 0.57, Lm); P.append(tp)
    for (x, y, z) in dots: P.append(sphere('Button', (x, y + 0.002, z), 0.012, M['brasslm']))
    for sx in (-1, 1):
        P.append(box('Arm', (sx * (L / 2 - arm / 2), 0, 0.51), (arm, D, 0.42), Lm, bevel=0.03))
        P.append(cyl('ArmRoll', (sx * (L / 2 - arm / 2), 0, 0.735), arm / 2 + 0.012, D, Lm, rot=(math.pi / 2, 0, 0), seg=20))
        for sy in (-1, 1): P.append(sphere('ArmEnd', (sx * (L / 2 - arm / 2), sy * D / 2, 0.735), arm / 2 + 0.012, Lm, 16))
        for yy in (-0.22, 0.0, 0.22):
            for zz in (0.48, 0.62): P.append(sphere('Button', (sx * (L / 2 + 0.002), yy, zz), 0.011, M['brasslm']))
    for xx in np.linspace(-L / 2 + 0.06, L / 2 - 0.06, int(L / 0.07)):                      # brass nail trim along the base front
        P.append(sphere('Nail', (xx, D / 2 + 0.002, 0.15), 0.008, M['brasslm'], 6))
    return P

def armchair():
    P = []; dw = M['darkwood']
    for sx in (-1, 1):
        for sy, hgt in ((-1, 0.92), (1, 0.45)):
            P.append(box('Leg', (sx * 0.31, sy * 0.32, hgt / 2), (0.05, 0.05, hgt), dw, bevel=0.006))
        P.append(box('ArmPost', (sx * 0.31, 0.27, 0.54), (0.04, 0.04, 0.18), dw, bevel=0.005))
        P.append(box('Arm', (sx * 0.31, -0.02, 0.64), (0.065, 0.62, 0.03), dw, bevel=0.008))
        P.append(box('SideRail', (sx * 0.31, 0, 0.37), (0.04, 0.62, 0.07), dw, bevel=0.004))
        P.append(box('ArmRail', (sx * 0.31, -0.02, 0.585), (0.025, 0.58, 0.025), dw, bevel=0.004))
        P.append(box('CaneSide', (sx * 0.31, -0.02, 0.50), (0.01, 0.55, 0.12), M['cane']))
    P.append(box('FrontRail', (0, 0.32, 0.37), (0.60, 0.04, 0.07), dw, bevel=0.004)); P.append(box('BackRail', (0, -0.32, 0.37), (0.60, 0.04, 0.07), dw, bevel=0.004))
    P.append(box('SeatBoard', (0, 0, 0.425), (0.58, 0.62, 0.03), dw))
    P.append(box('TopRail', (0, -0.32, 0.89), (0.64, 0.05, 0.07), dw, bevel=0.01)); P.append(box('MidRail', (0, -0.32, 0.47), (0.60, 0.04, 0.04), dw, bevel=0.004))
    P.append(box('CaneBack', (0, -0.32, 0.68), (0.57, 0.01, 0.38), M['cane']))
    for xx in (-0.15, 0.15): P.append(box('BackBar', (xx, -0.32, 0.68), (0.02, 0.03, 0.38), dw))
    P.append(box('SeatCushion', (0, 0.03, 0.50), (0.56, 0.54, 0.11), M['ivory'], bevel=0.035, segs=4))
    bc = box('BackCushion', (0, 0, 0), (0.52, 0.11, 0.38), M['ivory'], bevel=0.04, segs=4); bc.rotation_euler = (math.radians(-12), 0, 0); bc.location = (0, -0.25, 0.70); P.append(bc)
    return P

def coffee_table():
    P = []; Rw = M['rose']
    P.append(box('Top', (0, 0, 0.405), (1.15, 0.65, 0.04), Rw, bevel=0.012)); P.append(box('Inset', (0, 0, 0.427), (1.05, 0.55, 0.006), M['darkwood']))
    P.append(box('TopLip', (0, 0, 0.38), (1.10, 0.60, 0.02), Rw, bevel=0.006))
    P.append(box('Apron', (0, 0, 0.335), (1.0, 0.5, 0.09), Rw, bevel=0.008))
    for xx in np.linspace(-0.42, 0.42, 9):                                          # carved lozenge band on the apron faces
        for sy in (-1, 1): P.append(box('Carve', (xx, sy * 0.254, 0.335), (0.05, 0.012, 0.04), M['darkwood'], bevel=0.006, rot=(0, 0, 0)))
    for sx in (-1, 1):
        for sy in (-1, 1):
            pts = []; radii = []
            for t in map(float, np.linspace(0, 1, 9)):
                pts.append((sx * (0.50 + 0.05 * math.sin(math.pi * t * 0.9) * 0.0 + 0.045 * math.sin(math.pi * t)), sy * (0.25 + 0.045 * math.sin(math.pi * t)), 0.29 - t * 0.27))
                radii.append(0.034 - 0.014 * t + 0.01 * math.sin(math.pi * t))
            P.append(SL.tube('Leg', pts, radii, Rw, seg=10)); P.append(sphere('Foot', pts[-1], 0.02, Rw, 8))
    return P

def sideboard():
    P = []; Rw = M['rose']; W, D = 1.7, 0.48
    for sx in (-1, 1):
        for sy in (-1, 1): P.append(box('Foot', (sx * (W / 2 - 0.07), sy * (D / 2 - 0.06), 0.05), (0.07, 0.07, 0.10), M['darkwood'], bevel=0.005))
    P.append(box('Body', (0, 0, 0.435), (W, D, 0.67), Rw, bevel=0.006)); P.append(box('Top', (0, 0, 0.8035), (W + 0.04, D + 0.03, 0.03), Rw, bevel=0.008))
    f = D / 2 + 0.002
    for sx in (-1, 1):
        P.append(box('Groove', (sx * 0.30, f, 0.435), (0.008, 0.006, 0.62), M['darkwood']))
        P.append(box('Panel', (sx * 0.575, f, 0.44), (0.40, 0.01, 0.46), Rw, bevel=0.004)); P.append(box('PanelFrame', (sx * 0.575, f - 0.002, 0.44), (0.46, 0.008, 0.52), M['darkwood']))
        P.append(cyl('Pull', (sx * 0.36, f + 0.014, 0.46), 0.011, 0.028, M['brasslm'], rot=(math.pi / 2, 0, 0), seg=12))
        for sy2 in (-1, 1): P.append(box('Corner', (sx * (W / 2 - 0.02), f + 0.003, 0.77 + sy2 * 0.0), (0.05, 0.012, 0.05), M['brasslm']))
        P.append(box('CornerLo', (sx * (W / 2 - 0.02), f + 0.003, 0.125), (0.05, 0.012, 0.05), M['brasslm']))
    for z in (0.31, 0.50): P.append(box('Groove', (0, f, z), (0.55, 0.006, 0.008), M['darkwood']))
    for z in (0.215, 0.405, 0.60): P.append(box('Pull', (0, f + 0.007, z), (0.10, 0.014, 0.024), M['brasslm'], bevel=0.004))
    return P

def side_table(h, w):
    """A rosewood lamp table: bevelled top with an inlaid border, a drawer with a brass knob, turned legs, a lower shelf (front = local +y)."""
    P = []; Rw = M['rose']; lg = w / 2 - 0.035
    P.append(box('Top', (0, 0, h - 0.015), (w, w, 0.03), Rw, bevel=0.009))
    P.append(box('Inlay', (0, 0, h + 0.0005), (w - 0.07, w - 0.07, 0.002), M['darkwood']))
    P.append(box('Inlay2', (0, 0, h + 0.0012), (w - 0.12, w - 0.12, 0.002), Rw))
    P.append(box('Apron', (0, 0, h - 0.085), (w - 0.06, w - 0.06, 0.10), Rw, bevel=0.004))
    P.append(box('Drawer', (0, (w - 0.06) / 2 + 0.002, h - 0.085), (w - 0.14, 0.008, 0.075), Rw, bevel=0.003))
    P.append(box('DrawerLine', (0, (w - 0.06) / 2 + 0.0025, h - 0.085), (w - 0.12, 0.004, 0.082), M['darkwood']))
    P.append(sphere('Knob', (0, (w - 0.06) / 2 + 0.018, h - 0.085), 0.014, M['brasslm'], 12))
    for sx in (-1, 1):
        for sy in (-1, 1):
            prof = [(0, 0), (0.016, 0), (0.024, 0.02), (0.014, 0.05), (0.02, 0.08), (0.013, 0.12), (0.019, 0.16), (0.014, 0.2), (0.017, h * 0.45), (0.021, h * 0.55), (0.014, h * 0.6), (0.016, h - 0.14), (0.02, h - 0.12), (0.0, h - 0.12)]
            lg_ = SL.lathe('Leg', prof, M['darkwood'], seg=14); lg_.location = (sx * lg, sy * lg, 0); P.append(lg_)
    P.append(box('Shelf', (0, 0, 0.16), (w - 0.06, w - 0.06, 0.018), Rw, bevel=0.005))
    P.append(box('ShelfRail', (0, 0, 0.19), (w - 0.07, w - 0.07, 0.012), M['darkwood']))
    P.append(box('ShelfHole', (0, 0, 0.19), (w - 0.11, w - 0.11, 0.014), M['darkwood']))
    return P

# ---- the pieces, placed (rz: a piece faces local +y; -x is rz +90, +x is rz -90, -y is rz 180)
P_SOFA = bake_piece(chester(2.10, 0.95, 3), 'LM_Sofa', (X1 - 0.675, 0.55, 0), math.radians(90), 2048, 1.0)
P_LOVE = bake_piece(chester(1.70, 0.95, 2), 'LM_Loveseat', (X1 - 0.85, Y0 + 0.475, 0), 0.0, 1024, 1.0)
P_ARM1 = bake_piece(armchair(), 'LM_Armchair1', (-1.25, 0.65, 0), math.radians(-80), 1024, 1.0)
P_ARM2 = bake_piece(armchair(), 'LM_Armchair2', (-1.25, -0.30, 0), math.radians(-100), 1024, 1.0)
P_TA = bake_piece(side_table(0.55, 0.40), 'LM_SideTableA', (2.36, 1.84, 0), math.radians(90), 1024, 1.0)
P_TB = bake_piece(side_table(0.50, 0.38), 'LM_SideTableB', (2.38, -0.85, 0), math.radians(90), 1024, 1.0)
P_SIDE = bake_piece(sideboard(), 'LM_Sideboard', (-1.20, Y1 - 0.24, 0), math.pi, 1024, 1.0)

# ---- the Persian rug
rug = grid('Rug', (0.2 - 1.35, 0.05 - 0.95, 0.012), (2.7, 0, 0), (0, 1.9, 0), M['rug'], tile=2.7)
_me = rug.data; _lm = _me.uv_layers['LM']; _uv = _me.uv_layers['UV']
for li in range(len(_me.loops)): _uv.data[li].uv = _lm.data[li].uv

# ---------------------------------------------------------------- staging props (no dots, live-lit)
STAGE = []
def cover_mat(name, base, gold, seed):
    Hh, W = 192, 256; y, x = np.mgrid[0:Hh, 0:W]; rng_ = np.random.default_rng(seed)
    rgb = np.ones((Hh, W, 3)) * np.array(base) * (0.9 + 0.1 * rng_.random((Hh, W))[..., None])
    gm = np.zeros((Hh, W), bool)
    gm |= ((y > 10) & (y < 13) & (x > 10) & (x < W - 10)) | ((y > Hh - 13) & (y < Hh - 10) & (x > 10) & (x < W - 10)) | ((x > 10) & (x < 13) & (y > 10) & (y < Hh - 10)) | ((x > W - 13) & (x < W - 10) & (y > 10) & (y < Hh - 10))
    gm |= (y > 40) & (y < 48) & (x > 50) & (x < W - 50)                 # title bar
    gm |= (y > 60) & (y < 64) & (x > 70) & (x < W - 70)
    gm |= ((x - W / 2) ** 2 + (y - 125) ** 2 < 420) & ((x - W / 2) ** 2 + (y - 125) ** 2 > 300)   # small emblem ring
    rgb = np.where(gm[..., None], np.array(gold), rgb)
    return SL.mat(name, base, 0.55, image=SL.img(name + '_col', np.clip(rgb, 0, 1), TMP), sheen=0.2)
M['cover'] = cover_mat('Book Cloth A', (0.32, 0.10, 0.07), (0.80, 0.62, 0.25), 1)
M['cover2'] = cover_mat('Book Cloth B', (0.08, 0.16, 0.12), (0.85, 0.80, 0.60), 2)
M['cover3'] = cover_mat('Book Cloth C', (0.46, 0.30, 0.12), (0.18, 0.10, 0.05), 3)
_pg = np.tile((0.90 - 0.06 * ((np.arange(64) % 3) == 0))[:, None, None], (1, 8, 3)); M['pages'] = SL.mat('Page Edges', (0.9, 0.88, 0.8), 0.9, image=SL.img('pages_col', np.clip(_pg, 0, 1), TMP))

def book(loc, w, d, t, m, rz=0.0):
    x, y, z = loc
    parts = [box('BookTop', (x, y, z + t - 0.0025), (w, d, 0.005), m, bevel=0.0015), box('BookBot', (x, y, z + 0.0025), (w, d, 0.005), m, bevel=0.0015),
             box('BookSpine', (x - w / 2 + 0.003, y, z + t / 2), (0.006, d, t), m, bevel=0.002), box('Pages', (x + 0.003, y, z + t / 2), (w - 0.012, d - 0.008, t - 0.008), M['pages'])]
    o = join(parts, 'Book')
    bpy.ops.object.select_all(action='DESELECT'); o.select_set(True); bpy.context.view_layer.objects.active = o
    bpy.context.scene.cursor.location = (x, y, z + t / 2); bpy.ops.object.origin_set(type='ORIGIN_CURSOR'); o.rotation_euler.z = rz
    STAGE.append(o); return o
def stack(x, y, z, items, rz=0.0):
    for k, (w, d, t, m, dz) in enumerate(items):
        book((x, y, z), w, d, t, M[m], rz + dz); z += t

def pleated_shade(loc, r0, r1, h, seg=72):
    V, F = [], []
    for k in range(2):
        pass
    rows = 3
    for i in range(rows):
        t = i / (rows - 1); r = r0 + (r1 - r0) * t
        for s in range(seg): a = 2 * math.pi * s / seg; rr = r * (1 + 0.04 * math.cos(24 * a)); V.append((rr * math.cos(a), rr * math.sin(a), h * t))
    for i in range(rows - 1):
        for s in range(seg): F.append((i * seg + s, i * seg + (s + 1) % seg, (i + 1) * seg + (s + 1) % seg, (i + 1) * seg + s))
    o = SL.mesh_obj('Shade', V, F, M['shade']); o.location = loc; return o

def brass_lamp(x, y, z):
    base = SL.lathe('LampBase', [(0, 0), (0.07, 0), (0.075, 0.012), (0.055, 0.03), (0.026, 0.06), (0.015, 0.11), (0.018, 0.2), (0.026, 0.25), (0.0, 0.255)], M['brass'], seg=24)
    base.location = (x, y, z); sh = pleated_shade((x, y, z + 0.25), 0.115, 0.075, 0.21)
    bulb = sphere('Bulb', (x, y, z + 0.29), 0.022, M['glow'], 8); STAGE.extend([base, sh, bulb]); return (x, y, z + 0.29)

def decanter(x, y, z):
    g = SL.lathe('Decanter', [(0, 0.0), (0.042, 0.0), (0.048, 0.015), (0.048, 0.11), (0.03, 0.135), (0.013, 0.16), (0.014, 0.22), (0.02, 0.23), (0.02, 0.235), (0.0, 0.235)], M['glassc'], seg=28)
    wh = SL.lathe('Whisky', [(0, 0.004), (0.041, 0.004), (0.046, 0.016), (0.046, 0.085), (0.0, 0.085)], M['amber'], seg=24)
    stop = SL.lathe('Stopper', [(0, 0.22), (0.013, 0.22), (0.017, 0.245), (0.0, 0.26)], M['glassc'], seg=14)
    for o in (g, wh, stop): o.location = (x, y, z); STAGE.append(o)
def tumbler(x, y, z):
    g = SL.lathe('Tumbler', [(0, 0.0), (0.028, 0.0), (0.036, 0.09), (0.0, 0.09)], M['glassc'], seg=20); g.location = (x, y, z); STAGE.append(g)
    w = SL.lathe('Tumbler Drink', [(0, 0.006), (0.027, 0.006), (0.032, 0.035), (0.0, 0.035)], M['amber'], seg=20); w.location = (x, y, z); STAGE.append(w)
def silver_tray(x, y, z):
    t = SL.lathe('Tray', [(0, 0), (0.15, 0), (0.158, 0.014), (0.168, 0.022), (0.158, 0.02), (0.15, 0.008), (0.0, 0.008)], M['silver'], seg=40); t.location = (x, y, z); STAGE.append(t)
    decanter(x - 0.03, y + 0.015, z + 0.008); tumbler(x + 0.08, y - 0.04, z + 0.008); tumbler(x + 0.06, y + 0.07, z + 0.008)
def tea_cup(x, y, z):
    s = SL.lathe('Saucer', [(0, 0), (0.05, 0), (0.075, 0.012), (0.0, 0.006)], M['porcelain'], seg=28)
    c = SL.lathe('Cup', [(0, 0.008), (0.026, 0.008), (0.038, 0.055), (0.04, 0.058), (0.036, 0.058), (0.0, 0.015)], M['porcelain'], seg=24)
    t = SL.lathe('Tea', [(0, 0.045), (0.036, 0.045), (0.0, 0.045)], M['tea'], seg=20)
    h = SL.tube('Handle', [(0.038, 0, 0.05), (0.058, 0, 0.048), (0.06, 0, 0.032), (0.04, 0, 0.022)], [0.005] * 4, M['porcelain'], seg=6)
    for o in (s, c, t, h): o.location = (x, y, z); STAGE.append(o)
def newspaper(loc, rz, w=0.40, d=0.28):
    n = SL.img('news', np.clip(0.80 + 0.12 * np.sin(np.mgrid[0:128, 0:256][0] * 1.4) * (0.5 + 0.5 * np.sin(np.mgrid[0:128, 0:256][1] * 0.15)) + 0.04 * rng.normal(0, 1, (128, 256)), 0, 1)[..., None].repeat(3, 2), TMP)
    m = SL.mat('Newspaper', (0.8, 0.78, 0.72), 0.95, image=n)
    o = box('Newspaper', (0, 0, 0), (w, d, 0.01), m, bevel=0.002); o.rotation_euler.z = rz; o.location = loc; STAGE.append(o)
    f = box('Fold', (0, 0, 0), (w, 0.004, 0.02), M['paper']); f.rotation_euler.z = rz; f.location = Vector(loc) + Vector((0, 0, 0.006)); STAGE.append(f)
def sleeve_mat(name, c1, c2, seed):
    S = 256; y, x = np.mgrid[0:S, 0:S] / S; r = np.hypot(x - 0.5, y - 0.45)
    rgb = np.ones((S, S, 3)) * np.array(c1)
    rgb = np.where(((r > 0.18) & (r < 0.26))[..., None], np.array(c2), rgb); rgb = np.where((r < 0.12)[..., None], np.array(c2) * 0.6, rgb)
    rgb = np.where(((y > 0.80) & (y < 0.84) & (x > 0.12) & (x < 0.88))[..., None], np.array(c2), rgb); rgb = np.where(((y > 0.88) & (y < 0.905) & (x > 0.12) & (x < 0.6))[..., None], np.array(c2) * 0.8, rgb)
    rgb *= (0.94 + 0.06 * np.random.default_rng(seed).random((S, S))[..., None])
    return SL.mat(name, c1, 0.7, image=SL.img(name + '_col', np.clip(rgb, 0, 1), TMP))
def disc_mat():
    S = 512; y, x = np.mgrid[0:S, 0:S] / S; r = np.hypot(x - 0.5, y - 0.5) * 2
    grooves = 0.5 + 0.5 * np.sin(r * 420); face = 0.03 + 0.03 * grooves
    rgb = np.ones((S, S, 3)) * face[..., None]; lab = r < 0.34
    rgb = np.where(lab[..., None], np.array([0.62, 0.12, 0.08]), rgb); rgb = np.where(((r < 0.30) & (r > 0.26))[..., None], np.array([0.9, 0.8, 0.5]), rgb); rgb = np.where((r < 0.04)[..., None], np.array([0.1, 0.1, 0.1]), rgb)
    return SL.mat('Vinyl Disc', (0.02, 0.02, 0.02), 0.22, image=SL.img('disc_col', np.clip(rgb, 0, 1), TMP), normal=SL.normal_img('disc_nor', np.clip(0.5 + 0.35 * grooves * (r > 0.36) * (r < 0.98), 0, 1), TMP, 2.0), nstrength=0.7)
M['disc'] = disc_mat()
M['sleeve1'] = sleeve_mat('Sleeve A', (0.55, 0.30, 0.10), (0.92, 0.82, 0.55), 4); M['sleeve2'] = sleeve_mat('Sleeve B', (0.10, 0.20, 0.26), (0.88, 0.62, 0.30), 5); M['sleeve3'] = sleeve_mat('Sleeve C', (0.80, 0.74, 0.60), (0.25, 0.12, 0.10), 6)
def vinyl(x, y, z):
    """Three record sleeves leaning against the wall (printed covers) and a record half drawn out of the front one."""
    for k, (dx, dy, m) in enumerate(((0.0, 0.02, 'sleeve3'), (-0.014, -0.03, 'sleeve2'), (-0.028, 0.0, 'sleeve1'))):
        sl = box('Sleeve', (x + dx, y + dy, z + 0.158), (0.005, 0.31, 0.31), M[m], bevel=0.001); STAGE.append(sl)
    disc = cyl('Disc', (x - 0.034, y + 0.03, z + 0.168 + 0.07), 0.15, 0.003, M['disc'], rot=(0, math.pi / 2, 0), seg=64); STAGE.append(disc)

def pattern_mat(name, base, motif, k=5):
    S = 512; y, x = np.mgrid[0:S, 0:S] / S
    line = (np.abs(((x + y) * k) % 1 - 0.5) < 0.035) | (np.abs(((x - y) * k) % 1 - 0.5) < 0.035)
    dots = (np.abs((x * k) % 1 - 0.5) < 0.06) & (np.abs((y * k) % 1 - 0.5) < 0.06)
    weave = 0.88 + 0.12 * np.sin(x * S * 0.95) * np.sin(y * S * 0.95)
    nz = 0.94 + 0.06 * noise(S, S, 21, 2)
    rgb = np.where((line | dots)[..., None], np.array(motif), np.array(base)) * (weave * nz)[..., None]
    hgt = 0.5 + 0.3 * (weave - 0.88) / 0.12 + 0.25 * (line | dots)
    return SL.mat(name, base, 0.85, image=SL.img(name + '_col', np.clip(rgb, 0, 1), TMP), normal=SL.normal_img(name + '_nor', np.clip(hgt, 0, 1), TMP, 3.0), nstrength=1.0, sheen=0.5)
M['pipe_teal'] = mat('Piping Teal', (0.04, 0.2, 0.22, 1), 0.8); M['pipe_ochre'] = mat('Piping Ochre', (0.45, 0.28, 0.07, 1), 0.8)
M['teal2'] = pattern_mat('Teal Cushion', (0.05, 0.27, 0.29), (0.78, 0.62, 0.28))
M['ochre2'] = pattern_mat('Ochre Cushion', (0.60, 0.40, 0.10), (0.25, 0.10, 0.05))

def pillow_mesh(name, centre, normal, up, W, Hh, T, m, n=22):
    """A plump scatter cushion: a domed top and bottom meeting at pinched seams, a dimple at the middle, piping round the edge."""
    nrm = Vector(normal).normalized(); up = Vector(up).normalized(); right = up.cross(nrm).normalized(); up = nrm.cross(right).normalized(); c = Vector(centre)
    prof = lambda u: max(0.0, 1 - u * u) ** 0.55
    V, F, UV = [], [], []
    for side in (1, -1):
        base = len(V)
        for j in range(n + 1):
            for i in range(n + 1):
                u = i / n * 2 - 1; v = j / n * 2 - 1
                tt = T / 2 * prof(u) * prof(v) * (1 - 0.22 * math.exp(-(u * u + v * v) / 0.03))
                V.append(tuple(c + right * (u * W / 2) + up * (v * Hh / 2) + nrm * (side * tt))); UV.append((u * W / 2 / 0.3 + 0.5, v * Hh / 2 / 0.3 + 0.5))
        for j in range(n):
            for i in range(n):
                a_ = base + j * (n + 1) + i; b_ = a_ + 1; c_ = a_ + n + 2; d_ = a_ + n + 1
                F.append((a_, b_, c_, d_) if side == 1 else (a_, d_, c_, b_))
    o = SL.mesh_obj(name, V, F, m, UV)
    bm = bmesh.new(); bm.from_mesh(o.data); bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5); bmesh.ops.recalc_face_normals(bm, faces=bm.faces); bm.to_mesh(o.data); bm.free(); o.data.update()
    path = [(-1 + 2 * k / n, -1) for k in range(n)] + [(1, -1 + 2 * k / n) for k in range(n)] + [(1 - 2 * k / n, 1) for k in range(n)] + [(-1, 1 - 2 * k / n) for k in range(n + 1)]
    pts = [tuple(c + right * (u * W / 2) + up * (v * Hh / 2)) for u, v in path]
    pipe = SL.tube(name + ' Piping', pts, [0.008] * len(pts), M['pipe_' + ('teal' if 'Teal' in name else 'ochre')], seg=6)
    STAGE.extend([o, pipe]); return o

def lean(deg, along):
    """(normal, up) of a cushion leaning back by deg, facing along = a unit x/y vector pointing into the room."""
    a = math.radians(deg); ax, ay = along
    return ((ax * math.cos(a), ay * math.cos(a), math.sin(a)), (-ax * math.sin(a), -ay * math.sin(a), math.cos(a)))

def candlestick(x, y, z):
    b = SL.lathe('Candlestick', [(0, 0), (0.04, 0), (0.045, 0.01), (0.012, 0.03), (0.012, 0.09), (0.028, 0.105), (0.0, 0.105)], M['brass'], seg=24); b.location = (x, y, z)
    c = cyl('Candle', (x, y, z + 0.105 + 0.05), 0.014, 0.10, M['porcelain'], seg=14); fl = sphere('Flame', (x, y, z + 0.215), 0.009, M['glow'], 6); STAGE.extend([b, c, fl])

LAMP_PTS = []                                        # (the brass lamps went: Lexton, the floor lamps and the globe lamp light the room now)
stack(2.28, 1.985, 0.552, [(0.15, 0.22, 0.040, 'cover', 0.1), (0.14, 0.21, 0.030, 'cover2', -0.15), (0.13, 0.19, 0.035, 'cover3', 0.2)])
vinyl(2.555, 1.86, 0.552)
stack(0.15, 0.04, 0.359, [(0.24, 0.17, 0.035, 'cover2', 0.2), (0.22, 0.16, 0.03, 'cover', -0.1)])
stack(-1.20, 1.86, 0.82, [(0.26, 0.19, 0.040, 'cover3', 0.15), (0.24, 0.18, 0.030, 'cover', -0.1), (0.22, 0.17, 0.035, 'cover2', 0.2)])
candlestick(-1.20, 1.86, 0.82 + 0.105)
newspaper((1.8, 0.25, 0.478), math.radians(70)); newspaper((1.85, -1.45, 0.478), math.radians(-15), 0.36, 0.26)
n1, u1 = lean(10, (-1, 0)); n2, u2 = lean(10, (0, 1))
pillow_mesh('Cushion Teal', (2.02, 1.05, 0.70), n1, u1, 0.46, 0.44, 0.19, M['teal2'])
pillow_mesh('Cushion Ochre', (2.02, -0.10, 0.70), n1, u1, 0.40, 0.40, 0.17, M['ochre2'])
pillow_mesh('Cushion Teal 2', (1.45, -1.64, 0.71), n2, u2, 0.46, 0.44, 0.19, M['teal2'])
pillow_mesh('Cushion Ochre 2', (2.15, -1.64, 0.70), n2, u2, 0.40, 0.40, 0.17, M['ochre2'])

# ---------------------------------------------------------------- his layout: the furniture (and what stands on it) moves to where he put it in admin
from mathutils import Matrix
_si = json.load(open(os.path.join(OUT, 'split_info.json'), encoding='utf8')); _pls = json.load(open(os.path.join(OUT, 'placements.json'), encoding='utf8'))['staging']
_order = ['LM_Sofa', 'LM_Loveseat', 'LM_Armchair1', 'LM_Armchair2', 'LM_Sideboard', 'LM_SideTableA', 'LM_SideTableB']
def _bbox(o):
    cs = [o.matrix_world @ Vector(c) for c in o.bound_box]
    return Vector([min(c[i] for c in cs) for i in range(3)]), Vector([max(c[i] for c in cs) for i in range(3)])
_boxes = {n: _bbox(bpy.data.objects[n]) for n in _order}; _groups = {n: [bpy.data.objects[n]] for n in _order}
for o in list(bpy.data.objects):
    if o.type != 'MESH' or not o.name.startswith(('Cushion', 'Newspaper', 'Fold', 'Book', 'Candle', 'Flame', 'Sleeve', 'Disc')): continue
    mn, mx = _bbox(o); c = (mn + mx) / 2; best = None
    for n, (fmn, fmx) in _boxes.items():
        if fmn.x - 0.12 <= c.x <= fmx.x + 0.12 and fmn.y - 0.12 <= c.y <= fmx.y + 0.12 and fmn.z - 0.05 <= c.z <= fmx.z + 0.8:
            area_ = (fmx.x - fmn.x) * (fmx.y - fmn.y)
            if best is None or area_ < best[0]: best = (area_, n)
    if best: _groups[best[1]].append(o)
for k, n in enumerate(_order):
    old, new, phi = _si[k]['pos'], _pls[k]['pos'], _pls[k].get('rotY', 0.0)
    oc = Vector((old[0], -old[2], 0)); nc = Vector((new[0], -new[2], 0))
    Mx = Matrix.Translation(nc) @ Matrix.Rotation(phi, 4, 'Z') @ Matrix.Translation(-oc)
    for o in _groups[n]: o.matrix_world = Mx @ o.matrix_world
    print('MOVED', n, [round(v, 2) for v in oc[:2]], '->', [round(v, 2) for v in nc[:2]], 'turn', round(phi, 2), 'with', len(_groups[n]) - 1, 'extras')
bpy.context.view_layer.update()
REMOVED = []
for k, n in enumerate(_order):                     # a piece he dragged out of the room (he did not want it): gone from the build
    nc = _pls[k]['pos']
    if not (X0 < nc[0] < X1 and Y0 < -nc[2] < Y1):
        for o in _groups[n]:
            if o in LMX: LMX.remove(o)
            if o in STAGE: STAGE.remove(o)
            bpy.data.objects.remove(o)
        REMOVED.append(n); print('REMOVED', n)

# ---------------------------------------------------------------- raised wall panels (picture-frame mouldings) in the ceiling's colour
PZ0, PZ1 = 0.90, 2.45
def _strip(parts, axis, w0, s, a_, b_, za, zb, proj):
    if axis == 'y': parts.append(box('Pnl', ((a_ + b_) / 2, w0 + s * proj / 2, (za + zb) / 2), (b_ - a_, proj, zb - za), M['plaster'], bevel=0.004))
    else: parts.append(box('Pnl', (w0 + s * proj / 2, (a_ + b_) / 2, (za + zb) / 2), (proj, b_ - a_, zb - za), M['plaster'], bevel=0.004))
def _frame(parts, axis, w0, s, a_, b_, z0, z1, tt, proj):
    _strip(parts, axis, w0, s, a_, b_, z0, z0 + tt, proj); _strip(parts, axis, w0, s, a_, b_, z1 - tt, z1, proj)
    _strip(parts, axis, w0, s, a_, a_ + tt, z0 + tt, z1 - tt, proj); _strip(parts, axis, w0, s, b_ - tt, b_, z0 + tt, z1 - tt, proj)
PANELS = [('y', Y1, -1, -1.95, -0.45), ('y', Y1, -1, -0.25, 0.75), ('y', Y1, -1, 0.95, 1.95), ('y', Y0, 1, 0.95, 2.25), ('x', X0, 1, -1.65, -0.75), ('x', X1, -1, -1.85, -0.75)]
_pp = []
for axis, w0, s, a_, b_ in PANELS:
    _frame(_pp, axis, w0, s, a_, b_, PZ0, PZ1, 0.055, 0.024); _frame(_pp, axis, w0, s, a_ + 0.10, b_ - 0.10, PZ0 + 0.10, PZ1 - 0.10, 0.024, 0.013)
panels = join(_pp, 'LM_Panels'); make_uv(panels, 1.0); lm(panels); LMRES['LM_Panels'] = 2048

# ---------------------------------------------------------------- a stepped false ceiling: dropped frame + thin lip (baked), cove glow, recessed downlights
IN_, FW_, DROP_ = 0.19, 0.50, 0.16
xa_, xb_, ya_, yb_ = X0 + IN_, X1 - IN_, Y0 + IN_, Y1 - IN_; zc_ = H - DROP_ / 2
_dp = [box('DropL', ((xa_ + xa_ + FW_) / 2, 0, zc_), (FW_, yb_ - ya_, DROP_), M['plaster'], 0.004), box('DropR', ((xb_ + xb_ - FW_) / 2, 0, zc_), (FW_, yb_ - ya_, DROP_), M['plaster'], 0.004),
       box('DropF', (0, (ya_ + ya_ + FW_) / 2, zc_), (xb_ - xa_ - 2 * FW_, FW_, DROP_), M['plaster'], 0.004), box('DropB', (0, (yb_ + yb_ - FW_) / 2, zc_), (xb_ - xa_ - 2 * FW_, FW_, DROP_), M['plaster'], 0.004)]
LIP_, LD_ = 0.07, 0.045; zl_ = H - DROP_ - LD_ / 2
_dp += [box('LipL', (xa_ + FW_ + LIP_ / 2, 0, zl_), (LIP_, yb_ - ya_ - 2 * FW_ + 2 * LIP_, LD_), M['plaster'], 0.003), box('LipR', (xb_ - FW_ - LIP_ / 2, 0, zl_), (LIP_, yb_ - ya_ - 2 * FW_ + 2 * LIP_, LD_), M['plaster'], 0.003),
        box('LipF', (0, ya_ + FW_ + LIP_ / 2, zl_), (xb_ - xa_ - 2 * FW_, LIP_, LD_), M['plaster'], 0.003), box('LipB', (0, yb_ - FW_ - LIP_ / 2, zl_), (xb_ - xa_ - 2 * FW_, LIP_, LD_), M['plaster'], 0.003)]
dropc = join(_dp, 'LM_DropCeiling'); make_uv(dropc, 1.5); lm(dropc); LMRES['LM_DropCeiling'] = 2048
G_ = 0.025; zg_ = H - 0.012; XI, YI = xb_ - FW_ - LIP_ - 0.02, yb_ - FW_ - LIP_ - 0.02     # the glow lines sit just inside the lip, on the raised ceiling
box('Cove Glow L', (-XI, 0, zg_), (G_, 2 * YI - 0.1, 0.012), M['glow']); box('Cove Glow R', (XI, 0, zg_), (G_, 2 * YI - 0.1, 0.012), M['glow'])
box('Cove Glow F', (0, -YI, zg_), (2 * XI - 0.1, G_, 0.012), M['glow']); box('Cove Glow B', (0, YI, zg_), (2 * XI - 0.1, G_, 0.012), M['glow'])
M['dl'] = mat('Downlight Lens', (0.02, 0.02, 0.02, 1), 0.3, emit=((1.0, 0.82, 0.55, 1), 8.0)); M['dltrim'] = mat('Downlight Trim', (0.10, 0.08, 0.06, 1), 0.4)
DL_SPOTS = [(xa_ + FW_ / 2, y_) for y_ in (-1.2, 0.0, 1.2)] + [(xb_ - FW_ / 2, y_) for y_ in (-1.2, 0.0, 1.2)] + [(x_, ya_ + FW_ / 2) for x_ in (-0.9, 0.9)] + [(x_, yb_ - FW_ / 2) for x_ in (-0.9, 0.9)]
for _i, (x_, y_) in enumerate(DL_SPOTS):
    cyl('DLTrim%d' % _i, (x_, y_, H - DROP_ - 0.004), 0.075, 0.008, M['dltrim']); cyl('DLLens%d' % _i, (x_, y_, H - DROP_ - 0.009), 0.052, 0.006, M['dl'])
for o in STAGE: o.select_set(False)
