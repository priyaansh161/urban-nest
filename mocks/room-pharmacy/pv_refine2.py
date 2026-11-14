# Realism pass, batch 2 (31 Oct 2026): the counting tray (his reference photo), weighing boats and prescription
# baskets rebuilt to their real shapes. The first versions read as "a square and a circle" and toy boxes.
import bpy, bmesh, math, os, random
from pv_lib import principled, image_material, lathe, _bx, TEX, imperfect

def tub(name, top, bottom, h, m, wall=0.0012, corner=0.004, z0=0.0):
    """An open tapered tub (weighing boat, Rx basket): rectangular bottom, wider top, thin moulded walls, rounded
    vertical corners. top/bottom are (w, d); the open side faces up."""
    bm = bmesh.new()
    (tw, td), (bw, bd) = top, bottom
    B = [bm.verts.new(p) for p in [(-bw / 2, -bd / 2, z0), (bw / 2, -bd / 2, z0), (bw / 2, bd / 2, z0), (-bw / 2, bd / 2, z0)]]
    T = [bm.verts.new(p) for p in [(-tw / 2, -td / 2, z0 + h), (tw / 2, -td / 2, z0 + h), (tw / 2, td / 2, z0 + h), (-tw / 2, td / 2, z0 + h)]]
    bm.faces.new(list(reversed(B)))
    for i in range(4):
        j = (i + 1) % 4; bm.faces.new((B[i], B[j], T[j], T[i]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(name, me); bpy.context.scene.collection.objects.link(o); me.materials.append(m)
    bv = o.modifiers.new('corners', 'BEVEL'); bv.width = corner; bv.segments = 5; bv.limit_method = 'ANGLE'; bv.angle_limit = math.radians(50)
    s = o.modifiers.new('wall', 'SOLIDIFY'); s.thickness = wall; s.offset = -1          # inwards: the floor thickens up, never into the counter
    return o

def weighing_boats(loc=(0, 0, 0), rot=0.0, n=3, tablets=0):
    """Anti-static weighing boats as they really are: square, shallow, sloped sides (8 cm across the top, 5.5 cm
    across the bottom, 2.4 cm deep), thin white plastic, nested in a stack."""
    root = bpy.data.objects.new('Weighing boats', None); bpy.context.scene.collection.objects.link(root)
    white = principled('Boat white', (0.95, 0.95, 0.94), rough=0.3, sss=0.25)
    for i in range(n):
        tub('Weighing boat', (0.08, 0.08), (0.055, 0.055), 0.024, white, wall=0.0006, corner=0.003, z0=i * 0.004).parent = root
    rnd = random.Random(5); tab = principled('Tablet white', (0.93, 0.93, 0.9), rough=0.55)
    for k in range(tablets):
        lathe('Tablet', [(0, 0), (0.0035, 0), (0.0042, 0.0007), (0.0042, 0.002), (0.0035, 0.0028), (0, 0.003)], tab, seg=32,
              loc=(rnd.uniform(-0.014, 0.014), rnd.uniform(-0.014, 0.014), (n - 1) * 0.004 + 0.0008)).parent = root
    root.location = loc; root.rotation_euler.z = rot
    return root

def rx_baskets(loc=(0, 0, 0), rot=0.0):
    """Prescription baskets as pharmacies use them: tapered moulded tubs (30 x 20 cm, 10 cm deep) in muted colours,
    a label card at the front of each, one nested on another; a bagged order waiting in the front one."""
    root = bpy.data.objects.new('Rx baskets', None); bpy.context.scene.collection.objects.link(root)
    slate = imperfect(principled('Basket slate blue', (0.24, 0.36, 0.52), rough=0.42), 'satin')
    sage = imperfect(principled('Basket sage', (0.36, 0.5, 0.4), rough=0.42), 'satin')
    lab = image_material('Order label', os.path.join(TEX, 'receipt.png'), rough=0.5)
    for y, z, m in ((-0.11, 0.0, slate), (0.12, 0.0, sage), (0.12, 0.03, slate)):
        t = tub('Rx basket', (0.3, 0.2), (0.27, 0.17), 0.1, m, wall=0.002, corner=0.012, z0=z); t.location = (0, y, 0); t.parent = root
        _bx('Basket label', (0, y - 0.1 - 0.0012, z + 0.07), (0.09, 0.0008, 0.035), lab, bw=0.0).parent = root
    bag = _bx('Order bag', (-0.04, -0.11, 0.08), (0.12, 0.08, 0.15), principled('Kraft bag', (0.72, 0.56, 0.38), rough=0.85), bw=0.006)
    bag.rotation_euler.z = 0.15; bag.parent = root
    root.location = loc; root.rotation_euler.z = rot
    return root

def counting_tray(loc=(0, 0, 0), rot=0.0):
    """The blue pill counting tray from his reference photo: a shallow tray with low walls; along the left end a
    channel the counted pills are swept into; the long blue spatula lying flat on the counter in front of it.
    (31 Oct: the clear lid and the pour spout read as stray shapes floating outside the tray, so they are gone.)"""
    blue = imperfect(principled('Counting tray blue', (0.015, 0.06, 0.5), rough=0.3, coat=0.25), 'satin')
    root = bpy.data.objects.new('Counting tray', None); bpy.context.scene.collection.objects.link(root)
    W, D = 0.23, 0.13
    tub('Tray body', (W, D), (W - 0.01, D - 0.01), 0.014, blue, wall=0.0022, corner=0.008).parent = root
    _bx('Channel wall', (-W / 2 + 0.042, 0, 0.0075), (0.0022, D - 0.016, 0.0105), blue, bw=0.0007).parent = root
    # spatula: flat blade with a raised spine and a handle, resting on the counter just clear of the tray's front
    sp = _bx('Spatula', (0.0, 0.0, 0.0008), (0.15, 0.022, 0.0016), blue, bw=0.0006)
    _bx('Spatula spine', (-0.005, 0.0, 0.0045), (0.13, 0.004, 0.006), blue, bw=0.001).parent = sp
    _bx('Spatula handle', (0.11, 0.0, 0.003), (0.07, 0.012, 0.006), blue, bw=0.002).parent = sp
    sp.location = (0.0, -D / 2 - 0.028, 0.0); sp.rotation_euler.z = 0.06; sp.parent = root
    root.location = loc; root.rotation_euler.z = rot
    return root
