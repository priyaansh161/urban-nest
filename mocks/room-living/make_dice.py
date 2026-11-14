# White marble dice cube (listing 6f883f83), built in Blender: a 7.6 cm (three-inch) cube with softly rounded edges, real
# drilled pips (1 to 6, opposite faces adding to 7), white Carrara-style marble from the Marble019 scan with grey veins.
#   blender -b -P make_dice.py -- <out.glb> <Marble019 dir>
import bpy, math, os, sys
from mathutils import Vector
DST, TEX = sys.argv[sys.argv.index('--') + 1:]
bpy.ops.wm.read_factory_settings(use_empty=True)
A = 0.076; PR = 0.0078; PD = 0.011; OFF = A * 0.27
bpy.ops.mesh.primitive_cube_add(size=A, location=(0, 0, A / 2)); cube = bpy.context.object; cube.name = 'Marble Dice'
bv = cube.modifiers.new('b', 'BEVEL'); bv.width = 0.004; bv.segments = 5; bpy.ops.object.modifier_apply(modifier='b')
LAYOUT = {1: [(0, 0)], 2: [(-1, -1), (1, 1)], 3: [(-1, -1), (0, 0), (1, 1)], 4: [(-1, -1), (-1, 1), (1, -1), (1, 1)],
          5: [(-1, -1), (-1, 1), (0, 0), (1, -1), (1, 1)], 6: [(-1, -1), (-1, 0), (-1, 1), (1, -1), (1, 0), (1, 1)]}
FACES = {1: (Vector((0, 0, 1)), Vector((1, 0, 0))), 6: (Vector((0, 0, -1)), Vector((1, 0, 0))), 2: (Vector((0, -1, 0)), Vector((1, 0, 0))),
         5: (Vector((0, 1, 0)), Vector((1, 0, 0))), 3: (Vector((1, 0, 0)), Vector((0, 1, 0))), 4: (Vector((-1, 0, 0)), Vector((0, 1, 0)))}
cutters = []
for n, (nrm, u) in FACES.items():
    v = nrm.cross(u); centre = Vector((0, 0, A / 2)) + nrm * (A / 2)
    for (a, b) in LAYOUT[n]:
        p = centre + u * (a * OFF) + v * (b * OFF)
        bpy.ops.mesh.primitive_cylinder_add(radius=PR, depth=0.02, vertices=28, location=p + nrm * (0.01 - PD + PR * 0.4))     # a drilled hole...
        cy_ = bpy.context.object; cy_.rotation_euler = nrm.to_track_quat('Z', 'Y').to_euler(); cutters.append(cy_)
        bpy.ops.mesh.primitive_uv_sphere_add(radius=PR, segments=24, ring_count=12, location=p - nrm * (PD - PR * 0.6))   # ...with a rounded bottom
        cutters.append(bpy.context.object)
bpy.ops.object.select_all(action='DESELECT')
for c in cutters: c.select_set(True)
bpy.context.view_layer.objects.active = cutters[0]; bpy.ops.object.join(); cut = bpy.context.object
bpy.context.view_layer.objects.active = cube
md = cube.modifiers.new('pips', 'BOOLEAN'); md.object = cut; md.operation = 'DIFFERENCE'; md.solver = 'EXACT'; bpy.ops.object.modifier_apply(modifier='pips')
bpy.data.objects.remove(cut)
bpy.ops.object.shade_smooth_by_angle(angle=math.radians(40))
m = bpy.data.materials.new('White Marble'); m.use_nodes = True; nt = m.node_tree; b = nt.nodes['Principled BSDF']
def img(k, col=True):
    t = nt.nodes.new('ShaderNodeTexImage'); t.image = bpy.data.images.load(os.path.join(TEX, 'Marble019_2K-JPG_%s.jpg' % k))
    if not col: t.image.colorspace_settings.name = 'Non-Color'
    return t
c_ = img('Color'); r_ = img('Roughness', False); n_ = img('NormalGL', False)
mx = nt.nodes.new('ShaderNodeMix'); mx.data_type = 'RGBA'; mx.blend_type = 'MULTIPLY'; mx.inputs['Factor'].default_value = 1
nt.links.new(c_.outputs['Color'], mx.inputs['A']); mx.inputs['B'].default_value = (1.06, 1.06, 1.04, 1)
nt.links.new(mx.outputs['Result'], b.inputs['Base Color'])
rm = nt.nodes.new('ShaderNodeMath'); rm.operation = 'MULTIPLY'; rm.inputs[1].default_value = 0.6; nt.links.new(r_.outputs['Color'], rm.inputs[0]); nt.links.new(rm.outputs[0], b.inputs['Roughness'])
nm = nt.nodes.new('ShaderNodeNormalMap'); nm.inputs['Strength'].default_value = 0.3; nt.links.new(n_.outputs['Color'], nm.inputs['Color']); nt.links.new(nm.outputs['Normal'], b.inputs['Normal'])
cube.data.materials.clear(); cube.data.materials.append(m)
me = cube.data; me.uv_layers.new(name='UV')
bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.select_all(action='SELECT'); bpy.ops.uv.cube_project(cube_size=0.25); bpy.ops.object.mode_set(mode='OBJECT')
print('DICE', [round(d, 3) for d in cube.dimensions], len(me.polygons))
sc = bpy.context.scene; sc.render.engine = 'CYCLES'; sc.cycles.samples = 48; sc.view_settings.view_transform = 'AgX'
w = bpy.data.worlds.new('w'); sc.world = w; w.use_nodes = True; w.node_tree.nodes['Background'].inputs['Color'].default_value = (0.85, 0.85, 0.83, 1)
bpy.ops.mesh.primitive_plane_add(size=2); fl = bpy.context.object
ld = bpy.data.lights.new('k', 'AREA'); ld.energy = 5; ld.size = 0.4; lo = bpy.data.objects.new('k', ld); sc.collection.objects.link(lo); lo.location = (0.15, -0.2, 0.3); lo.rotation_euler = (Vector((0, 0, 0.03)) - lo.location).to_track_quat('-Z', 'Y').to_euler()
cd = bpy.data.cameras.new('c'); cd.lens = 70; cam = bpy.data.objects.new('c', cd); sc.collection.objects.link(cam); sc.camera = cam
cam.location = (0.16, -0.24, 0.18); cam.rotation_euler = (Vector((0, 0, 0.035)) - cam.location).to_track_quat('-Z', 'Y').to_euler()
sc.render.resolution_x, sc.render.resolution_y = 800, 700; sc.render.filepath = os.path.splitext(DST)[0] + '_look.png'; bpy.ops.render.render(write_still=True)
bpy.data.objects.remove(fl); bpy.ops.object.select_all(action='DESELECT'); cube.select_set(True)
bpy.ops.export_scene.gltf(filepath=DST, export_format='GLB', use_selection=True, export_apply=True, export_image_format='JPEG', export_jpeg_quality=88)
print('DONE dice')
