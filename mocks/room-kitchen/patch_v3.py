# v3 changes to build_kitchen_v1.py (his review, 15 Nov, composition): an open utensil drawer under the hob, a brass hook
# for the apron, a neem spatula resting on the spoon rest, the towel on the counter edge, the soap on the sink mat; the
# box-built mixer and chimney go (Meshy builds of a real Bajaj mixer and Elica hood stand in placements.json staging).
p = 'build_kitchen_v1.py'; s = open(p, encoding='utf8').read()
def R(a, b):
    global s
    if a not in s: raise SystemExit('missing: ' + a[:80])
    s = s.replace(a, b)

# ---- the open drawer: the top drawer of the bank under the hob (y 0.08..0.83, z 0.56..0.80), pulled out 40 cm
R("base_run_x(-1.40, Y1, [-0.98, -0.52, 0.08, 0.83], drawers=(0.08, 0.83, [0.33, 0.56]))",
"""base_run_x(-1.40, Y1, [-0.98, -0.52, 0.08, 0.83], drawers=(0.08, 0.83, [0.33]))
DR = dict(y0=0.085, y1=0.825, z0=0.565, z1=0.795, out=0.40)      # the open drawer
base.append(bx('Drawer Cavity', RX + 0.019, RX + 0.021, DR['y0'], DR['y1'], DR['z0'], DR['z1'], M['gap']))""")
R("bases = join(base, 'LM_Bases')", """for i_, f_ in enumerate(base):
    if f_.name.startswith('Front') and abs(f_.location.x - (RX + 0.01)) < 0.02 and f_.dimensions.y > 3.0:   # cut the open drawer's mouth in the right-run front
        cut(f_, box('cut', (RX + 0.01, (DR['y0'] + DR['y1']) / 2, (DR['z0'] + DR['z1']) / 2), (0.06, DR['y1'] - DR['y0'], DR['z1'] - DR['z0']), M['gap']))
xf_ = RX - DR['out']                                               # the drawer itself: navy front, steel profile, white box inside
M['drawerin'] = mat('Drawer Inside', (0.86, 0.85, 0.83, 1), 0.5)
base += [bx('Drawer Front', xf_ - 0.02, xf_, DR['y0'], DR['y1'], DR['z0'] - 0.003, DR['z1'] + 0.003, M['navy']),
         bx('Drawer Profile', xf_ - 0.032, xf_ - 0.02, DR['y0'] + 0.01, DR['y1'] - 0.01, DR['z1'] - 0.03, DR['z1'] - 0.012, M['profile']),
         bx('Drawer Bottom', xf_, RX + 0.50, DR['y0'] + 0.01, DR['y1'] - 0.01, DR['z0'] + 0.005, DR['z0'] + 0.017, M['drawerin']),
         bx('Drawer Side', xf_, RX + 0.50, DR['y0'] + 0.01, DR['y0'] + 0.022, DR['z0'] + 0.005, DR['z1'] - 0.06, M['drawerin']),
         bx('Drawer Side', xf_, RX + 0.50, DR['y1'] - 0.022, DR['y1'] - 0.01, DR['z0'] + 0.005, DR['z1'] - 0.06, M['drawerin']),
         bx('Drawer Back', RX + 0.488, RX + 0.50, DR['y0'] + 0.01, DR['y1'] - 0.01, DR['z0'] + 0.005, DR['z1'] - 0.06, M['drawerin']),
         bx('Drawer Divider', xf_, RX + 0.50, 0.44, 0.452, DR['z0'] + 0.017, DR['z0'] + 0.08, M['drawerin'])]
bases = join(base, 'LM_Bases')""")

