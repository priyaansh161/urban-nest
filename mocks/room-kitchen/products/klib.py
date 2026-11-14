# Shared Blender helpers for the kitchen product models (v2: photo-faithful).  Import from a product script run as
#   blender -b -P <product>.py -- <outdir>
import bpy, bmesh, math, os, sys
import numpy as np
from mathutils import Vector, Matrix

HERE = os.path.dirname(os.path.abspath(__file__))
TEX = os.path.abspath(os.path.join(HERE, '..', '..', 'room-living', 'textures', 'walnut_veneer'))
OUT = os.path.abspath(sys.argv[sys.argv.index('--') + 1]) if '--' in sys.argv else os.path.join(HERE, 'out2')
os.makedirs(OUT, exist_ok=True)
P = []

def reset():
    P.clear(); bpy.ops.wm.read_factory_settings(use_empty=True)
def link(o):
    bpy.context.scene.collection.objects.link(o); P.append(o); return o
def activate(o):
    bpy.ops.object.select_all(action='DESELECT'); o.select_set(True); bpy.context.view_layer.objects.active = o
def srgb(c):                                       # display colour -> linear
    return tuple(((x + 0.055) / 1.055) ** 2.4 if x > 0.04045 else x / 12.92 for x in c)

# ---------------- materials ----------------
def pmat(name, col, rough=0.5, metal=0.0, trans=0.0, ior=1.45, coat=0.0, coat_rough=0.05, display=True):
    m = bpy.data.materials.get(name)
    if m: return m
    m = bpy.data.materials.new(name); m.use_nodes = True; b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (*(srgb(col) if display else col), 1)
    b.inputs['Roughness'].default_value = rough; b.inputs['Metallic'].default_value = metal
    if trans: b.inputs['Transmission Weight'].default_value = trans
    b.inputs['IOR'].default_value = ior
    if coat: b.inputs['Coat Weight'].default_value = coat; b.inputs['Coat Roughness'].default_value = coat_rough
    return m
def see_through(name, col, alpha, rough=0.03, coat=0.0, glow=None):
    """Glass / liquid that reads on any page: tinted, partly transparent (glTF alphaMode BLEND), two-sided, glossy."""
    m = pmat(name, col, rough, coat=coat); b = m.node_tree.nodes['Principled BSDF']; b.inputs['Alpha'].default_value = alpha
    if glow: b.inputs['Emission Color'].default_value = (*srgb(glow), 1); b.inputs['Emission Strength'].default_value = 1.0
    try: m.surface_render_method = 'BLENDED'
    except Exception: pass
    m.use_backface_culling = False
    return m
def np_img(name, arr, alpha=False, noncolor=False):          # arr h x w x 3|4 in display values (or data if noncolor)
    h, w = arr.shape[:2]; img = bpy.data.images.new(name, w, h, alpha=alpha)
    px = np.ones((h, w, 4), np.float32); px[..., :arr.shape[2]] = arr; img.pixels.foreach_set(px.ravel()); img.pack()
    if noncolor: img.colorspace_settings.name = 'Non-Color'
    return img
