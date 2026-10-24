# Renders each glb from 4 sides (front/right/back/left, Blender -Y/+X/+Y/-X) into one PNG per model.
import bpy, sys, os, math
from mathutils import Vector
args = sys.argv[sys.argv.index('--') + 1:]
outdir, files = args[0], args[1:]
for f in files:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=f)
    sc = bpy.context.scene
    objs = [o for o in sc.objects if o.type == 'MESH']
    mn = Vector((1e9,) * 3); mx = Vector((-1e9,) * 3)
    for o in objs:
        for c in o.bound_box:
            w = o.matrix_world @ Vector(c)
            for i in range(3): mn[i] = min(mn[i], w[i]); mx[i] = max(mx[i], w[i])
    ctr = (mn + mx) / 2; r = max((mx - mn)) * 1.3
    sc.render.engine = 'BLENDER_WORKBENCH'
    sc.display.shading.light = 'STUDIO'; sc.display.shading.color_type = 'TEXTURE'
    sc.render.resolution_x = sc.render.resolution_y = 420
    sc.render.film_transparent = False
    sc.world = bpy.data.worlds.new('w'); sc.world.color = (0.85, 0.85, 0.85)
    cam_d = bpy.data.cameras.new('c'); cam_d.type = 'ORTHO'; cam_d.ortho_scale = r
    cam = bpy.data.objects.new('c', cam_d); sc.collection.objects.link(cam); sc.camera = cam
    base = os.path.splitext(os.path.basename(f))[0][:22]
    for name, d in [('front_-Y', (0, -1, 0.15)), ('right_+X', (1, 0, 0.15)), ('back_+Y', (0, 1, 0.15)), ('left_-X', (-1, 0, 0.15)), ('top', (0, -0.05, 1))]:
        cam.location = ctr + Vector(d).normalized() * r * 2
        cam.rotation_euler = (ctr - cam.location).to_track_quat('-Z', 'Y').to_euler()
        sc.render.filepath = os.path.join(outdir, base + '__' + name + '.png'); bpy.ops.render.render(write_still=True)
print('DONE')
