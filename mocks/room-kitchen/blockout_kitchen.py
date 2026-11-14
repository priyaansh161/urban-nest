# Blockout of the kitchen from LAYOUT.md: plain blocks at real size.  blender -b -P blockout_kitchen.py -- <outdir>
import bpy, sys, os, math
from mathutils import Vector
OUT = sys.argv[sys.argv.index('--') + 1]
bpy.ops.wm.read_factory_settings(use_empty=True); scene = bpy.context.scene
X0, X1, Y0, Y1, H = -1.45, 1.45, -1.7, 1.7, 2.9
CT = 0.90
def mat(n, c):
    m = bpy.data.materials.new(n); m.diffuse_color = (*c, 1); return m
M = {k: mat(k, c) for k, c in dict(wall=(0.93, 0.90, 0.84), floor=(0.86, 0.80, 0.70), ceil=(0.95, 0.94, 0.92), wood=(0.62, 0.43, 0.25),
     base=(0.17, 0.20, 0.26), top=(0.95, 0.95, 0.93), marble=(0.92, 0.92, 0.92), steel=(0.65, 0.66, 0.68), black=(0.05, 0.05, 0.06),
     glass=(0.55, 0.75, 0.85), prod=(0.95, 0.3, 0.55), stage=(0.5, 0.7, 0.4)).items()}
def box(n, c, d, m):
    bpy.ops.mesh.primitive_cube_add(size=1, location=c); o = bpy.context.active_object; o.name = n; o.scale = d; o.data.materials.append(M[m]); return o
