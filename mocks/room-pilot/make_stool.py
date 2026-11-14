# CARTADEN mango-wood stool (Amazon B0DWN6C8KY, 3 Nov 2026), built from its listing photos (source/stool/):
# 29 x 29 cm, 30 cm tall; a top of seven slats running front to back with 6 mm gaps, a 4.5 cm apron round all four
# sides, 4 cm square legs, low H stretchers (one across the front, one across the back, a bar between them) and
# black rubber feet. Honey mango wood: the vanity's walnut scan, warmed to the photos' golden brown.
# Real metres; base at z = 0, front toward -y (glTF +z). Draco.
#   blender -b -P make_stool.py -- <room-pilot dir>        (or run inside an open Blender: OUT defaults to here)
import bpy, bmesh, math, os, sys
import numpy as np
OUT = sys.argv[sys.argv.index('--') + 1] if '--' in sys.argv else r'C:\Users\priya\OneDrive\Projects\urban-nest\mocks\room-pilot'
NAME = 'bath-cartaden-stool'
for o in list(bpy.data.objects): bpy.data.objects.remove(o)
for m in list(bpy.data.materials):
    if m.name.startswith('Mango') or m.name.startswith('Rubber'): bpy.data.materials.remove(m)

W, H = 0.29, 0.30                     # square top, overall height
LEG, TOP, APR = 0.044, 0.018, 0.045    # leg section, slat thickness, apron height
FOOT = 0.004                           # rubber pads under the legs
SL, GAP = 7, 0.006

