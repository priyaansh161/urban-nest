# Soul & Scents Jasmine reed diffuser, 50 ml (Amazon B0FDQNCQ39, a Lavender + Jasmine set; 3 Nov 2026), built from
# its listing photos (source/diffuser/): a squat frosted-glass cylinder with softly rounded shoulders, a matte black
# screw collar, five black fibre reeds fanned flat, and the real olive-green label (cropped from photo 3).
# Real metres; base at z = 0, label facing -y (the room, glTF +z). Draco.
#   blender -b -P make_diffuser.py -- <room-pilot dir>        (or run inside an open Blender: OUT defaults to here)
import bpy, math, os, sys
from mathutils import Vector
OUT = sys.argv[sys.argv.index('--') + 1] if '--' in sys.argv else r'C:\Users\priya\OneDrive\Projects\urban-nest\mocks\room-pilot'
NAME = 'bath-reed-diffuser'
for o in list(bpy.data.objects): bpy.data.objects.remove(o)

R, HB = 0.030, 0.062                    # bottle radius and height (50 ml)
RC, HC = 0.0145, 0.019                  # collar

def mat(name, col, rough, metal=0.0, image=None):
    m = bpy.data.materials.new(name); m.use_nodes = True; b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (*col, 1); b.inputs['Roughness'].default_value = rough; b.inputs['Metallic'].default_value = metal
    if image:
        t = m.node_tree.nodes.new('ShaderNodeTexImage'); t.image = image; m.node_tree.links.new(t.outputs['Color'], b.inputs['Base Color'])
    return m

frost = mat('Frosted Glass', (0.66, 0.70, 0.66), 0.38)          # acid-etched glass: pale, faintly green, soft sheen
black = mat('Matte Black Cap', (0.018, 0.018, 0.02), 0.6)
reed_m = mat('Black Fibre Reed', (0.02, 0.02, 0.022), 0.75)
li = bpy.data.images.load(os.path.join(OUT, 'source', 'diffuser', 'label_jasmine.png')); li.pack()
label_m = mat('Jasmine Label', (1, 1, 1), 0.55, image=li)

def lathe(name, prof, m, seg=64):
    V, F = [], []
    n = len(prof)
    for s in range(seg):
        a = 2 * math.pi * s / seg
        for r, z in prof: V.append((r * math.cos(a), r * math.sin(a), z))
    for s in range(seg):
        for i in range(n - 1):
            p, q = s * n + i, ((s + 1) % seg) * n + i
            F.append((p, q, q + 1, p + 1))
    me = bpy.data.meshes.new(name); me.from_pydata(V, [], F); me.materials.append(m)
    for p in me.polygons: p.use_smooth = True
    o = bpy.data.objects.new(name, me); bpy.context.scene.collection.objects.link(o); return o

parts = []
# bottle: thick flat base, straight wall, a rounded shoulder into a short neck under the collar
prof = [(0.0, 0.0), (R - 0.004, 0.0), (R - 0.001, 0.0008), (R, 0.004)] + \
       [(R, HB - 0.008)] + [(R - 0.008 + 0.008 * math.cos(a), HB - 0.008 + 0.008 * math.sin(a)) for a in [math.pi / 2 * k / 6 for k in range(1, 7)]] + \
       [(0.0125, HB), (0.0125, HB + 0.004), (0.0, HB + 0.004)]
parts.append(lathe('Bottle', prof, frost))
cprof = [(0.0, HB + 0.002), (RC - 0.001, HB + 0.002), (RC, HB + 0.003), (RC, HB + HC - 0.002), (RC - 0.0015, HB + HC), (0.0065, HB + HC), (0.0065, HB + HC - 0.004), (0.0, HB + HC - 0.004)]   # the reed hole
parts.append(lathe('Collar', cprof, black, 48))
# the label: a 5:4 panel wrapped round the front, a hair proud of the glass
LW, LH, LZ = 0.044, 0.035, 0.0085
seg = 24; ang = LW / R; V, F, UV = [], [], []
for s in range(seg + 1):
    a = -math.pi / 2 - ang / 2 + ang * s / seg
    for z, v in ((LZ, 0.0), (LZ + LH, 1.0)):
        V.append(((R + 0.0004) * math.cos(a), (R + 0.0004) * math.sin(a), z)); UV.append((s / seg, v))
for s in range(seg): F.append((2 * s, 2 * s + 2, 2 * s + 3, 2 * s + 1))
me = bpy.data.meshes.new('Label'); me.from_pydata(V, [], F); uv = me.uv_layers.new(name='UVMap')
for p in me.polygons:
    for l, vi in zip(p.loop_indices, p.vertices): uv.data[l].uv = UV[vi]
    p.use_smooth = True
me.materials.append(label_m); lab = bpy.data.objects.new('Label', me); bpy.context.scene.collection.objects.link(lab); parts.append(lab)
# five reeds, fanned flat (side to side, as in the photos), 17 cm long: all five pass through the collar's one
# reed hole, crossing just inside it, the lower 4.5 cm down in the oil (3 Nov 2026: they used to fan out from the
# bottle's floor and came up through the cap's walls instead of its hole)
P = Vector((0.0, 0.0, HB + HC - 0.004))
for k, tilt in enumerate((-19, -9.5, 0, 9.5, 19)):
    t = math.radians(tilt); L = 0.17
    d = Vector((math.sin(t), 0.0, math.cos(t))).normalized()
    off = Vector((0.0018 * (k - 2) * 0.5, 0.0012 * ((k % 2) * 2 - 1), 0.0))          # side by side in the hole, not one point
    bpy.ops.mesh.primitive_cylinder_add(radius=0.0016, depth=L, vertices=8, location=P + off + d * (L / 2 - 0.045))
    rd = bpy.context.object; rd.rotation_euler = d.to_track_quat('Z', 'Y').to_euler(); rd.data.materials.append(reed_m)
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=False); parts.append(rd)

for o in parts:                         # every part gets the UV map before the join, or the label's can be lost
    if not o.data.uv_layers: o.data.uv_layers.new(name='UVMap')
bpy.ops.object.select_all(action='DESELECT')
for o in parts: o.select_set(True)
bpy.context.view_layer.objects.active = parts[0]; bpy.ops.object.join(); d = bpy.context.object; d.name = 'Soul and Scents Jasmine Reed Diffuser'
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
print('DIFFUSER', [round(x, 3) for x in d.dimensions], sum(len(p.vertices) - 2 for p in d.data.polygons), 'tris')
p = os.path.join(OUT, 'products', NAME + '.glb')
bpy.ops.object.select_all(action='DESELECT'); d.select_set(True)
bpy.ops.export_scene.gltf(filepath=p, export_format='GLB', use_selection=True, export_apply=True, export_image_format='JPEG', export_jpeg_quality=90,
                          export_draco_mesh_compression_enable=True, export_draco_mesh_compression_level=6)
print('EXPORTED', p, round(os.path.getsize(p) / 1e3), 'KB')
