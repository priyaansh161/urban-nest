# Blockout of the lounge from LAYOUT.md: plain blocks at real size. blender -b -P blockout_living.py -- <outdir>
import bpy, sys, os, math
from mathutils import Vector
OUT = sys.argv[sys.argv.index('--') + 1]
bpy.ops.wm.read_factory_settings(use_empty=True); scene = bpy.context.scene
X0, X1, Y0, Y1, H = -2.6, 2.6, -2.1, 2.1, 3.0
def mat(n, c):
    m = bpy.data.materials.new(n); m.diffuse_color = (*c, 1); return m
M = {k: mat(k, c) for k, c in dict(wall=(0.06, 0.10, 0.24), floor=(0.88, 0.88, 0.86), ceil=(0.93, 0.91, 0.87), cream=(0.92, 0.9, 0.84),
     cog=(0.55, 0.27, 0.10), rose=(0.22, 0.09, 0.06), rattan=(0.7, 0.55, 0.32), rug=(0.55, 0.22, 0.15), green=(0.08, 0.22, 0.12),
     glass=(0.1, 0.12, 0.2), prod=(0.95, 0.3, 0.55), leaf=(0.1, 0.35, 0.12), black=(0.02, 0.02, 0.02)).items()}
def box(n, c, d, m, rot=0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=c, rotation=(0, 0, rot)); o = bpy.context.active_object; o.name = n; o.scale = d; o.data.materials.append(M[m]); return o
def cyl(n, c, r, h, m):
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=h, location=c); o = bpy.context.active_object; o.name = n; o.data.materials.append(M[m]); return o
def arch(n, axis, pos, cx, w, sill, apex):
    spring = apex - w / 2
    if axis == 'x':
        box(n, (pos - 0.02, cx, (sill + spring) / 2), (0.05, w, spring - sill), 'glass'); o = cyl(n + ' top', (pos - 0.02, cx, spring), w / 2, 0.05, 'glass'); o.rotation_euler = (0, math.pi / 2, 0)
        for s in (-1, 1): box(n + ' shutter', (pos - 0.1, cx + s * (w / 2 + 0.2), (sill + spring) / 2), (0.05, 0.4, spring - sill), 'green')
    else:
        box(n, (cx, pos + 0.02, (sill + spring) / 2), (w, 0.05, spring - sill), 'glass'); o = cyl(n + ' top', (cx, pos + 0.02, spring), w / 2, 0.05, 'glass'); o.rotation_euler = (math.pi / 2, 0, 0)
        for s in (-1, 1): box(n + ' shutter', (cx + s * (w / 2 + 0.2), pos + 0.1, (sill + spring) / 2), (0.4, 0.05, spring - sill), 'green')
box('Floor', (0, 0, -0.01), (5.2, 4.2, 0.02), 'floor')
box('Border', (0, 0, 0.001), (4.4, 3.4, 0.002), 'black'); box('Border2', (0, 0, 0.003), (4.3, 3.3, 0.002), 'floor')
box('Ceiling', (0, 0, H + 0.01), (5.2, 4.2, 0.02), 'ceil')
box('Back', (0, Y1 + 0.05, H / 2), (5.2, 0.1, H), 'wall'); box('Front', (0, Y0 - 0.05, H / 2), (5.2, 0.1, H), 'wall')
box('Left', (X0 - 0.05, 0, H / 2), (0.1, 4.2, H), 'wall'); box('Right', (X1 + 0.05, 0, H / 2), (0.1, 4.2, H), 'wall')
for n, c, d in [('Cove B', (0, Y1 - 0.12, H - 0.12), (5.2, 0.24, 0.24)), ('Cove F', (0, Y0 + 0.12, H - 0.12), (5.2, 0.24, 0.24)),
                ('Cove L', (X0 + 0.12, 0, H - 0.12), (0.24, 4.2, 0.24)), ('Cove R', (X1 - 0.12, 0, H - 0.12), (0.24, 4.2, 0.24))]: box(n, c, d, 'cream')
