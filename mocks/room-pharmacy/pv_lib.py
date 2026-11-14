# PharmVials products built in Blender to their published sizes (pharmvials.com drawings, refs/d*.jpg):
# child-resistant and snap-cap vials in amber and blue, capsules, the counting tray. Every shape is a
# lathe (a profile spun round) so walls have real thickness and the amber plastic refracts like the real thing.
# Imported by the scene scripts (vial_station.py ...). Units: metres.
import bpy, bmesh, math, os, random
from mathutils import Vector, Matrix

HERE = os.path.dirname(os.path.abspath(__file__))
TEX = os.path.join(HERE, 'tex')

# Published sizes, cm: overall height with cap, body height, base diameter (child-resistant; snap 13 DR is 7.0/5.5/3.3)
VIALS = {6: (6.6, 5.3, 2.6), 8: (7.2, 5.9, 3.0), 13: (7.3, 5.9, 3.3), 20: (7.1, 5.6, 4.1), 40: (10.3, 8.7, 5.2)}

# ---- materials
_M = {}
def principled(name, color, rough=0.4, transmission=0.0, ior=1.45, coat=0.0, sss=0.0, metallic=0.0, alpha=1.0):
    if name in _M: return _M[name]
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (*color, 1)
    b.inputs['Roughness'].default_value = rough
    b.inputs['Metallic'].default_value = metallic
    b.inputs['Transmission Weight'].default_value = transmission
    b.inputs['IOR'].default_value = ior
    b.inputs['Coat Weight'].default_value = coat
    b.inputs['Subsurface Weight'].default_value = sss
    b.inputs['Alpha'].default_value = alpha
    _M[name] = m; return m

def image_material(name, path, rough=0.45, base=None):
    """A printed surface: the PNG drives the colour; optional base colour shows where the PNG is transparent."""
    if name in _M: return _M[name]
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree; b = nt.nodes['Principled BSDF']
    t = nt.nodes.new('ShaderNodeTexImage'); t.image = bpy.data.images.load(path, check_existing=True)
    t.interpolation = 'Cubic'
    nt.links.new(t.outputs['Color'], b.inputs['Base Color'])
    b.inputs['Roughness'].default_value = rough
    _M[name] = m; return m

def imperfect(m, kind='glossy'):
    """Roughness from an imperfection map (tex/rough_*.png, make_imperfections.cjs): fingerprints, smudges and
    scuffs instead of an evenly perfect shine. Image -> Separate Color (G) -> Roughness, the pattern glTF exports."""
    nt = m.node_tree; b = nt.nodes['Principled BSDF']
    if b.inputs['Roughness'].is_linked: return m
    t = nt.nodes.new('ShaderNodeTexImage'); t.image = bpy.data.images.load(os.path.join(TEX, 'rough_%s.png' % kind), check_existing=True)
    t.image.colorspace_settings.name = 'Non-Color'
    sp = nt.nodes.new('ShaderNodeSeparateColor'); nt.links.new(t.outputs['Color'], sp.inputs['Color'])
    nt.links.new(sp.outputs['Green'], b.inputs['Roughness'])
    return m

def amber():  return imperfect(principled('Amber PP', (1.0, 0.42, 0.04), rough=0.09, transmission=1.0, ior=1.49))
def blue():   return imperfect(principled('Blue PP', (0.12, 0.42, 1.0), rough=0.09, transmission=1.0, ior=1.49))
def cap_white(): return imperfect(principled('Cap PP white', (0.93, 0.93, 0.91), rough=0.32, sss=0.15), 'satin')

