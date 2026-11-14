# Layout check for the PharmVials sample room (a pharmacy's back dispensary) before any detailed building:
# the room, benches and machines as plain blocks, and the PharmVials products at true size so the scale reads.
# Follows the agreed floor plan (29 Oct 2026). Renders a view from the door and a plan from above.
#   blender -b -P blockout_pharmacy.py -- <room-pharmacy dir>
# Blender metres: x -2.8..2.8 (left..right), y -2.1..2.1 (front wall with door .. back wall), z 0..2.7.
import bpy, sys, os
from mathutils import Vector
OUT = sys.argv[sys.argv.index('--') + 1]
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
X0, X1, Y0, Y1, H = -2.8, 2.8, -2.1, 2.1, 2.7

def mat(name, c):
    m = bpy.data.materials.new(name); m.diffuse_color = (*c, 1); return m
M = {k: mat(k, c) for k, c in {
    'wall': (0.93, 0.93, 0.92), 'floor': (0.72, 0.73, 0.74), 'ceil': (0.96, 0.96, 0.96), 'bench': (0.85, 0.86, 0.87),
    'top': (0.97, 0.97, 0.97), 'steel': (0.62, 0.64, 0.66), 'dark': (0.15, 0.16, 0.17), 'glass': (0.78, 0.86, 0.9),
    'box': (0.80, 0.76, 0.68),
    # PharmVials products: tinted so they stand out in the grey room
    'amber': (0.78, 0.45, 0.12), 'cap': (0.95, 0.95, 0.95), 'blister': (0.55, 0.78, 0.82), 'kraft': (0.72, 0.56, 0.38),
    'jar': (0.96, 0.96, 0.94), 'label': (1.0, 1.0, 1.0)}.items()}

def box(name, c, d, m):
    bpy.ops.mesh.primitive_cube_add(size=1, location=c); o = bpy.context.active_object; o.name = name; o.scale = d
    o.data.materials.append(M[m]); return o
def cyl(name, c, r, h, m, v=24):
    bpy.ops.mesh.primitive_cylinder_add(vertices=v, radius=r, depth=h, location=(c[0], c[1], c[2] + h / 2))
    o = bpy.context.active_object; o.name = name; o.data.materials.append(M[m]); return o

# ---- shell: floor, ceiling, four walls; the front wall has the door (left) and the hatch to the front store (right)
box('Floor', (0, 0, -0.01), (X1 - X0, Y1 - Y0, 0.02), 'floor')
box('Ceiling', (0, 0, H + 0.01), (X1 - X0, Y1 - Y0, 0.02), 'ceil')
box('Back Wall', (0, Y1 + 0.05, H / 2), (X1 - X0, 0.1, H), 'wall')
box('Left Wall', (X0 - 0.05, 0, H / 2), (0.1, Y1 - Y0, H), 'wall')
box('Right Wall', (X1 + 0.05, 0, H / 2), (0.1, Y1 - Y0, H), 'wall')
DOOR = (-2.3, -1.2); HATCH = (0.4, 1.9)          # x ranges of the door and the hatch in the front wall
fy = Y0 - 0.05
box('Front Wall left', ((X0 + DOOR[0]) / 2, fy, H / 2), (DOOR[0] - X0, 0.1, H), 'wall')
box('Front Wall over door', (sum(DOOR) / 2, fy, 2.4), (DOOR[1] - DOOR[0], 0.1, 0.6), 'wall')
box('Front Wall mid', ((DOOR[1] + HATCH[0]) / 2, fy, H / 2), (HATCH[0] - DOOR[1], 0.1, H), 'wall')
box('Front Wall under hatch', (sum(HATCH) / 2, fy, 0.5), (HATCH[1] - HATCH[0], 0.1, 1.0), 'wall')
box('Front Wall over hatch', (sum(HATCH) / 2, fy, 2.3), (HATCH[1] - HATCH[0], 0.1, 0.8), 'wall')
box('Front Wall right', ((HATCH[1] + X1) / 2, fy, H / 2), (X1 - HATCH[1], 0.1, H), 'wall')

def bench(name, cx, cy, sx, sy_, h=0.9):
    box(name, (cx, cy, (h - 0.04) / 2), (sx, sy_, h - 0.04), 'bench')
    box(name + ' top', (cx, cy, h - 0.02), (sx + 0.02, sy_ + 0.02, 0.04), 'top')
    return h

