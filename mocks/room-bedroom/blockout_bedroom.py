# Layout check for the bedroom before any detailed building: the room and the big pieces I will build (bed,
# fluted panel, window + curtains, dresser, walk-in opening) as plain blocks, and the real product models from
# placements.json at true size. Renders a front view (like the reference) and a plan from above.
#   blender -b -P blockout_bedroom.py -- <room-bedroom dir>
# Blender metres: x -2.1..2.1 (left..right), y -1.9..1.9 (front open .. back wall), z 0..2.8.
import bpy, sys, os, math, json
from mathutils import Vector
OUT = sys.argv[sys.argv.index('--') + 1]
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
X0, X1, Y0, Y1, H = -2.1, 2.1, -1.9, 1.9, 2.8

def mat(name, c):
    m = bpy.data.materials.new(name); m.diffuse_color = (*c, 1); return m
M = {k: mat(k, c) for k, c in {
    'wall': (0.82, 0.74, 0.64), 'floor': (0.62, 0.44, 0.27), 'ceil': (0.92, 0.9, 0.86), 'slat': (0.70, 0.56, 0.42),
    'boucle': (0.90, 0.86, 0.79), 'linen': (0.95, 0.94, 0.91), 'teal': (0.10, 0.33, 0.35), 'walnut': (0.33, 0.20, 0.12),
    'glass': (0.75, 0.86, 0.9), 'sheer': (0.93, 0.91, 0.86), 'dark': (0.12, 0.11, 0.1), 'terra': (0.62, 0.32, 0.22)}.items()}

def box(name, c, d, m):
    bpy.ops.mesh.primitive_cube_add(size=1, location=c); o = bpy.context.active_object; o.name = name; o.scale = d
    o.data.materials.append(M[m]); return o

# shell: floor, ceiling, back / left / right walls (front open, as in the viewer)
box('Floor', (0, 0, -0.01), (X1 - X0, Y1 - Y0, 0.02), 'floor')
box('Ceiling', (0, 0, H + 0.01), (X1 - X0, Y1 - Y0, 0.02), 'ceil')
box('Back Wall', (0, Y1 + 0.05, H / 2), (X1 - X0, 0.1, H), 'wall')
box('Left Wall', (X0 - 0.05, 0, H / 2), (0.1, Y1 - Y0, H), 'wall')
# right wall with the walk-in opening near the back (y 0.95..1.85)
box('Right Wall front', (X1 + 0.05, (Y0 + 0.95) / 2, H / 2), (0.1, 0.95 - Y0, H), 'wall')
box('Right Wall over door', (X1 + 0.05, 1.4, 2.4), (0.1, 0.9, 0.8), 'wall')
box('Walk-in (dark beyond)', (X1 + 0.6, 1.4, 1.0), (1.0, 0.9, 2.0), 'dark')
# cove: a 15 cm drop round the edge of the ceiling
for n, c, d in [('Cove L', (X0 + 0.25, 0, H - 0.08), (0.5, Y1 - Y0, 0.16)), ('Cove R', (X1 - 0.25, 0, H - 0.08), (0.5, Y1 - Y0, 0.16)),
                ('Cove B', (0, Y1 - 0.25, H - 0.08), (X1 - X0, 0.5, 0.16))]:
    box(n, c, d, 'ceil')
# fluted slat panel behind the bed, floor to 2.5 m, 2.6 m wide
box('Fluted Panel', (0, Y1 - 0.03, 1.25), (2.6, 0.04, 2.5), 'slat')
# bed: queen mattress 1.6 x 2.0 on a bouclé frame, upholstered headboard
box('Bed Frame', (0, Y1 - 0.06 - 1.1, 0.2), (1.78, 2.15, 0.28), 'boucle')
box('Headboard', (0, Y1 - 0.12, 0.85), (1.78, 0.12, 1.1), 'boucle')
box('Mattress + duvet', (0, Y1 - 0.18 - 1.0, 0.47), (1.65, 1.95, 0.26), 'linen')
box('Teal throw', (0, Y1 - 0.18 - 1.45, 0.61), (1.75, 0.9, 0.03), 'teal')
for i, (x, m) in enumerate([(-0.45, 'linen'), (0.45, 'linen'), (-0.25, 'terra'), (0.25, 'teal'), (0, 'boucle')]):
    box('Pillow %d' % i, (x, Y1 - 0.32 - 0.06 * (i >= 2), 0.72 - 0.04 * (i >= 2)), (0.6 if i < 2 else 0.42, 0.14, 0.32 if i < 2 else 0.3), m)
