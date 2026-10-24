# blender -b -P prep_one.py -- <raw.glb> <out.glb> [target_tris]
# Draco + 1024px JPEG textures for one staging model; decimates only if above target_tris. Prints size info.
import bpy, sys, os
from mathutils import Vector
a = sys.argv[sys.argv.index('--') + 1:]
src, dst = a[0], a[1]; target = int(a[2]) if len(a) > 2 else 30000
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=src)
meshes = [o for o in bpy.context.scene.objects if o.type == 'MESH']
tris = sum(len(p.vertices) - 2 for o in meshes for p in o.data.polygons)
if tris > target:
    for o in meshes:
        bpy.context.view_layer.objects.active = o
        d = o.modifiers.new('d', 'DECIMATE'); d.ratio = target / tris
        bpy.ops.object.modifier_apply(modifier=d.name)
for img in bpy.data.images:
    if max(img.size) > 1024: img.scale(1024, 1024)
mn = Vector((1e9,) * 3); mx = Vector((-1e9,) * 3)
for o in meshes:
    for c in o.bound_box:
        w = o.matrix_world @ Vector(c)
        for i in range(3): mn[i] = min(mn[i], w[i]); mx[i] = max(mx[i], w[i])
print('SIZE tris_before', tris, 'tris_after', sum(len(p.vertices) - 2 for o in meshes for p in o.data.polygons), 'dims(blender x,y,z)', [round(mx[i] - mn[i], 3) for i in range(3)])
bpy.ops.export_scene.gltf(filepath=dst, export_format='GLB', export_apply=True, export_image_format='JPEG', export_jpeg_quality=88,
                          export_draco_mesh_compression_enable=True, export_draco_mesh_compression_level=6)
print('SAVED', dst, round(os.path.getsize(dst) / 1e6, 2), 'MB')
