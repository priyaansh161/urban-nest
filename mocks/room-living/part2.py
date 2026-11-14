
# ---------------------------------------------------------------- materials
LINEN = lambda name, c: ph(name, 'rough_linen', 1024, recolour=c, contrast=1.3)
def ph2(name, folder, stem, size=2048, tint=None, recolour=None, contrast=1.0, rough_img=True):
    f = lambda k: '%s/%s_%s.jpg' % (folder, stem, k)
    return pbr(name, scan_img(f('Color') if folder == 'Marble019' else f('diff_2k'), size, tint=tint, recolour=recolour, contrast=contrast),
               scan_img(f('NormalGL') if folder == 'Marble019' else f('nor_gl_2k'), 1024, False),
               scan_img(f('Roughness') if folder == 'Marble019' else f('rough_2k'), 512, False))

def noise(h, w, seed, r):
    a = np.random.default_rng(seed).normal(0, 1, (h, w)); a = SL.blur(a, r); return a / max(1e-6, np.abs(a).max())

def leather_mat():
    n = noise(512, 512, 3, 2); n2 = noise(512, 512, 4, 9)
    base = np.array([0.50, 0.23, 0.08]); rgb = base[None, None, :] * (0.88 + 0.07 * n[..., None] + 0.10 * n2[..., None])
    c = SL.img('leather_col', np.clip(rgb, 0, 1), TMP); nm = SL.normal_img('leather_nor', 0.5 + 0.5 * n, TMP, 1.2)
    return SL.mat('Cognac Leather', base, 0.42, 0.0, image=c, normal=nm, nstrength=0.35, sheen=0.3)

def cane_images():
    S = 256; y, x = np.mgrid[0:S, 0:S] / S * 2 * math.pi * 20
    w1 = np.sin(x + y); w2 = np.sin(x - y); hexa = np.clip(0.5 + 0.5 * np.maximum(w1, w2), 0, 1)
    hole = np.clip((np.cos(x) * np.cos(y) - 0.25) * 4, 0, 1)                        # open weave: dark gaps between the strands
    base = np.array([0.80, 0.62, 0.33]); gap = np.array([0.10, 0.06, 0.03])
    rgb = gap + (base - gap) * (0.45 + 0.55 * hexa)[..., None] * (1 - 0.8 * hole[..., None]) + 0.0
    rgb = np.clip(np.where(hole[..., None] > 0.5, gap + (base - gap) * 0.35, rgb), 0, 1)
    return SL.img('cane_col', rgb, TMP), SL.normal_img('cane_nor', 0.5 + 0.5 * hexa - 0.4 * hole, TMP, 4.0)

def rug_image():
    Hh, Ww = 720, 1024; v, u = np.mgrid[0:Hh, 0:Ww]; u = u / Ww; v = v / Hh
    sel = lambda c, a, b: np.where(c[..., None], a, b)
    X = u * 2.7; Y = v * 1.9; dx = np.minimum(X, 2.7 - X); dy = np.minimum(Y, 1.9 - Y); d = np.minimum(dx, dy)      # metres from the nearest edge
    rust, indigo, cream, red, gold = (np.array(c) for c in [(0.50, 0.17, 0.10), (0.08, 0.12, 0.26), (0.80, 0.70, 0.52), (0.62, 0.20, 0.12), (0.72, 0.52, 0.22)])
    lat = np.cos((X + Y) * 17) * np.cos((X - Y) * 17)                                     # diamond lattice of the field
    field = sel(lat > 0.15, rust, sel(lat > -0.35, red, indigo))
    cx, cy = abs(X - 1.35), abs(Y - 0.95); med = (cx / 0.9) + (cy / 0.55)                 # a centre lozenge
    field = sel(med < 1.0, sel(np.cos(cx * 30) * np.cos(cy * 30) > 0, indigo, cream * 0.9), field)
    field = sel(abs(med - 1.05) < 0.05, gold, field)
    flor = np.cos(np.where(dx < dy, Y, X) * 40)
    rgb = sel((d > 0.07) & (d < 0.26), sel(flor > 0, rust, indigo), field)                # main border
    rgb = sel((d > 0.26) & (d < 0.30), cream, rgb); rgb = sel((d > 0.04) & (d < 0.07), cream, rgb)
    rgb = sel(d <= 0.04, indigo, rgb); rgb = sel((d > 0.30) & (d < 0.33), gold, rgb)
    rgb = rgb * (0.80 + 0.20 * (0.5 + noise(Hh, Ww, 8, 1))[..., None]) * (0.92 + 0.08 * noise(Hh, Ww, 9, 12)[..., None])  # faded, woven
    return SL.img('rug_col', np.clip(rgb, 0, 1), TMP)

