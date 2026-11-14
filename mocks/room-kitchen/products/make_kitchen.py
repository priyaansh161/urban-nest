# Kitchen Essentials built in Blender from their listing photos and real listing sizes (no Meshy: simple shapes and glass).
#   blender -b -P make_kitchen.py -- <outdir> <keys,comma,separated|all> <walnut_veneer dir>
# Each product: <outdir>/<key>.glb plus <key>_look.png (a Cycles check render). Origin = bottom centre, metres, z up.
import bpy, bmesh, math, os, sys
import numpy as np
from mathutils import Vector, Matrix
OUT, WHICH, TEX = sys.argv[sys.argv.index('--') + 1:]
OUT, TEX = os.path.abspath(OUT), os.path.abspath(TEX); os.makedirs(OUT, exist_ok=True)
P = []                                   # parts of the product being built

def reset():
    P.clear(); bpy.ops.wm.read_factory_settings(use_empty=True)
def link(o):
    bpy.context.scene.collection.objects.link(o); P.append(o); return o
def activate(o):
    bpy.ops.object.select_all(action='DESELECT'); o.select_set(True); bpy.context.view_layer.objects.active = o

# ---------- materials (Principled colours are linear) ----------
def pmat(name, col, rough=0.5, metal=0.0, trans=0.0, ior=1.45, coat=0.0):
    m = bpy.data.materials.get(name)
    if m: return m
    m = bpy.data.materials.new(name); m.use_nodes = True; b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (*col, 1); b.inputs['Roughness'].default_value = rough; b.inputs['Metallic'].default_value = metal
    if trans: b.inputs['Transmission Weight'].default_value = trans; b.inputs['IOR'].default_value = ior
    if coat: b.inputs['Coat Weight'].default_value = coat
    return m
def img_mat(name, img, rough=0.5, alpha=False, metal=0.0, normal=None, nstr=0.3):
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree; b = nt.nodes['Principled BSDF']
    t = nt.nodes.new('ShaderNodeTexImage'); t.image = img; nt.links.new(t.outputs['Color'], b.inputs['Base Color'])
    b.inputs['Roughness'].default_value = rough; b.inputs['Metallic'].default_value = metal
    if alpha:
        nt.links.new(t.outputs['Alpha'], b.inputs['Alpha'])
        try: m.surface_render_method = 'DITHERED'
        except Exception: pass
    if normal:
        tn = nt.nodes.new('ShaderNodeTexImage'); tn.image = normal; tn.image.colorspace_settings.name = 'Non-Color'
        nm = nt.nodes.new('ShaderNodeNormalMap'); nm.inputs['Strength'].default_value = nstr
        nt.links.new(tn.outputs['Color'], nm.inputs['Color']); nt.links.new(nm.outputs['Normal'], b.inputs['Normal'])
    return m
def np_img(name, arr, alpha=False):            # arr h x w x 3|4, display (sRGB) values 0..1
    h, w = arr.shape[:2]; img = bpy.data.images.new(name, w, h, alpha=alpha)
    px = np.ones((h, w, 4), np.float32); px[..., :arr.shape[2]] = arr; img.pixels.foreach_set(px.ravel()); img.pack(); return img
_GRAIN = None
def wood(name, dark, light, rough=0.5):        # the walnut scan's grain, recoloured (dark/light in sRGB)
    global _GRAIN
    if _GRAIN is None:
        im = bpy.data.images.load(os.path.join(TEX, 'walnut_veneer_Diffuse_2k.jpg')); im.scale(1024, 1024)
        px = np.empty(1024 * 1024 * 4, np.float32); im.pixels.foreach_get(px); px = px.reshape(1024, 1024, 4)
        L = px[..., :3] @ np.array([0.3, 0.59, 0.11]); lo, hi = np.percentile(L, [2, 98]); _GRAIN = np.clip(0.5 + ((L - lo) / (hi - lo) - 0.5) * 0.6, 0, 1)
    d, l = np.array(dark), np.array(light)
    img = np_img(name + ' grain', d + (l - d) * _GRAIN[..., None])
    nrm = bpy.data.images.load(os.path.join(TEX, 'walnut_veneer_nor_gl_2k.jpg')); nrm.scale(1024, 1024)
    return img_mat(name, img, rough, normal=nrm, nstr=0.25)
STEEL = lambda: pmat('Stainless Steel', (0.78, 0.78, 0.77), 0.22, 1.0)
BRUSHED = lambda: pmat('Brushed Steel', (0.72, 0.72, 0.71), 0.38, 1.0)
GLASS = lambda: pmat('Glass', (1, 1, 1), 0.02, 0.0, 1.0, 1.47)
CLEAR = lambda: pmat('Clear Plastic', (0.97, 0.98, 0.99), 0.08, 0.0, 1.0, 1.49)
OIL = lambda: pmat('Oil', (1.0, 0.72, 0.10), 0.03, 0.0, 0.55, 1.47)
BLACK = lambda: pmat('Black Coat', (0.012, 0.012, 0.013), 0.42, 0.25)
WHITE = lambda: pmat('White Plastic', (0.80, 0.80, 0.79), 0.35)

# ---------- geometry helpers ----------
def mesh_obj(name, bm, mats):
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free(); o = bpy.data.objects.new(name, me)
    for m in mats: me.materials.append(m)
    return link(o)
