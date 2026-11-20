# placements.json for the kitchen: the kitchen Essentials at real size, where a cook would use them.
# pos = three.js [x, y(up), z] = Blender (x, -z, y). Counter top is 0.90. See LAYOUT.md for the plan.
#
# Composition (his review, 15 Nov): a working kitchen, not a shop shelf. One spoon rest (a neem spatula on it, staging)
# by the hob; no table pieces (salt & pepper) and no second oil dispenser; jars, mugs and the butter dish up on the open
# niche shelves; the small steel tools in the open drawer under the hob; the board clear; the strainer drying on the dish
# mat. Left out of the room (still on their listings): VOLRIX dispenser, NAALSA and wooden spoon rests, salt & pepper,
# wooden tissue box.
import json, os
items = {r['id'][:8]: r for r in json.load(open('kitchen_items.json', encoding='utf8'))}
CT = 0.90
def P(id8, name, z, x, y, size, rot=0.0, **kw):
    r = items[id8]; d = dict(id=r['id'], name=name, file='final/%s.glb' % id8, listing=r['name'], link=r.get('buy_link'), tag='ESSENTIALS · KITCHEN',
                             pos=[x, z, -y]); d.update(size)
    if rot: d['rotY'] = rot
    desc = ' '.join((r.get('description') or '').split()); desc = desc.split('. ')[0].rstrip('.') + '.' if desc else ''
    d['desc'] = desc[:220]
    d['specs'] = [s for s in (r.get('specs') or []) if s[0] in ('Material', 'Material Type', 'Colour', 'Item Dimensions L x W x H', 'Product Dimensions', 'Item Dimensions L x W', 'Item Dimensions D x W x H', 'Item Dimensions W x H', 'Brand', 'Brand Name', 'Capacity')][:3]
    d.update(kw); return d
H = lambda h: {'height': h}; L = lambda l: {'length': l}
Q = 1.5708
SH0, SH1 = 1.538, 1.938          # the niche's two shelf surfaces (build: UZ0 + 0.018, UZ0 + 0.418)
NX = 1.27                        # niche shelf centre (x); the niche runs y -0.90..-0.42
DZ = 0.582                       # the open drawer's floor
out = [
    # back run: rack left of the sink; right of it the sponge tray draining into the sink (soap on it, staging), the curd maker
    # 20 Nov: the ZROY two-tier rack in place of the TEX-RO (its Meshy build reads better); the Epicstack soap pump + sponge
    # holder stands on the sink mat (the green soap bottle, staging, went)
    P('1c96d2fe', 'ZROY 2-Tier Dish Drying Rack', CT, -0.56, 1.42, L(0.42)),
    P('1b0130dd', 'HOMEZE Silicone Sink Mat', CT, 0.48, 1.44, L(0.30), -Q),
    P('32bb34cd', 'Epicstack 3-in-1 Soap Dispenser', CT + 0.012, 0.48, 1.44, L(0.195), -Q),
    P('b4bd8136', 'HomeWiz Hung Curd Maker', CT, 0.74, 1.52, H(0.185)),
    # the corner: knife block and the spatula set in reach of the hob
    P('48410c20', 'Amazon Basics Knife Block Set', CT, 1.24, 1.56, H(0.36), -0.6),
    P('57ccb316', 'Vanam Neem Wood Spatula Set', CT, 1.29, 1.06, H(0.37)),        # clear of the splash (x 1.438)
    # the hob, the one spoon rest beside it, the Kmils dispenser against the splash
    P('d0ccbf0a', 'Glen 3-Burner Glass Top Gas Stove', CT, 1.21, 0.455, L(0.70), -Q),
    P('5c8fc071', 'Primeway Spoon Rest', CT, 1.03, -0.07, L(0.20), Q),
    P('46c9cd64', 'Kmils Oil Dispenser with Brush', CT, 1.36, -0.02, H(0.145)),
    # prep: the board clear, the kitchen roll behind it; the mixer (staging) after it
    P('53d21ba3', 'Mango Wood Chopping Board', CT, 1.00, -0.39, L(0.38), Q),
    P('7419de18', 'Wooden Tissue Roll Holder', CT, 1.36, -0.30, H(0.30)),
    # the front end: the dish mat with the strainer bowl drying on it
    # the green knife set is a ribbed block (Meshy build of its photo, 17 Nov), so it stands on the counter, not in the drawer
    P('c65af49f', 'Green Knife Set with Block', CT, 1.35, -0.47, H(0.33), -Q),
    P('3e046e4a', 'HomeCloud Dish Drying Mat', CT, 1.12, -1.16, L(0.50), Q),
    P('f146104d', 'Clazkit Strainer Bowl', CT + 0.005, 1.08, -1.14, L(0.22)),
    # the open niche: mugs and the butter dish up top, the two pickle sets below
    P('04283da4', 'Coffee Mugs', SH1, NX, -0.765, H(0.10), -Q),              # inside the niche: y -0.902..-0.418
    P('3bc04eb5', 'Butter Dish with Lid', SH1, NX, -0.53, L(0.18), -Q),
    P('c02bca89', "D'Maiolica Pickle Jars, Set of 2", SH0, NX, -0.765, L(0.25), -Q),
    P('ace72caf', 'Painted Pickle Jars with Tray', SH0, NX, -0.53, L(0.27)),       # the tray runs front-to-back so both sets fit
    # the open drawer under the hob: the garlic press, the coconut opener, the basting brush
    P('b46a7d38', 'HomeWiz Garlic Press', DZ, 0.72, 0.56, L(0.16), Q),
    P('b4867f61', 'Nestasia Coconut Opener', DZ, 0.62, 0.62, L(0.17), Q),
    P('71a93adf', 'Silicone Basting Brush', DZ, 0.81, 0.25, L(0.21), Q),
    # (the apron left the room, 15 Nov) the bag holder on the end panel, the two runners on the floor
    P('6970f7d6', 'OrganizeMee Bag Holder', 0.36, 1.15, -1.45, H(0.208), alignBack=1.42),
    P('643d1344', 'HomeCloud Kitchen Runner', 0.0, 0.0, 0.80, L(1.20), Q),
    P('258b0233', 'CANWAY Wood Print Runner', 0.0, 0.55, -0.40, L(1.20)),
]
# staging (no dot): a real Bajaj mixer and the Elica curved-glass hood, both Meshy builds of their product photos
STAGING = [dict(name='Bajaj Mixer Grinder', file='final/stage_mixer.glb', length=0.36, pos=[1.27, CT, 0.77], rotY=-Q),
           dict(name='Elica Curved Glass Chimney', file='final/stage_chimney.glb', length=0.60, pos=[1.25, 1.57, -0.455], rotY=-Q, alignRight=1.43)]
json.dump({'_note': 'kitchen products, see make_placements.py', 'products': out, 'staging': STAGING}, open('placements.json', 'w', encoding='utf8'), indent=1, ensure_ascii=False)
print(len(out), 'products', len(STAGING), 'staging')
