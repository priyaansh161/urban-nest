# DailyObjects Surge Foldaway 3-in-1 charger, rebuilt in Blender (1 Nov 2026) from its listing photos
# (source/dock/): the Meshy model read as a blob. Matte black anodised aluminium; a 9 cm square base with a
# soft-touch pad for earbuds and the white "DailyObjects" mark on its front edge; a slanted arm with a round
# cut-out; a square head tilted back 15 degrees carrying the white MagSafe puck; the watch puck behind it.
#   blender -b -P make_dock.py -- <room-bedroom dir>      -> products/bed-charging-dock.glb (front = glTF +z)
import bpy, bmesh, math, os, sys
from mathutils import Vector, Matrix
OUT = os.path.abspath(sys.argv[sys.argv.index('--') + 1])
bpy.ops.wm.read_factory_settings(use_empty=True)


def mat(name, col, rough, metal=0.0):
    m = bpy.data.materials.new(name); m.use_nodes = True; b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = col + (1,); b.inputs['Roughness'].default_value = rough; b.inputs['Metallic'].default_value = metal
    return m


ALU = mat('Anodised Black', (0.02, 0.02, 0.022), 0.5, 0.3)
SOFT = mat('Soft Touch Black', (0.012, 0.012, 0.013), 0.75)
PAD = mat('MagSafe Pad', (0.86, 0.86, 0.85), 0.55)
GREY = mat('Logo Grey', (0.55, 0.55, 0.55), 0.5)
WHITE = mat('Logo White', (0.9, 0.9, 0.9), 0.5)


def rbox(name, dim, m, r, seg=6, loc=(0, 0, 0)):
    """Rounded box: corners rounded in plan (r), edges softly chamfered (1 mm)."""
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc); o = bpy.context.object; o.name = name; o.scale = dim
    bpy.ops.object.transform_apply(scale=True)
    bm = bmesh.new(); bm.from_mesh(o.data)
    vert_edges = [e for e in bm.edges if abs((e.verts[0].co - e.verts[1].co).normalized().z) > 0.99] if dim[2] < max(dim[0], dim[1]) else []
    if vert_edges: bmesh.ops.bevel(bm, geom=vert_edges, offset=r, segments=seg, affect='EDGES', profile=0.5)
    bm.to_mesh(o.data); bm.free()
    md = o.modifiers.new('B', 'BEVEL'); md.width = 0.001; md.segments = 2; md.limit_method = 'ANGLE'
    bpy.ops.object.modifier_apply(modifier='B')
    o.data.materials.append(m); return o


def cyl(name, r, h, m, loc=(0, 0, 0), rot=(0, 0, 0), seg=48):
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=h, vertices=seg, location=loc, rotation=rot); o = bpy.context.object; o.name = name
    md = o.modifiers.new('B', 'BEVEL'); md.width = min(0.0012, h / 3); md.segments = 2; bpy.ops.object.modifier_apply(modifier='B')
    o.data.materials.append(m); return o


def cut(o, cutter):
    md = o.modifiers.new('C', 'BOOLEAN'); md.object = cutter; md.operation = 'DIFFERENCE'; md.solver = 'EXACT'
    bpy.context.view_layer.objects.active = o; bpy.ops.object.modifier_apply(modifier='C'); bpy.data.objects.remove(cutter)


parts = []
# base: 90 x 90 x 15 mm, its pad a shallow soft-touch square on top
parts.append(rbox('Base', (0.09, 0.09, 0.015), ALU, 0.012, loc=(0, 0, 0.0075)))
parts.append(rbox('Earbud Pad', (0.066, 0.066, 0.0012), SOFT, 0.009, loc=(0, -0.006, 0.0153)))
parts.append(cyl('Pad Mark', 0.0025, 0.0004, GREY, loc=(0, -0.006, 0.0161), seg=16))
# the "DailyObjects" mark: a tiny white bar on the front edge (the wordmark at 2 mm tall reads as a light line)
parts.append(rbox('Front Mark', (0.022, 0.0006, 0.0025), WHITE, 0.0005, seg=2, loc=(-0.018, -0.0451, 0.0075)))

