
# ---------------------------------------------------------------- products: shadow casters for the bake (the viewer places them live)
def place_fp(d):
    made = place(d)
    if 'footprint' in d:                                            # the viewer's footprint fit: x and depth scaled to the listed size
        root = made[-2]; inner = made[-1]; new = made[:-2]
        rz = root.rotation_euler.z; root.rotation_euler.z = 0; bpy.context.view_layer.update()
        mn, mx = bounds(new); sz = mx - mn
        inner.scale = (inner.scale.x * d['footprint'][0] / sz.x, inner.scale.y * d['footprint'][1] / sz.y, inner.scale.z)
        bpy.context.view_layer.update(); mn, mx = bounds(new); c = (mn + mx) / 2
        root.location.x -= c.x - root.location.x; root.location.y -= c.y - root.location.y
        root.rotation_euler.z = rz; bpy.context.view_layer.update()
    return made
PL = json.load(open(os.path.join(OUT, 'placements.json'), encoding='utf8'))
CASTERS = []; PLACED = {}
for d in PL['products'] + [x for x in PL.get('staging', []) if not x.get('lm')]:
    if 'file' in d and os.path.exists(os.path.join(OUT, 'products', d['file'])):
        made = place_fp(d); CASTERS += made; PLACED[d['name']] = made
if 'bounds' in ARGS:
    for n, objs in PLACED.items():
        mn, mx = bounds(objs); print('BOUNDS %-40s x %6.3f %6.3f  y %6.3f %6.3f  z %6.3f %6.3f' % (n[:40], mn.x, mx.x, mn.y, mx.y, mn.z, mx.z))
    sys.exit(0)

VIEWS = {'entry': ((1.05, Y0 + 0.45, 1.55), (-0.2, Y1, 1.0), 15), 'living': ((0.3, 0.3, 1.5), (0.0, -3.7, 0.95), 17),
         'tv': ((-1.15, -2.40, 1.15), (1.75, -1.45, 1.15), 19), 'dining': ((0.15, -0.7, 1.55), (-0.5, 3.3, 0.85), 17),
         'balcony': ((0.3, 0.2, 1.45), (-0.1, Y1 + 1.5, 1.2), 18)}
if 'wb' in ARGS:
    scene.render.engine = 'BLENDER_WORKBENCH'; sh = scene.display.shading; sh.light = 'STUDIO'; sh.color_type = 'TEXTURE'
    scene.world = bpy.data.worlds.new('w'); scene.world.color = (0.35, 0.35, 0.35)
    cdw = bpy.data.cameras.new('c'); cw = bpy.data.objects.new('c', cdw); scene.collection.objects.link(cw); scene.camera = cw
    for k, (l, t, ln) in VIEWS.items():
        cdw.lens = ln; cw.location = l; cw.rotation_euler = (Vector(t) - Vector(l)).to_track_quat('-Z', 'Y').to_euler()
        scene.render.resolution_x, scene.render.resolution_y = 1200, 700; scene.render.filepath = OUT + '/wb_%s.png' % k; bpy.ops.render.render(write_still=True)
    for o in bpy.data.objects:
        if o.name.startswith(('Shell_Ceiling', 'LM_FalseCeiling', 'Cove', 'DL', 'Shell_Kitchen Ceiling', 'Shell_Corridor Ceiling', 'Shell_Balcony Ceiling')): o.hide_render = True
    cdw.type = 'ORTHO'; cdw.ortho_scale = 9.0; cw.location = (-0.8, 0.4, 8); cw.rotation_euler = (0, 0, 0)
    scene.render.resolution_x, scene.render.resolution_y = 900, 1000; scene.render.filepath = OUT + '/wb_plan.png'; bpy.ops.render.render(write_still=True)
    print('DONE wb'); sys.exit(0)

for o in LMX: lightmap_prep(o, LMRES.get(o.name, 1024))
for ob, ul, vl in SHELL:
    d = 0.009 if ('Ceiling' in ob.name or 'Outside' in ob.name or 'Kitchen' in ob.name or 'Corridor' in ob.name) else 0.0055
    lightmap_prep(ob, (max(16, min(1024, round(ul / d))), max(16, min(1024, round(vl / d)))), new_uv=False)

