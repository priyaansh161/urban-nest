# Sunday Bedroom staging (Nov 2026), after its Gemini cover: breakfast tray on the bed (coffee with a teaspoon and
# sugar, a croissant, jam, a linen napkin and butter knife, a bud vase), slippers on the rug, a snake plant in a
# ribbed ceramic pot on a walnut stand by the right nightstand. No dots. (The floor vase became a product, the
# Qutub planter; the dresser is full, so nothing more goes on it.) Called by build_bedroom_v1.py once the
# bedding is draped (the tray sits on the throw by ray cast). Room metres: x -2.1..2.1, y -1.9..1.9, z up.
import bpy, math, os, random, sys
import numpy as np
from mathutils import Vector
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from staging_lib import img, mat, lathe, box, cyl, tube, join, place, mesh_obj, leaf_strip, disc_leaf, noise_img, blur


# ---- the snake plant (Sansevieria 'Laurentii'), detailed 3 Nov 2026 at his ask: the first leaves were flat,
# paper-thin strips with smooth wave bands. A real one has thick stiff leaves, a little channelled down the middle,
# jagged grey-green "tiger" bands across a deep green, a broad yellow margin, a pale foot where it leaves the soil
# and a dry brown point; and they grow as fans of three or four, the outer leaves shorter, wrapped at the base.
def snake_material(T):
    rng = np.random.default_rng(31)
    H, W = 1024, 128
    v = np.linspace(0, 1, H)[:, None]; u = np.linspace(0, 1, W)[None, :]
    wob = blur(rng.normal(0, 1, (H, W)), 14); wob /= np.abs(wob).max()
    zig = 0.003 * np.sin(u * 2 * np.pi * 3 + v * 40) + 0.022 * wob                    # bands waver irregularly across the leaf
    phase = (v + zig) * 34 + 0.35 * blur(rng.normal(0, 1, (H, 1)), 20).repeat(W, 1) / 0.05
    band = np.clip((np.sin(phase * 2 * np.pi / 2) - 0.25) * 2.2, 0, 1) * (0.55 + 0.45 * np.abs(blur(rng.normal(0, 1, (H, W)), 3)) / 0.5)
    band = np.clip(band, 0, 1)
    dark, light = np.array([0.09, 0.21, 0.10]), np.array([0.36, 0.45, 0.33])
    rgb = dark + (light - dark) * band[..., None] * 0.65
    rgb *= (0.92 + 0.08 * (blur(rng.normal(0, 1, (H, W)), 10) / 0.1).clip(-1, 1))[..., None]
    m = np.abs(u - 0.5) * 2                                                             # 0 at the middle, 1 at the edge
    rim = np.clip((m - 0.89) / 0.03, 0, 1)                                              # yellow margin, a dark line inside it
    line = np.exp(-((m - 0.88) / 0.012) ** 2)
    rgb = rgb * (1 - 0.5 * line[..., None])
    rgb = rgb * (1 - rim[..., None]) + np.array([0.86, 0.80, 0.34]) * rim[..., None] * (0.9 + 0.1 * wob[..., None])
    foot = np.clip((0.07 - v) / 0.07, 0, 1)                                             # pale where it leaves the soil
    rgb = rgb * (1 - foot[..., None] * 0.6) + np.array([0.62, 0.66, 0.48]) * foot[..., None] * 0.6
    tip = np.clip((v - 0.965) / 0.025, 0, 1)                                            # the dry brown point
    rgb = rgb * (1 - tip[..., None]) + np.array([0.46, 0.36, 0.22]) * tip[..., None]
    return mat('Stg Snake Leaf', (0.2, 0.35, 0.15), 0.38, image=img('stg_snake', np.clip(rgb[::-1], 0, 1), T))   # row 0 = the tip


