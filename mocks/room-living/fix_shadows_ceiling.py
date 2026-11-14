# No re-bake: (1) paint the baked furniture / painting ghost shadows out of the floor, wall and ceiling lightmaps (a grey
# "closing": dark patches smaller than ~0.8 m are filled from their surroundings, the room's real light falloff stays),
# (2) build a stepped false ceiling with a warm cove glow, (3) export the room without the movable furniture.
#   blender -b living_v1.blend -P fix_shadows_ceiling.py -- <room-living dir>
import bpy, sys, os, math
import numpy as np
OUT = os.path.abspath(sys.argv[sys.argv.index('--') + 1])
FURN = ('LM_Sofa', 'LM_Loveseat', 'LM_Armchair1', 'LM_Armchair2', 'LM_Sideboard', 'LM_SideTableA', 'LM_SideTableB')
DRESS = ('Cushion', 'Newspaper', 'Fold', 'Book', 'Candle', 'Flame', 'Sleeve', 'Disc')

def maxf(a):
    p = np.pad(a, 1, mode='edge'); return np.max([p[i:i + a.shape[0], j:j + a.shape[1]] for i in range(3) for j in range(3)], axis=0)
def minf(a):
    p = np.pad(a, 1, mode='edge'); return np.min([p[i:i + a.shape[0], j:j + a.shape[1]] for i in range(3) for j in range(3)], axis=0)
def box_blur(a, r):
    for ax in (0, 1):
        k = np.ones(2 * r + 1) / (2 * r + 1); p = np.pad(a, [(r, r) if i == ax else (0, 0) for i in range(2)], mode='edge')
        a = sum(k[i] * np.take(p, range(i, i + a.shape[ax]), axis=ax) for i in range(2 * r + 1))
    return a

