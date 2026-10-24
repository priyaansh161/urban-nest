import bpy, bmesh, math, sys
from mathutils import Vector

OUT = sys.argv[sys.argv.index('--') + 1]  # output folder

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene

# ---------- materials (metres everywhere) ----------
def mat(name, color=(0.8, 0.8, 0.8, 1), rough=0.5, metal=0.0, setup=None):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    bsdf = nt.nodes['Principled BSDF']
    bsdf.inputs['Base Color'].default_value = color
    bsdf.inputs['Roughness'].default_value = rough
    bsdf.inputs['Metallic'].default_value = metal
    if setup:
        setup(nt, bsdf)
    return m

def ramp(nt, fac, stops):
    r = nt.nodes.new('ShaderNodeValToRGB')
    r.color_ramp.elements[0].position = stops[0][0]
    r.color_ramp.elements[0].color = stops[0][1]
    r.color_ramp.elements[1].position = stops[-1][0]
    r.color_ramp.elements[1].color = stops[-1][1]
    for pos, col in stops[1:-1]:
        e = r.color_ramp.elements.new(pos)
        e.color = col
    nt.links.new(fac, r.inputs['Fac'])
    return r

def marble_setup(nt, b):
    tc = nt.nodes.new('ShaderNodeTexCoord')
    mp = nt.nodes.new('ShaderNodeMapping'); mp.inputs['Scale'].default_value = (1.2, 1.2, 1.2)
    nz = nt.nodes.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value = 2.2
    nz.inputs['Detail'].default_value = 12; nz.inputs['Distortion'].default_value = 1.6
    wv = nt.nodes.new('ShaderNodeTexWave'); wv.inputs['Scale'].default_value = 1.4
    wv.inputs['Distortion'].default_value = 9; wv.inputs['Detail'].default_value = 3
    nt.links.new(tc.outputs['Object'], mp.inputs['Vector'])
    nt.links.new(mp.outputs['Vector'], nz.inputs['Vector'])
    nt.links.new(mp.outputs['Vector'], wv.inputs['Vector'])
    nt.links.new(nz.outputs['Fac'], wv.inputs['Phase Offset'])
    r = ramp(nt, wv.outputs['Fac'], [(0.42, (0.93, 0.92, 0.90, 1)), (0.5, (0.62, 0.61, 0.60, 1)), (0.56, (0.95, 0.94, 0.92, 1))])
    nt.links.new(r.outputs['Color'], b.inputs['Base Color'])

def wood_setup(nt, b):
    tc = nt.nodes.new('ShaderNodeTexCoord')
    mp = nt.nodes.new('ShaderNodeMapping'); mp.inputs['Scale'].default_value = (14, 1.5, 1.5)
    nz = nt.nodes.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value = 18; nz.inputs['Detail'].default_value = 6
    nt.links.new(tc.outputs['Object'], mp.inputs['Vector'])
    nt.links.new(mp.outputs['Vector'], nz.inputs['Vector'])
    r = ramp(nt, nz.outputs['Fac'], [(0.3, (0.36, 0.22, 0.11, 1)), (0.7, (0.55, 0.37, 0.20, 1))])
    nt.links.new(r.outputs['Color'], b.inputs['Base Color'])
    bump = nt.nodes.new('ShaderNodeBump'); bump.inputs['Strength'].default_value = 0.15
    nt.links.new(nz.outputs['Fac'], bump.inputs['Height'])
    nt.links.new(bump.outputs['Normal'], b.inputs['Normal'])

def cement_setup(nt, b):
    nz = nt.nodes.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value = 4; nz.inputs['Detail'].default_value = 14
    nz2 = nt.nodes.new('ShaderNodeTexNoise'); nz2.inputs['Scale'].default_value = 90
    r = ramp(nt, nz.outputs['Fac'], [(0.35, (0.62, 0.58, 0.52, 1)), (0.65, (0.74, 0.70, 0.64, 1))])
    nt.links.new(r.outputs['Color'], b.inputs['Base Color'])
    bump = nt.nodes.new('ShaderNodeBump'); bump.inputs['Strength'].default_value = 0.08
    nt.links.new(nz2.outputs['Fac'], bump.inputs['Height'])
    nt.links.new(bump.outputs['Normal'], b.inputs['Normal'])

