# The Essentials shower mat (VHKD PVC anti-slip, light blue): rounded slab 70 x 36 cm, 8 mm thick, with a drawn
# texture of grip nubs (dimpled), drain holes, an oval scrub pad at one end and corner rings.
#   blender -b -P make_shower_mat.py -- <out.glb>
import bpy, sys, os, math, tempfile
import numpy as np
out = sys.argv[sys.argv.index('--') + 1]
bpy.ops.wm.read_factory_settings(use_empty=True)
L, Wd, T = 0.70, 0.36, 0.008
PX, PY = 1400, 720                      # 2000 px per metre
yy, xx = np.mgrid[0:PY, 0:PX].astype(float)
X, Y = xx / PX * L, yy / PY * Wd
base = np.array([0.70, 0.79, 0.94]); nubc = np.array([0.77, 0.85, 0.98]); edgec = np.array([0.58, 0.67, 0.85]); holec = np.array([0.32, 0.35, 0.40])
img = np.ones((PY, PX, 3)) * base
# scrub pad: an oval at the left end
pcx, pcy, pa, pb = 0.075, Wd / 2, 0.042, 0.105
pd = ((X - pcx) / pa) ** 2 + ((Y - pcy) / pb) ** 2
pad = pd < 1
ridges = (np.sin(X * 2 * np.pi / 0.004) > 0.3)
img[pad] = np.where(ridges[pad][:, None], nubc * 0.96, base * 0.92)
img[(pd >= 1) & (pd < 1.12)] = edgec
# nubs on a grid, kept off the border and the pad
P, R = 0.026, 0.0095
gx, gy = (X - 0.13) % P - P / 2, (Y - 0.018) % P - P / 2
d = np.sqrt(gx ** 2 + gy ** 2)
zone = (X > 0.135) & (X < L - 0.02) & (Y > 0.02) & (Y < Wd - 0.02)
nub = zone & (d < R)
img[nub] = nubc
img[zone & (d >= R) & (d < R + 0.0012)] = edgec
dimple = nub & (((gx * 1000) % 3.0 < 0.9) & ((gy * 1000) % 3.0 < 0.9))
img[dimple] = nubc * 0.9
# drain holes at the cell corners
hx, hy = (X - 0.13 - P / 2) % P - P / 2, (Y - 0.018 - P / 2) % P - P / 2
img[zone & (np.sqrt(hx ** 2 + hy ** 2) < 0.0028)] = holec
# corner rings
for cx, cy in [(0, 0), (L, 0), (0, Wd), (L, Wd)]:
    r = np.sqrt((X - cx) ** 2 + (Y - cy) ** 2)
    for rr in (0.03, 0.038, 0.046): img[np.abs(r - rr) < 0.0009] = edgec
im = bpy.data.images.new('shower_mat', PX, PY, alpha=False)
rgba = np.ones((PY, PX, 4), dtype=np.float32); rgba[..., :3] = img
im.pixels.foreach_set(rgba.ravel())
p = os.path.join(tempfile.gettempdir(), 'shower_mat_tex.png'); im.filepath_raw = p; im.file_format = 'PNG'; im.save()
tex = bpy.data.images.load(p); tex.pack()
m = bpy.data.materials.new('PVC Shower Mat'); m.use_nodes = True
nt = m.node_tree; b = nt.nodes['Principled BSDF']; t = nt.nodes.new('ShaderNodeTexImage'); t.image = tex
nt.links.new(t.outputs['Color'], b.inputs['Base Color']); b.inputs['Roughness'].default_value = 0.55
# rounded-rectangle top, UV straight from position, then given thickness
r, N = 0.03, 8; pts = []
for cx, cy, a0 in [(L / 2 - r, Wd / 2 - r, 0), (-L / 2 + r, Wd / 2 - r, 90), (-L / 2 + r, -Wd / 2 + r, 180), (L / 2 - r, -Wd / 2 + r, 270)]:
    for k in range(N + 1):
        a = math.radians(a0 + 90 * k / N); pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
verts = [(0, 0, T)] + [(px, py, T) for px, py in pts]
me = bpy.data.meshes.new('Shower Mat'); n = len(pts)
me.from_pydata(verts, [], [(0, 1 + k, 1 + (k + 1) % n) for k in range(n)])
uv = me.uv_layers.new(name='UV')
for poly in me.polygons:
    for li, vi in zip(poly.loop_indices, poly.vertices):
        vx, vy, _ = verts[vi]; uv.data[li].uv = (0.5 + vx / L, 0.5 - vy / Wd)
ob = bpy.data.objects.new('Shower Mat', me); bpy.context.scene.collection.objects.link(ob); me.materials.append(m)
bpy.context.view_layer.objects.active = ob
s = ob.modifiers.new('thick', 'SOLIDIFY'); s.thickness = T; s.offset = -1
bpy.ops.object.modifier_apply(modifier=s.name)
bpy.ops.export_scene.gltf(filepath=out, export_format='GLB', export_apply=True, export_image_format='JPEG', export_jpeg_quality=90)
print('SAVED', out, round(os.path.getsize(out) / 1e6, 2), 'MB')