def snake_leaves(R, z0, m):
    """Fans of stiff, thick, channelled sword leaves on a pot's soil at height z0 (pot centre at x = y = 0)."""
    V, F, UV = [], [], []
    NA, NL = 7, 18                                                                      # points across each face, rows along
    def leaf(base, ang, lean, L, Wd, bend, twist):
        up = Vector((math.cos(ang) * lean, math.sin(ang) * lean, 1)).normalized()
        out = Vector((math.cos(ang), math.sin(ang), 0))                                  # the leaf's face looks out of its fan
        side = up.cross(out).normalized(); nrm = side.cross(up).normalized()
        o = len(V)
        for i in range(NL + 1):
            t = i / NL
            w = Wd * (0.55 + 0.45 * math.sin(math.pi * min(1.0, 0.18 + t * 0.9))) * (1 - t ** 3.2) ** 0.9   # narrow foot, widest ~40 %, a long point
            th = 0.0055 * (1 - t) ** 0.6 + 0.0008
            c = base + up * L * t + nrm * bend * L * t * t                               # curves gently outward
            tw = twist * t; sd = side * math.cos(tw) + nrm * math.sin(tw); nm = nrm * math.cos(tw) - side * math.sin(tw)
            ring = []
            for j in range(NA):                                                          # front face, edge to edge
                s = -1 + 2 * j / (NA - 1); arc = math.sqrt(max(0.0, 1 - s * s))
                ring.append((c + sd * s * w / 2 - nm * 0.18 * w * (1 - s * s) + nm * th / 2 * arc, (j / (NA - 1), t)))
            for j in range(NA - 2, 0, -1):                                               # back face, back again
                s = -1 + 2 * j / (NA - 1); arc = math.sqrt(max(0.0, 1 - s * s))
                ring.append((c + sd * s * w / 2 - nm * 0.18 * w * (1 - s * s) - nm * th / 2 * arc, (j / (NA - 1), t)))
            for p, uv in ring: V.append(p); UV.append(uv)
        n = 2 * NA - 2
        for i in range(NL):
            for j in range(n):
                a, b = o + i * n + j, o + i * n + (j + 1) % n
                F.append((a, b, b + n, a + n))
    for k in range(4):                                                                  # four fans round the pot
        fa = 2 * math.pi * k / 4 + R.uniform(-0.3, 0.3); fr = R.uniform(0.025, 0.055)
        fc = Vector((fr * math.cos(fa), fr * math.sin(fa), z0 - 0.01))
        tall = R.uniform(0.55, 0.72)
        for j in range(R.choice((3, 4))):
            a = fa + R.uniform(-0.5, 0.5) + j * 2.1
            L = tall * (1.0 if j == 0 else R.uniform(0.55, 0.85))
            leaf(fc + Vector((R.uniform(-0.008, 0.008), R.uniform(-0.008, 0.008), 0)), a, R.uniform(0.04, 0.12) + 0.05 * j,
                 L, R.uniform(0.060, 0.080), R.uniform(0.02, 0.08), R.uniform(-0.35, 0.35))
    o = mesh_obj('Snake Leaves', V, F, m, UV)
    for p in o.data.polygons: p.use_smooth = True
    return o


