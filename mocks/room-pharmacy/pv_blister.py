# Blister side of the PharmVials sample counter: Paxxol cards (Jumbo, Twin, Tri-Fold) built as card panels
# carrying the redrawn artwork (make_blister_textures.cjs), clear blister bubbles sitting exactly in each
# printed window (from tex/pax_*.json), tablets and capsules in the filled ones, the white filling tray and
# red seal roller from PharmVials' kit photo, and an unbranded blister-filling machine.
import bpy, bmesh, math, os, json, random
from mathutils import Vector, Matrix
from pv_lib import principled, image_material, lathe, capsule, TEX, _M, imperfect

# panel sizes, metres (Jumbo/Tri-Fold panel 22.9 x 30.5 cm; Twin panel 13.3 x 30.5 cm)
JW, JH, TW = 0.229, 0.305, 0.133
CARD_T = 0.0007

def pet():   return principled('Blister PET', (0.97, 0.98, 1.0), rough=0.04, transmission=1.0, ior=1.12)   # low IOR: reads as a thin shell, not a solid block

def panel(name, tex, w, h, back=None):
    """One card panel, w x h, lying in the XY plane with its left edge on the origin (the fold line)."""
    me = bpy.data.meshes.new(name); bm = bmesh.new(); uv = bm.loops.layers.uv.new()
    v = [bm.verts.new(p) for p in [(0, 0, 0), (w, 0, 0), (w, h, 0), (0, h, 0)]]
    f = bm.faces.new(v)
    for l, q in zip(f.loops, [(0, 0), (1, 0), (1, 1), (0, 1)]): l[uv].uv = q
    bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(name, me); bpy.context.scene.collection.objects.link(o)
    o.data.materials.append(image_material('Card ' + os.path.basename(tex), os.path.join(TEX, tex), rough=0.45))
    if back:
        o.data.materials.append(image_material('Card ' + os.path.basename(back), os.path.join(TEX, back.replace('.png', '_back.png')), rough=0.45))   # seen from behind, so mirrored
    s = o.modifiers.new('card', 'SOLIDIFY'); s.thickness = CARD_T; s.offset = 1     # card grows up from z=0, never into the counter
    if back: s.material_offset = 1; s.material_offset_rim = 1
    return o

def rounded_box(name, sx, sy, sz, m, bw):
    bpy.ops.mesh.primitive_cube_add(size=1); o = bpy.context.active_object; o.name = name
    o.data.transform(Matrix.Translation((0, 0, 0.5)) @ Matrix.Diagonal((1, 1, 1, 1)))
    o.data.transform(Matrix.Diagonal((sx, sy, sz, 1)))
    b = o.modifiers.new('b', 'BEVEL'); b.width = bw; b.segments = 5; b.harden_normals = True
    for f in o.data.polygons: f.use_smooth = True
    o.data.materials.append(m); return o

TABLET = None
def pills_in(parent, cx, cy, ww, wh, rnd):
    """A dose: one or two capsules and a couple of tablets resting in a bubble."""
    global TABLET
    tabs = [principled('Tablet white', (0.93, 0.93, 0.9), rough=0.55), principled('Tablet yellow', (0.95, 0.82, 0.35), rough=0.5),
            principled('Tablet peach', (0.95, 0.7, 0.55), rough=0.5)]
    caps = [(principled('Gelatin maroon', (0.32, 0.03, 0.05), rough=0.12, coat=0.6), principled('Gelatin mustard', (0.86, 0.58, 0.1), rough=0.12, coat=0.6)),
            (principled('Gelatin blue', (0.1, 0.25, 0.6), rough=0.12, coat=0.6), principled('Gelatin white', (0.92, 0.92, 0.9), rough=0.12, coat=0.6))]
    for k in range(rnd.randint(2, 4)):
        x = cx + rnd.uniform(-0.3, 0.3) * ww; y = cy + rnd.uniform(-0.3, 0.3) * wh
        if rnd.random() < 0.4:
            c = capsule('Dose capsule', rnd.choice(caps), length=0.017, r=0.003, loc=(x, y, CARD_T + 0.0031), rot=(math.pi / 2, 0, rnd.uniform(0, 6.28)))
        else:
            r = rnd.choice((0.0035, 0.0045, 0.005))
            c = lathe('Tablet', [(0, 0)] + [(r * 0.85, 0), (r, 0.0008), (r, 0.0022), (r * 0.85, 0.003), (0, 0.0033)], rnd.choice(tabs), seg=32,
                      loc=(x, y, CARD_T + 0.0001))
        c.parent = parent

