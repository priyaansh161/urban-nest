# Patch the baked room without a re-bake (31 Oct 2026): drop the gloves box, move the thermal-label dot onto the
# label roll, and delete the machine faces that lie flat inside a bigger face (they z-fought: black flickering stripes).
import bpy, bmesh, json, os, collections
from mathutils import Vector
HERE = os.path.dirname(bpy.data.filepath)
kill = {x for o in bpy.data.objects if o.name.startswith("Gloves box") for x in [o] + list(o.children_recursive)}
for o in kill: bpy.data.objects.remove(o)
if 0:
    for c in o.children_recursive: bpy.data.objects.remove(c)
    bpy.data.objects.remove(o)

m = bpy.data.objects['LM_Machine']; bm = bmesh.new(); bm.from_mesh(m.data); bm.faces.ensure_lookup_table()
planes = collections.defaultdict(list)
for f in bm.faces:
    n = f.normal; ax = max(range(3), key=lambda i: abs(n[i]))
    if abs(n[ax]) < 0.999: continue
    planes[(ax, n[ax] > 0, round(f.calc_center_median()[ax], 4))].append(f)
gone = set()
for (ax, _, _), fs in planes.items():
    if len(fs) < 2: continue
    o1, o2 = [i for i in range(3) if i != ax]
    fs.sort(key=lambda f: -f.calc_area())
    for big in fs:
        if big in gone: continue
        lo = [min(v.co[i] for v in big.verts) for i in (o1, o2)]; hi = [max(v.co[i] for v in big.verts) for i in (o1, o2)]
        for f in fs:
            if f is big or f in gone or f.calc_area() > big.calc_area(): continue
            if all(lo[k] - 1e-4 <= v.co[i] <= hi[k] + 1e-4 for v in f.verts for k, i in enumerate((o1, o2))): gone.add(f)
print('hidden coplanar faces removed', len(gone))
bmesh.ops.delete(bm, geom=list(gone), context='FACES'); bm.to_mesh(m.data); bm.free()

P = json.load(open(os.path.join(HERE, 'placements.json')))
P['products'] = [p for p in P['products'] if 'Gloves' not in p['name']]
roll = bpy.data.objects['Label roll']; bpy.context.view_layer.update()
pts = [roll.matrix_world @ Vector(c) for o in [roll] + list(roll.children_recursive) if o.type == 'MESH' for c in o.bound_box]
c = sum(pts, Vector()) / len(pts); top = max(p.z for p in pts)
for p in P['products']:
    if p['name'].startswith('Paxxol 4.625'): p['dotAt'] = [round(c.x, 3), round(top + 0.03, 3), round(-c.y, 3)]
json.dump(P, open(os.path.join(HERE, 'placements.json'), 'w'), indent=1)
bpy.ops.export_scene.gltf(filepath=os.path.join(HERE, 'pharmacy.glb'), export_format='GLB', export_cameras=False,
                          export_lights=False, export_apply=True, export_yup=True, export_image_format='JPEG', export_jpeg_quality=88)
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
print('PATCHED', len(P['products']), 'products')