def clean(name, radius_m, px_per_m):
    img = bpy.data.images.get(name)
    if img is None: print('NO IMAGE', name); return
    w, h = img.size; px = np.array(img.pixels[:], dtype=np.float32).reshape(h, w, 4); f = 8; hh, ww = h // f * f, w // f * f
    r = max(2, int(radius_m * px_per_m / f)); tot = 0.0
    for c in range(3):
        L = px[..., c]
        small = L[:hh, :ww].reshape(hh // f, f, ww // f, f).max(axis=(1, 3))          # block max, so thin dark lines do not matter
        d = small
        for _ in range(r): d = maxf(d)
        for _ in range(r): d = minf(d)                                                  # closing: fills dark patches narrower than 2r blocks
        d = box_blur(d, 2)
        B = np.kron(d, np.ones((f, f), np.float32)); B = np.pad(B, ((0, h - B.shape[0]), (0, w - B.shape[1])), mode='edge')
        ratio = L / np.maximum(B, 1e-3); wgt = np.clip((0.97 - ratio) / 0.16, 0, 1)    # only genuine dark patches are filled; the gentle falloff is left alone
        wgt = box_blur(wgt, 3)
        px[..., c] = np.clip(L * (1 - wgt) + B * wgt, 0, 1); tot += float(wgt.mean())
    img.pixels.foreach_set(px.ravel()); img.pack(); img.update()
    print('CLEANED', name, w, h, 'filled share', round(tot / 3, 3))

SHELL_PPM = {'LM_Shell_Floor.png': 205, 'LM_Shell_Back Wall.png': 205, 'LM_Shell_Front Wall.png': 205, 'LM_Shell_Left Wall.png': 222, 'LM_Shell_Right Wall.png': 222, 'LM_Shell_Ceiling.png': 111, 'LM_Shell_Rug.png': 379}
for n, ppm in SHELL_PPM.items():
    clean(n, 1.5 if ('Wall' in n or 'Floor' in n or 'Rug' in n) else 0.6, ppm)


def flatten(name, spread):
    """Thin strips (cornice, skirting): keep a little shading but squash patches far from the typical brightness."""
    img = bpy.data.images.get(name)
    if img is None: print('NO IMAGE', name); return
    w, h = img.size; px = np.array(img.pixels[:], dtype=np.float32).reshape(h, w, 4); L = px[..., :3].mean(-1); ok = L > 0.01
    med = float(np.median(L[ok])); tgt = np.clip(L, med - spread, med + spread) / np.maximum(L, 1e-3)
    px[..., :3] = np.clip(px[..., :3] * np.where(ok, tgt, 1.0)[..., None], 0, 1); img.pixels.foreach_set(px.ravel()); img.pack(); img.update(); print('FLATTENED', name, round(med, 3))
def lift(name, frac):
    """Window reveals / frames: no pure-black corners; nothing darker than frac of the median."""
    img = bpy.data.images.get(name)
    if img is None: print('NO IMAGE', name); return
    w, h = img.size; px = np.array(img.pixels[:], dtype=np.float32).reshape(h, w, 4); L = px[..., :3].mean(-1); ok = L > 0.005
    med = float(np.median(L[ok])); tgt = np.maximum(L, frac * med) / np.maximum(L, 1e-3)
    px[..., :3] = np.clip(px[..., :3] * np.where(ok, tgt, 1.0)[..., None], 0, 1); img.pixels.foreach_set(px.ravel()); img.pack(); img.update(); print('LIFTED', name, round(med, 3))
flatten('LM_LM_Cornice.png', 0.05); flatten('LM_LM_Skirting.png', 0.06)
for n in ('LM_LM_RevealF.png', 'LM_LM_RevealR.png', 'LM_LM_FrameF.png', 'LM_LM_FrameR.png'): lift(n, 0.75)

def ceiling_shading(name):
    """A warm cove glow on the raised ceiling just inside the dropped frame, and a soft shadow right at the frame's edge."""
    img = bpy.data.images.get(name)
    if img is None: print('NO IMAGE', name); return
    w, h = img.size; px = np.array(img.pixels[:], dtype=np.float32).reshape(h, w, 4)
    xs = (np.arange(w) + 0.5) / w * 5.2 - 2.6; ys = (np.arange(h) + 0.5) / h * 4.2 - 2.1
    X, Y = np.meshgrid(xs, ys); d = np.minimum(1.84 - np.abs(X), 1.34 - np.abs(Y))       # distance inside the raised area's edge
    inside = d > 0
    glow = np.where(inside, 0.55 * np.exp(-np.maximum(d, 0) / 0.30), 0.0)
    shade = np.where(inside, 1 - 0.30 * np.exp(-np.maximum(d, 0) / 0.05), 1.0)
    base = px[..., :3] * shade[..., None]
    base = base + glow[..., None] * np.array([1.0, 0.72, 0.42], np.float32)
    px[..., :3] = np.clip(base, 0, 1); img.pixels.foreach_set(px.ravel()); img.pack(); img.update(); print('CEILING shaded', w, h)
ceiling_shading('LM_Shell_Ceiling.png')

# ---- the movable furniture (and what stands on it) leaves the room file; it ships as its own pieces
for o in list(bpy.data.objects):
    if o.type == 'MESH' and (o.name in FURN or o.name.startswith(DRESS)): bpy.data.objects.remove(o)

# ---- a stepped false ceiling: a dropped frame round the room under the cornice, a second thin lip, and a warm cove glow
X0, X1, Y0, Y1, H = -2.6, 2.6, -2.1, 2.1, 3.0
def mat(name, base, rough, emit=None, strength=1.0):
    m = bpy.data.materials.new(name); m.use_nodes = True; b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (*base, 1); b.inputs['Roughness'].default_value = rough
    if emit: b.inputs['Emission Color'].default_value = (*emit, 1); b.inputs['Emission Strength'].default_value = strength
    return m
M_PL = mat('False Ceiling', (0.90, 0.88, 0.83), 0.85, (0.62, 0.60, 0.56), 1.0)
M_GLOW = mat('Cove Glow', (0.02, 0.02, 0.02), 0.5, (1.0, 0.76, 0.45), 5.0)
def box(name, c, d, m):
    bpy.ops.mesh.primitive_cube_add(size=1, location=c); o = bpy.context.active_object; o.name = name; o.scale = d
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True); o.data.materials.append(m)
    bv = o.modifiers.new('B', 'BEVEL'); bv.width = 0.004; bv.segments = 2; bpy.ops.object.modifier_apply(modifier='B'); return o
