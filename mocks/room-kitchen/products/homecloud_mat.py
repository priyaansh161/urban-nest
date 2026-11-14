# HomeCloud kitchen floor runner (643d1344), 45 x 120 cm: the listing photo's own print (rectified, the far rows rebuilt from
# the sharp near ones: the tiles repeat every three rows, the middle three shifted a column; see ref/homecloud_print.png),
# flat-woven face, soft rounded corners, a thin rubber back.   blender -b -P homecloud_mat.py -- <outdir>
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from klib import *

reset()
W, D = 0.45, 1.20
pr = bpy.data.images.load(os.path.join(HERE, 'ref', 'homecloud_print.png'))
N = 1024; yy, xx = np.mgrid[0:N, 0:N] / N * 2 * math.pi * 120                   # flat weave, ~0.5 mm
weave = 0.5 + 0.25 * np.sin(xx) * np.sign(np.sin(yy / 2)) + 0.25 * np.sin(yy) * np.sign(np.sin(xx / 2))
weave = weave * 0.75 + 0.25 * tile_noise(N, N, 40, 40, seed=7)
TOP = tex_mat('Runner Print', pr, 0.85, 0.0, np_img('runner weave', height_to_normal(weave, 2.5), noncolor=True), 0.3)
RUB = pmat('Rubber Back', (0.30, 0.17, 0.08), 0.75)
slab('Back', rrect(W, D, 0.030, 12), 0, 0.0015, RUB, bevel=0.0004)
top = slab('Face', rrect(W - 0.001, D - 0.001, 0.0295, 12), 0.0015, 0.005, TOP, bevel=0.0012, bseg=3)
planar_uv(top, W, D)
nt = TOP.node_tree; tn = [n for n in nt.nodes if n.type == 'TEX_IMAGE' and n.image.name == 'runner weave'][0]
mp = nt.nodes.new('ShaderNodeMapping'); tc = nt.nodes.new('ShaderNodeTexCoord'); mp.inputs['Scale'].default_value = (12, 32, 1)
nt.links.new(tc.outputs['UV'], mp.inputs['Vector']); nt.links.new(mp.outputs['Vector'], tn.inputs['Vector'])
finish('homecloud_mat', 'HomeCloud Kitchen Floor Runner', view=(0.3, -1, 1.2))
print('DONE')
