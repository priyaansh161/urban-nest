# Kitchen "The NCR Kitchen", laid out from mocks/room-refs/kitchen/kitchen-ncr-v1.jpg (see LAYOUT.md).
# Same pipeline as the Heritage Lounge (mocks/room-living/build_living_v1.py): grid shells + scanned textures, every built
# surface gets an image lightmap from one Cycles bake, the products in placements.json stand in for the bake (their
# shadows land in the maps) and are removed before export; the viewer places them live.
#   blender -b -P build_kitchen_v1.py -- <room-kitchen dir> [quick|fast|wb]
# Metres: x -1.45..1.45 (left..right seen from the opening), y -1.7..1.7 (opening wall .. window wall), z 0..2.9.
import bpy, bmesh, math, sys, os, tempfile, json
import numpy as np
from mathutils import Vector

ARGS = sys.argv[sys.argv.index('--') + 1:]
OUT = os.path.abspath(ARGS[0]); QUICK = 'quick' in ARGS; FAST = 'fast' in ARGS
TMP = tempfile.mkdtemp(prefix='kit1_')
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
X0, X1, Y0, Y1, H = -1.45, 1.45, -1.7, 1.7, 2.9
CT = 0.90                       # counter top
STEP = 0.08
WARM = (1.0, 0.80, 0.55); DAY = (1.0, 0.96, 0.90)
rng = np.random.default_rng(7)
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

TEXDIR = os.path.join(OUT, '..', 'room-living', 'textures')
def scan_img(rel, size, colour=True, tint=None, recolour=None, contrast=1.0, rot90=False):
    img = bpy.data.images.load(os.path.join(TEXDIR, rel), check_existing=False)
    if max(img.size) > size: img.scale(size, size)
    if tint or recolour or contrast != 1.0 or rot90:
        w, h = img.size; px = np.array(img.pixels[:], dtype=np.float32).reshape(h, w, 4)
        if rot90: px = np.ascontiguousarray(np.rot90(px))
        p2 = px.reshape(-1, 4)
        if recolour:
            l = p2[:, :3] @ np.array([0.2126, 0.7152, 0.0722], dtype=np.float32); l = 1 + (l / max(1e-4, l.mean()) - 1) * contrast
            p2[:, :3] = l[:, None] * np.array(recolour, dtype=np.float32)
        elif contrast != 1.0: m_ = p2[:, :3].mean(0); p2[:, :3] = m_ + (p2[:, :3] - m_) * contrast
        if tint: p2[:, :3] *= np.array(tint, dtype=np.float32)
        p2[:, :3] = np.clip(p2[:, :3], 0, 1); img.pixels.foreach_set(p2.ravel())
    if not colour: img.colorspace_settings.name = 'Non-Color'
    img.pack(); return img

def pbr(name, color_img, normal_img, rough_img, rough=None, nstr=1.0):
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree; b = nt.nodes['Principled BSDF']
    tc = nt.nodes.new('ShaderNodeTexImage'); tc.image = color_img; nt.links.new(tc.outputs['Color'], b.inputs['Base Color'])
    if rough_img:
        tr = nt.nodes.new('ShaderNodeTexImage'); tr.image = rough_img; nt.links.new(tr.outputs['Color'], b.inputs['Roughness'])
    else: b.inputs['Roughness'].default_value = rough
    if normal_img:
        tn = nt.nodes.new('ShaderNodeTexImage'); tn.image = normal_img
        nm = nt.nodes.new('ShaderNodeNormalMap'); nm.inputs['Strength'].default_value = nstr
        nt.links.new(tn.outputs['Color'], nm.inputs['Color']); nt.links.new(nm.outputs['Normal'], b.inputs['Normal'])
    return m

# ---------------------------------------------------------------- helpers (as in the lounge)
SHELL = []
def grid(name, origin, u, v, m, tile=2.4, holes=()):
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
    lm_ = me.uv_layers.new(name='LM')
    for poly in me.polygons:
        for li, vi in zip(poly.loop_indices, poly.vertices):
            lm_.data[li].uv = ((vi % (nx + 1)) / nx, (vi // (nx + 1)) / ny)
    me.uv_layers.active = lm_
    ob = bpy.data.objects.new('Shell_' + name, me); scene.collection.objects.link(ob); me.materials.append(m)
    SHELL.append((ob, ul, vl)); return ob

def box(name, loc, dim, m, bevel=0.0, rot=(0, 0, 0), segs=3):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc, rotation=rot)
    o = bpy.context.active_object; o.name = name; o.scale = dim
    bpy.ops.object.transform_apply(scale=True); o.data.materials.append(m)
    if bevel:
        bv = o.modifiers.new('Bevel', 'BEVEL'); bv.width = bevel; bv.segments = segs; bpy.ops.object.modifier_apply(modifier=bv.name)
    return o
def bx(name, xa, xb, ya, yb, za, zb, m, bevel=0.0):
    """A box by its extents."""
    return box(name, ((xa + xb) / 2, (ya + yb) / 2, (za + zb) / 2), (xb - xa, yb - ya, zb - za), m, bevel)

def cyl(name, loc, r, h, m, rot=(0, 0, 0), seg=32, r2=None):
    if r2 is None: bpy.ops.mesh.primitive_cylinder_add(vertices=seg, radius=r, depth=h, location=loc, rotation=rot)
    else: bpy.ops.mesh.primitive_cone_add(vertices=seg, radius1=r, radius2=r2, depth=h, location=loc, rotation=rot)
    o = bpy.context.active_object; o.name = name; o.data.materials.append(m); bpy.ops.object.shade_smooth(); return o

def join(objs, name):
    bpy.ops.object.select_all(action='DESELECT')
    for o in objs: o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]; bpy.ops.object.join(); bpy.context.active_object.name = name
    return bpy.context.active_object

def cut(o, cutter):
    md = o.modifiers.new('c', 'BOOLEAN'); md.object = cutter; md.operation = 'DIFFERENCE'; md.solver = 'EXACT'
    bpy.ops.object.select_all(action='DESELECT'); o.select_set(True); bpy.context.view_layer.objects.active = o
    bpy.ops.object.modifier_apply(modifier='c'); bpy.data.objects.remove(cutter)

def world_uv(o, tile, vertical_grain=False):
    """Texture UVs from world position, projected along each face's main axis (real scale). vertical_grain: the image's
    v axis runs up (z) on every side face, so a laminate's grain stands upright like the photo's tall units."""
    me = o.data; uv = me.uv_layers[0] if me.uv_layers else me.uv_layers.new(name='UVMap'); mw = o.matrix_world
    keep = {i for i, sl in enumerate(o.material_slots) if sl.material and sl.material.name.startswith(('Samsung', 'Elica', 'Electrolux'))}
    for poly in me.polygons:
        if poly.material_index in keep: continue                 # appliance faces keep their own photo mapping
        ax = max(range(3), key=lambda i: abs(poly.normal[i]))
        for li, vi in zip(poly.loop_indices, poly.vertices):
            p = mw @ me.vertices[vi].co
            a, b = ((p.y, p.z), (p.x, p.z), (p.x, p.y))[ax]
            uv.data[li].uv = (a / tile, b / tile) if not vertical_grain or ax == 2 else (b / tile, a / tile)

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
    """The viewer's placeItem() in Blender. three.js (x, y, z) is Blender (x, -z, y)."""
    new = import_glb(os.path.join(OUT, 'products', d['file']))
    root = bpy.data.objects.new('Place ' + d['name'], None); scene.collection.objects.link(root)
    inner = bpy.data.objects.new('Place inner', None); scene.collection.objects.link(inner); inner.parent = root
    for o in new:
        if o.parent is None: o.parent = inner
    bpy.context.view_layer.update(); mn, mx = bounds(new); sz = mx - mn
    s = d['length'] / max(sz.x, sz.y) if 'length' in d else d['height'] / sz.z
    inner.scale = (s, s, s); bpy.context.view_layer.update(); mn, mx = bounds(new); c = (mn + mx) / 2
    inner.location -= Vector((c.x, c.y, mx.z if d.get('hang') else mn.z))
    x, y, z = d['pos']; root.location = (x, -z, y); root.rotation_euler.z = d.get('rotY', 0)
    for k, ax, sgn in (('alignBack', 1, None), ('alignLeft', 0, 'min'), ('alignRight', 0, 'max')):
        if k not in d: continue
        bpy.context.view_layer.update(); mn, mx = bounds(new)
        if k == 'alignBack': root.location.y += -d[k] - mx.y
        elif sgn == 'min': root.location.x += d[k] - mn.x
        else: root.location.x += d[k] - mx.x
    bpy.context.view_layer.update(); return new + [root, inner]

LM = []
def lightmap_prep(o, res, new_uv=True):
    me = o.data; me.uv_layers[0].active_render = True
    w, h = res if isinstance(res, tuple) else (res, res)
    if FAST: w, h = min(w, 256), min(h, 256)
    if new_uv:
        lmu = me.uv_layers.new(name='LM'); me.uv_layers.active = lmu
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

def save_img(name, rgb, colour=True):
    h, w = rgb.shape[:2]; rgba = np.ones((h, w, 4), dtype=np.float32); rgba[..., :3] = rgb
    im = bpy.data.images.new(name, w, h, alpha=False); im.pixels.foreach_set(rgba.ravel())
    p = os.path.join(TMP, name + '.png'); im.filepath_raw = p; im.file_format = 'PNG'; im.save()
    out = bpy.data.images.load(p)
    if not colour: out.colorspace_settings.name = 'Non-Color'
    out.pack(); return out

def noise(h, w, seed, r):
    a = np.random.default_rng(seed).normal(0, 1, (h, w)); a = SL.blur(a, r); return a / max(1e-6, np.abs(a).max())

