# v2 changes to build_kitchen_v1.py (his review, 15 Nov): real appliance faces from their photos, a deep sink with a proper
# gooseneck tap, a draped towel, an open niche in the uppers. Applied as text edits; run once (blender --python-expr).
import sys
p = 'build_kitchen_v1.py'; s = open(p, encoding='utf8').read()
def R(a, b):
    global s
    if a not in s: raise SystemExit('missing: ' + a[:80])
    s = s.replace(a, b)

# ---- appliance faces: photo textures on the fronts (lightmapped like the rest, so they bake with the room)
R("LAM = (0.60, 0.41, 0.23)", '''LAM = (0.60, 0.41, 0.23)
APP = os.path.join(OUT, 'appliances')
def face_mat(name, file, rough):
    im = bpy.data.images.load(os.path.join(APP, file)); im.pack()
    return pbr(name, im, None, None, rough=rough)
def face_uv(o, axis_u, axis_v, u0, u1, v0, v1):
    """Fit the image over the object: u along axis_u from u0..u1, v along axis_v from v0..v1 (world)."""
    me = o.data; uv = me.uv_layers[0] if me.uv_layers else me.uv_layers.new(name='UV')
    for poly in me.polygons:
        for li, vi in zip(poly.loop_indices, poly.vertices):
            c = me.vertices[vi].co
            uv.data[li].uv = ((c[axis_u] - u0) / (u1 - u0), (c[axis_v] - v0) / (v1 - v0))''')
R("'steeldark': mat('Steel Shadow', (0.14, 0.145, 0.155, 1), 0.35),", '''\'steeldark\': mat('Steel Shadow', (0.14, 0.145, 0.155, 1), 0.35),
    'fridge': face_mat('Samsung Side-by-Side Doors', 'fridge_front.png', 0.3),
    'oven': face_mat('Elica Built-in Oven Front', 'oven_front.png', 0.08),
    'micro': face_mat('Electrolux Built-in Microwave Front', 'microwave_front.png', 0.1),
    'brushed': mat('Fridge Side Steel', (0.40, 0.41, 0.43, 1), 0.35),''')

# the oven and the microwave: their real fronts (60 x 60 and 60 x 39 cm, as listed), set into the oak column
R("""tall += [bx('Oven', FX, FX + 0.012, AY0 + 0.01, AY1 - 0.01, 0.50, 1.10, M['blackglass'], 0.003),
         bx('Oven Window', FX + 0.012, FX + 0.014, AY0 + 0.07, AY1 - 0.07, 0.56, 0.92, M['matblack']),
         bx('Oven Handle', FX + 0.03, FX + 0.045, AY0 + 0.05, AY1 - 0.05, 0.98, 1.0, M['steel'], 0.004),
         bx('Oven Panel', FX + 0.012, FX + 0.014, AY0 + 0.05, AY1 - 0.05, 1.01, 1.08, M['steeldark']),
         bx('Microwave', FX, FX + 0.012, AY0 + 0.01, AY1 - 0.01, 1.16, 1.56, M['blackglass'], 0.003),
         bx('Microwave Window', FX + 0.012, FX + 0.014, AY0 + 0.04, AY1 - 0.16, 1.21, 1.51, M['matblack']),
         bx('Microwave Panel', FX + 0.012, FX + 0.014, AY1 - 0.13, AY1 - 0.04, 1.21, 1.51, M['steeldark'])]
for k in range(3): tall.append(cyl('Knob', (FX + 0.02, AY0 + 0.12 + k * 0.08, 1.045), 0.012, 0.02, M['steel'], rot=(0, math.pi / 2, 0), seg=16))""",
"""ACX = (AY0 + AY1) / 2
OV = bx('Oven', FX - 0.01, FX + 0.008, ACX - 0.2975, ACX + 0.2975, 0.505, 1.100, M['oven'], 0.002)
face_uv(OV, 1, 2, ACX + 0.2975, ACX - 0.2975, 0.505, 1.100)      # faces +x: the photo's left is the room's +y side
MW = bx('Microwave', FX - 0.01, FX + 0.008, ACX - 0.2975, ACX + 0.2975, 1.160, 1.549, M['micro'], 0.002)
face_uv(MW, 1, 2, ACX + 0.2975, ACX - 0.2975, 1.160, 1.549)
tall += [OV, MW, bx('Oven Handle', FX + 0.008, FX + 0.034, ACX - 0.245, ACX + 0.245, 1.002, 1.016, M['steel'], 0.005)]
for dy in (0.205, 0.0, -0.205):                                  # the three steel dials standing out of the glass
    tall.append(cyl('Dial', (FX + 0.018, ACX + dy, 1.063), 0.019, 0.02, M['steel'], rot=(0, math.pi / 2, 0), seg=32))""")