def night_image():
    Hh, Ww = 512, 256; v, u = np.mgrid[0:Hh, 0:Ww]; v = v / Hh; u = u / Ww
    sky = np.array([0.02, 0.03, 0.07]) * (1 - v[..., None]) + np.array([0.05, 0.06, 0.09]) * v[..., None]
    gl = np.exp(-(((u - 0.72) / 0.10) ** 2 + ((v - 0.52) / 0.07) ** 2)); lamp = np.exp(-(((u - 0.72) / 0.012) ** 2 + ((v - 0.5) / 0.02) ** 2))
    tree = np.exp(-(((u - 0.2) / 0.24) ** 2 + ((v - 0.78) / 0.2) ** 2)) * 0.5
    rgb = sky + np.array([1.0, 0.65, 0.25]) * (0.35 * gl + 1.2 * lamp)[..., None] + np.array([0.01, 0.05, 0.03]) * tree[..., None]
    return SL.img('night_col', np.clip(rgb, 0, 1), TMP)

NIGHT = SL.mat('Night Outside', (0.2, 0.2, 0.3), 1.0, image=night_image())
_nb = NIGHT.node_tree.nodes['Principled BSDF']
for nd in list(NIGHT.node_tree.nodes):
    if nd.type == 'TEX_IMAGE': NIGHT.node_tree.links.new(nd.outputs['Color'], _nb.inputs['Emission Color'])
_nb.inputs['Emission Strength'].default_value = 1.0; _nb.inputs['Base Color'].default_value = (0, 0, 0, 1)

cane_c, cane_n = cane_images()
def louvre_mat():
    S = 128; v = np.linspace(0, 1, S, endpoint=False)[:, None].repeat(S, 1); ph_ = (v * 2) % 1     # two louvres per 11 cm tile
    hgt = np.where(ph_ < 0.8, ph_ / 0.8, 1 - (ph_ - 0.8) / 0.2) * 0.9                               # sloped slat, sharp gap
    base = np.array([0.05, 0.17, 0.09]); rgb = base[None, None, :] * (0.55 + 0.75 * hgt[..., None])
    return SL.mat('Louvre Green', base, 0.5, image=SL.img('louvre_col', np.clip(rgb, 0, 1), TMP), normal=SL.normal_img('louvre_nor', hgt, TMP, 5.0), nstrength=1.0)