IN, FW, DROP = 0.19, 0.50, 0.16          # clear of the cornice's 17 cm, frame width, drop under the ceiling
xa, xb, ya, yb = X0 + IN, X1 - IN, Y0 + IN, Y1 - IN
zc = H - DROP / 2
box('DropL', ((xa + xa + FW) / 2, 0, zc), (FW, yb - ya, DROP), M_PL); box('DropR', ((xb + xb - FW) / 2, 0, zc), (FW, yb - ya, DROP), M_PL)
box('DropF', (0, (ya + ya + FW) / 2, zc), (xb - xa - 2 * FW, FW, DROP), M_PL); box('DropB', (0, (yb + yb - FW) / 2, zc), (xb - xa - 2 * FW, FW, DROP), M_PL)
LIP, LD = 0.07, 0.045                       # a thin second step along the inner edge
zl = H - DROP - LD / 2
box('LipL', (xa + FW + LIP / 2, 0, zl), (LIP, yb - ya - 2 * FW + 2 * LIP, LD), M_PL); box('LipR', (xb - FW - LIP / 2, 0, zl), (LIP, yb - ya - 2 * FW + 2 * LIP, LD), M_PL)
box('LipF', (0, ya + FW + LIP / 2, zl), (xb - xa - 2 * FW, LIP, LD), M_PL); box('LipB', (0, yb - FW - LIP / 2, zl), (xb - xa - 2 * FW, LIP, LD), M_PL)
G = 0.025                                   # the cove glow: a lit line on the raised ceiling, just inside the frame
zg = H - 0.012
box('GlowL', (xa + FW + LIP + G / 2 + 0.01, 0, zg), (G, yb - ya - 2 * FW - 0.1, 0.012), M_GLOW); box('GlowR', (xb - FW - LIP - G / 2 - 0.01, 0, zg), (G, yb - ya - 2 * FW - 0.1, 0.012), M_GLOW)
box('GlowF', (0, ya + FW + LIP + G / 2 + 0.01, zg), (xb - xa - 2 * FW - 2 * LIP - 0.1, G, 0.012), M_GLOW); box('GlowB', (0, yb - FW - LIP - G / 2 - 0.01, zg), (xb - xa - 2 * FW - 2 * LIP - 0.1, G, 0.012), M_GLOW)

# recessed downlights in the dropped frame (a bright warm lens in a dark trim ring)
M_TRIM = mat('Downlight Trim', (0.10, 0.08, 0.06), 0.4); M_LENS = mat('Downlight Lens', (0.02, 0.02, 0.02), 0.3, (1.0, 0.82, 0.55), 6.0)
def cyl(name, loc, r, h, m):
    bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=r, depth=h, location=loc); o = bpy.context.active_object; o.name = name; o.data.materials.append(m); return o
zd = H - DROP - 0.004
spots = [(xa + FW / 2, y_) for y_ in (-1.2, 0.0, 1.2)] + [(xb - FW / 2, y_) for y_ in (-1.2, 0.0, 1.2)] + [(x_, ya + FW / 2) for x_ in (-0.9, 0.9)] + [(x_, yb - FW / 2) for x_ in (-0.9, 0.9)]
for i, (x_, y_) in enumerate(spots):
    cyl('DLTrim%d' % i, (x_, y_, zd), 0.075, 0.008, M_TRIM); cyl('DLLens%d' % i, (x_, y_, zd - 0.005), 0.052, 0.006, M_LENS)

bpy.ops.export_scene.gltf(filepath=os.path.join(OUT, 'living_v1_fixed.glb'), export_format='GLB', export_apply=True, export_cameras=False, export_lights=False, export_image_format='JPEG', export_jpeg_quality=85)
print('DONE fix')