# ---- geometry
def lathe(name, prof, mat, seg=96, loc=(0, 0, 0), uv=False, knurl=None):
    """Spin a closed (r, z) profile round the Z axis into a watertight mesh. uv: cylindrical UVs (8 per metre up).
    knurl (z0, z1, count, depth): the outermost surface between z0 and z1 is cut into count square-topped ribs."""
    me = bpy.data.meshes.new(name); bm = bmesh.new(); rings = []
    for r, z in prof:
        ring = []
        for i in range(seg):
            a = 2 * math.pi * i / seg
            rr = max(r, 1e-5)
            if knurl and knurl[0] <= z <= knurl[1] and r >= max(p[0] for p in prof) - 1e-6:
                rr += knurl[3] * max(-1.0, min(1.0, 2.5 * math.cos(knurl[2] * a))) * 0.5 - knurl[3] * 0.5
            ring.append(bm.verts.new((rr * math.cos(a), rr * math.sin(a), z)))
        rings.append(ring)
    n = len(rings)
    for k in range(n):
        A, B = rings[k], rings[(k + 1) % n]
        for i in range(seg):
            j = (i + 1) % seg
            try: bm.faces.new((A[i], A[j], B[j], B[i]))
            except ValueError: pass
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-6)
    bm.to_mesh(me); bm.free()
    for p in me.polygons: p.use_smooth = True
    if uv:
        lay = me.uv_layers.new(name='UV')
        for p in me.polygons:
            ac = math.atan2(p.center.y, p.center.x)
            for li in p.loop_indices:
                co = me.vertices[me.loops[li].vertex_index].co; a = math.atan2(co.y, co.x)
                if ac > 2.5 and a < 0: a += 2 * math.pi
                lay.data[li].uv = (a / (2 * math.pi) + 0.5, co.z * 8)
    o = bpy.data.objects.new(name, me); bpy.context.scene.collection.objects.link(o)
    o.data.materials.append(mat); o.location = loc
    return o

def arc(r0, z0, rad, a0, a1, steps=6):
    return [(r0 + rad * math.cos(math.radians(a0 + (a1 - a0) * s / steps)), z0 + rad * math.sin(math.radians(a0 + (a1 - a0) * s / steps))) for s in range(steps + 1)]

def vial_body(name, dr, color='amber', snap=False):
    H, hb, d = VIALS[dr]
    if snap and dr == 13: H, hb = 7.0, 5.5
    rb = d / 200; hb /= 100; rt = rb * 1.07; w = 0.0011; fil = 0.0025
    # outer: base (slight foot), wall tapering out, rolled rim; inner back down; floor 1.4 mm with a dimple
    prof = [(0, 0.0012), (rb - fil, 0.0)] + arc(rb - fil, fil, fil, -90, 0, 4)[1:] + \
           [(rt, hb - 0.004), (rt + 0.0009, hb - 0.0025), (rt + 0.0009, hb - 0.0008), (rt - 0.0002, hb)] + \
           [(rt - w - 0.0002, hb), (rt - w, hb - 0.002), (rb - w, 0.0014 + fil)] + \
           arc(rb - w - fil * 0.7, 0.0014 + fil, fil * 0.7, 0, -90, 4)[1:] + [(0.003, 0.0014), (0, 0.0019)]
    return lathe(name, prof, amber() if color == 'amber' else blue(), uv=True)

def cr_cap(name, dr):
    """Child-resistant 'push down & turn' cap: ribbed skirt, printed top."""
    H, hb, d = VIALS[dr]
    rb = d / 200; rt = rb * 1.07; rc = rt + 0.0022; hc = (H - hb) / 100 + 0.0015
    prof = [(0.0, hc), (rc - 0.0012, hc)] + arc(rc - 0.0012, hc - 0.0012, 0.0012, 90, 0, 4)[1:] + \
           [(rc, 0.0005), (rc - 0.0005, 0), (rc - 0.0017, 0), (rc - 0.0017, hc - 0.0022), (0.0, hc - 0.0022)]
    # the skirt is knurled: 80 vertical grip ribs moulded into it, the detail that says child-resistant cap
    o = lathe(name, prof, cap_white(), seg=320, uv=True, knurl=(0.0, hc, 80, 0.0006))
    # printed top: a disc just above the cap, UV mapped flat
    bpy.ops.mesh.primitive_circle_add(vertices=96, radius=rc - 0.0012, fill_type='NGON', location=(0, 0, hc + 0.00005))
    top = bpy.context.active_object; top.name = name + ' print'
    me = top.data; uv = me.uv_layers.new()
    for loop in me.loops:
        co = me.vertices[loop.vertex_index].co
        uv.data[loop.index].uv = (0.5 + co.x / (2 * (rc - 0.0012)) * 0.98, 0.5 + co.y / (2 * (rc - 0.0012)) * 0.98)
    me.materials.append(image_material('Cap print', os.path.join(TEX, 'cap_cr.png'), rough=0.32))
    top.parent = o
    return o, hc

