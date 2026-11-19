# placements.json for the hall: Collection pieces (and the Woodshoppe caddy) where a Noida family would keep them.
# pos = three.js [x, y(up), z] = Blender (x, -z, y). See LAYOUT.md.
import json, os
D = os.path.dirname(os.path.abspath(__file__))
items = {r['id'][:8]: r for r in json.load(open(os.path.join(D, 'hall_items.json'), encoding='utf8'))}
def P(id8, name, bx_, by_, bz, size, rot=0.0, **kw):
    """bx_, by_, bz: Blender x, y and the height the piece stands on."""
    r = items[id8]; tag = ('ESSENTIALS · ' if r.get('section') == 'essentials' else 'COLLECTION · ') + (r.get('category') or '').upper().replace('-', ' ')
    d = dict(id=r['id'], name=name, file='final/%s.glb' % id8, listing=r['name'], link=r.get('buy_link'), tag=tag, pos=[bx_, bz, -by_]); d.update(size)
    if rot: d['rotY'] = rot
    desc = ' '.join((r.get('description') or '').split()); desc = desc.split('. ')[0].rstrip('.') + '.' if desc else ''
    d['desc'] = desc[:220]
    d['specs'] = [s for s in (r.get('specs') or []) if s[0] in ('Material', 'Material Type', 'Colour', 'Color', 'Item Dimensions L x W x H', 'Product Dimensions', 'Brand', 'Brand Name', 'Size')][:3]
    d.update(kw); return d
H = lambda h: {'height': h}; L = lambda l: {'length': l}
Q = 1.5708
X0, X1, Y0, Y1 = -1.75, 1.75, -3.9, 3.9
TX, TY = -0.15, 2.05                    # dining table centre (staging), top at 0.76
MC = 1.60                               # mandir centre (y)
out = [
    # living: the L-sofa along the left wall under the Gond set; coffee table with a candle (and staged books); tripod lamp in the corner by the door
    P('8ff6fee2', 'Torque Berlin L-Shaped Sofa', -0.905, -2.19, 0.0, L(2.80), Q, footprint=[2.80, 1.65]),
    P('e716af29', 'Enfurnish Sheesham Coffee Table', 0.36, -2.15, 0.0, L(1.00), Q),
    P('cbee0eaf', 'Botanico Coffee Vanilla 3-Wick Candle', 0.26, -2.42, 0.382, H(0.10)),
    P('7fbfd698', 'Modern Wooden Tripod Floor Lamp', -1.48, -3.683, 0.0, H(1.40)),     # the corner by the door, its shade over the sofa's arm
    P('0c9ab81d', 'kotart Gond Art Paintings, Set of 6', X0 + 0.03, -2.325, 1.17, L(1.30), Q, alignLeft=X0 + 0.018, noShadow=True),
    # the TV console: a gold elephant toward the entry end, a donut vase of dried flowers at the other
    P('1ff58ff3', 'BEHOMA Gold Elephant Candle Holder', X1 - 0.22, -2.28, 0.60, H(0.30), -Q),
    P('088bb117', 'PUREZENTO Twister Donut Vase with Dried Flowers', X1 - 0.22, -0.76, 0.60, H(0.48), Q),
    # between the TV wall and the crockery unit: the round wooden table with its plant
    P('13e166b8', 'DAXTANAR Solid Wood Round Table', X1 - 0.30, 0.25, 0.0, H(0.80)),
    # dining: the linear chandelier over the table, the wooden T-light urli on the runner, flowers on the crockery counter
    P('91771cce', '10-Light Linear Glass Chandelier', TX, TY, 3.0, L(1.00), Q, hang=True),
    P('0193738b', 'BEHOMA Wooden T-Light Urli', TX, TY, 0.766, L(0.32)),
    P('d3cee741', 'Geometric Vase with Artificial Flowers', X1 - 0.21, 1.30, 0.875, H(0.42)),
    # the front wall by the door: the pendulum clock
    P('2278822e', 'The Artment Mono Pendulum Wall Clock', -0.70, Y0 + 0.045, 1.38, H(0.58), 3.1416),
    # the mandir: Ganesh on his marble step, the brass elephant urli on the drawer unit below
    P('395cbcd3', 'Brass Ganesh Idol', X0 + 0.135, MC, 1.08, H(0.22), Q),
    P('9fb4a2b2', 'Kansakruti Brass Elephant Urli', X0 + 0.21, MC, 0.70, L(0.26), Q),
    # the entry: the panther in the middle of the shoe cabinet, the round leaf art above it
    P('9e634a2b', 'ZART Black Panther Showpiece', X1 - 0.18, -3.35, 0.975, L(0.30), 0.838),     # the model runs at 42 deg: turned to lie along the wall
    P('1e947d6f', 'SAF 3D Leaf Round Wall Art', X1 - 0.03, -3.35, 1.22, H(0.56), -Q, alignRight=X1 - 0.005, noShadow=True),
]
json.dump({'_note': 'hall products, see make_placements.py', 'room': 'hall_v1-web.glb', 'products': out, 'staging': []},
          open(os.path.join(D, 'placements.json'), 'w', encoding='utf8'), indent=1, ensure_ascii=False)
print(len(out), 'products')