# ---------------------------------------------------------------- the kitchen's materials
def tile_image():
    """One 80 cm beige glossy vitrified tile: warm sand, soft clouding and faint drifting veins (no grout: that is geometry)."""
    S = 1024; c1 = noise(S, S, 3, 40); c2 = noise(S, S, 4, 10); c3 = noise(S, S, 5, 2)
    y, x = np.mgrid[0:S, 0:S] / S
    vein = np.exp(-((np.sin((x * 1.3 + y * 0.6 + 0.25 * c1) * 9) ) ** 2) / 0.004) * 0.5
    base = np.array([0.83, 0.77, 0.67])
    rgb = base[None, None, :] * (1 + 0.035 * c1[..., None] + 0.02 * c2[..., None] + 0.012 * c3[..., None]) - 0.03 * vein[..., None]
    return SL.img('tile_col', np.clip(rgb, 0, 1), TMP)

def outside_image():
    """Day view from a Noida high-rise: hazy pale sky, a row of tall residential towers, tree tops below the sill."""
    Hh, Ww = 768, 840; v, u = np.mgrid[0:Hh, 0:Ww]; v = 1 - v / Hh; u = u / Ww          # v = 0 at the bottom
    sky = np.array([0.86, 0.90, 0.94]) * (1 - 0.25 * v[..., None]) + np.array([0.62, 0.74, 0.88]) * 0.25 * v[..., None]
    rgb = sky.copy()
    r_ = np.random.default_rng(3)
    for k in range(9):                                                                   # towers: pale render, a grid of windows, balconies
        cx = 0.05 + k * 0.115 + r_.uniform(-0.03, 0.03); w_ = r_.uniform(0.06, 0.10); top = r_.uniform(0.55, 0.95)
        m_ = (abs(u - cx) < w_ / 2) & (v < top)
        shade = 0.78 + 0.12 * r_.random()
        col = np.array([0.86, 0.84, 0.80]) * shade
        win = ((np.floor(v * 90) % 3) == 0) & ((np.floor((u - cx) * 400) % 4) < 2)
        bal = (np.floor(v * 90) % 3) == 1
        t_ = np.where(win[..., None], col * 0.55, np.where(bal[..., None], col * 0.92, col))
        far = 0.65 + 0.35 * (k % 3) / 2; t_ = t_ * far + sky * (1 - far)                   # haze on the far ones
        rgb = np.where(m_[..., None], t_, rgb)
    trees = (v < 0.22 + 0.05 * np.sin(u * 40) * np.cos(u * 17))
    leaf = np.array([0.20, 0.36, 0.14]) * (0.7 + 0.5 * (0.5 + 0.5 * noise(Hh, Ww, 9, 2)))[..., None]
    rgb = np.where(trees[..., None], leaf, rgb)
    return SL.img('outside_col', np.clip(rgb, 0, 1), TMP)

LAM = (0.60, 0.41, 0.23)
APP = os.path.join(OUT, 'appliances')
def face_mat(name, file, rough):
    im = bpy.data.images.load(os.path.join(APP, file)); im.pack()
    return pbr(name, im, None, None, rough=rough)
def face_uv(o, axis_u, axis_v, u0, u1, v0, v1):
    """Fit the image over the object: u along axis_u from u0..u1, v along axis_v from v0..v1 (world)."""
    me = o.data; uv = me.uv_layers[0] if me.uv_layers else me.uv_layers.new(name='UV')
    for poly in me.polygons:
        for li, vi in zip(poly.loop_indices, poly.vertices):
            c = me.vertices[vi].co
            uv.data[li].uv = ((c[axis_u] - u0) / (u1 - u0), (c[axis_v] - v0) / (v1 - v0))                       # the photo's warm oak laminate
M = {
    'wall': pbr('Warm White Paint', scan_img('beige_wall_001/beige_wall_001_diff_2k.jpg', 1024, recolour=(0.90, 0.86, 0.78), contrast=0.25),
                scan_img('beige_wall_001/beige_wall_001_nor_gl_2k.jpg', 1024, False), None, rough=0.85, nstr=0.4),
    'ceiling': mat('Ceiling', (0.93, 0.91, 0.87, 1), 0.9),
    'tile': SL.mat('Beige Vitrified Tile', (0.83, 0.77, 0.67), 0.12, image=tile_image()),
    'grout': mat('Grout', (0.66, 0.61, 0.53, 1), 0.7),
    'marble': pbr('White Marble Splash', scan_img('Marble019/Marble019_2K-JPG_Color.jpg', 2048, tint=(1.04, 1.03, 1.02)),
                  scan_img('Marble019/Marble019_2K-JPG_NormalGL.jpg', 1024, False), None, rough=0.12, nstr=0.3),
    'quartz': pbr('White Quartz', scan_img('Marble019/Marble019_2K-JPG_Color.jpg', 1024, tint=(1.03, 1.02, 1.0), contrast=0.55),
                  None, None, rough=0.18),
    'oak': pbr('Oak Laminate', scan_img('walnut_veneer/walnut_veneer_Diffuse_2k.jpg', 2048, recolour=LAM, contrast=1.9),
               scan_img('walnut_veneer/walnut_veneer_nor_gl_2k.jpg', 1024, False), None, rough=0.45, nstr=0.5),
    'navy': mat('Charcoal Navy Matte', (0.020, 0.027, 0.048, 1), 0.55),
    'gap': mat('Shutter Gap', (0.02, 0.02, 0.025, 1), 0.8),
    'profile': mat('Steel J-Profile (painted)', (0.42, 0.43, 0.45, 1), 0.35),
    'blackglass': mat('Black Glass', (0.012, 0.012, 0.014, 1), 0.06),
    'steel': mat('Brushed Steel (painted)', (0.30, 0.31, 0.33, 1), 0.32),       # metal bakes black in a diffuse map: painted grey
    'steeldark': mat('Steel Shadow', (0.14, 0.145, 0.155, 1), 0.35),
    'fridge': face_mat('Samsung Side-by-Side Doors', 'fridge_front.png', 0.3),
    'oven': face_mat('Elica Built-in Oven Front', 'oven_front.png', 0.08),
    'micro': face_mat('Electrolux Built-in Microwave Front', 'microwave_front.png', 0.1),
    'brushed': mat('Fridge Side Steel', (0.40, 0.41, 0.43, 1), 0.35),
    'upvc': mat('White uPVC', (0.94, 0.94, 0.93, 1), 0.35),
    'glass': mat('Window Glass', (0.85, 0.90, 0.92, 1), 0.02, alpha=0.08),
    'matblack': mat('Matte Black', (0.02, 0.02, 0.022, 1), 0.45),
    'chrome': mat('Chrome', (0.85, 0.85, 0.86, 1), 0.08, 1.0),
    'hoodglass': mat('Hood Glass', (0.10, 0.13, 0.14, 1), 0.05, alpha=0.55),
    'led': mat('LED Strip', (1, 0.9, 0.75, 1), 0.5, emit=((1.0, 0.85, 0.62, 1), 6.0)),
    'dl': mat('Downlight Lens', (0.02, 0.02, 0.02, 1), 0.3, emit=((1.0, 0.86, 0.66, 1), 10.0)),
    'dltrim': mat('Downlight Trim', (0.92, 0.92, 0.90, 1), 0.4),
    'switch': mat('Switch Plate', (0.95, 0.95, 0.94, 1), 0.3),
}
OUTSIDE = SL.mat('Outside Day', (0.8, 0.85, 0.9), 1.0, image=outside_image())
_ob = OUTSIDE.node_tree.nodes['Principled BSDF']
for nd in list(OUTSIDE.node_tree.nodes):
    if nd.type == 'TEX_IMAGE': OUTSIDE.node_tree.links.new(nd.outputs['Color'], _ob.inputs['Emission Color'])
_ob.inputs['Emission Strength'].default_value = 1.6; _ob.inputs['Base Color'].default_value = (0, 0, 0, 1)

LMX, LMRES = [], {}
def lm(o, res=1024): LMX.append(o); LMRES[o.name] = res; return o

# ---------------------------------------------------------------- shell: floor (80 cm tiles), ceiling, four walls
NC = lambda l: max(1, round(l / STEP))
DUW = (X1 - X0) / NC(X1 - X0); DUD = (Y1 - Y0) / NC(Y1 - Y0); DZ = H / NC(H)
WIN = (-0.60, 0.60, 1.10, 2.20)                 # window in the back wall: x, x, sill, head
OPEN = (-0.80, 0.80, 2.40)                      # the way in, in the front wall: no door
win_hole = (round((WIN[0] - X0) / DUW), round((WIN[1] - X0) / DUW), round(WIN[2] / DZ), round(WIN[3] / DZ))
WX0, WX1, WZ0, WZ1 = X0 + win_hole[0] * DUW, X0 + win_hole[1] * DUW, win_hole[2] * DZ, win_hole[3] * DZ
op_hole = (round((X1 - OPEN[1]) / DUW), round((X1 - OPEN[0]) / DUW), 0, round(OPEN[2] / DZ))
OX0, OX1, OZ1 = X1 - op_hole[1] * DUW, X1 - op_hole[0] * DUW, op_hole[3] * DZ
floor = grid('Floor', (X0, Y0, 0), (X1 - X0, 0, 0), (0, Y1 - Y0, 0), M['tile'], tile=0.8)
def tile_uv(ob, T=0.8, seed=5):
    """Every tile reads a different turn / flip / offset of the tile image, so no two tiles match."""
    me = ob.data; uv = me.uv_layers['UV']; r = np.random.default_rng(seed); cache = {}
    for poly in me.polygons:
        cx = sum(me.vertices[v].co.x for v in poly.vertices) / 4; cy = sum(me.vertices[v].co.y for v in poly.vertices) / 4
        key = (int(math.floor((cx + 0.4) / T)), int(math.floor((cy - Y0) / T)))      # tiles laid from the opening, centred on x
        if key not in cache: cache[key] = (int(r.integers(0, 4)), bool(r.integers(0, 2)), float(r.random()) * 0.3, float(r.random()) * 0.3)
        k, flip, ox, oy = cache[key]
        for li, vi in zip(poly.loop_indices, poly.vertices):
            co = me.vertices[vi].co; u = (co.x + 0.4 - key[0] * T) / T; v = (co.y - Y0 - key[1] * T) / T
            if flip: u = 1 - u
            for _ in range(k): u, v = 1 - v, u
            uv.data[li].uv = (u * 0.7 + ox, v * 0.7 + oy)
