# Clean Blender builds of two products whose Meshy models came out shabby (grey, scratched rack; speckled brush):
#   bath-towel-rack.glb   Gloxy Premium Towel Rack, 24" black matte stainless steel (59 x 23.4 x 19.7 cm):
#                         two wall brackets, a shelf of five flat rails, a towel rod below, double hooks at the
#                         bracket feet and three sliding hooks; folded white towels on the shelf, an olive hand
#                         towel over the rod (as in its listing photos)
#   bath-toilet-brush.glb BonKaso Tilly: white open-front holder 13.5 cm tall on an 11.5 cm light-grey foot,
#                         round grey-white bristle head inside, white + light-grey handle
# Real metres; base at z = 0, the wall side at y = 0, the front toward -y (the room); Draco.
#   blender -b -P make_rack_brush.py -- <products dir>
import bpy, bmesh, sys, os, math, tempfile
import numpy as np
from mathutils import Vector
out = sys.argv[sys.argv.index('--') + 1]
TMP = tempfile.mkdtemp(prefix='rackbrush_')
rng = np.random.default_rng(5)

def img(name, arr):
    h, w = arr.shape[:2]; rgba = np.ones((h, w, 4), dtype=np.float32); rgba[..., :3] = np.clip(arr, 0, 1)
    im = bpy.data.images.new(name, w, h, alpha=False); im.pixels.foreach_set(rgba.ravel())
    p = os.path.join(TMP, name + '.png'); im.filepath_raw = p; im.file_format = 'PNG'; im.save()
    im2 = bpy.data.images.load(p); im2.pack(); return im2

def towel_tex(name, base, band=None, S=512):
    """Terry towel: a fine woven loop texture, soft mottling, and (for the hand towel) a woven border band."""
    y, x = np.mgrid[0:S, 0:S] / S
    loops = 0.5 + 0.5 * np.sin(x * 2 * np.pi * 90) * np.sin(y * 2 * np.pi * 90)
    v = 0.86 + 0.10 * loops + 0.06 * (rng.random((S, S)) - 0.5)
    arr = np.array(base)[None, None, :] * v[..., None]
    if band:
        b = ((y > 0.08) & (y < 0.15)) | ((y > 0.85) & (y < 0.92))
        arr[b] = np.array(band)[None, :] * (0.9 + 0.1 * np.sin(x[b] * 2 * np.pi * 160))[:, None]
    return img(name, arr)

def mat(name, color, rough, metal=0.0, image=None):
    m = bpy.data.materials.new(name); m.use_nodes = True; b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (*color, 1); b.inputs['Roughness'].default_value = rough; b.inputs['Metallic'].default_value = metal
    if image:
        t = m.node_tree.nodes.new('ShaderNodeTexImage'); t.image = image; m.node_tree.links.new(t.outputs['Color'], b.inputs['Base Color'])
    return m

def box(loc, dim, m, bevel=0.0015, seg=3):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc); o = bpy.context.active_object; o.scale = dim
    bpy.ops.object.transform_apply(scale=True); o.data.materials.append(m)
    if bevel:
        bv = o.modifiers.new('b', 'BEVEL'); bv.width = bevel; bv.segments = seg; bpy.ops.object.modifier_apply(modifier=bv.name)
    bpy.ops.object.shade_smooth(); return o

def cyl(loc, r, h, m, rot=(0, 0, 0), seg=24, bevel=0.0):
    bpy.ops.mesh.primitive_cylinder_add(vertices=seg, radius=r, depth=h, location=loc, rotation=rot); o = bpy.context.active_object
    o.data.materials.append(m)
    if bevel:
        bv = o.modifiers.new('b', 'BEVEL'); bv.width = bevel; bv.segments = 2; bpy.ops.object.modifier_apply(modifier=bv.name)
    bpy.ops.object.shade_smooth(); return o

def tube(pts, r, m, res=10):
    """Round bar along a polyline (hooks)."""
    cu = bpy.data.curves.new('t', 'CURVE'); cu.dimensions = '3D'; cu.bevel_depth = r; cu.bevel_resolution = 3; cu.use_fill_caps = True
    sp = cu.splines.new('POLY'); sp.points.add(len(pts) - 1)
    for p, q in zip(sp.points, pts): p.co = (*q, 1)
    cu.materials.append(m); o = bpy.data.objects.new('t', cu); bpy.context.scene.collection.objects.link(o); return o

