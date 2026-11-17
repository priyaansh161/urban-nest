# "World Mart Woodshoppe Cutlery Case, Shisham Wood Caddy" (ade2831e), from its listing photos (20 W x 13 D x 10 H cm):
# a low open tray (5 cm walls) in red-brown shisham; on the left a full-depth slot for napkins behind a divider; at the
# back right a taller box (10 cm) split into three cells for spoons, forks and knives; open floor in front of it for the
# grinders. "World Mart" with its globe-and-M mark burnt into the front, low on the left.
#   blender -b -P caddy.py -- <outdir>
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'room-kitchen', 'products'))
from klib import *

reset()
WD = wood('Shisham', (0.30, 0.13, 0.065), (0.52, 0.27, 0.15), 0.42, contrast=0.5, along='v')
BURN = pmat('Burnt Mark', (0.09, 0.04, 0.02), 0.6)
T = 0.008                                         # board thickness
W, D, HL, HT = 0.20, 0.13, 0.05, 0.10
def board(x0, x1, y0, y1, z0, z1):
    o = slab('Board', [(x0, y0), (x1, y0), (x1, y1), (x0, y1)], z0, z1, WD, bevel=0.0008, bseg=2); cube_uv(o, 0.25); return o
x0, x1, y0, y1 = -W / 2, W / 2, -D / 2, D / 2
board(x0, x1, y0, y1, 0, T)                                            # floor
board(x0, x1, y0, y0 + T, T, HL)                                       # front
board(x0, x0 + T, y0 + T, y1, T, HL)                                   # left end
XD = x0 + 0.055                                                        # napkin slot divider
board(XD, XD + T, y0 + T, y1, T, HL)
# the tall box at the back right: back wall full height across the whole caddy behind it
TB0, TB1 = XD, x1                                                     # tall box spans from the divider to the right end
TY = y1 - 0.062                                                        # its front face
board(x0 + T, x1, y1 - T, y1, T, HL)                                   # back (low part, behind the napkin slot)
board(TB0, x1, y1 - T, y1, HL, HT)                                     # back, the tall part
board(x1 - T, x1, y0 + T, y1 - T, T, HL)                               # right end, low
board(x1 - T, x1, TY, y1 - T, HL, HT)                                  # right end, tall part
board(TB0, TB0 + T, TY, y1 - T, HL, HT)                                # tall box left side (sits on the divider)
board(TB0 + T, x1 - T, TY, TY + T, T, HT)                              # tall box front
for k in (1, 2):                                                       # three cells
    xc = TB0 + T + (x1 - T - TB0 - T) * k / 3
    board(xc - T / 2, xc + T / 2, TY + T, y1 - T, T, HT - 0.004)
# the mark: a small globe over an M, "World Mart" in script below it, burnt in on the front, left
mw = Matrix.Translation((x0 + 0.030, y0 - 0.0002, 0.016)) @ Matrix.Rotation(math.pi / 2, 4, 'X')
text_mesh('World Mart', 0.0065, BURN, mw, ext=0.00012)
text_mesh('M', 0.010, BURN, Matrix.Translation((x0 + 0.030, y0 - 0.0002, 0.028)) @ Matrix.Rotation(math.pi / 2, 4, 'X'), ext=0.00012)
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.0028, location=(x0 + 0.030, y0 - 0.0001, 0.037), segments=24, ring_count=12)
g = bpy.context.object; g.scale = (1, 0.06, 1); g.data.materials.append(BURN); P.append(g)
finish('caddy', 'Woodshoppe Shisham Cutlery Caddy', view=(-0.5, -1, 0.7))
print('DONE')