# ---- back wall: a long dispensing counter (pharmacies keep bulk stock in a warehouse, not here), the everyday
#      equipment along it, left to right, and just one or two open boxes of vials to take from
h = bench('Back counter', 0, Y1 - 0.33, 5.2, 0.62)
by = Y1 - 0.38
box('Undercounter fridge door', (-2.1, Y1 - 0.64, 0.42), (0.6, 0.02, 0.74), 'glass')        # vaccines, insulin
box('Blister heat sealer', (-2.2, by, h + 0.11), (0.4, 0.45, 0.22), 'steel')                   # seals the filled cards
box('Sealer handle', (-2.2, by - 0.12, h + 0.3), (0.3, 0.04, 0.04), 'dark')
box('Tablet counter', (-1.35, by, h + 0.1), (0.25, 0.3, 0.2), 'cap')                          # electronic pill counter
box('Tablet counter funnel', (-1.35, by - 0.02, h + 0.24), (0.14, 0.14, 0.08), 'glass')
box('Weighing scale', (-0.75, by, h + 0.04), (0.3, 0.3, 0.08), 'steel')
box('Scale display', (-0.75, by + 0.17, h + 0.16), (0.2, 0.03, 0.12), 'dark')
box('Water dispenser', (-0.1, by + 0.05, h + 0.2), (0.25, 0.25, 0.4), 'cap')                  # reconstitutes antibiotic suspensions
cyl('Water bottle', (-0.1, by + 0.05, h + 0.4), 0.1, 0.35, 'glass')
cyl('Mortar', (0.45, by - 0.05, h), 0.07, 0.07, 'jar')
cyl('Graduated cylinder', (0.62, by + 0.05, h), 0.025, 0.25, 'glass')
cyl('Graduated cylinder', (0.72, by + 0.05, h), 0.02, 0.18, 'glass')
box('Pill crusher', (0.95, by, h + 0.07), (0.12, 0.12, 0.14), 'cap')
box('Sink', (1.55, by, h - 0.06), (0.6, 0.42, 0.14), 'steel')
cyl('Tap', (1.55, by + 0.24, h), 0.015, 0.3, 'steel')
box('Open vial box', (2.2, by, h + 0.12), (0.4, 0.3, 0.24), 'box')
for n in range(5):
    cyl('Vial', (2.08 + n * 0.06, by - 0.02, h + 0.24), 0.022, 0.03, 'amber')

# ---- left wall, back: blister-filling machine (about 1.0 m wide, 0.8 deep, 1.95 tall), glass front, card slot
mx, my = X0 + 0.42, 0.65
box('Blister machine', (mx, my, 0.975), (0.8, 1.0, 1.95), 'cap')
box('Blister machine glass', (mx + 0.41, my, 1.25), (0.02, 0.8, 0.9), 'glass')
box('Blister machine slot', (mx + 0.41, my, 0.55), (0.03, 0.4, 0.06), 'dark')
box('Card coming out', (mx + 0.5, my, 0.58), (0.2, 0.33, 0.012), 'blister')

# ---- left wall, front: blister bench, finished packs in three sizes and a rack
h = bench('Blister bench', X0 + 0.35, -0.9, 0.7, 1.1)
for k, (w, d) in enumerate([(0.23, 0.33), (0.19, 0.26), (0.14, 0.2)]):
    for n in range(6):
        box('Blister pack', (X0 + 0.3, -0.55 - k * 0.32, h + 0.006 + n * 0.012), (w, d * 0.9, 0.01), 'blister')
box('Blister rack', (X0 + 0.12, -1.25, h + 0.25), (0.2, 0.4, 0.5), 'steel')

# ---- centre: counting island with tray, splitter, rows of vials, a label printer and a roll of labels
h = bench('Counting island', 0, 0.1, 1.7, 1.2, 0.95)
box('Counting tray', (-0.35, 0.15, h + 0.015), (0.3, 0.2, 0.03), 'cap')
box('Spatula', (-0.15, 0.1, h + 0.005), (0.18, 0.02, 0.01), 'steel')
box('Pill splitter', (-0.6, -0.15, h + 0.02), (0.08, 0.05, 0.04), 'cap')
for r, (rad, ht) in enumerate([(0.022, 0.065), (0.028, 0.08), (0.035, 0.1)]):
    for n in range(6):
        c = cyl('Vial', (0.05 + n * 0.09, -0.05 - r * 0.12, h), rad, ht, 'amber')
        cyl('Vial cap', (0.05 + n * 0.09, -0.05 - r * 0.12, h + ht), rad + 0.003, 0.015, 'cap')