def tile_setup(nt, b):
    tc = nt.nodes.new('ShaderNodeTexCoord')
    mp = nt.nodes.new('ShaderNodeMapping'); mp.inputs['Scale'].default_value = (1, 1, 1)
    br = nt.nodes.new('ShaderNodeTexBrick')
    br.offset = 0.0; br.inputs['Scale'].default_value = 1.0
    br.inputs['Mortar Size'].default_value = 0.006; br.inputs['Bias'].default_value = 0.0
    br.inputs['Brick Width'].default_value = 0.6; br.inputs['Row Height'].default_value = 0.6
    br.inputs['Color1'].default_value = (0.36, 0.34, 0.31, 1)
    br.inputs['Color2'].default_value = (0.48, 0.46, 0.43, 1)
    br.inputs['Mortar'].default_value = (0.16, 0.15, 0.14, 1)
    nt.links.new(tc.outputs['Object'], mp.inputs['Vector'])
    nt.links.new(mp.outputs['Vector'], br.inputs['Vector'])
    nt.links.new(br.outputs['Color'], b.inputs['Base Color'])
    bump = nt.nodes.new('ShaderNodeBump'); bump.inputs['Strength'].default_value = 0.2
    nt.links.new(br.outputs['Fac'], bump.inputs['Height'])
    nt.links.new(bump.outputs['Normal'], b.inputs['Normal'])

M = {
    'tile': mat('Floor Stone Tile', rough=0.35, setup=tile_setup),
    'cement': mat('Microcement', (0.80, 0.73, 0.64, 1), 0.85),
    'oak': mat('Fluted Oak', (0.62, 0.43, 0.24, 1), 0.55),
    'oak2': mat('Fluted Oak B', (0.55, 0.37, 0.20, 1), 0.55),
    'oak3': mat('Fluted Oak C', (0.68, 0.48, 0.28, 1), 0.55),
    'marble': mat('Marble', rough=0.12, setup=marble_setup),
    'white': mat('Gloss White Ceramic', (0.95, 0.95, 0.94, 1), 0.08),
    'brass': mat('Brushed Brass', (0.85, 0.65, 0.28, 1), 0.28, 1.0),
    'ceiling': mat('Ceiling', (0.92, 0.91, 0.89, 1), 0.9),
    'rug': mat('Teal Rug', (0.05, 0.28, 0.30, 1), 1.0),
    'black': mat('Black Metal', (0.02, 0.02, 0.02, 1), 0.4, 0.8),
    'mirror': mat('Mirror', (0.62, 0.68, 0.72, 1), 0.10, 0.6),
}
glow = bpy.data.materials.new('Warm Glow'); glow.use_nodes = True
eb = glow.node_tree.nodes['Principled BSDF']
eb.inputs['Base Color'].default_value = (1, 0.8, 0.55, 1)
eb.inputs['Emission Color'].default_value = (1, 0.72, 0.4, 1)
eb.inputs['Emission Strength'].default_value = 3.0
M['glow'] = glow

# ---------- helpers ----------
def box(name, loc, dim, m, bevel=0.0, collection=None):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o = bpy.context.active_object
    o.name = name
    o.scale = dim
    bpy.ops.object.transform_apply(scale=True)
    o.data.materials.append(m)
    if bevel:
        bv = o.modifiers.new('Bevel', 'BEVEL'); bv.width = bevel; bv.segments = 4
    return o

