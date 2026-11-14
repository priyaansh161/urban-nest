# ETIQUETTE ART fluted nightstand (listing 8e9ff004), rebuilt clean in Blender from its listing photos (source/nightstand/):
# 36 W x 30 D x 56 H cm; matte black wood; a fluted drawer (10 cm) with a brass knob, an open shelf (11 cm) above it, sides
# that curve back from full depth to an 18 cm deep top shelf with a low gallery rim, four splayed tapered legs.
# The Meshy model had a lumpy, smeared skin (and marks where its plant and cup stood), so this replaces it.
# Real metres; base at z = 0, front toward -y (glTF +z).   blender -b -P make_nightstand.py -- <out.glb> <walnut scan dir>
import bpy, bmesh, math, os, sys
from mathutils import Vector
a = sys.argv[sys.argv.index('--') + 1:]; DST, TEX = a
bpy.ops.wm.read_factory_settings(use_empty=True)
W, D, H = 0.36, 0.30, 0.56
LEGH = 0.31; T = 0.016                       # leg height to the carcass, board thickness
ZB = LEGH                                    # carcass bottom
ZD = ZB + 0.105                              # drawer top / open-shelf board
ZS = ZD + 0.11 + T                           # top shelf board
DT = 0.18                                    # top shelf depth

def wood(name, tint, rough):
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree; b = nt.nodes['Principled BSDF']
    tc = nt.nodes.new('ShaderNodeTexImage'); tc.image = bpy.data.images.load(os.path.join(TEX, 'walnut_veneer_Diffuse_2k.jpg'))
    bw = nt.nodes.new('ShaderNodeRGBToBW'); nt.links.new(tc.outputs['Color'], bw.inputs['Color'])
    mx = nt.nodes.new('ShaderNodeMix'); mx.data_type = 'RGBA'; mx.blend_type = 'MULTIPLY'; mx.inputs['Factor'].default_value = 1
    nt.links.new(bw.outputs['Val'], mx.inputs['A']); mx.inputs['B'].default_value = tint
    nt.links.new(mx.outputs['Result'], b.inputs['Base Color']); b.inputs['Roughness'].default_value = rough
    tn = nt.nodes.new('ShaderNodeTexImage'); tn.image = bpy.data.images.load(os.path.join(TEX, 'walnut_veneer_nor_gl_2k.jpg')); tn.image.colorspace_settings.name = 'Non-Color'
    nm = nt.nodes.new('ShaderNodeNormalMap'); nm.inputs['Strength'].default_value = 0.4; nt.links.new(tn.outputs['Color'], nm.inputs['Color']); nt.links.new(nm.outputs['Normal'], b.inputs['Normal'])
    return m
BLACK = wood('Matte Black Wood', (0.032, 0.031, 0.030, 1), 0.5)
BRASS = bpy.data.materials.new('Brass Knob'); BRASS.use_nodes = True; bb = BRASS.node_tree.nodes['Principled BSDF']
bb.inputs['Base Color'].default_value = (0.78, 0.55, 0.24, 1); bb.inputs['Metallic'].default_value = 1.0; bb.inputs['Roughness'].default_value = 0.3

parts = []
def box(c, d, bev=0.0015):
    bpy.ops.mesh.primitive_cube_add(size=1, location=c); o = bpy.context.object; o.scale = d
    bpy.ops.object.transform_apply(scale=True)
    if bev: md = o.modifiers.new('b', 'BEVEL'); md.width = bev; md.segments = 2; bpy.ops.object.modifier_apply(modifier='b')
    o.data.materials.append(BLACK); parts.append(o); return o

# side panels: full depth up to the open shelf, then a quarter-round back to the top shelf's depth
def side(x):
    prof = [(-D / 2, ZB), (D / 2, ZB), (D / 2, H), (D / 2 - DT, H)]
    r = D - DT; cy = -D / 2 + r; cz = ZD + 0.02
    prof = [(-D / 2, ZB), (D / 2, ZB), (D / 2, H), (D / 2 - DT, H)]
    rz = (H - (ZD + 0.03))                                # the curve runs from the top shelf's front edge down to just above the drawer
    for k in range(1, 15):
        t = math.pi / 2 * k / 14
        prof.append((-D / 2 + (D - DT) * math.cos(t), H - rz * math.sin(t)))   # concave: the cut sweeps down to the drawer, as in the photos
    prof.append((-D / 2, ZD + 0.03))
    bm = bmesh.new(); vs = []
    for (y, z) in prof: vs.append(bm.verts.new((x - T / 2, y, z)))
    f = bm.faces.new(vs); bmesh.ops.recalc_face_normals(bm, faces=[f])
    ext = bmesh.ops.extrude_face_region(bm, geom=[f]); nv = [e for e in ext['geom'] if isinstance(e, bmesh.types.BMVert)]
    bmesh.ops.translate(bm, verts=nv, vec=(T, 0, 0)); bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new('Side'); bm.to_mesh(me); bm.free(); o = bpy.data.objects.new('Side', me); bpy.context.scene.collection.objects.link(o)
    me.materials.append(BLACK); parts.append(o)