def tex_mat(name, color_img=None, rough=0.5, metal=0.0, normal_img=None, nstr=0.5, rough_img=None, alpha=False, coat=0.0, trans=0.0, ior=1.45, col=None):
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree; b = nt.nodes['Principled BSDF']
    if color_img is not None:
        t = nt.nodes.new('ShaderNodeTexImage'); t.image = color_img; nt.links.new(t.outputs['Color'], b.inputs['Base Color'])
        if alpha:
            nt.links.new(t.outputs['Alpha'], b.inputs['Alpha'])
            try: m.surface_render_method = 'DITHERED'
            except Exception: pass
    elif col is not None: b.inputs['Base Color'].default_value = (*srgb(col), 1)
    b.inputs['Roughness'].default_value = rough; b.inputs['Metallic'].default_value = metal
    if trans: b.inputs['Transmission Weight'].default_value = trans
    b.inputs['IOR'].default_value = ior
    if coat: b.inputs['Coat Weight'].default_value = coat; b.inputs['Coat Roughness'].default_value = 0.04
    if rough_img is not None:                          # glTF wants roughness in G of a metal-rough map
        tr = nt.nodes.new('ShaderNodeTexImage'); tr.image = rough_img; rough_img.colorspace_settings.name = 'Non-Color'
        sp = nt.nodes.new('ShaderNodeSeparateColor'); nt.links.new(tr.outputs['Color'], sp.inputs['Color']); nt.links.new(sp.outputs['Green'], b.inputs['Roughness'])
    if normal_img is not None:
        tn = nt.nodes.new('ShaderNodeTexImage'); tn.image = normal_img; normal_img.colorspace_settings.name = 'Non-Color'
        nm = nt.nodes.new('ShaderNodeNormalMap'); nm.inputs['Strength'].default_value = nstr
        nt.links.new(tn.outputs['Color'], nm.inputs['Color']); nt.links.new(nm.outputs['Normal'], b.inputs['Normal'])
    return m
def height_to_normal(hm, strength=2.0):           # hm: h x w float 0..1 (tileable) -> normal map (OpenGL, display-free)
    gy, gx = np.gradient(hm.astype(np.float32))
    n = np.dstack([-gx * strength, gy * strength, np.ones_like(hm)]); n /= np.linalg.norm(n, axis=2, keepdims=True)
    return n * 0.5 + 0.5
def tile_noise(h, w, scale_y, scale_x, seed=0, octaves=3):   # tileable smooth noise via FFT filtering
    rng = np.random.default_rng(seed); out = np.zeros((h, w), np.float32)
    for o in range(octaves):
        f = np.fft.fft2(rng.normal(size=(h, w)))
        ky = np.fft.fftfreq(h)[:, None] * h; kx = np.fft.fftfreq(w)[None, :] * w
        g = np.exp(-((ky / (scale_y * 2 ** o)) ** 2 + (kx / (scale_x * 2 ** o)) ** 2))
        n = np.real(np.fft.ifft2(f * g)); n = (n - n.mean()) / (n.std() + 1e-9); out += n / (2 ** o)
    out = (out - out.min()) / (out.max() - out.min()); return out
def brushed_steel(name, along='u', rough=0.28, col=(0.80, 0.80, 0.79), N=512, seed=3, polished=False):
    """Stainless with real hairline brushing: streaky roughness + a faint normal, streaks along U (or V)."""
    if along == 'u': hm = tile_noise(N, N, 60, 0.6, seed)
    else: hm = tile_noise(N, N, 0.6, 60, seed)
    r = np.clip(rough + (hm - 0.5) * (0.06 if polished else 0.14), 0.04, 0.9)
    rimg = np_img(name + ' rough', np.dstack([r, r, r]), noncolor=True)
    nimg = np_img(name + ' nrm', height_to_normal(hm, 0.8), noncolor=True)
    return tex_mat(name, None, rough, 1.0, nimg, 0.25, rimg, col=col)
_GRAIN = {}
def wood(name, dark, light, rough=0.5, contrast=0.6, along='u', size=1024):
    if 'g' not in _GRAIN:
        im = bpy.data.images.load(os.path.join(TEX, 'walnut_veneer_Diffuse_2k.jpg')); im.scale(size, size)
        px = np.empty(size * size * 4, np.float32); im.pixels.foreach_get(px); px = px.reshape(size, size, 4)
        L = px[..., :3] @ np.array([0.3, 0.59, 0.11]); lo, hi = np.percentile(L, [2, 98]); _GRAIN['g'] = np.clip((L - lo) / (hi - lo), 0, 1)
    g = np.clip(0.5 + (_GRAIN['g'] - 0.5) * contrast, 0, 1)
    if along == 'v': g = g.T.copy()
    d, l = np.array(dark), np.array(light); img = np_img(name + ' grain', d + (l - d) * g[..., None])
    nrm = bpy.data.images.load(os.path.join(TEX, 'walnut_veneer_nor_gl_2k.jpg')); nrm.scale(size, size)
    return tex_mat(name, img, rough, 0.0, nrm, 0.35)