M = {
    'wall': ph2('Navy Paint', 'beige_wall_001', 'beige_wall_001', recolour=(0.022, 0.045, 0.13), contrast=0.35),   # flat navy, keeps the plaster's fine relief
    'marble': ph2('White Marble', 'Marble019', 'Marble019_2K-JPG', tint=(1.04, 1.04, 1.02)),
    'plaster': mat('Ceiling-colour Plaster', (0.92, 0.90, 0.85, 1), 0.7),
    'ceiling': mat('Ceiling', (0.92, 0.90, 0.85, 1), 0.9),
    'inlay': mat('Black Inlay', (0.012, 0.012, 0.014, 1), 0.18),
    'rose': pbr('Rosewood', scan_img('walnut_veneer/walnut_veneer_Diffuse_2k.jpg', 1024, tint=(0.62, 0.30, 0.22)),
                scan_img('walnut_veneer/walnut_veneer_nor_gl_2k.jpg', 1024, False), scan_img('walnut_veneer/walnut_veneer_Rough_2k.jpg', 512, False)),
    'darkwood': mat('Dark Wood', (0.10, 0.045, 0.03, 1), 0.45),
    'leather': leather_mat(),
    'brass': mat('Brass', (0.80, 0.56, 0.22, 1), 0.28, 1.0),
    'brasslm': mat('Brass (lightmapped)', (0.78, 0.54, 0.20, 1), 0.38, 0.0),      # metal bakes black in a diffuse lightmap (the black dots on the sofas), so lightmapped brass is painted gold
    'grout': mat('Grout', (0.30, 0.30, 0.29, 1), 0.6),
    'louvre': louvre_mat(),
    'green': mat('Shutter Green', (0.045, 0.16, 0.09, 1), 0.5),
    'cane': SL.mat('Cane', (0.8, 0.6, 0.3), 0.55, image=cane_c, normal=cane_n, nstrength=1.0),
    'ivory': LINEN('Ivory Linen', (0.90, 0.86, 0.76)),
    'teal': LINEN('Teal Velvet', (0.05, 0.27, 0.29)),
    'paper': mat('Newsprint', (0.88, 0.86, 0.80, 1), 0.9),
    'rug': SL.mat('Persian Rug', (0.5, 0.2, 0.1), 0.95, image=rug_image(), sheen=0.4, normal=SL.normal_img('rug_nor', 0.5 + 0.5 * noise(720, 1024, 5, 1), TMP, 3.0), nstrength=0.8),
    'shade': mat('Pleated Shade', (0.95, 0.88, 0.70, 1), 0.7, 0.0, emit=((1.0, 0.82, 0.55, 1), 1.4)),
    'glassc': mat('Crystal Glass', (0.85, 0.90, 0.92, 1), 0.04, 0.0, alpha=0.18),
    'amber': mat('Whisky', (0.55, 0.25, 0.05, 1), 0.2),
    'silver': mat('Silver', (0.80, 0.82, 0.85, 1), 0.2, 1.0),
    'cover': mat('Book Cover A', (0.30, 0.10, 0.07, 1), 0.6), 'cover2': mat('Book Cover B', (0.07, 0.12, 0.10, 1), 0.6), 'cover3': mat('Book Cover C', (0.45, 0.30, 0.12, 1), 0.6),
    'vinyl': mat('Vinyl', (0.01, 0.01, 0.012, 1), 0.2), 'label': mat('Record Label', (0.65, 0.1, 0.08, 1), 0.6),
    'porcelain': mat('Porcelain', (0.95, 0.94, 0.90, 1), 0.2),
    'tea': mat('Tea', (0.30, 0.15, 0.06, 1), 0.2),
    'night': NIGHT,
}
M['glow'] = mat('Warm Glow', (1, .85, .65, 1), 0.5, 0.0, emit=((1, .78, .5, 1), 2.0))

# ---------------------------------------------------------------- shell
NC = lambda l: max(1, round(l / STEP))
DUW = (X1 - X0) / NC(X1 - X0); DUD = (Y1 - Y0) / NC(Y1 - Y0); DZ = H / NC(H)
SIDE = dict()           # for the arched windows: snapped hole numbers and edges
SPRING_R = 0.6
def arch_hole(axis, c, hw=SPRING_R, sill=0.9, ztop=2.7):
    A, du = (Y1, DUD) if axis == 'x' else (X1, DUW)
    i0 = round((A - (c + hw)) / du); i1 = round((A - (c - hw)) / du)
    j0 = round(sill / DZ); j1 = round(ztop / DZ)
    hi, lo = A - i0 * du, A - i1 * du
    return dict(hole=(i0, i1, j0, j1), c=(hi + lo) / 2, hw=(hi - lo) / 2, sill=j0 * DZ, top=j1 * DZ)
