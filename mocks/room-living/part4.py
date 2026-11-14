
# ---------------------------------------------------------------- products: shadow casters for the bake, lamps lit
PL = json.load(open(os.path.join(OUT, 'placements.json')))
CASTERS, LAMPS = [], []
for d in [x for x in PL['staging'] if not x.get('lm')] + PL['products']:
    if 'file' not in d: continue
    made = place(d); CASTERS += made
    if any(k in d for k in ('alignBack', 'alignLeft', 'alignRight')) or d.get('rotY') in (3.14159,) and d['pos'][1] > 0.5:   # wall pieces cast no shadow in the bake: moving one never uncovers a black footprint
        for o in made:
            if o.type == 'MESH': o.visible_shadow = False
    if not d.get('light'): continue
    if d['light'].get('at'): LAMPS.append((d['name'], d['light']['w'], np.array(d['light']['at']))); continue
    p = world_points(made); zmin, zmax = p[:, 2].min(), p[:, 2].max()
    ax = p[p[:, 2] > zmax - 0.02][:, :2].mean(0); rad = lambda z0: np.linalg.norm(p[(p[:, 2] > z0) & (p[:, 2] <= z0 + 0.01)][:, :2] - ax, axis=1)
    r0 = np.linalg.norm(p[p[:, 2] > zmax - 0.04][:, :2] - ax, axis=1).max(); z = zmax - 0.03
    while z > zmin and len(rad(z - 0.01)) and rad(z - 0.01).max() > 0.5 * r0: z -= 0.01
    LAMPS.append((d['name'], d['light']['w'], np.array([ax[0], ax[1], z - 0.03]))); print('LAMP', d['name'], LAMPS[-1][2])
for nm, c in zip(('Brass A', 'Brass B'), LAMP_PTS): LAMPS.append((nm, 22, np.array(c)))
for d in PL['products']:
    if d['name'].startswith('Victorian'):
        pass

if 'wb' in ARGS:       # fast workbench views for checking shapes (no lighting, seconds not minutes)
    scene.render.engine = 'BLENDER_WORKBENCH'; sh = scene.display.shading; sh.light = 'STUDIO'; sh.color_type = 'TEXTURE'
    scene.world = bpy.data.worlds.new('w'); scene.world.color = (0.35, 0.35, 0.35)
    cdw = bpy.data.cameras.new('c'); cw = bpy.data.objects.new('c', cdw); scene.collection.objects.link(cw); scene.camera = cw
    for o in bpy.data.objects:
        if o.name.startswith(('Shell_Ceiling', 'LM_Cornice', 'LM_CeilingRose')): o.hide_render = True
    shots = {'sofa': ((0.7, -0.9, 1.1), (2.3, 0.6, 0.5), 20), 'frontwin': ((-0.7, 0.2, 1.4), (-0.7, -2.1, 1.5), 22), 'cornerA': ((2.3, -1.9, 1.6), (-1.5, 1.2, 0.8), 16),
             'cornerB': ((-2.4, -1.9, 1.5), (1.5, 1.0, 0.8), 16), 'back': ((0.0, -1.0, 1.4), (-0.4, 2.1, 1.0), 20), 'sofa2': ((1.0, 1.0, 1.6), (2.4, -0.6, 0.5), 20)}
    for k, (l, t, ln) in shots.items():
        cdw.lens = ln; cw.location = l; cw.rotation_euler = (Vector(t) - Vector(l)).to_track_quat('-Z', 'Y').to_euler()
        scene.render.resolution_x, scene.render.resolution_y = 1200, 700; scene.render.filepath = OUT + '/wb_%s.png' % k; bpy.ops.render.render(write_still=True)
    for nm in ('Cushion Teal', 'Cushion Teal 2', 'LM_ShuttersF'):
        o = bpy.data.objects[nm]; mn, mx = bounds([o]); print('BOUNDS', nm, [round(v, 2) for v in mn], [round(v, 2) for v in mx], len(o.data.vertices))
    exec(open(os.path.join(OUT, 'check_overlaps_living.py')).read())
    print('DONE wb'); sys.exit(0)

for o in [bpy.data.objects[n] for n in _order if n in bpy.data.objects]: print('TRIS', o.name, sum(len(pg.vertices) - 2 for pg in o.data.polygons))
for o in LMX: lightmap_prep(o, LMRES.get(o.name, 1024 if o.name not in ('LM_Skirting', 'LM_Inlay', 'LM_CeilingRose') else 512))
for ob, ul, vl in SHELL:
    d = 0.009 if 'Ceiling' in ob.name else 0.0045
    if ob.name == 'Shell_Rug': lightmap_prep(ob, (1024, 720), new_uv=False); continue
    lightmap_prep(ob, (max(16, min(1024, round(ul / d))), max(16, min(1024, round(vl / d)))), new_uv=False)

