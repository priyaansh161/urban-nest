# NAALSA stainless spoon rest (5ee6f430, 20.5 x 9.5 cm) and Primeway PP spoon rest (5c8fc071, 20 x 10.5 cm), from their photos.
#   blender -b -P spoon_rests.py -- <outdir> [naalsa|primeway]
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from klib import *
WHICH = sys.argv[sys.argv.index('--') + 2] if len(sys.argv) > sys.argv.index('--') + 2 else 'both'

def dense(a, b, n, tail=0.0, tail_n=0):
    xs = list(np.linspace(a, b - tail, n)); 
    if tail: xs += list(np.linspace(b - tail, b, tail_n + 1))[1:]
    return xs

def naalsa():
    # round bowl with a flat floor, a narrow neck rising to a flat paddle that bends down at the end; matte brushed steel
    reset()
    S = brushed_steel('Matte Steel', 'u', 0.36, (0.80, 0.80, 0.79), polished=True)
    CX, R = -0.0550, 0.0475
    def wc(x): return math.sqrt(max(R * R - (x - CX) ** 2, 0))
    def wn(x): return 0.0132 + 0.0030 * smoothstep((x - 0.0) / 0.05)
    def w(x):
        a, b, k = wc(x), (wn(x) if x > CX else 0.0), 0.005
        m = max(a, b); return m + k * math.log(math.exp((a - m) / k) + math.exp((b - m) / k)) - k * math.log(2) * (1 if abs(a - b) < 1e-9 else 0)
    OX = np.linspace(CX - R, 0.1025, 2400); OW = np.array([w(x) for x in OX])
    OUT = np.concatenate([np.stack([OX, OW], 1), np.stack([OX, -OW], 1)])
    def c(x):
        x0 = CX + 0.30 * R
        if x <= x0: return 0.0012
        if x <= 0.084: return 0.0012 + (0.0400 - 0.0012) * smoothstep((x - x0) / (0.064 - x0)) ** 1.25
        return 0.0400 - 0.0260 * smoothstep((x - 0.084) / 0.0185) ** 0.75
    def d(x): return 0.0013 + 0.0157 * (1 - smoothstep((x - (CX + 0.35 * R)) / (0.002 - (CX + 0.35 * R))))
    def z(x, y):
        dist = float(np.min(np.hypot(OUT[:, 0] - x, OUT[:, 1] - y)))
        Wd = 0.021 if x < CX + 0.4 * R else max(min(0.021, w(x)), 0.004)
        u = min(dist / Wd, 1.0)
        return c(x) + d(x) * (1 - smoothstep(u) ** 0.85)
    xs = dense(CX - R + 0.0005, 0.1025, 300, tail=0.02, tail_n=60)
    shell('Spoon Rest', xs, w, z, 0.0015, S, nv=64, uvscale=(30, 30))
    # the engraved NAALSA label on the paddle
    LBL = pmat('Engraving', (0.42, 0.42, 0.42), 0.6, 0.6)
    slab('Label', rrect(0.0150, 0.0060, 0.0006, 4), 0.0, 0.00008, LBL, bevel=0).location = (0.072, 0, 0.04012)
    text_mesh('NAALSA', 0.0032, S, Matrix.Translation((0.072, 0, 0.04024)), ext=0.00003)
    finish('naalsa', 'NAALSA Stainless Steel Spoon Rest', view=(0.4, -1, 0.75))

def primeway():
    # a shallow charcoal PP dish, wide oval front, the back rising into a curled hook with a hanging slot, a dotted grip pad, 3 feet
    reset()
    PP = pmat('Charcoal PP', (0.24, 0.24, 0.25), 0.55)
    def w(x):
        if x < -0.050: return 0.0525 * math.sqrt(max(1 - ((x + 0.050) / 0.050) ** 2, 0))
        if x < 0.040: return 0.0525 - 0.0085 * ((x + 0.050) / 0.090) ** 2
        b = 0.0440 - 0.0130 * (x - 0.040) / 0.060
        if x > 0.093: b *= math.sqrt(max(1 - ((x - 0.093) / 0.0072) ** 2, 0))
        return b
    def z(x, y):
        v = abs(y) / max(w(x), 1e-4)
        side = 0.003 + 0.015 * (1 - smoothstep((x - 0.005) / 0.075))
        zf = 0.0045 + 0.012 * max(0, (-0.070 - x) / 0.030) ** 2
        if x > 0.030:
            t = (x - 0.030) / 0.070
            zf += 0.0420 * math.sin(min(t / 0.62, 1) * math.pi / 2) ** 2 - 0.0130 * max(0, (t - 0.62) / 0.38) ** 1.6
        return zf + side * v ** 2.6
    xs = dense(-0.1 + 0.00002, 0.1, 300)
    sh = shell('Rest', xs, w, z, 0.0026, PP, nv=64, uvscale=(20, 20))
    hx = 0.066; e = 1e-4; nrm = Vector((-(z(hx + e, 0) - z(hx - e, 0)) / (2 * e), 0, 1)).normalized()
    slot = cutter_cyl(1.0, 1.0, (0, 0, 0), v=48); slot.scale = (0.0050, 0.0105, 0.0055); bpy.ops.object.transform_apply(scale=True)
    slot.matrix_world = Matrix.Translation((hx, 0, z(hx, 0))) @ nrm.to_track_quat('Z', 'Y').to_matrix().to_4x4(); bpy.ops.object.transform_apply(location=True, rotation=True)
    cut(sh, slot)
    for i in range(-9, 10):
        for j in range(-6, 7):
            x = i * 0.0048 - 0.004; y = j * 0.0048 + (0.0024 if i % 2 else 0)
            if ((x + 0.004) / 0.046) ** 2 + (y / 0.030) ** 2 > 1: continue
            bpy.ops.mesh.primitive_uv_sphere_add(radius=0.0011, segments=12, ring_count=6, location=(x, y, z(x, y) - 0.0004))
            d = bpy.context.object; d.scale = (1, 1, 0.8); d.data.materials.append(PP); P.append(d)
    for (x, y) in ((-0.060, 0.0), (0.020, -0.022), (0.020, 0.022)):
        cyl(0.0035, 0.0030, (x, y, z(x, y) - 0.0026 - 0.0012), PP, v=24, bev=0.0006)
    finish('primeway', 'Primeway PP Spoon Rest', view=(0.4, -1, 0.75))

if WHICH in ('naalsa', 'both'): naalsa()
if WHICH in ('primeway', 'both'): primeway()
print('DONE')
