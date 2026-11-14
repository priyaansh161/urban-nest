# OrganizeMee garbage bag holder (6970f7d6), wall-mounted, 26 cm wide x 6.5 cm deep; the height (~19 cm) is read off the
# straight-on listing photo, which the listed 14.7 cm does not match. Glossy white box, rounded bottom corners, the front
# edge stepping down past the fifth roll; five tall black bag rolls standing in it and a shorter sixth on the right; the
# vertical pull slot with a bag coming out; the logo (Organize + green Mee, check badge) and the blue-outlined label.
#   blender -b -P bag_holder.py -- <outdir>
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from klib import *

reset()
W, Hh, D = 0.26, 0.19, 0.065
WHITE = pmat('Glossy White PP', (0.93, 0.93, 0.92), 0.18, coat=0.4)
_cr = tile_noise(512, 512, 30, 30, seed=3) * 0.6 + tile_noise(512, 512, 90, 90, seed=8) * 0.4
ROLL = tex_mat('Black Bag Roll', np_img('roll col', np.clip(0.025 + 0.03 * _cr[..., None] * np.ones(3), 0, 1)), 0.35, 0.0, np_img('roll crinkle', height_to_normal(_cr, 4.0), noncolor=True), 0.8)
AB = 'C:/Windows/Fonts/arialbd.ttf'
BLUE = pmat('Label Blue', (0.62, 0.78, 0.88), 0.4); INK = pmat('Label Ink', (0.03, 0.03, 0.03), 0.5)
GREEN = pmat('Logo Green', (0.30, 0.65, 0.20), 0.4); GREY = pmat('Logo Grey', (0.20, 0.20, 0.22), 0.5)
UP = Matrix.Rotation(math.pi / 2, 4, 'X')                       # profiles are drawn x across, y up; this stands them up (y -> z)
def front_profile(inset=0.0, top_extra=0.0):
    pts = []
    def arc(cx, cy, r, a0, a1, n=12):
        for k in range(n + 1):
            a = math.radians(a0 + (a1 - a0) * k / n); pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    i = inset; R = 0.024 - i
    arc(i + R, i + R, R, 180, 270); arc(W - i - R, i + R, R, 270, 360)                       # rounded bottom
    zr = 0.160 + top_extra; zl = 0.183 + top_extra
    pts += [(W - i, zr - 0.006), (W - i - 0.004, zr)]                                          # right part, low front edge
    for k in range(13):                                          # the S-curve up to the taller left part
        t = k / 12; x = 0.175 - 0.020 * t; z = zr + (zl - zr) * (0.5 - 0.5 * math.cos(math.pi * t)); pts.append((x, z))
    pts += [(i + 0.004, zl), (i, zl - 0.006)]
    return pts
body = slab('Box', front_profile(), -D / 2, D / 2, WHITE, bevel=0.0025, bseg=3); body.matrix_world = UP; activate(body); bpy.ops.object.transform_apply(rotation=True)
cav = slab('cav', front_profile(0.003, 0.05), -D / 2 + 0.003, D / 2 - 0.003, None, bevel=0, keep=False); cav.matrix_world = UP @ Matrix.Translation((0, 0.008, 0))
activate(cav); bpy.ops.object.transform_apply(location=True, rotation=True); cut(body, cav)
cut(body, cutter_box((0.201, -D / 2, 0.088), (0.011, 0.02, 0.118)))
cut(body, cyl(0.0055, 0.02, (0.201, -D / 2, 0.147), None, rot=(math.pi / 2, 0, 0), v=24))
cut(body, cyl(0.0055, 0.02, (0.201, -D / 2, 0.029), None, rot=(math.pi / 2, 0, 0), v=24))
for k, (x, r, top) in enumerate(((0.0245, 0.0215, 0.208), (0.0675, 0.0215, 0.207), (0.1105, 0.0215, 0.206), (0.1535, 0.0215, 0.205), (0.1950, 0.0205, 0.203), (0.2350, 0.0190, 0.184))):
    lathe('Roll', [(0.0, 0.008), (r, 0.008), (r, top - 0.002), (r - 0.0015, top)] + [(r * (1 - j / 7) * 0.92, top + 0.0004 * (j % 2)) for j in range(1, 8)] + [(0.004, top - 0.003), (0.0, top - 0.003)],
          [ROLL], seg=64)
    P[-1].location = (x, 0.002 * (k % 2), 0); cyl_uv(P[-1], 0, 0.21)
flap = shell('Bag', list(np.linspace(0.0, 0.055, 24)), lambda x: 0.045 * (1 - 0.3 * x / 0.055), lambda x, y: 0.012 * math.sin(y * 60) * x / 0.055, 0.0006, ROLL, nv=24)
flap.matrix_world = Matrix.Translation((0.201, -D / 2 - 0.002, 0.090)) @ Matrix.Rotation(-math.pi / 2, 4, 'Z') @ Matrix.Rotation(math.radians(70), 4, 'X') @ Matrix.Rotation(-0.35, 4, 'Z')
F = -D / 2 - 0.0002
lb = slab('Label', rrect(0.130, 0.060, 0.006, 6), 0, 0.0004, BLUE, bevel=0); lb.matrix_world = Matrix.Translation((0.093, F, 0.056)) @ UP
lw = slab('Label', rrect(0.124, 0.054, 0.004, 6), 0, 0.0005, WHITE, bevel=0); lw.matrix_world = Matrix.Translation((0.093, F - 0.0003, 0.056)) @ UP
text_mesh('TRASH BIN ORGANIZER', 0.0205, INK, Matrix.Translation((0.093, F - 0.0009, 0.0555)) @ UP @ Matrix.Diagonal((0.62, 1, 1, 1)), ext=0.00002, font=AB)
text_mesh('Organize', 0.0085, GREY, Matrix.Translation((0.0440, F - 0.0004, 0.141)) @ UP, ext=0.00002, font=AB)
text_mesh('Mee', 0.0085, GREEN, Matrix.Translation((0.0612, F - 0.0004, 0.141)) @ UP, ext=0.00002, font=AB)
ring_ = lathe('Badge', [(0.0035, 0), (0.0048, 0), (0.0048, 0.0004), (0.0035, 0.0004)], [GREY], seg=48, closed=True)
P[-1].matrix_world = Matrix.Translation((0.021, F, 0.1415)) @ UP
text_mesh('✓', 0.0075, GREY, Matrix.Translation((0.0212, F - 0.0004, 0.1415)) @ UP, ext=0.00002, font='C:/Windows/Fonts/seguisym.ttf')
finish('bag_holder', 'OrganizeMee Garbage Bag Holder', view=(0.3, -1, 0.35))
print('DONE')