# ---------------------------------------------------------------- lights (night: chandelier candles, brass lamps, street lamps)
def area(name, loc, sx, sy, energy, color, rot):
    ld = bpy.data.lights.new(name, 'AREA'); ld.energy = energy; ld.color = color; ld.shape = 'RECTANGLE'; ld.size = sx; ld.size_y = sy
    lo = bpy.data.objects.new(name, ld); lo.location = loc; lo.rotation_euler = rot; scene.collection.objects.link(lo)
def aim(lo, target): lo.rotation_euler = (Vector(target) - lo.location).to_track_quat('-Z', 'Y').to_euler()
MOON = (0.62, 0.72, 1.0)
for nm, loc, tgt, sz in (('Moon R', (X1 + 1.1, WR['c'], 2.5), (X1 - 2.2, WR['c'] - 0.2, 0.0), (1.4, 1.9)), ('Moon F', (WF['c'], Y0 - 1.1, 2.5), (WF['c'] + 0.2, Y0 + 2.2, 0.0), (1.4, 1.9))):
    area(nm, loc, sz[0], sz[1], 520, MOON, (0, 0, 0)); aim(bpy.data.objects[nm], tgt)
def spot(name, loc, target, w, deg, blend=0.7, color=WARM):
    ld = bpy.data.lights.new(name, 'SPOT'); ld.energy = w; ld.color = color; ld.spot_size = math.radians(deg); ld.spot_blend = blend; ld.shadow_soft_size = 0.03
    lo = bpy.data.objects.new(name, ld); lo.location = Vector(loc); scene.collection.objects.link(lo); aim(lo, target)
for i_, (x_, y_) in enumerate(DL_SPOTS): spot('DL%d' % i_, (x_, y_, H - DROP_ - 0.02), (x_, y_, 0.0), 30, 80, 0.75)       # downlights: pools on the floor and scallops down the walls
for nm, loc, tgt in (('Pic Gond', (-1.2, Y1 - 0.30, 2.62), (-1.2, Y1, 1.55)), ('Pic Paper', (1.6, Y0 + 0.30, 2.62), (1.6, Y0, 1.55)), ('Pic Artsense', (X0 + 0.30, -1.2, 2.62), (X0, -1.2, 1.55)), ('Pic Clock', (X1 - 0.30, -1.3, 2.62), (X1, -1.3, 1.6))):
    spot(nm, loc, tgt, 45, 55, 0.85)                                                                                       # picture lights wash each frame
for nm, loc, rot in (('Cove L', (-XI + 0.05, 0, H - 0.02), (0, math.radians(-38), 0)), ('Cove R', (XI - 0.05, 0, H - 0.02), (0, math.radians(38), 0))):
    area(nm, loc, 0.12, 2 * YI - 0.1, 40, WARM, rot)
for nm, loc, rot in (('Cove B', (0, YI - 0.05, H - 0.02), (math.radians(-38), 0, 0)), ('Cove F', (0, -YI + 0.05, H - 0.02), (math.radians(38), 0, 0))):
    area(nm, loc, 2 * XI - 0.1, 0.12, 40, WARM, rot)
area('Fill', (0.15, 0.1, H - 0.05), 4.0, 3.0, 30, (1.0, 0.92, 0.82), (0, 0, 0))
for nm, w, c in LAMPS + [('Chandelier', 160, np.array([0.15, 0.1, 2.30])), ('Chandelier Low', 40, np.array([0.15, 0.1, 2.0]))]:
    ld = bpy.data.lights.new('Lamp', 'POINT'); ld.energy = w; ld.color = WARM; ld.shadow_soft_size = 0.05
    lo = bpy.data.objects.new('Lamp ' + nm, ld); lo.location = Vector(c.tolist()); scene.collection.objects.link(lo)
world = bpy.data.worlds.new('W'); scene.world = world; world.use_nodes = True
world.node_tree.nodes['Background'].inputs['Color'].default_value = (0.04, 0.05, 0.08, 1); world.node_tree.nodes['Background'].inputs['Strength'].default_value = 0.3

# ---------------------------------------------------------------- bake light into every lightmap
scene.render.engine = 'CYCLES'; scene.cycles.device = 'CPU'
if not QUICK:
    scene.cycles.samples = 12 if FAST else 128
    scene.render.bake.target = 'IMAGE_TEXTURES'; scene.render.bake.margin = 8; scene.render.bake.use_clear = True
    bpy.ops.object.select_all(action='DESELECT')
    for o, _, _ in LM: o.select_set(True)
    bpy.context.view_layer.objects.active = LM[0][0]
    bpy.ops.object.bake(type='DIFFUSE', pass_filter={'DIRECT', 'INDIRECT'}, margin=8, use_clear=True)
    BAKED = {}
    for o, img, uvn in LM:
        w, h = img.size; BAKED[o.name] = gblur(np.array(img.pixels[:], dtype=np.float32).reshape(h, w, 4)[..., :3])
    room_names = {ob.name for ob, _, _ in SHELL if "Rug" not in ob.name}
    lum = np.concatenate([BAKED[n].reshape(-1, 3) for n in room_names]) @ np.array([0.2126, 0.7152, 0.0722])
    gain = 0.92 / max(1e-4, np.percentile(lum, 98.5)); print('BAKE gain', round(float(gain), 3), 'p50', round(float(np.percentile(lum, 50)), 3))
    LM_IMG = {}
    for o, img, uvn in LM:
        a = np.clip(BAKED[o.name] * gain, 0, 1); h, w = a.shape[:2]
        a = np.where(a <= 0.0031308, a * 12.92, 1.055 * np.power(a, 1 / 2.4) - 0.055)
        LM_IMG[o.name] = save_img('LM_' + o.name, a)
        print('LIGHTMAP', o.name, w, 'px, mean', round(float(a.mean()), 3))


