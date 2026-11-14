# Realism pass for the interactive counter (31 Oct 2026). His verdict on the first baked viewer: "mushy,
# everything circular, cartoonish". The causes, and what this module does about each:
#   - every lathe-built object (vials, caps, rolls, cups) was smooth-shaded across its sharp edges, so a roll's flat
#     end melted into its curved face (his "donut") -> crisp(): smooth only between faces under 35 degrees
#   - surfaces drawn with Blender node maths (the roll ends) come out plain in a web viewer -> real image textures
#   - a few objects were simple stand-ins (the pill cutter, the computer) -> rebuilt in detail
# plus the two additions he approved: an Rx Pickup sign and a PharmVials box of vials.
import bpy, bmesh, math, os, random
from mathutils import Vector, Matrix
from pv_lib import principled, image_material, lathe, _bx, TEX, VIALS, vial

def crisp(objs, angle=35):
    """Smooth shading only where faces meet at less than `angle`: round things stay round, edges stay sharp."""
    meshes = [o for o in objs if o.type == 'MESH']
    bpy.ops.object.select_all(action='DESELECT')
    for o in meshes: o.select_set(True)
    if meshes:
        bpy.context.view_layer.objects.active = meshes[0]
        bpy.ops.object.shade_smooth_by_angle(angle=math.radians(angle), keep_sharp_edges=True)

def box_uv(o, tile):
    """World-scale UVs on a box-like mesh (each face projected along its main axis), `tile` metres per image."""
    me = o.data; uv = me.uv_layers[0] if me.uv_layers else me.uv_layers.new(name='UV'); mw = o.matrix_world
    for p in me.polygons:
        n = p.normal; ax = max(range(3), key=lambda i: abs(n[i]))
        for li in p.loop_indices:
            w = mw @ me.vertices[me.loops[li].vertex_index].co
            a, b = [(w.y, w.z), (w.x, w.z), (w.x, w.y)][ax]
            uv.data[li].uv = (a / tile, b / tile)

def roll_ends():
    """The ends of every Paxxol roll: wound paper rings round a brown core, as an image (planar UVs on the end faces)."""
    m = image_material('Roll end', os.path.join(TEX, 'roll_side.png'), rough=0.85)
    for o in bpy.data.objects:
        if o.type != 'MESH' or not any(s.material and s.material.name.startswith('Roll side') for s in o.material_slots): continue
        me = o.data; idx = [i for i, s in enumerate(o.material_slots) if s.material and s.material.name.startswith('Roll side')]
        for i in idx: o.material_slots[i].material = m
        R = max(math.hypot(v.co.x, v.co.y) for v in me.vertices)
        uv = me.uv_layers[0]
        for p in me.polygons:
            if p.material_index in idx and abs(p.normal.z) > 0.5:
                for li in p.loop_indices:
                    co = me.vertices[me.loops[li].vertex_index].co
                    uv.data[li].uv = (0.5 + co.x / (2 * R), 0.5 + co.y / (2 * R))

def _stadium(name, L, W, h, z0, m, bev=0.003):
    """A pill-shaped slab (two half-circles joined by straight sides), L long, W wide, h tall, edges rounded."""
    bm = bmesh.new(); r = W / 2; seg = 24; pts = []
    for k in range(seg + 1): a = -math.pi / 2 + math.pi * k / seg; pts.append(((L / 2 - r) + r * math.cos(a), r * math.sin(a)))
    for k in range(seg + 1): a = math.pi / 2 + math.pi * k / seg; pts.append((-(L / 2 - r) + r * math.cos(a), r * math.sin(a)))
    vs = [bm.verts.new((x, y, z0)) for x, y in pts]; f = bm.faces.new(vs)
    ext = bmesh.ops.extrude_face_region(bm, geom=[f]); top = [e for e in ext['geom'] if isinstance(e, bmesh.types.BMVert)]
    bmesh.ops.translate(bm, verts=top, vec=(0, 0, h)); bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(name, me); bpy.context.scene.collection.objects.link(o); me.materials.append(m)
    b = o.modifiers.new('round', 'BEVEL'); b.width = bev; b.segments = 4; b.limit_method = 'ANGLE'; b.harden_normals = True
    return o

