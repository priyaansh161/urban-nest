# Paper side of the PharmVials sample counter, and the set shared by every station:
# Paxxol thermal label and receipt rolls, an unbranded desktop thermal printer, printed sheets that can
# curl out of the printer or lie on the counter, the counter/backsplash/light (stage) and the camera (shoot).
import bpy, bmesh, math, os
from mathutils import Vector, Matrix
from pv_lib import principled, image_material, lathe, _M

def paper_side():
    """End face of a roll: wound paper (fine rings) round a brown cardboard core."""
    if 'Roll side' in _M: return _M['Roll side']
    m = bpy.data.materials.new('Roll side'); m.use_nodes = True; nt = m.node_tree; b = nt.nodes['Principled BSDF']
    tc = nt.nodes.new('ShaderNodeTexCoord')
    flat = nt.nodes.new('ShaderNodeVectorMath'); flat.operation = 'MULTIPLY'; flat.inputs[1].default_value = (1, 1, 0)
    rad = nt.nodes.new('ShaderNodeVectorMath'); rad.operation = 'LENGTH'
    nt.links.new(tc.outputs['Object'], flat.inputs[0]); nt.links.new(flat.outputs[0], rad.inputs[0])
    sc = nt.nodes.new('ShaderNodeMath'); sc.operation = 'MULTIPLY'; sc.inputs[1].default_value = 6000
    wave = nt.nodes.new('ShaderNodeMath'); wave.operation = 'SINE'
    nt.links.new(rad.outputs['Value'], sc.inputs[0]); nt.links.new(sc.outputs[0], wave.inputs[0])
    ramp = nt.nodes.new('ShaderNodeValToRGB')
    ramp.color_ramp.elements[0].color = (0.86, 0.86, 0.83, 1); ramp.color_ramp.elements[1].color = (0.95, 0.95, 0.93, 1)
    nt.links.new(wave.outputs[0], ramp.inputs[0])
    core = nt.nodes.new('ShaderNodeMath'); core.operation = 'LESS_THAN'; core.inputs[1].default_value = 0.0185
    nt.links.new(rad.outputs['Value'], core.inputs[0])
    mix = nt.nodes.new('ShaderNodeMix'); mix.data_type = 'RGBA'
    nt.links.new(core.outputs[0], mix.inputs['Factor']); nt.links.new(ramp.outputs['Color'], mix.inputs['A'])
    mix.inputs['B'].default_value = (0.42, 0.27, 0.15, 1)
    nt.links.new(mix.outputs['Result'], b.inputs['Base Color']); b.inputs['Roughness'].default_value = 0.85
    _M['Roll side'] = m; return m

def paper_roll(name, width, od, tex, loc=(0, 0, 0), standing=True, rot=0.0, core_r=0.0165):
    """A roll of labels or receipts. standing=True: on its edge (axis level), else lying flat (axis up)."""
    R = od / 2
    o = lathe(name, [(core_r, 0), (R - 0.001, 0), (R, 0.001), (R, width - 0.001), (R - 0.001, width), (core_r, width)], paper_side(), seg=128)
    me = o.data
    me.materials.append(image_material('Roll ' + os.path.basename(tex), tex, rough=0.55))
    me.materials.append(principled('Core', (0.42, 0.27, 0.15), rough=0.9))
    uv = me.uv_layers.new()
    for p in me.polygons:
        c = p.center; r = math.hypot(c.x, c.y)
        if r > R - 0.0005 and abs(p.normal.z) < 0.5: p.material_index = 1
        elif r < core_r + 0.0005 and abs(p.normal.z) < 0.5: p.material_index = 2
        ac = math.atan2(c.y, c.x)
        for li in p.loop_indices:
            v = me.vertices[me.loops[li].vertex_index].co
            a = math.atan2(v.y, v.x)
            if ac > 2.5 and a < 0: a += 2 * math.pi            # keep each face on one side of the seam
            uv.data[li].uv = (a / (2 * math.pi) + 0.5, v.z / width)
    if standing:
        me.transform(Matrix.Translation((0, 0, -width / 2)))
        o.rotation_euler = (math.pi / 2, 0, rot); o.location = (loc[0], loc[1], R)
    else:
        o.rotation_euler.z = rot; o.location = loc
    return o

