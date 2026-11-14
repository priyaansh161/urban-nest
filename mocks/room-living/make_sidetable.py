# InoSlashed rattan-webbing end table (listing 5e586bdd), rebuilt clean in Blender from its listing photos (source/sidetable/):
# 30.5 x 30.5 x 43.2 cm, walnut laminated MDF; a square top with rounded corners and an edge band, four flat board legs set
# into the corners, a low shelf frame with the same rounded corners and a cane (rattan webbing) panel. The Meshy model had a
# lumpy glossy skin and the photo's styling (plants, candles, books) baked into it, so this replaces it.
#   blender -b -P make_sidetable.py -- <out.glb> <walnut scan dir>
import bpy, bmesh, math, os, sys
import numpy as np
from mathutils import Vector
DST, TEX = sys.argv[sys.argv.index('--') + 1:]
bpy.ops.wm.read_factory_settings(use_empty=True)
S, H = 0.305, 0.432; TT = 0.02; R = 0.03; LW, LT = 0.045, 0.018; ZF0, ZF1 = 0.012, 0.034

def walnut():
    m = bpy.data.materials.new('Walnut Laminate'); m.use_nodes = True; nt = m.node_tree; b = nt.nodes['Principled BSDF']
    tc = nt.nodes.new('ShaderNodeTexImage'); tc.image = bpy.data.images.load(os.path.join(TEX, 'walnut_veneer_Diffuse_2k.jpg'))
    mx = nt.nodes.new('ShaderNodeMix'); mx.data_type = 'RGBA'; mx.blend_type = 'MULTIPLY'; mx.inputs['Factor'].default_value = 1
    nt.links.new(tc.outputs['Color'], mx.inputs['A']); mx.inputs['B'].default_value = (0.40, 0.25, 0.15, 1)
    nt.links.new(mx.outputs['Result'], b.inputs['Base Color']); b.inputs['Roughness'].default_value = 0.45
    tn = nt.nodes.new('ShaderNodeTexImage'); tn.image = bpy.data.images.load(os.path.join(TEX, 'walnut_veneer_nor_gl_2k.jpg')); tn.image.colorspace_settings.name = 'Non-Color'
    nm = nt.nodes.new('ShaderNodeNormalMap'); nm.inputs['Strength'].default_value = 0.35; nt.links.new(tn.outputs['Color'], nm.inputs['Color']); nt.links.new(nm.outputs['Normal'], b.inputs['Normal'])
    return m
def cane():
    N = 512; y, x = np.mgrid[0:N, 0:N] / N * 2 * math.pi * 14
    hexa = np.clip(0.5 + 0.5 * np.maximum(np.sin(x + y), np.sin(x - y)), 0, 1); hole = np.clip((np.cos(x) * np.cos(y) - 0.3) * 4, 0, 1)
    base = np.array([0.86, 0.72, 0.45]); rgb = base * (0.55 + 0.45 * hexa)[..., None]
    alpha = 1 - hole
    img = bpy.data.images.new('cane', N, N, alpha=True); px = np.ones((N, N, 4), np.float32); px[..., :3] = rgb; px[..., 3] = alpha
    img.pixels.foreach_set(px.ravel()); img.pack()
    m = bpy.data.materials.new('Cane Webbing'); m.use_nodes = True; nt = m.node_tree; b = nt.nodes['Principled BSDF']
    t = nt.nodes.new('ShaderNodeTexImage'); t.image = img; nt.links.new(t.outputs['Color'], b.inputs['Base Color']); nt.links.new(t.outputs['Alpha'], b.inputs['Alpha'])
    b.inputs['Roughness'].default_value = 0.7
    try: m.surface_render_method = 'DITHERED'
    except Exception: pass
    return m
WAL, CANE = walnut(), cane()
parts = []

def rrect(w, d, r, seg=8):
    pts = []
    for cx, cy, a0 in ((w / 2 - r, d / 2 - r, 0), (-w / 2 + r, d / 2 - r, 90), (-w / 2 + r, -d / 2 + r, 180), (w / 2 - r, -d / 2 + r, 270)):
        for k in range(seg + 1):
            a = math.radians(a0 + 90 * k / seg); pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts
def slab(name, outer, inner, z0, z1, m):
    bm = bmesh.new()
    if inner is None:
        f = bm.faces.new([bm.verts.new((x, y, z0)) for x, y in outer])
    else:
        vo = [bm.verts.new((x, y, z0)) for x, y in outer]; vi = [bm.verts.new((x, y, z0)) for x, y in inner]; n = len(vo)
        for k in range(n): bm.faces.new((vo[k], vo[(k + 1) % n], vi[(k + 1) % n], vi[k]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    ext = bmesh.ops.extrude_face_region(bm, geom=list(bm.faces)); nv = [e for e in ext['geom'] if isinstance(e, bmesh.types.BMVert)]
    bmesh.ops.translate(bm, verts=nv, vec=(0, 0, z1 - z0)); bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free(); o = bpy.data.objects.new(name, me); bpy.context.scene.collection.objects.link(o)
    me.materials.append(m); bv = o.modifiers.new('b', 'BEVEL'); bv.width = 0.0015; bv.segments = 2
    bpy.context.view_layer.objects.active = o; bpy.ops.object.modifier_apply(modifier='b'); parts.append(o); return o
slab('Top', rrect(S, S, R), None, H - TT, H, WAL)
slab('ShelfFrame', rrect(S - 0.01, S - 0.01, R - 0.005), rrect(S - 0.07, S - 0.07, 0.008), ZF0, ZF1, WAL)
bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 0, ZF0 + 0.012)); c = bpy.context.object; c.scale = (S - 0.068, S - 0.068, 1)
bpy.ops.object.transform_apply(scale=True); c.data.materials.append(CANE); parts.append(c)
for sx in (-1, 1):
    for sy in (-1, 1):
        wide_x = (sx == sy)                                  # the boards alternate, as in the photos
        dx, dy = (LW, LT) if wide_x else (LT, LW)
        cx = sx * (S / 2 - 0.012 - dx / 2); cy = sy * (S / 2 - 0.012 - dy / 2)
        bpy.ops.mesh.primitive_cube_add(size=1, location=(cx, cy, (ZF0 + H - TT) / 2)); o = bpy.context.object; o.scale = (dx, dy, H - TT - ZF0)
        bpy.ops.object.transform_apply(scale=True); bv = o.modifiers.new('b', 'BEVEL'); bv.width = 0.003; bv.segments = 3; bpy.ops.object.modifier_apply(modifier='b')
        o.data.materials.append(WAL); parts.append(o)
        bpy.ops.mesh.primitive_cylinder_add(radius=0.008, depth=ZF0, vertices=16, location=(cx, cy, ZF0 / 2)); f = bpy.context.object
        fm = bpy.data.materials.get('Buffer') or bpy.data.materials.new('Buffer'); fm.use_nodes = True; fm.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value = (0.85, 0.87, 0.9, 1)
        f.data.materials.append(fm); parts.append(f)
bpy.ops.object.select_all(action='DESELECT')
for o in parts: o.select_set(True)
bpy.context.view_layer.objects.active = parts[0]; bpy.ops.object.join(); st = bpy.context.object; st.name = 'InoSlashed Rattan End Table'
me = st.data
if not me.uv_layers: me.uv_layers.new(name='UV')
bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.select_all(action='SELECT'); bpy.ops.uv.cube_project(cube_size=0.6); bpy.ops.object.mode_set(mode='OBJECT')
ci = [i for i, s in enumerate(me.materials) if s.name == 'Cane Webbing'][0]          # cane panel: its own square UV, 1:1
uv = me.uv_layers.active.data
for p in me.polygons:
    if p.material_index == ci:
        for li, vi in zip(p.loop_indices, p.vertices):
            co = me.vertices[vi].co; uv[li].uv = (co.x / 0.12 + 0.5, co.y / 0.12 + 0.5)
print('SIDETABLE', [round(d, 3) for d in st.dimensions])
sc = bpy.context.scene; sc.render.engine = 'CYCLES'; sc.cycles.samples = 32; sc.view_settings.view_transform = 'AgX'
w = bpy.data.worlds.new('w'); sc.world = w; w.use_nodes = True; w.node_tree.nodes['Background'].inputs['Color'].default_value = (0.9, 0.9, 0.88, 1)
bpy.ops.mesh.primitive_plane_add(size=4); fl = bpy.context.object
ld = bpy.data.lights.new('k', 'AREA'); ld.energy = 90; ld.size = 1.0; lo = bpy.data.objects.new('k', ld); sc.collection.objects.link(lo); lo.location = (0.5, -0.8, 1.2); lo.rotation_euler = (Vector((0, 0, 0.2)) - lo.location).to_track_quat('-Z', 'Y').to_euler()
cd = bpy.data.cameras.new('c'); cd.lens = 50; cam = bpy.data.objects.new('c', cd); sc.collection.objects.link(cam); sc.camera = cam
cam.location = (0.5, -0.85, 0.75); cam.rotation_euler = (Vector((0, 0, 0.2)) - cam.location).to_track_quat('-Z', 'Y').to_euler()
sc.render.resolution_x, sc.render.resolution_y = 800, 900; sc.render.filepath = os.path.splitext(DST)[0] + '_look.png'; bpy.ops.render.render(write_still=True)
bpy.data.objects.remove(fl); bpy.ops.object.select_all(action='DESELECT'); st.select_set(True)
bpy.ops.export_scene.gltf(filepath=DST, export_format='GLB', use_selection=True, export_apply=True, export_image_format='AUTO')
print('DONE sidetable')