# ---------------------------------------------------------------- materials
W_DIR = os.path.join(OUT, 'textures', 'walnut_veneer')
def ld(f, size, colour=True, tint=None):
    i = bpy.data.images.load(os.path.join(W_DIR, f), check_existing=False)
    if max(i.size) > size: i.scale(size, size)
    if tint:
        w, h = i.size
        px = np.array(i.pixels[:], np.float32).reshape(h, w, 4)
        # mango's darker streaks run with the grain (rows = along it): long soft bands, a few darker heartwood marks
        rng = np.random.default_rng(8)
        low = np.kron(rng.normal(0, 1, (6, 48)), np.ones((h // 6 + 1, w // 48 + 1)))[:h, :w]
        for _ in range(3): low = (np.roll(low, 9, 1) + low + np.roll(low, -9, 1)) / 3; low = (np.roll(low, 60, 0) + low + np.roll(low, -60, 0)) / 3
        streak = np.clip(1.0 - 0.28 * np.maximum(low, 0) - 0.05 * np.abs(low), 0.6, 1.05)
        px[..., :3] = np.clip(px[..., :3] * np.array(tint, np.float32) * streak[..., None], 0, 1); i.pixels.foreach_set(px.ravel())
    if not colour: i.colorspace_settings.name = 'Non-Color'
    i.pack(); return i
mango = bpy.data.materials.new('Mango Wood'); mango.use_nodes = True; nt = mango.node_tree; b = nt.nodes['Principled BSDF']
t = nt.nodes.new('ShaderNodeTexImage'); t.image = ld('walnut_veneer_Diffuse_2k.jpg', 1024, tint=(1.15, 0.95, 0.52)); nt.links.new(t.outputs['Color'], b.inputs['Base Color'])
t = nt.nodes.new('ShaderNodeTexImage'); t.image = ld('walnut_veneer_Rough_2k.jpg', 512, False)
mr = nt.nodes.new('ShaderNodeMath'); mr.operation = 'MULTIPLY_ADD'; mr.inputs[1].default_value = 0.8; mr.inputs[2].default_value = 0.0   # a satin lacquer: a little glossier than the raw scan
nt.links.new(t.outputs['Color'], mr.inputs[0]); nt.links.new(mr.outputs['Value'], b.inputs['Roughness'])
t = nt.nodes.new('ShaderNodeTexImage'); t.image = ld('walnut_veneer_nor_gl_2k.jpg', 1024, False)
n = nt.nodes.new('ShaderNodeNormalMap'); nt.links.new(t.outputs['Color'], n.inputs['Color']); nt.links.new(n.outputs['Normal'], b.inputs['Normal'])
rubber = bpy.data.materials.new('Rubber Feet'); rubber.use_nodes = True
rubber.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value = (0.02, 0.02, 0.02, 1); rubber.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value = 0.85

# ---------------------------------------------------------------- parts
def piece(loc, dim, m, grain, off, bevel=0.0018):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc); o = bpy.context.object; o.scale = dim
    bpy.ops.object.transform_apply(scale=True)
    md = o.modifiers.new('B', 'BEVEL'); md.width = bevel; md.segments = 2; bpy.ops.object.modifier_apply(modifier='B')
    me = o.data; uv = me.uv_layers[0]
    for p in me.polygons:                                  # wood grain along the piece's length, world scale
        ax = max(range(3), key=lambda a: abs(p.normal[a])); pl = [a for a in range(3) if a != ax]
        if grain in pl: pl = [a for a in pl if a != grain] + [grain]
        for li in p.loop_indices:
            co = me.vertices[me.loops[li].vertex_index].co + o.location
            uv.data[li].uv = (co[pl[0]] / 0.9 + off[0], co[pl[1]] / 0.9 + off[1])
    me.materials.append(m); return o

parts = []
h = W / 2 - LEG / 2
for k, (sx, sy) in enumerate(((-1, -1), (1, -1), (-1, 1), (1, 1))):
    parts.append(piece((sx * h, sy * h, FOOT + (H - TOP - FOOT) / 2), (LEG, LEG, H - TOP - FOOT), mango, 2, (k * 0.31, k * 0.17)))
    bpy.ops.mesh.primitive_cylinder_add(radius=0.016, depth=FOOT, vertices=24, location=(sx * h, sy * h, FOOT / 2))
    f = bpy.context.object; f.data.materials.append(rubber); parts.append(f)
za = H - TOP - APR / 2
for s in (-1, 1):                                          # aprons, set 4 mm in from the legs' faces
    parts.append(piece((0, s * (W / 2 - 0.004 - 0.009), za), (W - 2 * LEG, 0.018, APR), mango, 0, (0.4 + s * 0.2, 0.1)))
    parts.append(piece((s * (W / 2 - 0.004 - 0.009), 0, za), (0.018, W - 2 * LEG, APR), mango, 1, (0.2, 0.5 + s * 0.2)))
zs = 0.052                                                 # the H: front and back stretchers, a bar between them
for s in (-1, 1):
    parts.append(piece((0, s * (W / 2 - 0.004 - 0.011), zs), (W - 2 * LEG, 0.022, 0.030), mango, 0, (0.7 + s * 0.1, 0.3)))
parts.append(piece((0, 0, zs), (0.024, 2 * (W / 2 - 0.004 - 0.022) + 0.004, 0.026), mango, 1, (0.15, 0.8)))   # the bar runs right into both stretchers (it stopped 2 cm short of each)
sw = (W - (SL - 1) * GAP) / SL
for k in range(SL):                                        # seven slats, front to back
    x = -W / 2 + sw / 2 + k * (sw + GAP)
    parts.append(piece((x, 0, H - TOP / 2), (sw, W, TOP), mango, 1, (k * 0.23, k * 0.41), bevel=0.0025))

bpy.ops.object.select_all(action='DESELECT')
for o in parts: o.select_set(True)
bpy.context.view_layer.objects.active = parts[0]; bpy.ops.object.join(); st = bpy.context.object; st.name = 'CARTADEN Mango Wood Stool'
for p in st.data.polygons: p.use_smooth = False
print('STOOL', [round(d, 3) for d in st.dimensions], sum(len(p.vertices) - 2 for p in st.data.polygons), 'tris')
p = os.path.join(OUT, 'products', NAME + '.glb')
bpy.ops.object.select_all(action='DESELECT'); st.select_set(True)
bpy.ops.export_scene.gltf(filepath=p, export_format='GLB', use_selection=True, export_apply=True, export_image_format='JPEG', export_jpeg_quality=88,
                          export_draco_mesh_compression_enable=True, export_draco_mesh_compression_level=6)
print('EXPORTED', p, round(os.path.getsize(p) / 1e3), 'KB')