# the fridge: the Samsung's own doors, steel sides, real bar handles
R("""fr = [bx('Fridge Body', X0 + 0.02, X0 + 0.72, FY0, FY1, 0.03, 1.80, M['steel'], 0.012), bx('Fridge Feet', X0 + 0.05, X0 + 0.68, FY0 + 0.03, FY1 - 0.03, 0, 0.03, M['matblack']),
      bx('Fridge Seam', X0 + 0.72, X0 + 0.723, FY0 + 0.01, FY1 - 0.01, 1.22, 1.226, M['steeldark']),
      bx('Fridge Seam', X0 + 0.72, X0 + 0.723, (FY0 + FY1) / 2 - 0.002, (FY0 + FY1) / 2 + 0.002, 0.04, 1.79, M['steeldark'])]
for y_ in ((FY0 + FY1) / 2 - 0.045, (FY0 + FY1) / 2 + 0.045):
    fr.append(bx('Fridge Handle', X0 + 0.723, X0 + 0.745, y_ - 0.008, y_ + 0.008, 0.70, 1.60, M['steel'], 0.004))""",
"""FB = bx('Fridge Body', X0 + 0.02, X0 + 0.68, FY0 + 0.005, FY1 - 0.005, 0.04, 1.80, M['brushed'], 0.006)
FD = bx('Fridge Doors', X0 + 0.68, X0 + 0.73, FY0 + 0.005, FY1 - 0.005, 0.04, 1.80, M['fridge'], 0.008)
face_uv(FD, 1, 2, FY1 - 0.005, FY0 + 0.005, 0.04, 1.80)          # faces +x: the photo's left (freezer) is the room's +y side
fr = [FB, FD, bx('Fridge Feet', X0 + 0.05, X0 + 0.66, FY0 + 0.04, FY1 - 0.04, 0, 0.04, M['matblack'])]
GY = (FY1 - 0.005) - (FY1 - FY0 - 0.01) * (400 / 697)            # where the photo's door gap falls along the run
for y_ in (GY - 0.035, GY + 0.035):                              # vertical bar handles either side of the gap
    fr.append(bx('Fridge Handle', X0 + 0.735, X0 + 0.752, y_ - 0.009, y_ + 0.009, 0.62, 1.42, M['steel'], 0.005))
    for z_ in (0.64, 1.40): fr.append(bx('Handle Post', X0 + 0.728, X0 + 0.737, y_ - 0.007, y_ + 0.007, z_ - 0.012, z_ + 0.012, M['steel'], 0.002))""")