box('Label printer', (0.6, 0.4, h + 0.09), (0.22, 0.25, 0.18), 'dark')
cyl('Label roll', (0.3, 0.45, h), 0.06, 0.1, 'label').rotation_euler.x = 1.5708
box('Monitor', (-0.45, 0.62, h + 0.22), (0.5, 0.04, 0.32), 'dark')

# ---- right wall, back: compounding bench, ointment jars (some open), scale, mixing slab
h = bench('Compounding bench', X1 - 0.35, 0.65, 0.7, 1.1)
for n in range(8):
    x = X1 - 0.5 + (n % 2) * 0.12; y = 0.35 + (n // 2) * 0.1
    cyl('Ointment jar', (x, y, h), 0.035, 0.05, 'jar')
    if n % 3: cyl('Jar lid', (x, y, h + 0.05), 0.037, 0.015, 'cap')
box('Scale', (X1 - 0.3, 0.95, h + 0.04), (0.25, 0.25, 0.08), 'steel')
box('Mixing slab', (X1 - 0.25, 0.4, h + 0.01), (0.25, 0.25, 0.02), 'glass')

# ---- right wall, front: methadone station: pump with the stock bottle on top, trays of 2 and 3 oz bottles
h = bench('Methadone bench', X1 - 0.35, -0.9, 0.7, 1.1)
box('Methadone pump', (X1 - 0.25, -0.6, h + 0.15), (0.28, 0.3, 0.3), 'cap')
cyl('Stock bottle', (X1 - 0.25, -0.6, h + 0.3), 0.08, 0.32, 'amber')
for t, s in enumerate([0.045, 0.055]):                       # 2 oz and 3 oz square bottles
    box('Bottle tray', (X1 - 0.4, -0.95 - t * 0.3, h + 0.01), (0.32, 0.26, 0.02), 'steel')
    for n in range(12):
        x = X1 - 0.52 + (n % 4) * 0.08; y = -1.05 - t * 0.3 + (n // 4) * 0.08
        b = box('Methadone bottle', (x, y, h + 0.02 + s), (s, s, s * 2), 'amber')
        box('Bottle cap', (x, y, h + 0.02 + s * 3 + 0.01), (s * 0.7, s * 0.7, 0.02), 'cap')

# ---- front wall, right: packing counter under the hatch, paper bags with labelled orders, a till screen
h = bench('Packing counter', 1.25, Y0 + 0.3, 2.7, 0.6)
for n in range(7):
    w = 0.18 + 0.04 * (n % 2)
    box('Paper bag', (0.2 + n * 0.3, Y0 + 0.32, h + 0.16), (w, 0.11, 0.32), 'kraft')
    box('Bag label', (0.2 + n * 0.3, Y0 + 0.32 + 0.056, h + 0.2), (w * 0.7, 0.002, 0.07), 'label')

# ---- renders: workbench, the opening view (front wall, middle), a closer look, and a plan
scene.render.engine = 'BLENDER_WORKBENCH'; sh = scene.display.shading
sh.light = 'STUDIO'; sh.color_type = 'MATERIAL'; sh.show_shadows = True; sh.show_cavity = True
scene.world = bpy.data.worlds.new('w'); scene.world.color = (0.2, 0.2, 0.2)
cam_d = bpy.data.cameras.new('c'); cam = bpy.data.objects.new('c', cam_d); scene.collection.objects.link(cam); scene.camera = cam
cam_d.lens = 14; cam.location = (-0.4, Y0 + 0.15, 1.7)
cam.rotation_euler = (Vector((-0.4, 1.4, 0.8)) - cam.location).to_track_quat('-Z', 'Y').to_euler()
scene.render.resolution_x, scene.render.resolution_y = 1600, 900
scene.render.filepath = os.path.join(OUT, 'blockout_start.png'); bpy.ops.render.render(write_still=True)
# a closer look at the counting island and the blister corner
cam_d.lens = 24; cam.location = (0.9, -1.2, 1.55)
cam.rotation_euler = (Vector((-1.2, 0.5, 0.95)) - cam.location).to_track_quat('-Z', 'Y').to_euler()
scene.render.filepath = os.path.join(OUT, 'blockout_close.png'); bpy.ops.render.render(write_still=True)
for o in bpy.data.objects:
    if o.name.startswith('Ceiling'): o.hide_render = True
cam_d.type = 'ORTHO'; cam_d.ortho_scale = 6.2; cam.location = (0, 0, 9); cam.rotation_euler = (0, 0, 0)
scene.render.resolution_x, scene.render.resolution_y = 1240, 1000
scene.render.filepath = os.path.join(OUT, 'blockout_plan.png'); bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, 'blockout_pharmacy.blend'))
print('DONE')
