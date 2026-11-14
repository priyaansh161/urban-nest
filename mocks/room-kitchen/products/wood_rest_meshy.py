# Wooden spatula rest (2759a7b9), 11.9 x 11.4 x 1.8 cm: Meshy's shape (built from listing photo 1, it got the wide front, the
# narrowing sides and the rolled back right) with Meshy's flat caramel paint replaced by the carved acacia grain from
# wood_rest.py.   blender -b -P wood_rest_meshy.py -- <outdir>
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from klib import *

reset()
RAW = os.path.abspath(os.path.join(HERE, '..', '..', '..', 'models', 'source', 'wooden-spatula-rest-raw.glb'))
bpy.ops.import_scene.gltf(filepath=RAW)
objs = [o for o in bpy.context.scene.objects if o.type == 'MESH']
bpy.ops.object.select_all(action='DESELECT')
for o in objs: o.select_set(True)
bpy.context.view_layer.objects.active = objs[0]
if len(objs) > 1: bpy.ops.object.join()
o = bpy.context.view_layer.objects.active
bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM'); bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
for e in [x for x in bpy.context.scene.objects if x.type != 'MESH']: bpy.data.objects.remove(e)
me = o.data
co = np.array([v.co[:] for v in me.vertices]); lo, hi = co.min(0), co.max(0); dims = hi - lo
up = int(np.argmin(dims))                                  # the thin axis is the height
s = 0.119 / max(d for i, d in enumerate(dims) if i != up)   # longest footprint side = 11.9 cm
c = (lo + hi) / 2; c[up] = lo[up]
for v in me.vertices:
    p = (np.array(v.co[:]) - c) * s
    if up != 2: p[[up, 2]] = p[[2, up]]
    v.co = p
if up != 2:                                                # an axis swap mirrors the mesh; turn the faces back out
    bm = bmesh.new(); bm.from_mesh(me); bmesh.ops.reverse_faces(bm, faces=bm.faces); bm.to_mesh(me); bm.free()
me.update()
print('dims cm', [round(x * 100, 2) for x in o.dimensions])
ACACIA = wood('Acacia', (0.36, 0.21, 0.12), (0.62, 0.40, 0.26), 0.45, contrast=0.45)
me.materials.clear(); me.materials.append(ACACIA)
for uvl in list(me.uv_layers): me.uv_layers.remove(uvl)
uvl = me.uv_layers.new(name='UV').data
for p in me.polygons:                                       # same projection as wood_rest.py: grain on top, end grain on sides
    side = abs(p.normal.z) < 0.5
    for li in p.loop_indices:
        x, y, z = me.vertices[me.loops[li].vertex_index].co
        uvl[li].uv = ((x + y) / 0.30 + 0.5, z / 0.30 + 0.2) if side else (x / 0.30 + 0.5, y / 0.30 + 0.5)
P.append(o)
finish('wood_rest', 'Wooden Spatula Rest', view=(0.35, -1, 0.85))
print('DONE')