# ---------------------------------------------------------------- previews: front, corner (like the reference), plan
scene.view_settings.view_transform = 'AgX'; scene.cycles.samples = 14 if QUICK else 96; scene.cycles.use_denoising = True
cam_d = bpy.data.cameras.new('Cam'); cam_d.lens = 18
cam = bpy.data.objects.new('Cam', cam_d); scene.collection.objects.link(cam)
tag = 'quick' if QUICK else 'v1'
def shot(name, loc, tgt, lens, res):
    cam_d.lens = lens; cam.location = loc; cam.rotation_euler = (Vector(tgt) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    if FAST or 'nopreview' in ARGS: return
    scene.camera = cam; scene.render.resolution_x, scene.render.resolution_y = res; scene.render.filepath = OUT + '/living_%s_%s.png' % (tag, name); bpy.ops.render.render(write_still=True)
R = (1000, 560) if QUICK else (1800, 1000)
shot('front', (0.0, Y0 + 0.15, 1.35), (0.0, Y1, 1.2), 18, R)
shot('corner', (-2.35, -1.9, 1.15), (1.3, 0.9, 1.0), 16, R)          # the reference's viewpoint: low, from a corner
shot('corner2', (2.3, -1.85, 1.5), (-1.2, 1.0, 1.1), 16, R)
shot('door', (-2.4, 1.7, 1.5), (1.4, -0.4, 0.9), 16, R)
shot('sofa', (0.7, -0.9, 1.1), (2.3, 0.6, 0.5), 20, R)
hide = [o for o, _, _ in SHELL if 'Ceiling' in o.name] + [o for o in LMX if o.name in ('LM_Cornice', 'LM_CeilingRose')] + [o for o in CASTERS if 'chandelier' in o.name.lower() or 'Chandelier' in o.name]
for o in hide: o.hide_render = True
pd = bpy.data.cameras.new('Plan'); pd.type = 'ORTHO'; pd.ortho_scale = 6.0
pc = bpy.data.objects.new('Plan', pd); scene.collection.objects.link(pc); pc.location = (0, 0, 8); pc.rotation_euler = (0, 0, 0)
if not (FAST or 'nopreview' in ARGS): scene.camera = pc; scene.render.resolution_x = scene.render.resolution_y = 1000; scene.render.filepath = OUT + '/living_%s_plan.png' % tag; bpy.ops.render.render(write_still=True)
for o in hide: o.hide_render = False
if QUICK: print('DONE quick'); sys.exit(0)

# ---------------------------------------------------------------- export: products out (the viewer places them), lightmaps in as emissive
for o in CASTERS: bpy.data.objects.remove(o)
for o, _, uvn in LM:
    for slot in o.material_slots:
        nt = slot.material.node_tree; b = nt.nodes['Principled BSDF']
        nt.nodes.remove(nt.nodes['LM_BAKE'])
        for n_ in list(nt.nodes):
            if n_.type == 'TEX_IMAGE' and not n_.inputs['Vector'].is_linked and uvn != o.data.uv_layers[0].name:
                um = nt.nodes.new('ShaderNodeUVMap'); um.uv_map = o.data.uv_layers[0].name; nt.links.new(um.outputs['UV'], n_.inputs['Vector'])
        t = nt.nodes.new('ShaderNodeTexImage'); t.image = LM_IMG[o.name]
        um = nt.nodes.new('ShaderNodeUVMap'); um.uv_map = uvn; nt.links.new(um.outputs['UV'], t.inputs['Vector'])
        nt.links.new(t.outputs['Color'], b.inputs['Emission Color']); b.inputs['Emission Strength'].default_value = 1.0
    o.data.uv_layers.active = o.data.uv_layers[0]

kw = dict(filepath=OUT + '/living_v1.glb', export_format='GLB', export_apply=True, export_cameras=False, export_lights=False, export_image_format='JPEG', export_jpeg_quality=85)
bpy.ops.export_scene.gltf(**kw)
bpy.ops.wm.save_as_mainfile(filepath=OUT + '/living_v1.blend'); print('DONE', round(os.path.getsize(OUT + '/living_v1.glb') / 1e6, 2), 'MB')
