import math
def sub(s, a, b, n=1):
    assert a in s, a[:80]
    return s.replace(a, b, n)

# ================= part3: cushions, staging
t = open('part3.py', encoding='utf8').read()
a = t.index("def pillow_("); b = t.index("LAMP_PTS = []")
newp = '''def pattern_mat(name, base, motif, k=5):
    S = 512; y, x = np.mgrid[0:S, 0:S] / S
    line = (np.abs(((x + y) * k) % 1 - 0.5) < 0.035) | (np.abs(((x - y) * k) % 1 - 0.5) < 0.035)
    dots = (np.abs((x * k) % 1 - 0.5) < 0.06) & (np.abs((y * k) % 1 - 0.5) < 0.06)
    weave = 0.88 + 0.12 * np.sin(x * S * 0.95) * np.sin(y * S * 0.95)
    nz = 0.94 + 0.06 * noise(S, S, 21, 2)
    rgb = np.where((line | dots)[..., None], np.array(motif), np.array(base)) * (weave * nz)[..., None]
    hgt = 0.5 + 0.3 * (weave - 0.88) / 0.12 + 0.25 * (line | dots)
    return SL.mat(name, base, 0.85, image=SL.img(name + '_col', np.clip(rgb, 0, 1), TMP), normal=SL.normal_img(name + '_nor', np.clip(hgt, 0, 1), TMP, 3.0), nstrength=1.0, sheen=0.5)
M['teal2'] = pattern_mat('Teal Cushion', (0.05, 0.27, 0.29), (0.78, 0.62, 0.28))
M['ochre2'] = pattern_mat('Ochre Cushion', (0.60, 0.40, 0.10), (0.25, 0.10, 0.05))

def pillow_mesh(name, centre, normal, up, W, Hh, T, m, n=22):
    """A plump scatter cushion: a domed top and bottom meeting at pinched seams, a dimple at the middle, piping round the edge."""
    nrm = Vector(normal).normalized(); up = Vector(up).normalized(); right = up.cross(nrm).normalized(); up = nrm.cross(right).normalized(); c = Vector(centre)
    prof = lambda u: max(0.0, 1 - abs(u) ** 3) ** 0.7
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
    pipe = SL.tube(name + ' Piping', pts, [0.007] * len(pts), m, seg=6)
    STAGE.extend([o, pipe]); return o

def lean(deg, along):
    """(normal, up) of a cushion leaning back by deg, facing along = a unit x/y vector pointing into the room."""
    a = math.radians(deg); ax, ay = along
    return ((ax * math.cos(a), ay * math.cos(a), math.sin(a)), (-ax * math.sin(a), -ay * math.sin(a), math.cos(a)))

def candlestick(x, y, z):
    b = SL.lathe('Candlestick', [(0, 0), (0.04, 0), (0.045, 0.01), (0.012, 0.03), (0.012, 0.09), (0.028, 0.105), (0.0, 0.105)], M['brass'], seg=24); b.location = (x, y, z)
    c = cyl('Candle', (x, y, z + 0.105 + 0.05), 0.014, 0.10, M['porcelain'], seg=14); fl = sphere('Flame', (x, y, z + 0.215), 0.009, M['glow'], 6); STAGE.extend([b, c, fl])

'''
t = t[:a] + newp + t[b:]
a = t.index("LAMP_PTS = []")
tail = t[a:]
b2 = tail.index("for o in STAGE: o.select_set(False)")
newtail = '''LAMP_PTS = []                                        # (the brass lamps went: Lexton, the floor lamps and the globe lamp light the room now)
stack(2.28, 1.985, 0.552, [(0.15, 0.22, 0.040, 'cover', 0.1), (0.14, 0.21, 0.030, 'cover2', -0.15), (0.13, 0.19, 0.035, 'cover3', 0.2)])
vinyl(2.555, 1.86, 0.552)
stack(0.15, 0.04, 0.359, [(0.24, 0.17, 0.035, 'cover2', 0.2), (0.22, 0.16, 0.03, 'cover', -0.1)])
stack(-1.20, 1.86, 0.82, [(0.26, 0.19, 0.040, 'cover3', 0.15), (0.24, 0.18, 0.030, 'cover', -0.1), (0.22, 0.17, 0.035, 'cover2', 0.2)])
candlestick(-1.20, 1.86, 0.82 + 0.105)
newspaper((2.0, 0.25, 0.478), math.radians(70)); newspaper((1.65, -1.52, 0.478), math.radians(-15), 0.36, 0.26)
n1, u1 = lean(10, (-1, 0)); n2, u2 = lean(10, (0, 1))
pillow_mesh('Cushion Teal', (2.22, 1.05, 0.70), n1, u1, 0.46, 0.44, 0.15, M['teal2'])
pillow_mesh('Cushion Ochre', (2.22, -0.10, 0.68), n1, u1, 0.40, 0.40, 0.13, M['ochre2'])
pillow_mesh('Cushion Teal 2', (1.28, -1.64, 0.70), n2, u2, 0.46, 0.44, 0.15, M['teal2'])
pillow_mesh('Cushion Ochre 2', (2.12, -1.64, 0.68), n2, u2, 0.40, 0.40, 0.13, M['ochre2'])
'''
t = t[:a] + newtail + tail[b2:]
open('part3.py', 'w', encoding='utf8').write(t)

