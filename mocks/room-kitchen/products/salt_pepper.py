# The Better Home glass salt & pepper shakers (0d924fe2), from its listing photos: mini mason-jar shakers in glossy milk-white
# and black glass, a mug handle each, a stainless screw lid with rolled beads and thread rings, the holes punched in an S / a P,
# and thin hand-lettered SALT / PEPPER running down the front.   blender -b -P salt_pepper.py -- <outdir>
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from klib import *

reset()
JAR = [(0, 0.0012), (0.018, 0.0008), (0.0235, 0.0), (0.0262, 0.0008), (0.0272, 0.0030), (0.0273, 0.0055), (0.02705, 0.0062), (0.0273, 0.0070),
       (0.0273, 0.0615), (0.0270, 0.0660), (0.0258, 0.0705), (0.0240, 0.0735), (0.0228, 0.0748), (0.0226, 0.0765), (0.0233, 0.0772), (0.0226, 0.0780),
       (0.0226, 0.0795), (0.0233, 0.0802), (0.0226, 0.0810), (0.0215, 0.0840), (0.0195, 0.0846), (0, 0.0846)]
LID = [(0.0228, 0.0752), (0.0240, 0.0753), (0.0249, 0.0758), (0.0253, 0.0766), (0.0252, 0.0776), (0.0247, 0.0782), (0.0246, 0.0790),
       (0.0246, 0.0800), (0.02435, 0.0803), (0.0246, 0.0806), (0.0246, 0.0818), (0.02435, 0.0821), (0.0246, 0.0824), (0.0246, 0.0836),
       (0.02435, 0.0839), (0.0246, 0.0842), (0.0246, 0.0880), (0.0245, 0.0892), (0.0240, 0.0901), (0.0232, 0.0905), (0.0224, 0.0903),
       (0.0219, 0.0897), (0.0215, 0.0895), (0.017, 0.0895), (0.013, 0.0895), (0.009, 0.0895), (0.005, 0.0895), (0.002, 0.0895), (0, 0.0895), (0, 0.0889), (0.0238, 0.0889), (0.0238, 0.0760), (0.0231, 0.0754)]
HANDLE = [(0.0250, 0.0585), (0.0310, 0.0607), (0.0380, 0.0603), (0.0433, 0.0572), (0.0457, 0.0512), (0.0461, 0.0350), (0.0452, 0.0262),
          (0.0424, 0.0212), (0.0370, 0.0196), (0.0310, 0.0198), (0.0252, 0.0215)]
DZ = 0.0075
JAR = [(r, z if z < 0.06 else z - DZ) for r, z in JAR]; LID = [(r, z - DZ) for r, z in LID]
HANDLE = [(x, 0.0196 + (z - 0.0196) * 0.83) for x, z in HANDLE]
R, CIRC, W, H = 0.0273, 2 * math.pi * 0.0273, 4096, 2048
STEEL = pmat('Lid Steel', (0.86, 0.86, 0.85), 0.24, 1.0)
SIFT = pmat('Sifter', (0.03, 0.03, 0.035), 0.7)

def label_img(name, body, ink, word, cap, zc, wr=1.0):
    def to_px(pl): return [((0.5 + s / CIRC) * W, z / 0.1 * H) for s, z in pl]
    _, L = word_strokes(word, (0, 0), (0, -1), (1, 0), cap, wr)
    strokes, _ = word_strokes(word, (-cap / 2 + 0.0002, zc + L / 2), (0, -1), (1, 0), cap, wr)
    m = stroke_mask(H, W, [to_px(pl) for pl in strokes], 7.5)[..., None]
    col = np.array(body)[None, None, :] * (1 - m) + np.array(ink)[None, None, :] * m
    return np_img(name, col)

def shaker(x0, handle_angle, body, ink, word, cap, holes, wr=1.0):
    img = label_img(word + ' label', body, ink, word, cap, 0.0335, wr)
    glass = tex_mat(word + ' Glass', img, 0.05, coat=1.0)
    hglass = pmat(word + ' Handle Glass', body, 0.05, coat=1.0)
    j = lathe(word + ' Jar', JAR, [glass], seg=192); cyl_uv(j, 0.0, 0.1)
    h = sweep(word + ' Handle', [(x, 0, z) for x, z in HANDLE], hglass, profile=superellipse(0.0056, 0.0034, 2.8, 48), twist_up=(0, 1, 0))
    h.matrix_world = Matrix.Rotation(handle_angle, 4, 'Z')
    lid = lathe(word + ' Lid', LID, [STEEL], seg=192, closed=True, uvs=(1, 20))
    # the holes, punched through the lid top in the shape of the letter
    g = GLYPHS[word[0]]; dots = []
    for pl in g:
        pts = [Vector((px, py, 0)) for px, py in pl]; total = sum((b - a).length for a, b in zip(pts, pts[1:])); n = max(int(total / 0.17), 2)
        acc, k, seglen = 0, 0, [(b - a).length for a, b in zip(pts, pts[1:])]
        for i in range(n + 1):
            d = total * i / n
            while k < len(seglen) - 1 and d > sum(seglen[:k + 1]): k += 1
            t = (d - sum(seglen[:k])) / max(seglen[k], 1e-9); q = pts[k].lerp(pts[k + 1], min(t, 1)); dots.append(q)
    uniq = []
    for q in dots:
        if all((q - u).length > 0.11 for u in uniq): uniq.append(q)
    dots = uniq
    gw = max(max(p[0] for p in pl) for pl in g)
    cs = [cutter_cyl(0.00095, 0.004, ((q.x - gw / 2) * 0.0175, (q.y - 0.5) * 0.0175, 0.0895 - DZ), v=16) for q in dots]
    nb = len(lid.data.vertices); cut(lid, join_cutters(cs)); print('LID', word, nb, '->', len(lid.data.vertices), 'dots', len(dots))
    cyl(0.0237, 0.0004, (0, 0, 0.0886 - DZ), SIFT, v=96)
    for o in P[-4:] if False else []: pass
    for o in (j, h, lid, P[-1]):
        o.matrix_world = Matrix.Translation((x0, 0, 0)) @ o.matrix_world

shaker(-0.0283, math.pi, (0.93, 0.94, 0.93), (0.06, 0.06, 0.07), 'SALT', 0.0128, 'S', 1.3)
shaker(0.0283, 0.0, (0.03, 0.03, 0.035), (0.95, 0.95, 0.94), 'PEPPER', 0.0112, 'P', 1.05)
finish('salt_pepper', 'The Better Home Glass Salt & Pepper Shakers', view=(0.1, -1, 0.35))
print('DONE')