def hook(x, y, z, m, depth=0.03, drop=0.035):
    """J hook hanging from (x, y, z): down, then curling out toward the front and up."""
    pts = [(x, y, z), (x, y, z - drop)]
    for k in range(1, 10):
        a = math.pi * k / 9
        pts.append((x, y - depth / 2 + math.cos(a) * depth / 2, z - drop - math.sin(a) * depth / 2 * 0.9))
    pts.append((x, y - depth, z - drop + 0.008))
    return tube(pts, 0.0028, m)

def soft_box(loc, dim, m, bevel):
    """A folded towel: a box with very round edges and a slight sag."""
    o = box(loc, dim, m, bevel=bevel, seg=5)
    for v in o.data.vertices:
        v.co.z -= 0.004 * (1 - (2 * v.co.x / dim[0]) ** 2)
    return o

def hanging_fall(x0, y, z_top, width, length, m, folds=3):
    """One fall of a towel hanging from the rod: a cloth panel with soft vertical folds that settle toward the
    hem, a rounded hem, and UVs running down the towel (so the woven band crosses it near the bottom)."""
    bm = bmesh.new(); NX, NZ = 24, 30; th = 0.004
    uv = bm.loops.layers.uv.new('UVMap'); grid = {}
    for side, dy in (('f', -th), ('b', th)):
        for i in range(NX + 1):
            for k in range(NZ + 1):
                u, t = i / NX, k / NZ
                fold = 0.0035 * math.sin(u * math.pi * 2 * folds) * (0.4 + 0.6 * t)       # folds deepen toward the hem
                hem = 0.004 * math.sin(u * math.pi) * t ** 6                                # the hem curls a little
                grid[side, i, k] = bm.verts.new((x0 - width / 2 + u * width, y + dy + fold + hem, z_top - t * length))
    for side in ('f', 'b'):
        for i in range(NX):
            for k in range(NZ):
                q = [grid[side, i, k], grid[side, i + 1, k], grid[side, i + 1, k + 1], grid[side, i, k + 1]]
                f = bm.faces.new(q if side == 'b' else q[::-1])
                for lp, (a, b) in zip(f.loops, ((i, k), (i + 1, k), (i + 1, k + 1), (i, k + 1)) if side == 'b' else ((i, k + 1), (i + 1, k + 1), (i + 1, k), (i, k))):
                    lp[uv].uv = (a / NX, 1 - b / NZ)
    for i in range(NX):                                                                        # close the hem and sides
        bm.faces.new((grid['f', i, NZ], grid['f', i + 1, NZ], grid['b', i + 1, NZ], grid['b', i, NZ]))
    for i in (0, NX):
        for k in range(NZ):
            bm.faces.new((grid['f', i, k], grid['f', i, k + 1], grid['b', i, k + 1], grid['b', i, k]))
    me = bpy.data.meshes.new('fall'); bm.to_mesh(me); bm.free(); me.materials.append(m)
    for p in me.polygons: p.use_smooth = True
    o = bpy.data.objects.new('fall', me); bpy.context.scene.collection.objects.link(o); return o

def finish(objs, name):
    for o in [o for o in objs if o.type == 'CURVE']:
        bpy.ops.object.select_all(action='DESELECT'); o.select_set(True); bpy.context.view_layer.objects.active = o
        bpy.ops.object.convert(target='MESH'); bpy.ops.object.shade_smooth()
    meshes = [o for o in bpy.context.scene.objects if o.type == 'MESH']
    bpy.ops.object.select_all(action='DESELECT')
    for o in meshes: o.select_set(True)
    bpy.context.view_layer.objects.active = meshes[0]; bpy.ops.object.join(); j = bpy.context.active_object; j.name = name
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    p = os.path.join(out, name + '.glb')
    bpy.ops.export_scene.gltf(filepath=p, export_format='GLB', export_apply=True, export_image_format='JPEG', export_jpeg_quality=90,
                              export_draco_mesh_compression_enable=True, export_draco_mesh_compression_level=6)
    dims = [round(d, 3) for d in j.dimensions]
    print('BUILT', name, len(j.data.polygons), 'faces', dims, round(os.path.getsize(p) / 1e3), 'KB')

