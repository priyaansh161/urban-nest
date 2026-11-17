# Splits a Meshy model into its loose parts and lists them (size, centre), or keeps only the parts named and exports.
#   blender -b -P mocks/sofas/parts.py -- <in.glb>                          list parts
#   blender -b -P mocks/sofas/parts.py -- <in.glb> <out.glb> drop <i,j,..>  export without those parts
#   blender -b -P mocks/sofas/parts.py -- <in.glb> <out.glb> cut <expr>     export without faces whose centre matches expr (x,y,z, metres)
import bpy, sys, bmesh
from mathutils import Vector
a = sys.argv[sys.argv.index('--') + 1:]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=a[0])
obs = [o for o in bpy.context.scene.objects if o.type == 'MESH']
for o in obs: o.select_set(True)
bpy.context.view_layer.objects.active = obs[0]
if len(obs) > 1: bpy.ops.object.join()
o = bpy.context.view_layer.objects.active
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
if len(a) > 2 and a[2] == 'cut':
    bm = bmesh.new(); bm.from_mesh(o.data)
    f = eval('lambda x, y, z: ' + a[3])
    gone = [fc for fc in bm.faces if f(*fc.calc_center_median())]
    bmesh.ops.delete(bm, geom=gone, context='FACES'); bm.to_mesh(o.data); bm.free()
    print('cut', len(gone), 'faces')
else:
    bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.select_all(action='SELECT'); bpy.ops.mesh.separate(type='LOOSE'); bpy.ops.object.mode_set(mode='OBJECT')
    parts = sorted([p for p in bpy.context.scene.objects if p.type == 'MESH'], key=lambda p: -len(p.data.polygons))
    for i, p in enumerate(parts):
        bb = [p.matrix_world @ Vector(c) for c in p.bound_box]
        mn = Vector((min(v.x for v in bb), min(v.y for v in bb), min(v.z for v in bb))); mx = Vector((max(v.x for v in bb), max(v.y for v in bb), max(v.z for v in bb)))
        if i < 40: print('PART %d faces %d  x %.2f..%.2f  y %.2f..%.2f  z %.2f..%.2f' % (i, len(p.data.polygons), mn.x, mx.x, mn.y, mx.y, mn.z, mx.z))
    print('PARTS', len(parts))
    if len(a) > 2 and a[2] == 'drop':
        for i in map(int, a[3].split(',')): bpy.data.objects.remove(parts[i])
if len(a) > 1:
    bpy.ops.export_scene.gltf(filepath=a[1], export_format='GLB', export_yup=True)
    print('EXPORTED', a[1])