# ---------------------------------------------------------------- lights: late-afternoon sun through the balcony, the sky, coves, downlights, the pendant
def area(name, loc, sx, sy, energy, color, target=None, rot=(0, 0, 0)):
    ld = bpy.data.lights.new(name, 'AREA'); ld.energy = energy; ld.color = color; ld.shape = 'RECTANGLE'; ld.size = sx; ld.size_y = sy
    lo = bpy.data.objects.new(name, ld); lo.location = loc; lo.rotation_euler = rot; scene.collection.objects.link(lo)
    if target: lo.rotation_euler = (Vector(target) - lo.location).to_track_quat('-Z', 'Y').to_euler()
    return lo
def spot(name, loc, target, w, deg, blend=0.75, color=WARM):
    ld = bpy.data.lights.new(name, 'SPOT'); ld.energy = w; ld.color = color; ld.spot_size = math.radians(deg); ld.spot_blend = blend; ld.shadow_soft_size = 0.03
    lo = bpy.data.objects.new(name, ld); lo.location = Vector(loc); scene.collection.objects.link(lo)
    lo.rotation_euler = (Vector(target) - lo.location).to_track_quat('-Z', 'Y').to_euler()
def point(name, loc, w, color=WARM, r=0.05):
    ld = bpy.data.lights.new(name, 'POINT'); ld.energy = w; ld.color = color; ld.shadow_soft_size = r
    lo = bpy.data.objects.new(name, ld); lo.location = loc; scene.collection.objects.link(lo)
area('Sky Balcony', (0, Y1 + 0.35, 1.25), BX1 - BX0, 2.3, 900, (0.92, 0.96, 1.0), target=(0, 0.5, 0.6))
area('Sky Balcony Open', (0, BY1 + 0.3, 1.5), X1 - X0, 2.5, 500, (0.90, 0.95, 1.0), target=(0, Y1, 0.8))
sun = bpy.data.lights.new('Sun', 'SUN'); sun.energy = 2.6; sun.color = (1.0, 0.86, 0.66); sun.angle = math.radians(1.5)
so = bpy.data.objects.new('Sun', sun); scene.collection.objects.link(so); so.rotation_euler = (Vector((0.35, -1.0, -0.42)) * -1).to_track_quat('Z', 'Y').to_euler()
for i_, (x_, y_) in enumerate(DL): spot('DL%d' % i_, (x_, y_, FZ - 0.02), (x_, y_, 0.0), 22, 80, 0.8)
for t in (LIV, DIN):
    cx_, cy_ = (t[0] + t[1]) / 2, (t[2] + t[3]) / 2
    for nm_, loc_, rot_, sx_, sy_ in (('Cove L', (t[0] + 0.08, cy_, H - 0.02), (0, math.radians(-40), 0), 0.08, t[3] - t[2] - 0.2),
                                      ('Cove R', (t[1] - 0.08, cy_, H - 0.02), (0, math.radians(40), 0), 0.08, t[3] - t[2] - 0.2),
                                      ('Cove F', (cx_, t[2] + 0.08, H - 0.02), (math.radians(40), 0, 0), t[1] - t[0] - 0.2, 0.08),
                                      ('Cove B', (cx_, t[3] - 0.08, H - 0.02), (math.radians(-40), 0, 0), t[1] - t[0] - 0.2, 0.08)):
        area(nm_, loc_, sx_, sy_, 22, (1.0, 0.82, 0.58), rot=rot_)