def pill_cutter(loc=(0, 0, 0), rot=0.0):
    """PharmVials' multiple pill cutter, closed: a deep-blue pill-shaped case (10 x 4.5 x 2.6 cm) in two halves,
    the seam between them, a thumb notch, and the white peg heads of the blade bar showing through the lid slot."""
    blue = principled('Cutter blue', (0.0, 0.2, 0.62), rough=0.28, coat=0.35)
    root = bpy.data.objects.new('Pill cutter', None); bpy.context.scene.collection.objects.link(root)
    _stadium('Cutter base', 0.1, 0.045, 0.0125, 0.0, blue).parent = root
    _stadium('Cutter lid', 0.1, 0.045, 0.0125, 0.0133, blue).parent = root
    _stadium('Cutter seam', 0.0985, 0.0435, 0.0008, 0.0125, principled('Seam dark', (0.01, 0.05, 0.16), rough=0.6), bev=0.0002).parent = root
    _bx('Lid slot', (0, 0, 0.0259), (0.062, 0.006, 0.0006), principled('Slot dark', (0.01, 0.04, 0.12), rough=0.5), bw=0.0002).parent = root
    for x in (-0.024, 0.0, 0.024):
        lathe('Peg head', [(0, 0.0259), (0.0018, 0.0259), (0.0018, 0.0266), (0, 0.0269)], principled('Peg white', (0.92, 0.92, 0.9), rough=0.35), seg=16,
              loc=(x, 0, 0)).parent = root
    _bx('Thumb notch', (0.0, -0.0222, 0.0133), (0.016, 0.002, 0.003), principled('Seam dark', (0.01, 0.05, 0.16), rough=0.6), bw=0.0008).parent = root
    root.location = loc; root.rotation_euler.z = rot
    return root

