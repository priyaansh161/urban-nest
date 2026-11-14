# Photo-dressed products (31 Oct 2026). His idea, the way Meshy does it: build the box to the product's real
# dimensions, then paste a straightened photo of the real thing on each face (rectify.cjs) instead of modelling
# every button, slot and seam. Photos are free-licence, see refs/photo-tex/LICENCES.txt.
import bpy, bmesh, math, os
from pv_lib import principled, image_material, lathe, _bx, TEX, imperfect

def photo_face(name, img, corners, uv=((0, 0), (1, 0), (1, 1), (0, 1)), rough=0.4):
    """A one-sided quad carrying a photo. corners: bottom-left, bottom-right, top-right, top-left (outward face)."""
    me = bpy.data.meshes.new(name); bm = bmesh.new()
    f = bm.faces.new([bm.verts.new(c) for c in corners])
    lay = bm.loops.layers.uv.new('UVMap')
    for loop, t in zip(f.loops, uv): loop[lay].uv = t
    bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(name, me); bpy.context.scene.collection.objects.link(o)
    me.materials.append(image_material(name + ' photo', os.path.join(TEX, img), rough=rough))
    return o

def thermal_printer(loc=(0, 0, 0), rot=0.0):
    """A 4-inch direct-thermal label printer (Wagtail CT200 photo): square white body with rounded upright
    corners, a gloss-black top lid, the exit slot low on the front. 21 x 25 x 15.5 cm.
    Returns (body, exit point (y, z) in its own space) so the printed label runs out of the slot."""
    W, D, H, r = 0.21, 0.25, 0.155, 0.012
    white = imperfect(principled('Printer white', (0.86, 0.86, 0.87), rough=0.35, coat=0.2), 'satin')
    body = bpy.data.objects.new('Thermal printer', None); bpy.context.scene.collection.objects.link(body)   # origin on the counter
    _bx('Printer body', (0, 0, H / 2), (W, D, H), white, bw=r, seg=6).parent = body
    e = 0.0004                                                   # photos float just off the faces
    hw, hd = W / 2 - r * 0.6, D / 2 - r * 0.6
    photo_face('Printer front', 'printer_front.png',
               [(-hw, -D / 2 - e, 0.0), (hw, -D / 2 - e, 0.0), (hw, -D / 2 - e, H - 0.004), (-hw, -D / 2 - e, H - 0.004)]).parent = body
    side = [(0, 0.05), (1, 0.05), (1, 1), (0, 1)]               # trims the photo's floor shadow off the bottom
    photo_face('Printer side R', 'printer_side_c.png',
               [(W / 2 + e, -hd, 0.0), (W / 2 + e, hd, 0.0), (W / 2 + e, hd, H - 0.004), (W / 2 + e, -hd, H - 0.004)], uv=side).parent = body
    photo_face('Printer side L', 'printer_side_c.png',          # mirrored: the latch stays at the front
               [(-W / 2 - e, hd, 0.0), (-W / 2 - e, -hd, 0.0), (-W / 2 - e, -hd, H - 0.004), (-W / 2 - e, hd, H - 0.004)],
               uv=[(1, 0.05), (0, 0.05), (0, 1), (1, 1)]).parent = body
    lid = principled('Printer lid gloss', (0.012, 0.012, 0.014), rough=0.08, coat=1.0)
    _bx('Printer lid', (0, 0.006, H + 0.001), (W - 0.014, D - 0.026, 0.003), lid, bw=0.004).parent = body
    lathe('Power button', [(0, 0), (0.006, 0), (0.0062, 0.0015), (0, 0.0019)],
          principled('Button orange', (0.95, 0.32, 0.04), rough=0.35), seg=48, loc=(-W / 2 + 0.024, -D / 2 + 0.03, H + 0.0025)).parent = body
    led = principled('LED green', (0.2, 1.0, 0.4)); led.node_tree.nodes['Principled BSDF'].inputs['Emission Color'].default_value = (0.2, 1, 0.4, 1)
    led.node_tree.nodes['Principled BSDF'].inputs['Emission Strength'].default_value = 4
    _bx('Status LED', (-W / 2 + 0.024, -D / 2 + 0.042, H + 0.0026), (0.0016, 0.0016, 0.0004), led, bw=0).parent = body
    for x in (-W / 2 + 0.02, W / 2 - 0.02):
        for y in (-D / 2 + 0.02, D / 2 - 0.02):
            _bx('Printer foot', (x, y, -0.002), (0.016, 0.016, 0.004), principled('Rubber', (0.02, 0.02, 0.02), rough=0.8), bw=0.002).parent = body
    body.location = (loc[0], loc[1], loc[2] + 0.004); body.rotation_euler.z = rot
    return body, (-D / 2 - e, 0.004 + H * (1 - 0.664))