# ---------------- geometry ----------------
def mesh_obj(name, bm, mats):
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free(); o = bpy.data.objects.new(name, me)
    for m in mats: me.materials.append(m)
    return link(o)
def lathe(name, prof, mats, midx=None, seg=160, closed=False, uvs=(1, 1), smooth_prof=0):
    """Revolve an (r, z) profile about z. Ends at r=0 close it; closed=True joins last->first. UV: u around, v = profile length."""
    if smooth_prof: prof = [tuple(p) for p in cr([(r, 0, z) for r, z in prof], smooth_prof)]; prof = [(p[0], p[2]) for p in prof]; midx = None if midx is None else midx
    bm = bmesh.new(); uvl = bm.loops.layers.uv.new('UV'); n = len(prof)
    cum = [0.0]
    for i in range(1, n): cum.append(cum[-1] + math.dist(prof[i - 1], prof[i]))
    total = cum[-1] + (math.dist(prof[-1], prof[0]) if closed else 0)
    rings, info = [], {}
    for i, (r, z) in enumerate(prof):
        if r < 1e-7:
            v = bm.verts.new((0, 0, z)); info[v] = (i, None); rings.append([v])
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
            f = bm.faces.new(vs); f.material_index = (midx[i] if midx else 0)
            for lp in f.loops:
                ii, kk = info[lp.vert]
                u = (k + 0.5) if kk is None else (seg if (kk == 0 and k == seg - 1) else kk)
                v = total if (closed and (i, j) == (n - 1, 0) and ii == 0) else cum[ii]
                lp[uvl].uv = (u / seg * uvs[0], v * uvs[1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return mesh_obj(name, bm, mats)
def cyl_uv(o, z0, z1, seam_angle=math.pi / 2):
    """Cylindrical UV from world coords: u = angle (seam at seam_angle), v = (z - z0) / (z1 - z0)."""
    me = o.data
    if not me.uv_layers: me.uv_layers.new(name='UV')
    uv = me.uv_layers.active.data; mw = o.matrix_world
    for p in me.polygons:
        cs = [mw @ me.vertices[vi].co for vi in p.vertices]
        us = [((math.atan2(c.y, c.x) - seam_angle) % (2 * math.pi)) / (2 * math.pi) for c in cs]
        if max(us) - min(us) > 0.5: us = [u + 1 if u < 0.5 else u for u in us]
        for li, u, c in zip(p.loop_indices, us, cs): uv[li].uv = (u, (c.z - z0) / (z1 - z0))
def rrect(w, d, r, seg=12):
    pts = []
    for cx, cy, a0 in ((w / 2 - r, d / 2 - r, 0), (-w / 2 + r, d / 2 - r, 90), (-w / 2 + r, -d / 2 + r, 180), (w / 2 - r, -d / 2 + r, 270)):
        for k in range(seg + 1):
            a = math.radians(a0 + 90 * k / seg); pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts
def superellipse(a, b, n=4.0, N=48):
    pts = []
    for k in range(N):
        t = 2 * math.pi * k / N; c, s = math.cos(t), math.sin(t)
        pts.append((a * math.copysign(abs(c) ** (2 / n), c), b * math.copysign(abs(s) ** (2 / n), s)))
    return pts
def slab(name, outer, z0, z1, m, bevel=0.0015, bseg=3, keep=True):
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
    bpy.ops.object.modifier_apply(modifier='c')
    if cutter in P: P.remove(cutter)
    bpy.data.objects.remove(cutter)
def cutter_box(c, d):
    bpy.ops.mesh.primitive_cube_add(size=1, location=c); o = bpy.context.object; o.scale = d; bpy.ops.object.transform_apply(scale=True); return o
def cutter_cyl(r, depth, loc, rot=(0, 0, 0), v=48):
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=depth, vertices=v, location=loc, rotation=rot); return bpy.context.object
def join_cutters(cs):
    bpy.ops.object.select_all(action='DESELECT')
    for c in cs: c.select_set(True)
    bpy.context.view_layer.objects.active = cs[0]; bpy.ops.object.join(); return bpy.context.object
def cyl(r, depth, loc, m, rot=(0, 0, 0), v=96, bev=0.0, bseg=3):
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=depth, vertices=v, location=loc, rotation=rot); o = bpy.context.object
    if bev: bv = o.modifiers.new('b', 'BEVEL'); bv.width = bev; bv.segments = bseg; bv.limit_method = 'ANGLE'; bpy.ops.object.modifier_apply(modifier='b')
    if m: o.data.materials.append(m)
    P.append(o); return o
