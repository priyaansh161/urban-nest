import bpy, sys, os, math
from mathutils import Vector
a = sys.argv[sys.argv.index('--') + 1:]
for src in a[1:]:
    bpy.ops.wm.read_factory_settings(use_empty=True); bpy.ops.import_scene.gltf(filepath=os.path.abspath(src))
    obs = [o for o in bpy.context.scene.objects if o.type == 'MESH']
    pts = [o.matrix_world @ Vector(c) for o in obs for c in o.bound_box]
    lo = Vector([min(p[i] for p in pts) for i in range(3)]); hi = Vector([max(p[i] for p in pts) for i in range(3)]); dims = hi - lo
    print('DIMS', os.path.basename(src), [round(d, 3) for d in dims])
    sc = bpy.context.scene; sc.render.engine = 'CYCLES'; sc.cycles.samples = 48; sc.view_settings.view_transform = 'AgX'
    w = bpy.data.worlds.new('w'); sc.world = w; w.use_nodes = True; w.node_tree.nodes['Background'].inputs['Color'].default_value = (0.75, 0.75, 0.74, 1)
    bpy.ops.mesh.primitive_plane_add(size=6, location=(0, 0, lo.z))
    sd = bpy.data.lights.new('s', 'SUN'); sd.energy = 2.5; so = bpy.data.objects.new('s', sd); sc.collection.objects.link(so); so.rotation_euler = (math.radians(40), 0, math.radians(30))
    tgt = (lo + hi) / 2; d = Vector((0.6, -1, 0.55)).normalized()
    cd = bpy.data.cameras.new('c'); cd.lens = 50; cam = bpy.data.objects.new('c', cd); sc.collection.objects.link(cam); sc.camera = cam
    cam.location = tgt + d * dims.length * 1.75; cam.rotation_euler = (tgt - cam.location).to_track_quat('-Z', 'Y').to_euler()
    sc.render.resolution_x = sc.render.resolution_y = 600; sc.render.filepath = os.path.abspath(os.path.join(a[0], os.path.basename(src)[:-4] + '_meshy.png')); bpy.ops.render.render(write_still=True)