# arm: a 56 mm wide, 14 mm thick slab rising from the base's back, leaning forward 18 degrees, ring cut-out
arm = rbox('Arm', (0.056, 0.014, 0.115), ALU, 0.004, loc=(0, 0, 0.0575))
ring = cyl('Ring Cut', 0.017, 0.05, ALU, rot=(math.pi / 2, 0, 0), loc=(0, 0, 0.052))
cut(arm, ring)
arm.data.transform(Matrix.Rotation(math.radians(14), 4, 'X'))      # leans forward, over the base
arm.location = (0, 0.026, 0.013); parts.append(arm)
# head: 82 mm square, 12 mm thick, tilted back 15 degrees; white MagSafe puck (60 mm) proud of its face
top = Vector((0, 0.026, 0.013)) + Matrix.Rotation(math.radians(14), 3, 'X') @ Vector((0, 0, 0.104)) + Vector((0, -0.014, 0))   # the head sits on the arm's front
hd = rbox('Head', (0.082, 0.082, 0.012), ALU, 0.013, loc=(0, 0, 0))   # built flat (corners round in plan), then stood up
hd.data.transform(Matrix.Rotation(math.radians(90), 4, 'X'))
puck = cyl('MagSafe Puck', 0.030, 0.004, PAD, rot=(math.pi / 2, 0, 0), loc=(0, -0.0075, 0))
logo = cyl('Puck Mark', 0.004, 0.0004, GREY, rot=(math.pi / 2, 0, 0), loc=(0, -0.0097, 0.004), seg=16)
watch = cyl('Watch Puck', 0.019, 0.012, SOFT, rot=(math.pi / 2, 0, 0), loc=(0.012, 0.012, -0.012))
watch_face = cyl('Watch Face', 0.014, 0.0006, ALU, rot=(math.pi / 2, 0, 0), loc=(0.012, 0.0183, -0.012))
for o in (hd, puck, logo, watch, watch_face):
    o.data.transform(Matrix.Rotation(math.radians(-15), 4, 'X')); o.location = top; parts.append(o)

for o in parts:                         # flat facets on the boxes (their bevels carry the light), smooth round parts
    rnd = any(k in o.name for k in ('Puck', 'Mark', 'Face'))
    for p in o.data.polygons: p.use_smooth = rnd
bpy.ops.object.select_all(action='DESELECT')
for o in parts: o.select_set(True)
bpy.context.view_layer.objects.active = parts[0]; bpy.ops.object.join()
dock = bpy.context.object; dock.name = 'Surge Foldaway 3-in-1'
bpy.ops.object.transform_apply(location=True)
z = [ (dock.matrix_world @ v.co).z for v in dock.data.vertices]
print('DOCK height', round(max(z) - min(z), 4), 'tris', sum(len(p.vertices) - 2 for p in dock.data.polygons))

# preview render next to the photo's angle
sc = bpy.context.scene; sc.render.engine = 'BLENDER_EEVEE'; sc.render.resolution_x = sc.render.resolution_y = 700
w = bpy.data.worlds.new('W'); sc.world = w; w.use_nodes = True; w.node_tree.nodes['Background'].inputs['Color'].default_value = (0.9, 0.9, 0.9, 1)
for loc, e in (((0.4, -0.5, 0.6), 60), ((-0.5, -0.2, 0.4), 25)):
    l = bpy.data.lights.new('L', 'AREA'); l.energy = e; l.size = 0.5; lo = bpy.data.objects.new('L', l); lo.location = loc; sc.collection.objects.link(lo)
    lo.rotation_euler = (Vector((0, 0, 0.08)) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
cd = bpy.data.cameras.new('C'); cd.lens = 70; cam = bpy.data.objects.new('C', cd); sc.collection.objects.link(cam); sc.camera = cam
cam.location = (0.22, -0.36, 0.2); cam.rotation_euler = (Vector((0, 0, 0.075)) - cam.location).to_track_quat('-Z', 'Y').to_euler()
sc.render.filepath = os.path.join(OUT, 'source', 'dock', 'dock_build.png'); bpy.ops.render.render(write_still=True)
for o in list(sc.objects):
    if o.type != 'MESH': bpy.data.objects.remove(o)
bpy.ops.export_scene.gltf(filepath=os.path.join(OUT, 'products', 'bed-charging-dock.glb'), export_format='GLB', export_yup=True, export_apply=True)
print('DONE dock')
