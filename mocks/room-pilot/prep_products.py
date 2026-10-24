# Bathroom MK2 products (his Meshy downloads, ~100k tris and 2-4k textures each) -> room-ready products/mk2-*.glb.
# Detail lives in the textures, so meshes are decimated hard while colour + normal maps stay sharp (2048 colour on
# the two busiest pieces, 1024 elsewhere: a 2048 colour JPEG is ~3 MB; normal maps 1024). Meshy's emissive map is dropped (it is black). Draco.
#   blender -b -P prep_products.py -- <source dir: Downloads, or the repo's models/> <out dir> [names...]
import bpy, sys, os
from mathutils import Vector
dl, out = sys.argv[sys.argv.index('--') + 1: sys.argv.index('--') + 3]
# (download file prefix, output name, target triangles, texture size)
JOBS = [('Meshy_AI_Beige_Pebble_Bath_Mat_', 'mk2-vanity-mat', 20000, 1024),
        ('Meshy_AI_Beige_U_shaped_textur_', 'mk2-toilet-mat', 15000, 1024),
        ('Meshy_AI_Botanico_Coffee_Vanil_', 'mk2-scented-candle', 15000, 1024),
        ('Meshy_AI_Ceramic_Canister_Set__', 'mk2-accessories-set', 40000, 2048),
        ('Meshy_AI_Chrome_Towel_Ring_in__', 'mk2-towel-hanger', 25000, 1024),
        ('Meshy_AI_Golden_Luxe_Bathroom__', 'mk2-wall-shelf-organiser', 50000, 2048),
        ('Meshy_AI_Modern_black_wall_mou_', 'mk2-towel-rack', 40000, 1024),
        ('Meshy_AI_Navy_Fuzzy_Slippers_', 'mk2-bathroom-sliders', 25000, 1024),
        ('Meshy_AI_Obsidian_Wall_Thermos_', 'mk2-wall-soap-dispenser', 10000, 1024),
        ('Meshy_AI_Phone_on_Toilet_Paper_', 'mk2-toilet-paper-holder', 25000, 1024),
        ('Meshy_AI_White_electric_wand_m_', 'mk2-toilet-brush', 15000, 1024),
        ('Meshy_AI_Wooden_Slat_Bath_Mat_', 'mk2-shower-mat', 15000, 1024),
        ('Meshy_AI_White_Ribbed_Trash_Ca_', 'mk2-dustbin', 20000, 1024),
        # the new bath products (24 Oct): their listing models in <repo>/models/, made by tools/list-product.mjs --3d-for
        ('weava-home-memory-foam-bath-mat', 'bath-vanity-mat', 20000, 1024),
        ('saral-home-easy-living', 'bath-toilet-mat', 20000, 1024),
        ('homeze-tpe-anti-slip-shower-mat', 'bath-shower-mat', 25000, 1024),
        ('the-artment-your-artistic-apartment', 'bath-stone-mat', 15000, 1024),
        ('pano-polyresin-bathroom-set', 'bath-accessories-set', 30000, 1024),
        ('the-better-home-soap-dispenser-set', 'bath-dispenser-set', 30000, 1024),
        ('oslen-magic-sticker-towel-ring', 'bath-towel-ring', 20000, 1024),
        ('gloxy-premium-towel-rack', 'bath-towel-rack', 40000, 1024),
        ('achro-self-adhesive-and-wall-mount', 'bath-paper-holder', 25000, 1024),
        ('bonkaso-tilly-toilet-brush', 'bath-toilet-brush', 15000, 1024)]
only = sys.argv[sys.argv.index('--') + 3:]
for prefix, name, target, tex in JOBS:
    if only and name not in only: continue
    src = sorted(f for f in os.listdir(dl) if f.startswith(prefix) and f.endswith('.glb'))[-1]
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=os.path.join(dl, src))
    meshes = [o for o in bpy.context.scene.objects if o.type == 'MESH']
    tris = sum(len(p.vertices) - 2 for o in meshes for p in o.data.polygons)
    if tris > target:
        for o in meshes:
            if name.endswith('-mat'):
                # thin sheets: collapsing the top and the underside into each other throws spikes, so delete the
                # underside first (the thin axis is the smallest one; the toilet mat stands up, its back faces +y)
                import bmesh
                dims = o.dimensions; ax = min(range(3), key=lambda i: dims[i]); sign = 1 if ax == 1 else -1
                bm = bmesh.new(); bm.from_mesh(o.data)
                bmesh.ops.delete(bm, geom=[f for f in bm.faces if f.normal[ax] * sign > 0.5], context='FACES')
                bm.to_mesh(o.data); bm.free()
                lo = min(v.co[ax] for v in o.data.vertices); hi = max(v.co[ax] for v in o.data.vertices)
            now = sum(len(p.vertices) - 2 for p in o.data.polygons)
            bpy.context.view_layer.objects.active = o
            d = o.modifiers.new('d', 'DECIMATE'); d.ratio = min(1.0, target / max(now, 1)); d.use_collapse_triangulate = True
            bpy.ops.object.modifier_apply(modifier=d.name)
            if name.endswith('-mat'):           # any spike left is pulled back inside the mat's own thickness
                for v in o.data.vertices: v.co[ax] = min(hi, max(lo, v.co[ax]))
                o.data.update(); bpy.context.view_layer.update()
    for m in bpy.data.materials:
        if not m.use_nodes: continue
        b = next((n for n in m.node_tree.nodes if n.type == 'BSDF_PRINCIPLED'), None)
        if not b: continue
        for l in list(b.inputs['Emission Color'].links): m.node_tree.links.remove(l)
        b.inputs['Emission Strength'].default_value = 0.0
    for img in list(bpy.data.images):
        if img.users == 0 or 'emissive' in img.name: continue
        size = tex if 'base' in img.name else 1024   # normal maps at 1024: at 2048 they were 2-4 MB of JPEG noise each
        if max(img.size) > size: img.scale(size, size)
    mn = Vector((1e9,) * 3); mx = Vector((-1e9,) * 3)
    for o in meshes:
        for c in o.bound_box:
            w = o.matrix_world @ Vector(c)
            for i in range(3): mn[i] = min(mn[i], w[i]); mx[i] = max(mx[i], w[i])
    dst = os.path.join(out, name + '.glb')
    bpy.ops.export_scene.gltf(filepath=dst, export_format='GLB', export_apply=True, export_image_format='JPEG', export_jpeg_quality=84,
                              export_draco_mesh_compression_enable=True, export_draco_mesh_compression_level=6)
    after = sum(len(p.vertices) - 2 for o in meshes for p in o.data.polygons)
    print('PRODUCT', name, 'tris', tris, '->', after, 'dims', [round(mx[i] - mn[i], 3) for i in range(3)], round(os.path.getsize(dst) / 1e6, 2), 'MB')
