# Prints triangle count, bounding box (Blender Z-up after glTF import), and texture sizes for each given glb.
import bpy, sys, os
files = sys.argv[sys.argv.index('--') + 1:]
for f in files:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=f)
    meshes = [o for o in bpy.context.scene.objects if o.type == 'MESH']
    tris = sum(len(p.vertices) - 2 for o in meshes for p in o.data.polygons)
    mn = [1e9] * 3; mx = [-1e9] * 3
    for o in meshes:
        for c in o.bound_box:
            w = o.matrix_world @ __import__('mathutils').Vector(c)
            for i in range(3): mn[i] = min(mn[i], w[i]); mx[i] = max(mx[i], w[i])
    print('MODEL', os.path.basename(f), 'meshes', len(meshes), 'tris', tris)
    print('  size x,y,z (Blender Z-up):', [round(mx[i] - mn[i], 3) for i in range(3)], 'min', [round(v, 3) for v in mn])
    print('  images:', [(i.name, tuple(i.size)) for i in bpy.data.images])
