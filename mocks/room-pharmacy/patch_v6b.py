# 1 Nov 2026: the wall clock and the Rx sign print were both built facing into the wall. Turn them round.
import bpy, math, mathutils, os
HERE = os.path.dirname(bpy.data.filepath)
O = bpy.data.objects
clk = O['Wall clock']
clk.rotation_euler.z += math.pi
clk.location.x = -2.41 if clk.parent is None else clk.location.x      # rim back sits on the wall (inner face -2.45)
sf = O['Rx sign face']
mw = sf.matrix_world.copy(); c = mw.translation.copy()
R = mathutils.Matrix.Translation(c) @ mathutils.Matrix.Rotation(math.pi, 4, 'Z') @ mathutils.Matrix.Translation(-c)
sf.matrix_world = R @ mw
bpy.context.view_layer.update()
print('CLOCK', clk.parent, tuple(round(v, 3) for v in O['Clock face'].matrix_world.translation), 'SIGN', tuple(round(v, 3) for v in sf.matrix_world.translation))
bpy.ops.export_scene.gltf(filepath=os.path.join(HERE, 'pharmacy.glb'), export_format='GLB', export_cameras=False,
                          export_lights=False, export_apply=True, export_yup=True, export_image_format='JPEG', export_jpeg_quality=88)
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
