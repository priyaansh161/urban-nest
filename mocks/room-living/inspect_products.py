# Lay every product of placements.json in a row at its real height (workbench), to check the models by eye.
import bpy, sys, os, json, math
from mathutils import Vector
OUT = os.path.abspath(sys.argv[sys.argv.index('--') + 1])
bpy.ops.wm.read_factory_settings(use_empty=True); scene = bpy.context.scene
PL = json.load(open(os.path.join(OUT, 'placements.json')))
def bounds(objs):
    mn = Vector((1e9,) * 3); mx = Vector((-1e9,) * 3)
    for o in objs:
        if o.type != 'MESH': continue
        for c in o.bound_box:
            w = o.matrix_world @ Vector(c)
            for i in range(3): mn[i] = min(mn[i], w[i]); mx[i] = max(mx[i], w[i])
    return mn, mx
x = 0
for d in PL['products']:
    before = set(bpy.data.objects); bpy.ops.import_scene.gltf(filepath=os.path.join(OUT, 'products', d['file']))
    new = [o for o in bpy.data.objects if o not in before]
    root = bpy.data.objects.new('r', None); scene.collection.objects.link(root)
    for o in new:
        if o.parent is None: o.parent = root
    bpy.context.view_layer.update(); mn, mx = bounds(new); sz = mx - mn; s = d['length'] / max(sz.x, sz.y) if 'length' in d else d['height'] / sz.z
    root.scale = (s, s, s); bpy.context.view_layer.update(); mn, mx = bounds(new); c = (mn + mx) / 2
    root.location = (x - c.x, -c.y, -mn.z); x += (mx.x - mn.x) + 0.25
    print(d['name'], 'size cm', [round((mx[i] - mn[i]) * 100) for i in range(3)])
scene.render.engine = 'BLENDER_WORKBENCH'; sh = scene.display.shading; sh.light = 'STUDIO'; sh.color_type = 'TEXTURE'
scene.world = bpy.data.worlds.new('w'); scene.world.color = (0.3, 0.3, 0.3)
cd = bpy.data.cameras.new('c'); cd.type = 'ORTHO'; cd.ortho_scale = x + 0.3; cam = bpy.data.objects.new('c', cd); scene.collection.objects.link(cam); scene.camera = cam
cam.location = (x / 2 - 0.2, -8, 0.85); cam.rotation_euler = (math.pi / 2, 0, 0)
scene.render.resolution_x = 2400; scene.render.resolution_y = int(2400 * 1.9 / (x + 0.3)) + 100; scene.render.filepath = os.path.join(OUT, 'products_row.png'); bpy.ops.render.render(write_still=True)