def sheet(name, img, w, path, loc=(0, 0, 0), rot=0.0, rough=0.5):
    """A printed sheet (label strip, receipt) of width w following a side profile path = [(y, z), ...]."""
    me = bpy.data.meshes.new(name); bm = bmesh.new(); uv = bm.loops.layers.uv.new()
    pts = [Vector((0, y, z)) for y, z in path]
    L = [0.0]
    for i in range(1, len(pts)): L.append(L[-1] + (pts[i] - pts[i - 1]).length)
    steps = 60; rows = []
    for s in range(steps + 1):
        t = L[-1] * s / steps
        k = min(max(i for i in range(len(L)) if L[i] <= t + 1e-9), len(pts) - 2)
        p = pts[k].lerp(pts[k + 1], (t - L[k]) / max(L[k + 1] - L[k], 1e-9))
        rows.append((bm.verts.new((-w / 2, p.y, p.z)), bm.verts.new((w / 2, p.y, p.z)), s / steps))
    for i in range(steps):
        a, b, va = rows[i]; c, d, vb = rows[i + 1]
        f = bm.faces.new((a, b, d, c))
        for l, q in zip(f.loops, [(0, 1 - va), (1, 1 - va), (1, 1 - vb), (0, 1 - vb)]): l[uv].uv = q
    bm.to_mesh(me); bm.free()
    for p in me.polygons: p.use_smooth = True
    o = bpy.data.objects.new(name, me); bpy.context.scene.collection.objects.link(o)
    o.data.materials.append(image_material('Sheet ' + os.path.basename(img), img, rough=rough))
    s = o.modifiers.new('thick', 'SOLIDIFY'); s.thickness = 0.00015
    o.location = loc; o.rotation_euler.z = rot
    return o

def _rb(n, c, s, m, bw, seg=6):
    bpy.ops.mesh.primitive_cube_add(size=1, location=c); o = bpy.context.active_object; o.name = n
    o.data.transform(Matrix.Diagonal((*s, 1)))
    b = o.modifiers.new('b', 'BEVEL'); b.width = bw; b.segments = seg; b.harden_normals = True
    for f in o.data.polygons: f.use_smooth = True
    o.data.materials.append(m); return o

def thermal_printer(loc=(0, 0, 0), rot=0.0):
    """A desktop direct-thermal label printer, unbranded: rounded clamshell body, dark lid, front exit slot.
    Returns (body, exit point (y, z) in its own space) so a printed label can run out of the slot."""
    shell = principled('Printer shell', (0.2, 0.21, 0.22), rough=0.5)
    lidm = principled('Printer lid', (0.06, 0.065, 0.07), rough=0.28, coat=0.4)
    W, D = 0.2, 0.24
    body = _rb('Thermal printer', (0, 0, 0.045), (W, D, 0.09), shell, 0.004)       # small chamfers: real moulded housings are crisp
    for n, c, s, m, bw in [
            ('Printer lid', (0, 0.01, 0.112), (W - 0.004, D - 0.03, 0.075), lidm, 0.012),
            ('Roll window', (0, 0.03, 0.1505), (0.11, 0.09, 0.002), principled('Smoke window', (0.3, 0.32, 0.34), rough=0.05, transmission=0.6), 0.001),
            ('Exit slot', (0, -D / 2 - 0.0005, 0.072), (0.135, 0.004, 0.006), principled('Slot', (0.01, 0.01, 0.01), rough=0.8), 0.0008),
            ('Button', (0.055, -D / 2 + 0.02, 0.0905), (0.014, 0.01, 0.003), principled('Button', (0.25, 0.26, 0.27), rough=0.5), 0.0012),
            ('Button', (0.075, -D / 2 + 0.02, 0.0905), (0.014, 0.01, 0.003), principled('Button', (0.25, 0.26, 0.27), rough=0.5), 0.0012)]:
        _rb(n, c, s, m, bw).parent = body
    ledm = principled('LED', (0.1, 0.9, 0.3), rough=0.2)
    ledm.node_tree.nodes['Principled BSDF'].inputs['Emission Color'].default_value = (0.1, 1, 0.35, 1)
    ledm.node_tree.nodes['Principled BSDF'].inputs['Emission Strength'].default_value = 6
    _rb('Status light', (0.035, -D / 2 + 0.02, 0.0908), (0.004, 0.004, 0.002), ledm, 0.0005).parent = body
    for x in (-W / 2 + 0.02, W / 2 - 0.02):
        for y in (-D / 2 + 0.02, D / 2 - 0.02):
            _rb('Foot', (x, y, -0.002), (0.018, 0.018, 0.004), principled('Rubber', (0.03, 0.03, 0.03), rough=0.9), 0.002).parent = body
    # the details that say "label printer": the lid seam, the serrated steel tear bar over the exit, a row of
    # status icons, the feed button, the lid-release latches on both sides
    dark = principled('Seam dark', (0.01, 0.01, 0.012), rough=0.6)
    _rb('Lid seam', (0, 0, 0.0905), (W + 0.0004, D + 0.0004, 0.0012), dark, 0.0003).parent = body
    steel = principled('Tear bar steel', (0.75, 0.76, 0.78), rough=0.25, metallic=1.0)
    _rb('Tear bar', (0, -D / 2 - 0.003, 0.079), (0.14, 0.004, 0.006), steel, 0.0006).parent = body
    for i in range(28):
        _rb('Tear tooth', (-0.065 + i * 0.0048, -D / 2 - 0.0055, 0.0815), (0.002, 0.002, 0.0015), steel, 0.0).parent = body
    icon = principled('Status icon', (0.85, 0.9, 0.95), rough=0.4)
    icon.node_tree.nodes['Principled BSDF'].inputs['Emission Color'].default_value = (0.75, 0.85, 1.0, 1)
    icon.node_tree.nodes['Principled BSDF'].inputs['Emission Strength'].default_value = 1.5
    for i in range(5):
        _rb('Status icon', (-0.045 + i * 0.011, -D / 2 + 0.012, 0.0905), (0.006, 0.0045, 0.0006), icon, 0.0003).parent = body
    _rb('Feed button', (0.055, -D / 2 + 0.014, 0.0905), (0.026, 0.012, 0.003), principled('Button', (0.25, 0.26, 0.27), rough=0.5), 0.002).parent = body
    for x in (-W / 2 - 0.0006, W / 2 + 0.0006):
        _rb('Release latch', (x, -0.03, 0.078), (0.002, 0.03, 0.012), dark, 0.0008).parent = body
    body.location = (loc[0], loc[1], loc[2] + 0.004); body.rotation_euler.z = rot
    return body, (-D / 2, 0.072)