def snap_cap(name, dr):
    """Snap cap: smooth flat lid with an overhanging flange and a thumb tab."""
    H, hb, d = VIALS[dr]
    rb = d / 200; rt = rb * 1.07; rc = rt + 0.0024; hc = 0.0085
    prof = [(0.0, hc), (rc - 0.001, hc)] + arc(rc - 0.001, hc - 0.001, 0.001, 90, 0, 3)[1:] + \
           [(rc + 0.0006, hc - 0.0028), (rc + 0.0006, hc - 0.0042), (rc - 0.0004, hc - 0.0042), (rc - 0.0004, 0.0),
            (rc - 0.0016, 0.0), (rc - 0.0016, hc - 0.0016), (0.0, hc - 0.0016)]
    o = lathe(name, prof, imperfect(principled('Snap PP white', (0.95, 0.95, 0.93), rough=0.22, sss=0.3), 'satin'), seg=128, uv=True)
    # the moulded ring on the lid, as on the real snap cap
    lathe(name + ' ring', [(rc * 0.62, hc), (rc * 0.66, hc), (rc * 0.66, hc + 0.0005), (rc * 0.62, hc + 0.0005)], o.data.materials[0], seg=96).parent = o
    bpy.ops.mesh.primitive_cube_add(size=1, location=(rc + 0.0035, 0, hc - 0.0035)); t = bpy.context.active_object
    t.scale = (0.007, 0.009, 0.0012); t.name = name + ' tab'; t.data.materials.append(o.data.materials[0]); t.parent = o
    return o, hc

def vial(name, dr, color='amber', cap='cr', loc=(0, 0, 0), rot=0.0, cap_off=None):
    """A vial standing at loc. cap_off=(x, y, upside_down) puts its cap beside it instead of on it."""
    body = vial_body(name, dr, color, snap=(cap == 'snap'))
    body.location = loc; body.rotation_euler.z = rot
    H, hb, d = VIALS[dr]
    c, hc = (cr_cap if cap == 'cr' else snap_cap)(name + ' cap', dr)
    if cap_off is None:
        c.parent = body; c.location = (0, 0, hb / 100 - 0.0035 if cap == 'cr' else hb / 100 - 0.0012)
    else:
        x, y, flip = cap_off
        c.location = (x, y, hc if flip else 0); c.rotation_euler.x = math.pi if flip else 0
    return body

def label_wrap(body, dr, img, frac=0.80, rot=0.0):
    """Wrap a printed Rx label round a vial: a thin cylinder band, frac of the way round, UVs from the angle."""
    H, hb, d = VIALS[dr]
    rb = d / 200; hb /= 100; rt = rb * 1.07
    z0, z1 = 0.006, min(hb - 0.006, 0.006 + 0.054)
    me = bpy.data.meshes.new('Label'); bm = bmesh.new(); seg = 80
    a_span = 2 * math.pi * frac
    rows = []
    for zz in (z0, z1):
        r = rb + (rt - rb) * (zz / hb) + 0.00025
        rows.append([bm.verts.new((r * math.cos(rot - a_span / 2 + a_span * i / seg), r * math.sin(rot - a_span / 2 + a_span * i / seg), zz)) for i in range(seg + 1)])
    faces = [bm.faces.new((rows[0][i], rows[0][i + 1], rows[1][i + 1], rows[1][i])) for i in range(seg)]
    uv = bm.loops.layers.uv.new()
    for i, f in enumerate(faces):
        for l in f.loops:
            k = rows[0].index(l.vert) if l.vert in rows[0] else rows[1].index(l.vert)
            l[uv].uv = (k / seg, 0 if l.vert in rows[0] else 1)
    bm.to_mesh(me); bm.free()
    for p in me.polygons: p.use_smooth = True
    o = bpy.data.objects.new('Label', me); bpy.context.scene.collection.objects.link(o)
    o.data.materials.append(image_material('Label ' + os.path.basename(img), img, rough=0.5)); o.parent = body
    return o