tile_uv(floor)
grid('Ceiling', (X0, Y1, H), (X1 - X0, 0, 0), (0, -(Y1 - Y0), 0), M['ceiling'], tile=3.0)
grid('Back Wall', (X0, Y1, 0), (X1 - X0, 0, 0), (0, 0, H), M['wall'], tile=3.0, holes=[win_hole])
grid('Left Wall', (X0, Y0, 0), (0, Y1 - Y0, 0), (0, 0, H), M['wall'], tile=3.0)
grid('Right Wall', (X1, Y1, 0), (0, -(Y1 - Y0), 0), (0, 0, H), M['wall'], tile=3.0)
grid('Front Wall', (X1, Y0, 0), (-(X1 - X0), 0, 0), (0, 0, H), M['wall'], tile=3.0, holes=[op_hole])
gl = [box('Grout', (-0.4 + 0.8 * k, 0, 0.0008), (0.004, Y1 - Y0, 0.0016), M['grout']) for k in range(-1, 3) if X0 < -0.4 + 0.8 * k < X1]
gl += [box('Grout', (0, Y0 + 0.8 * k, 0.0008), (X1 - X0, 0.004, 0.0016), M['grout']) for k in range(1, 5) if Y0 + 0.8 * k < Y1]
grout = join(gl, 'LM_Grout'); world_uv(grout, 1.0); lm(grout, 512)

# the opening: wall thickness round it (jambs and head, plaster) and a marble threshold strip
T_ = 0.15
op = [bx('Jamb', OX0 - 0.005, OX0, Y0 - T_, Y0, 0, OZ1, M['wall']), bx('Jamb', OX1, OX1 + 0.005, Y0 - T_, Y0, 0, OZ1, M['wall']),
      bx('Head', OX0, OX1, Y0 - T_, Y0, OZ1, OZ1 + 0.005, M['wall'])]
opening = join(op, 'LM_Opening'); world_uv(opening, 3.0); lm(opening, 512)
floor_out = grid('Floor Outside', (X0 - 0.6, Y0 - 1.6, -0.002), (X1 - X0 + 1.2, 0, 0), (0, 1.6 - T_, 0), M['tile'], tile=0.8)   # the hall floor seen through the opening
tile_uv(floor_out, seed=9)

# ---------------------------------------------------------------- the window: white uPVC, two sashes, outside view, marble sill
wp = []
FD = 0.10                                                     # frame sits 10 cm into the reveal
for xa, xb, za, zb in ((WX0, WX1, WZ0, WZ0 + 0.06), (WX0, WX1, WZ1 - 0.06, WZ1), (WX0, WX0 + 0.06, WZ0 + 0.06, WZ1 - 0.06), (WX1 - 0.06, WX1, WZ0 + 0.06, WZ1 - 0.06)):
    wp.append(bx('Frame', xa, xb, Y1 + FD, Y1 + FD + 0.07, za, zb, M['upvc'], 0.004))
wm = (WX0 + WX1) / 2
wp.append(bx('Mullion', wm - 0.035, wm + 0.035, Y1 + FD - 0.01, Y1 + FD + 0.07, WZ0 + 0.06, WZ1 - 0.06, M['upvc'], 0.004))
for xa, xb in ((WX0 + 0.06, wm - 0.035), (wm + 0.035, WX1 - 0.06)):                 # sash frames inside the outer frame
    for a, b, c, d in ((xa, xb, WZ0 + 0.06, WZ0 + 0.11), (xa, xb, WZ1 - 0.11, WZ1 - 0.06), (xa, xa + 0.05, WZ0 + 0.11, WZ1 - 0.11), (xb - 0.05, xb, WZ0 + 0.11, WZ1 - 0.11)):
        wp.append(bx('Sash', a, b, Y1 + FD + 0.005, Y1 + FD + 0.06, c, d, M['upvc'], 0.003))
wp.append(bx('Handle', wm - 0.07, wm - 0.05, Y1 + FD - 0.035, Y1 + FD, WZ0 + 0.45, WZ0 + 0.60, M['upvc'], 0.004))
wp += [bx('Reveal', WX0 - 0.002, WX0, Y1, Y1 + FD, WZ0, WZ1, M['wall']), bx('Reveal', WX1, WX1 + 0.002, Y1, Y1 + FD, WZ0, WZ1, M['wall']),
       bx('Reveal', WX0, WX1, Y1, Y1 + FD, WZ1, WZ1 + 0.002, M['wall'])]
window = join(wp, 'LM_Window'); world_uv(window, 1.0); lm(window, 1024)
glass = bx('Window Glass', WX0 + 0.06, WX1 - 0.06, Y1 + FD + 0.03, Y1 + FD + 0.034, WZ0 + 0.06, WZ1 - 0.06, M['glass'])
glass.visible_shadow = False
sill = bx('Sill', WX0 - 0.03, WX1 + 0.03, Y1 - 0.03, Y1 + FD + 0.005, WZ0 - 0.025, WZ0, M['marble'], 0.004)
pl = bpy.data.meshes.new('Outside'); Vn = [(WX0 - 0.6, Y1 + 1.2, WZ0 - 0.5), (WX1 + 0.6, Y1 + 1.2, WZ0 - 0.5), (WX1 + 0.6, Y1 + 1.2, WZ1 + 0.5), (WX0 - 0.6, Y1 + 1.2, WZ1 + 0.5)]
pl.from_pydata(Vn, [], [(0, 1, 2, 3)]); uvl = pl.uv_layers.new(name='UV')
for li, uv_ in zip(range(4), ((0, 0), (1, 0), (1, 1), (0, 1))): uvl.data[li].uv = uv_
pl.materials.append(OUTSIDE); outside = bpy.data.objects.new('Outside View', pl); scene.collection.objects.link(outside)

# ---------------------------------------------------------------- LEFT wall: tall oak unit with built-in oven + microwave, steel fridge, pull-out
D_TALL, Z_TALL = 0.62, 2.40
FX = X0 + D_TALL                                             # front face of the tall units
def shutter_gaps(parts, x, ys, za, zb):
    for y in ys: parts.append(bx('Gap', x, x + 0.003, y - 0.002, y + 0.002, za, zb, M['gap']))
tall = [bx('Tall Carcass', X0, FX, -1.70, -0.05, 0.08, Z_TALL, M['oak']), bx('Tall Plinth', X0, FX - 0.05, -1.70, -0.05, 0, 0.08, M['navy'])]
# appliances column y -0.70..-0.10: drawer under, oven, microwave, shutter over
AY0, AY1 = -0.68, -0.10
ACX = (AY0 + AY1) / 2
OV = bx('Oven', FX - 0.01, FX + 0.008, ACX - 0.2975, ACX + 0.2975, 0.505, 1.100, M['oven'], 0.002)
face_uv(OV, 1, 2, ACX - 0.2975, ACX + 0.2975, 0.505, 1.100)      # faces +x: looking at it from the aisle, +y is to the right
MW = bx('Microwave', FX - 0.01, FX + 0.008, ACX - 0.2975, ACX + 0.2975, 1.160, 1.549, M['micro'], 0.002)
face_uv(MW, 1, 2, ACX - 0.2975, ACX + 0.2975, 1.160, 1.549)
tall += [OV, MW, bx('Oven Handle', FX + 0.008, FX + 0.030, ACX - 0.255, ACX + 0.255, 0.930, 0.942, M['steel'], 0.005)]
for dy in (-0.13, 0.0, 0.135):                                  # the three steel dials standing out of the glass
    tall.append(cyl('Dial', (FX + 0.018, ACX + dy, 1.048), 0.019, 0.02, M['steel'], rot=(0, math.pi / 2, 0), seg=32))
shutter_gaps(tall, FX, [AY0, AY1, -1.19], 0.08, Z_TALL)
for z in (0.50, 1.10, 1.16, 1.56, 1.62): tall.append(bx('Gap', FX, FX + 0.003, AY0, AY1, z - 0.002, z + 0.002, M['gap']))
tall.append(bx('Gap', FX, FX + 0.003, -1.70, AY0, 1.20, 1.204, M['gap']))
tall_u = join(tall, 'LM_TallUnit'); world_uv(tall_u, 2.0); lm(tall_u, 2048)
# fridge y -0.02..0.78: double-door, steel, recessed handles; oak cabinet over it; a 30 cm oak pull-out pantry to the back run
FY0, FY1 = -0.02, 0.78
FB = bx('Fridge Body', X0 + 0.02, X0 + 0.68, FY0 + 0.005, FY1 - 0.005, 0.04, 1.80, M['brushed'], 0.006)
FD = bx('Fridge Doors', X0 + 0.68, X0 + 0.73, FY0 + 0.005, FY1 - 0.005, 0.04, 1.80, M['fridge'], 0.008)
face_uv(FD, 1, 2, FY0 + 0.005, FY1 - 0.005, 0.04, 1.80)          # faces +x: the photo's left (freezer) is the room's -y side
fr = [FB, FD, bx('Fridge Feet', X0 + 0.05, X0 + 0.66, FY0 + 0.04, FY1 - 0.04, 0, 0.04, M['matblack'])]
GY = (FY0 + 0.005) + (FY1 - FY0 - 0.01) * (325 / 697)            # the photo's door gap: 309..341 of its 697 px
for y_ in (GY - 0.035, GY + 0.035):                              # vertical bar handles either side of the gap
    fr.append(bx('Fridge Handle', X0 + 0.735, X0 + 0.752, y_ - 0.009, y_ + 0.009, 0.62, 1.42, M['steel'], 0.005))
    for z_ in (0.64, 1.40): fr.append(bx('Handle Post', X0 + 0.728, X0 + 0.737, y_ - 0.007, y_ + 0.007, z_ - 0.012, z_ + 0.012, M['steel'], 0.002))
