# HomeCloud dish drying mat (3e046e4a), 50 x 40 cm, from its listing photo: the actual Moroccan tile print (rectified out of the
# photo, tiles rebuilt clean, see mat_print.mjs) on a soft absorbent fabric top with a fine weave, on a thin dark rubber base
# with rounded corners.   blender -b -P dish_mat.py -- <outdir>
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from klib import *

reset()
W, D = 0.50, 0.40
pr = bpy.data.images.load(os.path.join(HERE, 'ref', 'mat_print.png'))
N = 1024; yy, xx = np.mgrid[0:N, 0:N] / N * 2 * math.pi * 160                  # fine weave, ~0.3 mm threads
weave = 0.5 + 0.25 * np.sin(xx) * np.sign(np.sin(yy / 2)) + 0.25 * np.sin(yy) * np.sign(np.sin(xx / 2))
weave = weave * 0.7 + 0.3 * tile_noise(N, N, 40, 40, seed=5)
TOP = tex_mat('Mat Print', pr, 0.88, 0.0, np_img('weave', height_to_normal(weave, 3.0), noncolor=True), 0.35)
RUB = pmat('Rubber Base', (0.13, 0.10, 0.11), 0.7)
base = slab('Base', rrect(W, D, 0.014, 12), 0, 0.0015, RUB, bevel=0.0004)
top = slab('Top', rrect(W - 0.002, D - 0.002, 0.013, 12), 0.0015, 0.0045, TOP, bevel=0.0012, bseg=3)
planar_uv(top, W, D)
me = top.data; uv = me.uv_layers.active.data                                   # the weave map tiles 20x over the print
nt = TOP.node_tree; tn = [n for n in nt.nodes if n.type == 'TEX_IMAGE' and n.image.name == 'weave'][0]
mp = nt.nodes.new('ShaderNodeMapping'); tc = nt.nodes.new('ShaderNodeTexCoord'); mp.inputs['Scale'].default_value = (20, 16, 1)
nt.links.new(tc.outputs['UV'], mp.inputs['Vector']); nt.links.new(mp.outputs['Vector'], tn.inputs['Vector'])
finish('dish_mat', 'HomeCloud Dish Drying Mat', view=(0.3, -1, 1.1))
print('DONE')
