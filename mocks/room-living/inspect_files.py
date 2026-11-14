# Lay given .glb files in a row (equal height, labelled by index) and render a workbench strip.
import bpy, sys, os, math
from mathutils import Vector
args = sys.argv[sys.argv.index('--') + 1:]; out = args[0]; files = args[1:]
bpy.ops.wm.read_factory_settings(use_empty=True); scene = bpy.context.scene
def bounds(objs):
    mn = Vector((1e9,) * 3); mx = Vector((-1e9,) * 3)
    for o in objs:
        if o.type != 'MESH': continue
        for c in o.bound_box:
            w = o.matrix_world @ Vector(c)
            for i in range(3): mn[i] = min(mn[i], w[i]); mx[i] = max(mx[i], w[i])
    return mn, mx
x = 0
for f in files:
    before = set(bpy.data.objects); bpy.ops.import_scene.gltf(filepath=f); new = [o for o in bpy.data.objects if o not in before]
    root = bpy.data.objects.new('r', None); scene.collection.objects.link(root)
    for o in new:
        if o.parent is None: o.parent = root
    bpy.context.view_layer.update(); mn, mx = bounds(new); s = 1.0 / max(mx - mn)
    root.scale = (s, s, s); bpy.context.view_layer.update(); mn, mx = bounds(new); c = (mn + mx) / 2
    root.location = (x - c.x, -c.y, -mn.z); x += 1.25
scene.render.engine = 'BLENDER_WORKBENCH'; sh = scene.display.shading; sh.light = 'STUDIO'; sh.color_type = 'TEXTURE'
scene.world = bpy.data.worlds.new('w'); scene.world.color = (0.8, 0.8, 0.8)
cd = bpy.data.cameras.new('c'); cd.type = 'ORTHO'; cd.ortho_scale = x; cam = bpy.data.objects.new('c', cd); scene.collection.objects.link(cam); scene.camera = cam
cam.location = (x / 2 - 0.62, -6, 2.0); cam.rotation_euler = (math.radians(75), 0, 0)
scene.render.resolution_x = 2400; scene.render.resolution_y = int(2400 * 1.4 / x) + 60; scene.render.filepath = out; bpy.ops.render.render(write_still=True)
