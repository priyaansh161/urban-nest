# Staging for the PharmVials sample counter: the small things that make it a working pharmacy, several of
# them PharmVials' own catalogue items (digital lab scale, weighing boats, nitrile gloves, oral syringes,
# methadone cups) and the rest everyday counter life (pen cup, sticky notes, hand sanitizer, a plant).
import bpy, math, os, random
from mathutils import Vector, Matrix
from pv_lib import principled, image_material, lathe, _bx, TEX

def _emit(name, color, strength):
    m = principled(name, color, rough=0.4)
    b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Emission Color'].default_value = (*color, 1); b.inputs['Emission Strength'].default_value = strength
    return m

def _root(name, loc, rot):
    r = bpy.data.objects.new(name, None); bpy.context.scene.collection.objects.link(r)
    return r

def _done(r, loc, rot):
    r.location = loc; r.rotation_euler.z = rot; return r

def digital_scale(loc=(0, 0, 0), rot=0.0, boat=True):
    """PharmVials' digital laboratory scale (310 g): black body, steel pan, lit LCD reading a weight,
    with a white weighing boat on the pan."""
    r = _root('Digital scale', loc, rot)
    _bx('Scale body', (0, 0, 0.012), (0.1, 0.13, 0.024), principled('Scale black', (0.03, 0.03, 0.035), rough=0.35, coat=0.3), bw=0.008, seg=4).parent = r
    _bx('Scale pan', (0, 0.018, 0.0255), (0.075, 0.075, 0.003), principled('Pan steel', (0.82, 0.82, 0.82), rough=0.18, metallic=1.0), bw=0.0015).parent = r
    _bx('LCD', (0, -0.045, 0.0242), (0.05, 0.018, 0.0008), image_material('LCD reading', os.path.join(TEX, 'lcd.png'), rough=0.2), bw=0.0003).parent = r
    for i, x in enumerate((-0.03, 0.03)):
        _bx('Scale key', (x, -0.052, 0.0245), (0.012, 0.007, 0.0015), principled('Key grey', (0.3, 0.3, 0.32), rough=0.4), bw=0.0007).parent = r
    if boat:
        b = weighing_boats(loc=(0, 0.018, 0.027), n=1, tablets=6)
        b.parent = r
    return _done(r, loc, rot)

def weighing_boats(loc=(0, 0, 0), rot=0.0, n=4, tablets=0):
    """Anti-static weighing boats: shallow square white dishes (PharmVials sells them in three sizes), stacked."""
    r = _root('Weighing boats', loc, rot)
    white = principled('Boat white', (0.95, 0.95, 0.94), rough=0.3, sss=0.2)
    for i in range(n):
        _bx('Weighing boat', (0, 0, i * 0.0035 + 0.0006), (0.06, 0.06, 0.0012), white, bw=0.005, seg=3).parent = r
        for x, y in ((-0.029, 0), (0.029, 0), (0, -0.029), (0, 0.029)):
            w = _bx('Boat wall', (x, y, i * 0.0035 + 0.005), (0.004 if x else 0.06, 0.06 if x else 0.004, 0.009), white, bw=0.0015)
            w.rotation_euler = ((0.5 if y > 0 else -0.5) if y else 0, (-0.5 if x > 0 else 0.5) if x else 0, 0); w.parent = r
    rnd = random.Random(5); tab = principled('Tablet white', (0.93, 0.93, 0.9), rough=0.55)
    for k in range(tablets):
        t = lathe('Tablet', [(0, 0), (0.0035, 0), (0.0042, 0.0007), (0.0042, 0.002), (0.0035, 0.0028), (0, 0.003)], tab, seg=32,
                  loc=(rnd.uniform(-0.016, 0.016), rnd.uniform(-0.016, 0.016), (n - 1) * 0.0035 + 0.0013))
        t.parent = r
    return _done(r, loc, rot)

