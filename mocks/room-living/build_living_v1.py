# Living room "The Heritage Lounge", laid out from mocks/room-refs/living2/lounge-v1.jpg (see LAYOUT.md).
# Same pipeline as the bedroom (build_bedroom_v1.py): grid shells + scanned textures, every built surface gets an image
# lightmap from one Cycles bake, products in placements.json stand in for the bake and are removed before export.
#   blender -b -P build_living_v1.py -- <room-living dir> [quick]
# Metres: x -2.6..2.6 (left..right), y -2.1..2.1 (front wall .. back wall), z 0..3.0. Blender y = -three.js z.
import bpy, bmesh, math, sys, os, tempfile, json
import numpy as np
from mathutils import Vector

ARGS = sys.argv[sys.argv.index('--') + 1:]
OUT = os.path.abspath(ARGS[0]); QUICK = 'quick' in ARGS; FAST = 'fast' in ARGS     # fast: a coarse bake (12 samples, 256 px maps) + export, to check cameras and layout in the viewer
TMP = tempfile.mkdtemp(prefix='liv1_')
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
X0, X1, Y0, Y1, H = -2.6, 2.6, -2.1, 2.1, 3.0
STEP = 0.08
WARM = (1.0, 0.80, 0.55)
rng = np.random.default_rng(11)
sys.path.insert(0, os.path.join(OUT, '..'))
import staging_lib as SL

# ---------------------------------------------------------------- materials
def mat(name, color, rough=0.5, metal=0.0, emit=None, alpha=None):
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = color; b.inputs['Roughness'].default_value = rough; b.inputs['Metallic'].default_value = metal
    if emit: b.inputs['Emission Color'].default_value = emit[0]; b.inputs['Emission Strength'].default_value = emit[1]
    if alpha is not None:
        b.inputs['Alpha'].default_value = alpha
        try: m.surface_render_method = 'BLENDED'
        except Exception: pass
    return m

TEXDIR = os.path.join(OUT, 'textures')
def scan_img(rel, size, colour=True, tint=None, recolour=None, contrast=1.0):
    img = bpy.data.images.load(os.path.join(TEXDIR, rel))
    if max(img.size) > size: img.scale(size, size)
    if tint or recolour or contrast != 1.0:
        px = np.array(img.pixels[:], dtype=np.float32).reshape(-1, 4)
        if recolour:     # keep the weave, change the colour: luminance (mean 1, softened) times the new colour
            l = px[:, :3] @ np.array([0.2126, 0.7152, 0.0722], dtype=np.float32); l = 1 + (l / max(1e-4, l.mean()) - 1) * contrast
            px[:, :3] = l[:, None] * np.array(recolour, dtype=np.float32)
        elif contrast != 1.0: m_ = px[:, :3].mean(0); px[:, :3] = m_ + (px[:, :3] - m_) * contrast   # the nubs of a bouclé read at room distance
        if tint: px[:, :3] *= np.array(tint, dtype=np.float32)
        px[:, :3] = np.clip(px[:, :3], 0, 1); img.pixels.foreach_set(px.ravel())
    if not colour: img.colorspace_settings.name = 'Non-Color'
    img.pack(); return img

def pbr(name, color_img, normal_img, rough_img, rough=None):
    """A material from a colour image, an OpenGL normal map and a roughness image (or a flat roughness)."""
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree; b = nt.nodes['Principled BSDF']
    tc = nt.nodes.new('ShaderNodeTexImage'); tc.image = color_img; nt.links.new(tc.outputs['Color'], b.inputs['Base Color'])
    if rough_img:
        tr = nt.nodes.new('ShaderNodeTexImage'); tr.image = rough_img; nt.links.new(tr.outputs['Color'], b.inputs['Roughness'])
    else: b.inputs['Roughness'].default_value = rough
    tn = nt.nodes.new('ShaderNodeTexImage'); tn.image = normal_img
    nm = nt.nodes.new('ShaderNodeNormalMap'); nt.links.new(tn.outputs['Color'], nm.inputs['Color']); nt.links.new(nm.outputs['Normal'], b.inputs['Normal'])
    return m

def ph(name, a, size=2048, tint=None, recolour=None, contrast=1.0):
    """Poly Haven scan set textures/<a>/<a>_{diff,nor_gl,rough}_2k.jpg"""
    f = lambda k: '%s/%s_%s_2k.jpg' % (a, a, k)
    return pbr(name, scan_img(f('diff'), size, tint=tint, recolour=recolour, contrast=contrast), scan_img(f('nor_gl'), 1024, False), scan_img(f('rough'), 512, False))