fr += [bx('Over Fridge', X0, FX, FY0, FY1, 1.88, Z_TALL, M['oak']), bx('Pantry', X0, FX, FY1 + 0.005, 1.10, 0.08, Z_TALL, M['oak']),
       bx('Pantry Plinth', X0, FX - 0.05, FY1, 1.10, 0, 0.08, M['navy']), bx('Fridge Side', X0, FX, FY1, FY1 + 0.005, 0.08, Z_TALL, M['oak'])]
shutter_gaps(fr, FX, [(FY0 + FY1) / 2], 1.88, Z_TALL)
fr.append(bx('Gap', FX, FX + 0.003, FY1 + 0.03, 1.08, 1.30, 1.304, M['gap']))
fr.append(bx('Pull', FX + 0.003, FX + 0.012, FY1 + 0.04, FY1 + 0.06, 0.95, 1.65, M['profile']))
fridge = join(fr, 'LM_FridgeWall'); world_uv(fridge, 2.0); lm(fridge, 2048)
# bulkhead: plain wall from the tall units up to the ceiling
bulk = [bx('Bulkhead', X0, FX, -1.70, 1.10, Z_TALL, H, M['wall'])]

# ---------------------------------------------------------------- BACK run (window wall) and RIGHT run: navy bases, white quartz
BY = Y1 - 0.60                     # back run front face (y)
RX = X1 - 0.60                     # right run front face (x)
KNEE = -0.30                       # knee space under the counter from the pantry to here (as in the photo)
SINK = (0.05, 1.40, 0.56, 0.42)   # centre x, y, size x, y
base = []
def base_run_y(xa, xb, doors):     # back run, fronts face -y
    base.append(bx('Carcass', xa, xb, BY + 0.02, Y1, 0.10, 0.86, M['navy']))
    base.append(bx('Plinth', xa, xb, BY + 0.06, Y1, 0, 0.10, M['matblack']))
    base.append(bx('Front', xa, xb, BY, BY + 0.02, 0.10, 0.80, M['navy']))
    base.append(bx('JProfile', xa, xb, BY + 0.005, BY + 0.02, 0.80, 0.86, M['profile']))
    for x in doors: base.append(bx('Gap', x - 0.002, x + 0.002, BY - 0.001, BY + 0.002, 0.10, 0.80, M['gap']))
def base_run_x(ya, yb, doors, drawers=None):
    base.append(bx('Carcass', RX + 0.02, X1, ya, yb, 0.10, 0.86, M['navy']))
    base.append(bx('Plinth', RX + 0.06, X1, ya, yb, 0, 0.10, M['matblack']))
    base.append(bx('Front', RX, RX + 0.02, ya, yb, 0.10, 0.80, M['navy']))
    base.append(bx('JProfile', RX, RX + 0.015, ya, yb, 0.80, 0.86, M['profile']))
    for y in doors: base.append(bx('Gap', RX - 0.001, RX + 0.002, y - 0.002, y + 0.002, 0.10, 0.80, M['gap']))
    if drawers:
        ya_, yb_, zs = drawers
        for z in zs:
            base.append(bx('Gap', RX - 0.001, RX + 0.002, ya_, yb_, z - 0.002, z + 0.002, M['gap']))
            base.append(bx('Drawer Profile', RX - 0.012, RX, ya_ + 0.01, yb_ - 0.01, z - 0.03, z - 0.012, M['profile']))
base_run_y(KNEE, X1 - 0.60, [0.05, 0.40])
base_run_x(-1.40, Y1, [-0.98, -0.52, 0.08, 0.83], drawers=(0.08, 0.83, [0.33]))
DR = dict(y0=0.085, y1=0.825, z0=0.565, z1=0.795, out=0.40)      # the open drawer

base.append(bx('Knee Back', X0 + D_TALL, KNEE, Y1 - 0.02, Y1, 0.0, 0.86, M['wall']))
base.append(bx('Knee Side', KNEE, KNEE + 0.02, BY + 0.02, Y1, 0.0, 0.86, M['navy']))
base.append(bx('End Panel', RX, X1, -1.42, -1.40, 0.0, 0.86, M['navy']))
def ctr(o):                                                         # a part's real centre (the boxes keep it in the mesh, not the object)
    return sum((o.matrix_world @ Vector(c) for c in o.bound_box), Vector()) / 8
for f_ in base:                                                    # the back-run carcass under the sink: hollow where the bowl hangs
    if f_.name.startswith('Carcass') and f_.dimensions.x > 0.9 and ctr(f_).y > 1.0:
        cut(f_, box('cut', (SINK[0], SINK[1], 0.76), (SINK[2] + 0.06, SINK[3] + 0.06, 0.30), M['gap']))
for i_, f_ in enumerate(base):
    if f_.name.startswith(('Front', 'Carcass')) and f_.dimensions.y > 3.0 and ctr(f_).x > RX - 0.05:   # the right run: open the drawer's mouth and the space behind it
        cut(f_, box('cut', (RX + 0.27, (DR['y0'] + DR['y1']) / 2, (DR['z0'] + DR['z1']) / 2), (0.56, DR['y1'] - DR['y0'], DR['z1'] - DR['z0']), M['gap']))
M['cavity'] = mat('Cabinet Cavity', (0.025, 0.025, 0.03, 1), 0.8)
base += [bx('Cavity Top', RX + 0.02, RX + 0.55, DR['y0'], DR['y1'], DR['z1'], DR['z1'] + 0.006, M['cavity']),
         bx('Cavity Back', RX + 0.54, RX + 0.55, DR['y0'], DR['y1'], DR['z0'], DR['z1'], M['cavity']),
         bx('Cavity Side', RX + 0.02, RX + 0.55, DR['y0'] - 0.006, DR['y0'], DR['z0'], DR['z1'], M['cavity']),
         bx('Cavity Side', RX + 0.02, RX + 0.55, DR['y1'], DR['y1'] + 0.006, DR['z0'], DR['z1'], M['cavity']),
         bx('Cavity Floor', RX + 0.02, RX + 0.55, DR['y0'], DR['y1'], DR['z0'] - 0.006, DR['z0'], M['cavity'])]
xf_ = RX - DR['out']                                               # the drawer itself: navy front, steel profile, white box inside
M['drawerin'] = mat('Drawer Inside', (0.86, 0.85, 0.83, 1), 0.5)
base += [bx('Drawer Front', xf_ - 0.02, xf_, DR['y0'], DR['y1'], DR['z0'] - 0.003, DR['z1'] + 0.003, M['navy']),
         bx('Drawer Profile', xf_ - 0.032, xf_ - 0.02, DR['y0'] + 0.01, DR['y1'] - 0.01, DR['z1'] - 0.03, DR['z1'] - 0.012, M['profile']),
         bx('Drawer Bottom', xf_, RX + 0.50, DR['y0'] + 0.01, DR['y1'] - 0.01, DR['z0'] + 0.005, DR['z0'] + 0.017, M['drawerin']),
         bx('Drawer Side', xf_, RX + 0.50, DR['y0'] + 0.01, DR['y0'] + 0.022, DR['z0'] + 0.005, DR['z1'] - 0.06, M['drawerin']),
         bx('Drawer Side', xf_, RX + 0.50, DR['y1'] - 0.022, DR['y1'] - 0.01, DR['z0'] + 0.005, DR['z1'] - 0.06, M['drawerin']),
         bx('Drawer Back', RX + 0.488, RX + 0.50, DR['y0'] + 0.01, DR['y1'] - 0.01, DR['z0'] + 0.005, DR['z1'] - 0.06, M['drawerin']),
         bx('Drawer Divider', xf_, RX + 0.50, 0.44, 0.452, DR['z0'] + 0.017, DR['z0'] + 0.08, M['drawerin'])]
bases = join(base, 'LM_Bases'); world_uv(bases, 1.0); lm(bases, 2048)
# quartz counter in one piece, sink cut in it; marble splash up to the wall cabinets
top_parts = [bx('Counter Back', X0 + D_TALL, X1, BY - 0.02, Y1, 0.86, CT, M['quartz'], 0.003),
             bx('Counter Right', RX - 0.02, X1, -1.42, BY - 0.02, 0.86, CT, M['quartz'], 0.003)]
counter = join(top_parts, 'LM_Counter')
cutter = box('cut', (SINK[0], SINK[1], 0.88), (SINK[2], SINK[3], 0.2), M['quartz'], 0.03); cut(counter, cutter)
world_uv(counter, 1.2); lm(counter, 2048)
sk = []
SX0, SX1, SY0, SY1, SZ = SINK[0] - SINK[2] / 2, SINK[0] + SINK[2] / 2, SINK[1] - SINK[3] / 2, SINK[1] + SINK[3] / 2, 0.68
M['sinksteel'] = mat('Sink Satin Steel', (0.30, 0.31, 0.33, 1), 0.38)
SZ = 0.66                                                        # bowl floor: 20 cm below the counter top
M['sinkfloor'] = mat('Sink Floor Steel', (0.20, 0.205, 0.22, 1), 0.4)
T_ = 0.008
sk += [bx('Sink Floor', SX0, SX1, SY0, SY1, SZ - T_, SZ, M['sinkfloor'], 0.002),
       bx('Sink Wall L', SX0 - T_, SX0, SY0 - T_, SY1 + T_, SZ - T_, 0.875, M['sinksteel']), bx('Sink Wall R', SX1, SX1 + T_, SY0 - T_, SY1 + T_, SZ - T_, 0.875, M['sinksteel']),
       bx('Sink Wall F', SX0, SX1, SY0 - T_, SY0, SZ - T_, 0.875, M['sinksteel']), bx('Sink Wall B', SX0, SX1, SY1, SY1 + T_, SZ - T_, 0.875, M['sinksteel'])]
