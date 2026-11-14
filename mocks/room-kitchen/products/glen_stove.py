# Glen 3-burner toughened-glass gas stove (d0ccbf0a), 70 W x 40.5 D x 11 H cm, from its listing photos: a black glass top with
# softly rounded corners on a black powder-coated body, three brass burners (ported crown, centre cap) each in a polished
# chrome spill tray, black four-prong cast pan supports, three black knobs with chrome rings on the front edge, GLEN in white
# on the glass (front-left and front-centre).   blender -b -P glen_stove.py -- <outdir>
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from klib import *

reset()
W, D = 0.70, 0.405
GLASS = pmat('Black Toughened Glass', (0.008, 0.008, 0.01), 0.04, coat=1.0, coat_rough=0.02)
BODY = pmat('Black Powder Coat', (0.025, 0.025, 0.028), 0.5, 0.3)
CHROME = pmat('Polished Chrome', (0.90, 0.90, 0.90), 0.07, 1.0)
BRASS = pmat('Brass', (0.72, 0.52, 0.28), 0.32, 1.0)
CAST = pmat('Cast Iron Black', (0.03, 0.03, 0.03), 0.55, 0.4)
KNOB = pmat('Knob Black', (0.02, 0.02, 0.022), 0.25)
WHITE = pmat('White Print', (0.92, 0.92, 0.92), 0.4)
ZB, ZG = 0.060, 0.066                                          # body top, glass top
slab('Body', rrect(W - 0.016, D - 0.02, 0.010, 8), 0.010, ZB, BODY, bevel=0.003)
for x in (-0.31, 0.31):
    for y in (-0.16, 0.16): cyl(0.012, 0.010, (x, y, 0.005), KNOB, v=32, bev=0.002)
slab('Glass', rrect(W, D, 0.012, 10), ZB, ZG, GLASS, bevel=0.0015, bseg=2)
BX = (-0.230, 0.0, 0.230); BY = (0.025, 0.045, 0.025)
for bx_, by_ in zip(BX, BY):
    lathe('Spill Tray', [(0.030, ZG + 0.002), (0.040, ZG + 0.0015), (0.070, ZG + 0.003), (0.080, ZG + 0.0045), (0.083, ZG + 0.003),
                         (0.083, ZG), (0.030, ZG)], [CHROME], seg=160, closed=True)
    P[-1].location = (bx_, by_, 0)
    crown = [(0.0, ZG + 0.004), (0.046, ZG + 0.004), (0.048, ZG + 0.008)]                  # brass burner: base, ported wall, crown
    for k in range(6): crown += [(0.048, ZG + 0.010 + k * 0.0026), (0.0465, ZG + 0.0113 + k * 0.0026)]
    crown += [(0.047, ZG + 0.026), (0.040, ZG + 0.028), (0.030, ZG + 0.028), (0.030, ZG + 0.022), (0.020, ZG + 0.022), (0.0, ZG + 0.022)]
    lathe('Burner', crown, [BRASS], seg=128); P[-1].location = (bx_, by_, 0)
    lathe('Cap', [(0.0, ZG + 0.022), (0.026, ZG + 0.022), (0.027, ZG + 0.027), (0.022, ZG + 0.031), (0.0, ZG + 0.032)], [BRASS], seg=96); P[-1].location = (bx_, by_, 0)
    for k in range(18):                                          # flame ports round the crown
        a = 2 * math.pi * k / 18
        cyl(0.0016, 0.004, (bx_ + 0.048 * math.cos(a), by_ + 0.048 * math.sin(a), ZG + 0.017), CAST, rot=(0, math.pi / 2, a), v=12)
    star = []                                                    # the cast star the prongs stand on, flat on the glass round the tray
    for k in range(64):
        a = 2 * math.pi * k / 64; d = min(abs(((a - math.pi / 4) % (math.pi / 2)) - math.pi / 4), 1)
        r = 0.088 + 0.040 * max(0.0, 1 - d / 0.30) ** 1.6
        star.append((bx_ + r * math.cos(a), by_ + r * math.sin(a)))
    st = slab('Star', star, ZG, ZG + 0.004, CAST, bevel=0.0012)
    cut(st, cyl(0.084, 0.02, (bx_, by_, ZG), None, v=128))
    for k in range(4):                                           # solid cast prongs: up from the star's points, a flat top for the pan
        a = math.pi / 4 + k * math.pi / 2; ca, sa = math.cos(a), math.sin(a)
        pts = [(0.116, ZG + 0.003), (0.108, ZG + 0.020), (0.100, ZG + 0.040), (0.090, ZG + 0.045), (0.066, ZG + 0.045), (0.060, ZG + 0.036)]
        sweep('Prong', [(bx_ + r * ca, by_ + r * sa, z) for r, z in pts], CAST, profile=superellipse(0.0055, 0.0042, 3.5, 24), twist_up=(0, 0, 1), n=10)
FRONT = -D / 2 + 0.008
for bx_ in BX:                                                   # knobs on the front lip, chrome ring behind each
    cyl(0.021, 0.004, (bx_, FRONT - 0.002, 0.034), CHROME, rot=(math.pi / 2, 0, 0), v=96, bev=0.001)
    lathe('Knob', [(0.0, 0.0), (0.017, 0.0), (0.018, 0.004), (0.016, 0.022), (0.014, 0.026), (0.0, 0.027)], [KNOB], seg=96)
    k_ = P[-1]; k_.matrix_world = Matrix.Translation((bx_, FRONT - 0.004, 0.034)) @ Matrix.Rotation(math.pi / 2, 4, 'X')
    slab('Grip', rrect(0.006, 0.030, 0.002, 4), 0, 0.022, KNOB, bevel=0.001)
    g = P[-1]; g.matrix_world = Matrix.Translation((bx_, FRONT - 0.006, 0.034)) @ Matrix.Rotation(math.pi / 2, 4, 'X')
    cyl(0.0022, 0.0006, (bx_, FRONT + 0.012, ZG + 0.0003), WHITE, v=24)       # the little ignition mark printed behind each knob
text_mesh('GLEN', 0.016, WHITE, Matrix.Translation((-W / 2 + 0.055, -D / 2 + 0.030, ZG + 0.0002)), ext=0.00002)
text_mesh('GLEN', 0.011, WHITE, Matrix.Translation((0.0, -0.075, ZG + 0.0002)), ext=0.00002)
finish('glen_stove', 'Glen 3 Burner Glass Top Gas Stove', view=(0.25, -1, 0.75))
print('DONE')