def bubbles(panel_obj, json_name, w, h, filled=0, seed=1, sealed=True):
    """Clear bubbles over every window of a grid panel; the first `filled` windows (in dose order) get pills."""
    wins = json.load(open(os.path.join(TEX, json_name)))
    rnd = random.Random(seed)
    order = sorted(range(len(wins)), key=lambda i: (round(wins[i][1], 3), wins[i][0]))      # row by row, as a pharmacist fills
    rank = {i: k for k, i in enumerate(order)}
    for i, (fx, fy, fw, fh) in enumerate(wins):
        ww, wh = fw * w * 0.92, fh * h * 0.9
        cx = (fx + fw / 2) * w; cy = (1 - fy - fh / 2) * h
        b = rounded_box('Bubble', ww, wh, 0.011, pet(), 0.0035)
        b.parent = panel_obj; b.location = (cx, cy, CARD_T + 0.0003)
        if rank[i] < filled: pills_in(panel_obj, cx, cy, ww, wh, rnd)
    return panel_obj

def book(name, left_tex, right_tex, grid_json, w, h, open_deg=180, filled=0, seed=1, cover=None, loc=(0, 0, 0), rot=0.0):
    """A two-panel card hinged on its middle: right panel (the dose grid) lies flat, left panel (Rx label
    side; its back is the Paxxol cover) swings up by open_deg - 180 or folds over it when open_deg is ~0."""
    root = bpy.data.objects.new(name, None); bpy.context.scene.collection.objects.link(root)
    right = panel(name + ' grid', right_tex, w, h); right.parent = root
    bubbles(right, grid_json, w, h, filled=filled, seed=seed)
    left = panel(name + ' label side', left_tex, w, h, back=cover)
    left.data.transform(Matrix.Translation((-w, 0, 0)))                    # its fold edge on the origin too
    left.rotation_euler.y = math.radians(180 - open_deg); left.parent = root
    if open_deg < 20: left.location.z = 0.0125 + CARD_T          # closed: the cover rests on the bubbles
    root.location = loc; root.rotation_euler.z = rot
    return root

def filling_tray(loc=(0, 0, 0), rot=0.0, cols=4):
    """The white tray a card sits face-down in while the bubbles are filled: one recess per dose."""
    m = principled('Tray PS', (0.93, 0.93, 0.92), rough=0.3)
    root = rounded_box('Filling tray', 0.25, 0.32, 0.022, m, 0.004)
    for c in range(cols):
        for r in range(7):
            cell = rounded_box('Tray cell', 0.042, 0.033, 0.003, principled('Tray cell', (0.8, 0.8, 0.79), rough=0.35), 0.002)
            cell.location = (-0.095 + c * 0.063, -0.12 + r * 0.04, 0.0205); cell.parent = root
    root.location = loc; root.rotation_euler.z = rot
    return root

def seal_roller(loc=(0, 0, 0), rot=0.0):
    """Hand roller for pressing the cold-seal card onto the blisters: black rubber drum, red handle."""
    red = principled('Roller red', (0.75, 0.05, 0.05), rough=0.3, coat=0.4)
    drum = lathe('Roller drum', [(0.004, 0), (0.019, 0), (0.02, 0.002), (0.02, 0.098), (0.019, 0.1), (0.004, 0.1)],
                 principled('Rubber', (0.03, 0.03, 0.03), rough=0.7), seg=48)
    drum.rotation_euler = (0, math.pi / 2, 0)
    root = bpy.data.objects.new('Seal roller', None); bpy.context.scene.collection.objects.link(root); drum.parent = root
    drum.location = (-0.05, 0, 0.02)
    for x in (-0.054, 0.054):
        a = rounded_box('Roller arm', 0.006, 0.05, 0.012, red, 0.002); a.location = (x, -0.02, 0.014); a.rotation_euler.x = 0.5; a.parent = root
    h = lathe('Roller handle', [(0, 0), (0.012, 0), (0.014, 0.03), (0.013, 0.1), (0.011, 0.11), (0, 0.11)], red, seg=32)
    h.rotation_euler.x = math.radians(-70); h.location = (0, -0.04, 0.03); h.parent = root
    root.location = loc; root.rotation_euler.z = rot
    return root

