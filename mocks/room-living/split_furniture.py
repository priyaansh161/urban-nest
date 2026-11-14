# Splits the baked furniture (with whatever stands on it) out of the room into pieces of their own, WITHOUT re-baking:
# the saved living_v1.blend already holds every lightmap, so each piece keeps its own baked light and the room file loses
# the furniture. The pieces become movable "staging" items in placements.json (admin Rooms can drag, turn and lift them).
#   blender -b living_v1.blend -P split_furniture.py -- <room-living dir>
import bpy, sys, os, json
from mathutils import Vector
OUT = os.path.abspath(sys.argv[sys.argv.index('--') + 1])
FURN = {'LM_Sofa': ('liv-sofa', 'Chesterfield Sofa'), 'LM_Loveseat': ('liv-loveseat', 'Chesterfield Loveseat'), 'LM_Armchair1': ('liv-armchair-1', 'Rattan Armchair'),
        'LM_Armchair2': ('liv-armchair-2', 'Rattan Armchair'), 'LM_Sideboard': ('liv-sideboard', 'Rosewood Sideboard'),
        'LM_SideTableA': ('liv-side-table-a', 'Rosewood Side Table'), 'LM_SideTableB': ('liv-side-table-b', 'Rosewood Side Table')}
DRESS = ('Cushion', 'Newspaper', 'Fold', 'Book', 'Candle', 'Flame', 'Sleeve', 'Disc')
def bb(o):
    cs = [o.matrix_world @ Vector(c) for c in o.bound_box]
    return Vector([min(c[i] for c in cs) for i in range(3)]), Vector([max(c[i] for c in cs) for i in range(3)])
FURN = {n: v for n, v in FURN.items() if n in bpy.data.objects}
objs = {n: bpy.data.objects[n] for n in FURN}
boxes = {n: bb(o) for n, o in objs.items()}
groups = {n: [o] for n, o in objs.items()}
for o in bpy.data.objects:
    if o.type != 'MESH' or not o.name.startswith(DRESS): continue
    mn, mx = bb(o); c = (mn + mx) / 2; best = None
    for n, (fmn, fmx) in boxes.items():
        if fmn.x - 0.12 <= c.x <= fmx.x + 0.12 and fmn.y - 0.12 <= c.y <= fmx.y + 0.12 and fmn.z - 0.05 <= c.z <= fmx.z + 0.8:
            area = (fmx.x - fmn.x) * (fmx.y - fmn.y)
            if best is None or area < best[0]: best = (area, n)
    if best: groups[best[1]].append(o)
info = []
for n, (fn, title) in FURN.items():
    objs_ = groups[n]; mins = [bb(o) for o in objs_]
    mn = Vector([min(m[0][i] for m in mins) for i in range(3)]); mx = Vector([max(m[1][i] for m in mins) for i in range(3)])
    bpy.ops.object.select_all(action='DESELECT')
    for o in objs_: o.select_set(True)
    bpy.context.view_layer.objects.active = objs_[0]
    bpy.ops.export_scene.gltf(filepath=os.path.join(OUT, 'products', fn + '_raw.glb'), export_format='GLB', use_selection=True, export_apply=True, export_cameras=False, export_lights=False, export_image_format='JPEG', export_jpeg_quality=85)
    info.append({'name': title, 'file': fn + '.glb', 'height': round(mx.z - mn.z, 4), 'pos': [round((mn.x + mx.x) / 2, 4), round(mn.z, 4), round(-(mn.y + mx.y) / 2, 4)], 'dressing': len(objs_) - 1})
    print('PIECE', fn, info[-1]['dressing'], 'extras', [round(v, 2) for v in mn], [round(v, 2) for v in mx])
for n in FURN:
    for o in groups[n]: bpy.data.objects.remove(o)
bpy.ops.export_scene.gltf(filepath=os.path.join(OUT, 'living_v1_nofurn.glb'), export_format='GLB', export_apply=True, export_cameras=False, export_lights=False, export_image_format='JPEG', export_jpeg_quality=85)
json.dump(info, open(os.path.join(OUT, 'split_info.json'), 'w'), indent=1)
print('DONE split')