# ---- the sink: a real 20 cm deep undermount bowl with rounded corners and a drain; a proper single-lever gooseneck tap
R("""sk += [bx('Sink Floor', SX0, SX1, SY0, SY1, SZ - 0.01, SZ, M['steeldark']), bx('Sink Wall', SX0 - 0.01, SX0, SY0, SY1, SZ, 0.88, M['steel']),
       bx('Sink Wall', SX1, SX1 + 0.01, SY0, SY1, SZ, 0.88, M['steel']), bx('Sink Wall', SX0, SX1, SY0 - 0.01, SY0, SZ, 0.88, M['steel']),
       bx('Sink Wall', SX0, SX1, SY1, SY1 + 0.01, SZ, 0.88, M['steel'])]
sk.append(cyl('Drain', (SINK[0] + 0.12, SINK[1], SZ + 0.001), 0.04, 0.003, M['steeldark'], seg=32))
tp = [(SINK[0] - 0.10, SY1 + 0.05, CT), (SINK[0] - 0.10, SY1 + 0.05, CT + 0.25), (SINK[0] - 0.10, SY1 + 0.03, CT + 0.33), (SINK[0] - 0.10, SY1 - 0.04, CT + 0.355), (SINK[0] - 0.10, SY1 - 0.11, CT + 0.33), (SINK[0] - 0.10, SY1 - 0.13, CT + 0.27)]
sk.append(SL.tube('Tap', tp, [0.014, 0.013, 0.012, 0.012, 0.012, 0.013], M['matblack'], seg=16))
sk.append(cyl('Tap Base', (SINK[0] - 0.10, SY1 + 0.05, CT + 0.015), 0.025, 0.03, M['matblack'], seg=24))
sk.append(box('Tap Lever', (SINK[0] - 0.10 + 0.04, SY1 + 0.05, CT + 0.12), (0.07, 0.012, 0.012), M['matblack'], 0.004))""",
"""M['sinksteel'] = mat('Sink Satin Steel', (0.46, 0.47, 0.49, 1), 0.38)
SZ = 0.66                                                        # bowl floor: 20 cm below the counter top
bowl = box('Sink Bowl', (SINK[0], SINK[1], (SZ + 0.862) / 2 - 0.006), (SINK[2] + 0.02, SINK[3] + 0.02, 0.862 - SZ + 0.012), M['sinksteel'], 0.03, segs=6)
inner = box('cut', (SINK[0], SINK[1], (SZ + 0.95) / 2), (SINK[2], SINK[3], 0.95 - SZ), M['sinksteel'], 0.025, segs=6); cut(bowl, inner)
sk.append(bowl)
sk.append(cyl('Drain', (SINK[0] + 0.14, SINK[1] - 0.04, SZ + 0.001), 0.045, 0.004, M['steeldark'], seg=48))
sk.append(cyl('Drain Cap', (SINK[0] + 0.14, SINK[1] - 0.04, SZ + 0.004), 0.030, 0.004, M['sinksteel'], seg=48))
TX, TY = SINK[0] - 0.12, SY1 + 0.055                             # the tap: a round body, an arched spout over the bowl, a side lever
tb = SL.lathe('Tap Body', [(0.0, CT), (0.028, CT), (0.028, CT + 0.008), (0.020, CT + 0.014), (0.017, CT + 0.20), (0.0, CT + 0.20)], M['matblack'], seg=40)
tb.location = (TX, TY, 0); sk.append(tb)
arc = [(TX, TY - 0.065 + 0.065 * math.cos(a), CT + 0.19 + 0.17 * math.sin(a)) for a in np.linspace(0.0, math.pi, 28)]
arc += [(TX, arc[-1][1], arc[-1][2] - 0.04)]
sk.append(SL.tube('Tap Spout', arc, [0.0135] * len(arc), M['matblack'], seg=24))
ae = SL.lathe('Tap Aerator', [(0.0, 0.0), (0.0145, 0.0), (0.0145, 0.022), (0.0, 0.022)], M['matblack'], seg=32); ae.location = (TX, arc[-1][1], arc[-1][2] - 0.022); sk.append(ae)
sk.append(SL.tube('Tap Lever', [(TX + 0.015, TY, CT + 0.15), (TX + 0.05, TY, CT + 0.165), (TX + 0.085, TY, CT + 0.172)], [0.008, 0.007, 0.006], M['matblack'], seg=16))""")

