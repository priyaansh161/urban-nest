# Quiet Bath staging (Nov 2026), after its Gemini cover: folded towels and a candle on the mango-wood stool between
# the toilet and the glass, a framed abstract print above the toilet, a eucalyptus bunch hung in the shower, a
# plastic waste bin by the vanity, and the bottles and washcloth in the
# shower niche. No dots. Called by build_bath_v7.py after the placed items are in. Room metres: x -2.2..2.2,
# y -1.4..1.4 (back wall), z up.
# 2 Nov 2026 (his review of the first bake): the olive tree read as cartoonish, the woven bin as a flimsy laundry
# basket, the diffuser and the niche bottles as plain shapes, and the waffle mitt as a block. Now every surface
# carries relief (normal maps: terry loops, plastic flutes), the
# bottles have printed labels (make_staging_labels.cjs) and everything has real wall thickness. The mitt is gone.
import bpy, bmesh, math, os, random, sys
import numpy as np
from mathutils import Vector, Matrix
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from staging_lib import img, mat, lathe, box, cyl, tube, join, place, mesh_obj, disc_leaf, noise_img, normal_img, blur

Y1 = 1.4
TX = 0.10


def box_uv(o, tile, grain=0, off=(0.0, 0.0)):
    """World-scale UVs on every face (projected along its main axis), the texture's v running along `grain`
    (0 x, 1 y, 2 z) wherever that axis lies in the face: wood grain runs the length of a slat or a leg."""
    me = o.data; uv = me.uv_layers[0] if me.uv_layers else me.uv_layers.new(name='UVMap')
    for p in me.polygons:
        ax = max(range(3), key=lambda a: abs(p.normal[a])); pl = [a for a in range(3) if a != ax]
        if grain in pl: pl = [a for a in pl if a != grain] + [grain]
        for li in p.loop_indices:
            co = me.vertices[me.loops[li].vertex_index].co
            uv.data[li].uv = (co[pl[0]] / tile + off[0], co[pl[1]] / tile + off[1])
    return o


def band(name, r, z0, z1, a0, a1, m, seg=24):
    """A label: part of a cylinder (angles a0..a1, radians) from z0 to z1, the picture spread across it."""
    V, F, UV = [], [], []
    for s in range(seg + 1):
        a = a0 + (a1 - a0) * s / seg
        for z, v in ((z0, 0.0), (z1, 1.0)): V.append((r * math.cos(a), r * math.sin(a), z)); UV.append((s / seg, v))   # a0 is the viewer's left
    for s in range(seg): F.append((2 * s, 2 * s + 2, 2 * s + 3, 2 * s + 1))
    return mesh_obj(name, V, F, m, UV)


def disc(name, r, z, m, seg=32, flip=False):
    """A flat disc facing +z (or -z) with planar UVs 0..1 (the end of a towel roll)."""
    V, F, UV = [(0, 0, z)], [], [(0.5, 0.5)]
    for s in range(seg):
        a = 2 * math.pi * s / seg; V.append((r * math.cos(a), r * math.sin(a), z)); UV.append((0.5 + 0.5 * math.cos(a), 0.5 + 0.5 * math.sin(a)))
    for s in range(seg):
        f = (0, 1 + s, 1 + (s + 1) % seg); F.append(f[::-1] if flip else f)
    return mesh_obj(name, V, F, m, UV, smooth=False)


def turn(o, mtx):
    o.data.transform(mtx); o.data.update(); return o


def terry(name, base, T, rng, S=256):
    """Terry cloth: colour with soft mottling and a dense field of small loops as relief (tiles every 10 cm)."""
    loops = blur(rng.random((S, S)), 1)
    loops = (loops - loops.min()) / (loops.max() - loops.min())
    mott = blur(rng.normal(0, 1, (S, S)), 12); mott /= np.abs(mott).max()
    col = np.array(base)[None, None, :] * (0.90 + 0.10 * loops[..., None] + 0.04 * mott[..., None])
    return img(name, np.clip(col, 0, 1), T), normal_img(name + '_n', loops, T, strength=2.5)


def label_mat(name, T):
    i = bpy.data.images.load(os.path.join(T, name + '.png')); i.pack()
    return mat('Stg Label ' + name, (1, 1, 1), 0.6, image=i)


