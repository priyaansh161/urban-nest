# Studio renders of the two collection vases WITH flowers (we never show an empty vase), for the Gemini sheets.
#   blender -b -P render_vases.py -- <room-pilot dir> <out dir>
import bpy, sys, os, math
from mathutils import Vector
root, out = sys.argv[sys.argv.index('--') + 1: sys.argv.index('--') + 3]
JOBS = [('14-ribbed-ceramic-vase', 'ribbed-ceramic-vase-for-home-decor-modern-minimali-light.glb', 0.30, 0.40),
        ('15-spring-vase', 'Spring Vase.glb', 0.20, 0.28)]
def bounds(objs):
    mn = Vector((1e9,) * 3); mx = Vector((-1e9,) * 3)
    for o in objs:
        if o.type != 'MESH': continue
        for c in o.bound_box:
            w = o.matrix_world @ Vector(c)
            for i in range(3): mn[i] = min(mn[i], w[i]); mx[i] = max(mx[i], w[i])
    return mn, mx
def load(path, height, z0):
    before = set(bpy.data.objects); bpy.ops.import_scene.gltf(filepath=path)
    new = [o for o in bpy.data.objects if o not in before]
    tops = [o for o in new if o.parent is None]
    bpy.context.view_layer.update(); mn, mx = bounds(new)
    s = height / (mx.z - mn.z)
    for o in tops: o.scale = (o.scale.x * s, o.scale.y * s, o.scale.z * s)
    bpy.context.view_layer.update(); mn, mx = bounds(new)
    c = (mn + mx) / 2
    for o in tops: o.location -= Vector((c.x, c.y, mn.z - z0))
    bpy.context.view_layer.update(); return new
for name, vase, vh, fh in JOBS:
    bpy.ops.wm.read_factory_settings(use_empty=True); sc = bpy.context.scene
    load(os.path.join(root, 'products', vase), vh, 0.0)
    load(os.path.join(root, 'staging', 'flowers.glb'), fh, vh - 0.03)
    sc.render.engine = 'CYCLES'; sc.cycles.samples = 64; sc.cycles.use_denoising = True
    sc.view_settings.view_transform = 'AgX'; sc.render.resolution_x = sc.render.resolution_y = 800
    sc.render.film_transparent = True; sc.render.image_settings.color_mode = 'RGBA'   # cut-out: a white vase cannot be told from a light backdrop
    w = bpy.data.worlds.new('w'); sc.world = w; w.use_nodes = True
    w.node_tree.nodes['Background'].inputs['Color'].default_value = (0.95, 0.94, 0.92, 1); w.node_tree.nodes['Background'].inputs['Strength'].default_value = 0.9
    for loc, e in [((1.2, -1.4, 1.6), 120), ((-1.4, -0.6, 0.9), 50)]:
        ld = bpy.data.lights.new('k', 'AREA'); ld.energy = e; ld.size = 1.0
        lo = bpy.data.objects.new('k', ld); lo.location = loc; lo.rotation_euler = (Vector((0, 0, 0.25)) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler(); sc.collection.objects.link(lo)
    total = vh + fh - 0.03
    cd = bpy.data.cameras.new('c'); cd.lens = 70
    cam = bpy.data.objects.new('c', cd); sc.collection.objects.link(cam); sc.camera = cam
    target = Vector((0, 0, total / 2)); cam.location = target + Vector((0, -1, 0.25)).normalized() * total * 3.6
    cam.rotation_euler = (target - cam.location).to_track_quat('-Z', 'Y').to_euler()
    sc.render.filepath = os.path.join(out, name + '.png'); bpy.ops.render.render(write_still=True); print('VASE', name)