def cr(pts, n=16):
    Pt = [Vector(p) for p in pts]; out = []
    for i in range(len(Pt) - 1):
        p0, p1, p2, p3 = Pt[max(i - 1, 0)], Pt[i], Pt[i + 1], Pt[min(i + 2, len(Pt) - 1)]
        for s in range(n):
            t = s / n; t2, t3 = t * t, t * t * t
            out.append(0.5 * (2 * p1 + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t2 + (-p0 + 3 * p1 - 3 * p2 + p3) * t3))
    out.append(Pt[-1]); return out
def sweep(name, path, m, r=None, profile=None, smooth=True, closed=False, n=16, twist_up=None, scale_fn=None):
    """Sweep a cross-section along a path. profile = list of (a, b) 2D points (closed) in the path's normal plane;
    default a circle of radius r (64 sides). scale_fn(t)->(sa, sb) tapers along t in 0..1. Real mesh, smooth, capped."""
    pts = cr(path, n) if (smooth and not closed) else [Vector(p) for p in path]
    if profile is None: profile = [(r * math.cos(2 * math.pi * k / 64), r * math.sin(2 * math.pi * k / 64)) for k in range(64)]
    N = len(pts); bm = bmesh.new(); rings = []
    up0 = Vector(twist_up) if twist_up else None
    prev_n = None
    for i, p in enumerate(pts):
        if closed: tng = (pts[(i + 1) % N] - pts[i - 1]).normalized()
        else: tng = (pts[min(i + 1, N - 1)] - pts[max(i - 1, 0)]).normalized()
        if up0 is not None: nrm = (up0 - tng * up0.dot(tng)).normalized()
        else:
            if prev_n is None:
                a = Vector((0, 0, 1)) if abs(tng.z) < 0.9 else Vector((1, 0, 0)); prev_n = (a - tng * a.dot(tng)).normalized()
            nrm = (prev_n - tng * prev_n.dot(tng)).normalized(); prev_n = nrm
        bin_ = tng.cross(nrm)
        sa, sb = scale_fn(i / (N - 1)) if scale_fn else (1, 1)
        rings.append([bm.verts.new(p + nrm * (a * sa) + bin_ * (b * sb)) for a, b in profile])
    K = len(profile)
    for i in range(N - (0 if closed else 1)):
        a, b = rings[i], rings[(i + 1) % N]
        for k in range(K): bm.faces.new((a[k], a[(k + 1) % K], b[(k + 1) % K], b[k]))
    if not closed:
        bm.faces.new(rings[0][::-1]); bm.faces.new(rings[-1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return mesh_obj(name, bm, [m])
def text_mesh(body, size, m, mw, ext=0.0003, font=None):
    cu = bpy.data.curves.new('t', 'FONT'); cu.body = body; cu.size = size; cu.extrude = ext; cu.align_x = 'CENTER'; cu.align_y = 'CENTER'
    if font: cu.font = bpy.data.fonts.load(font)
    o = bpy.data.objects.new('t', cu); bpy.context.scene.collection.objects.link(o); cu.materials.append(m); o.matrix_world = mw
    activate(o); bpy.ops.object.convert(target='MESH'); P.append(o); return o
def planar_uv(o, sx, sy, ox=0.5, oy=0.5, axes='xy'):
    me = o.data
    if not me.uv_layers: me.uv_layers.new(name='UV')
    uv = me.uv_layers.active.data; mw = o.matrix_world
    for p in me.polygons:
        for li, vi in zip(p.loop_indices, p.vertices):
            co = mw @ me.vertices[vi].co; a, b = getattr(co, axes[0]), getattr(co, axes[1]); uv[li].uv = (a / sx + ox, b / sy + oy)
def cube_uv(o, size):
    activate(o)
    if not o.data.uv_layers: o.data.uv_layers.new(name='UV')
    bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.select_all(action='SELECT'); bpy.ops.uv.cube_project(cube_size=size); bpy.ops.object.mode_set(mode='OBJECT')
def subdiv(o, levels=2):
    activate(o); md = o.modifiers.new('s', 'SUBSURF'); md.levels = levels; md.render_levels = levels; bpy.ops.object.modifier_apply(modifier='s')

# ---------------- strokes: hand-lettering into a texture ----------------
def stroke_mask(h, w, polylines, radius_px):
    """Rasterise monoline strokes (lists of (x_px, y_px)) into an anti-aliased mask."""
    m = np.zeros((h, w), np.float32); R = int(math.ceil(radius_px + 2))
    yy, xx = np.mgrid[-R:R + 1, -R:R + 1]
    for pl in polylines:
        pts = [Vector((x, y, 0)) for x, y in pl]
        dense = []
        for a, b in zip(pts, pts[1:]):
            n = max(int((b - a).length / 0.8), 1)
            for s in range(n): dense.append(a.lerp(b, s / n))
        dense.append(pts[-1])
        for p in dense:
            cx, cy = int(round(p.x)), int(round(p.y))
            if cx < -R or cy < -R or cx >= w + R or cy >= h + R: continue
            d = np.hypot(xx + cx - p.x, yy + cy - p.y); v = np.clip(radius_px + 0.5 - d, 0, 1)
            y0, y1, x0, x1 = cy - R, cy + R + 1, cx - R, cx + R + 1
            sy0, sx0 = max(0, -y0), max(0, -x0); y0c, x0c = max(y0, 0), max(x0, 0); y1c, x1c = min(y1, h), min(x1, w)
            m[y0c:y1c, x0c:x1c] = np.maximum(m[y0c:y1c, x0c:x1c], v[sy0:sy0 + (y1c - y0c), sx0:sx0 + (x1c - x0c)])
    return m
# Tall, skinny monoline capitals (farmhouse hand-lettering), in a 0..1 tall, 0..W wide box; each glyph = list of polylines
def _arc(cx, cy, rx, ry, a0, a1, n=14):
    return [(cx + rx * math.cos(math.radians(a0 + (a1 - a0) * k / n)), cy + ry * math.sin(math.radians(a0 + (a1 - a0) * k / n))) for k in range(n + 1)]
GLYPHS = {
    'S': [[(p[0], p[1]) for p in [tuple(v[:2]) for v in cr([(0.40, 0.88, 0), (0.30, 0.98, 0), (0.15, 0.99, 0), (0.04, 0.88, 0), (0.06, 0.70, 0), (0.22, 0.55, 0), (0.38, 0.40, 0), (0.44, 0.20, 0), (0.36, 0.04, 0), (0.20, 0.0, 0), (0.06, 0.06, 0), (0.0, 0.16, 0)], 10)]]],
    'A': [[(0.0, 0.0), (0.24, 1.0), (0.48, 0.0)], [(0.07, 0.30), (0.41, 0.30)]],
    'L': [[(0.04, 1.0), (0.04, 0.0), (0.42, 0.0)]],
    'T': [[(0.0, 1.0), (0.48, 1.0)], [(0.24, 1.0), (0.24, 0.0)]],
    'P': [[(0.04, 0.0), (0.04, 1.0), (0.22, 1.0)] + _arc(0.22, 0.78, 0.22, 0.22, 90, -90)[1:] + [(0.04, 0.56)]],
    'E': [[(0.40, 1.0), (0.04, 1.0), (0.04, 0.0), (0.40, 0.0)], [(0.04, 0.53), (0.34, 0.53)]],
    'R': [[(0.04, 0.0), (0.04, 1.0), (0.22, 1.0)] + _arc(0.22, 0.78, 0.22, 0.22, 90, -90)[1:] + [(0.04, 0.56)], [(0.18, 0.56), (0.46, 0.0)]],
    'B': [[(0.04, 0.0), (0.04, 1.0), (0.22, 1.0)] + _arc(0.22, 0.77, 0.2, 0.23, 90, -90)[1:] + [(0.04, 0.54), (0.24, 0.54)] + _arc(0.24, 0.27, 0.22, 0.27, 90, -90)[1:] + [(0.04, 0.0)]],
    'U': [[(0.04, 1.0), (0.04, 0.25)] + _arc(0.24, 0.25, 0.2, 0.25, 180, 360)[1:] + [(0.44, 1.0)]],
}
def word_strokes(word, origin, along, up, cap, wratio=1.0, gap=0.22):
    """Lay out a word: origin = start of baseline (px), along = unit baseline direction, up = unit up direction, cap = cap height px."""
    out = []; x = 0.0
    for ch in word:
        if ch == ' ': x += 0.35 * cap; continue
        g = GLYPHS[ch]; gw = max(max(p[0] for p in pl) for pl in g)
        for pl in g:
            out.append([(origin[0] + along[0] * (x + px * cap * wratio) + up[0] * py * cap, origin[1] + along[1] * (x + px * cap * wratio) + up[1] * py * cap) for px, py in pl])
        x += (gw * wratio + gap) * cap
    return out, x - gap * cap

# ---------------- finish: join, centre, check render, export ----------------
def finish(key, title, view=(0.6, -1, 0.55), smooth_angle=40, keep_sharp=False):
    for o in list(P):
        if o.name not in bpy.context.scene.objects: P.remove(o)
    for o in P:                                   # one UV map name everywhere, or joined parts sample the wrong map
        if o.type != 'MESH': continue
        if not o.data.uv_layers: o.data.uv_layers.new(name='UV')
        o.data.uv_layers[0].name = 'UV'
        while len(o.data.uv_layers) > 1: o.data.uv_layers.remove(o.data.uv_layers[1])
    bpy.ops.object.select_all(action='DESELECT')
    for o in P: o.select_set(True)
    bpy.context.view_layer.objects.active = P[0]
    bpy.ops.object.convert(target='MESH'); bpy.ops.object.join(); o = bpy.context.object; o.name = title
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    co = np.empty(len(o.data.vertices) * 3); o.data.vertices.foreach_get('co', co); co = co.reshape(-1, 3)
    lo, hi = co.min(0), co.max(0); co += np.array([-(lo[0] + hi[0]) / 2, -(lo[1] + hi[1]) / 2, -lo[2]])
    o.data.vertices.foreach_set('co', co.ravel()); o.data.update()
    if not o.data.uv_layers: o.data.uv_layers.new(name='UV')
    bpy.ops.object.shade_smooth_by_angle(angle=math.radians(smooth_angle))
    dims = Vector(hi - lo); print('BUILT', key, [round(d, 4) for d in dims], len(o.data.polygons), 'faces')
    sc = bpy.context.scene; sc.render.engine = 'CYCLES'; sc.cycles.samples = 96; sc.view_settings.view_transform = 'AgX'
    w = bpy.data.worlds.new('w'); sc.world = w; w.use_nodes = True; w.node_tree.nodes['Background'].inputs['Color'].default_value = (0.8, 0.8, 0.8, 1)
    bpy.ops.mesh.primitive_plane_add(size=8); fl = bpy.context.object; fl.data.materials.append(pmat('Floor', (0.85, 0.84, 0.82), 0.6))
    sd = bpy.data.lights.new('s', 'SUN'); sd.energy = 2.2; sd.angle = math.radians(15); so = bpy.data.objects.new('s', sd); sc.collection.objects.link(so)
    so.rotation_euler = (math.radians(40), 0, math.radians(30))
    d = Vector(view).normalized(); tgt = Vector((0, 0, dims.z * 0.45))
    cd = bpy.data.cameras.new('c'); cd.lens = 50; cam = bpy.data.objects.new('c', cd); sc.collection.objects.link(cam); sc.camera = cam
    cam.location = tgt + d * dims.length * 1.7; cam.rotation_euler = (tgt - cam.location).to_track_quat('-Z', 'Y').to_euler()
    sc.render.resolution_x = sc.render.resolution_y = 800; sc.render.filepath = os.path.join(OUT, key + '_look.png'); bpy.ops.render.render(write_still=True)
    bpy.data.objects.remove(fl); activate(o)
    bpy.ops.export_scene.gltf(filepath=os.path.join(OUT, key + '.glb'), export_format='GLB', use_selection=True, export_apply=True, export_image_format='AUTO')
    return o

def shell(name, xs, wfun, zfun, t, m, nv=48, uvscale=(5, 5)):
    """A thin sheet over a plan outline: for each x in xs a row across y in [-w(x), w(x)], top surface z = zfun(x, y);
    the underside is the top pushed down along its normal by t; edges closed. For dishes, spoon rests, scoops, hooks."""
    import numpy as _np
    X = _np.array(xs); rows = []
    for x in X:
        w = max(wfun(x), 1e-5); ys = _np.sin(_np.linspace(-math.pi / 2, math.pi / 2, nv + 1)) * w    # denser near the rim
        rows.append([(x, y, zfun(x, y)) for y in ys])
    T = _np.array(rows)                                          # (nx, nv+1, 3)
    dx = _np.gradient(T, axis=0); dy = _np.gradient(T, axis=1)
    n = _np.cross(dx, dy); n /= _np.linalg.norm(n, axis=2, keepdims=True) + 1e-12
    n[n[..., 2] < 0] *= -1
    B = T - n * t
    bm = bmesh.new(); uvl = bm.loops.layers.uv.new('UV')
    vt = [[bm.verts.new(tuple(p)) for p in row] for row in T]; vb = [[bm.verts.new(tuple(p)) for p in row] for row in B]
    def face(vs):
        try:
            f = bm.faces.new(vs)
            for lp in f.loops: lp[uvl].uv = (lp.vert.co.x * uvscale[0], lp.vert.co.y * uvscale[1])
        except ValueError: pass
    nx = len(X)
    for i in range(nx - 1):
        for j in range(nv):
            face((vt[i][j], vt[i + 1][j], vt[i + 1][j + 1], vt[i][j + 1])); face((vb[i][j], vb[i][j + 1], vb[i + 1][j + 1], vb[i + 1][j]))
        face((vt[i][0], vb[i][0], vb[i + 1][0], vt[i + 1][0])); face((vt[i][nv], vt[i + 1][nv], vb[i + 1][nv], vb[i][nv]))
    for i in (0, nx - 1):
        for j in range(nv): face((vt[i][j], vt[i][j + 1], vb[i][j + 1], vb[i][j]))
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=2e-6); bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return mesh_obj(name, bm, [m])
def smoothstep(a): a = min(max(a, 0.0), 1.0); return a * a * (3 - 2 * a)