# window on the left wall (front half), sheer curtains either side
box('Window', (X0 + 0.01, -0.55, 1.45), (0.03, 1.3, 1.7), 'glass')
for y in (-1.35, 0.25):
    box('Curtain', (X0 + 0.1, y, 1.35), (0.06, 0.4, 2.6), 'sheer')
# dresser on the right wall, front of the walk-in opening
box('Dresser', (X1 - 0.25, 0.25, 0.4), (0.5, 1.5, 0.8), 'walnut')

# ---- products, placed exactly as the viewer places them (three.js x, y, z -> Blender x, -z, y)
def bounds(objs):
    mn = Vector((1e9,) * 3); mx = Vector((-1e9,) * 3)
    for o in objs:
        if o.type != 'MESH': continue
        for c in o.bound_box:
            w = o.matrix_world @ Vector(c)
            for i in range(3): mn[i] = min(mn[i], w[i]); mx[i] = max(mx[i], w[i])
    return mn, mx
def place(d):
    path = os.path.join(OUT, 'products', d['file'])
    if not os.path.exists(path): print('MISSING', d['file']); return
    before = set(bpy.data.objects); bpy.ops.import_scene.gltf(filepath=path)
    new = [o for o in bpy.data.objects if o not in before]
    root = bpy.data.objects.new('Place ' + d['name'], None); scene.collection.objects.link(root)
    inner = bpy.data.objects.new('inner', None); scene.collection.objects.link(inner); inner.parent = root
    for o in new:
        if o.parent is None: o.parent = inner
    bpy.context.view_layer.update(); mn, mx = bounds(new); sz = mx - mn
    s = d['length'] / max(sz.x, sz.y) if 'length' in d else d['height'] / sz.z
    inner.scale = (s, s, s); bpy.context.view_layer.update(); mn, mx = bounds(new); c = (mn + mx) / 2
    inner.location -= Vector((c.x, c.y, mn.z))
    x, y, z = d['pos']; root.location = (x, -z, y); root.rotation_euler.z = d.get('rotY', 0)
    if 'alignBack' in d:
        bpy.context.view_layer.update(); mn, mx = bounds(new); root.location.y += -d['alignBack'] - mx.y
    bpy.context.view_layer.update(); mn, mx = bounds(new)
    print('PLACED', d['name'], 'size cm', [round((mx[i] - mn[i]) * 100) for i in range(3)])
pl = json.load(open(os.path.join(OUT, 'placements.json')))
for d in pl['products'] + pl['staging']: place(d)

# ---- renders: workbench, front (as the reference) and plan
scene.render.engine = 'BLENDER_WORKBENCH'; sh = scene.display.shading
sh.light = 'STUDIO'; sh.color_type = 'TEXTURE'; sh.show_shadows = True; sh.show_cavity = True
scene.world = bpy.data.worlds.new('w'); scene.world.color = (0.2, 0.2, 0.2)
cam_d = bpy.data.cameras.new('c'); cam = bpy.data.objects.new('c', cam_d); scene.collection.objects.link(cam); scene.camera = cam
cam_d.lens = 16; cam.location = (0, Y0 - 0.2, 1.4)
cam.rotation_euler = (Vector((0, Y1, 1.15)) - cam.location).to_track_quat('-Z', 'Y').to_euler()
scene.render.resolution_x, scene.render.resolution_y = 1600, 900
scene.render.filepath = os.path.join(OUT, 'blockout_front.png'); bpy.ops.render.render(write_still=True)
for o in bpy.data.objects:
    if o.name.startswith(('Ceiling', 'Cove')): o.hide_render = True
cam_d.type = 'ORTHO'; cam_d.ortho_scale = 4.8; cam.location = (0, 0, 9); cam.rotation_euler = (0, 0, 0)
scene.render.resolution_x = scene.render.resolution_y = 1000
scene.render.filepath = os.path.join(OUT, 'blockout_plan.png'); bpy.ops.render.render(write_still=True)
print('DONE')