# ================= part2: window detail
s = open('part2.py', encoding='utf8').read()
s = sub(s, "    wtube(frame, axis, c, [(p[0], spring + p[1], -0.02) for p in ring_pts], 0.032, M['plaster'])", """    ring_o = [(hw + 0.105) * np.array([math.cos(a), math.sin(a)]) for a in ang]; ring_i = [(hw + 0.05) * np.array([math.cos(a), math.sin(a)]) for a in ang]
    wtube(frame, axis, c, [(p[0], spring + p[1], -0.03) for p in ring_o], 0.04, M['plaster'])
    wtube(frame, axis, c, [(p[0], spring + p[1], -0.05) for p in ring_i], 0.022, M['plaster'])
    wbox(frame, axis, c, 'Keystone', 0, spring + hw + 0.105, -0.05, 0.13, 0.2, 0.06, M['plaster'], 0.012)
    for s_ in (-1, 1): wbox(frame, axis, c, 'Corbel', s_ * (hw + 0.03), sill - 0.1, -0.05, 0.07, 0.11, 0.07, M['plaster'], 0.01)""")
s = sub(s, "wbox(frame, axis, c, 'Arch', s * (hw + 0.075), (sill - 0.03 + spring) / 2, -0.02, 0.064, spring - sill + 0.03, 0.04, M['plaster'], 0.004)", "wbox(frame, axis, c, 'Arch', s * (hw + 0.105), (sill - 0.03 + spring) / 2, -0.03, 0.08, spring - sill + 0.03, 0.05, M['plaster'], 0.006); wbox(frame, axis, c, 'Arch2', s * (hw + 0.05), (sill - 0.03 + spring) / 2, -0.05, 0.045, spring - sill + 0.03, 0.04, M['plaster'], 0.004)")
s = sub(s, "wbox(reveal, axis, c, 'Sill', 0, sill - 0.015, T / 2 - 0.02, 2 * hw + 0.1, 0.03, T + 0.06, M['plaster'], 0.004)", "wbox(reveal, axis, c, 'Sill', 0, sill - 0.018, (T - 0.09) / 2, 2 * hw + 0.2, 0.036, T + 0.09, M['plaster'], 0.007)")
s = sub(s, "wtube(frame, axis, c, [(hw * 0.97 * math.cos(a), spring + hw * 0.97 * math.sin(a), fd) for a in ang], 0.018, M['green'])", "wtube(frame, axis, c, [(hw * 0.97 * math.cos(a), spring + hw * 0.97 * math.sin(a), fd) for a in ang], 0.03, M['green'])")
s = sub(s, "s * hw * 0.97, (sill + spring) / 2, fd, 0.04, spring - sill, 0.05, M['green'])", "s * hw * 0.97, (sill + spring) / 2, fd, 0.06, spring - sill, 0.06, M['green'], 0.004)")
s = sub(s, "0.04 if zz in (sill, spring) else 0.022, 0.05, M['green'])", "0.06 if zz in (sill, spring) else 0.032, 0.055, M['green'], 0.003)")
s = sub(s, "s * hw, (sill + spring) / 2, fd, 0.018, spring - sill, 0.04, M['green'])", "s * hw, (sill + spring) / 2, fd, 0.028, spring - sill, 0.05, M['green'], 0.003)")
s = sub(s, "(hw * 0.97 * math.cos(a), spring + hw * 0.97 * math.sin(a), fd)], 0.011, M['green'])", "(hw * 0.97 * math.cos(a), spring + hw * 0.97 * math.sin(a), fd)], 0.017, M['green'])")
open('part2.py', 'w', encoding='utf8').write(s)