WR = arch_hole('x', 0.55); WF = arch_hole('y', -0.7)
_floor = grid('Floor', (X0, Y0, 0), (X1 - X0, 0, 0), (0, Y1 - Y0, 0), M['marble'], tile=1.2)
SLX, SLY = 15 * DUW, 15 * DUD                      # one marble slab = 15 grid cells each way (1.2 m)
def slab_uv(ob, seed=5):
    """Every slab reads a different (turned, flipped, shifted) part of the marble scan, so the floor stops repeating."""
    me = ob.data; uv = me.uv_layers['UV']; r = np.random.default_rng(seed); cache = {}
    for poly in me.polygons:
        cx = sum(me.vertices[v].co.x for v in poly.vertices) / len(poly.vertices); cy = sum(me.vertices[v].co.y for v in poly.vertices) / len(poly.vertices)
        key = (int(math.floor((cx - X0) / SLX)), int(math.floor((cy - Y0) / SLY)))
        if key not in cache: cache[key] = (int(r.integers(0, 4)), bool(r.integers(0, 2)), float(r.random()), float(r.random()))
        k, flip, ox, oy = cache[key]
        for li, vi in zip(poly.loop_indices, poly.vertices):
            co = me.vertices[vi].co; u = (co.x - X0 - key[0] * SLX) / SLX; v = (co.y - Y0 - key[1] * SLY) / SLY
            if flip: u = 1 - u
            for _ in range(k): u, v = 1 - v, u
            uv.data[li].uv = (u * SLX / 1.2 + ox, v * SLY / 1.2 + oy)
slab_uv(_floor)
grid('Ceiling', (X0, Y1, H), (X1 - X0, 0, 0), (0, -(Y1 - Y0), 0), M['ceiling'], tile=3.0)
grid('Back Wall', (X0, Y1, 0), (X1 - X0, 0, 0), (0, 0, H), M['wall'], tile=3.0)
grid('Left Wall', (X0, Y0, 0), (0, Y1 - Y0, 0), (0, 0, H), M['wall'], tile=3.0)
grid('Right Wall', (X1, Y1, 0), (0, -(Y1 - Y0), 0), (0, 0, H), M['wall'], tile=3.0, holes=[WR['hole']])
grid('Front Wall', (X1, Y0, 0), (-(X1 - X0), 0, 0), (0, 0, H), M['wall'], tile=3.0, holes=[WF['hole']])

LMX = []          # extra objects that get a lightmap (built surfaces)
def lm(o): LMX.append(o); return o
def make_uv(o, tile=3.0): world_uv(o, tile)

# cornice: three stepped bands round the top of the walls, a ceiling rose over the table, skirting round the foot
CT = 3.0
def run(name, depth, hgt, zb, m):
    parts = [box(name, (0, Y1 - depth / 2, zb + hgt / 2), (X1 - X0, depth, hgt), m), box(name, (0, Y0 + depth / 2, zb + hgt / 2), (X1 - X0, depth, hgt), m),
             box(name, (X0 + depth / 2, 0, zb + hgt / 2), (depth, Y1 - Y0 - 2 * depth, hgt), m), box(name, (X1 - depth / 2, 0, zb + hgt / 2), (depth, Y1 - Y0 - 2 * depth, hgt), m)]
    return parts
corn = run('Cornice', 0.045, 0.20, 2.80, M['plaster']) + run('Cornice', 0.11, 0.07, 2.93, M['plaster']) + run('Cornice', 0.17, 0.035, 2.965, M['plaster'])
corn += run('Cornice', 0.075, 0.025, 2.86, M['plaster'])
cornice = join(corn, 'LM_Cornice'); make_uv(cornice, 1.5); lm(cornice)
sk = run('Skirting', 0.016, 0.15, 0, M['plaster']) + run('Skirting', 0.03, 0.025, 0.15, M['plaster'])
skirting = join(sk, 'LM_Skirting'); make_uv(skirting, 1.5); lm(skirting)
rose = [cyl('Rose', (0.15, 0.1, CT - 0.014), 0.55, 0.028, M['plaster'], seg=48), cyl('Rose', (0.15, 0.1, CT - 0.035), 0.40, 0.03, M['plaster'], seg=48),
        cyl('Rose', (0.15, 0.1, CT - 0.055), 0.24, 0.03, M['plaster'], seg=48)]