arch('Win right', 'x', X1, 0.55, 1.2, 0.9, 2.8); arch('Win front', 'y', Y0, -0.7, 1.2, 0.9, 2.8)
box('Door', (X0 + 0.04, 0.8, 1.2), (0.06, 1.0, 2.4), 'rose')
box('Sideboard', (-1.2, 1.86, 0.41), (1.7, 0.48, 0.82), 'rose')
box('Side table A', (2.35, 1.85, 0.3), (0.5, 0.5, 0.6), 'rose'); box('Side table B', (2.35, -0.85, 0.3), (0.45, 0.45, 0.6), 'rose')
box('Sofa', (2.12, 0.55, 0.4), (0.95, 2.1, 0.8), 'cog'); box('Loveseat', (1.75, -1.6, 0.4), (1.7, 0.95, 0.8), 'cog')
for i, (x, y) in enumerate([(-1.25, 0.65), (-1.25, -0.3)]): box('Armchair %d' % i, (x, y, 0.45), (0.75, 0.75, 0.9), 'rattan')
box('Rug', (0.2, 0.05, 0.01), (2.7, 1.9, 0.02), 'rug'); box('Coffee table', (0.15, 0.1, 0.21), (1.15, 0.65, 0.42), 'rose')
cyl('Navy vase', (-2.35, 1.9, 0.255), 0.115, 0.51, 'prod'); box('Horse', (-1.9, 1.86, 0.82 + 0.1275), (0.18, 0.095, 0.255), 'prod')
cyl('Whisper vase', (-0.55, 1.86, 0.82 + 0.115), 0.08, 0.23, 'prod'); box('Canvas', (-1.2, Y1 - 0.03, 1.5), (0.6, 0.04, 0.68), 'prod')
cyl('Planter+palm', (0.55, 1.85, 0.725), 0.22, 1.45, 'leaf'); box('Clock', (X1 - 0.03, -0.9, 1.8), (0.04, 0.5, 0.5), 'prod')
cyl('Urli', (0.15, 0.1, 0.42 + 0.057), 0.075, 0.114, 'prod'); cyl('Chandelier', (0.15, 0.1, H - 0.15 - 0.35), 0.4, 0.7, 'prod')
cyl('Stool', (-1.9, -1.85, 0.15), 0.15, 0.3, 'prod'); cyl('Tripod lamp', (-2.35, -0.9, 0.75), 0.17, 1.5, 'prod')
scene.render.engine = 'BLENDER_WORKBENCH'; sh = scene.display.shading; sh.light = 'STUDIO'; sh.color_type = 'MATERIAL'
scene.world = bpy.data.worlds.new('w'); scene.world.color = (0.35, 0.35, 0.35)
cd = bpy.data.cameras.new('c'); cam = bpy.data.objects.new('c', cd); scene.collection.objects.link(cam); scene.camera = cam
def shot(name, loc, tgt, lens=18, res=(1600, 900)):
    cd.type = 'PERSP'; cd.lens = lens; cam.location = loc; cam.rotation_euler = (Vector(tgt) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    scene.render.resolution_x, scene.render.resolution_y = res; scene.render.filepath = os.path.join(OUT, name); bpy.ops.render.render(write_still=True)
shot('blockout_front.png', (0, Y0 + 0.15, 1.4), (0, Y1, 1.1))
shot('blockout_corner.png', (-2.4, -1.9, 1.3), (1.2, 1.0, 0.9), lens=15)
for o in bpy.data.objects:
    if o.name.startswith(('Ceiling', 'Cove')): o.hide_render = True
cd.type = 'ORTHO'; cd.ortho_scale = 5.8; cam.location = (0, 0, 9); cam.rotation_euler = (0, 0, 0)
scene.render.resolution_x = scene.render.resolution_y = 1100; scene.render.filepath = os.path.join(OUT, 'plan.png'); bpy.ops.render.render(write_still=True)