for (xa, ya) in ((SX0, SY0), (SX1, SY0), (SX0, SY1), (SX1, SY1)):          # soft inside corners
    sk.append(cyl('Sink Corner', (xa, ya, (SZ + 0.875) / 2), 0.012, 0.875 - SZ, M['sinksteel'], seg=16))
sk.append(cyl('Drain', (SINK[0] + 0.14, SINK[1] - 0.04, SZ + 0.001), 0.045, 0.004, M['steeldark'], seg=48))
sk.append(cyl('Drain Cap', (SINK[0] + 0.14, SINK[1] - 0.04, SZ + 0.004), 0.030, 0.004, M['sinksteel'], seg=48))
TX, TY = SINK[0] - 0.12, SY1 + 0.055                             # the tap: a round body, an arched spout over the bowl, a side lever
tb = SL.lathe('Tap Body', [(0.0, CT), (0.028, CT), (0.028, CT + 0.008), (0.020, CT + 0.014), (0.017, CT + 0.20), (0.0, CT + 0.20)], M['matblack'], seg=40)
tb.location = (TX, TY, 0); sk.append(tb)
arc = [(TX, TY - 0.065 + 0.065 * math.cos(a), CT + 0.19 + 0.17 * math.sin(a)) for a in np.linspace(0.0, math.pi, 28)]
arc += [(TX, arc[-1][1], arc[-1][2] - 0.04)]
sk.append(SL.tube('Tap Spout', arc, [0.0135] * len(arc), M['matblack'], seg=24))
ae = SL.lathe('Tap Aerator', [(0.0, 0.0), (0.0145, 0.0), (0.0145, 0.022), (0.0, 0.022)], M['matblack'], seg=32); ae.location = (TX, arc[-1][1], arc[-1][2] - 0.022); sk.append(ae)
sk.append(SL.tube('Tap Lever', [(TX + 0.015, TY, CT + 0.15), (TX + 0.05, TY, CT + 0.165), (TX + 0.085, TY, CT + 0.172)], [0.008, 0.007, 0.006], M['matblack'], seg=16))
sink = join(sk, 'LM_Sink'); world_uv(sink, 0.5); lm(sink, 512)
SPL = 1.52                          # splash top: the underside of the wall cabinets
spl = [bx('Splash Back L', X0 + D_TALL, WX0 - 0.03, Y1 - 0.012, Y1, CT, SPL, M['marble']),
       bx('Splash Back M', WX0 - 0.03, WX1 + 0.03, Y1 - 0.012, Y1, CT, WZ0 - 0.025, M['marble']),
       bx('Splash Back R', WX1 + 0.03, X1 - 0.012, Y1 - 0.012, Y1, CT, SPL, M['marble']),
       bx('Splash Right', X1 - 0.012, X1, -1.42, Y1 - 0.012, CT, SPL, M['marble'])]
splash = join(spl, 'LM_Splash'); world_uv(splash, 1.6); lm(splash, 2048)
# a switch board on the splash next to the hob, like the photo
sw = [bx('Switch', X1 - 0.02, X1 - 0.012, -0.32, -0.18, 1.18, 1.27, M['switch'], 0.003), bx('Switch', X1 - 0.02, X1 - 0.012, BY + 0.25, BY + 0.37, 1.30, 1.39, M['switch'], 0.003)]

# ---------------------------------------------------------------- wall cabinets (oak, 35 deep) with LED strips under them; chimney niche
UZ0, UZ1 = SPL, 2.38
up = []
def upper_x(ya, yb, splits):         # on the right wall, fronts face -x
    up.append(bx('Upper', X1 - 0.35, X1, ya, yb, UZ0, UZ1, M['oak'], 0.002))
    for y in splits: up.append(bx('Gap', X1 - 0.353, X1 - 0.349, y - 0.002, y + 0.002, UZ0, UZ1, M['gap']))
    up.append(bx('Profile', X1 - 0.35, X1 - 0.30, ya + 0.005, yb - 0.005, UZ0 - 0.012, UZ0, M['profile']))
upper_x(-1.40, -0.92, []); upper_x(-0.40, 0.08, []); upper_x(0.83, Y1, [1.25])
ON = (-0.92, -0.40)                                               # the open niche between them
M['shelfwhite'] = mat('Shelf White Laminate', (0.90, 0.89, 0.86, 1), 0.5)
up += [bx('Niche Back', X1 - 0.02, X1, ON[0], ON[1], UZ0, UZ1, M['shelfwhite']), bx('Niche Side', X1 - 0.35, X1, ON[0], ON[0] + 0.018, UZ0, UZ1, M['oak']),
       bx('Niche Side', X1 - 0.35, X1, ON[1] - 0.018, ON[1], UZ0, UZ1, M['oak']), bx('Niche Base', X1 - 0.35, X1, ON[0], ON[1], UZ0, UZ0 + 0.018, M['oak']),
       bx('Niche Top', X1 - 0.35, X1, ON[0], ON[1], UZ1 - 0.018, UZ1, M['oak']), bx('Niche Shelf', X1 - 0.33, X1 - 0.02, ON[0] + 0.018, ON[1] - 0.018, UZ0 + 0.40, UZ0 + 0.418, M['oak'])]
up.append(bx('Niche Top', X1 - 0.35, X1, 0.08, 0.83, 2.05, UZ1, M['oak'], 0.002))             # a short cabinet over the chimney
up.append(bx('Niche Back', X1 - 0.02, X1, 0.08, 0.83, UZ0, 2.05, M['marble']))
up.append(bx('Upper Back', WX1 + 0.18, X1 - 0.35, Y1 - 0.35, Y1, UZ0, UZ1, M['oak'], 0.002))  # back wall, right of the window
up.append(bx('Gap', WX1 + 0.18 + 0.002, X1 - 0.35, Y1 - 0.353, Y1 - 0.349, UZ0 + 0.37, UZ0 + 0.374, M['gap']))
up += [bx('Bulk', X1 - 0.35, X1, -1.40, Y1, UZ1, H, M['wall']), bx('Bulk', WX1 + 0.18, X1 - 0.35, Y1 - 0.35, Y1, UZ1, H, M['wall'])]
uppers = join(up, 'LM_Uppers'); world_uv(uppers, 2.0); lm(uppers, 2048)
bulkhead = join(bulk + sw, 'LM_Bulk'); world_uv(bulkhead, 3.0); lm(bulkhead, 512)
LEDS = [bx('LED R1', X1 - 0.33, X1 - 0.31, -1.38, 0.06, UZ0 - 0.006, UZ0 - 0.002, M['led']), bx('LED R2', X1 - 0.33, X1 - 0.31, 0.85, Y1 - 0.36, UZ0 - 0.006, UZ0 - 0.002, M['led']),
        bx('LED B', WX1 + 0.20, X1 - 0.36, Y1 - 0.33, Y1 - 0.31, UZ0 - 0.006, UZ0 - 0.002, M['led'])]
# chimney: black body in the niche, angled glass visor (like the photo's)
M['hoodblack'] = mat('Hood Black', (0.015, 0.015, 0.017, 1), 0.85)
# (the chimney is the Elica hood in placements.json staging)

# ---------------------------------------------------------------- recessed downlights
FC = dict(x0=-0.50, x1=0.62, y0=-1.15, y1=0.82, drop=0.15)       # the raised centre (over the aisle)
M['gypsum'] = mat('Gypsum White', (0.94, 0.93, 0.90, 1), 0.85)
fz = H - FC['drop']
fc = [bx('FC Band', X0, FC['x0'], Y0, Y1, fz, H, M['gypsum']), bx('FC Band', FC['x1'], X1, Y0, Y1, fz, H, M['gypsum']),
      bx('FC Band', FC['x0'], FC['x1'], Y0, FC['y0'], fz, H, M['gypsum']), bx('FC Band', FC['x0'], FC['x1'], FC['y1'], Y1, fz, H, M['gypsum'])]
fc += [bx('FC Lip', FC['x0'], FC['x0'] + 0.06, FC['y0'], FC['y1'], fz - 0.04, fz, M['gypsum']), bx('FC Lip', FC['x1'] - 0.06, FC['x1'], FC['y0'], FC['y1'], fz - 0.04, fz, M['gypsum']),
       bx('FC Lip', FC['x0'] + 0.06, FC['x1'] - 0.06, FC['y0'], FC['y0'] + 0.06, fz - 0.04, fz, M['gypsum']), bx('FC Lip', FC['x0'] + 0.06, FC['x1'] - 0.06, FC['y1'] - 0.06, FC['y1'], fz - 0.04, fz, M['gypsum'])]
