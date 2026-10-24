# Makes light "room versions" of collection models: decimated + 1024px textures + Draco.
# Usage: blender -b -P lod_products.py -- <models dir> <out dir>
import bpy, sys, os
src_dir, out_dir = sys.argv[sys.argv.index('--') + 1: sys.argv.index('--') + 3]
JOBS = [  # (file, target triangles)
    ('ribbed-ceramic-vase-for-home-decor-modern-minimali-light.glb', 12000),
    ('Spring Vase.glb', 12000),
    ('the-crafted-gesture-designer-5-globe-wall-lamp-luxury-bubble.glb', 15000),
    ('shadowkart-upholstered-ottoman-storage-bench-premium-boucle-.glb', 15000),
]
os.makedirs(out_dir, exist_ok=True)
for fname, target in JOBS:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=os.path.join(src_dir, fname))
    meshes = [o for o in bpy.context.scene.objects if o.type == 'MESH']
    total = sum(len(o.data.polygons) for o in meshes) * 1  # approx faces
    ratio = min(1.0, target / max(1, total))
    for o in meshes:
        bpy.context.view_layer.objects.active = o
        d = o.modifiers.new('dec', 'DECIMATE'); d.ratio = ratio
        bpy.ops.object.modifier_apply(modifier=d.name)
    for img in bpy.data.images:
        w, h = img.size
        if max(w, h) > 1024:
            k = 1024 / max(w, h); img.scale(max(1, int(w * k)), max(1, int(h * k)))
    out = os.path.join(out_dir, fname)
    bpy.ops.export_scene.gltf(filepath=out, export_format='GLB', export_apply=True,
                              export_draco_mesh_compression_enable=True, export_draco_mesh_compression_level=6)
    after = sum(len(o.data.polygons) for o in bpy.context.scene.objects if o.type == 'MESH')
    print('LOD', fname, 'faces', total, '->', after, 'ratio', round(ratio, 3), 'MB', round(os.path.getsize(out) / 1e6, 2))
