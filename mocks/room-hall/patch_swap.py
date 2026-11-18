# His review, 18 Nov: the living sits by the main door (front), the dining and the kitchen at the back. Patches hall_body.py,
# hall_tail.py and make_placements.py (backups *.pre_swap).
import os, shutil
D = os.path.dirname(os.path.abspath(__file__))
def patch(fn, pairs):
    p = os.path.join(D, fn); shutil.copy(p, p + '.pre_swap'); s = open(p, encoding='utf8').read()
    for a, b in pairs:
        if a not in s: raise SystemExit('%s: missing %r' % (fn, a[:70]))
        s = s.replace(a, b)
    open(p, 'w', encoding='utf8').write(s); print('patched', fn)

patch('hall_body.py', [
    ("KIT = hy(-3.35, -2.45, 2.25)", "KIT = hy(2.45, 3.35, 2.25)                 # the kitchen at the back, by the dining"),
    ("for a, b in ((Y0, KY0), (KY1, PY0), (PY1, Y1)): sky_(a, b, X0, -1)", "for a, b in ((Y0, PY0), (PY1, KY0), (KY1, Y1)): sky_(a, b, X0, -1)"),
    ("for a, b in ((-2.88, -2.57), (-0.93, 1.13)): sky_(a, b, X1, 1)", "for a, b in ((-2.88, -2.67), (-0.43, 0.93), (2.57, Y1)): sky_(a, b, X1, 1)"),
    ("TVC = 2.35; TV0, TV1 = TVC - 1.20, TVC + 1.20; MW = 0.70", "TVC = -1.55; TV0, TV1 = TVC - 1.10, TVC + 1.10; MW = 0.65     # the living at the front: TV wall just past the shoe cabinet"),
    ("CN0, CN1 = TVC - 1.05, TVC + 1.05", "CN0, CN1 = TVC - 0.95, TVC + 0.95"),
    ("ac = [bx('AC Body', X0, X0 + 0.21, 2.75, 3.65, 2.25, 2.55, M['white'], 0.02), bx('AC Vent', X0 + 0.15, X0 + 0.212, 2.80, 3.60, 2.27, 2.30, M['matblack'])]",
     "ac = [bx('AC Body', X0, X0 + 0.21, -3.40, -2.50, 2.25, 2.55, M['white'], 0.02), bx('AC Vent', X0 + 0.15, X0 + 0.212, -3.35, -2.55, 2.27, 2.30, M['matblack'])]"),
    ("CU0, CU1 = -2.55, -0.95; CD = 0.42", "CU0, CU1 = 0.95, 2.55; CD = 0.42"),
    ("MY0, MY1 = -2.05, -1.15; MC = (MY0 + MY1) / 2", "MY0, MY1 = 1.15, 2.05; MC = (MY0 + MY1) / 2"),
    ("LIV = (-1.15, 1.15, 0.55, 3.35); DIN = (-0.95, 0.75, -3.10, -0.95)", "LIV = (-1.15, 1.15, -3.35, -0.55); DIN = (-0.95, 0.75, 0.95, 3.10)"),
    ("for y0, y1 in ((Y0, DIN[2]), (DIN[3], LIV[2]), (LIV[3], Y1)):", "for y0, y1 in ((Y0, LIV[2]), (LIV[3], DIN[2]), (DIN[3], Y1)):"),
    ("""DL = [(-1.45, 1.05), (-1.45, 2.15), (-1.45, 3.25), (1.45, 1.45), (1.45, 3.25), (-0.5, 0.25), (0.5, 0.25),
      (-1.35, -2.70), (-1.35, -1.40), (1.40, -2.30), (1.40, -1.20), (0.0, -3.55), (1.05, -3.55), (-0.6, 3.62), (0.6, 3.62)]""",
     """DL = [(-1.45, -3.20), (-1.45, -2.15), (-1.45, -1.10), (1.45, -2.45), (1.45, -0.75), (-0.5, -0.25), (0.5, -0.25),
      (-1.35, 1.40), (-1.35, 2.70), (1.40, 1.20), (1.40, 2.30), (0.0, -3.62), (1.05, -3.62), (-0.6, 3.62), (0.6, 3.62)]"""),
    ("TX, TY = -0.15, -2.05", "TX, TY = -0.15, 2.05"),
    ("rug = S(box('Rug', (0.0, 2.10, 0.006), (1.70, 2.40, 0.012), M['rug'], 0.004)); cube = rug", "rug = S(box('Rug', (0.0, -2.10, 0.006), (1.70, 2.40, 0.012), M['rug'], 0.004))"),
    ("uv.data[li].uv = ((co.x + 0.85) / 1.70, (co.y - 0.90) / 2.40)", "uv.data[li].uv = ((co.x + 0.85) / 1.70, (co.y + 3.30) / 2.40)"),
    ("areca(1.38, 3.50, 0)", "areca(1.40, 0.25, 0)                                                  # between the TV wall and the crockery unit"),
])
patch('hall_tail.py', [
    ("""VIEWS = {'entry': ((1.05, Y0 + 0.45, 1.55), (-0.2, Y1, 1.0), 15), 'living': ((0.2, -0.4, 1.5), (0.4, 3.6, 0.95), 17),
         'tv': ((-1.15, 1.30, 1.15), (1.75, 2.55, 1.15), 19), 'dining': ((1.0, 0.7, 1.55), (-0.6, -3.2, 0.85), 17),
         'balcony': ((0.3, 1.0, 1.45), (-0.1, Y1 + 1.5, 1.2), 18)}""",
     """VIEWS = {'entry': ((1.05, Y0 + 0.45, 1.55), (-0.2, Y1, 1.0), 15), 'living': ((0.3, 0.3, 1.5), (0.0, -3.7, 0.95), 17),
         'tv': ((-1.15, -2.40, 1.15), (1.75, -1.45, 1.15), 19), 'dining': ((0.9, -0.5, 1.55), (-0.6, 3.3, 0.85), 17),
         'balcony': ((0.3, 0.2, 1.45), (-0.1, Y1 + 1.5, 1.2), 18)}"""),
])
patch('make_placements.py', [
    ("TX, TY = -0.15, -2.05", "TX, TY = -0.15, 2.05"),
    ("P('8ff6fee2', 'Torque Berlin L-Shaped Sofa', -0.905, 2.15,", "P('8ff6fee2', 'Torque Berlin L-Shaped Sofa', -0.905, -2.15,"),
    ("P('e716af29', 'Enfurnish Sheesham Coffee Table', 0.30, 1.95,", "P('e716af29', 'Enfurnish Sheesham Coffee Table', 0.30, -2.15,"),
    ("P('aef51ee7', 'BEHOMA Brass Peacock Urli', 0.30, 1.95,", "P('aef51ee7', 'BEHOMA Brass Peacock Urli', 0.30, -2.15,"),
    ("P('e570aa03', 'Homesake ARC Floor Lamp', -1.40, 0.50,", "P('e570aa03', 'Homesake ARC Floor Lamp', -0.40, -0.45,"),
    ("P('9677aca6', 'Paper Plane Abstract Canvas 122 x 81', X0 + 0.03, 2.15,", "P('9677aca6', 'Paper Plane Abstract Canvas 122 x 81', X0 + 0.03, -2.15,"),
    ("P('872070ef', 'UAG 7 Running Horses', X1 - 0.24, 3.05,", "P('872070ef', 'UAG 7 Running Horses', X1 - 0.24, -2.25,"),
    ("P('271ce125', 'Ribbed Ceramic Vase', X1 - 0.24, 1.55,", "P('271ce125', 'Ribbed Ceramic Vase', X1 - 0.24, -0.80,"),
    ("P('395cbcd3', 'Brass Ganesh Idol', X0 + 0.15, -1.60,", "P('395cbcd3', 'Brass Ganesh Idol', X0 + 0.15, 1.60,"),
])
