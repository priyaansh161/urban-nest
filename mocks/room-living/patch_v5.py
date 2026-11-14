import json, re
def sub(s, a, b, n=1):
    assert a in s, a[:90]
    return s.replace(a, b, n)

# ================================================================= part2: colours, textures, floor slabs, shutters
s = open('part2.py', encoding='utf8').read()
s = sub(s, "recolour=(0.022, 0.045, 0.13), contrast=0.0)", "recolour=(0.022, 0.045, 0.13), contrast=0.35)")
s = sub(s, "'plaster': mat('White Plaster', (0.90, 0.88, 0.82, 1), 0.7),", "'plaster': mat('Ceiling-colour Plaster', (0.92, 0.90, 0.85, 1), 0.7),")
s = sub(s, "grid('Floor', (X0, Y0, 0), (X1 - X0, 0, 0), (0, Y1 - Y0, 0), M['marble'], tile=1.2)", '''_floor = grid('Floor', (X0, Y0, 0), (X1 - X0, 0, 0), (0, Y1 - Y0, 0), M['marble'], tile=1.2)
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
slab_uv(_floor)''')
s = sub(s, "box('Grout', (0, Y0 + 1.2 * k, 0.0012)", "box('Grout', (0, Y0 + SLY * k, 0.0012)")
# shutters: framed leaves with louvre panels and brass hinges
old = "        wbox(shutters, axis, c, 'Leaf', uc, sill - 0.05 + hgt / 2, -0.038, w, hgt, 0.04, M['louvre'])\n"
new = '''        zb = sill - 0.05; zt = zb + hgt; zc = (zb + zt) / 2; dd_ = -0.040
        wbox(shutters, axis, c, 'StileA', uc - w / 2 + 0.03, zc, dd_, 0.06, hgt, 0.05, M['green'], 0.003); wbox(shutters, axis, c, 'StileB', uc + w / 2 - 0.03, zc, dd_, 0.06, hgt, 0.05, M['green'], 0.003)
        wbox(shutters, axis, c, 'RailB', uc, zb + 0.045, dd_, w, 0.09, 0.05, M['green'], 0.003); wbox(shutters, axis, c, 'RailT', uc, zt - 0.045, dd_, w, 0.09, 0.05, M['green'], 0.003)
        wbox(shutters, axis, c, 'RailM', uc, zc, dd_, w, 0.08, 0.05, M['green'], 0.003)
        wbox(shutters, axis, c, 'LouvreLo', uc, (zb + 0.09 + zc - 0.04) / 2, dd_ - 0.004, w - 0.1, zc - 0.04 - zb - 0.09, 0.03, M['louvre'])
        wbox(shutters, axis, c, 'LouvreHi', uc, (zc + 0.04 + zt - 0.09) / 2, dd_ - 0.004, w - 0.1, zt - 0.09 - zc - 0.04, 0.03, M['louvre'])
        for zh in (zb + 0.25, zc, zt - 0.25): wbox(shutters, axis, c, 'Hinge', u0 - s * 0.01, zh, -0.07, 0.07, 0.11, 0.012, M['brasslm'], 0.002)
'''
s = sub(s, old, new)
open('part2.py', 'w', encoding='utf8').write(s)

# ================================================================= part3: relayout to his layout, panel mouldings, false ceiling
t = open('part3.py', encoding='utf8').read()
a = "for o in STAGE: o.select_set(False)"
assert a in t
add = '''
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
'''
t = sub(t, a, add + a)
open('part3.py', 'w', encoding='utf8').write(t)
if 'import json' not in open('part1b.py', encoding='utf8').read(): print('NOTE part1b has json?')

# ================================================================= part4: casters skip the split furniture, lights
q = open('part4.py', encoding='utf8').read()
q = sub(q, "for d in PL['staging'] + PL['products']:", "for d in [x for x in PL['staging'] if not x.get('lm')] + PL['products']:")
a = q.index("area('Street R'"); b = q.index("area('Fill'")
newl = '''def aim(lo, target): lo.rotation_euler = (Vector(target) - lo.location).to_track_quat('-Z', 'Y').to_euler()
MOON = (0.62, 0.72, 1.0)
for nm, loc, tgt, sz in (('Moon R', (X1 + 1.1, WR['c'], 2.5), (X1 - 2.2, WR['c'] - 0.2, 0.0), (1.4, 1.9)), ('Moon F', (WF['c'], Y0 - 1.1, 2.5), (WF['c'] + 0.2, Y0 + 2.2, 0.0), (1.4, 1.9))):
    area(nm, loc, sz[0], sz[1], 520, MOON, (0, 0, 0)); aim(bpy.data.objects[nm], tgt)
def spot(name, loc, target, w, deg, blend=0.7, color=WARM):
    ld = bpy.data.lights.new(name, 'SPOT'); ld.energy = w; ld.color = color; ld.spot_size = math.radians(deg); ld.spot_blend = blend; ld.shadow_soft_size = 0.03
    lo = bpy.data.objects.new(name, ld); lo.location = Vector(loc); scene.collection.objects.link(lo); aim(lo, target)
for i_, (x_, y_) in enumerate(DL_SPOTS): spot('DL%d' % i_, (x_, y_, H - DROP_ - 0.02), (x_, y_, 0.0), 30, 80, 0.75)       # downlights: pools on the floor and scallops down the walls
for nm, loc, tgt in (('Pic Gond', (-1.2, Y1 - 0.30, 2.62), (-1.2, Y1, 1.55)), ('Pic Paper', (1.6, Y0 + 0.30, 2.62), (1.6, Y0, 1.55)), ('Pic Artsense', (X0 + 0.30, -1.2, 2.62), (X0, -1.2, 1.55)), ('Pic Clock', (X1 - 0.30, -1.3, 2.62), (X1, -1.3, 1.6))):
    spot(nm, loc, tgt, 45, 55, 0.85)                                                                                       # picture lights wash each frame
for nm, loc, rot in (('Cove L', (-XI + 0.05, 0, H - 0.02), (0, math.radians(-38), 0)), ('Cove R', (XI - 0.05, 0, H - 0.02), (0, math.radians(38), 0))):
    area(nm, loc, 0.12, 2 * YI - 0.1, 40, WARM, rot)
for nm, loc, rot in (('Cove B', (0, YI - 0.05, H - 0.02), (math.radians(-38), 0, 0)), ('Cove F', (0, -YI + 0.05, H - 0.02), (math.radians(38), 0, 0))):
    area(nm, loc, 2 * XI - 0.1, 0.12, 40, WARM, rot)
'''
q = q[:a] + newl + q[b:]
q = sub(q, "np.percentile(lum, 97)", "np.percentile(lum, 98.5)")
open('part4.py', 'w', encoding='utf8').write(q)

# ================================================================= placements: art centred in its wall panel, lamp clear of the panel
p = json.load(open('placements.json', encoding='utf8'))
OV = {'Gond Art Set of Six': {'pos': [-1.2, 1.3, 0]}, 'Modern Abstract Canvas': {'pos': [1.6, 0.95, 2.085]}, 'Woman with Flower Canvas': {'pos': [-2.575, 1.295, 1.2]},
      'Double-Sided Station Clock': {'pos': [2.55, 1.4, 1.3]}, '5-Globe Wall Lamp': {'pos': [2.3, 1.75, 0]}}
for d in p['products']:
    if d['name'] in OV: d.update(OV[d['name']])
json.dump(p, open('placements.json', 'w', encoding='utf8'), indent=1, ensure_ascii=False)
print('patched v5')