def computer(loc=(0, 0, 0), rot=0.0):
    """The dispensing computer, built like a real office set: a thin-bezel 24 in monitor with its picture inset in
    the bezel, a sloped arm on a flat oval base, a low-profile keyboard with every key, a shaped mouse."""
    root = bpy.data.objects.new('Computer', None); bpy.context.scene.collection.objects.link(root)
    body = principled('Monitor body', (0.05, 0.05, 0.055), rough=0.32, coat=0.2)
    alu = principled('Stand aluminium', (0.62, 0.63, 0.65), rough=0.28, metallic=1.0)
    # base: a flat rounded slab; arm: a leaning plate up to the hinge
    _stadium('Monitor base', 0.24, 0.17, 0.008, 0.0, alu, bev=0.003).parent = root
    arm = _bx('Monitor arm', (0, 0.05, 0.14), (0.055, 0.012, 0.27), alu, bw=0.004); arm.rotation_euler.x = math.radians(-12); arm.parent = root
    # panel: 0.545 x 0.325 x 0.016 with a rounded back housing; bezel 6 mm; picture inset, mapped once, upright
    W, H, Z = 0.545, 0.325, 0.33
    _bx('Monitor panel', (0, 0.03, Z), (W, 0.016, H), body, bw=0.003).parent = root
    _bx('Monitor back', (0, 0.045, Z - 0.02), (0.3, 0.02, 0.18), body, bw=0.01).parent = root
    _bx('Chin logo plate', (0, 0.0215, Z - H / 2 + 0.006), (0.03, 0.0006, 0.004), alu, bw=0.0002).parent = root
    scr = image_material('Rx screen glow', os.path.join(TEX, 'rx_screen.png'), rough=0.12)
    b = scr.node_tree.nodes['Principled BSDF']; tx = [n for n in scr.node_tree.nodes if n.type == 'TEX_IMAGE'][0]
    scr.node_tree.links.new(tx.outputs['Color'], b.inputs['Emission Color']); b.inputs['Emission Strength'].default_value = 0.9
    me = bpy.data.meshes.new('Monitor screen'); sw, sh = W - 0.012, H - 0.02
    me.from_pydata([(-sw / 2, 0, -sh / 2), (sw / 2, 0, -sh / 2), (sw / 2, 0, sh / 2), (-sw / 2, 0, sh / 2)], [], [(0, 1, 2, 3)])
    uv = me.uv_layers.new(name='UV')
    for i, q in enumerate([(0, 0), (1, 0), (1, 1), (0, 1)]): uv.data[i].uv = q
    s = bpy.data.objects.new('Monitor screen', me); bpy.context.scene.collection.objects.link(s); me.materials.append(scr)
    s.location = (0, 0.0215, Z + 0.004); s.parent = root          # its face already points at the room (-y)
    # keyboard: tilted slab, 6 rows of keys (the bottom row with a space bar), a number pad block
    kb = principled('Keyboard body', (0.11, 0.11, 0.12), rough=0.45)
    keyc = principled('Key cap', (0.2, 0.2, 0.21), rough=0.55)
    _bx('Keyboard', (0, -0.17, 0.008), (0.44, 0.135, 0.012), kb, bw=0.004).parent = root
    k = 0.0175; x0 = -0.205
    for r in range(6):
        y = -0.12 - r * 0.0195; n = 14 if r < 5 else 0
        for c in range(n):
            _bx('Key', (x0 + c * 0.0195 + (0.005 if r in (2, 3) else 0), y, 0.0155), (k, k, 0.005), keyc, bw=0.0015).parent = root
        if r == 5:
            _bx('Space bar', (-0.06, y, 0.0155), (0.11, k, 0.005), keyc, bw=0.0015).parent = root
            for c in (0, 1, 2, 9, 10, 11, 12, 13):
                _bx('Key', (x0 + c * 0.0195, y, 0.0155), (k, k, 0.005), keyc, bw=0.0015).parent = root
    for r in range(5):
        for c in range(3):
            _bx('Key', (0.085 + c * 0.0195 + 0.03, -0.12 - r * 0.0195, 0.0155), (k, k, 0.005), keyc, bw=0.0015).parent = root
    # mouse: a smooth ellipsoid, flattened, with its button split
    bpy.ops.mesh.primitive_uv_sphere_add(segments=32, ring_count=16, radius=1); mo = bpy.context.active_object; mo.name = 'Mouse'
    mo.scale = (0.031, 0.058, 0.019); mo.location = (0.29, -0.15, 0.0); mo.data.materials.append(kb)
    for p in mo.data.polygons: p.use_smooth = True
    bm = bmesh.new(); bm.from_mesh(mo.data)
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if v.co.z < -0.05], context='VERTS'); bm.to_mesh(mo.data); bm.free()
    mo.parent = root
    _bx('Mouse split', (0.29, -0.175, 0.0185), (0.0008, 0.035, 0.002), principled('Split', (0.02, 0.02, 0.02), rough=0.6), bw=0.0).parent = root
    root.location = loc; root.rotation_euler.z = rot
    return root