# ================= part4
q = open('part4.py', encoding='utf8').read()
q = q.replace("(P_SOFA, P_LOVE, P_ARM1, P_ARM2, P_SIDE, P_TA, P_TB)", "(P_SOFA, P_LOVE, P_ARM1, P_ARM2, P_SIDE, P_TA, P_TB)")
open('part4.py', 'w', encoding='utf8').write(q)

# ================= placements
m = open('make_placements.py', encoding='utf8').read()
def rp(a, b):
    global m
    assert a in m, a[:70]
    m = m.replace(a, b, 1)
rp("height=0.18,pos=[-1.25,0.82,-1.86]))", "height=0.18,pos=[2.38,0.502,0.85]))")
rp("None,height=0.17,pos=[-0.9,0.82,-1.86]))", "None,height=0.34,pos=[-0.6,0.82,-1.86]))")
rp("None,height=0.205,pos=[-0.55,0.82,-1.86]))", "None,height=0.38,pos=[0.15,0.357,-0.30]))")
rp("height=1.0,pos=[0.45,0,-1.9]))", "height=1.0,pos=[-2.35,0,-1.85]))")
rp("{\"noShadow\":True},height=0.32,pos=[2.55,1.8,1.15]", "{\"noShadow\":True},height=0.55,pos=[2.55,1.8,1.15]")
rp("height=1.5,pos=[-2.3,0,0.95]))", "height=1.5,pos=[-2.3,0,1.8]))")
rp("height=0.432,pos=[1.25,0,-1.88]))", "height=0.55,pos=[1.25,0,-1.88]))")
rp("pos=[0.15,0.357,-0.40],rotY=1.5708", "pos=[0.15,0.357,0.20],rotY=1.5708")
rp("None,height=0.5,pos=[1.9,1.75,0],alignBack=-2.07,noShadow=True))", "{\"glow\":1.1,\"light\":{\"w\":14,\"at\":[1.9,1.95,1.75]}},height=0.5,pos=[1.9,1.75,0],alignBack=-2.07,noShadow=True))")
open('make_placements.py', 'w', encoding='utf8').write(m)

# ================= viewer
v = open('viewer.html', encoding='utf8').read()
v = sub(v, '  <button data-view="wide" class="on">Wide</button>', '  <button data-view="painting">Painting</button>')
v = sub(v, "  wide:    {", "  painting:{ pos:[-0.6, 1.55, -1.5], target:[1.75, 1.65, 2.08] },        // the Paper Plane canvas on the front wall, seen from the back of the room\n  wide:    {")
v = sub(v, "  holder.position.set(...def.pos); holder.rotation.y = def.rotY || 0;", "  holder.position.set(...def.pos); holder.rotation.y = def.rotY || 0;\n  if (def.glow) obj.traverse(o => { if (!o.isMesh) return; (Array.isArray(o.material) ? o.material : [o.material]).forEach(mt => { if (mt && mt.isMeshStandardMaterial) { mt.emissive = new THREE.Color(0xffb552); mt.emissiveMap = mt.map || null; mt.emissiveIntensity = def.glow; mt.needsUpdate = true; } }); });   // a lit lamp (the 5-globe wall lamp)")
open('viewer.html', 'w', encoding='utf8').write(v)
print('patched')