def build(OUT):
    T = os.path.join(OUT, 'textures', 'staging'); os.makedirs(T, exist_ok=True)
    scene = bpy.context.scene
    made = []
    R = random.Random(11)

    # ---- materials
    gy = np.linspace(0, 1, 256)[:, None]; gx = np.linspace(0, 1, 512)[None, :]
    grain = 0.5 + 0.5 * np.sin(gy * 140 + 6 * np.sin(gx * 9 + gy * 20) + 2 * np.sin(gx * 31))
    oak_rgb = np.stack([0.66 - 0.07 * grain, 0.48 - 0.06 * grain, 0.31 - 0.05 * grain], -1)
    oak = mat('Stg Oak', (0.62, 0.45, 0.29), 0.45, image=img('stg_oak', np.clip(oak_rgb, 0, 1), T))
    porcelain = mat('Stg Porcelain', (0.93, 0.92, 0.89), 0.18)
    coffee = mat('Stg Coffee', (0.17, 0.09, 0.05), 0.08)
    linen = mat('Stg Linen Napkin', (0.86, 0.82, 0.74), 0.95, sheen=0.3)
    steel = mat('Stg Cutlery', (0.80, 0.80, 0.78), 0.22, metal=1.0)
    jam = mat('Stg Jam', (0.42, 0.04, 0.06), 0.12)
    sugar = mat('Stg Sugar', (0.95, 0.94, 0.92), 0.75)
    crema = mat('Stg Crema', (0.55, 0.36, 0.20), 0.3)
    v = np.linspace(0, 1, 128)[:, None]; u = np.linspace(0, 1, 256)[None, :]
    band = 0.5 + 0.5 * np.cos(u * 2 * math.pi * 7)                       # seven rolled layers along the croissant
    cr = np.stack([0.78 - 0.30 * band, 0.52 - 0.26 * band, 0.20 - 0.12 * band], -1) * (0.85 + 0.15 * np.sin(v * math.pi))[..., None]
    croissant_m = mat('Stg Croissant', (0.7, 0.45, 0.2), 0.55, image=img('stg_croissant', np.clip(cr, 0, 1), T))
    glass = mat('Stg Ceramic', (0.80, 0.84, 0.78), 0.35)            # opaque: transmission glass reads black in the viewer
    stem_m = mat('Stg Stem', (0.25, 0.38, 0.18), 0.6)
    petal = mat('Stg Petal', (0.96, 0.95, 0.92), 0.5)
    plush = mat('Stg Plush', (0.46, 0.39, 0.31), 1.0, sheen=0.1)
    sole_m = mat('Stg Sole', (0.45, 0.40, 0.35), 0.9)
    insole = mat('Stg Insole', (0.86, 0.80, 0.71), 1.0, sheen=0.3)
    soil = mat('Stg Soil', (0.12, 0.08, 0.06), 1.0)
    ceramic_pot = mat('Stg Ribbed Ceramic', (0.88, 0.85, 0.79), 0.45, image=img('stg_pot_glaze', noise_img(64, 256, (0.89, 0.86, 0.80), 0.02, 4, 8), T))
    walnut = mat('Stg Walnut', (0.25, 0.15, 0.09), 0.5)
    pebble = [mat('Stg Pebble Grey', (0.55, 0.53, 0.50), 0.7), mat('Stg Pebble Light', (0.80, 0.78, 0.74), 0.7)]
    snake_m = snake_material(T)

    # ---- breakfast tray on the bed, cup + saucer, croissant on a plate, bud vase with one white flower
    dg = bpy.context.evaluated_depsgraph_get()
    TX, TY, TR = 0.30, 0.42, -0.18
    zs = []
    for dx in (-0.2, 0.2):
        for dy in (-0.12, 0.12):
            p = Vector((TX + dx * math.cos(TR) - dy * math.sin(TR), TY + dx * math.sin(TR) + dy * math.cos(TR), 2.0))
            hit, loc, *_ = scene.ray_cast(dg, p, Vector((0, 0, -1)))
            if hit: zs.append(loc.z)
    tz = (max(zs) if zs else 0.62) + 0.002
    tr = [box('Tray Base', (0, 0, 0.006), (0.48, 0.32, 0.012), oak, bevel=0.003)]
    for sx in (-1, 1):
        tr.append(box('Tray Side', (sx * 0.233, 0, 0.035), (0.014, 0.32, 0.058), oak, bevel=0.004))
        tr.append(box('Tray Grip', (sx * 0.233, 0, 0.044), (0.0155, 0.085, 0.017), mat('Stg Grip', (0.16, 0.11, 0.07), 0.8), bevel=0.006, segs=4))   # the cut-out handle, its end grain darker
    for sy in (-1, 1): tr.append(box('Tray Side', (0, sy * 0.153, 0.025), (0.48, 0.014, 0.038), oak, bevel=0.004))
    saucer = lathe('Saucer', [(0.0, 0.012), (0.05, 0.012), (0.072, 0.02), (0.075, 0.024), (0.07, 0.024), (0.05, 0.017), (0.0, 0.017)], porcelain)
    saucer.location = (-0.11, 0.04, 0)
    cup = lathe('Cup', [(0.0, 0.017), (0.026, 0.017), (0.038, 0.03), (0.043, 0.075), (0.044, 0.08), (0.04, 0.08), (0.037, 0.035), (0.0, 0.032)], porcelain)
    cup.location = (-0.11, 0.04, 0)
    handle = tube('Cup Handle', [(-0.11 + 0.042, 0.04, 0.068), (-0.11 + 0.066, 0.04, 0.064), (-0.11 + 0.068, 0.04, 0.045), (-0.11 + 0.042, 0.04, 0.038)], [0.005] * 4, porcelain, 8)
    cof = cyl('Coffee', (-0.11, 0.04, 0.071), 0.039, 0.002, coffee, 32)
    foam = cyl('Crema', (-0.11, 0.04, 0.0725), 0.03, 0.001, crema, 24)
    plate = lathe('Plate', [(0.0, 0.012), (0.06, 0.012), (0.095, 0.022), (0.1, 0.026), (0.094, 0.026), (0.06, 0.017), (0.0, 0.017)], porcelain)
    plate.location = (0.09, -0.02, 0)
    # croissant: a crescent tube that is fat in the middle and rolled in seven ridges
    V, F, UV = [], [], []
    ns, nr = 90, 18
    for i in range(ns + 1):
        t = i / ns; ang = math.radians(-70 + 140 * t)
        c = Vector((0.09 + 0.075 * math.sin(ang), -0.02 - 0.05 + 0.075 * (1 - math.cos(ang)) * 0.9, 0.034))
        rad = 0.008 + 0.024 * math.sin(math.pi * t) ** 0.8
        rad *= 1 + 0.09 * (0.5 + 0.5 * math.cos(t * 2 * math.pi * 7)) ** 2.5 - 0.03   # rounded rolls with soft creases between
        tang = Vector((math.cos(ang), math.sin(ang) * 0.9, 0)).normalized(); side = Vector((0, 0, 1)).cross(tang)
        for k in range(nr):
            a = 2 * math.pi * k / nr
            V.append(c + rad * (math.cos(a) * side * 1.15 + math.sin(a) * Vector((0, 0, 0.75)))); UV.append((t, k / nr))
    for i in range(ns):
        for k in range(nr): F.append((i * nr + k, i * nr + (k + 1) % nr, (i + 1) * nr + (k + 1) % nr, (i + 1) * nr + k))
    croissant = mesh_obj('Croissant', V, F, croissant_m, UV)
    for o in (croissant,):
        for vv in o.data.vertices: vv.co.z = max(vv.co.z, 0.0175)          # flat underside on the plate
    bud = lathe('Bud Vase', [(0.0, 0.012), (0.022, 0.012), (0.026, 0.04), (0.018, 0.09), (0.009, 0.115), (0.011, 0.125), (0.007, 0.125), (0.005, 0.11), (0.0, 0.11)], glass)
    bud.location = (0.19, 0.105, 0)
    stem = tube('Flower Stem', [(0.19, 0.105, 0.03), (0.192, 0.106, 0.10), (0.196, 0.108, 0.15), (0.202, 0.111, 0.185)], [0.0018] * 4, stem_m, 6)
    V, F, UV = [], [], []
    for k in range(6):
        a = 2 * math.pi * k / 6
        leaf_strip(V, F, UV, (0.202, 0.111, 0.185), (math.cos(a) * 0.6, math.sin(a) * 0.6, 0.8), (-math.sin(a), math.cos(a), 0), 0.03, 0.022, n=5, droop=0.5)
    petals = mesh_obj('Flower', V, F, petal, UV)
    extra = []
    nap = box('Napkin', (-0.12, -0.095, 0.0175), (0.13, 0.085, 0.008), linen, bevel=0.003, segs=3)
    for vv in nap.data.vertices: vv.co.z += 0.0015 * math.sin(vv.co.x * 60) * math.cos(vv.co.y * 50)     # soft, not boxy
    extra.append(nap)
    extra.append(box('Napkin Fold', (-0.12, -0.06, 0.0225), (0.13, 0.012, 0.004), linen, bevel=0.0018, segs=3))
    extra.append(box('Knife Blade', (-0.108, -0.095, 0.0235), (0.085, 0.013, 0.0016), steel, bevel=0.0006))
    extra.append(box('Knife Handle', (-0.166, -0.095, 0.0245), (0.07, 0.011, 0.006), steel, bevel=0.0025))
    spoon = [box('Spoon Handle', (-0.11 + 0.035, 0.04 - 0.045, 0.0255), (0.07, 0.006, 0.002), steel, bevel=0.0008)]
    bowl = lathe('Spoon Bowl', [(0.0, 0.0), (0.009, 0.0025), (0.011, 0.004), (0.0, 0.0035)], steel, 16); bowl.scale = (1.4, 1.0, 1.0); bowl.location = (-0.11 + 0.082, 0.04 - 0.045, 0.0235)
    spoon.append(bowl)
    for o in spoon: o.rotation_euler.z = 0.0
    extra += spoon
    ram = lathe('Ramekin', [(0.0, 0.012), (0.026, 0.012), (0.03, 0.016), (0.031, 0.042), (0.028, 0.042), (0.026, 0.017), (0.0, 0.017)], porcelain, 32)
    ram.location = (-0.005, 0.11, 0); extra.append(ram)
    extra.append(cyl('Jam', (-0.005, 0.11, 0.033), 0.026, 0.004, jam, 28))
    extra.append(box('Jam Spoon', (-0.005 + 0.012, 0.11, 0.045), (0.06, 0.005, 0.0018), steel, bevel=0.0007))
    for i, (sx, sy) in enumerate(((-0.165, 0.035), (-0.155, 0.05))):
        c = box('Sugar Cube', (sx, sy, 0.0275), (0.012, 0.012, 0.012), sugar, bevel=0.0015); c.rotation_euler.z = 0.4 * i; extra.append(c)
    for i in range(9):
        extra.append(box('Crumb', (0.09 + R.uniform(-0.09, 0.09), -0.02 + R.uniform(-0.08, 0.08), 0.0185 if i % 2 else 0.013),
                         (R.uniform(0.002, 0.005),) * 2 + (0.002,), croissant_m, bevel=0.0007))
    tray = join(tr + [saucer, cup, handle, cof, foam, plate, croissant, bud, stem, petals] + extra, 'Staging Breakfast Tray')
    made.append(place(tray, (TX, TY, tz), TR))

    # ---- slippers on the rug in front of the bed
    def slipper(sx):
        # a flat sole with a soft insole, and a low plush band over the front 55% (open heel)
        sole = lathe('Sole', [(0.0, 0.0), (0.046, 0.0), (0.05, 0.006), (0.05, 0.014), (0.0, 0.014)], sole_m, 40)
        ins = lathe('Insole', [(0.0, 0.014), (0.045, 0.014), (0.045, 0.02), (0.0, 0.02)], insole, 40)
        up = lathe('Upper', [(0.0, 0.014), (0.051, 0.014), (0.052, 0.028), (0.045, 0.040), (0.026, 0.047), (0.0, 0.049)], plush, 64)
        for o in (sole, ins): o.scale = (1.0, 2.5, 1.0)
        up.scale = (1.02, 2.0, 1.0); up.location = (0, 0.03, 0)
        bpy.ops.object.select_all(action='DESELECT')
        for o in (sole, ins, up): o.select_set(True)
        bpy.context.view_layer.objects.active = sole; bpy.ops.object.transform_apply(location=True, scale=True)
        import bmesh as _bm
        bm = _bm.new(); bm.from_mesh(up.data)
        _bm.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], plane_co=(0, 0.02, 0), plane_no=(0, -1, 0), clear_outer=True)   # a clean, straight opening
        bm.to_mesh(up.data); bm.free()
        md = up.modifiers.new('S', 'SOLIDIFY'); md.thickness = 0.008
        bpy.context.view_layer.objects.active = up; bpy.ops.object.modifier_apply(modifier='S')
        s = join([sole, ins, up], 'Slipper'); s.location = (sx, 0, 0); return s
    pair = join([slipper(-0.065), slipper(0.065)], 'Staging Slippers')
    made.append(place(pair, (0.42, -0.80, 0.03), math.radians(168)))

    # ---- snake plant in a ribbed ceramic pot on a walnut stand, by the right nightstand
    ZP = 0.20                                                  # the pot sits on a 20 cm walnut stand
    pot = lathe('Pot', [(0.0, ZP), (0.105, ZP), (0.118, ZP + 0.02), (0.128, ZP + 0.13), (0.125, ZP + 0.24), (0.12, ZP + 0.255), (0.108, ZP + 0.255), (0.108, ZP + 0.23), (0.0, ZP + 0.23)], ceramic_pot, 96)
    for vv in pot.data.vertices:                               # vertical ribs round the outside wall
        r = math.hypot(vv.co.x, vv.co.y)
        if r > 0.112 and ZP + 0.01 < vv.co.z < ZP + 0.245:
            k = 1 + 0.035 * max(0, math.cos(math.atan2(vv.co.y, vv.co.x) * 24)) ** 2
            vv.co.x *= k; vv.co.y *= k
    stand = [cyl('Stand Ring', (0, 0, ZP - 0.012), 0.118, 0.022, walnut, 48)]
    for k in range(3):
        a = 2 * math.pi * k / 3
        stand.append(tube('Stand Leg', [(0.095 * math.cos(a), 0.095 * math.sin(a), ZP - 0.01), (0.15 * math.cos(a), 0.15 * math.sin(a), 0.0)], [0.011, 0.007], walnut, 10))
    dirt = cyl('Soil', (0, 0, ZP + 0.232), 0.108, 0.006, soil, 32)
    peb = []
    for k in range(46):                                        # river pebbles over the soil
        rr, a = 0.1 * math.sqrt(R.random()), R.uniform(0, 2 * math.pi)
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=R.uniform(0.008, 0.014), location=(rr * math.cos(a), rr * math.sin(a), ZP + 0.238))
        o = bpy.context.object; o.scale = (1, R.uniform(0.7, 1), 0.55); o.data.materials.append(pebble[k % 2]); peb.append(o)
    leaves = snake_leaves(R, ZP + 0.23, snake_m)
    made.append(place(join([pot, dirt, leaves] + stand + peb, 'Staging Snake Plant'), (1.62, 1.62, 0), 0.4))

    for o in made: print('STAGING', o.name, sum(len(p.vertices) - 2 for p in o.data.polygons), 'tris')
    return made