# ---------------------------------------------------------------- towel rack
bpy.ops.wm.read_factory_settings(use_empty=True)
BLACK = mat('Matte Black Steel', (0.018, 0.018, 0.02), 0.55, 0.2)   # powder-coat matte: little metal, or it mirrors the white room and reads grey
W, D, H = 0.59, 0.234, 0.197
BX = 0.255                                       # brackets at +-BX
objs = []
for s in (-1, 1):
    x = s * BX
    objs.append(box((x, -0.006, H / 2), (0.024, 0.012, H), BLACK))                  # wall bracket
    objs.append(box((x, -D / 2, H - 0.007), (0.020, D, 0.014), BLACK))              # shelf arm, straight out
    objs.append(cyl((x, -0.020, H - 0.024), 0.007, 0.012, BLACK, rot=(math.pi / 2, 0, 0)))   # hinge knuckle
    objs.append(box((x, -0.035, 0.070), (0.016, 0.060, 0.012), BLACK))              # rod arm
    objs.append(hook(x - 0.010, -0.010, 0.008, BLACK)); objs.append(hook(x + 0.010, -0.010, 0.008, BLACK))   # double hook
for i, y in enumerate((-0.035, -0.080, -0.125, -0.170, -0.218)):                     # five flat shelf rails
    objs.append(box((0, y, H + 0.004), (W, 0.016 if i < 4 else 0.020, 0.008), BLACK, bevel=0.003))
    for s in (-1, 1): objs.append(box((s * (W / 2 + 0.004), y, H + 0.004), (0.010, 0.017 if i < 4 else 0.022, 0.010), BLACK, bevel=0.0035))   # end caps
objs.append(cyl((0, -0.062, 0.070), 0.0085, W - 0.03, BLACK, rot=(0, math.pi / 2, 0)))   # towel rod
for s in (-1, 1): objs.append(cyl((s * (W - 0.03) / 2, -0.062, 0.070), 0.0105, 0.012, BLACK, rot=(0, math.pi / 2, 0), bevel=0.003))
for x in (-0.12, -0.085, -0.05): objs.append(hook(x, -0.062, 0.070 - 0.009, BLACK, depth=0.022, drop=0.030))   # sliding hooks
WHITE_T = mat('White Towel', (1, 1, 1), 0.95, image=towel_tex('towel_white', (0.93, 0.93, 0.91)))
OLIVE_T = mat('Olive Towel', (1, 1, 1), 0.95, image=towel_tex('towel_olive', (0.47, 0.42, 0.22), band=(0.40, 0.36, 0.18)))
objs.append(soft_box((0.04, -0.118, H + 0.026), (0.30, 0.17, 0.036), WHITE_T, 0.014))   # two folded towels on the shelf
objs.append(soft_box((0.045, -0.120, H + 0.060), (0.28, 0.16, 0.032), WHITE_T, 0.013))
# the olive hand towel over the rod: a long front fall, a shorter back fall, and the fold over the top
TX0, TW = 0.13, 0.15
objs.append(hanging_fall(TX0, -0.0745, 0.070, TW, 0.30, OLIVE_T))
objs.append(hanging_fall(TX0, -0.0495, 0.070, TW, 0.21, OLIVE_T, folds=2))
objs.append(cyl((TX0, -0.062, 0.070), 0.0128, TW, OLIVE_T, rot=(0, math.pi / 2, 0), seg=20))
finish(objs, 'bath-towel-rack')

