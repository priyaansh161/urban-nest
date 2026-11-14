import re
def sub(s, a, b, n=1):
    assert a in s, a[:90]
    return s.replace(a, b, n)

# ======================= part2: windows (clean stepped arched architrave, frame close to the room)
s = open('part2.py', encoding='utf8').read()
a = s.index("    # plaster architrave: an arched moulding round the opening, on the wall")
b = s.index("    # frame, mullions, fanlight")
new = '''    # plaster architrave: two stepped bands (flat, concentric) up the jambs and round the arch, a keystone, sill corbels
    arch_band(axis, c, hw + 0.015, hw + 0.095, spring, sill - 0.03, -0.018, 0.0, M['plaster'], frame)
    arch_band(axis, c, hw + 0.095, hw + 0.145, spring, sill - 0.03, -0.040, -0.018, M['plaster'], frame)
    wbox(frame, axis, c, 'Keystone', 0, spring + hw + 0.12, -0.05, 0.12, 0.16, 0.06, M['plaster'], 0.01)
    for s_ in (-1, 1): wbox(frame, axis, c, 'Corbel', s_ * (hw + 0.04), sill - 0.1, -0.05, 0.07, 0.11, 0.07, M['plaster'], 0.01)
'''
s = s[:a] + new + s[b:]
s = sub(s, "    fd = T - 0.04\n", "    fd = 0.05\n")
s = sub(s, "spring = top - hw; T = 0.20", "spring = top - hw; T = 0.12")
s = sub(s, "def window(axis, W, tag):", '''def arch_band(axis, c, r_in, r_out, spring, z0, d0, d1, m, bucket, n=28):
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

def window(axis, W, tag):''')
open('part2.py', 'w', encoding='utf8').write(s)

# ======================= part3: sofa out of the wall, vinyl, books, side tables
t = open('part3.py', encoding='utf8').read()
t = sub(t, "P_SOFA = bake_piece(chester(2.10, 0.95, 3), 'LM_Sofa', (X1 - 0.475, 0.55, 0)", "P_SOFA = bake_piece(chester(2.10, 0.95, 3), 'LM_Sofa', (X1 - 0.675, 0.55, 0)")
t = sub(t, "newspaper((2.0, 0.25, 0.478)", "newspaper((1.8, 0.25, 0.478)")
t = sub(t, "(2.22, 1.05, 0.70), n1, u1", "(2.02, 1.05, 0.70), n1, u1")
t = sub(t, "(2.22, -0.10, 0.70), n1, u1", "(2.02, -0.10, 0.70), n1, u1")
# side tables: turned legs, inlaid top, drawer + knob; faced into the room (-x)
a = t.index("def side_table("); b = t.index("# ---- the pieces, placed")
new_side = '''def side_table(h, w):
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

'''
t = t[:a] + new_side + t[b:]
t = sub(t, "'LM_SideTableA', (2.36, 1.84, 0), 0.0, 512, 1.0)", "'LM_SideTableA', (2.36, 1.84, 0), math.radians(90), 1024, 1.0)")
t = sub(t, "'LM_SideTableB', (2.38, -0.85, 0), 0.0, 512, 1.0)", "'LM_SideTableB', (2.38, -0.85, 0), math.radians(90), 1024, 1.0)")
# books with covers and page edges
a = t.index("def book("); b = t.index("def stack(")
new_book = '''def cover_mat(name, base, gold, seed):
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
'''
t = t[:a] + new_book + t[b:]
# vinyl records: three sleeves with printed art, one disc half drawn out, with grooves and a label
a = t.index("def vinyl("); b = t.index("def pillow_") if "def pillow_(" in t else t.index("def pattern_mat(")
new_vinyl = '''def sleeve_mat(name, c1, c2, seed):
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

'''
t = t[:a] + new_vinyl + t[b:]
open('part3.py', 'w', encoding='utf8').write(t)

# ======================= part4: no hi-res previews, 128 samples
q = open('part4.py', encoding='utf8').read()
q = sub(q, "samples = 12 if FAST else 192", "samples = 12 if FAST else 128")
q = sub(q, "    if FAST: return\n    scene.camera = cam;", "    if FAST or 'nopreview' in ARGS: return\n    scene.camera = cam;")
q = sub(q, "if not FAST: scene.camera = pc;", "if not (FAST or 'nopreview' in ARGS): scene.camera = pc;")
open('part4.py', 'w', encoding='utf8').write(q)
b = open('bake_living.sh', encoding='utf8').read()
b = sub(b, '-- "$(pwd -W)" >', '-- "$(pwd -W)" nopreview >')
open('bake_living.sh', 'w', encoding='utf8').write(b)

# ======================= placements
m = open('make_placements.py', encoding='utf8').read()
m = sub(m, "pos=[2.55,1.8,1.15],rotY=-1.5708,alignRight=2.59", "pos=[2.55,1.8,1.15],rotY=3.14159,alignRight=2.59")
m = sub(m, "height=1.22,pos=[1.75,1.7,2.085]", "height=1.45,pos=[1.75,1.65,2.085]")
m = sub(m, "height=0.5,pos=[1.9,1.75,0],alignBack=-2.07", "height=0.5,pos=[1.9,1.75,0],rotY=3.14159,alignBack=-2.07")
open('make_placements.py', 'w', encoding='utf8').write(m)

# ======================= admin: the lounge is now an editable room
ad = open('../../admin/rooms.html', encoding='utf8').read()
ad = sub(ad, "  { key: 'quiet-bath',     name: 'The Quiet Bath' },", "  { key: 'quiet-bath',     name: 'The Quiet Bath' },\n  { key: 'living-room',    name: 'The Heritage Lounge' },")
open('../../admin/rooms.html', 'w', encoding='utf8').write(ad)
print('patched v4')