def folded_towel(x, y, z, w, d, layers, m, R, name):
    """A towel folded in thirds and in half: a stack of soft layers, each a little off true, the folds rounded."""
    out, th = [], 0.017
    for k in range(layers):
        o = box(name, (x + R.uniform(-0.004, 0.004), y + R.uniform(-0.004, 0.004), z + th * (k + 0.5)), (w - 0.004 * (k % 2), d, th), m, bevel=th * 0.48, segs=4)
        for v in o.data.vertices: v.co.z -= 0.0015 * (1 - (2 * v.co.x / w) ** 2)       # it settles a little in the middle
        box_uv(o, 0.10); out.append(o)
    return out, z + th * layers


def soft_towel(x, y, z, w, d, layers, m, R, name, lay=0.016, rz=0.0):
    """A folded towel that reads as cloth, not a board (3 Nov 2026, his note: the stacked slabs looked stiff). One
    pillowy piece: every edge rounded to nearly half its thickness, the front a full round fold, the top puffed and
    settling at the corners, a crease between the layers on the sides and back, and a little unevenness throughout."""
    h = lay * layers
    bpy.ops.mesh.primitive_cube_add(size=1); o = bpy.context.object; o.name = name
    bm = bmesh.new(); bm.from_mesh(o.data)
    bmesh.ops.subdivide_edges(bm, edges=bm.edges[:], cuts=14, use_grid_fill=True)
    bm.to_mesh(o.data); bm.free()
    a, b, c = w / 2, d / 2, h / 2
    rs = min(c * 0.92, b)                                                   # rounding: about half the thickness
    for v in o.data.vertices:
        p = Vector((v.co.x * w, v.co.y * d, v.co.z * h))
        q = Vector((max(-(a - rs), min(a - rs, p.x)), max(-(b - rs), min(b - rs, p.y)), max(-(c - rs), min(c - rs, p.z))))
        dv = p - q
        if dv.length > 1e-9: p = q + dv.normalized() * rs
        u, t = p.x / a, p.y / b                                               # -1..1 across and front to back
        top = max(0.0, (p.z + c) / h)                                         # 0 at the bottom, 1 on top
        p.z += 0.0045 * top * (1 - u * u) * (1 - 0.6 * t * t)                 # puffed on top
        p.z -= 0.003 * top * (u * u) * (t * t)                                # corners settle
        if p.y > -b + rs * 0.5:                                               # the creases between layers (not on the front fold)
            for k in range(1, layers):
                zk = -c + lay * k
                p -= Vector((math.copysign(1, p.x) if abs(p.x) > a - 0.004 else 0, 1 if p.y > b - 0.004 else 0, 0)) * 0.0022 * math.exp(-((p.z - zk) / 0.0025) ** 2)
        p += Vector((R.uniform(-1, 1), R.uniform(-1, 1), R.uniform(-1, 1))) * 0.0004
        v.co = p
    for p in o.data.polygons: p.use_smooth = True
    o.data.materials.append(m)
    o.rotation_euler.z = rz; o.location = (x, y, z + c + 0.0005)
    bpy.ops.object.select_all(action='DESELECT'); o.select_set(True); bpy.context.view_layer.objects.active = o
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    box_uv(o, 0.10)
    return o, z + h


def rolled_towel(L, r, m_body, m_end, name):
    """A rolled towel lying along y: a terry body and two spiral ends (the roll seen end on). Built along z."""
    body = lathe(name, [(0.0, 0.004), (r * 0.94, 0.0), (r, 0.006), (r, L - 0.006), (r * 0.94, L), (0.0, L - 0.004)], m_body, 40, u_scale=2 * math.pi * r / 0.10)
    for v in body.data.vertices:                                          # the loose end of the roll, a flap round it
        a = math.atan2(v.co.y, v.co.x)
        if math.hypot(v.co.x, v.co.y) > r * 0.9: v.co.x *= 1 + 0.035 * max(0.0, math.cos(a - 0.6)); v.co.y *= 1 + 0.035 * max(0.0, math.cos(a - 0.6))
    ends = [disc(name + ' End', r * 0.97, -0.0005, m_end, flip=True), disc(name + ' End', r * 0.97, L + 0.0005, m_end)]
    o = join([body] + ends, name)
    return turn(o, Matrix.Rotation(math.pi / 2, 4, 'X') @ Matrix.Translation((0, 0, -L / 2)))   # +z -> -y: one spiral faces the room