falsec = join(fc, 'LM_FalseCeiling'); world_uv(falsec, 3.0); lm(falsec, 2048)
M['cove'] = mat('Cove Glow', (1, .88, .7, 1), 0.5, 0.0, emit=((1, .80, .55, 1), 3.0))
CG = [bx('Cove Glow', FC['x0'] + 0.08, FC['x0'] + 0.10, FC['y0'] + 0.1, FC['y1'] - 0.1, H - 0.012, H - 0.004, M['cove']),
      bx('Cove Glow', FC['x1'] - 0.10, FC['x1'] - 0.08, FC['y0'] + 0.1, FC['y1'] - 0.1, H - 0.012, H - 0.004, M['cove']),
      bx('Cove Glow', FC['x0'] + 0.1, FC['x1'] - 0.1, FC['y0'] + 0.08, FC['y0'] + 0.10, H - 0.012, H - 0.004, M['cove']),
      bx('Cove Glow', FC['x0'] + 0.1, FC['x1'] - 0.1, FC['y1'] - 0.10, FC['y1'] - 0.08, H - 0.012, H - 0.004, M['cove'])]
DLZ = fz                                                            # downlights sit in the band's underside
DL = [(0.80, -0.95), (0.80, -0.20), (0.80, 0.55), (-0.25, 1.02), (0.40, 1.02), (-0.68, -1.30), (-0.68, 0.40)]
for i_, (x_, y_) in enumerate(DL):
    cyl('DLTrim%d' % i_, (x_, y_, DLZ - 0.004), 0.05, 0.008, M['dltrim']); cyl('DLLens%d' % i_, (x_, y_, DLZ - 0.009), 0.035, 0.006, M['dl'])

# ---------------------------------------------------------------- staging: not for sale, lit live in the viewer (shadows bake under them)
STAGE = []
def lathe(name, prof, m, loc, seg=40):
    o = SL.lathe(name, prof, m, seg=seg); o.location = loc; STAGE.append(o); return o
M['white'] = mat('Glossy White Plastic', (0.93, 0.93, 0.92, 1), 0.2); M['lilac'] = mat('Lilac Plastic', (0.45, 0.42, 0.75, 1), 0.3)
M['ss'] = mat('Stainless', (0.78, 0.78, 0.79, 1), 0.18, 1.0); M['terracotta'] = mat('Terracotta', (0.58, 0.30, 0.18, 1), 0.8)
M['leaf'] = mat('Leaf', (0.13, 0.32, 0.09, 1), 0.5); M['soap'] = mat('Dish Soap', (0.55, 0.80, 0.15, 1), 0.15)
_ty = np.mgrid[0:256, 0:256][0] / 256; _st = (np.abs(((_ty * 6) % 1) - 0.5) < 0.06) | (np.abs(((_ty * 6) % 1) - 0.5) > 0.47)
M['towel'] = SL.mat('Hand Towel', (0.88, 0.85, 0.78), 0.9, sheen=0.5, image=SL.img('towel_col', np.clip(np.where(_st[..., None], np.array([0.62, 0.20, 0.14]), np.array([0.90, 0.87, 0.80])) * (0.93 + 0.07 * noise(256, 256, 31, 1)[..., None]), 0, 1), TMP),
                     normal=SL.normal_img('towel_nor', 0.5 + 0.5 * np.sin(np.mgrid[0:256, 0:256][1] * 1.6) * np.sin(np.mgrid[0:256, 0:256][0] * 1.6), TMP, 2.0), nstrength=0.6)
M['spice1'] = mat('Turmeric', (0.85, 0.55, 0.05, 1), 0.8); M['spice2'] = mat('Chilli', (0.60, 0.12, 0.05, 1), 0.8); M['spice3'] = mat('Coriander', (0.55, 0.45, 0.25, 1), 0.8)
M['jarglass'] = mat('Jar Glass', (0.9, 0.92, 0.9, 1), 0.05, alpha=0.25); M['cork'] = mat('Wood Lid', (0.45, 0.30, 0.16, 1), 0.6)
M['ro'] = mat('RO Black', (0.03, 0.03, 0.035, 1), 0.15)
# mixer grinder (the photo's lilac-and-white one): base, steel jar, lid
mx_, my_ = 1.28, -0.38
# (the mixer is the Bajaj in placements.json staging)
# RO purifier on the wall right of the window
STAGE.append(box('RO', (WX1 + 0.32, Y1 - 0.08, 1.80), (0.28, 0.14, 0.40), M['ro'], 0.02))
STAGE.append(box('RO Tap', (WX1 + 0.32, Y1 - 0.16, 1.66), (0.03, 0.04, 0.06), M['white'], 0.008))
# pressure cooker on the hob, dish soap, spice jars, plants on the sill, a hand towel on a drawer
lathe('Cooker', [(0, 0), (0.11, 0), (0.115, 0.01), (0.115, 0.15), (0.12, 0.16), (0.10, 0.17), (0, 0.175)], M['ss'], (1.20, 0.62, CT + 0.11))
STAGE.append(box('Cooker Handle', (1.20 - 0.17, 0.62, CT + 0.27), (0.14, 0.03, 0.025), M['matblack'], 0.008))
lathe('Whistle', [(0, 0), (0.012, 0), (0.01, 0.04), (0.015, 0.05), (0, 0.06)], M['matblack'], (1.20, 0.62, CT + 0.285))
lathe('Soap', [(0, 0), (0.03, 0), (0.032, 0.12), (0.02, 0.15), (0.008, 0.16), (0.008, 0.19), (0, 0.19)], M['soap'], (0.50, 1.47, CT + 0.012))
for k, sp in enumerate(()):                                  # (the spice jars made way for the painted pickle set, 14 Nov)
    x_ = 0.62 + k * 0.10
    lathe('Spice Jar', [(0, 0), (0.035, 0), (0.037, 0.10), (0.03, 0.11), (0, 0.11)], M['jarglass'], (x_, 1.62, CT))
    lathe('Spice', [(0, 0.004), (0.033, 0.004), (0.033, 0.07), (0, 0.07)], M[sp], (x_, 1.62, CT))
    lathe('Spice Lid', [(0, 0), (0.033, 0), (0.034, 0.025), (0, 0.025)], M['cork'], (x_, 1.62, CT + 0.11))
def pot_plant(x, y, z, h=0.22, seed=0):
    lathe('Pot', [(0, 0), (0.045, 0), (0.06, 0.10), (0.064, 0.105), (0, 0.105)], M['terracotta'], (x, y, z))
    V, F, UV = [], [], []; r = np.random.default_rng(seed)
    for k in range(22):
        a = r.uniform(0, 2 * math.pi); up = Vector((0.35 * math.cos(a), 0.35 * math.sin(a), 1)).normalized(); side = Vector((-math.sin(a), math.cos(a), 0))
        up = Vector((r.uniform(0.2, 0.7) * math.cos(a), r.uniform(0.2, 0.7) * math.sin(a), 1)).normalized()
        SL.leaf_strip(V, F, UV, Vector((x, y, z + 0.10)), up, side, r.uniform(0.45, 1.0) * h, r.uniform(0.03, 0.05), droop=r.uniform(0.3, 0.9))
    STAGE.append(SL.mesh_obj('Plant', V, F, M['leaf'], UV))
M['soil'] = mat('Potting Soil', (0.10, 0.07, 0.05, 1), 0.95)
_lv = np.mgrid[0:128, 0:64][0] / 128.0
M['tulsi'] = SL.mat('Tulsi Leaf', (0.16, 0.36, 0.10), 0.45, image=SL.img('tulsi_col', np.clip(np.array([0.13, 0.33, 0.08]) * (0.8 + 0.35 * _lv)[..., None] * (1 - 0.25 * (np.abs(np.mgrid[0:128, 0:64][1] / 64.0 - 0.5) < 0.03))[..., None], 0, 1), TMP))
_band = 0.5 + 0.5 * np.sin(np.mgrid[0:256, 0:64][0] / 256.0 * 60 + 2 * np.sin(np.mgrid[0:256, 0:64][1] / 64.0 * 6))
_edge = (np.abs(np.mgrid[0:256, 0:64][1] / 64.0 - 0.5) > 0.44)
M['snake'] = SL.mat('Snake Plant Leaf', (0.12, 0.30, 0.10), 0.4, image=SL.img('snake_col', np.clip(np.where(_edge[..., None], np.array([0.62, 0.62, 0.22]), np.array([0.07, 0.22, 0.08]) + np.array([0.10, 0.16, 0.08]) * _band[..., None]), 0, 1), TMP))
def pot(x, y, z, r=0.055, h=0.10):
    lathe('Pot', [(0, 0), (r * 0.72, 0), (r * 0.95, h * 0.85), (r * 1.08, h * 0.86), (r * 1.10, h), (r * 0.92, h), (r * 0.92, h * 0.9), (0, h * 0.9)], M['terracotta'], (x, y, z), seg=48)
    lathe('Soil', [(0, h * 0.86), (r * 0.9, h * 0.86), (0, h * 0.88)], M['soil'], (x, y, z), seg=32)
def leaf_quad(V, F, UV, base, d, side, L, W, curl=0.0, n=8):
    """An oval leaf from base along d, width across side, cupped by curl."""
    k0 = len(V)
    for i in range(n + 1):
        t = i / n; w = W * math.sin(math.pi * min(t * 1.05, 1.0)) ** 0.8
        c = base + d * (L * t) - Vector((0, 0, 1)) * (0.25 * L * t * t)
        for sgn in (-1, 0, 1):
            V.append(tuple(c + side * (sgn * w / 2) + Vector((0, 0, 1)) * (curl * w * (1 - abs(sgn))))); UV.append(((sgn + 1) / 2, t))
    for i in range(n):
        for j in range(2):
            a = k0 + i * 3 + j; F.append((a, a + 1, a + 4, a + 3))
