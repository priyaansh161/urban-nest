# Close-up of the Paxxol cards from the blister station: same scene (blister_station.blend), camera moved in
# over the open Jumbo card so the artwork and the doses in the bubbles read.
#   blender -b blister_station.blend -P cards_closeup.py -- <out.png> [samples]
import bpy, sys
from mathutils import Vector
argv = sys.argv[sys.argv.index('--') + 1:]
cam = bpy.context.scene.camera; cd = cam.data
cd.lens = 45; cam.location = (-0.2, -0.78, 0.42)
cam.rotation_euler = (Vector((-0.12, -0.08, 0.0)) - cam.location).to_track_quat('-Z', 'Y').to_euler()
cd.dof.focus_distance = (Vector((0.04, -0.12, 0.005)) - cam.location).length; cd.dof.aperture_fstop = 5.6
bpy.context.scene.cycles.samples = int(argv[1]) if len(argv) > 1 else 200
bpy.context.scene.render.filepath = argv[0]; bpy.ops.render.render(write_still=True)
print('DONE')