def vial_box(loc=(0, 0, 0), rot=0.0):
    """A PharmVials shipping box of 13 DR amber vials (33.2 x 29.4 x 37.2 cm, as their listing gives), its top
    flaps open, vials showing inside."""
    root = bpy.data.objects.new('PharmVials box', None); bpy.context.scene.collection.objects.link(root)
    W, D, H = 0.332, 0.294, 0.372
    side = image_material('Vial box side', os.path.join(TEX, 'vial_box.png'), rough=0.85)
    kraft = principled('Box kraft', (0.6, 0.45, 0.29), rough=0.85)
    me = bpy.data.meshes.new('Vial box'); bm = bmesh.new(); uvl = bm.loops.layers.uv.new()
    bmesh.ops.create_cube(bm, size=1)
    bmesh.ops.scale(bm, vec=(W, D, H), verts=bm.verts); bmesh.ops.translate(bm, vec=(0, 0, H / 2), verts=bm.verts)
    bmesh.ops.delete(bm, geom=[f for f in bm.faces if f.normal.z > 0.5], context='FACES')       # open top
    for f in bm.faces:
        n = f.normal
        for l in f.loops:
            c = l.vert.co
            l[uvl].uv = ((c.x / W + 0.5) if abs(n.y) > 0.5 else (c.y / D + 0.5), c.z / H)
            if n.x > 0.5 or n.y > 0.5: l[uvl].uv = (1 - l[uvl].uv[0], l[uvl].uv[1])
    bm.to_mesh(me); bm.free()
    bo = bpy.data.objects.new('Vial box', me); bpy.context.scene.collection.objects.link(bo); me.materials.append(side); bo.parent = root
    s = bo.modifiers.new('wall', 'SOLIDIFY'); s.thickness = 0.004; s.offset = -1
    for n_, c, sz, ax, ang in [('Flap', (0, -D / 2 - 0.07, H), (W, 0.14, 0.003), 'x', -0.5), ('Flap', (0, D / 2 + 0.07, H), (W, 0.14, 0.003), 'x', 0.5),
                               ('Flap', (-W / 2 - 0.07, 0, H), (0.14, D, 0.003), 'y', 0.45), ('Flap', (W / 2 + 0.07, 0, H), (0.14, D, 0.003), 'y', -0.45)]:
        f = _bx(n_, c, sz, kraft, bw=0.0008)
        # hinge each flap on its edge of the opening, tipped outwards
        pivot = Vector((c[0] * (W / 2) / abs(c[0]) if c[0] else 0, c[1] * (D / 2) / abs(c[1]) if c[1] else 0, H))
        f.data.transform(Matrix.Translation(Vector(c) - pivot)); f.location = pivot
        setattr(f.rotation_euler, ax, ang); f.parent = root
    rnd = random.Random(2)
    for i in range(5):
        for j in range(4):
            v = vial('Box vial', 13, 'amber', 'cr', loc=(-0.12 + i * 0.06 + rnd.uniform(-0.004, 0.004), -0.1 + j * 0.065, H - 0.08))
            v.parent = root
    root.location = loc; root.rotation_euler.z = rot
    return root

def rx_sign(loc=(0, 0, 0), rot=0.0):
    """The Rx Pickup sign: a white acrylic panel (60 x 18 cm) on two brushed stand-offs."""
    root = bpy.data.objects.new('Rx Pickup sign', None); bpy.context.scene.collection.objects.link(root)
    me = bpy.data.meshes.new('Rx sign face'); w, h = 0.6, 0.18
    me.from_pydata([(-w / 2, 0, -h / 2), (w / 2, 0, -h / 2), (w / 2, 0, h / 2), (-w / 2, 0, h / 2)], [], [(0, 1, 2, 3)])
    uv = me.uv_layers.new(name='UV')
    for i, q in enumerate([(0, 0), (1, 0), (1, 1), (0, 1)]): uv.data[i].uv = q
    o = bpy.data.objects.new('Rx sign face', me); bpy.context.scene.collection.objects.link(o)
    me.materials.append(image_material('Rx sign', os.path.join(TEX, 'rx_pickup.png'), rough=0.2))
    o.location = (0, -0.0125, 0); o.parent = root                 # faces the room (-y)
    _bx('Rx sign panel', (0, -0.006, 0), (w, 0.012, h), principled('Acrylic white', (0.95, 0.95, 0.95), rough=0.15, coat=0.6), bw=0.003).parent = root
    for x in (-w / 2 + 0.04, w / 2 - 0.04):
        so = lathe('Stand-off', [(0, 0), (0.007, 0), (0.007, 0.018), (0, 0.018)], principled('Brushed steel', (0.7, 0.7, 0.7), rough=0.3, metallic=1.0), seg=16,
                   loc=(x, 0.0, 0))
        so.rotation_euler.x = -math.pi / 2; so.parent = root          # from the panel back to the wall (+y)
    root.location = loc; root.rotation_euler.z = rot
    return root
