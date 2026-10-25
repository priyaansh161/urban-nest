// The bedroom's pieces that came as Meshy originals (his Downloads, 25 Oct): full detail, 2K textures, Draco.
// Geometry is cut only where it is absurd (the geometric floor lamp is ~2M triangles), with meshoptimizer's
// seam-safe simplifier; everything else keeps every triangle (see the 3D quality-over-speed rule).
//   node mocks/room-bedroom/prep_downloads.mjs <downloads dir>
import { createRequire } from 'node:module';
import { spawnSync } from 'node:child_process';
import { readdirSync, unlinkSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
const HERE = dirname(fileURLToPath(import.meta.url));
const TOOLS = join(HERE, '../../tools');
const require = createRequire(join(TOOLS, 'package.json'));
const { NodeIO } = require('@gltf-transform/core');
const { ALL_EXTENSIONS } = require('@gltf-transform/extensions');
const { weld, simplify, prune } = require('@gltf-transform/functions');
const { MeshoptSimplifier } = require('meshoptimizer');
const draco3d = require('draco3dgltf');

const DL = process.argv[2];
// (Meshy file prefix, room copy in products/, triangle target or null = full detail)
const JOBS = [
  ['Meshy_AI_Crimson_Sonata_', 'bed-piano-canvas', null],
  ['Meshy_AI_Blue_Twin_Bell_Alarm_', 'bed-alarm-clock', null],
  ['Meshy_AI_Golden_Halo_Lamp_', 'bed-table-lamp', null],
  ['Meshy_AI_Geometric_Timber_Glow_', 'bed-geometric-floor-lamp', 300000],
];
await MeshoptSimplifier.ready;
const io = new NodeIO().registerExtensions(ALL_EXTENSIONS).registerDependencies({ 'draco3d.decoder': await draco3d.createDecoderModule() });
for (const [prefix, name, target] of JOBS) {
  const src = readdirSync(DL).filter((f) => f.startsWith(prefix) && f.endsWith('.glb')).sort().pop();
  let input = join(DL, src), tmp = null;
  if (target) {
    const doc = await io.read(input);
    await doc.transform(weld(), simplify({ simplifier: MeshoptSimplifier, ratio: 0.15, error: 0.0005 }), prune());
    tmp = input = join(HERE, 'products', name + '.simplified.tmp.glb');
    await io.write(tmp, doc);
  }
  const r = spawnSync(process.execPath, [join(TOOLS, 'compress-model.mjs'), input, join(HERE, 'products', name + '.glb'), '--size=2048'], { encoding: 'utf8' });
  if (tmp) unlinkSync(tmp);
  console.log(name, (r.stdout.match(/— [\d.]+ MB \([^)]*\)/g) || ['?']).pop());
}