for s in (-1, 1): side(s * (W / 2 - T / 2))
iw = W - 2 * T
box((0, 0, ZB + T / 2), (iw, D, T))                                   # bottom
box((0, 0, ZD + T / 2), (iw, D - 0.004, T))                           # open shelf (on the drawer box)
box((0, D / 2 - DT / 2, ZS - T / 2 + 0.0), (iw, DT, T))              # top shelf
box((0, D / 2 - T / 2, (ZB + H) / 2), (iw, T, H - ZB))               # back
box((0, D / 2 - DT + T / 2, ZS + 0.015), (iw, T * 0.9, 0.03))        # gallery lip along the top shelf's front
# drawer: front panel with vertical flutes and a brass knob
fz0, fz1 = ZB + 0.004, ZD - 0.002; fy = -D / 2 - 0.002
box((0, fy + 0.008, (fz0 + fz1) / 2), (iw - 0.004, 0.016, fz1 - fz0), 0.002)
n = 22; pitch = (iw - 0.02) / n
for k in range(n):
    bpy.ops.mesh.primitive_cylinder_add(radius=pitch * 0.48, depth=fz1 - fz0 - 0.012, vertices=12, location=(-iw / 2 + 0.01 + pitch * (k + 0.5), fy - 0.0005, (fz0 + fz1) / 2))
    o = bpy.context.object; o.scale.y = 0.45; bpy.ops.object.transform_apply(scale=True); o.data.materials.append(BLACK); bpy.ops.object.shade_smooth(); parts.append(o)
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.011, segments=20, ring_count=12, location=(0, fy - 0.017, (fz0 + fz1) / 2)); k_ = bpy.context.object; k_.data.materials.append(BRASS); bpy.ops.object.shade_smooth(); parts.append(k_)
bpy.ops.mesh.primitive_cylinder_add(radius=0.004, depth=0.012, vertices=10, location=(0, fy - 0.008, (fz0 + fz1) / 2), rotation=(math.pi / 2, 0, 0)); s_ = bpy.context.object; s_.data.materials.append(BRASS); parts.append(s_)
# legs: tapered, splayed outward ~10 degrees
for sx in (-1, 1):
    for sy in (-1, 1):
        top = Vector((sx * (W / 2 - 0.045), sy * (D / 2 - 0.045), ZB)); dirv = Vector((sx * math.sin(math.radians(7)), sy * math.sin(math.radians(5)), -1)).normalized()
        L = LEGH / abs(dirv.z); mid = top + dirv * (L / 2)
        bpy.ops.mesh.primitive_cone_add(vertices=20, radius1=0.011, radius2=0.017, depth=L, location=mid)
        o = bpy.context.object; o.rotation_euler = (-dirv).to_track_quat('Z', 'Y').to_euler(); o.data.materials.append(BLACK); bpy.ops.object.shade_smooth(); parts.append(o)

bpy.ops.object.select_all(action='DESELECT')
for o in parts: o.select_set(True)
bpy.context.view_layer.objects.active = parts[0]; bpy.ops.object.join(); ns = bpy.context.object; ns.name = 'ETIQUETTE ART Fluted Nightstand'
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
me = ns.data; me.uv_layers.new(name='UV')
bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.select_all(action='SELECT'); bpy.ops.uv.cube_project(cube_size=0.6); bpy.ops.object.mode_set(mode='OBJECT')
print('NIGHTSTAND', [round(d, 3) for d in ns.dimensions])
# a quick look
sc = bpy.context.scene; sc.render.engine = 'CYCLES'; sc.cycles.samples = 32; sc.view_settings.view_transform = 'AgX'
w = bpy.data.worlds.new('w'); sc.world = w; w.use_nodes = True; w.node_tree.nodes['Background'].inputs['Color'].default_value = (0.9, 0.9, 0.88, 1)
bpy.ops.mesh.primitive_plane_add(size=4, location=(0, 0, 0)); fl = bpy.context.object
ld = bpy.data.lights.new('k', 'AREA'); ld.energy = 120; ld.size = 1.2; lo = bpy.data.objects.new('k', ld); sc.collection.objects.link(lo); lo.location = (0.6, -0.9, 1.3); lo.rotation_euler = (Vector((0, 0, 0.3)) - lo.location).to_track_quat('-Z', 'Y').to_euler()
cd = bpy.data.cameras.new('c'); cd.lens = 50; cam = bpy.data.objects.new('c', cd); sc.collection.objects.link(cam); sc.camera = cam
cam.location = (0.55, -1.1, 0.75); cam.rotation_euler = (Vector((0, 0, 0.3)) - cam.location).to_track_quat('-Z', 'Y').to_euler()
sc.render.resolution_x, sc.render.resolution_y = 800, 900; sc.render.filepath = os.path.splitext(DST)[0] + '_look.png'; bpy.ops.render.render(write_still=True)
bpy.data.objects.remove(fl)
bpy.ops.object.select_all(action='DESELECT'); ns.select_set(True)
bpy.ops.export_scene.gltf(filepath=DST, export_format='GLB', use_selection=True, export_apply=True, export_image_format='JPEG', export_jpeg_quality=88)
print('DONE nightstand')
