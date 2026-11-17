# ASCII top view of a model: each cell the highest face centre there (0-9 = height in tenths of the model's height).
#   blender -b -P mocks/sofas/heightmap.py -- <in.glb>
import bpy, sys
a = sys.argv[sys.argv.index('--') + 1:]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=a[0])
pts = []
for o in bpy.context.scene.objects:
    if o.type == 'MESH':
        M = o.matrix_world
        pts += [M @ p.center for p in o.data.polygons]
X0, X1 = min(p.x for p in pts), max(p.x for p in pts); Y0, Y1 = min(p.y for p in pts), max(p.y for p in pts); Z0, Z1 = min(p.z for p in pts), max(p.z for p in pts)
print('BOUNDS x %.2f..%.2f y %.2f..%.2f z %.3f..%.3f' % (X0, X1, Y0, Y1, Z0, Z1))
N = 48; W = int(N * (X1 - X0) / (Y1 - Y0)) if Y1 > Y0 else N
g = {}
for p in pts:
    i = min(N - 1, int((Y1 - p.y) / (Y1 - Y0) * N)); j = min(W - 1, int((p.x - X0) / (X1 - X0) * W))
    g[(i, j)] = max(g.get((i, j), -1), p.z)
for i in range(N):
    print('ROW %5.2f ' % (Y1 - (i + 0.5) * (Y1 - Y0) / N) + ''.join(str(min(9, int((g[(i, j)] - Z0) / (Z1 - Z0) * 10))) if (i, j) in g else '.' for j in range(W)))
print('COLS x from %.2f step %.3f' % (X0, (X1 - X0) / W))
import collections
h = collections.Counter(round(p.z, 2) for p in pts)
print('LOWZ', sorted(h.items())[:12])
