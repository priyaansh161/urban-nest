# Staging appliances for the kitchen (no dots, not for sale), from Meshy builds of real products' photos:
#   mixer: Bajaj Ninja Carve 750 W (white/purple). Meshy built the base with its big jar AND the two small jars beside it;
#          only the main unit stays (the parts standing under the tallest one).
#   chimney: Elica Curve 60 cm curved-glass hood, as Meshy built it (its duct cover goes up into the cabinet niche).
# Writes ../products/final/stage_mixer.glb and stage_chimney.glb.   blender -b -P finish_staging.py
import bpy, bmesh, os, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(HERE, '..', 'products', 'final')

def load(f):
    bpy.ops.wm.read_factory_settings(use_empty=True); bpy.ops.import_scene.gltf(filepath=os.path.join(HERE, f))
    ms = [o for o in bpy.data.objects if o.type == 'MESH']
    bpy.ops.object.select_all(action='DESELECT')
    for o in ms: o.select_set(True)
    bpy.context.view_layer.objects.active = ms[0]
    if len(ms) > 1: bpy.ops.object.join()
    o = bpy.context.view_layer.objects.active; bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM'); bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    for e in [x for x in bpy.data.objects if x != o]: bpy.data.objects.remove(e)
    return o

def export(o, name):
    bpy.ops.object.select_all(action='DESELECT'); o.select_set(True); bpy.context.view_layer.objects.active = o
    bpy.ops.export_scene.gltf(filepath=os.path.join(OUT, name), export_format='GLB', use_selection=True, export_draco_mesh_compression_enable=True, export_image_format='WEBP')

# mixer: keep the faces over the main unit's footprint (measured: the unit stands at x -0.46..0.57, y 0..0.83 in Meshy's
# frame; the two small jars sit in front of it, y < 0, either side). Meshy's mesh is many loose shards, so this cuts by position.
o = load('mixer.glb')
bm = bmesh.new(); bm.from_mesh(o.data)
def keep(c): return (-0.47 < c.x < 0.58) if c.z > -0.30 else (-0.445 < c.x < 0.40)     # the small jars stand low, either side
gone = [f for f in bm.faces if not keep(f.calc_center_median())]
bmesh.ops.delete(bm, geom=gone, context='FACES'); bm.to_mesh(o.data); bm.free(); o.data.update()
print('MIXER faces left', len(o.data.polygons))
export(o, 'stage_mixer.glb')

export(load('chimney.glb'), 'stage_chimney.glb')
print('DONE')