def capsule(name, mats, length=0.0215, r=0.0038, loc=(0, 0, 0), rot=(0, 0, 0)):
    """A two-piece hard capsule (size 0 is ~21.7 mm x 7.6 mm), cap half and body half in two colours."""
    def half(L, rr, m):
        prof = [(0, 0)] + arc(0, rr, rr, -90, 0, 8)[1:] + [(rr, L), (0, L)]
        return lathe(name, prof, m, seg=40)
    body = half(length * 0.62, r, mats[0])
    body.data.transform(Matrix.Translation((0, 0, -length / 2)))      # origin at the capsule's centre
    capo = half(length * 0.5, r * 1.04, mats[1]); capo.rotation_euler.x = math.pi
    capo.location = (0, 0, length / 2); capo.parent = body
    body.location = loc; body.rotation_euler = rot
    return body

def fill_vial(body, dr, n, mats, seed=1):
    """Capsules piled loosely inside a vial (they settle in layers, any angle)."""
    rnd = random.Random(seed)
    H, hb, d = VIALS[dr]; rin = d / 200 - 0.0035
    z = 0.0055
    for i in range(n):
        a = rnd.random() * 2 * math.pi; rr = rnd.random() * rin * 0.6
        c = capsule('Capsule', mats, loc=(rr * math.cos(a), rr * math.sin(a), z),
                    rot=(rnd.uniform(1.2, 1.9), 0, rnd.random() * 6.28))
        c.parent = body
        if i % 3 == 2: z += 0.0062
    return body

def _bx(n, c, s, m, bw=0.0008, off=(0, 0, 0), seg=3):
    bpy.ops.mesh.primitive_cube_add(size=1, location=c); o = bpy.context.active_object; o.name = n
    o.data.transform(Matrix.Translation(off) @ Matrix.Diagonal((*s, 1)))   # size in the mesh, so children are not scaled
    bev = o.modifiers.new('b', 'BEVEL'); bev.width = bw; bev.segments = seg; bev.harden_normals = True
    for f in o.data.polygons: f.use_smooth = True
    o.data.materials.append(m); return o

def counting_tray(loc=(0, 0, 0), rot=0.0, lid_open=1.0):
    """The classic blue pill counting tray (as in his reference photo): shallow tray with a pour spout at one
    corner, a clear hinged return trough along the left end, and the long blue spatula across it."""
    blue = principled('Counting tray blue', (0.015, 0.06, 0.5), rough=0.3, coat=0.25)
    clear = principled('Trough PET', (0.95, 0.97, 1.0), rough=0.05, transmission=1.0, ior=1.3)
    W, D, Hh, t = 0.23, 0.13, 0.014, 0.0022
    root = _bx('Counting tray', (0, 0, t / 2), (W, D, t), blue, bw=0.006, seg=4)
    for n, c, s in [('rim f', (0.012, -D / 2 + t / 2, Hh / 2), (W - 0.024, t, Hh)), ('rim b', (0.012, D / 2 - t / 2, Hh / 2), (W - 0.024, t, Hh)),
                    ('rim r', (W / 2 - t / 2, -0.012, Hh / 2), (t, D - 0.024, Hh))]:
        _bx(n, c, s, blue).parent = root
    # pour spout: the back right corner narrows to a lip
    sp = _bx('Pour spout', (W / 2 - 0.012, D / 2 - 0.012, Hh / 2 + 0.002), (0.034, t, Hh + 0.004), blue)
    sp.rotation_euler.z = math.radians(-45); sp.parent = root
    # the clear trough along the left end: a half pipe the counted pills are swept into, with its lid
    tr = lathe('Return trough', [(0.017, 0.0), (0.018, 0.0), (0.018, D - 0.01), (0.017, D - 0.01)], clear, seg=48)
    for v in tr.data.vertices:                                            # keep the lower half: a half pipe
        if v.co.y < 0: v.co.y = 0
    tr.rotation_euler.x = -math.pi / 2; tr.location = (-W / 2 + 0.006, -D / 2 + 0.005, 0.018); tr.parent = root
    lid = _bx('Trough lid', (-W / 2 + 0.006, -D / 2 + 0.006, 0.019), (0.036, D - 0.012, 0.0014), clear, off=(0, (D - 0.012) / 2, 0))
    lid.rotation_euler = (0, -1.1 * lid_open, 0); lid.location.x -= 0.018; lid.parent = root
    # spatula: a long flat blue blade raised on its edge rib, handle out past the right rim
    s = _bx('Spatula', (0.03, 0.015, 0.0035), (0.16, 0.022, 0.0016), blue, bw=0.0007)
    _bx('Spatula rib', (0.0, 0.0, 0.004), (0.15, 0.004, 0.008), blue, bw=0.001).parent = s
    _bx('Spatula handle', (0.11, 0.0, 0.006), (0.07, 0.012, 0.006), blue, bw=0.002).parent = s
    s.rotation_euler.z = 0.08; s.parent = root
    root.location = loc; root.rotation_euler.z = rot
    return root