def build(OUT, niche=None):
    T = os.path.join(OUT, 'textures', 'staging'); os.makedirs(T, exist_ok=True)
    made = []
    R = random.Random(5); rng = np.random.default_rng(12)

    oak = mat('Stg Frame Oak', (0.66, 0.50, 0.34), 0.5)
    mount = mat('Stg Mount', (0.95, 0.94, 0.91), 0.9)
    pr = bpy.data.images.load(os.path.join(T, 'stg_print.png')); pr.pack()
    art = mat('Stg Print', (1, 1, 1), 0.9, image=pr)
    euca = mat('Stg Eucalyptus', (0.30, 0.42, 0.38), 0.55)
    stem_m = mat('Stg Stem', (0.30, 0.36, 0.24), 0.6)
    twine = mat('Stg Twine', (0.72, 0.62, 0.46), 0.9)
    brass = mat('Stg Brass', (0.83, 0.66, 0.38), 0.3, metal=1.0)
    tc, tn = terry('stg_terry_white', (0.93, 0.92, 0.89), T, rng)
    towel_w = mat('Stg Towel White', (1, 1, 1), 0.95, image=tc, normal=tn, sheen=0.3)
    tc, tn = terry('stg_terry_oat', (0.78, 0.71, 0.60), T, rng)
    towel_o = mat('Stg Towel Oat', (1, 1, 1), 0.95, image=tc, normal=tn, sheen=0.3)
    # the spiral of a rolled towel seen end on, in both colours
    S = 256; yy, xx = (np.mgrid[0:S, 0:S] + 0.5) / S - 0.5; rr = np.hypot(xx, yy) * 2; th = np.arctan2(yy, xx) / (2 * math.pi)
    turns = (rr * 7 - th + 0.04 * blur(rng.normal(0, 1, (S, S)), 6)) % 1; ridge = np.clip(np.abs(turns - 0.5) * 2, 0, 1) ** 3
    loops = blur(rng.random((S, S)), 1); h = 0.75 * (1 - ridge) + 0.25 * loops
    end_n = normal_img('stg_roll_end_n', h, T, strength=2.0)
    roll_w = mat('Stg Roll End White', (1, 1, 1), 0.95, image=img('stg_roll_end_white', np.clip(np.array([0.93, 0.92, 0.89])[None, None] * (0.80 + 0.2 * h[..., None]), 0, 1), T), normal=end_n)
    roll_o = mat('Stg Roll End Oat', (1, 1, 1), 0.95, image=img('stg_roll_end_oat', np.clip(np.array([0.78, 0.71, 0.60])[None, None] * (0.80 + 0.2 * h[..., None]), 0, 1), T), normal=end_n)

    # ---- on the CARTADEN mango-wood stool between the toilet and the glass (where the olive tree stood; the stool
    # itself is a product now, placements.json, built by make_stool.py): towels folded on its 29 cm slatted top and
    # an amber candle beside them. Same spot as the stool: PX, PY, its top at H.
    PX, PY, H = 0.76, Y1 - 0.175, 0.30
    parts = []
    tw, top = soft_towel(-0.045, 0.0, H, 0.19, 0.20, 3, towel_w, R, 'Folded Towel', rz=0.02)
    tw2, _ = soft_towel(-0.040, 0.006, top - 0.002, 0.175, 0.185, 2, towel_o, R, 'Folded Towel', rz=-0.05)
    parts += [tw, tw2]
    amber = mat('Stg Amber Glass', (0.10, 0.035, 0.008), 0.06)
    wax = mat('Stg Wax', (0.92, 0.88, 0.80), 0.55, sheen=0.2)
    jar = lathe('Candle Jar', [(0.0, 0.0), (0.036, 0.0), (0.040, 0.004), (0.040, 0.082), (0.037, 0.085), (0.034, 0.083), (0.034, 0.012), (0.0, 0.012)], amber, 48)
    parts += [jar, cyl('Wax', (0, 0, 0.066), 0.0338, 0.004, wax, 40), tube('Wick', [(0, 0, 0.068), (0.001, 0, 0.078), (0.003, 0.001, 0.083)], [0.0012] * 3, mat('Stg Wick', (0.05, 0.04, 0.035), 0.9), 6)]
    for o in parts[-3:]: o.location = (0.095, -0.03, H)
    made.append(place(join(parts, 'Staging Stool Towels'), (PX, PY, 0), 0.04))

    # ---- framed abstract print above the toilet (3:4, oak frame, white mount)
    FWD, FHT, FZ = 0.42, 0.56, 1.58
    fr = [box('Frame', (0, 0, 0), (FWD, 0.025, FHT), oak, bevel=0.002)]
    fr.append(box('Mount', (0, -0.0135, 0), (FWD - 0.04, 0.002, FHT - 0.04), mount))
    pic = box('Print', (0, -0.0148, 0), (FWD - 0.14, 0.001, (FWD - 0.14) * 4 / 3), art)
    for poly in pic.data.polygons:
        for li in poly.loop_indices:
            co = pic.data.vertices[pic.data.loops[li].vertex_index].co
            pic.data.uv_layers.active.data[li].uv = (co.x / (FWD - 0.14) + 0.5, co.z / ((FWD - 0.14) * 4 / 3) + 0.5)
    made.append(place(join(fr + [pic], 'Staging Framed Print'), (TX, Y1 - 0.0135, FZ)))

    # ---- eucalyptus bunch hung upside down from its own brass hook on the back wall inside the shower, tied with twine
    HX, HY, HZ = 1.38, Y1 - 0.06, 1.70
    rose = cyl('Hook Rose', (HX, Y1 - 0.004, HZ + 0.06), 0.013, 0.008, brass, 20); rose.rotation_euler.x = math.pi / 2
    parts = [rose, tube('Hook Arm', [(HX, Y1 - 0.004, HZ + 0.06), (HX, Y1 - 0.05, HZ + 0.055), (HX, Y1 - 0.062, HZ + 0.072)], [0.0035] * 3, brass, 10),
             tube('Twine Loop', [(HX - 0.01, HY, HZ - 0.005), (HX, HY - 0.003, HZ + 0.054), (HX + 0.01, HY, HZ - 0.005)], [0.0018] * 3, twine, 6),
             cyl('Twine Wrap', (HX, HY, HZ - 0.02), 0.012, 0.03, twine, 12)]
    V, F, UV = [], [], []
    for k in range(9):
        a = 2 * math.pi * k / 9 + R.uniform(-0.3, 0.3); spread = R.uniform(0.15, 0.4); L = R.uniform(0.32, 0.48)
        d = Vector((math.cos(a) * spread, -abs(math.sin(a)) * spread * 0.5, -1)).normalized()   # never into the wall
        pts = [Vector((HX, HY, HZ)) + d * L * t for t in np.linspace(0, 1, 5)]
        parts.append(tube('Euca Stem', pts, [0.0025] * 5, stem_m, 5))
        for j in range(16):
            t = 0.12 + 0.88 * j / 16; i0 = min(3, int(t * 4)); p = pts[i0].lerp(pts[i0 + 1], t * 4 - i0)
            side = Vector((R.uniform(-1, 1), R.uniform(-0.5, -0.1), R.uniform(-0.3, 0.3))).normalized()   # leaves face the room
            disc_leaf(V, F, UV, p + side * 0.018, side, R.uniform(0.014, 0.022))
    parts.append(mesh_obj('Eucalyptus Leaves', V, F, euca, UV))
    made.append(join(parts, 'Staging Eucalyptus Bunch'))

    # ---- plastic waste bin at the vanity's left end: 4 mm walls, a rolled rim, soft vertical flutes, satin greige
    S = 128; grain = blur(rng.random((S, S)), 1)
    plastic = mat('Stg Bin Plastic', (0.45, 0.40, 0.33), 0.45, normal=normal_img('stg_plastic_n', grain, T, strength=0.6))
    prof = [(0.0, 0.0, 0), (0.094, 0.0, 0), (0.100, 0.006, 0), (0.104, 0.03, 1), (0.114, 0.27, 1), (0.117, 0.285, 0), (0.121, 0.293, 0),
            (0.1215, 0.299, 0), (0.119, 0.304, 0), (0.114, 0.303, 0), (0.112, 0.296, 0), (0.111, 0.285, 0), (0.097, 0.012, 0), (0.0, 0.012, 0)]
    SEG, NP = 120, len(prof); V, F, UV = [], [], []
    for s in range(SEG + 1):
        a = 2 * math.pi * s / SEG
        for i, (r, z, rib) in enumerate(prof):
            r += 0.003 * (0.5 + 0.5 * math.cos(a * 24)) * rib                   # 24 flutes on the outside only
            V.append((r * math.cos(a), r * math.sin(a), z)); UV.append((s / SEG * 3, z / 0.1))
    for s in range(SEG):
        for i in range(NP - 1): p = s * NP + i; F.append((p, p + NP, p + NP + 1, p + 1))
    bin_ = mesh_obj('Staging Waste Bin', V, F, plastic, UV)
    import bmesh
    bm = bmesh.new(); bm.from_mesh(bin_.data); bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-6); bm.to_mesh(bin_.data); bm.free()
    made.append(place(bin_, (-1.98, 0.80, 0)))

    # (the counter's reed diffuser is a product now: Soul & Scents Jasmine, placements.json, make_diffuser.py)

    # ---- the shower niche (right wall, opening facing -x): a matte black pump bottle with its label, an amber
    # bath-oil bottle with a dropper, a white rolled washcloth
    if niche:
        X1, ny0, ny1, nz0 = niche
        NXc = X1 + 0.05
        black = mat('Stg Bottle Black', (0.03, 0.03, 0.032), 0.55)
        chrome = mat('Stg Pump Chrome', (0.85, 0.85, 0.86), 0.15, metal=1.0)
        b1 = lathe('Pump Bottle', [(0.0, 0.0), (0.027, 0.0), (0.030, 0.004), (0.030, 0.150), (0.026, 0.162), (0.012, 0.170), (0.012, 0.176), (0.0, 0.176)], black, 48)
        l1 = band('Pump Label', 0.0305, 0.04, 0.125, math.pi - 0.95, math.pi + 0.95, label_mat('lbl_bodywash', T))
        pump = [lathe('Pump Collar', [(0.0, 0.172), (0.0135, 0.172), (0.0135, 0.186), (0.0, 0.186)], black, 24),
                cyl('Pump Stem', (0, 0, 0.196), 0.004, 0.022, chrome, 16),
                box('Pump Head', (-0.010, 0, 0.209), (0.04, 0.016, 0.012), black, bevel=0.004),
                tube('Pump Nozzle', [(-0.028, 0, 0.209), (-0.036, 0, 0.205)], [0.003, 0.003], black, 10)]
        o1 = join([b1, l1] + pump, 'Staging Niche Body Wash'); o1.location = (NXc, ny0 + 0.07, nz0); made.append(o1)
        b2 = lathe('Oil Bottle', [(0.0, 0.0), (0.019, 0.0), (0.021, 0.004), (0.021, 0.068), (0.016, 0.078), (0.0085, 0.082), (0.0085, 0.088), (0.0, 0.088)], amber, 40)
        l2 = band('Oil Label', 0.0215, 0.016, 0.056, math.pi - 0.9, math.pi + 0.9, label_mat('lbl_serum', T))
        drop = [lathe('Dropper Cap', [(0.0, 0.086), (0.0105, 0.086), (0.0105, 0.104), (0.009, 0.106), (0.0, 0.106)], black, 24),
                lathe('Dropper Bulb', [(0.0, 0.104), (0.007, 0.105), (0.0075, 0.118), (0.005, 0.128), (0.0, 0.130)], mat('Stg Bulb', (0.08, 0.08, 0.08), 0.5), 20)]
        o2 = join([b2, l2] + drop, 'Staging Niche Bath Oil'); o2.location = (NXc + 0.01, ny0 + 0.16, nz0); made.append(o2)
        cloth = rolled_towel(0.085, 0.026, towel_w, roll_w, 'Staging Niche Washcloth')
        turn(cloth, Matrix.Rotation(-math.pi / 2, 4, 'Z'))                     # lying along x, its spiral to the room
        cloth.location = (NXc + 0.002, ny1 - 0.075, nz0 + 0.026); made.append(cloth)
        for o in made[-3:]:
            bpy.ops.object.select_all(action='DESELECT'); o.select_set(True); bpy.context.view_layer.objects.active = o
            bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

    for o in made: print('STAGING', o.name, sum(len(p.vertices) - 2 for p in o.data.polygons), 'tris')
    return made