# ---------------------------------------------------------------- toilet brush
bpy.ops.wm.read_factory_settings(use_empty=True)
WHITE = mat('White Plastic', (0.93, 0.93, 0.92), 0.35)
GREY = mat('Light Grey', (0.70, 0.71, 0.72), 0.45)
y_, x_ = np.mgrid[0:256, 0:256] / 256
bristles = 0.78 + 0.22 * (np.sin((x_ * 120 + np.sin(y_ * 30) * 2) * np.pi) > 0.2)   # fine bristle streaks
BRISTLE = mat('Bristles', (1, 1, 1), 0.9, image=img('bristles', np.stack([bristles * 0.86, bristles * 0.87, bristles * 0.88], -1)))
objs = []
RX, RY, HH = 0.050, 0.041, 0.135
# holder: an oval shell, a little narrower at the top, with a tall open window in the front
bm = bmesh.new()
N, L = 48, 12
rings = []
for i in range(L + 1):
    t = i / L; z = 0.012 + t * (HH - 0.012); k = 1 - 0.14 * t
    rings.append([bm.verts.new((math.cos(2 * math.pi * j / N) * RX * k, math.sin(2 * math.pi * j / N) * RY * k, z)) for j in range(N)])
for i in range(L):
    for j in range(N):
        a, b = rings[i][j], rings[i][(j + 1) % N]; c, d = rings[i + 1][(j + 1) % N], rings[i + 1][j]
        ang = 2 * math.pi * (j + 0.5) / N; z = 0.012 + (i + 0.5) / L * (HH - 0.012)
        front = math.sin(ang) < -0.80 and 0.030 < z < 0.118          # the scoop-shaped opening, facing -y
        if not front: bm.faces.new((a, b, c, d))
bot = bm.faces.new(rings[0][::-1])
me = bpy.data.meshes.new('holder'); bm.to_mesh(me); bm.free()
shell = bpy.data.objects.new('holder', me); bpy.context.scene.collection.objects.link(shell); me.materials.append(WHITE)
sd = shell.modifiers.new('s', 'SOLIDIFY'); sd.thickness = 0.003; bpy.context.view_layer.objects.active = shell; bpy.ops.object.modifier_apply(modifier=sd.name)
bv = shell.modifiers.new('b', 'BEVEL'); bv.width = 0.0012; bv.segments = 2; bpy.ops.object.modifier_apply(modifier=bv.name)
for p in me.polygons: p.use_smooth = True
objs.append(shell)
foot = cyl((0, 0, 0.006), 1.0, 0.012, GREY, seg=48, bevel=0.003); foot.scale = (0.0575, 0.047, 1); objs.append(foot)
# the head: a grey core and ~700 TPR bristles radiating from it, white at the tips (as in the listing's close-up)
bpy.ops.mesh.primitive_uv_sphere_add(segments=24, ring_count=12, radius=0.014, location=(0, -0.004, 0.058))
core = bpy.context.active_object; core.data.materials.append(GREY); bpy.ops.object.shade_smooth(); objs.append(core)
bm = bmesh.new(); C = Vector((0, -0.004, 0.058)); NB = 700; gold = math.pi * (3 - math.sqrt(5))
for n in range(NB):
    zz = 1 - 2 * (n + 0.5) / NB; rr = math.sqrt(1 - zz * zz); a = gold * n
    d = Vector((math.cos(a) * rr, math.sin(a) * rr, zz * 1.1)).normalized()
    side = d.cross(Vector((0, 0, 1)) if abs(d.z) < 0.9 else Vector((1, 0, 0))).normalized() * 0.0007
    up = d.cross(side).normalized() * 0.0007
    base = C + d * 0.012; tip = C + d * (0.031 + 0.002 * math.sin(n * 7.3))
    vs = [bm.verts.new(base + side), bm.verts.new(base + up), bm.verts.new(base - side), bm.verts.new(base - up), bm.verts.new(tip)]
    for k in range(4): bm.faces.new((vs[k], vs[(k + 1) % 4], vs[4]))
me = bpy.data.meshes.new('bristles'); bm.to_mesh(me); bm.free(); me.materials.append(BRISTLE)
objs.append(bpy.data.objects.new('bristles', me)); bpy.context.scene.collection.objects.link(objs[-1])
objs.append(cyl((0, -0.004, 0.105), 0.0060, 0.090, GREY, seg=20))          # lower shaft (inside + just above the holder)
objs.append(cyl((0, -0.004, 0.255), 0.0066, 0.210, WHITE, seg=20, bevel=0.002))   # handle
objs.append(cyl((0, -0.004, 0.152), 0.0075, 0.012, GREY, seg=20, bevel=0.002))    # grip collar
finish(objs, 'bath-toilet-brush')