def pill_cutter(loc=(0, 0, 0), rot=0.0):
    """PharmVials' multiple pill cutter: a blue pill-shaped case, closed (10 x 4.5 x 2.6 cm): two halves with a seam."""
    blue = principled('Cutter blue', (0.0, 0.32, 0.85), rough=0.33, coat=0.3)
    L, Wd, r = 0.1, 0.045, 0.0225
    base = bpy.data.objects.new('Pill cutter', None); bpy.context.scene.collection.objects.link(base)
    for n, z0, h in (('Cutter base', 0.0, 0.0125), ('Cutter lid', 0.0135, 0.0125)):     # each half: a rounded disc stretched into an oval
        o = lathe(n, [(0, z0), (r - 0.002, z0), (r, z0 + 0.002), (r, z0 + h - 0.002), (r - 0.002, z0 + h), (0, z0 + h)], blue, seg=64)
        o.scale.x = L / Wd; o.parent = base
    base.location = loc; base.rotation_euler.z = rot
    return base

def label_tape(loc=(0, 0, 0), rot=0.0, standing=False):
    """PharmVials' Prescription Clear Label Tape: a clear 2 in roll on a white core, its name printed in blue."""
    W, R, rc = 0.048, 0.04, 0.0385 * 0.7
    clear = principled('Tape film', (0.94, 0.96, 0.98), rough=0.12, transmission=0.85, ior=1.4)
    o = lathe('Clear label tape', [(rc, 0), (R, 0), (R, W), (rc, W)], clear, seg=96)
    core = lathe('Tape core', [(rc - 0.004, 0), (rc, 0), (rc, W), (rc - 0.004, W)], principled('Core white', (0.92, 0.92, 0.9), rough=0.6), seg=64)
    core.parent = o
    # printed wrap: blue lettering on a transparent band just outside the roll
    wrap = lathe('Tape print', [(R + 0.0002, 0.003), (R + 0.0002, W - 0.003)], clear, seg=96)
    me = wrap.data; me.materials.clear()
    m = bpy.data.materials.new('Tape print'); m.use_nodes = True; nt = m.node_tree; b = nt.nodes['Principled BSDF']
    tx = nt.nodes.new('ShaderNodeTexImage'); tx.image = bpy.data.images.load(os.path.join(TEX, 'tape_print.png'), check_existing=True)
    nt.links.new(tx.outputs['Color'], b.inputs['Base Color']); nt.links.new(tx.outputs['Alpha'], b.inputs['Alpha'])
    b.inputs['Roughness'].default_value = 0.2
    me.materials.append(m)
    uv = me.uv_layers.new()
    for p in me.polygons:
        ac = math.atan2(p.center.y, p.center.x)
        for li in p.loop_indices:
            v = me.vertices[me.loops[li].vertex_index].co; a = math.atan2(v.y, v.x)
            if ac > 2.5 and a < 0: a += 2 * math.pi
            uv.data[li].uv = (a / (2 * math.pi) + 0.5, (v.z - 0.003) / (W - 0.006))
    wrap.parent = o
    if standing:
        o.rotation_euler = (math.pi / 2, 0, rot); o.location = (loc[0], loc[1] + W / 2, R)
    else:
        o.rotation_euler.z = rot; o.location = loc
    return o
