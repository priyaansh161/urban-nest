# Finds objects passing through each other ("defying reality"): BVH overlap between every pair of product meshes.
#   blender -b pharmacy.blend -P check_overlaps.py
# Set pieces (counter, walls, baked shells) are skipped: things are meant to rest on them.
import bpy, re
from mathutils.bvhtree import BVHTree

SKIP = re.compile(r'^(LM_|Shell_|Counter|Backsplash|Floor|Ceiling|Cabinet|Wall|Skirting|Door|Handle|LED|Light)')
def root(o):
    while o.parent: o = o.parent
    return o
def base(n): return re.sub(r'\.\d{3}$', '', n)

dg = bpy.context.evaluated_depsgraph_get()
meshes = [o for o in bpy.context.scene.objects if o.type == 'MESH' and not SKIP.match(o.name) and o.visible_get()]
trees, boxes = {}, {}
for o in meshes:
    ev = o.evaluated_get(dg); me = ev.to_mesh()
    vs = [o.matrix_world @ v.co for v in me.vertices]; ev.to_mesh_clear()
    if not vs: continue
    trees[o.name] = BVHTree.FromPolygons([tuple(v) for v in vs], [tuple(p.vertices) for p in o.evaluated_get(dg).to_mesh().polygons])
    o.evaluated_get(dg).to_mesh_clear()
    boxes[o.name] = ([min(v[i] for v in vs) for i in range(3)], [max(v[i] for v in vs) for i in range(3)])

names = list(boxes); seen = set()
for i, a in enumerate(names):
    for b in names[i + 1:]:
        A, B = boxes[a], boxes[b]
        if any(A[1][k] < B[0][k] or B[1][k] < A[0][k] for k in range(3)): continue
        oa, ob = bpy.data.objects[a], bpy.data.objects[b]
        if oa.parent == ob or ob.parent == oa: continue           # a part and the thing it is mounted on
        if trees[a].overlap(trees[b]):
            key = (base(root(oa).name), base(a), base(root(ob).name), base(b))
            if key in seen: continue
            seen.add(key)
            print('OVERLAP  %s / %s   <->   %s / %s' % key)
print('checked', len(names), 'meshes')
