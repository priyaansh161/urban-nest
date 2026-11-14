# placements.json for the kitchen: every kitchen Essential that has a model, at its real size, where a cook would use it.
# pos = three.js [x, y(up), z] = Blender (x, -z, y). Counter top is 0.90. See LAYOUT.md for the plan.
import json, os
items = {r['id'][:8]: r for r in json.load(open('kitchen_items.json', encoding='utf8'))}
CT = 0.90
def P(id8, name, z, x, y, size, rot=0.0, **kw):
    r = items[id8]; d = dict(id=r['id'], name=name, file='final/%s.glb' % id8, listing=r['name'], link=r.get('buy_link'), tag='ESSENTIALS · KITCHEN',
                             pos=[x, z, -y]); d.update(size); 
    if rot: d['rotY'] = rot
    desc = ' '.join((r.get('description') or '').split()); desc = desc.split('. ')[0].rstrip('.') + '.' if desc else ''
    d['desc'] = desc[:220]
    d['specs'] = [s for s in (r.get('specs') or []) if s[0] in ('Material', 'Material Type', 'Colour', 'Item Dimensions L x W x H', 'Product Dimensions', 'Item Dimensions L x W', 'Item Dimensions D x W x H', 'Item Dimensions W x H', 'Brand', 'Brand Name', 'Capacity')][:3]
    d.update(kw); return d
H = lambda h: {'height': h}; L = lambda l: {'length': l}
Q = 1.5708
out = [
    # back run, left of the sink (over the knee space): the dish rack; the strainer at the far end
    P('6410bafe', 'TEX-RO Dish Drying Rack', CT, -0.60, 1.40, L(0.43)),
    P('f146104d', 'Clazkit Strainer Bowl', CT, -1.13, 1.40, L(0.22)),
    # right of the sink: sponge tray draining into the sink, butter dish, wooden spatula rest
    P('1b0130dd', 'HOMEZE Silicone Sink Mat', CT, 0.46, 1.42, L(0.30), -Q),
    P('3bc04eb5', 'Butter Dish with Lid', CT, 0.70, 1.33, L(0.18)),
    P('2759a7b9', 'Wooden Spatula Rest', CT, 0.93, 1.27, L(0.119)),
    # the corner and the hob side of the right run
    P('57ccb316', 'Vanam Neem Wood Spatula Set', CT, 1.30, 1.42, H(0.37)),
    P('0d924fe2', 'Glass Salt & Pepper Shakers', CT, 1.30, 0.97, H(0.136), Q),
    P('5ee6f430', 'NAALSA Steel Spoon Rest', CT, 0.98, 0.95, L(0.205), Q),
    P('d0ccbf0a', 'Glen 3-Burner Glass Top Gas Stove', CT, 1.21, 0.455, L(0.70), -Q),
    P('46c9cd64', 'Kmils Oil Dispenser with Brush', CT, 1.36, -0.06, H(0.145)),
    P('b16d9948', '2-in-1 Glass Oil Dispenser', CT, 1.35, -0.18, H(0.25)),
    P('5c8fc071', 'Primeway Spoon Rest', CT, 1.00, -0.06, L(0.20), Q),
    P('71a93adf', 'Silicone Basting Brush', CT, 1.00, -0.27, L(0.21), Q),
    # prep: the board with the garlic press and the coconut opener on it
    P('53d21ba3', 'Mango Wood Chopping Board', CT, 0.98, -0.60, L(0.40), Q),
    P('b46a7d38', 'HomeWiz Garlic Press', CT + 0.025, 0.98, -0.50, L(0.16), Q),
    P('b4867f61', 'Nestasia Coconut Opener', CT + 0.025, 0.99, -0.70, L(0.17), Q),
    P('7419de18', 'Wooden Tissue Roll Holder', CT, 1.33, -0.68, H(0.30)),
    P('b4bd8136', 'HomeWiz Hung Curd Maker', CT, 1.31, -0.88, H(0.185)),
    # the dish mat at the front end, mugs drying on it
    P('3e046e4a', 'HomeCloud Dish Drying Mat', CT, 1.15, -1.18, L(0.50)),
    P('04283da4', 'Coffee Mugs', CT + 0.005, 1.12, -1.16, H(0.10)),
    # the apron hangs on the tall unit's wood panel, facing the room
    P('e5075788', 'Ecotribe Cotton Apron', 0.78, -0.80, -1.25, H(0.78), Q, alignLeft=-0.83),
    # added 14 Nov evening: the kitchen listings that had no model until today
    P('48410c20', 'Amazon Basics Knife Block Set', CT, 1.06, 1.58, H(0.36), -0.35),
    P('ace72caf', 'Painted Pickle Jars with Tray', CT, 0.74, 1.59, L(0.27)),
    P('c02bca89', "D'Maiolica Pickle Jars, Set of 2", 1.128, 0.30, 1.74, L(0.25)),
    P('c65af49f', 'Green Knife Set of 3', CT, -0.92, 1.40, L(0.318)),
    P('6970f7d6', 'OrganizeMee Bag Holder', 0.36, 1.15, -1.45, H(0.208), alignBack=1.42),
    P('643d1344', 'HomeCloud Kitchen Runner', 0.0, 0.0, 0.78, L(1.20), Q),
    P('258b0233', 'CANWAY Wood Print Runner', 0.0, 0.52, -0.35, L(1.20)),
]
json.dump({'_note': 'kitchen products, see make_placements.py', 'products': out, 'staging': []}, open('placements.json', 'w', encoding='utf8'), indent=1, ensure_ascii=False)
print(len(out), 'products')