def tulsi(x, y, z, seed=3):
    pot(x, y, z); r = np.random.default_rng(seed); V, F, UV = [], [], []; stems = []
    for k in range(7):
        a = r.uniform(0, 2 * math.pi); lean = r.uniform(0.15, 0.45); h = r.uniform(0.12, 0.20)
        top = Vector((x + lean * h * math.cos(a), y + lean * h * math.sin(a), z + 0.09 + h)); bot = Vector((x, y, z + 0.09))
        stems.append(SL.tube('Tulsi Stem', [bot, (bot + top) / 2 + Vector((0, 0, 0.01)), top], [0.0025, 0.002, 0.0015], M['tulsi'], seg=6))
        for j in range(9):
            t = 0.25 + 0.75 * j / 8; c = bot.lerp(top, t)
            for sgn in (-1, 1):
                b_ = a + sgn * math.pi / 2 + j * 0.9; d = Vector((math.cos(b_), math.sin(b_), 0.45)).normalized()
                leaf_quad(V, F, UV, c, d, Vector((-d.y, d.x, 0)).normalized(), 0.028 * (1.2 - 0.5 * t), 0.018 * (1.2 - 0.5 * t), curl=0.25)
    STAGE.append(SL.mesh_obj('Tulsi', V, F, M['tulsi'], UV)); STAGE.extend(stems)
def snake_plant(x, y, z, seed=5):
    pot(x, y, z, r=0.06, h=0.11); r = np.random.default_rng(seed); V, F, UV = [], [], []
    for k in range(9):
        a = r.uniform(0, 2 * math.pi); off = r.uniform(0.0, 0.03); base = Vector((x + off * math.cos(a), y + off * math.sin(a), z + 0.10))
        L = r.uniform(0.20, 0.34); lean = r.uniform(0.05, 0.25); d = Vector((lean * math.cos(a), lean * math.sin(a), 1)).normalized()
        side = Vector((-math.sin(a + 0.6), math.cos(a + 0.6), 0)); n = 10; k0 = len(V)
        for i in range(n + 1):
            t = i / n; w = 0.034 * (1 - t ** 3) + 0.002; c = base + d * (L * t)
            for sgn in (-1, 0, 1): V.append(tuple(c + side * (sgn * w / 2) + Vector((0, 0, 0)) - (Vector((-side.y, side.x, 0)) * 0.006 * (1 - abs(sgn))))); UV.append(((sgn + 1) / 2, t))
        for i in range(n):
            for j in range(2):
                q = k0 + i * 3 + j; F.append((q, q + 1, q + 4, q + 3))
    STAGE.append(SL.mesh_obj('Snake Plant', V, F, M['snake'], UV))
tulsi(WX0 + 0.16, Y1 + 0.05, WZ0); snake_plant(WX1 - 0.17, Y1 + 0.05, WZ0)
tw = []
for k in range(14):                                          # towel folded over the top drawer's profile, hanging down
    t = k / 13; tw.append((RX - 0.012 - 0.02 * math.sin(t * math.pi) * 0.3, -0.20, 0.79 - t * 0.38))
STAGE.append(SL.tube('Towel', tw, [0.0] * len(tw), M['towel'], seg=4)) if False else None
def towel(xf, yc, ztop, w=0.26, front=0.36, back=0.12):
    """A cotton towel hung over a bar at (xf, ztop): a short back flap, a longer front flap, soft folds, a slight sway."""
    NU, NV = 28, 46; L = back + 0.04 + front; V, F, UV = [], [], []
    for j in range(NV + 1):
        sv = j / NV * L
        for i in range(NU + 1):
            u = i / NU - 0.5; y = yc + u * w
            fold = 0.004 * math.sin(u * 22 + sv * 9) + 0.003 * math.sin(u * 47 - sv * 5)
            if sv < back: x, z = xf + 0.012 + fold * 0.5, ztop - (back - sv)
            elif sv < back + 0.04:
                a = (sv - back) / 0.04 * math.pi; x, z = xf + 0.006 * math.cos(a) + 0.006, ztop + 0.006 * math.sin(a)
            else:
                d = sv - back - 0.04; x, z = xf - 0.004 - fold - 0.012 * (d / front) ** 2, ztop - d
                y += 0.01 * (d / front) ** 2 * math.sin(u * 3)
            V.append((x, y, z)); UV.append((i / NU, sv / L * 1.4))
    for j in range(NV):
        for i in range(NU): F.append((j * (NU + 1) + i, j * (NU + 1) + i + 1, (j + 1) * (NU + 1) + i + 1, (j + 1) * (NU + 1) + i))
    o = SL.mesh_obj('Towel', V, F, M['towel'], UV)
    md = o.modifiers.new('s', 'SOLIDIFY'); md.thickness = 0.003
    bpy.ops.object.select_all(action='DESELECT'); o.select_set(True); bpy.context.view_layer.objects.active = o; bpy.ops.object.modifier_apply(modifier='s')
    STAGE.append(o)
towel(RX - 0.004, -1.05, 0.845, back=0.03, front=0.34)
# the hob stands in until the Glen stove has its model (then it moves to placements.json as a product)
GLEN = os.path.join(OUT, 'products', 'final', 'd0ccbf0a.glb')
if not os.path.exists(GLEN):
    STAGE.append(box('Hob Glass', (1.21, 0.455, CT + 0.06), (0.405, 0.70, 0.008), M['blackglass'], 0.004))
    STAGE.append(box('Hob Body', (1.21, 0.455, CT + 0.028), (0.40, 0.69, 0.056), M['ss'], 0.006))
    for y_ in (0.22, 0.455, 0.69):
        lathe('Burner', [(0, 0), (0.05, 0), (0.05, 0.015), (0.035, 0.02), (0, 0.022)], mat('Brass Burner', (0.7, 0.5, 0.2, 1), 0.3, 1.0), (1.23, y_, CT + 0.064))
M['brasshook'] = mat('Brass Hook (lightmapped look)', (0.72, 0.52, 0.22, 1), 0.35, 0.0)
hk = [bx('Hook Plate', FX, FX + 0.006, -1.27, -1.23, 1.52, 1.58, M['brasshook'], 0.002),
      SL.tube('Hook', [(FX + 0.006, -1.25, 1.555), (FX + 0.045, -1.25, 1.555), (FX + 0.055, -1.25, 1.575), (FX + 0.05, -1.25, 1.59)], [0.005] * 4, M['brasshook'], seg=12)]
# (the apron left the room, 15 Nov: its hook goes too)
for o in hk: bpy.data.objects.remove(o)
M['neem'] = SL.mat('Neem Wood', (0.42, 0.26, 0.13), 0.5)
def spatula(x, y, z, rz, tilt=0.06):
    """A flat neem-wood spatula (like the Vanam set's turner): 30 cm, a squared blade, a round handle."""
    from mathutils import Matrix
    P_ = [box('Spatula Blade', (0.0, 0.0, 0.0), (0.085, 0.06, 0.005), M['neem'], 0.002),
          SL.tube('Spatula Neck', [(0.04, 0, 0), (0.09, 0, 0.004)], [0.009, 0.007], M['neem'], seg=12),
          SL.tube('Spatula Handle', [(0.09, 0, 0.004), (0.21, 0, 0.012), (0.255, 0, 0.014)], [0.0075, 0.009, 0.0085], M['neem'], seg=14)]
    o = SL.join(P_, 'Neem Spatula')
    o.matrix_world = Matrix.Translation((x, y, z)) @ Matrix.Rotation(rz, 4, 'Z') @ Matrix.Rotation(-tilt, 4, 'Y')
    STAGE.append(o)
spatula(1.075, -0.07, CT + 0.016, math.pi, tilt=0.17)
for o in STAGE: o.select_set(False)

# ---------------------------------------------------------------- products: shadow casters for the bake
PL = json.load(open(os.path.join(OUT, 'placements.json'), encoding='utf8'))
CASTERS = []
PLACED = {}
for d in PL['products'] + [x for x in PL.get('staging', []) if not x.get('lm')]:
    if 'file' in d and os.path.exists(os.path.join(OUT, 'products', d['file'])):
        made = place(d); CASTERS += made; PLACED[d['name']] = made
if 'probe' in ARGS:
    from mathutils import Vector as _V
    dg = bpy.context.evaluated_depsgraph_get()
    for px, py in ((0.05, 1.40), (-0.10, 1.30), (0.20, 1.50), (1.10, 0.45)):
        hit = scene.ray_cast(dg, _V((px, py, 1.6)) if px < 1 else _V((0.70, py, 0.70)), _V((0, 0, -1)) if px < 1 else _V((1, 0, 0)))
        print('PROBE', px, py, 'hit', hit[0], round(hit[1].z, 3) if hit[0] else None, hit[4].name if hit[0] else None)
    sys.exit(0)
if 'bounds' in ARGS:                 # where every piece really is (Blender x, y, z), to check against walls, shelves, the drawer
    for n, objs in PLACED.items():
        mn, mx = bounds(objs); print('BOUNDS %-40s x %6.3f %6.3f  y %6.3f %6.3f  z %6.3f %6.3f' % (n[:40], mn.x, mx.x, mn.y, mx.y, mn.z, mx.z))
    sys.exit(0)

if 'wb' in ARGS:
    scene.render.engine = 'BLENDER_WORKBENCH'; sh = scene.display.shading; sh.light = 'STUDIO'; sh.color_type = 'TEXTURE'
    scene.world = bpy.data.worlds.new('w'); scene.world.color = (0.35, 0.35, 0.35)
    cdw = bpy.data.cameras.new('c'); cw = bpy.data.objects.new('c', cdw); scene.collection.objects.link(cw); scene.camera = cw
    for o in bpy.data.objects:
        if o.name.startswith('Shell_Ceiling'): o.hide_render = True
    shots = {'front': ((0.0, Y0 - 0.5, 1.5), (0.0, Y1, 1.05), 16), 'right': ((-0.5, -0.6, 1.5), (1.4, 0.2, 0.95), 20),
             'back': ((0.1, 0.2, 1.45), (0.0, Y1, 1.0), 20), 'left': ((0.6, 0.6, 1.4), (-1.45, -0.6, 1.1), 20)}
    for k, (l, t, ln) in shots.items():
        cdw.lens = ln; cw.location = l; cw.rotation_euler = (Vector(t) - Vector(l)).to_track_quat('-Z', 'Y').to_euler()
        scene.render.resolution_x, scene.render.resolution_y = 1200, 700; scene.render.filepath = OUT + '/wb_%s.png' % k; bpy.ops.render.render(write_still=True)
    print('DONE wb'); sys.exit(0)