def lathe(name, prof, mats, midx=None, seg=64, closed=False, uvs=(1, 1)):
    """Revolve a (r, z) profile about z. Profiles touching the axis (r=0) close themselves; closed=True joins last->first."""
    bm = bmesh.new(); uvl = bm.loops.layers.uv.new('UV'); n = len(prof)
    cum = [0.0]
    for i in range(1, n): cum.append(cum[-1] + math.dist(prof[i - 1], prof[i]))
    total = cum[-1] + (math.dist(prof[-1], prof[0]) if closed else 0)
    rings, info = [], {}
    for i, (r, z) in enumerate(prof):
        if r < 1e-7:
            v = bm.verts.new((0, 0, z)); info[v] = (i, None); rings.append(None); rings[-1] = [v]
        else:
            ring = []
            for k in range(seg):
                a = 2 * math.pi * k / seg; v = bm.verts.new((r * math.cos(a), r * math.sin(a), z)); info[v] = (i, k); ring.append(v)
            rings.append(ring)
    pairs = [(i, i + 1) for i in range(n - 1)] + ([(n - 1, 0)] if closed else [])
    for (i, j) in pairs:
        a, b = rings[i], rings[j]
        if len(a) == 1 and len(b) == 1: continue
        for k in range(seg):
            k1 = (k + 1) % seg
            if len(a) == 1: vs = [a[0], b[k], b[k1]]
            elif len(b) == 1: vs = [a[k], a[k1], b[0]]
            else: vs = [a[k], a[k1], b[k1], b[k]]
            f = bm.faces.new(vs); f.material_index = midx[i] if midx else 0
            for lp in f.loops:
                ii, kk = info[lp.vert]
                u = (k + 0.5) if kk is None else (seg if (kk == 0 and k == seg - 1) else kk)
                v = total if (closed and (i, j) == (n - 1, 0) and ii == 0) else cum[ii]
                lp[uvl].uv = (u / seg * uvs[0], v * uvs[1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return mesh_obj(name, bm, mats)
def rrect(w, d, r, seg=8):
    pts = []
    for cx, cy, a0 in ((w / 2 - r, d / 2 - r, 0), (-w / 2 + r, d / 2 - r, 90), (-w / 2 + r, -d / 2 + r, 180), (w / 2 - r, -d / 2 + r, 270)):
        for k in range(seg + 1):
            a = math.radians(a0 + 90 * k / seg); pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts
def slab(name, outer, z0, z1, m, bevel=0.0015, bseg=2, keep=True):
    bm = bmesh.new(); bm.faces.new([bm.verts.new((x, y, z0)) for x, y in outer]); bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    ext = bmesh.ops.extrude_face_region(bm, geom=list(bm.faces)); nv = [e for e in ext['geom'] if isinstance(e, bmesh.types.BMVert)]
    bmesh.ops.translate(bm, verts=nv, vec=(0, 0, z1 - z0)); bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free(); o = bpy.data.objects.new(name, me); bpy.context.scene.collection.objects.link(o)
    if m: me.materials.append(m)
    if bevel:
        activate(o); bv = o.modifiers.new('b', 'BEVEL'); bv.width = bevel; bv.segments = bseg; bv.limit_method = 'ANGLE'; bpy.ops.object.modifier_apply(modifier='b')
    if keep: P.append(o)
    return o
def cut(o, cutter, op='DIFFERENCE'):
    activate(o); md = o.modifiers.new('c', 'BOOLEAN'); md.object = cutter; md.operation = op; md.solver = 'EXACT'
    bpy.ops.object.modifier_apply(modifier='c');
    if cutter in P: P.remove(cutter)
    bpy.data.objects.remove(cutter)
def pocket(o, outer, z0, z1):
    cut(o, slab('cut', outer, z0, z1, None, bevel=0, keep=False))
def box(c, d, m, bev=0.001, keep=True):
    bpy.ops.mesh.primitive_cube_add(size=1, location=c); o = bpy.context.object; o.scale = d; bpy.ops.object.transform_apply(scale=True)
    if bev: bv = o.modifiers.new('b', 'BEVEL'); bv.width = bev; bv.segments = 2; bpy.ops.object.modifier_apply(modifier='b')
    if m: o.data.materials.append(m)
    if keep: P.append(o)
    else: bpy.context.scene.collection.objects.unlink(o) if False else None
    return o
def cyl(r, depth, loc, m, rot=(0, 0, 0), v=32, bev=0.0):
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=depth, vertices=v, location=loc, rotation=rot); o = bpy.context.object
    if bev: bv = o.modifiers.new('b', 'BEVEL'); bv.width = bev; bv.segments = 2; bpy.ops.object.modifier_apply(modifier='b')
    if m: o.data.materials.append(m)
    P.append(o); return o
def cr(pts, n=8):                         # Catmull-Rom through the points
    Pt = [Vector(p) for p in pts]; out = []
    for i in range(len(Pt) - 1):
        p0, p1, p2, p3 = Pt[max(i - 1, 0)], Pt[i], Pt[i + 1], Pt[min(i + 2, len(Pt) - 1)]
        for s in range(n):
            t = s / n; t2, t3 = t * t, t * t * t
            out.append(0.5 * (2 * p1 + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t2 + (-p0 + 3 * p1 - 3 * p2 + p3) * t3))
    out.append(Pt[-1]); return out
def tube(name, pts, r, m, smooth=True, closed=False, res=3, sy=1.0):
    pts = cr(pts) if (smooth and not closed) else [Vector(p) for p in pts]
    cu = bpy.data.curves.new(name, 'CURVE'); cu.dimensions = '3D'; cu.bevel_depth = r; cu.bevel_resolution = res; cu.use_fill_caps = True
    sp = cu.splines.new('POLY'); sp.points.add(len(pts) - 1)
    for p, c in zip(sp.points, pts): p.co = (c.x, c.y, c.z, 1)
    sp.use_cyclic_u = closed
    o = bpy.data.objects.new(name, cu); bpy.context.scene.collection.objects.link(o); cu.materials.append(m)
    activate(o); bpy.ops.object.convert(target='MESH')
    if sy != 1.0:
        o.scale = (1, sy, 1); bpy.ops.object.transform_apply(scale=True)
    P.append(o); return o
def text(body, size, m, mw, ext=0.0003):
    cu = bpy.data.curves.new('t', 'FONT'); cu.body = body; cu.size = size; cu.extrude = ext; cu.align_x = 'CENTER'; cu.align_y = 'CENTER'
    o = bpy.data.objects.new('t', cu); bpy.context.scene.collection.objects.link(o); cu.materials.append(m); o.matrix_world = mw
    activate(o); bpy.ops.object.convert(target='MESH'); P.append(o); return o
def planar_uv(o, sx, sy, ox=0.5, oy=0.5):
    me = o.data
    if not me.uv_layers: me.uv_layers.new(name='UV')
    uv = me.uv_layers.active.data
    for p in me.polygons:
        for li, vi in zip(p.loop_indices, p.vertices):
            co = o.matrix_world @ me.vertices[vi].co; uv[li].uv = (co.x / sx + ox, co.y / sy + oy)
def cube_uv(o, size):
    activate(o)
    if not o.data.uv_layers: o.data.uv_layers.new(name='UV')
    bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.select_all(action='SELECT'); bpy.ops.uv.cube_project(cube_size=size); bpy.ops.object.mode_set(mode='OBJECT')
def strip(name, xs, wfun, zfun, t, m, zcurl=None):
    """A sheet along x: width wfun(x), bottom height zfun(x), thickness t; zcurl(x, yn) adds a cross-curve (yn in -1..1)."""
    bm = bmesh.new(); ny = 10; rows = []
    for x in xs:
        w = max(wfun(x), 0.0006); row = []
        for j in range(ny + 1):
            yn = -1 + 2 * j / ny; z = zfun(x) + (zcurl(x, yn) if zcurl else 0)
            row.append((bm.verts.new((x, yn * w / 2, z)), bm.verts.new((x, yn * w / 2, z + t))))
        rows.append(row)
    for a, b in zip(rows, rows[1:]):
        for j in range(ny):
            bm.faces.new((a[j][0], b[j][0], b[j + 1][0], a[j + 1][0])); bm.faces.new((a[j][1], a[j + 1][1], b[j + 1][1], b[j][1]))
        bm.faces.new((a[0][0], a[0][1], b[0][1], b[0][0])); bm.faces.new((a[ny][0], b[ny][0], b[ny][1], a[ny][1]))
    for row in (rows[0], rows[-1]):
        for j in range(ny): bm.faces.new((row[j][0], row[j + 1][0], row[j + 1][1], row[j][1]))
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-6); bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return mesh_obj(name, bm, [m])