# ---- the box mixer and the box chimney go
R("""ch = [bx('Chimney Body', X1 - 0.30, X1 - 0.02, 0.18, 0.73, 1.80, 2.05, M['hoodblack'], 0.004)]
vis = box('Visor', (X1 - 0.30, 0.455, 1.74), (0.40, 0.62, 0.008), M['hoodglass'], rot=(0, math.radians(-28), 0)); ch.append(vis)
ch.append(bx('Visor Trim', X1 - 0.30, X1 - 0.02, 0.17, 0.74, 1.77, 1.80, M['steel']))
chimney = join(ch, 'LM_Chimney'); world_uv(chimney, 1.0); lm(chimney, 512)""", "# (the chimney is the Elica hood in placements.json staging)")
R("""STAGE.append(box('Mixer Base', (mx_, my_, CT + 0.085), (0.20, 0.26, 0.17), M['white'], 0.04))
STAGE.append(box('Mixer Panel', (mx_ - 0.101, my_, CT + 0.07), (0.004, 0.14, 0.10), M['lilac'], 0.01))
cyl('Mixer Knob', (mx_ - 0.11, my_, CT + 0.07), 0.022, 0.02, M['white'], rot=(0, math.pi / 2, 0)); STAGE.append(bpy.context.active_object)
lathe('Mixer Jar', [(0, 0), (0.05, 0), (0.06, 0.02), (0.075, 0.17), (0.08, 0.175), (0, 0.175)], M['ss'], (mx_, my_, CT + 0.17))
lathe('Mixer Lid', [(0, 0), (0.082, 0), (0.08, 0.02), (0.03, 0.035), (0.02, 0.06), (0, 0.06)], M['lilac'], (mx_, my_, CT + 0.345))""",
"# (the mixer is the Bajaj in placements.json staging)")

# ---- soap on the sink mat; the towel over the counter's J-profile by the prep area; the apron hook; the neem spatula
R("M['soap'], (-0.30, 1.62, CT))", "M['soap'], (0.50, 1.47, CT + 0.012))")
R("towel(RX - 0.012, 0.20, 0.79)", "towel(RX - 0.004, -1.05, 0.845, back=0.03, front=0.34)")
R("for o in STAGE: o.select_set(False)\n\n# ---------------------------------------------------------------- products", """M['brasshook'] = mat('Brass Hook (lightmapped look)', (0.72, 0.52, 0.22, 1), 0.35, 0.0)
hk = [bx('Hook Plate', FX, FX + 0.006, -1.27, -1.23, 1.52, 1.58, M['brasshook'], 0.002),
      SL.tube('Hook', [(FX + 0.006, -1.25, 1.555), (FX + 0.045, -1.25, 1.555), (FX + 0.055, -1.25, 1.575), (FX + 0.05, -1.25, 1.59)], [0.005] * 4, M['brasshook'], seg=12)]
STAGE.extend(hk)
M['neem'] = SL.mat('Neem Wood', (0.62, 0.42, 0.24), 0.55)
def spatula(x, y, z, rz, tilt=0.06):
    \"\"\"A flat neem-wood spatula (like the Vanam set's turner): 30 cm, a squared blade, a round handle.\"\"\"
    from mathutils import Matrix
    P_ = [box('Spatula Blade', (0.0, 0.0, 0.0), (0.085, 0.06, 0.005), M['neem'], 0.002),
          SL.tube('Spatula Neck', [(0.04, 0, 0), (0.09, 0, 0.004)], [0.009, 0.007], M['neem'], seg=12),
          SL.tube('Spatula Handle', [(0.09, 0, 0.004), (0.21, 0, 0.012), (0.255, 0, 0.014)], [0.0075, 0.009, 0.0085], M['neem'], seg=14)]
    o = SL.join(P_, 'Neem Spatula')
    o.matrix_world = Matrix.Translation((x, y, z)) @ Matrix.Rotation(rz, 4, 'Z') @ Matrix.Rotation(-tilt, 4, 'Y')
    STAGE.append(o)
spatula(1.02, -0.10, CT + 0.022, math.radians(-82))
for o in STAGE: o.select_set(False)

# ---------------------------------------------------------------- products""")
open(p, 'w', encoding='utf8').write(s); print('patched v3')