for o in LMX: lightmap_prep(o, LMRES.get(o.name, 1024))
for ob, ul, vl in SHELL:
    d = 0.009 if 'Ceiling' in ob.name or 'Outside' in ob.name else 0.0045
    lightmap_prep(ob, (max(16, min(1024, round(ul / d))), max(16, min(1024, round(vl / d)))), new_uv=False)
for o, res in ((sill, 512),): lightmap_prep(o, res); LMX.append(o)

# ---------------------------------------------------------------- lights: a bright late-morning day through the window, the downlights on, LED strips
def area(name, loc, sx, sy, energy, color, target=None, rot=(0, 0, 0)):
    ld = bpy.data.lights.new(name, 'AREA'); ld.energy = energy; ld.color = color; ld.shape = 'RECTANGLE'; ld.size = sx; ld.size_y = sy
    lo = bpy.data.objects.new(name, ld); lo.location = loc; lo.rotation_euler = rot; scene.collection.objects.link(lo)
    if target: lo.rotation_euler = (Vector(target) - lo.location).to_track_quat('-Z', 'Y').to_euler()
    return lo
def spot(name, loc, target, w, deg, blend=0.75, color=WARM):
    ld = bpy.data.lights.new(name, 'SPOT'); ld.energy = w; ld.color = color; ld.spot_size = math.radians(deg); ld.spot_blend = blend; ld.shadow_soft_size = 0.03
    lo = bpy.data.objects.new(name, ld); lo.location = Vector(loc); scene.collection.objects.link(lo)
    lo.rotation_euler = (Vector(target) - lo.location).to_track_quat('-Z', 'Y').to_euler()
area('Sky Window', (wm, Y1 + 0.06, (WZ0 + WZ1) / 2), WX1 - WX0 - 0.1, WZ1 - WZ0 - 0.1, 260, (0.92, 0.96, 1.0), target=(wm, 0.0, 0.6))
sun = bpy.data.lights.new('Sun', 'SUN'); sun.energy = 3.2; sun.color = (1.0, 0.90, 0.74); sun.angle = math.radians(1.5)
so = bpy.data.objects.new('Sun', sun); scene.collection.objects.link(so); so.rotation_euler = (Vector((0.35, -1.0, -0.55)) * -1).to_track_quat('Z', 'Y').to_euler()
for i_, (x_, y_) in enumerate(DL): spot('DL%d' % i_, (x_, y_, DLZ - 0.02), (x_, y_, 0.0), 24, 80, 0.8)
for nm_, loc_, rot_, sx_, sy_ in (('Cove L', (FC['x0'] + 0.09, (FC['y0'] + FC['y1']) / 2, H - 0.02), (0, math.radians(-40), 0), 0.08, FC['y1'] - FC['y0'] - 0.2),
                                  ('Cove R', (FC['x1'] - 0.09, (FC['y0'] + FC['y1']) / 2, H - 0.02), (0, math.radians(40), 0), 0.08, FC['y1'] - FC['y0'] - 0.2),
                                  ('Cove F', ((FC['x0'] + FC['x1']) / 2, FC['y0'] + 0.09, H - 0.02), (math.radians(40), 0, 0), FC['x1'] - FC['x0'] - 0.2, 0.08),
                                  ('Cove B', ((FC['x0'] + FC['x1']) / 2, FC['y1'] - 0.09, H - 0.02), (math.radians(-40), 0, 0), FC['x1'] - FC['x0'] - 0.2, 0.08)):
    area(nm_, loc_, sx_, sy_, 18, (1.0, 0.82, 0.58), rot=rot_)
for nm, (xa, xb, ya, yb) in (('LED R1', (X1 - 0.33, X1 - 0.31, -1.38, 0.06)), ('LED R2', (X1 - 0.33, X1 - 0.31, 0.85, Y1 - 0.36)), ('LED B', (WX1 + 0.20, X1 - 0.36, Y1 - 0.33, Y1 - 0.31))):
    area(nm, ((xa + xb) / 2, (ya + yb) / 2, UZ0 - 0.01), max(xb - xa, 0.03), max(yb - ya, 0.03), 14 * max(xb - xa, yb - ya) / 0.5, (1.0, 0.85, 0.62))
area('Fill', (0.0, 0.0, H - 0.05), 2.4, 3.0, 22, (1.0, 0.95, 0.88))
area('Hall', (0.0, Y0 - 1.2, 1.4), 1.6, 2.0, 60, (1.0, 0.92, 0.82), target=(0.0, 0.5, 1.0))
world = bpy.data.worlds.new('W'); scene.world = world; world.use_nodes = True
world.node_tree.nodes['Background'].inputs['Color'].default_value = (0.75, 0.82, 0.92, 1); world.node_tree.nodes['Background'].inputs['Strength'].default_value = 0.6

# ---------------------------------------------------------------- bake light into every lightmap
scene.render.engine = 'CYCLES'; scene.cycles.device = 'CPU'
if not QUICK:
    scene.cycles.samples = 12 if FAST else 160
    scene.render.bake.target = 'IMAGE_TEXTURES'; scene.render.bake.margin = 8; scene.render.bake.use_clear = True
    bpy.ops.object.select_all(action='DESELECT')
    for o, _, _ in LM: o.select_set(True)
    bpy.context.view_layer.objects.active = LM[0][0]
    bpy.ops.object.bake(type='DIFFUSE', pass_filter={'DIRECT', 'INDIRECT'}, margin=8, use_clear=True)
    BAKED = {}
    for o, img, uvn in LM:
        w, h = img.size; BAKED[o.name] = gblur(np.array(img.pixels[:], dtype=np.float32).reshape(h, w, 4)[..., :3])
    room_names = {ob.name for ob, _, _ in SHELL if 'Outside' not in ob.name}
    lum = np.concatenate([BAKED[n].reshape(-1, 3) for n in room_names]) @ np.array([0.2126, 0.7152, 0.0722])
    gain = 0.95 / max(1e-4, np.percentile(lum, 98.5)); print('BAKE gain', round(float(gain), 3), 'p50', round(float(np.percentile(lum, 50)), 3))
    LM_IMG = {}
    for o, img, uvn in LM:
        a = np.clip(BAKED[o.name] * gain, 0, 1); h, w = a.shape[:2]
        a = np.where(a <= 0.0031308, a * 12.92, 1.055 * np.power(a, 1 / 2.4) - 0.055)
        LM_IMG[o.name] = save_img('LM_' + o.name, a)
        print('LIGHTMAP', o.name, w, 'px, mean', round(float(a.mean()), 3))

# ---------------------------------------------------------------- previews
scene.view_settings.view_transform = 'AgX'; scene.cycles.samples = 24 if QUICK else 96; scene.cycles.use_denoising = True
cam_d = bpy.data.cameras.new('Cam'); cam = bpy.data.objects.new('Cam', cam_d); scene.collection.objects.link(cam)
tag = 'quick' if QUICK else 'v1'
def shot(name, loc, tgt, lens, res):
    cam_d.lens = lens; cam.location = loc; cam.rotation_euler = (Vector(tgt) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    if FAST or 'nopreview' in ARGS: return
    scene.camera = cam; scene.render.resolution_x, scene.render.resolution_y = res; scene.render.filepath = OUT + '/kitchen_%s_%s.png' % (tag, name); bpy.ops.render.render(write_still=True)
R = (1200, 660) if QUICK else (1800, 1000)
shot('front', (0.0, Y0 - 0.55, 1.50), (0.0, Y1, 1.05), 15, R)              # the reference's view: from the way in
shot('hob', (-0.55, -0.55, 1.55), (1.40, 0.30, 0.90), 20, R)
shot('sink', (0.05, 0.35, 1.55), (0.0, Y1, 1.0), 20, R)
shot('left', (0.70, 0.55, 1.45), (-1.45, -0.55, 1.05), 20, R)
hide = [o for o, _, _ in SHELL if 'Ceiling' in o.name] + [o for o in bpy.data.objects if o.name.startswith(('LM_FalseCeiling', 'Cove Glow'))] + [o for o in bpy.data.objects if o.name.startswith(('LM_Uppers', 'LM_Bulk', 'LM_Chimney', 'DL'))]
for o in hide: o.hide_render = True
pd = bpy.data.cameras.new('Plan'); pd.type = 'ORTHO'; pd.ortho_scale = 3.8
pc = bpy.data.objects.new('Plan', pd); scene.collection.objects.link(pc); pc.location = (0, 0, 8)
if not (FAST or 'nopreview' in ARGS): scene.camera = pc; scene.render.resolution_x = scene.render.resolution_y = 1000; scene.render.filepath = OUT + '/kitchen_%s_plan.png' % tag; bpy.ops.render.render(write_still=True)
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
kw = dict(filepath=OUT + '/kitchen_v1.glb', export_format='GLB', export_apply=True, export_cameras=False, export_lights=False, export_image_format='JPEG', export_jpeg_quality=85)
bpy.ops.export_scene.gltf(**kw)
bpy.ops.wm.save_as_mainfile(filepath=OUT + '/kitchen_v1.blend'); print('DONE', round(os.path.getsize(OUT + '/kitchen_v1.glb') / 1e6, 2), 'MB')
