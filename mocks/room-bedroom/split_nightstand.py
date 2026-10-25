# The Fluted Nightstand's Meshy model came with decor standing on its top (a potted plant, back left, and a cup,
# right). The left nightstand already carries the clock and the charging dock, so it gets a bare copy; the plant
# moves to the dresser as staging (no dot). The right nightstand keeps the original, cup and plant included.
#   blender -b -P split_nightstand.py -- <room-bedroom dir>
# Writes products/bed-nightstand-bare.glb, products/bed-nightstand-plant.glb and split_check.png.
import bpy, bmesh, sys, os
import numpy as np
from mathutils import Vector

OUT = os.path.abspath(sys.argv[sys.argv.index('--') + 1])
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
bpy.ops.import_scene.gltf(filepath=os.path.join(OUT, 'products/bed-nightstand.glb'))
meshes = [o for o in bpy.data.objects if o.type == 'MESH']
bpy.ops.object.select_all(action='DESELECT')
for o in meshes: o.select_set(True)
bpy.context.view_layer.objects.active = meshes[0]
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
if len(meshes) > 1: bpy.ops.object.join()
ob = bpy.context.active_object
for o in [o for o in bpy.data.objects if o.type != 'MESH']: bpy.data.objects.remove(o)

bm = bmesh.new(); bm.from_mesh(ob.data); bm.faces.ensure_lookup_table()
co = np.array([v.co[:] for v in bm.verts]); mn, mx = co.min(0), co.max(0)
# the top board: the height with the most upward-facing area in the top third
ups = [(f.calc_center_median().z, f.calc_area()) for f in bm.faces if f.normal.z > 0.95 and f.calc_center_median().z > mn[2] + 0.6 * (mx[2] - mn[2])]
z, a = np.array(ups).T; bins = np.round(z, 2); top = max(set(bins), key=lambda b: a[bins == b].sum())
print('top board at', top, 'of', round(mn[2], 3), '..', round(mx[2], 3))
# decor: everything standing on the top board, inside its edges (the board's own lip runs round the edge)
cx = (mn[0] + mx[0]) / 2; M = 0.04
def decor(f):
    c = f.calc_center_median()
    return c.z > top + 0.002 and mn[0] + M < c.x < mx[0] - M and mn[1] + M < c.y < mx[1] - M
dec = [f for f in bm.faces if decor(f)]
left = [f for f in dec if f.calc_center_median().x < cx]
# the plant itself: whatever stands within the reach of its leaves round the pot's axis (not stray bits of board)
hi = np.array([f.calc_center_median()[:2] for f in left if f.calc_center_median().z > top + 0.08]); axis = hi.mean(0)
reach = np.linalg.norm(hi - axis, axis=1).max()
def in_plant(c):
    d = np.linalg.norm(np.array(c[:2]) - axis)          # near the board only the pot itself, higher up the leaves too
    return c.z > top + 0.01 and d < (reach if c.z > top + 0.10 else 0.55 * reach)
low_ok = lambda f: all(v.co.z > top + 0.10 or np.linalg.norm(np.array(v.co[:2]) - axis) < 0.55 * reach for v in f.verts)   # no long slivers out to the board
short = lambda f: max(e.calc_length() for e in f.edges) < 0.04          # nor stretched triangles bridging to it
plant = {f.index for f in left if in_plant(f.calc_center_median()) and low_ok(f) and short(f)}
print('decor faces', len(dec), 'plant', len(plant))
# a clean top-board face's UV (front corner, away from where the decor stood): the board's texture has the pot's
# and the cup's footprints painted in, so the whole open top is recoloured from it
uvl = bm.loops.layers.uv.active
board = min((f for f in bm.faces if f.normal.z > 0.95 and abs(f.calc_center_median().z - top) < 0.006),
            key=lambda f: (f.calc_center_median() - Vector((mx[0] - 0.08, mn[1] + 0.08, top))).length)
board_uv = board.loops[0][uvl].uv.copy()

def export(keep, name, fill=False):
    b2 = bm.copy(); b2.faces.ensure_lookup_table()
    gone = [f for f in b2.faces if not keep(f.index)]
    bmesh.ops.delete(b2, geom=gone, context='FACES')
    if fill:                        # close the holes the decor left in the top board, in the board's colour
        edges = [e for e in b2.edges if e.is_boundary and abs(e.verts[0].co.z - top) < 0.03]
        new = bmesh.ops.holes_fill(b2, edges=edges, sides=0)['faces']
        uv2 = b2.loops.layers.uv.active
        for f in new:
            for l in f.loops: l[uv2].uv = board_uv
        for v in b2.verts:          # the pot and the cup left low ridges in the board: press it flat
            if abs(v.co.z - top) < 0.012 and mn[0] + M < v.co.x < mx[0] - M and mn[1] + M < v.co.y < mx[1] - M: v.co.z = top
        b2.normal_update()
        for f in b2.faces:
            c = f.calc_center_median()
            if f.normal.z > 0.9 and abs(c.z - top) < 0.01 and mn[0] + M < c.x < mx[0] - M and mn[1] + M < c.y < mx[1] - M:
                for l in f.loops: l[uv2].uv = board_uv
        print(name, 'patched', len(new), 'faces')
    me = bpy.data.meshes.new(name); b2.to_mesh(me); b2.free()
    for m in ob.data.materials: me.materials.append(m)
    o2 = bpy.data.objects.new(name, me); scene.collection.objects.link(o2)
    bpy.ops.object.select_all(action='DESELECT'); o2.select_set(True); bpy.context.view_layer.objects.active = o2
    bpy.ops.export_scene.gltf(filepath=os.path.join(OUT, 'products', name + '.glb'), export_format='GLB', use_selection=True, export_image_format='WEBP')
    return o2
decor_ix = {f.index for f in dec}
bare = export(lambda i: i not in decor_ix, 'bed-nightstand-bare', fill=True)
pl = export(lambda i: i in plant, 'bed-nightstand-plant')
ob.hide_render = True; pl.location.x = (mx[0] - mn[0]) * 1.3

scene.render.engine = 'BLENDER_WORKBENCH'; scene.display.shading.light = 'STUDIO'; scene.display.shading.color_type = 'TEXTURE'
cd = bpy.data.cameras.new('c'); cd.type = 'ORTHO'; cd.ortho_scale = 3.4; c = bpy.data.objects.new('c', cd); scene.collection.objects.link(c); scene.camera = c
c.location = (2.6, -4, 2.2); c.rotation_euler = (Vector((0.7, 0, 0.1)) - c.location).to_track_quat('-Z', 'Y').to_euler()
scene.render.resolution_x, scene.render.resolution_y = 900, 600; scene.render.filepath = os.path.join(OUT, 'split_check.png'); bpy.ops.render.render(write_still=True)
print('DONE')