ceil_rose = join(rose, 'LM_CeilingRose'); make_uv(ceil_rose, 1.5); lm(ceil_rose)
# black marble inlay: a broad band and a hairline round the floor, 55 cm in from the walls
def ring(inset, wd, z, name):
    xa, xb, ya, yb = X0 + inset, X1 - inset, Y0 + inset, Y1 - inset
    return [box(name, (0, ya, z), (xb - xa + wd, wd, 0.004), M['inlay']), box(name, (0, yb, z), (xb - xa + wd, wd, 0.004), M['inlay']),
            box(name, (xa, 0, z), (wd, yb - ya - wd, 0.004), M['inlay']), box(name, (xb, 0, z), (wd, yb - ya - wd, 0.004), M['inlay'])]
gl = [box('Grout', (X0 + 1.2 * k, 0, 0.0012), (0.006, Y1 - Y0, 0.0024), M['grout']) for k in range(1, 5)] + [box('Grout', (0, Y0 + SLY * k, 0.0012), (X1 - X0, 0.006, 0.0024), M['grout']) for k in range(1, 4)]
grout = join(gl, 'LM_Grout'); make_uv(grout, 1.0); lm(grout)
inlay = join(ring(0.50, 0.055, 0.002, 'Inlay') + ring(0.62, 0.014, 0.002, 'Inlay'), 'LM_Inlay'); make_uv(inlay, 1.0); lm(inlay)

# ---------------------------------------------------------------- arched windows with green louvred shutters
def wmap(axis, c, u, z, d):
    return (X1 + d, c + u, z) if axis == 'x' else (c + u, Y0 - d, z)      # d > 0 goes out into the wall, < 0 into the room
def wbox(parts, axis, c, name, u, z, d, du, dz, dd, m, bevel=0.0):
    dim = (dd, du, dz) if axis == 'x' else (du, dd, dz)
    parts.append(box(name, wmap(axis, c, u, z, d), dim, m, bevel=bevel))
def wtube(parts, axis, c, pts, r, m):
    P = [wmap(axis, c, u, z, d) for u, z, d in pts]
    parts.append(SL.tube('t', P, [r] * len(P), m, seg=6))
def arch_band(axis, c, r_in, r_out, spring, z0, d0, d1, m, bucket, n=28):
    """A flat band round an arched opening (up the jambs, over the arch, down the jambs), from depth d0 to d1: a closed solid."""
    def path(r):
        return [(-r, z0), (-r, spring)] + [(r * math.cos(a_), spring + r * math.sin(a_)) for a_ in np.linspace(math.pi, 0, n)[1:-1]] + [(r, spring), (r, z0)]
    pi_, po_ = path(r_in), path(r_out); V, F = [], []
    for (ui, zi), (uo, zo) in zip(pi_, po_):
        V += [wmap(axis, c, ui, zi, d0), wmap(axis, c, uo, zo, d0), wmap(axis, c, ui, zi, d1), wmap(axis, c, uo, zo, d1)]
    N = len(pi_)
    for k in range(N - 1):
        i, j = 4 * k, 4 * k + 4
        F += [(i, i + 1, j + 1, j), (i + 2, j + 2, j + 3, i + 3), (i + 1, i + 3, j + 3, j + 1), (i, j, j + 2, i + 2)]
    F += [(0, 2, 3, 1), (4 * (N - 1), 4 * (N - 1) + 1, 4 * (N - 1) + 3, 4 * (N - 1) + 2)]
    me = bpy.data.meshes.new('Band'); me.from_pydata(V, [], F)
    bm = bmesh.new(); bm.from_mesh(me); bmesh.ops.recalc_face_normals(bm, faces=bm.faces); bm.to_mesh(me); bm.free(); me.materials.append(m)
    ob = bpy.data.objects.new('Band', me); scene.collection.objects.link(ob); bucket.append(ob)