def gloves_box(loc=(0, 0, 0), rot=0.0):
    """A box of nitrile examination gloves (PharmVials stocks small, medium, large), one glove pulled up."""
    r = _root('Gloves box', loc, rot)
    _bx('Gloves box', (0, 0, 0.045), (0.24, 0.125, 0.09), image_material('Gloves box', os.path.join(TEX, 'gloves_box.png'), rough=0.55), bw=0.002).parent = r
    nitrile = principled('Nitrile blue', (0.25, 0.45, 0.95), rough=0.45, sss=0.2)
    g = lathe('Glove', [(0.0, 0.0), (0.03, 0.0), (0.028, 0.03), (0.018, 0.06), (0.006, 0.07), (0.0, 0.072)], nitrile, seg=24)
    g.scale = (1, 0.35, 1); g.location = (0, 0, 0.088); g.rotation_euler = (0.2, 0.3, 0); g.parent = r
    return _done(r, loc, rot)

def syringe(name, length=0.12, r_=0.006):
    clear = principled('Syringe barrel', (0.95, 0.96, 0.98), rough=0.08, transmission=0.9, ior=1.45)
    purple = principled('Plunger purple', (0.45, 0.2, 0.65), rough=0.4)
    o = lathe(name, [(r_ - 0.0006, 0), (r_, 0), (r_, length * 0.7), (r_ + 0.004, length * 0.7), (r_ + 0.004, length * 0.71), (r_ - 0.0006, length * 0.71)], clear, seg=32)
    p = lathe(name + ' plunger', [(0, length * 0.25), (r_ - 0.0008, length * 0.25), (r_ - 0.0008, length * 0.98), (r_ + 0.002, length * 0.98), (r_ + 0.002, length), (0, length)], purple, seg=24)
    p.parent = o
    tip = lathe(name + ' tip', [(0, -0.01), (0.0018, -0.01), (0.0022, 0), (0, 0)], clear, seg=16); tip.parent = o
    return o

def syringes_in_cup(loc=(0, 0, 0), rot=0.0):
    """A clear methadone cup holding PharmVials' oral syringes, plungers up."""
    r = _root('Syringe cup', loc, rot)
    cup = lathe('Methadone cup', [(0.0, 0.0), (0.02, 0.0), (0.026, 0.06), (0.0255, 0.06), (0.0195, 0.0015), (0.0, 0.0015)],
                principled('Cup PP', (0.96, 0.97, 0.98), rough=0.12, transmission=0.85, ior=1.4), seg=48)
    cup.parent = r
    for i, (x, y, a) in enumerate([(-0.007, 0.004, 0.08), (0.007, 0.0, -0.06), (0.0, -0.008, 0.02), (0.004, 0.009, -0.1)]):
        s = syringe('Oral syringe', 0.11 + 0.012 * (i % 2), 0.005 + 0.0015 * (i % 2)); s.location = (x, y, 0.012); s.rotation_euler = (a, -a, 0); s.parent = r
    return _done(r, loc, rot)

def pen_cup(loc=(0, 0, 0), rot=0.0):
    r = _root('Pen cup', loc, rot)
    lathe('Pen cup', [(0.0, 0.0), (0.035, 0.0), (0.035, 0.095), (0.032, 0.095), (0.032, 0.004), (0.0, 0.004)],
          principled('Cup matte', (0.85, 0.84, 0.8), rough=0.7), seg=48).parent = r
    cols = [(0.05, 0.1, 0.4), (0.05, 0.05, 0.05), (0.7, 0.08, 0.08), (0.05, 0.1, 0.4)]
    for i, c in enumerate(cols):
        p = lathe('Pen', [(0, 0), (0.0045, 0), (0.0045, 0.14), (0, 0.145)], principled('Pen %d' % i, c, rough=0.3), seg=16)
        a = i * 1.6; p.location = (0.012 * math.cos(a), 0.012 * math.sin(a), 0.004); p.rotation_euler = (0.18 * math.sin(a), -0.18 * math.cos(a), 0); p.parent = r
    return _done(r, loc, rot)