def blister_machine(loc=(0, 0, 0), rot=0.0):
    """An unbranded blister-card filling machine modelled on the SynMed Ultra (his reference photo): a warm
    grey cabinet with two glass tiers, each closed by double glass doors with blue light along their edges,
    a robot gantry and card trays inside, a solid base with key locks, a vented top with a blank name plate,
    and a side tower with orange buttons over three card slots. The tower stands on the right so the
    machine can sit at the end of a counter on its left."""
    grey = imperfect(principled('Machine grey', (0.6, 0.59, 0.56), rough=0.38, coat=0.25), 'satin')
    trim = principled('Machine trim', (0.42, 0.42, 0.41), rough=0.4, metallic=0.3)
    dark = principled('Machine dark', (0.06, 0.065, 0.07), rough=0.45)
    glass = principled('Machine glass', (0.95, 0.97, 0.99), rough=0.0, transmission=1.0, ior=1.05)    # thin door glass: see straight through
    inner = principled('Machine interior', (0.8, 0.82, 0.84), rough=0.45)
    whitep = principled('Card tray white', (0.93, 0.93, 0.92), rough=0.35)
    blue = principled('Edge LED', (0.3, 0.5, 1.0), rough=0.5)
    blue.node_tree.nodes['Principled BSDF'].inputs['Emission Color'].default_value = (0.35, 0.55, 1.0, 1)
    blue.node_tree.nodes['Principled BSDF'].inputs['Emission Strength'].default_value = 14
    cool = principled('Interior light', (0.9, 0.95, 1.0), rough=0.5)
    cool.node_tree.nodes['Principled BSDF'].inputs['Emission Color'].default_value = (0.2, 0.5, 1.0, 1)      # neon blue inside the tiers (31 Oct)
    cool.node_tree.nodes['Principled BSDF'].inputs['Emission Strength'].default_value = 30
    W, D, H = 1.15, 0.9, 2.0
    root = None
    def part(n, s, l, m, bw=0.002):          # crisp: 2 mm chamfers, as on sheet-metal and moulded panels
        o = rounded_box(n, *s, m, bw); o.location = l; o.parent = root; return o
    root = rounded_box('Blister machine', W, 0.04, H, grey, 0.003)               # the back panel; the cabinet is built hollow so the tiers show
    root.data.transform(Matrix.Translation((0, D / 2 - 0.02, 0)))
    for x in (-W / 2 + 0.015, W / 2 - 0.015):
        part('Side wall', (0.03, D - 0.1, H), (x, 0.05, 0), grey, 0.003)   # set back behind the front posts: coplanar fronts baked black
    part('Base block', (W, D - 0.1, 0.56), (0, 0.05, 0), grey, 0.003); part('Top block', (W, D - 0.1, 0.18), (0, 0.05, 1.82), grey, 0.003)
    part('Mid block', (W, D - 0.1, 0.07), (0, 0.05, 1.16), grey, 0.003)
    fy = -D / 2 + 0.05
    # solid base with a seam and two key locks; vented top band with a blank plate
    part('Base panel', (W, 0.1, 0.56), (0, fy, 0.0), grey, 0.003)
    part('Base seam', (W - 0.06, 0.004, 0.004), (0, -D / 2 - 0.0005, 0.42), trim, 0.001)
    for x in (-W / 2 + 0.12, W / 2 - 0.12):
        part('Key lock', (0.022, 0.006, 0.022), (x, -D / 2 - 0.002, 0.3), trim, 0.008)
    part('Top band', (W, 0.1, 0.18), (0, fy, 1.82), grey, 0.003)
    part('Name plate', (0.42, 0.004, 0.07), (-0.18, -D / 2 - 0.001, 1.88), principled('Plate', (0.75, 0.75, 0.73), rough=0.3), 0.003)
    for i in range(6):
        part('Vent', (0.012, 0.004, 0.09), (W / 2 - 0.2 + i * 0.025, -D / 2 - 0.001, 1.86), dark, 0.002)
    part('Mid band', (W, 0.1, 0.07), (0, fy, 1.16), grey, 0.003)
    for x in (-W / 2 + 0.03, W / 2 - 0.03):
        part('Frame post', (0.06, 0.1, 1.26), (x, fy, 0.56), grey, 0.003)
    # the two tiers
    for z0, z1 in ((0.56, 1.16), (1.23, 1.82)):
        h = z1 - z0; iw = W - 0.12
        part('Tier back', (iw, 0.02, h), (0, D / 2 - 0.12, z0), inner)
        part('Tier floor', (iw, D - 0.2, 0.02), (0, 0.0, z0), inner)
        part('Tier light', (iw - 0.06, 0.03, 0.01), (0, -0.1, z1 - 0.02), cool, 0.003)
        part('Tier light back', (iw - 0.06, 0.01, 0.012), (0, D / 2 - 0.135, z1 - 0.05), cool, 0.002)   # a second strip along the back wall
        # robot gantry: a rail across the top, a carriage, an arm down to the pick head
        part('Gantry rail', (iw - 0.04, 0.05, 0.04), (0, 0.05, z1 - 0.08), trim, 0.006)
        cx = rnd_x = (-0.15 if z0 < 1 else 0.2)
        part('Carriage', (0.12, 0.09, 0.08), (cx, 0.05, z1 - 0.13), dark, 0.003)
        part('Arm', (0.03, 0.03, h * 0.45), (cx, 0.03, z1 - 0.13 - h * 0.45), trim, 0.006)
        part('Pick head', (0.06, 0.05, 0.03), (cx, 0.03, z1 - 0.16 - h * 0.45), whitep, 0.006)
        # card trays on the floor, cards in them, a rack of canisters at the back
        for i in range(3):
            tx = -0.33 + i * 0.33
            part('Card tray', (0.27, 0.34, 0.035), (tx, -0.05, z0 + 0.02), whitep, 0.006)
            part('Card', (0.23, 0.3, 0.004), (tx, -0.05, z0 + 0.056), image_material('Card pax_grid_jumbo.png', os.path.join(TEX, 'pax_grid_jumbo.png'), rough=0.45), 0.001)
        for c in range(13):
            part('Canister', (0.055, 0.06, 0.09), (-0.48 + c * 0.08, D / 2 - 0.17, z0 + 0.12), principled('Canister', (0.85, 0.88, 0.92), rough=0.2, transmission=0.5, ior=1.4), 0.006)
        # double glass doors: frames, glass, handles meeting in the middle, blue light down the outer edges
        for side in (-1, 1):
            dx = side * iw / 4
            part('Door glass', (iw / 2 - 0.01, 0.008, h - 0.03), (dx, -D / 2 + 0.006, z0 + 0.015), glass, 0.004)
            for zz in (z0 + 0.012, z1 - 0.022):
                part('Door rail', (iw / 2 - 0.01, 0.014, 0.012), (dx, -D / 2 + 0.002, zz), trim, 0.003)
            part('Door stile', (0.014, 0.014, h - 0.03), (side * 0.008, -D / 2 + 0.002, z0 + 0.015), trim, 0.003)
            part('Handle', (0.012, 0.025, 0.1), (side * 0.03, -D / 2 - 0.02, z0 + h / 2 - 0.05), trim, 0.005)
            part('Edge light', (0.006, 0.006, h - 0.06), (side * (iw / 2 - 0.005), -D / 2 + 0.012, z0 + 0.03), blue, 0.002)
        part('Door latch', (0.05, 0.02, 0.025), (0, -D / 2 - 0.006, z0 - 0.0), whitep, 0.006)
    # the side tower, on the right: orange buttons over three card slots, a tall dark window on its side
    TW, TD, TH = 0.42, 0.72, 1.78
    tx0 = W / 2 + TW / 2 - 0.01
    part('Side tower', (TW, TD, TH), (tx0, 0.1, 0.0), grey, 0.003)
    for i in range(3):
        m = principled('Button orange', (1.0, 0.45, 0.08), rough=0.3)
        m.node_tree.nodes['Principled BSDF'].inputs['Emission Color'].default_value = (1.0, 0.45, 0.08, 1)
        m.node_tree.nodes['Principled BSDF'].inputs['Emission Strength'].default_value = 2
        part('Button', (0.028, 0.012, 0.028), (tx0 - 0.07 + i * 0.07, 0.1 - TD / 2 - 0.004, 1.38), m, 0.01)
    for k, z in enumerate((1.12, 0.88, 0.64)):
        part('Card slot', (0.2, 0.012, 0.13), (tx0, 0.1 - TD / 2 - 0.003, z), dark, 0.004)
        for j in range(4):
            part('Slot card', (0.17, 0.02, 0.006), (tx0 + 0.005, 0.1 - TD / 2 - 0.005, z + 0.025 + j * 0.022), whitep, 0.001)
    part('Tower window', (0.006, 0.18, 1.1), (tx0 + TW / 2 + 0.002, 0.0, 0.45), principled('Smoke', (0.12, 0.14, 0.17), rough=0.05, transmission=0.3), 0.003)
    root.location = loc; root.rotation_euler.z = rot
    return root