# ---- an open niche in the right-wall uppers (as in his MK1): white inside, two shelves for jars and mugs
R("upper_x(-1.40, 0.08, [-0.88, -0.40]); upper_x(0.83, Y1, [1.25])",
"""upper_x(-1.40, -0.92, []); upper_x(-0.40, 0.08, []); upper_x(0.83, Y1, [1.25])
ON = (-0.92, -0.40)                                               # the open niche between them
M['shelfwhite'] = mat('Shelf White Laminate', (0.90, 0.89, 0.86, 1), 0.5)
up += [bx('Niche Back', X1 - 0.02, X1, ON[0], ON[1], UZ0, UZ1, M['shelfwhite']), bx('Niche Side', X1 - 0.35, X1, ON[0], ON[0] + 0.018, UZ0, UZ1, M['oak']),
       bx('Niche Side', X1 - 0.35, X1, ON[1] - 0.018, ON[1], UZ0, UZ1, M['oak']), bx('Niche Base', X1 - 0.35, X1, ON[0], ON[1], UZ0, UZ0 + 0.018, M['oak']),
       bx('Niche Top', X1 - 0.35, X1, ON[0], ON[1], UZ1 - 0.018, UZ1, M['oak']), bx('Niche Shelf', X1 - 0.33, X1 - 0.02, ON[0] + 0.018, ON[1] - 0.018, UZ0 + 0.40, UZ0 + 0.418, M['oak'])]""")

# ---- the towel: a real drape, thin cotton folded over the drawer profile
R("""_tw = box('Towel', (RX - 0.018, 0.20, 0.62), (0.012, 0.24, 0.36), M['towel'], 0.005); _tw.rotation_euler.x = 0.04; STAGE.append(_tw); world_uv(_tw, 0.3)
STAGE.append(box('Towel Fold', (RX - 0.006, 0.20, 0.785), (0.03, 0.24, 0.025), M['towel'], 0.01))""",
'''def towel(xf, yc, ztop, w=0.26, front=0.36, back=0.12):
    """A cotton towel hung over a bar at (xf, ztop): a short back flap, a longer front flap, soft folds, a slight sway."""
    NU, NV = 28, 46; L = back + 0.04 + front; V, F, UV = [], [], []
    for j in range(NV + 1):
        sv = j / NV * L
        for i in range(NU + 1):
            u = i / NU - 0.5; y = yc + u * w
            fold = 0.004 * math.sin(u * 22 + sv * 9) + 0.003 * math.sin(u * 47 - sv * 5)
            if sv < back: x, z = xf + 0.012 + fold * 0.5, ztop - (back - sv)
            elif sv < back + 0.04:
                a = (sv - back) / 0.04 * math.pi; x, z = xf + 0.006 * math.cos(a) + 0.006, ztop + 0.006 * math.sin(a)
            else:
                d = sv - back - 0.04; x, z = xf - 0.004 - fold - 0.012 * (d / front) ** 2, ztop - d
                y += 0.01 * (d / front) ** 2 * math.sin(u * 3)
            V.append((x, y, z)); UV.append((i / NU, sv / L * 1.4))
    for j in range(NV):
        for i in range(NU): F.append((j * (NU + 1) + i, j * (NU + 1) + i + 1, (j + 1) * (NU + 1) + i + 1, (j + 1) * (NU + 1) + i))
    o = SL.mesh_obj('Towel', V, F, M['towel'], UV)
    md = o.modifiers.new('s', 'SOLIDIFY'); md.thickness = 0.003
    bpy.ops.object.select_all(action='DESELECT'); o.select_set(True); bpy.context.view_layer.objects.active = o; bpy.ops.object.modifier_apply(modifier='s')
    STAGE.append(o)
towel(RX - 0.012, 0.20, 0.79)''')
open(p, 'w', encoding='utf8').write(s); print('patched')