def sticky_notes(loc=(0, 0, 0), rot=0.0):
    r = _root('Sticky notes', loc, rot)
    _bx('Sticky notes', (0, 0, 0.006), (0.076, 0.076, 0.012), principled('Note yellow', (0.98, 0.88, 0.35), rough=0.7), bw=0.0005).parent = r
    top = _bx('Top note', (0.003, 0.002, 0.0122), (0.076, 0.076, 0.0002), image_material('Note', os.path.join(TEX, 'note.png'), rough=0.7), bw=0.0)
    top.rotation_euler.z = 0.06; top.parent = r
    return _done(r, loc, rot)

def sanitizer(loc=(0, 0, 0), rot=0.0):
    r = _root('Sanitizer', loc, rot)
    lathe('Sanitizer bottle', [(0, 0), (0.034, 0), (0.036, 0.004), (0.036, 0.15), (0.02, 0.17), (0.012, 0.175), (0, 0.175)],
          principled('Gel', (0.75, 0.88, 0.95), rough=0.05, transmission=0.95, ior=1.35), seg=48).parent = r
    lathe('Pump', [(0, 0.175), (0.012, 0.175), (0.012, 0.2), (0.004, 0.2), (0.004, 0.215), (0, 0.215)], principled('Pump white', (0.95, 0.95, 0.95), rough=0.3), seg=24).parent = r
    _bx('Pump nozzle', (0.014, 0, 0.212), (0.03, 0.008, 0.007), principled('Pump white', (0.95, 0.95, 0.95), rough=0.3), bw=0.002).parent = r
    _bx('Sanitizer label', (0, -0.0362, 0.07), (0.045, 0.0004, 0.06), image_material('Sanitizer label', os.path.join(TEX, 'sanitizer.png'), rough=0.5), bw=0.0).parent = r
    return _done(r, loc, rot)

def plant(loc=(0, 0, 0), rot=0.0, seed=3):
    """A small potted pothos: a white ceramic pot with trailing heart-shaped leaves."""
    r = _root('Plant', loc, rot)
    lathe('Pot', [(0, 0), (0.05, 0), (0.06, 0.1), (0.056, 0.1), (0.047, 0.006), (0, 0.006)], principled('Ceramic', (0.93, 0.92, 0.89), rough=0.25, coat=0.4), seg=48).parent = r
    lathe('Soil', [(0, 0.088), (0.056, 0.088), (0.056, 0.092), (0, 0.092)], principled('Soil', (0.12, 0.08, 0.05), rough=0.95), seg=32).parent = r
    leaf = principled('Leaf', (0.12, 0.42, 0.12), rough=0.35, sss=0.15)
    rnd = random.Random(seed)
    for i in range(22):
        bpy.ops.mesh.primitive_uv_sphere_add(segments=12, ring_count=8, radius=0.022)
        l = bpy.context.active_object; l.name = 'Leaf'; l.scale = (1, 0.7, 0.12); l.data.materials.append(leaf)
        for f in l.data.polygons: f.use_smooth = True
        a = rnd.uniform(0, 6.28); d = rnd.uniform(0.0, 0.09); h = 0.1 + rnd.uniform(0.0, 0.08) - (d * 0.9 if d > 0.06 else 0)
        l.location = (d * math.cos(a), d * math.sin(a), h); l.rotation_euler = (rnd.uniform(-0.6, 0.6), rnd.uniform(-0.6, 0.6), a); l.parent = r
    return _done(r, loc, rot)