# ---------- products ----------
def chopping_board():           # 53d21ba3  Wood Chop mango wood board, 38 x 20 x 2.5 cm, black D-handle on one end; no sleeve
    W = wood('Mango Wood', (0.66, 0.45, 0.26), (0.88, 0.69, 0.47), 0.55)
    b = slab('Board', rrect(0.38, 0.20, 0.022, 10), 0, 0.025, W, bevel=0.003, bseg=3); cube_uv(b, 0.45)
    pts = [(0.188, -0.032, 0.0125), (0.203, -0.031, 0.0125), (0.214, -0.02, 0.0125), (0.217, 0, 0.0125), (0.214, 0.02, 0.0125), (0.203, 0.031, 0.0125), (0.188, 0.032, 0.0125)]
    tube('Handle', pts, 0.0038, BLACK())
    for y in (-0.032, 0.032): cyl(0.006, 0.004, (0.188, y, 0.0125), BLACK(), rot=(0, math.pi / 2, 0))
    return 'Wood Chop Mango Wood Chopping Board'

def kmils():                    # 46c9cd64  230 ml borosilicate glass jar, white cap with pour spout, teal knob + silicone brush
    lathe('Glass', [(0, 0), (0.029, 0), (0.0315, 0.003), (0.0315, 0.106), (0.0287, 0.106), (0.0287, 0.006), (0, 0.006)], [GLASS()])
    lathe('Oil', [(0, 0.0063), (0.0284, 0.0063), (0.0284, 0.058), (0, 0.058)], [OIL()])
    lathe('Cap', [(0, 0.103), (0.0325, 0.103), (0.0325, 0.116), (0.030, 0.124), (0.022, 0.131), (0.011, 0.134), (0, 0.134)], [WHITE()])
    tube('Spout', [(0.02, 0, 0.122), (0.033, 0, 0.126), (0.038, 0, 0.128)], 0.0055, WHITE(), smooth=False)
    TEAL = pmat('Teal Silicone', (0.013, 0.11, 0.13), 0.55)
    lathe('Knob', [(0, 0.133), (0.0075, 0.133), (0.0075, 0.142), (0.0095, 0.145), (0.006, 0.148), (0, 0.148)], [TEAL])
    cyl(0.0042, 0.07, (0, 0, 0.068), TEAL)
    for i in range(7):
        x = -0.012 + i * 0.004; box((x, 0, 0.022), (0.0024, 0.006, 0.036), TEAL, bev=0.0008).rotation_euler = (0, -x * 3, 0)
    box((0, 0, 0.041), (0.03, 0.008, 0.008), TEAL, bev=0.002)
    return 'Kmils 230 ml Glass Oil Dispenser with Brush'

