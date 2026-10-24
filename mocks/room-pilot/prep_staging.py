# Web-ready staging items: your Meshy models from Downloads -> 1024px textures, JPEG, Draco.  Also builds a flower bunch for vases.
#   blender -b -P prep_staging.py -- <downloads dir> <out dir>
import bpy, sys, os, math, random
from mathutils import Vector
dl, out = sys.argv[sys.argv.index('--') + 1: sys.argv.index('--') + 3]
os.makedirs(out, exist_ok=True)
JOBS = [('Meshy_AI_Modern_Porcelain_Toil_1023104416_texture.glb', 'toilet.glb'),
        ('Meshy_AI_Chrome_Rain_Shower_Sy_1023104429_texture.glb', 'shower.glb'),
        ('Meshy_AI_Teal_Rug_with_Concent_1023104508_texture.glb', 'rug.glb')]
def export(path):
    bpy.ops.export_scene.gltf(filepath=path, export_format='GLB', export_apply=True, export_image_format='JPEG', export_jpeg_quality=88,
                              export_draco_mesh_compression_enable=True, export_draco_mesh_compression_level=6)
for src, dst in JOBS:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=os.path.join(dl, src))
    for img in bpy.data.images:
        w, h = img.size
        if max(w, h) > 1024: img.scale(1024, 1024)
    p = os.path.join(out, dst); export(p)
    print('STAGING', dst, round(os.path.getsize(p) / 1e6, 2), 'MB')

# ---- flower bunch: base at origin, ~0.42 m tall, stems fan outward ----
bpy.ops.wm.read_factory_settings(use_empty=True)
rnd = random.Random(21)
def pmat(n, c, r=0.6):
    m = bpy.data.materials.new(n); m.use_nodes = True; b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = c; b.inputs['Roughness'].default_value = r; return m
stem_m, leaf_m = pmat('Stem', (0.22, 0.32, 0.12, 1)), pmat('Leaf', (0.20, 0.36, 0.14, 1))
blooms = [pmat('BloomBlush', (0.92, 0.62, 0.66, 1), 0.7), pmat('BloomWhite', (0.96, 0.94, 0.90, 1), 0.7), pmat('BloomPeach', (0.95, 0.72, 0.55, 1), 0.7)]
centre_m = pmat('Centre', (0.85, 0.65, 0.2, 1))
def between(p0, p1, r, m, seg=6):
    p0, p1 = Vector(p0), Vector(p1); d = p1 - p0
    bpy.ops.mesh.primitive_cylinder_add(vertices=seg, radius=r, depth=d.length, location=(p0 + p1) / 2)
    o = bpy.context.active_object; o.rotation_euler = d.to_track_quat('Z', 'Y').to_euler(); o.data.materials.append(m); return o
def ell(loc, sc, m, rot=(0, 0, 0), seg=8, rings=5):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=seg, ring_count=rings, location=loc, rotation=rot)
    o = bpy.context.active_object; o.scale = sc; o.data.materials.append(m); bpy.ops.object.shade_smooth(); return o
parts = []
N = 11
for k in range(N):
    a = k * 2 * math.pi / N + rnd.uniform(-.25, .25)
    lean = rnd.uniform(0.05, 0.17); h = rnd.uniform(0.28, 0.44)
    tip = Vector((math.cos(a) * lean, math.sin(a) * lean, h))
    mid = Vector((math.cos(a) * lean * .45, math.sin(a) * lean * .45, h * .55))
    parts += [between((0, 0, 0), mid, 0.0035, stem_m), between(mid, tip, 0.0035, stem_m)]
    for t in (0.45, 0.62, 0.78):
        pt = mid.lerp(tip, (t - 0.45) / 0.55 * 0.9)
        for s in (-1, 1):
            parts.append(ell(pt + Vector((math.cos(a + s * 1.4) * .01, math.sin(a + s * 1.4) * .01, 0)), (0.012, 0.0045, 0.032), leaf_m,
                             rot=(rnd.uniform(-.5, .5), rnd.uniform(-.6, .6), a + s * 1.1)))
    if k % 2 == 0 or k % 3 == 0:               # blooms on most stems
        bm = blooms[k % 3]; r = rnd.uniform(0.026, 0.036)
        parts.append(ell(tip, (r, r, r * 0.55), centre_m, seg=8, rings=5))
        for i in range(8):
            ang = i * math.pi / 4
            parts.append(ell(tip + Vector((math.cos(ang) * r * .85, math.sin(ang) * r * .85, r * 0.1)), (r * 0.75, r * 0.38, r * 0.2), bm,
                             rot=(0, rnd.uniform(-.2, .2), ang), seg=8, rings=4))
bpy.ops.object.select_all(action='DESELECT')
for o in parts: o.select_set(True)
bpy.context.view_layer.objects.active = parts[0]; bpy.ops.object.join(); bpy.context.active_object.name = 'Flowers'
fp = os.path.join(out, 'flowers.glb'); export(fp); print('STAGING flowers.glb', round(os.path.getsize(fp) / 1e6, 2), 'MB')