def computer(loc=(0, 0, 0), rot=0.0):
    """The dispensing computer: a slim monitor on a stand (the pharmacy software on screen), keyboard, mouse."""
    r = _root('Computer', loc, rot)
    dark = principled('Monitor black', (0.03, 0.03, 0.035), rough=0.35)
    _bx('Monitor stand', (0, 0.06, 0.004), (0.2, 0.15, 0.008), dark, bw=0.004).parent = r
    _bx('Monitor neck', (0, 0.07, 0.11), (0.04, 0.02, 0.21), dark, bw=0.006).parent = r
    mon = _bx('Monitor', (0, 0.045, 0.3), (0.54, 0.022, 0.32), dark, bw=0.004); mon.parent = r
    scr = _emit('Rx software screen', (0.82, 0.88, 0.93), 1.2)
    _bx('Monitor screen', (0, 0.0335, 0.305), (0.51, 0.001, 0.29), image_material('Rx screen', os.path.join(TEX, 'rx_screen.png'), rough=0.2), bw=0.0).parent = r
    _bx('Keyboard', (0, -0.16, 0.009), (0.44, 0.14, 0.018), principled('Keyboard', (0.12, 0.12, 0.13), rough=0.5), bw=0.004).parent = r
    _bx('Keys', (0, -0.16, 0.0185), (0.41, 0.115, 0.002), principled('Keys', (0.2, 0.2, 0.21), rough=0.6), bw=0.0008).parent = r
    _bx('Mouse', (0.29, -0.15, 0.012), (0.065, 0.11, 0.024), principled('Mouse', (0.12, 0.12, 0.13), rough=0.4), bw=0.011, seg=5).parent = r
    return _done(r, loc, rot)

def rx_baskets(loc=(0, 0, 0), rot=0.0):
    """Colour-coded prescription baskets: each order waits in its own tub; a few hold bagged and vial orders."""
    r = _root('Rx baskets', loc, rot)
    cols = [('Basket blue', (0.1, 0.35, 0.8)), ('Basket green', (0.2, 0.6, 0.3)), ('Basket red', (0.8, 0.15, 0.12))]
    for i, (n, c) in enumerate(cols):
        m = principled(n, c, rough=0.35)
        y = -0.12 + i * 0.12; z = 0.0
        _bx(n + ' floor', (0, y, z + 0.002), (0.3, 0.2, 0.004), m, bw=0.004).parent = r
        for x, yy, sx, sy in ((-0.148, y, 0.005, 0.2), (0.148, y, 0.005, 0.2), (0, y - 0.098, 0.3, 0.005), (0, y + 0.098, 0.3, 0.005)):
            _bx(n + ' side', (x, yy, z + 0.05), (sx, sy, 0.1), m, bw=0.002).parent = r
        if i < 2:
            _bx('Order bag', (-0.05, y, 0.075), (0.12, 0.09, 0.14), principled('Kraft bag', (0.72, 0.56, 0.38), rough=0.8), bw=0.004).parent = r
            _bx('Order label', (-0.05, y - 0.0455, 0.1), (0.08, 0.001, 0.04), image_material('Order label', os.path.join(TEX, 'receipt.png'), rough=0.5), bw=0.0).parent = r
    return _done(r, loc, rot)

def wall_clock(loc=(0, 0, 0), rot=0.0):
    """A plain round wall clock (face toward -y before rotation): white face, black rim, hour ticks, hands."""
    r = _root('Wall clock', loc, rot)
    black = principled('Clock black', (0.03, 0.03, 0.03), rough=0.4)
    rim = lathe('Clock rim', [(0.0, 0.0), (0.16, 0.0), (0.16, 0.04), (0.15, 0.04), (0.15, 0.005), (0.0, 0.005)], black, seg=64)
    face = lathe('Clock face', [(0.0, 0.03), (0.15, 0.03), (0.15, 0.031), (0.0, 0.031)], principled('Clock face', (0.95, 0.95, 0.93), rough=0.5), seg=64)
    for o in (rim, face): o.rotation_euler.x = math.pi / 2; o.location.y = 0.04; o.parent = r
    for k in range(12):
        a = k * math.pi / 6; L = 0.024 if k % 3 == 0 else 0.012
        t = _bx('Tick', (0.13 * math.sin(a), -0.002, 0.13 * math.cos(a)), (0.004, 0.002, L), black, bw=0.0); t.rotation_euler.y = a; t.parent = r
    for n, L, w, a in (('Hour hand', 0.07, 0.007, 1.9), ('Minute hand', 0.11, 0.005, -0.6)):
        h = _bx(n, (0, -0.004, 0), (w, 0.002, L), black, bw=0.0, off=(0, 0, L / 2)); h.rotation_euler.y = a; h.parent = r
    return _done(r, loc, rot)
