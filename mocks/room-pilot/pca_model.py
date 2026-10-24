# Finds the model's long axis in the floor plane (angle from +X, degrees) and its size along the long/short axes.
import bpy, sys, math
import numpy as np
f = sys.argv[sys.argv.index('--') + 1]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=f)
pts = []
for o in bpy.context.scene.objects:
    if o.type == 'MESH':
        pts += [tuple(o.matrix_world @ v.co) for v in o.data.vertices]
p = np.array(pts); xy = p[:, :2] - p[:, :2].mean(0)
w, v = np.linalg.eigh(np.cov(xy.T)); ax = v[:, 1]
ang = math.degrees(math.atan2(ax[1], ax[0]))
u = xy @ v[:, 1]; s = xy @ v[:, 0]
print('PCA long_axis_angle_deg', round(ang, 1), 'long', round(u.max() - u.min(), 3), 'short', round(s.max() - s.min(), 3), 'height', round(p[:, 2].max() - p[:, 2].min(), 3))
# which side is the bowl opening / drain? centroid height of top 10% vs bottom
print('PCA zmin', round(p[:, 2].min(), 3), 'zmax', round(p[:, 2].max(), 3))
