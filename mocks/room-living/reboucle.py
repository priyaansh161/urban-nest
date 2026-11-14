# Meshy gave the Kaniel armchair the right shape but a smooth leather skin: re-skin it in its real camel bouclé.
#   blender -b -P reboucle.py -- <in.glb> <out.glb> <textures dir>
import bpy, sys, os, math
a = sys.argv[sys.argv.index('--') + 1:]; src, dst, tex = a
bpy.ops.wm.read_factory_settings(use_empty=True); bpy.ops.import_scene.gltf(filepath=src)
ms = [o for o in bpy.data.objects if o.type == 'MESH']
bpy.ops.object.select_all(action='DESELECT')
for o in ms: o.select_set(True)
bpy.context.view_layer.objects.active = ms[0]
if len(ms) > 1: bpy.ops.object.join()
o = bpy.context.active_object
bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
me = o.data
for uv in list(me.uv_layers): me.uv_layers.remove(uv)
me.uv_layers.new(name='UV')
bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.uv.smart_project(angle_limit=math.radians(60), island_margin=0.0, scale_to_bounds=False)
bpy.ops.object.mode_set(mode='OBJECT')
dims = max(o.dimensions); k = 9.0 * dims / 1.9                      # about 9 repeats across the chair (a ~10 cm bouclé tile)
for d in me.uv_layers['UV'].data: d.uv = (d.uv.x * k, d.uv.y * k)
m = bpy.data.materials.new('Camel Boucle'); m.use_nodes = True; nt = m.node_tree; b = nt.nodes['Principled BSDF']
def img(n, col=True):
    i = bpy.data.images.load(os.path.join(tex, 'curly_teddy_natural', 'curly_teddy_natural_%s_2k.jpg' % n))
    if not col: i.colorspace_settings.name = 'Non-Color'
    t = nt.nodes.new('ShaderNodeTexImage'); t.image = i; return t
dif = img('diff'); nor = img('nor_gl', False); rou = img('rough', False)
bw = nt.nodes.new('ShaderNodeRGBToBW'); nt.links.new(dif.outputs['Color'], bw.inputs['Color'])
mul = nt.nodes.new('ShaderNodeMix'); mul.data_type = 'RGBA'; mul.blend_type = 'MULTIPLY'; mul.inputs['Factor'].default_value = 1.0
nt.links.new(bw.outputs['Val'], mul.inputs['A']); mul.inputs['B'].default_value = (0.42, 0.21, 0.055, 1)
gain = nt.nodes.new('ShaderNodeMath'); gain.operation = 'MULTIPLY'; gain.inputs[1].default_value = 1.35
nt.links.new(bw.outputs['Val'], gain.inputs[0]); nt.links.new(gain.outputs[0], mul.inputs['A'])
nt.links.new(mul.outputs['Result'], b.inputs['Base Color'])
nm = nt.nodes.new('ShaderNodeNormalMap'); nm.inputs['Strength'].default_value = 1.2; nt.links.new(nor.outputs['Color'], nm.inputs['Color']); nt.links.new(nm.outputs['Normal'], b.inputs['Normal'])
nt.links.new(rou.outputs['Color'], b.inputs['Roughness'])
me.materials.clear(); me.materials.append(m)
wood = bpy.data.materials.new('Light Wood Feet'); wood.use_nodes = True; wb_ = wood.node_tree.nodes['Principled BSDF']
wb_.inputs['Base Color'].default_value = (0.30, 0.19, 0.10, 1); wb_.inputs['Roughness'].default_value = 0.5; me.materials.append(wood)
zmin = min(v.co.z for v in me.vertices); zmax = max(v.co.z for v in me.vertices)
for p in me.polygons:                                   # the four round feet: everything in the bottom 6 %
    if max(me.vertices[v].co.z for v in p.vertices) < zmin + 0.06 * (zmax - zmin): p.material_index = 1
# a quick Cycles look at the real colours
sc = bpy.context.scene; sc.render.engine = 'CYCLES'; sc.cycles.samples = 24; sc.view_settings.view_transform = 'AgX'
w = bpy.data.worlds.new('w'); sc.world = w; w.use_nodes = True; w.node_tree.nodes['Background'].inputs['Strength'].default_value = 1.0
ld = bpy.data.lights.new('k', 'AREA'); ld.energy = 600; ld.size = 3; lo = bpy.data.objects.new('k', ld); sc.collection.objects.link(lo); lo.location = (2, -4, 4); lo.rotation_euler = (math.radians(50), 0, math.radians(25))
cd = bpy.data.cameras.new('c'); cam = bpy.data.objects.new('c', cd); sc.collection.objects.link(cam); sc.camera = cam
from mathutils import Vector
c = Vector(o.location); cam.location = (dims * 0.9, -dims * 2.2, dims * 0.9); cam.rotation_euler = (Vector((0, 0, dims * 0.3)) - cam.location).to_track_quat('-Z', 'Y').to_euler()
sc.render.resolution_x, sc.render.resolution_y = 900, 800; sc.render.filepath = os.path.join(os.path.dirname(dst), 'renders', 'kaniel_cycles.png'); bpy.ops.render.render(write_still=True)
bpy.ops.export_scene.gltf(filepath=dst, export_format='GLB', export_apply=True, export_image_format='JPEG', export_jpeg_quality=88)
print('DONE reboucle')