def cyl(name, loc, r, h, m, rot=(0, 0, 0), seg=48):
    bpy.ops.mesh.primitive_cylinder_add(vertices=seg, radius=r, depth=h, location=loc, rotation=rot)
    o = bpy.context.active_object
    o.name = name
    o.data.materials.append(m)
    bpy.ops.object.shade_smooth()
    return o

def apply_mods(o):
    bpy.context.view_layer.objects.active = o
    for md in list(o.modifiers):
        bpy.ops.object.modifier_apply(modifier=md.name)

W, D, H = 3.2, 2.6, 2.7          # room width (x), depth (y), height (z), metres
X0, X1, Y0, Y1 = -W / 2, W / 2, -D / 2, D / 2

# ---------- shell ----------
bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 0, 0))
floor = bpy.context.active_object; floor.name = 'Floor'
floor.scale = (W, D, 1); bpy.ops.object.transform_apply(scale=True)
floor.data.materials.append(M['tile'])
box('Ceiling', (0, 0, H + 0.02), (W, D, 0.04), M['ceiling'])
box('Wall Right', (X1 + 0.05, 0, H / 2), (0.1, D, H), M['cement'])
# left wall with a window opening
wy0, wy1, wz0, wz1 = -0.55, 0.55, 0.95, 2.15
box('Wall Left Low', (X0 - 0.05, 0, wz0 / 2), (0.1, D, wz0), M['cement'])
box('Wall Left High', (X0 - 0.05, 0, (wz1 + H) / 2), (0.1, D, H - wz1), M['cement'])
box('Wall Left Front', (X0 - 0.05, (Y0 + wy0) / 2, (wz0 + wz1) / 2), (0.1, wy0 - Y0, wz1 - wz0), M['cement'])
box('Wall Left Back', (X0 - 0.05, (wy1 + Y1) / 2, (wz0 + wz1) / 2), (0.1, Y1 - wy1, wz1 - wz0), M['cement'])
# window frame + glass
for i, (loc, dim) in enumerate([
        ((X0 + 0.03, 0, wz0 + 0.02), (0.06, wy1 - wy0, 0.04)), ((X0 + 0.03, 0, wz1 - 0.02), (0.06, wy1 - wy0, 0.04)),
        ((X0 + 0.03, wy0 + 0.02, (wz0 + wz1) / 2), (0.06, 0.04, wz1 - wz0)), ((X0 + 0.03, wy1 - 0.02, (wz0 + wz1) / 2), (0.06, 0.04, wz1 - wz0)),
        ((X0 + 0.03, 0, (wz0 + wz1) / 2), (0.05, 0.03, wz1 - wz0))]):
    box('Window Frame %d' % i, loc, dim, M['black'])
sky = mat('Sky Glow', (1, 1, 1, 1), 1.0)
sky.node_tree.nodes['Principled BSDF'].inputs['Emission Color'].default_value = (0.85, 0.92, 1.0, 1)
sky.node_tree.nodes['Principled BSDF'].inputs['Emission Strength'].default_value = 2.0
box('Window Sky', (X0 - 0.12, 0, (wz0 + wz1) / 2), (0.02, wy1 - wy0, wz1 - wz0), sky)