def volrix():                   # b16d9948  500 ml 2-in-1 glass oil sprayer/pourer: tapered borosilicate bottle, white head + loop handle
    lathe('Glass', [(0, 0), (0.039, 0), (0.042, 0.004), (0.040, 0.10), (0.035, 0.165), (0.024, 0.182), (0.0215, 0.19), (0.0185, 0.19),
                    (0.021, 0.181), (0.032, 0.164), (0.037, 0.10), (0.039, 0.006), (0, 0.006)], [GLASS()])
    lathe('Oil', [(0, 0.0063), (0.0386, 0.0063), (0.0368, 0.10), (0.0355, 0.118), (0, 0.118)], [OIL()])
    lathe('Collar', [(0, 0.185), (0.0245, 0.185), (0.0245, 0.203), (0.022, 0.206), (0, 0.206)], [WHITE()])
    lathe('Head', [(0, 0.205), (0.021, 0.205), (0.02, 0.218), (0.014, 0.228), (0, 0.231)], [WHITE()])
    tube('Nozzle', [(0.012, 0, 0.217), (0.03, 0, 0.219), (0.036, 0, 0.22)], 0.005, WHITE(), smooth=False)
    tube('Trigger', [(-0.012, 0, 0.226), (-0.03, 0, 0.226), (-0.042, 0, 0.214)], 0.0045, WHITE(), sy=1.8)
    tube('Handle', [(-0.022, 0, 0.196), (-0.05, 0, 0.19), (-0.058, 0, 0.165), (-0.052, 0, 0.135), (-0.038, 0, 0.128)], 0.0062, WHITE(), sy=1.3)
    return 'VOLRIX 500 ml 2-in-1 Glass Oil Dispenser'

def salt_pepper():              # 0d924fe2  The Better Home glass shakers with handles, white + black, steel lids, SALT / PEPPER
    WH = pmat('White Glass', (0.85, 0.86, 0.86), 0.12, coat=0.6); BK = pmat('Black Glass', (0.012, 0.012, 0.013), 0.1, coat=0.6)
    for x0, body, ink, word in ((-0.042, WH, BK, 'SALT'), (0.042, BK, WH, 'PEPPER')):
        j = lathe('Jar', [(0, 0), (0.026, 0), (0.0285, 0.004), (0.0285, 0.072), (0.026, 0.078), (0.021, 0.082), (0.021, 0.088), (0, 0.088)], [body])
        j.location = (x0, 0, 0)
        l = lathe('Lid', [(0, 0.083), (0.0228, 0.083), (0.0228, 0.097), (0.0205, 0.0995), (0, 0.0995)], [STEEL()]); l.location = (x0, 0, 0)
        for k in range(7):
            a = 2 * math.pi * k / 6; rr = 0 if k == 6 else 0.009
            cyl(0.0013, 0.0008, (x0 + rr * math.cos(a), rr * math.sin(a), 0.0997), BLACK(), v=12)
        h = tube('Handle', [(0.026, 0, 0.066), (0.042, 0, 0.062), (0.047, 0, 0.045), (0.042, 0, 0.026), (0.026, 0, 0.021)], 0.0058, body, sy=1.25)
        h.location = (x0, 0, 0)
        size = 0.0125 if word == 'SALT' else 0.0105
        mw = Matrix.Translation((x0, -0.0289, 0.042)) @ Matrix.Rotation(math.pi / 2, 4, 'Y') @ Matrix.Rotation(math.pi / 2, 4, 'X')
        text(word, size, ink, mw)
    return 'The Better Home Glass Salt & Pepper Shakers'

def basting_brush():            # 71a93adf  P-Plus 21.5 cm stainless handle with hanging ring, black silicone head; lying flat
    S = STEEL(); SIL = pmat('Black Silicone', (0.015, 0.015, 0.016), 0.55)
    h = lathe('Handle', [(0, 0), (0.0055, 0.002), (0.0068, 0.03), (0.0075, 0.08), (0.0055, 0.135), (0.0035, 0.155), (0.004, 0.16), (0, 0.162)], [S], seg=24)
    h.rotation_euler = (0, math.pi / 2, 0); h.location = (-0.105, 0, 0.0075); h.scale = (0.55, 1, 1)     # elliptical section, flat side down
    tor = bpy.ops.mesh.primitive_torus_add(major_radius=0.0095, minor_radius=0.0022, location=(-0.114, 0, 0.0075)); t = bpy.context.object; t.data.materials.append(S); P.append(t)
    box((0.064, 0, 0.0075), (0.016, 0.03, 0.007), S, bev=0.002)
    for i in range(9):
        y = -0.0128 + i * 0.0032; box((0.093, y, 0.0075), (0.042, 0.0019, 0.0062), SIL, bev=0.0007)
    box((0.074, 0, 0.0075), (0.008, 0.032, 0.0085), SIL, bev=0.0015)
    return 'P-Plus Stainless Steel Silicone Basting Brush'