# ---------------------------------------------------------------- helpers
SHELL = []
def grid(name, origin, u, v, m, tile=2.4, holes=()):
    """A flat surface of STEP-sized quads (u x v points into the room) with texture UVs at real scale and a 0..1 lightmap
    UV. holes: (i0, i1, j0, j1) face ranges left out (the window and the walk-in opening)."""
    origin, u, v = Vector(origin), Vector(u), Vector(v)
    ul, vl = u.length, v.length; nx, ny = max(1, round(ul / STEP)), max(1, round(vl / STEP))
    verts = [tuple(origin + u * (i / nx) + v * (j / ny)) for j in range(ny + 1) for i in range(nx + 1)]
    faces = [(j * (nx + 1) + i, j * (nx + 1) + i + 1, (j + 1) * (nx + 1) + i + 1, (j + 1) * (nx + 1) + i) for j in range(ny) for i in range(nx)
             if not any(i0 <= i < i1 and j0 <= j < j1 for i0, i1, j0, j1 in holes)]
    me = bpy.data.meshes.new('Shell_' + name); me.from_pydata(verts, [], faces)
    uv = me.uv_layers.new(name='UV')
    for poly in me.polygons:
        for li, vi in zip(poly.loop_indices, poly.vertices):
            uv.data[li].uv = ((vi % (nx + 1)) * ul / nx / tile, (vi // (nx + 1)) * vl / ny / tile)
    lm = me.uv_layers.new(name='LM')
    for poly in me.polygons:
        for li, vi in zip(poly.loop_indices, poly.vertices):
            lm.data[li].uv = ((vi % (nx + 1)) / nx, (vi // (nx + 1)) / ny)
    me.uv_layers.active = lm
    ob = bpy.data.objects.new('Shell_' + name, me); scene.collection.objects.link(ob); me.materials.append(m)
    SHELL.append((ob, ul, vl)); return ob

def box(name, loc, dim, m, bevel=0.0, rot=(0, 0, 0), segs=3):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc, rotation=rot)
    o = bpy.context.active_object; o.name = name; o.scale = dim
    bpy.ops.object.transform_apply(scale=True); o.data.materials.append(m)
    if bevel:
        bv = o.modifiers.new('Bevel', 'BEVEL'); bv.width = bevel; bv.segments = segs; bpy.ops.object.modifier_apply(modifier=bv.name)
    return o

def cyl(name, loc, r, h, m, rot=(0, 0, 0), seg=32, r2=None):
    if r2 is None: bpy.ops.mesh.primitive_cylinder_add(vertices=seg, radius=r, depth=h, location=loc, rotation=rot)
    else: bpy.ops.mesh.primitive_cone_add(vertices=seg, radius1=r, radius2=r2, depth=h, location=loc, rotation=rot)
    o = bpy.context.active_object; o.name = name; o.data.materials.append(m); bpy.ops.object.shade_smooth(); return o

def join(objs, name):
    bpy.ops.object.select_all(action='DESELECT')
    for o in objs: o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]; bpy.ops.object.join(); bpy.context.active_object.name = name
    return bpy.context.active_object

def apply_all(o):
    bpy.ops.object.select_all(action='DESELECT'); o.select_set(True); bpy.context.view_layer.objects.active = o
    for md in list(o.modifiers): bpy.ops.object.modifier_apply(modifier=md.name)

def smooth(o):
    o.data.polygons.foreach_set('use_smooth', [True] * len(o.data.polygons)); o.data.update()

def world_uv(o, tile, swap=False):
    """Texture UVs from world position, projected along each face's main axis (real scale, straight grain).
    swap turns the texture 90 degrees."""
    me = o.data; uv = me.uv_layers[0] if me.uv_layers else me.uv_layers.new(name='UVMap'); mw = o.matrix_world
    for poly in me.polygons:
        ax = max(range(3), key=lambda i: abs(poly.normal[i]))
        for li, vi in zip(poly.loop_indices, poly.vertices):
            p = mw @ me.vertices[vi].co
            a, b = ((p.y, p.z), (p.x, p.z), (p.x, p.y))[ax]
            uv.data[li].uv = (b / tile, a / tile) if swap else (a / tile, b / tile)

def bounds(objs):
    mn = Vector((1e9,) * 3); mx = Vector((-1e9,) * 3)
    for o in objs:
        if o.type != 'MESH': continue
        for c in o.bound_box:
            w = o.matrix_world @ Vector(c)
            for i in range(3): mn[i] = min(mn[i], w[i]); mx[i] = max(mx[i], w[i])
    return mn, mx

def import_glb(path):
    before = set(bpy.data.objects); bpy.ops.import_scene.gltf(filepath=path)
    return [o for o in bpy.data.objects if o not in before]

def place(d):
    """The viewer's placeItem() in Blender (see the Quiet Bath build). three.js (x, y, z) is Blender (x, -z, y)."""
    new = import_glb(os.path.join(OUT, 'products', d['file']))
    root = bpy.data.objects.new('Place ' + d['name'], None); scene.collection.objects.link(root)
    inner = bpy.data.objects.new('Place inner', None); scene.collection.objects.link(inner); inner.parent = root
    for o in new:
        if o.parent is None: o.parent = inner
    bpy.context.view_layer.update(); mn, mx = bounds(new); sz = mx - mn
    s = d['length'] / max(sz.x, sz.y) if 'length' in d else d['height'] / sz.z
    inner.scale = (s, s, s); bpy.context.view_layer.update(); mn, mx = bounds(new); c = (mn + mx) / 2
    inner.location -= Vector((c.x, c.y, mx.z if d.get('hang') else mn.z)); body_h = mx.z - mn.z   # hang: placed by its top (ceiling pieces)
    x, y, z = d['pos']; root.location = (x, -z, y); root.rotation_euler.z = d.get('rotY', 0)
    if 'alignBack' in d:
        bpy.context.view_layer.update(); mn, mx = bounds(new); root.location.y += -d['alignBack'] - mx.y
    if 'alignLeft' in d:
        bpy.context.view_layer.update(); mn, mx = bounds(new); root.location.x += d['alignLeft'] - mn.x
    if 'alignRight' in d:
        bpy.context.view_layer.update(); mn, mx = bounds(new); root.location.x += d['alignRight'] - mx.x
    made = new + [root, inner]
    if d.get('flowers'):
        fnew = import_glb(os.path.join(OUT, 'products', d['flowers']))
        fl = bpy.data.objects.new('Place flowers', None); scene.collection.objects.link(fl); fl.parent = root
        for o in fnew:
            if o.parent is None: o.parent = fl
        fl.location = (0, 0, body_h - 0.03); fl.scale = ((d.get('flowerHeight') or 0.36) / 0.44,) * 3; fl.rotation_euler.z = -d.get('rotY', 0)
        made += fnew + [fl]
    bpy.context.view_layer.update(); return made

def world_points(objs):
    out = []
    for o in objs:
        if o.type != 'MESH' or not len(o.data.vertices): continue
        a = np.empty(len(o.data.vertices) * 3, np.float32); o.data.vertices.foreach_get('co', a)
        mw = np.array(o.matrix_world, dtype=np.float32); out.append(a.reshape(-1, 3) @ mw[:3, :3].T + mw[:3, 3])
    return np.concatenate(out)

LM = []
def lightmap_prep(o, res, new_uv=True):
    """Own lightmap UV layout (or the active one) + a float image every material of o bakes into (materials copied)."""
    me = o.data; me.uv_layers[0].active_render = True
    w, h = res if isinstance(res, tuple) else (res, res)
    if FAST: w, h = min(w, 256), min(h, 256)
    if new_uv:
        lm = me.uv_layers.new(name='LM'); me.uv_layers.active = lm
        bpy.ops.object.select_all(action='DESELECT'); o.select_set(True); bpy.context.view_layer.objects.active = o
        bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.uv.smart_project(angle_limit=math.radians(60), island_margin=0.006)
        bpy.ops.object.mode_set(mode='OBJECT')
    img = bpy.data.images.new('LMF_' + o.name, w, h, alpha=False, float_buffer=True)
    for slot in o.material_slots:
        m = slot.material.copy(); m.name = 'LM ' + slot.material.name; slot.material = m
        t = m.node_tree.nodes.new('ShaderNodeTexImage'); t.image = img; t.name = 'LM_BAKE'; m.node_tree.nodes.active = t
    LM.append((o, img, me.uv_layers.active.name))

def gblur(a, sigma=1.5):
    r = 4; k = np.exp(-np.arange(-r, r + 1) ** 2 / (2 * sigma * sigma)); k /= k.sum()
    for axis in (0, 1):
        p = np.pad(a, [(r, r) if i == axis else (0, 0) for i in range(a.ndim)], mode='edge')
        a = sum(k[i] * np.take(p, range(i, i + a.shape[axis]), axis=axis) for i in range(2 * r + 1))
    return a

def wrap_blur(a, sigma):
    """Gaussian blur of a seamless 2-D image, wrapping round its edges (stays seamless)."""
    h, w = a.shape; fy = np.fft.fftfreq(h)[:, None]; fx = np.fft.fftfreq(w)[None, :]
    return np.real(np.fft.ifft2(np.fft.fft2(a) * np.exp(-2 * (math.pi * sigma) ** 2 * (fx * fx + fy * fy))))

def save_img(name, rgb, colour=True):
    h, w = rgb.shape[:2]; rgba = np.ones((h, w, 4), dtype=np.float32); rgba[..., :3] = rgb
    im = bpy.data.images.new(name, w, h, alpha=False); im.pixels.foreach_set(rgba.ravel())
    p = os.path.join(TMP, name + '.png'); im.filepath_raw = p; im.file_format = 'PNG'; im.save()
    out = bpy.data.images.load(p)
    if not colour: out.colorspace_settings.name = 'Non-Color'
    out.pack(); return out

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

# ---------------------------------------------------------------- products: shadow casters for the bake, lamps lit
PL = json.load(open(os.path.join(OUT, 'placements.json')))
CASTERS, LAMPS = [], []
for d in [x for x in PL['staging'] if not x.get('lm')] + PL['products']:
    if 'file' not in d: continue
    made = place(d); CASTERS += made
    if not d.get('light'): continue
    if d['light'].get('at'): LAMPS.append((d['name'], d['light']['w'], np.array(d['light']['at']))); continue
    p = world_points(made); zmin, zmax = p[:, 2].min(), p[:, 2].max()
    ax = p[p[:, 2] > zmax - 0.02][:, :2].mean(0); rad = lambda z0: np.linalg.norm(p[(p[:, 2] > z0) & (p[:, 2] <= z0 + 0.01)][:, :2] - ax, axis=1)
    r0 = np.linalg.norm(p[p[:, 2] > zmax - 0.04][:, :2] - ax, axis=1).max(); z = zmax - 0.03
    while z > zmin and len(rad(z - 0.01)) and rad(z - 0.01).max() > 0.5 * r0: z -= 0.01
    LAMPS.append((d['name'], d['light']['w'], np.array([ax[0], ax[1], z - 0.03]))); print('LAMP', d['name'], LAMPS[-1][2])
for nm, c in zip(('Brass A', 'Brass B'), LAMP_PTS): LAMPS.append((nm, 22, np.array(c)))
for d in PL['products']:
    if d['name'].startswith('Victorian'):
        pass

if 'wb' in ARGS:       # fast workbench views for checking shapes (no lighting, seconds not minutes)
    scene.render.engine = 'BLENDER_WORKBENCH'; sh = scene.display.shading; sh.light = 'STUDIO'; sh.color_type = 'TEXTURE'
    scene.world = bpy.data.worlds.new('w'); scene.world.color = (0.35, 0.35, 0.35)
    cdw = bpy.data.cameras.new('c'); cw = bpy.data.objects.new('c', cdw); scene.collection.objects.link(cw); scene.camera = cw
    for o in bpy.data.objects:
        if o.name.startswith(('Shell_Ceiling', 'LM_Cornice', 'LM_CeilingRose')): o.hide_render = True
    shots = {'sofa': ((0.7, -0.9, 1.1), (2.3, 0.6, 0.5), 20), 'frontwin': ((-0.7, 0.2, 1.4), (-0.7, -2.1, 1.5), 22), 'cornerA': ((2.3, -1.9, 1.6), (-1.5, 1.2, 0.8), 16),
             'cornerB': ((-2.4, -1.9, 1.5), (1.5, 1.0, 0.8), 16), 'back': ((0.0, -1.0, 1.4), (-0.4, 2.1, 1.0), 20), 'sofa2': ((1.0, 1.0, 1.6), (2.4, -0.6, 0.5), 20)}
    for k, (l, t, ln) in shots.items():
        cdw.lens = ln; cw.location = l; cw.rotation_euler = (Vector(t) - Vector(l)).to_track_quat('-Z', 'Y').to_euler()
        scene.render.resolution_x, scene.render.resolution_y = 1200, 700; scene.render.filepath = OUT + '/wb_%s.png' % k; bpy.ops.render.render(write_still=True)
    for nm in ('Cushion Teal', 'Cushion Teal 2', 'LM_ShuttersF'):
        o = bpy.data.objects[nm]; mn, mx = bounds([o]); print('BOUNDS', nm, [round(v, 2) for v in mn], [round(v, 2) for v in mx], len(o.data.vertices))
    exec(open(os.path.join(OUT, 'check_overlaps_living.py')).read())
    print('DONE wb'); sys.exit(0)

for o in [bpy.data.objects[n] for n in _order if n in bpy.data.objects]: print('TRIS', o.name, sum(len(pg.vertices) - 2 for pg in o.data.polygons))
for o in LMX: lightmap_prep(o, LMRES.get(o.name, 1024 if o.name not in ('LM_Skirting', 'LM_Inlay', 'LM_CeilingRose') else 512))
for ob, ul, vl in SHELL:
    d = 0.009 if 'Ceiling' in ob.name else 0.0045
    if ob.name == 'Shell_Rug': lightmap_prep(ob, (1024, 720), new_uv=False); continue
    lightmap_prep(ob, (max(16, min(1024, round(ul / d))), max(16, min(1024, round(vl / d)))), new_uv=False)

# ---------------------------------------------------------------- lights (night: chandelier candles, brass lamps, street lamps)
def area(name, loc, sx, sy, energy, color, rot):
    ld = bpy.data.lights.new(name, 'AREA'); ld.energy = energy; ld.color = color; ld.shape = 'RECTANGLE'; ld.size = sx; ld.size_y = sy
    lo = bpy.data.objects.new(name, ld); lo.location = loc; lo.rotation_euler = rot; scene.collection.objects.link(lo)
def aim(lo, target): lo.rotation_euler = (Vector(target) - lo.location).to_track_quat('-Z', 'Y').to_euler()
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
area('Fill', (0.15, 0.1, H - 0.05), 4.0, 3.0, 30, (1.0, 0.92, 0.82), (0, 0, 0))
for nm, w, c in LAMPS + [('Chandelier', 160, np.array([0.15, 0.1, 2.30])), ('Chandelier Low', 40, np.array([0.15, 0.1, 2.0]))]:
    ld = bpy.data.lights.new('Lamp', 'POINT'); ld.energy = w; ld.color = WARM; ld.shadow_soft_size = 0.05
    lo = bpy.data.objects.new('Lamp ' + nm, ld); lo.location = Vector(c.tolist()); scene.collection.objects.link(lo)
world = bpy.data.worlds.new('W'); scene.world = world; world.use_nodes = True
world.node_tree.nodes['Background'].inputs['Color'].default_value = (0.04, 0.05, 0.08, 1); world.node_tree.nodes['Background'].inputs['Strength'].default_value = 0.3

# ---------------------------------------------------------------- bake light into every lightmap
scene.render.engine = 'CYCLES'; scene.cycles.device = 'CPU'
if not QUICK:
    scene.cycles.samples = 12 if FAST else 128
    scene.render.bake.target = 'IMAGE_TEXTURES'; scene.render.bake.margin = 8; scene.render.bake.use_clear = True
    bpy.ops.object.select_all(action='DESELECT')
    for o, _, _ in LM: o.select_set(True)
    bpy.context.view_layer.objects.active = LM[0][0]
    bpy.ops.object.bake(type='DIFFUSE', pass_filter={'DIRECT', 'INDIRECT'}, margin=8, use_clear=True)
    BAKED = {}
    for o, img, uvn in LM:
        w, h = img.size; BAKED[o.name] = gblur(np.array(img.pixels[:], dtype=np.float32).reshape(h, w, 4)[..., :3])
    room_names = {ob.name for ob, _, _ in SHELL if "Rug" not in ob.name}
    lum = np.concatenate([BAKED[n].reshape(-1, 3) for n in room_names]) @ np.array([0.2126, 0.7152, 0.0722])
    gain = 0.92 / max(1e-4, np.percentile(lum, 98.5)); print('BAKE gain', round(float(gain), 3), 'p50', round(float(np.percentile(lum, 50)), 3))
    LM_IMG = {}
    for o, img, uvn in LM:
        a = np.clip(BAKED[o.name] * gain, 0, 1); h, w = a.shape[:2]
        a = np.where(a <= 0.0031308, a * 12.92, 1.055 * np.power(a, 1 / 2.4) - 0.055)
        LM_IMG[o.name] = save_img('LM_' + o.name, a)
        print('LIGHTMAP', o.name, w, 'px, mean', round(float(a.mean()), 3))


# ---------------------------------------------------------------- previews: front, corner (like the reference), plan
scene.view_settings.view_transform = 'AgX'; scene.cycles.samples = 14 if QUICK else 96; scene.cycles.use_denoising = True
cam_d = bpy.data.cameras.new('Cam'); cam_d.lens = 18
cam = bpy.data.objects.new('Cam', cam_d); scene.collection.objects.link(cam)
tag = 'quick' if QUICK else 'v1'
def shot(name, loc, tgt, lens, res):
    cam_d.lens = lens; cam.location = loc; cam.rotation_euler = (Vector(tgt) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    if FAST or 'nopreview' in ARGS: return
    scene.camera = cam; scene.render.resolution_x, scene.render.resolution_y = res; scene.render.filepath = OUT + '/living_%s_%s.png' % (tag, name); bpy.ops.render.render(write_still=True)
R = (1000, 560) if QUICK else (1800, 1000)
shot('front', (0.0, Y0 + 0.15, 1.35), (0.0, Y1, 1.2), 18, R)
shot('corner', (-2.35, -1.9, 1.15), (1.3, 0.9, 1.0), 16, R)          # the reference's viewpoint: low, from a corner
shot('corner2', (2.3, -1.85, 1.5), (-1.2, 1.0, 1.1), 16, R)
shot('door', (-2.4, 1.7, 1.5), (1.4, -0.4, 0.9), 16, R)
shot('sofa', (0.7, -0.9, 1.1), (2.3, 0.6, 0.5), 20, R)
hide = [o for o, _, _ in SHELL if 'Ceiling' in o.name] + [o for o in LMX if o.name in ('LM_Cornice', 'LM_CeilingRose')] + [o for o in CASTERS if 'chandelier' in o.name.lower() or 'Chandelier' in o.name]
for o in hide: o.hide_render = True
pd = bpy.data.cameras.new('Plan'); pd.type = 'ORTHO'; pd.ortho_scale = 6.0
pc = bpy.data.objects.new('Plan', pd); scene.collection.objects.link(pc); pc.location = (0, 0, 8); pc.rotation_euler = (0, 0, 0)
if not (FAST or 'nopreview' in ARGS): scene.camera = pc; scene.render.resolution_x = scene.render.resolution_y = 1000; scene.render.filepath = OUT + '/living_%s_plan.png' % tag; bpy.ops.render.render(write_still=True)
for o in hide: o.hide_render = False
if QUICK: print('DONE quick'); sys.exit(0)

# ---------------------------------------------------------------- export: products out (the viewer places them), lightmaps in as emissive
for o in CASTERS: bpy.data.objects.remove(o)
for o, _, uvn in LM:
    for slot in o.material_slots:
        nt = slot.material.node_tree; b = nt.nodes['Principled BSDF']
        nt.nodes.remove(nt.nodes['LM_BAKE'])
        for n_ in list(nt.nodes):
            if n_.type == 'TEX_IMAGE' and not n_.inputs['Vector'].is_linked and uvn != o.data.uv_layers[0].name:
                um = nt.nodes.new('ShaderNodeUVMap'); um.uv_map = o.data.uv_layers[0].name; nt.links.new(um.outputs['UV'], n_.inputs['Vector'])
        t = nt.nodes.new('ShaderNodeTexImage'); t.image = LM_IMG[o.name]
        um = nt.nodes.new('ShaderNodeUVMap'); um.uv_map = uvn; nt.links.new(um.outputs['UV'], t.inputs['Vector'])
        nt.links.new(t.outputs['Color'], b.inputs['Emission Color']); b.inputs['Emission Strength'].default_value = 1.0
    o.data.uv_layers.active = o.data.uv_layers[0]

kw = dict(filepath=OUT + '/living_v1.glb', export_format='GLB', export_apply=True, export_cameras=False, export_lights=False, export_image_format='JPEG', export_jpeg_quality=85)
bpy.ops.export_scene.gltf(**kw)
bpy.ops.wm.save_as_mainfile(filepath=OUT + '/living_v1.blend'); print('DONE', round(os.path.getsize(OUT + '/living_v1.glb') / 1e6, 2), 'MB')
