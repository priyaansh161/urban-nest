// Give see-through materials real depth colour (KHR_materials_volume) so glass and oil read on a white page in model-viewer.
//   node mocks/room-kitchen/products/volume.mjs <in.glb> <out.glb> "Material Name=thickness,r,g,b,distance" ...
// thickness in metres (how thick the piece looks), r,g,b = attenuation colour (linear 0..1), distance = metres to reach it.
import { createRequire } from 'module';
const require = createRequire(import.meta.url);
const { NodeIO } = require('../../../tools/node_modules/@gltf-transform/core');
const { ALL_EXTENSIONS, KHRMaterialsVolume } = require('../../../tools/node_modules/@gltf-transform/extensions');
const [inp, out, ...rules] = process.argv.slice(2);
const io = new NodeIO().registerExtensions(ALL_EXTENSIONS);
const doc = await io.read(inp);
const ext = doc.createExtension(KHRMaterialsVolume);
for (const rule of rules) {
  const [name, vals] = rule.split('='); const [t, r, g, b, d] = vals.split(',').map(Number);
  const m = doc.getRoot().listMaterials().find((x) => x.getName() === name);
  if (!m) { console.error('no material ' + name + ' in', doc.getRoot().listMaterials().map((x) => x.getName())); process.exit(1); }
  m.setExtension('KHR_materials_volume', ext.createVolume().setThicknessFactor(t).setAttenuationColor([r, g, b]).setAttenuationDistance(d));
  console.log('volume', name, vals);
}
await io.write(out, doc);