def spoon_rest(L, rx, ry, D, t, w0, w1, rise, m):
    bx = -L / 2 + rx
    f = [(0, 0), (0.45, 0.10), (0.72, 0.30), (0.9, 0.62), (1.0, 1.0)]
    outer = [(a * rx, b * D) for a, b in f]; inner = [(max(a * rx - t, 0) if a else 0, b * D + t) for a, b in reversed(f)]
    prof = outer + [(rx + t * 0.3, D + t * 0.5)] + inner
    bwl = lathe('Bowl', prof, [m], seg=72); bwl.location = (bx, 0, 0); bwl.scale = (1, ry / rx, 1)
    x0, x1 = bx + rx * 0.86, L / 2; rend = w1 / 2
    def w(x):
        s = (x - x0) / (x1 - x0); base = w0 + (w1 - w0) * min(max(s, 0), 1)
        if x > x1 - rend: base = w1 * math.sqrt(max(1 - ((x - (x1 - rend)) / rend) ** 2, 0.0004))
        return base
    def z(x):
        s = min(max((x - x0) / (x1 - x0 - rend), 0), 1); return D - t * 0.6 + rise * (3 * s * s - 2 * s ** 3)
    xs = [x0 + (x1 - x0) * i / 60 for i in range(61)]
    strip('Handle', xs, w, z, t, m, zcurl=lambda x, yn: 0.0012 * yn * yn)

def naalsa():                   # 5ee6f430  20.5 x 10 cm brushed stainless spoon rest
    spoon_rest(0.205, 0.058, 0.05, 0.022, 0.0016, 0.03, 0.026, 0.014, BRUSHED()); return 'NAALSA Stainless Steel Spoon Rest'
def primeway():                 # 5c8fc071  20 x 10.5 cm charcoal PP spoon rest
    spoon_rest(0.20, 0.055, 0.0525, 0.017, 0.003, 0.05, 0.03, 0.016, pmat('Charcoal PP', (0.022, 0.023, 0.025), 0.5)); return 'Primeway PP Spoon Rest'

def wood_rest():                # 2759a7b9  11.9 x 11.4 cm polished wooden spatula rest with a carved dish
    W = wood('Sheesham Wood', (0.42, 0.25, 0.13), (0.64, 0.42, 0.24), 0.4)
    b = slab('Rest', rrect(0.119, 0.114, 0.028, 10), 0, 0.016, W, bevel=0.003, bseg=3)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=1, segments=48, ring_count=24, location=(0, -0.006, 0.0285)); s = bpy.context.object; s.scale = (0.046, 0.042, 0.016)
    cut(b, s); box((0, 0.047, 0.0165), (0.034, 0.03, 0.012), None, bev=0, keep=False); g = bpy.context.object; g.name = 'notch'
    bpy.ops.object.transform_apply(); cut(b, g); cube_uv(b, 0.2)
    return 'Wooden Spatula Rest'

def sink_mat():                 # 1b0130dd  HOMEZE grey silicone drainer mat 30 x 10 x 2 cm, ridges, front spout
    G = pmat('Grey Silicone', (0.15, 0.16, 0.17), 0.6)
    b = slab('Mat', rrect(0.30, 0.10, 0.016, 8), 0, 0.02, G, bevel=0.002)
    pocket(b, rrect(0.285, 0.085, 0.011, 8), 0.004, 0.03)
    for i in range(15):
        box((-0.126 + i * 0.018, 0, 0.0052), (0.0035, 0.066, 0.0026), G, bev=0.0008)
    sp = slab('Spout', rrect(0.05, 0.03, 0.008, 6), 0, 0.006, G, bevel=0.0015); sp.location = (0, -0.052, 0)
    return 'HOMEZE Silicone Sink Drainer Mat'

def dish_mat():                 # 3e046e4a  HomeCloud 50 x 40 cm absorbent drying mat, Moroccan tile print, rubber edge
    Wpx, Hpx = 1000, 800; yy, xx = np.mgrid[0:Hpx, 0:Wpx].astype(np.float32)
    border = 24; tile = (Wpx - 2 * border) / 5.0
    tx = (xx - border) / tile; ty = (yy - border) / ((Hpx - 2 * border) / 4.0)
    ix, iy = np.floor(tx), np.floor(ty); u = (tx - ix) * 2 - 1; v = (ty - iy) * 2 - 1
    r = np.hypot(u, v); th = np.arctan2(v, u)
    cream = np.array([0.94, 0.89, 0.79]); teal = np.array([0.13, 0.48, 0.50]); dark = np.array([0.22, 0.16, 0.12])
    pal = np.array([[0.78, 0.33, 0.18], [0.88, 0.64, 0.22], [0.16, 0.27, 0.48], [0.62, 0.24, 0.30]])
    col = np.broadcast_to(cream, (Hpx, Wpx, 3)).copy()
    corner = np.hypot(1 - np.abs(u), 1 - np.abs(v)) < 0.42; col[corner] = teal
    pick = pal[((ix + 2 * iy) % 4).astype(int)]
    star_r = 0.62 * (0.72 + 0.28 * np.cos(8 * th)); star = r < star_r; col[star] = pick[star]
    outline = np.abs(r - star_r) < 0.035; col[outline] = dark
    col[(r > 0.16) & (r < 0.24)] = teal; col[r <= 0.16] = cream
    petals = (r > 0.3) & (r < 0.45) & (np.cos(4 * th + math.pi / 4) > 0.75); col[petals] = cream
    grout = (np.abs(u) > 0.975) | (np.abs(v) > 0.975); col[grout] = col[grout] * 0.75
    edge = (xx < border) | (xx >= Wpx - border) | (yy < border) | (yy >= Hpx - border); col[edge] = [0.25, 0.17, 0.11]
    noise = np.random.default_rng(1).normal(0, 0.025, (Hpx, Wpx, 1)); col = np.clip(col + noise, 0, 1)
    M = img_mat('Tile Print Mat', np_img('mat print', col), 0.85)
    b = slab('Mat', rrect(0.50, 0.40, 0.012, 6), 0, 0.004, M, bevel=0.001); planar_uv(b, 0.50, 0.40)
    return 'HomeCloud Dish Drying Mat'