def digital_scale(loc=(0, 0, 0), rot=0.0, boat=True):
    """A pan-top laboratory balance (Kern photo for the key panel): cream body, flat back deck, the display and
    keys on a sloped front panel, a square brushed-steel pan. 20 x 26 cm, 13 cm pan."""
    from pv_refine2 import weighing_boats
    W = 0.2
    cream = imperfect(principled('Scale cream', (0.78, 0.75, 0.64), rough=0.42), 'satin')
    # side profile (y, z): flat deck at the back, sloping key panel at the front, extruded across the width
    prof = [(0.13, 0.0), (0.13, 0.058), (-0.03, 0.062), (-0.125, 0.032), (-0.13, 0.026), (-0.13, 0.0)]
    bm = bmesh.new()
    L = [bm.verts.new((-W / 2, y, z)) for y, z in prof]; R = [bm.verts.new((W / 2, y, z)) for y, z in prof]
    bm.faces.new(list(reversed(L))); bm.faces.new(R)
    for i in range(len(prof)):
        j = (i + 1) % len(prof); bm.faces.new((L[i], L[j], R[j], R[i]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new('Digital scale'); bm.to_mesh(me); bm.free()
    body = bpy.data.objects.new('Digital scale', me); bpy.context.scene.collection.objects.link(body); me.materials.append(cream)
    bv = body.modifiers.new('b', 'BEVEL'); bv.width = 0.004; bv.segments = 4; bv.harden_normals = True
    for p in me.polygons: p.use_smooth = True
    # the key panel photo on the slope, inset from the edges
    (y0, z0), (y1, z1) = (-0.122, 0.0335), (-0.034, 0.0612)
    n = math.hypot(y1 - y0, z1 - z0); ny, nz = (z1 - z0) / n * 0.0004, -(y1 - y0) / n * 0.0004   # a hair above the slope
    ny, nz = -abs(ny), abs(nz)
    hw = 0.092
    photo_face('Scale panel', 'scale_panel.png',
               [(-hw, y0 + ny, z0 + nz), (hw, y0 + ny, z0 + nz), (hw, y1 + ny, z1 + nz), (-hw, y1 + ny, z1 + nz)], rough=0.3).parent = body
    # brushed steel pan on a short post
    steel = imperfect(principled('Pan steel', (0.9, 0.9, 0.9), rough=0.38, metallic=1.0), 'satin')   # brushed: at 0.22 it mirrored the dark room
    _bx('Pan post', (0, 0.05, 0.064), (0.03, 0.03, 0.008), principled('Post dark', (0.05, 0.05, 0.05), rough=0.5), bw=0.002).parent = body
    pan = _bx('Scale pan', (0, 0.05, 0.0705), (0.13, 0.13, 0.005), steel, bw=0.004, seg=4); pan.parent = body
    for x in (-W / 2 + 0.025, W / 2 - 0.025):
        for y in (-0.1, 0.1):
            lathe('Scale foot', [(0, 0), (0.008, 0), (0.008, 0.004), (0, 0.004)], principled('Rubber', (0.02, 0.02, 0.02), rough=0.8),
                  seg=24, loc=(x, y, -0.004)).parent = body
    if boat:
        b = weighing_boats(loc=(0, 0.05, 0.0736), n=1, tablets=6); b.parent = body
    body.location = (loc[0], loc[1], loc[2] + 0.004); body.rotation_euler.z = rot
    return body
