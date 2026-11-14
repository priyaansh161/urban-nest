# 1 Nov 2026 patch, no re-bake: clock gets a printed face (its ticks and hands sat behind the face), the left-wall
# sign's print moves in front of its panel and says DISPENSARY, the floor gets 60 cm speckled vinyl tiles (base
# colour only; the baked lightmap still carries all its light).
import bpy, bmesh, os, numpy as np
HERE = os.path.dirname(bpy.data.filepath)
O = bpy.data.objects

# clock: drop the hidden ticks and hands, print them on the face instead
for o in list(O['Wall clock'].children_recursive):
    if o.name.startswith(('Tick', 'Hour hand', 'Minute hand')): bpy.data.objects.remove(o)
face = O['Clock face']; me = face.data
uv = me.uv_layers.new(name='UVMap')
for loop in me.loops:
    co = me.vertices[loop.vertex_index].co          # lathe profile in local x/y, axis along z
    uv.data[loop.index].uv = (0.5 + co.x / 0.30, 0.5 + co.y / 0.30)
def tex_into(mat, path, uvname=None, scale=None):
    nt = mat.node_tree; bsdf = nt.nodes['Principled BSDF']
    t = nt.nodes.new('ShaderNodeTexImage'); t.image = bpy.data.images.load(path); t.image.pack()
    if uvname:
        u = nt.nodes.new('ShaderNodeUVMap'); u.uv_map = uvname; nt.links.new(u.outputs['UV'], t.inputs['Vector'])
    nt.links.new(t.outputs['Color'], bsdf.inputs['Base Color'])
tex_into(face.active_material, os.path.join(HERE, 'tex', 'clock_face.png'), 'UVMap')

# sign: print in front of the panel, new wording
sf = O['Rx sign face']
sf.location.x += 0.0135 if sf.parent is None else 0
if sf.parent is not None:
    import mathutils
    mw = sf.matrix_world.copy(); mw.translation.x += 0.0135; sf.matrix_world = mw
img = [n for n in sf.active_material.node_tree.nodes if n.type == 'TEX_IMAGE'][0]
img.image = bpy.data.images.load(os.path.join(HERE, 'tex', 'rx_dispensary.png')); img.image.pack()

# floor: speckled vinyl tile, 2 x 2 tiles per image, mean close to the old flat grey
N = 1024; rng = np.random.default_rng(7)
base = np.full((N, N), 0.71)                                                # sRGB, about the old flat 0.46 linear
tile = (np.arange(N) // (N // 2))
base += ((tile[:, None] + tile[None, :]) % 2) * 0.015                      # neighbouring tiles differ a touch
low = rng.normal(0, 1, (N // 64, N // 64)); low = np.kron(low, np.ones((64, 64)))
base += 0.015 * low
sp = rng.random((N, N)); base[sp > 0.985] -= 0.13; base[sp < 0.006] += 0.07   # fleck
g = np.arange(N) % (N // 2); grout = (g < 2) | (g > N // 2 - 3)
base[grout[:, None] | grout[None, :]] = 0.60
rgb = np.stack([base * 0.99, base, base * 1.0, np.ones_like(base)], -1).clip(0, 1)
fi = bpy.data.images.new('floor_vinyl', N, N); fi.colorspace_settings.name = 'Non-Color'   # write the sRGB numbers as they are
fi.pixels.foreach_set(rgb.astype(np.float32).ravel())
fi.filepath_raw = os.path.join(HERE, 'tex', 'floor_vinyl.png'); fi.file_format = 'PNG'; fi.save()
fl = O['Shell_Floor']; fme = fl.data; fuv = fme.uv_layers['UVMap']
for loop in fme.loops:
    w = fl.matrix_world @ fme.vertices[loop.vertex_index].co
    fuv.data[loop.index].uv = (w.x / 1.2, w.y / 1.2)
fimg = bpy.data.images.load(os.path.join(HERE, 'tex', 'floor_vinyl.png')); fimg.pack()
fm = fl.active_material; nt = fm.node_tree; b = nt.nodes['Principled BSDF']
t = nt.nodes.new('ShaderNodeTexImage'); t.image = fimg
u = nt.nodes.new('ShaderNodeUVMap'); u.uv_map = 'UVMap'; nt.links.new(u.outputs['UV'], t.inputs['Vector'])
nt.links.new(t.outputs['Color'], b.inputs['Base Color'])

bpy.ops.export_scene.gltf(filepath=os.path.join(HERE, 'pharmacy.glb'), export_format='GLB', export_cameras=False,
                          export_lights=False, export_apply=True, export_yup=True, export_image_format='JPEG', export_jpeg_quality=88)
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
print('PATCHED v6', sf.matrix_world.translation.x)