def texro():                    # 6410bafe  TEX-RO black steel dish rack on a drainer tray, 43 x 32 x 13 cm, cutlery holder
    B = BLACK(); TRAY = pmat('Black Tray', (0.018, 0.018, 0.02), 0.35)
    t = slab('Tray', rrect(0.43, 0.32, 0.022, 8), 0, 0.018, TRAY, bevel=0.002); pocket(t, rrect(0.414, 0.304, 0.016, 8), 0.004, 0.03)
    sp = slab('Spout', rrect(0.04, 0.03, 0.006, 4), 0.006, 0.012, TRAY, bevel=0.001); sp.location = (0.12, -0.17, 0)
    R = 0.0024; W2, D2 = 0.43 - 0.03, 0.32 - 0.03
    for z in (0.034, 0.082, 0.128):
        tube('Rail', [(x, y, z) for x, y in rrect(W2, D2, 0.02, 4)], R, B, closed=True)
    xs = [-W2 / 2 + 0.01 + i * 0.039 for i in range(11)]
    for x in xs:
        for y in (-D2 / 2, D2 / 2): tube('Post', [(x, y, 0.034), (x, y, 0.128)], R, B, smooth=False)
    for y in [-D2 / 2 + 0.035 + i * 0.037 for i in range(7)]:
        tube('Post', [(-W2 / 2, y, 0.034), (-W2 / 2, y, 0.128)], R, B, smooth=False); tube('Post', [(W2 / 2, y, 0.034), (W2 / 2, y, 0.128)], R, B, smooth=False)
        tube('Base', [(-W2 / 2, y, 0.034), (W2 / 2, y, 0.034)], R * 0.85, B, smooth=False)
    for row_y, top in ((-0.035, 0.075), (0.085, 0.102)):
        for i in range(11):
            x = -0.07 + i * 0.024; tube('Prong', [(x, row_y, 0.034), (x, row_y, top - 0.008), (x + 0.004, row_y, top), (x + 0.008, row_y, top - 0.008), (x + 0.008, row_y, 0.034)], R * 0.9, B)
    for x in (-0.2, 0.2):
        for y in (-0.145, 0.145): cyl(0.006, 0.016, (x, y, 0.026), B, v=16)
    c = slab('Cutlery', rrect(0.085, 0.11, 0.01, 4), 0.03, 0.145, TRAY, bevel=0.0015); c.location = (-0.15, 0.05, 0)
    pocket(c, rrect(0.079, 0.104, 0.008, 4), 0.036, 0.2)
    for i in range(5):
        hcut = box((0, 0, 0), (0.008, 0.2, 0.07), None, bev=0, keep=False); hcut.location = (-0.15 - 0.028 + i * 0.014, 0.05, 0.1); bpy.ops.object.transform_apply(); cut(c, hcut)
    return 'TEX-RO Dish Drying Rack with Drainer Tray'

def curd_maker():               # b4bd8136  HomeWiz 1100 ml hung curd maker: clear box, white basket with fine steel mesh windows
    o = slab('Box', rrect(0.10, 0.085, 0.013, 8), 0, 0.165, CLEAR(), bevel=0.0015); pocket(o, rrect(0.094, 0.079, 0.010, 8), 0.003, 0.2)
    slab('Seal', rrect(0.1035, 0.0885, 0.014, 8), 0.163, 0.170, WHITE(), bevel=0.001)
    lid = slab('Lid', rrect(0.103, 0.088, 0.014, 8), 0.169, 0.181, CLEAR(), bevel=0.002)
    box((0, -0.046, 0.175), (0.03, 0.006, 0.006), WHITE(), bev=0.0015)
    bk = slab('Basket', rrect(0.088, 0.073, 0.009, 8), 0.03, 0.162, WHITE(), bevel=0.001); pocket(bk, rrect(0.084, 0.069, 0.007, 8), 0.034, 0.2)
    for x in (-0.021, 0.021):
        c = box((x, 0, 0.098), (0.03, 0.2, 0.1), None, bev=0, keep=False); cut(bk, c)
    c = box((0, 0, 0.098), (0.2, 0.046, 0.1), None, bev=0, keep=False); cut(bk, c)
    N = 128; yy, xx = np.mgrid[0:N, 0:N]; line = ((xx % 6) < 2) | ((yy % 6) < 2)
    a = np.zeros((N, N, 4), np.float32); a[..., :3] = 0.62; a[..., 3] = np.where(line, 1.0, 0.25)
    MESH = img_mat('Steel Mesh', np_img('mesh', a, alpha=True), 0.35, alpha=True, metal=0.8)
    mesh = slab('Mesh', rrect(0.0855, 0.0705, 0.008, 8), 0.045, 0.152, MESH, bevel=0); pocket(mesh, rrect(0.0849, 0.0699, 0.0077, 8), 0.04, 0.2)
    cube_uv(mesh, 0.02)
    return 'HomeWiz Hung Curd Maker 1100 ml'