def window(axis, W, tag):
    c, hw, sill, top = W['c'], W['hw'], W['sill'], W['top']; spring = top - hw; T = 0.12
    frame, shutters, reveal = [], [], []
    # spandrels: wall plane filler between the opening's rectangle and the arch
    for s in (-1, 1):
        pts = [(s * hw, spring)] + [(s * hw * math.cos(a), spring + hw * math.sin(a)) for a in np.linspace(0, math.pi / 2, 14)[1:]] + [(0, top), (s * hw, top)]
        Vv = [wmap(axis, c, u, z, 0.0) for u, z in pts]
        me = bpy.data.meshes.new('Spandrel'); me.from_pydata(Vv, [], [list(range(len(Vv)))] if s == 1 else [list(range(len(Vv)))[::-1]])
        # winding so the face looks into the room
        ob = bpy.data.objects.new('Spandrel', me); scene.collection.objects.link(ob); me.materials.append(M['wall']); reveal.append(ob)
    # reveal (wall thickness): jambs, sill, round the arch
    wbox(reveal, axis, c, 'Jamb', -hw, (sill + spring) / 2, T / 2, 0.01, spring - sill, T, M['plaster'])
    wbox(reveal, axis, c, 'Jamb', hw, (sill + spring) / 2, T / 2, 0.01, spring - sill, T, M['plaster'])
    wbox(reveal, axis, c, 'Sill', 0, sill - 0.018, (T - 0.09) / 2, 2 * hw + 0.2, 0.036, T + 0.09, M['plaster'], 0.007)
    ang = np.linspace(0, math.pi, 17); Vv, Ff = [], []
    for a in ang:
        for d in (0.0, T): Vv.append(wmap(axis, c, hw * math.cos(a), spring + hw * math.sin(a), d))
    for k in range(16): Ff.append((2 * k, 2 * k + 1, 2 * k + 3, 2 * k + 2))
    me = bpy.data.meshes.new('Intrados'); me.from_pydata(Vv, [], Ff); me.materials.append(M['plaster']); me.shade_smooth()
    ob = bpy.data.objects.new('Intrados', me); scene.collection.objects.link(ob); reveal.append(ob)
    # plaster architrave: two stepped bands (flat, concentric) up the jambs and round the arch, a keystone, sill corbels
    arch_band(axis, c, hw + 0.015, hw + 0.095, spring, sill - 0.03, -0.018, 0.0, M['plaster'], frame)
    arch_band(axis, c, hw + 0.095, hw + 0.145, spring, sill - 0.03, -0.040, -0.018, M['plaster'], frame)
    wbox(frame, axis, c, 'Keystone', 0, spring + hw + 0.12, -0.05, 0.12, 0.16, 0.06, M['plaster'], 0.01)
    for s_ in (-1, 1): wbox(frame, axis, c, 'Corbel', s_ * (hw + 0.04), sill - 0.1, -0.05, 0.07, 0.11, 0.07, M['plaster'], 0.01)
    # frame, mullions, fanlight
    fd = 0.05
    wtube(frame, axis, c, [(hw * 0.97 * math.cos(a), spring + hw * 0.97 * math.sin(a), fd) for a in ang], 0.03, M['green'])
    for s in (-1, 0, 1): wbox(frame, axis, c, 'Stile', s * hw * 0.97, (sill + spring) / 2, fd, 0.06, spring - sill, 0.06, M['green'], 0.004)
    for zz in np.linspace(sill, spring, 5): wbox(frame, axis, c, 'Rail', 0, zz, fd, 2 * hw, 0.06 if zz in (sill, spring) else 0.032, 0.055, M['green'], 0.003)
    for s in (-0.5, 0.5): wbox(frame, axis, c, 'Glazing', s * hw, (sill + spring) / 2, fd, 0.028, spring - sill, 0.05, M['green'], 0.003)
    for a in np.linspace(math.pi / 6, math.pi * 5 / 6, 5): wtube(frame, axis, c, [(0, spring, fd), (hw * 0.97 * math.cos(a), spring + hw * 0.97 * math.sin(a), fd)], 0.017, M['green'])
    for s in (-1, 1): wbox(frame, axis, c, 'Handle', s * 0.04, (sill + spring) / 2, fd - 0.05, 0.012, 0.16, 0.02, M['brasslm'])
    # night outside
    pl = bpy.data.meshes.new('Night'); Vn = [wmap(axis, c, u, z, T + 0.12) for u, z in ((-hw, sill), (hw, sill), (hw, top), (-hw, top))]
    pl.from_pydata(Vn, [], [(0, 1, 2, 3)]); uvl = pl.uv_layers.new(name='UV')
    for li, uv in zip(range(4), ((0, 0), (1, 0), (1, 1), (0, 1))): uvl.data[li].uv = uv
    pl.materials.append(M['night']); nob = bpy.data.objects.new('Night', pl); scene.collection.objects.link(nob)
    # louvred shutters, half open: leaves folded back flat against the wall either side
    for s in (-1, 1):
        u0 = s * (hw + 0.04); w = 0.58; uc = u0 + s * w / 2; hgt = spring - sill + 0.10
        zb = sill - 0.05; zt = zb + hgt; zc = (zb + zt) / 2; dd_ = -0.040
        wbox(shutters, axis, c, 'StileA', uc - w / 2 + 0.03, zc, dd_, 0.06, hgt, 0.05, M['green'], 0.003); wbox(shutters, axis, c, 'StileB', uc + w / 2 - 0.03, zc, dd_, 0.06, hgt, 0.05, M['green'], 0.003)
        wbox(shutters, axis, c, 'RailB', uc, zb + 0.045, dd_, w, 0.09, 0.05, M['green'], 0.003); wbox(shutters, axis, c, 'RailT', uc, zt - 0.045, dd_, w, 0.09, 0.05, M['green'], 0.003)
        wbox(shutters, axis, c, 'RailM', uc, zc, dd_, w, 0.08, 0.05, M['green'], 0.003)
        wbox(shutters, axis, c, 'LouvreLo', uc, (zb + 0.09 + zc - 0.04) / 2, dd_ - 0.004, w - 0.1, zc - 0.04 - zb - 0.09, 0.03, M['louvre'])
        wbox(shutters, axis, c, 'LouvreHi', uc, (zc + 0.04 + zt - 0.09) / 2, dd_ - 0.004, w - 0.1, zt - 0.09 - zc - 0.04, 0.03, M['louvre'])
        for zh in (zb + 0.25, zc, zt - 0.25): wbox(shutters, axis, c, 'Hinge', u0 - s * 0.01, zh, -0.07, 0.07, 0.11, 0.012, M['brasslm'], 0.002)
    for o in reveal + frame + shutters: o.select_set(False)
    rv = join(reveal, 'LM_Reveal' + tag); world_uv(rv, 3.0); lm(rv)
    fr = join(frame, 'LM_Frame' + tag); world_uv(fr, 1.0); lm(fr)
    sh = join(shutters, 'LM_Shutters' + tag); world_uv(sh, 0.11); lm(sh)
    return nob