def stage(wall=(0.66, 0.64, 0.6)):
    """The shared set: quartz counter top, backsplash, and the soft pharmacy light used for every station."""
    sc = bpy.context.scene
    quartz = principled('Quartz', (0.8, 0.8, 0.78), rough=0.22); wallm = principled('Wall', wall, rough=0.8)
    for n, c, s, m in [('Counter top', (0, 0, -0.02), (1.8, 0.7, 0.04), quartz), ('Backsplash', (0, 0.36, 0.4), (1.8, 0.02, 0.84), wallm)]:
        _rb(n, c, s, m, 0.003, 3)
    def area(n, loc, size, power, target, color=(1, 1, 1)):
        l = bpy.data.lights.new(n, 'AREA'); l.shape = 'RECTANGLE'; l.size = size[0]; l.size_y = size[1]; l.energy = power; l.color = color
        o = bpy.data.objects.new(n, l); sc.collection.objects.link(o); o.location = loc
        o.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    area('Key panel', (0.1, -0.55, 0.85), (1.0, 0.6), 22, (0, 0.05, 0), (1.0, 0.96, 0.9))
    area('Window', (-1.1, 0.05, 0.55), (0.8, 1.0), 14, (0, 0.05, 0.05), (1.0, 0.96, 0.9))
    area('Fill', (1.0, -0.3, 0.4), (0.6, 0.6), 4, (0, 0.05, 0.05), (0.9, 0.95, 1.0))
    w = bpy.data.worlds.new('w'); sc.world = w; w.use_nodes = True
    w.node_tree.nodes['Background'].inputs['Color'].default_value = (0.82, 0.8, 0.76, 1)
    w.node_tree.nodes['Background'].inputs['Strength'].default_value = 0.12

def shoot(out, samples, cam_loc, target, focus, lens=50, fstop=5.6, res=(1600, 900)):
    """Camera and Cycles settings shared by every station; renders to out."""
    sc = bpy.context.scene
    cd = bpy.data.cameras.new('cam'); cam = bpy.data.objects.new('cam', cd); sc.collection.objects.link(cam); sc.camera = cam
    cd.lens = lens; cam.location = cam_loc
    cam.rotation_euler = (Vector(target) - cam.location).to_track_quat('-Z', 'Y').to_euler()
    cd.dof.use_dof = True; cd.dof.focus_distance = (Vector(focus) - cam.location).length; cd.dof.aperture_fstop = fstop
    sc.render.engine = 'CYCLES'; cy = sc.cycles; cy.device = 'CPU'
    cy.samples = samples; cy.use_denoising = True; cy.max_bounces = 16; cy.transmission_bounces = 16
    cy.glossy_bounces = 8; cy.transparent_max_bounces = 16; cy.blur_glossy = 1.0; cy.caustics_reflective = False
    sc.view_settings.view_transform = 'AgX'; sc.view_settings.look = 'AgX - Medium High Contrast'
    sc.render.resolution_x, sc.render.resolution_y = res
    sc.render.filepath = out; bpy.ops.render.render(write_still=True)