def tissue_holder():            # 7419de18  Vintageware walnut-stained stand: round base, rod, ball finial; with a kitchen roll
    W = wood('Walnut Stain', (0.22, 0.11, 0.05), (0.52, 0.30, 0.16), 0.4)
    lathe('Base', [(0, 0), (0.063, 0), (0.0665, 0.004), (0.0665, 0.014), (0.062, 0.021), (0.02, 0.022), (0, 0.022)], [W], uvs=(4, 6))
    lathe('Rod', [(0, 0.02), (0.0105, 0.02), (0.0105, 0.275), (0, 0.275)], [W], uvs=(1, 3))
    lathe('Finial', [(0, 0.272), (0.008, 0.272), (0.009, 0.282), (0.015, 0.288), (0.0175, 0.298), (0.0145, 0.309), (0.007, 0.314), (0, 0.315)], [W], uvs=(1, 6))
    N = 512; yy, xx = np.mgrid[0:N, 0:N] / N
    d = np.abs(((xx + yy) * 12) % 1 - 0.5) < 0.03; e = np.abs(((xx - yy) * 12) % 1 - 0.5) < 0.03
    pap = np.full((N, N, 3), 0.965); pap[d | e] = 0.89
    PAPER = img_mat('Kitchen Roll', np_img('paper', pap), 0.9); CORE = pmat('Card Core', (0.42, 0.26, 0.13), 0.8)
    lathe('Roll', [(0.0215, 0.024), (0.056, 0.024), (0.0575, 0.0265), (0.0575, 0.2595), (0.056, 0.262), (0.0215, 0.262)], [PAPER, CORE],
          midx=[0, 0, 0, 0, 0, 1], closed=True, uvs=(3, 4.2))
    return 'Vintageware Wooden Kitchen Tissue Roll Holder'

def garlic_press():             # b46a7d38  HomeWiz steel garlic press, 16 cm long, 4 cm chamber; no garlic
    S = STEEL()
    lathe('Chamber', [(0, 0), (0.0165, 0), (0.0185, 0.003), (0.0185, 0.038), (0.0205, 0.0405), (0.0205, 0.043), (0.0165, 0.043), (0.0165, 0.0035), (0, 0.0035)], [S])
    for k in range(13):
        a = 2 * math.pi * k / 12; rr = 0 if k == 12 else 0.009
        cyl(0.0011, 0.0006, (rr * math.cos(a), rr * math.sin(a), -0.0001), BLACK(), v=10)
    for y in (-0.0125, 0.0125): box((-0.026, y, 0.043), (0.016, 0.003, 0.022), S, bev=0.001)
    cyl(0.0032, 0.031, (-0.028, 0, 0.049), S, rot=(math.pi / 2, 0, 0), v=16)
    tube('Upper', [(-0.028, 0, 0.051), (-0.012, 0, 0.0585), (0.01, 0, 0.061), (0.045, 0, 0.064), (0.09, 0, 0.071), (0.135, 0, 0.079), (0.158, 0, 0.081)], 0.0045, S, sy=2.3)
    cyl(0.0152, 0.012, (0, 0, 0.049), S, v=48, bev=0.001); cyl(0.004, 0.012, (0, 0, 0.057), S)
    tube('Lower', [(0.018, 0, 0.034), (0.04, 0, 0.032), (0.08, 0, 0.025), (0.12, 0, 0.019), (0.155, 0, 0.017)], 0.0045, S, sy=2.3)
    return 'HomeWiz Steel Garlic Crusher'

def coconut_opener():           # b4867f61  Nestasia stainless coconut opener, 17 x 10 cm: pointed scoop blade, T-bar with black grips
    S = STEEL(); RUB = pmat('Black Rubber', (0.012, 0.012, 0.012), 0.7)
    def w(x):
        return 0.012 + 0.014 * (x / 0.045) if x < 0.045 else 0.026 * max((0.135 - x) / 0.09, 0) ** 0.85
    xs = [0.135 * i / 70 for i in range(71)]
    strip('Blade', xs, w, lambda x: 0.002, 0.0012, S, zcurl=lambda x, yn: 0.0055 * yn * yn * min(1, w(x) / 0.026))
    tube('Shaft', [(-0.036, 0, 0.0075), (-0.015, 0, 0.0055), (0.004, 0, 0.0035)], 0.0045, S)
    cyl(0.0048, 0.1, (-0.038, 0, 0.0075), S, rot=(math.pi / 2, 0, 0), v=24)
    for y in (-0.034, 0.034): cyl(0.0075, 0.032, (-0.038, y, 0.0075), RUB, rot=(math.pi / 2, 0, 0), v=24, bev=0.002)
    return 'Nestasia Stainless Steel Coconut Opener'

def butter_dish():              # 3bc04eb5  True Decor sage-green enamel butter dish with lid, 18 x 11 x 8 cm, steel handle, emblem
    G = pmat('Sage Enamel', (0.26, 0.44, 0.37), 0.32, coat=0.3); CR = pmat('Cream Enamel', (0.85, 0.82, 0.74), 0.4)
    b = slab('Base', rrect(0.18, 0.11, 0.018, 8), 0, 0.011, G, bevel=0.002); pocket(b, rrect(0.170, 0.100, 0.014, 8), 0.0035, 0.03)
    l = slab('Lid', rrect(0.164, 0.094, 0.016, 8), 0.0035, 0.074, G, bevel=0.009, bseg=5); pocket(l, rrect(0.158, 0.088, 0.013, 8), 0.0, 0.0705)
    tube('Handle', [(-0.032, 0, 0.072), (-0.028, 0, 0.083), (0, 0, 0.085), (0.028, 0, 0.083), (0.032, 0, 0.072)], 0.0028, STEEL())
    for x in (-0.032, 0.032): cyl(0.005, 0.003, (x, 0, 0.0735), STEEL(), v=20)
    cyl(0.017, 0.0012, (0, -0.0472, 0.04), CR, rot=(math.pi / 2, 0, 0), v=48)
    text('BUTTER', 0.0065, G, Matrix.Translation((0, -0.0482, 0.04)) @ Matrix.Rotation(math.pi / 2, 4, 'X'), ext=0.0002)
    return 'True Decor Butter Dish with Lid'