point('Pendant', (TX, TY, 2.15), 60, (1.0, 0.80, 0.55), 0.3)
point('Mandir Lamp', (X0 + 0.16, MC, 1.70), 6, (1.0, 0.72, 0.42), 0.05)
area('Console Glow', (X1 - 0.23, TVC, 0.22), 0.30, CN1 - CN0, 18, (1.0, 0.82, 0.58), rot=(math.pi, 0, 0))
area('Crockery Glow', (X1 - 0.18, (CU0 + CU1) / 2, 1.24), 0.25, CU1 - CU0, 10, (1.0, 0.85, 0.62), rot=(math.pi, 0, 0))
area('Kitchen Light', (KX + 1.0, (KY0 + KY1) / 2, H - 0.05), 1.2, 1.2, 60, (1.0, 0.95, 0.88))
area('Corridor Light', (CX + 0.8, (PY0 + PY1) / 2, H - 0.05), 0.6, 0.6, 18, (1.0, 0.88, 0.70))
area('Fill', (0.0, 0.0, H - 0.05), 3.0, 7.0, 40, (1.0, 0.95, 0.88))
world = bpy.data.worlds.new('W'); scene.world = world; world.use_nodes = True
world.node_tree.nodes['Background'].inputs['Color'].default_value = (0.75, 0.82, 0.92, 1); world.node_tree.nodes['Background'].inputs['Strength'].default_value = 0.6

# ---------------------------------------------------------------- bake light into every lightmap
scene.render.engine = 'CYCLES'; scene.cycles.device = 'CPU'
if not QUICK:
    scene.cycles.samples = 12 if FAST else 160
    scene.render.bake.target = 'IMAGE_TEXTURES'; scene.render.bake.margin = 8; scene.render.bake.use_clear = True
    bpy.ops.object.select_all(action='DESELECT')
    for o, _, _ in LM: o.select_set(True)
    bpy.context.view_layer.objects.active = LM[0][0]
    bpy.ops.object.bake(type='DIFFUSE', pass_filter={'DIRECT', 'INDIRECT'}, margin=8, use_clear=True)
    BAKED = {}
    for o, img, uvn in LM:
        w, h = img.size; BAKED[o.name] = gblur(np.array(img.pixels[:], dtype=np.float32).reshape(h, w, 4)[..., :3])
    room_names = {ob.name for ob, _, _ in SHELL if 'Outside' not in ob.name and 'Kitchen' not in ob.name and 'Corridor' not in ob.name}
    lum = np.concatenate([BAKED[n].reshape(-1, 3) for n in room_names]) @ np.array([0.2126, 0.7152, 0.0722])
    gain = 0.95 / max(1e-4, np.percentile(lum, 98.5)); print('BAKE gain', round(float(gain), 3), 'p50', round(float(np.percentile(lum, 50)), 3))
    LM_IMG = {}
    for o, img, uvn in LM:
        a = np.clip(BAKED[o.name] * gain, 0, 1); h, w = a.shape[:2]
        a = np.where(a <= 0.0031308, a * 12.92, 1.055 * np.power(a, 1 / 2.4) - 0.055)
        LM_IMG[o.name] = save_img('LM_' + o.name, a)
        print('LIGHTMAP', o.name, w, 'px, mean', round(float(a.mean()), 3))

# ---------------------------------------------------------------- previews
scene.view_settings.view_transform = 'AgX'; scene.cycles.samples = 24 if QUICK else 96; scene.cycles.use_denoising = True
cam_d = bpy.data.cameras.new('Cam'); cam = bpy.data.objects.new('Cam', cam_d); scene.collection.objects.link(cam)
tag = 'quick' if QUICK else 'v1'
R = (1200, 660) if QUICK else (1800, 1000)
if not (FAST or 'nopreview' in ARGS):
    for k, (l, t, ln) in VIEWS.items():
        if QUICK and k not in ('entry', 'living', 'tv', 'dining'): continue
        cam_d.lens = ln; cam.location = l; cam.rotation_euler = (Vector(t) - Vector(l)).to_track_quat('-Z', 'Y').to_euler()
        scene.camera = cam; scene.render.resolution_x, scene.render.resolution_y = R; scene.render.filepath = OUT + '/hall_%s_%s.png' % (tag, k); bpy.ops.render.render(write_still=True)
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
kw = dict(filepath=OUT + '/hall_v1.glb', export_format='GLB', export_apply=True, export_cameras=False, export_lights=False, export_image_format='JPEG', export_jpeg_quality=85)
bpy.ops.export_scene.gltf(**kw)
bpy.ops.wm.save_as_mainfile(filepath=OUT + '/hall_v1.blend'); print('DONE', round(os.path.getsize(OUT + '/hall_v1.glb') / 1e6, 2), 'MB')
