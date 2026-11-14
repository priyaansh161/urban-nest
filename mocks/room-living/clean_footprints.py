# Fills the black footprints wall art leaves in the wall lightmaps (only near-black patches; the light pools stay), then
# re-exports the room without the movable furniture.  blender -b living_v1.blend -P clean_footprints.py -- <dir>
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
        ratio = L / np.maximum(B, 1e-3); wgt = np.clip((0.45 - ratio) / 0.20, 0, 1)    # only genuine dark patches are filled; the gentle falloff is left alone
        wgt = box_blur(wgt, 3)
        px[..., c] = np.clip(L * (1 - wgt) + B * wgt, 0, 1); tot += float(wgt.mean())
    img.pixels.foreach_set(px.ravel()); img.pack(); img.update()
    print('CLEANED', name, w, h, 'filled share', round(tot / 3, 3))

for n, ppm, r in (('LM_Shell_Back Wall.png', 205, 1.0), ('LM_Shell_Front Wall.png', 205, 1.0), ('LM_Shell_Left Wall.png', 222, 1.0), ('LM_Shell_Right Wall.png', 222, 1.0), ('LM_LM_Panels.png', 300, 0.25)):
    clean(n, r, ppm)
FURN = ('LM_Sofa', 'LM_Loveseat', 'LM_Armchair1', 'LM_Armchair2', 'LM_Sideboard', 'LM_SideTableA', 'LM_SideTableB')
DRESS = ('Cushion', 'Newspaper', 'Fold', 'Book', 'Candle', 'Flame', 'Sleeve', 'Disc')
for o in list(bpy.data.objects):
    if o.type == 'MESH' and (o.name in FURN or o.name.startswith(DRESS)): bpy.data.objects.remove(o)
bpy.ops.export_scene.gltf(filepath=os.path.join(OUT, 'living_v1_nofurn.glb'), export_format='GLB', export_apply=True, export_cameras=False, export_lights=False, export_image_format='JPEG', export_jpeg_quality=85)
print('DONE footprints')