def mugs():                     # 04283da4  teal-glazed stoneware mugs, brown glaze inside and rim, raw clay foot; two of the set
    TEAL = pmat('Teal Glaze', (0.012, 0.12, 0.13), 0.18, coat=0.4); BR = pmat('Brown Glaze', (0.42, 0.13, 0.035), 0.22, coat=0.4)
    CLAY = pmat('Raw Clay', (0.55, 0.33, 0.2), 0.8)
    prof = [(0, 0.002), (0.034, 0), (0.0385, 0.004), (0.041, 0.011), (0.0435, 0.094), (0.0428, 0.0965), (0.040, 0.0955), (0.0378, 0.013), (0, 0.010)]
    for (x, y, rz) in ((-0.052, 0, 0.3), (0.052, 0.018, 2.6)):
        m = lathe('Mug', prof, [CLAY, TEAL, BR], midx=[0, 0, 1, 1, 2, 2, 2, 2], seg=72)
        h = tube('Handle', [(0.041, 0, 0.078), (0.06, 0, 0.076), (0.068, 0, 0.058), (0.064, 0, 0.034), (0.041, 0, 0.026)], 0.0058, TEAL, sy=1.5)
        for o in (m, h): o.matrix_world = Matrix.Translation((x, y, 0)) @ Matrix.Rotation(rz, 4, 'Z')
    return 'Teal Stoneware Coffee Mugs'

BUILD = dict(chopping_board=chopping_board, kmils=kmils, volrix=volrix, salt_pepper=salt_pepper, basting_brush=basting_brush, naalsa=naalsa,
             primeway=primeway, wood_rest=wood_rest, sink_mat=sink_mat, dish_mat=dish_mat, texro=texro, curd_maker=curd_maker,
             tissue_holder=tissue_holder, garlic_press=garlic_press, coconut_opener=coconut_opener, butter_dish=butter_dish, mugs=mugs)

def finish(key, title):
    for o in list(P):
        if o.name not in bpy.context.scene.objects: P.remove(o)
    bpy.ops.object.select_all(action='DESELECT')
    for o in P: o.select_set(True)
    bpy.context.view_layer.objects.active = P[0]
    bpy.ops.object.convert(target='MESH'); bpy.ops.object.join(); o = bpy.context.object; o.name = title
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    co = np.empty(len(o.data.vertices) * 3); o.data.vertices.foreach_get('co', co); co = co.reshape(-1, 3)
    lo, hi = co.min(0), co.max(0); sh = np.array([-(lo[0] + hi[0]) / 2, -(lo[1] + hi[1]) / 2, -lo[2]]); co += sh
    o.data.vertices.foreach_set('co', co.ravel()); o.data.update()
    if not o.data.uv_layers: o.data.uv_layers.new(name='UV')
    bpy.ops.object.shade_smooth_by_angle(angle=math.radians(35))
    dims = Vector(hi - lo); print('BUILT', key, [round(d, 3) for d in dims], len(o.data.polygons), 'faces')
    sc = bpy.context.scene; sc.render.engine = 'CYCLES'; sc.cycles.samples = 64; sc.view_settings.view_transform = 'AgX'
    w = bpy.data.worlds.new('w'); sc.world = w; w.use_nodes = True; w.node_tree.nodes['Background'].inputs['Color'].default_value = (0.75, 0.75, 0.74, 1)
    bpy.ops.mesh.primitive_plane_add(size=6); fl = bpy.context.object; fl.data.materials.append(pmat('Floor', (0.62, 0.6, 0.57), 0.6))
    sd = bpy.data.lights.new('s', 'SUN'); sd.energy = 2.5; sd.angle = math.radians(12); so = bpy.data.objects.new('s', sd); sc.collection.objects.link(so)
    so.rotation_euler = (math.radians(40), 0, math.radians(30))
    flat = dims.z < 0.25 * max(dims.x, dims.y)
    d = Vector((0.45, -1, 1.0) if flat else (0.6, -1, 0.55)).normalized(); tgt = Vector((0, 0, dims.z * 0.45))
    cd = bpy.data.cameras.new('c'); cd.lens = 50; cam = bpy.data.objects.new('c', cd); sc.collection.objects.link(cam); sc.camera = cam
    cam.location = tgt + d * dims.length * 1.75; cam.rotation_euler = (tgt - cam.location).to_track_quat('-Z', 'Y').to_euler()
    sc.render.resolution_x = sc.render.resolution_y = 700; sc.render.filepath = os.path.join(OUT, key + '_look.png'); bpy.ops.render.render(write_still=True)
    bpy.data.objects.remove(fl); activate(o)
    bpy.ops.export_scene.gltf(filepath=os.path.join(OUT, key + '.glb'), export_format='GLB', use_selection=True, export_apply=True, export_image_format='AUTO')

keys = list(BUILD) if WHICH == 'all' else WHICH.split(',')
for k in keys:
    try:
        reset(); title = BUILD[k](); finish(k, title)
    except Exception as e:
        import traceback; traceback.print_exc(); print('FAILED', k, e)
print('DONE')