night_r = window('x', WR, 'R'); night_f = window('y', WF, 'F')
for nb_ in (night_r, night_f): nb_.name = 'Night_' + nb_.name

# the one door, on the left wall at the back: double leaf with raised panels, architrave, brass handles
dparts, dy = [], 0.80
wallx = X0
def dbox(name, y, z, dx, dy_, dz, m, bev=0.0): dparts.append(box(name, (wallx + dx / 2, dy + y, z), (dx, dy_, dz), m, bevel=bev))
dbox('Casing', -0.58, 1.27, 0.05, 0.10, 2.54, M['plaster']); dbox('Casing', 0.58, 1.27, 0.05, 0.10, 2.54, M['plaster']); dbox('Lintel', 0, 2.52, 0.07, 1.34, 0.12, M['plaster'], 0.01)
dbox('Frame', 0, 1.22, 0.06, 1.12, 2.44, M['darkwood'])
for s in (-1, 1):
    dbox('Leaf', s * 0.27, 1.21, 0.075, 0.52, 2.38, M['rose'], 0.004)
    for z0, h in ((0.55, 0.65), (1.42, 0.5), (2.05, 0.28)):
        dbox('Panel', s * 0.27, z0 + h / 2 + 0.05, 0.09, 0.36, h, M['rose'], 0.01)
    dbox('Handle', s * 0.06, 1.05, 0.11, 0.025, 0.16, M['brasslm'], 0.006)
door = join(dparts, 'LM_Door'); world_uv(door, 1.5); lm(door)