box('Floor', (0, 0, -0.01), (X1 - X0, Y1 - Y0, 0.02), 'floor'); box('Ceiling', (0, 0, H + 0.01), (X1 - X0, Y1 - Y0, 0.02), 'ceil')
box('Back', (0, Y1 + 0.05, H / 2), (X1 - X0, 0.1, H), 'wall'); box('Left', (X0 - 0.05, 0, H / 2), (0.1, Y1 - Y0, H), 'wall'); box('Right', (X1 + 0.05, 0, H / 2), (0.1, Y1 - Y0, H), 'wall')
box('Front L', (X0 + 0.325, Y0 - 0.05, H / 2), (0.65, 0.1, H), 'wall'); box('Front R', (X1 - 0.325, Y0 - 0.05, H / 2), (0.65, 0.1, H), 'wall'); box('Front head', (0, Y0 - 0.05, 2.5), (1.6, 0.1, 0.8), 'wall')
box('Window', (0, Y1 - 0.01, 1.6), (1.2, 0.03, 1.1), 'glass')
# left wall: tall unit with ovens, fridge, cabinet over it
box('Tall unit', (X0 + 0.31, -1.0, 1.2), (0.62, 1.4, 2.4), 'wood'); box('Microwave', (X0 + 0.63, -1.0, 1.55), (0.02, 0.56, 0.38), 'black'); box('Oven', (X0 + 0.63, -1.0, 0.95), (0.02, 0.56, 0.58), 'black')
box('Fridge', (X0 + 0.36, 0.175, 0.9), (0.72, 0.75, 1.8), 'steel'); box('Over fridge', (X0 + 0.31, 0.175, 2.1), (0.62, 0.75, 0.6), 'wood')
box('Side panel', (X0 + 0.31, 0.6, 1.2), (0.62, 0.04, 2.4), 'wood')
# back run
box('Back base', (0.35, Y1 - 0.3, 0.43), (2.2, 0.6, 0.86), 'base'); box('Back top', (0.35, Y1 - 0.3, CT - 0.02), (2.2, 0.62, 0.04), 'top')
box('Knee space', (-0.05, Y1 - 0.34, 0.43), (0.8, 0.5, 0.84), 'floor')
box('Backsplash', (0.35, Y1 - 0.005, CT + 0.3), (2.2, 0.01, 0.6), 'marble'); box('Sink', (-0.05, Y1 - 0.3, CT - 0.05), (0.6, 0.42, 0.1), 'steel')
# right run
box('Right base', (X1 - 0.3, -0.15, 0.43), (0.6, 2.5, 0.86), 'base'); box('Right top', (X1 - 0.3, -0.15, CT - 0.02), (0.62, 2.5, 0.04), 'top')
box('Right splash', (X1 - 0.005, 0.1, CT + 0.3), (0.01, 3.2, 0.6), 'marble')
box('Hob', (X1 - 0.3, 0.45, CT + 0.01), (0.5, 0.75, 0.02), 'black'); box('Chimney', (X1 - 0.25, 0.45, 1.75), (0.45, 0.75, 0.25), 'glass')
box('Uppers right', (X1 - 0.175, -0.65, 1.875), (0.35, 0.7, 0.75), 'wood'); box('Uppers right 2', (X1 - 0.175, 1.25, 1.875), (0.35, 0.9, 0.75), 'wood')
box('Uppers back', (0.95, Y1 - 0.175, 1.875), (0.6, 0.35, 0.75), 'wood')
# products (pink) and staging (green)
box('Drying rack', (-0.55, Y1 - 0.3, CT + 0.2), (0.45, 0.3, 0.4), 'prod'); box('Knife set', (0.6, Y1 - 0.15, CT + 0.15), (0.12, 0.1, 0.3), 'prod')
box('Pickle jars', (0.85, Y1 - 0.15, CT + 0.08), (0.25, 0.1, 0.16), 'prod'); box('Spatula set', (X1 - 0.15, 0.95, CT + 0.17), (0.12, 0.12, 0.34), 'prod')
box('Oil dispenser', (X1 - 0.12, 0.1, CT + 0.1), (0.08, 0.08, 0.2), 'prod'); box('Mixer', (X1 - 0.2, -0.35, CT + 0.2), (0.25, 0.25, 0.4), 'stage')
box('Tissue roll', (X1 - 0.15, -0.75, CT + 0.15), (0.12, 0.12, 0.3), 'prod'); box('Curd maker', (X1 - 0.2, -1.05, CT + 0.1), (0.18, 0.18, 0.2), 'prod')
box('Runner mat', (0.2, Y1 - 0.85, 0.005), (1.2, 0.45, 0.01), 'prod'); box('RO', (0.85, Y1 - 0.08, 1.5), (0.3, 0.15, 0.4), 'stage')
box('Apron', (X0 + 0.63, -0.25, 1.4), (0.02, 0.5, 0.75), 'prod')
scene.render.engine = 'BLENDER_WORKBENCH'; sh = scene.display.shading; sh.light = 'STUDIO'; sh.color_type = 'MATERIAL'
scene.world = bpy.data.worlds.new('w'); scene.world.color = (0.35, 0.35, 0.35)
cd = bpy.data.cameras.new('c'); cam = bpy.data.objects.new('c', cd); scene.collection.objects.link(cam); scene.camera = cam
def shot(name, loc, tgt, lens=18, res=(1600, 900)):
    cd.type = 'PERSP'; cd.lens = lens; cam.location = loc; cam.rotation_euler = (Vector(tgt) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    scene.render.resolution_x, scene.render.resolution_y = res; scene.render.filepath = os.path.join(OUT, name); bpy.ops.render.render(write_still=True)
shot('blockout_front.png', (0, Y0 - 0.6, 1.5), (0, Y1, 1.1), 16)        # like the reference: from the opening
for o in bpy.data.objects:
    if o.name.startswith(('Ceiling', 'Uppers', 'Over fridge', 'Chimney', 'Front head')): o.hide_render = True
cd.type = 'ORTHO'; cd.ortho_scale = 3.8; cam.location = (0, 0, 9); cam.rotation_euler = (0, 0, 0)
scene.render.resolution_x = scene.render.resolution_y = 1000; scene.render.filepath = os.path.join(OUT, 'plan.png'); bpy.ops.render.render(write_still=True)
