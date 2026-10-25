// The bath products' room copies, from their listing models (models/*.glb, already WebP textures + Draco).
// FULL detail by default (his call, 24 Oct: the spaces are for experience; a ~12 s load is fine, a skewed product
// is not). A triangle target only for a model that is genuinely absurd, and then meshoptimizer's simplifier, which
// keeps texture seams intact (Blender's collapse decimate smeared textures across them: blotchy rack, mat, brush).
//   node mocks/room-pilot/room_products.mjs [out-name ...]
import { createRequire } from 'node:module';
import { readdirSync, statSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
const HERE = dirname(fileURLToPath(import.meta.url));
const require = createRequire(join(HERE, '../../tools/package.json'));
const { NodeIO } = require('@gltf-transform/core');
const { ALL_EXTENSIONS, KHRDracoMeshCompression } = require('@gltf-transform/extensions');
const { weld, simplify, prune } = require('@gltf-transform/functions');
const { MeshoptSimplifier } = require('meshoptimizer');
const draco3d = require('draco3dgltf');

// (listing model prefix in models/, room copy in products/, triangle target or null = full detail)
const JOBS = [
  ['weava-home-memory-foam-bath-mat', 'bath-vanity-mat', null],
  ['saral-home-easy-living', 'bath-toilet-mat', null],
  ['homeze-tpe-anti-slip-shower-mat', 'bath-shower-mat', null],
  ['the-artment-your-artistic-apartment', 'bath-stone-mat', null],
  ['pano-polyresin-bathroom-set', 'bath-accessories-set', null],
  ['the-better-home-soap-dispenser-set', 'bath-dispenser-set', null],
  ['oslen-magic-sticker-towel-ring', 'bath-towel-ring', null],
  ['achro-self-adhesive-and-wall-mount', 'bath-paper-holder', null],
  // bath-towel-rack and bath-toilet-brush are modelled in Blender (make_rack_brush.py): their Meshy models were poor
];
const only = process.argv.slice(2);
const MODELS = join(HERE, '../../models'), OUT = join(HERE, 'products');
await MeshoptSimplifier.ready;
const io = new NodeIO().registerExtensions(ALL_EXTENSIONS).registerDependencies({
  'draco3d.decoder': await draco3d.createDecoderModule(), 'draco3d.encoder': await draco3d.createEncoderModule(),
});
const tris = (doc) => doc.getRoot().listMeshes().flatMap((m) => m.listPrimitives())
  .reduce((n, p) => n + (p.getIndices() ? p.getIndices().getCount() : p.getAttribute('POSITION').getCount()) / 3, 0);
for (const [prefix, name, target] of JOBS) {
  if (only.length && !only.includes(name)) continue;
  const src = readdirSync(MODELS).filter((f) => f.startsWith(prefix) && f.endsWith('.glb')).sort().pop();
  const doc = await io.read(join(MODELS, src));
  const before = tris(doc);
  if (target) await doc.transform(weld(), simplify({ simplifier: MeshoptSimplifier, ratio: Math.min(1, target / before), error: 0.002 }), prune());
  doc.createExtension(KHRDracoMeshCompression).setRequired(true);
  const out = join(OUT, name + '.glb');
  await io.write(out, doc);
  console.log('PRODUCT', name.padEnd(22), Math.round(before), '->', Math.round(tris(doc)), 'tris', (statSync(out).size / 1e6).toFixed(2), 'MB');
}
