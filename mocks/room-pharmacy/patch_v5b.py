# Paint out the removed gloves box's baked shadow on the counter lightmap (31 Oct 2026): mask the footprint plus its
# soft edge in lightmap space, then fill it from the surrounding pixels (Laplace inpaint), so no re-bake is needed.
import bpy, bmesh, math, numpy as np
from mathutils import Vector
from mathutils.geometry import intersect_point_tri_2d, barycentric_transform
o = bpy.data.objects['LM_Counter']; mw = o.matrix_world
img = bpy.data.images['LM_LM_Counter.png']; W, H = img.size
bm = bmesh.new(); bm.from_mesh(o.data); lm = bm.loops.layers.uv['LM']
tris = [t for t in bm.calc_loop_triangles() if (mw.to_3x3() @ t[0].face.normal).z > 0.99]
CX, CY, R, HX, HY, PAD = 0.13, 0.1, 0.25, 0.12, 0.0625, 0.07
mask = np.zeros((H, W), bool)
for i in range(-60, 61):
    for j in range(-40, 41):
        lx, ly = i / 60 * (HX + PAD), j / 40 * (HY + PAD)
        p = Vector((CX + lx * math.cos(R) - ly * math.sin(R), CY + lx * math.sin(R) + ly * math.cos(R), 0))
        for t in tris:
            w = [mw @ l.vert.co for l in t]; w2 = [Vector((v.x, v.y, 0)) for v in w]
            if intersect_point_tri_2d(p, *w2):
                uv = barycentric_transform(p, *w2, *[Vector((l[lm].uv.x, l[lm].uv.y, 0)) for l in t])
                x, y = int(uv.x * W), int(uv.y * H)
                mask[max(0, y - 2):y + 3, max(0, x - 2):x + 3] = True
                break
ys, xs = np.nonzero(mask); print('masked px', len(ys))
a = np.array(img.pixels[:], np.float32).reshape(H, W, 4)
y0, y1, x0, x1 = ys.min() - 6, ys.max() + 7, xs.min() - 6, xs.max() + 7
crop = a[y0:y1, x0:x1, :3].copy(); m = mask[y0:y1, x0:x1]
crop[m] = crop[~m].mean(0)
for _ in range(3000):
    avg = (np.roll(crop, 1, 0) + np.roll(crop, -1, 0) + np.roll(crop, 1, 1) + np.roll(crop, -1, 1)) / 4
    crop[m] = avg[m]
a[y0:y1, x0:x1, :3] = crop
img.pixels.foreach_set(a.ravel()); img.pack()
bpy.ops.export_scene.gltf(filepath=bpy.path.abspath('//pharmacy.glb'), export_format='GLB', export_cameras=False,
                          export_lights=False, export_apply=True, export_yup=True, export_image_format='JPEG', export_jpeg_quality=88)
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
print('PATCHED shadow')