# back wall: fluted oak, one joined mesh of vertical slats on a backing board
box('Back Wall Backing', (0, Y1 + 0.04, H / 2), (W, 0.08, H), M['black'])
slats = []
pitch, sw = 0.06, 0.04
n = int(W / pitch)
for i in range(n):
    x = X0 + pitch / 2 + i * pitch
    s = box('slat', (x, Y1 - 0.0125, H / 2), (sw, 0.025, H), [M['oak'], M['oak2'], M['oak3']][(i * 7 + i // 3) % 3], bevel=0.006)
    apply_mods(s)
    slats.append(s)
bpy.ops.object.select_all(action='DESELECT')
for s in slats:
    s.select_set(True)
bpy.context.view_layer.objects.active = slats[0]
bpy.ops.object.join()
bpy.context.active_object.name = 'Fluted Oak Wall'

# ---------- vanity (counter height 0.85 m) ----------
VX, VY = -0.1, Y1 - 0.30
vb = box('Vanity Cabinet', (VX, VY, 0.62), (1.2, 0.5, 0.46), M['oak'], bevel=0.008); apply_mods(vb)
for i in range(3):
    g = box('Drawer Gap %d' % i, (VX - 0.4 + i * 0.4, VY - 0.251, 0.62), (0.006, 0.004, 0.44), M['black'])
vt = box('Vanity Top', (VX, VY - 0.01, 0.865), (1.3, 0.54, 0.03), M['marble'], bevel=0.004); apply_mods(vt)
basin = cyl('Vessel Basin', (VX, VY - 0.02, 0.96), 0.2, 0.16, M['white'])
cyl('Basin Inner Shadow', (VX, VY - 0.02, 1.0), 0.17, 0.02, M['ceiling'])
# tap
cyl('Tap Stem', (VX, VY + 0.17, 1.00), 0.012, 0.28, M['brass'])
cyl('Tap Arm', (VX, VY + 0.07, 1.14), 0.010, 0.2, M['brass'], rot=(math.pi / 2, 0, 0))

# ---------- mirror with backlight ring ----------
cyl('Mirror Glow', (VX, Y1 - 0.045, 1.55), 0.50, 0.01, M['glow'], rot=(math.pi / 2, 0, 0))
cyl('Mirror', (VX, Y1 - 0.055, 1.55), 0.45, 0.012, M['mirror'], rot=(math.pi / 2, 0, 0))
cyl('Mirror Frame', (VX, Y1 - 0.052, 1.55), 0.462, 0.012, M['brass'], rot=(math.pi / 2, 0, 0))
# wall sconces either side
for sx in (-0.95, 0.75):
    cyl('Sconce %s' % sx, (sx, Y1 - 0.075, 1.6), 0.03, 0.12, M['brass'], rot=(math.pi / 2, 0, 0))
    cyl('Sconce Glow %s' % sx, (sx, Y1 - 0.14, 1.6), 0.045, 0.02, M['glow'], rot=(math.pi / 2, 0, 0))

# ---------- freestanding tub, 1.7 x 0.8 x 0.55 ----------
TX, TY = X1 - 0.65, -0.15
outer = box('Tub Outer', (TX, TY, 0.275), (0.8, 1.7, 0.55), M['white'], bevel=0.22)
apply_mods(outer)
inner = box('Tub Inner', (TX, TY, 0.37), (0.62, 1.52, 0.55), M['white'], bevel=0.2)
apply_mods(inner)
bm = outer.modifiers.new('Hollow', 'BOOLEAN'); bm.operation = 'DIFFERENCE'; bm.object = inner
apply_mods(outer)
bpy.data.objects.remove(inner)
bpy.context.view_layer.objects.active = outer
bpy.ops.object.shade_smooth()
outer.data.polygons.foreach_set('use_smooth', [True] * len(outer.data.polygons))
outer.data.update()
cyl('Tub Filler', (TX, TY + 0.95, 0.5), 0.015, 0.8, M['brass'])

# ---------- small things ----------
box('Teal Rug', (VX, VY - 0.85, 0.01), (1.0, 0.65, 0.02), M['rug'], bevel=0.008)
box('Stool', (TX - 0.65, TY - 0.55, 0.22), (0.3, 0.3, 0.44), M['oak'], bevel=0.02)

# ceiling cove light strip along the back wall
box('Cove Strip', (0, Y1 - 0.08, H - 0.04), (W - 0.1, 0.1, 0.02), M['glow'])

# ---------- lights ----------
def area(name, loc, size, energy, color, rot=(0, 0, 0), shape='RECTANGLE', size_y=None):
    ld = bpy.data.lights.new(name, 'AREA')
    ld.energy = energy; ld.color = color; ld.shape = shape; ld.size = size
    if size_y: ld.size_y = size_y
    lo = bpy.data.objects.new(name, ld)
    lo.location = loc; lo.rotation_euler = rot
    scene.collection.objects.link(lo)
    return lo

area('Window Light', (X0 + 0.15, 0, 1.6), 1.2, 110, (0.85, 0.92, 1.0), rot=(0, math.radians(90), 0), size_y=1.1)
area('Cove Light', (0, Y1 - 0.15, H - 0.06), 3.0, 30, (1.0, 0.75, 0.5), rot=(math.radians(180), 0, 0), size_y=0.2)
area('Mirror Light', (VX, Y1 - 0.2, 1.55), 0.8, 20, (1.0, 0.8, 0.6), rot=(math.radians(90), 0, 0), size_y=0.8)
area('Fill', (0.3, -0.8, 2.5), 2.0, 10, (1.0, 0.95, 0.9), rot=(math.radians(180), 0, 0), size_y=1.5)
scene.view_settings.view_transform = 'AgX'

world = bpy.data.worlds.new('World'); scene.world = world
world.use_nodes = True
world.node_tree.nodes['Background'].inputs['Color'].default_value = (0.05, 0.05, 0.06, 1)
world.node_tree.nodes['Background'].inputs['Strength'].default_value = 0.3

# ---------- camera ----------
cam_d = bpy.data.cameras.new('Cam'); cam_d.lens = 18
cam = bpy.data.objects.new('Cam', cam_d); scene.collection.objects.link(cam)
cam.location = (-0.15, Y0 + 0.12, 1.4)
look = Vector((-0.1, Y1, 1.0))
cam.rotation_euler = (look - cam.location).to_track_quat('-Z', 'Y').to_euler()
scene.camera = cam

# ---------- bake procedural colour into real images (glTF cannot carry procedural nodes) ----------
def bake_color(obj, m, px, tag):
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True); bpy.context.view_layer.objects.active = obj
    if tag != 'floor':   # the floor plane already has a clean 0-1 UV
        bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.uv.smart_project(angle_limit=math.radians(66), island_margin=0.01)
        bpy.ops.object.mode_set(mode='OBJECT')
    img = bpy.data.images.new('bake_' + tag, px, px)
    nt = m.node_tree
    tex = nt.nodes.new('ShaderNodeTexImage'); tex.image = img
    nt.nodes.active = tex
    for n in nt.nodes: n.select = False
    tex.select = True
    scene.cycles.samples = 8
    bpy.ops.object.bake(type='DIFFUSE', pass_filter={'COLOR'}, margin=6, use_clear=True)
    path = OUT + '/tex_' + tag + '.png'
    img.save_render(path)
    final = bpy.data.images.load(path); final.pack()
    bsdf = nt.nodes['Principled BSDF']
    for l in list(bsdf.inputs['Base Color'].links): nt.links.remove(l)
    for l in list(bsdf.inputs['Normal'].links): nt.links.remove(l)
    tex.image = final
    nt.links.new(tex.outputs['Color'], bsdf.inputs['Base Color'])

scene.render.engine = 'CYCLES'
bake_color(floor, M['tile'], 2048, 'floor')
bake_color(vt, M['marble'], 2048, 'marble')

# ---------- render ----------
scene.render.engine = 'CYCLES'
scene.cycles.device = 'CPU'
scene.cycles.samples = 64
scene.cycles.use_denoising = True
scene.render.resolution_x, scene.render.resolution_y = 1280, 720
scene.render.filepath = OUT + '/bathroom_preview.png'
bpy.ops.render.render(write_still=True)

# ---------- export (modifiers applied, +Y up per glTF) ----------
bpy.ops.export_scene.gltf(filepath=OUT + '/bathroom_pilot.glb', export_format='GLB', export_apply=True, export_cameras=False, export_lights=False)
bpy.ops.wm.save_as_mainfile(filepath=OUT + '/bathroom_pilot.blend')
print('DONE')
