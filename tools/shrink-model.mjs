/* Shrink a 3D model that is heavy because of its polygon count.
 *
 *   node tools/shrink-model.mjs <in.glb> <out.glb> [--verts=250000]
 *
 * compress-model.mjs alone cannot help a Meshy export with millions of
 * polygons: once its textures are WebP, what is left is geometry, and Draco
 * only packs that tighter. This first welds and simplifies the mesh down to a
 * vertex budget (meshoptimizer's simplifier, which keeps the silhouette and
 * the UV seams), then hands the result to compress-model.mjs for the WebP
 * textures and Draco. Reads Draco-compressed input too.
 *
 * Not for crystal chandeliers: simplifying rounds off the facets that make
 * crystal read as crystal. Lamps, clocks, vases and idols are fine. */
import { NodeIO } from '@gltf-transform/core';
import { ALL_EXTENSIONS } from '@gltf-transform/extensions';
import { weld, simplify, dedup, prune } from '@gltf-transform/functions';
import { MeshoptSimplifier } from 'meshoptimizer';
import { spawnSync } from 'node:child_process';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { unlinkSync } from 'node:fs';

const HERE = dirname(fileURLToPath(import.meta.url));
const [inPath, outPath] = process.argv.slice(2).filter((a) => !a.startsWith('--'));
const budget = Number((process.argv.find((a) => a.startsWith('--verts=')) || '--verts=250000').slice(8));
if (!inPath || !outPath) { console.error('usage: node tools/shrink-model.mjs <in.glb> <out.glb> [--verts=250000]'); process.exit(1); }

const draco3d = (await import('draco3dgltf')).default;
const io = new NodeIO().registerExtensions(ALL_EXTENSIONS).registerDependencies({
  'draco3d.decoder': await draco3d.createDecoderModule(),
  'draco3d.encoder': await draco3d.createEncoderModule(),
});
const doc = await io.read(inPath);
const count = () => doc.getRoot().listMeshes().reduce((s, m) => s + m.listPrimitives().reduce((t, p) => t + (p.getAttribute('POSITION')?.getCount() || 0), 0), 0);
const before = count();
// the input is decoded now; drop Draco so the intermediate file is plain (compress-model re-applies it)
doc.getRoot().listExtensionsUsed().filter((e) => e.extensionName === 'KHR_draco_mesh_compression').forEach((e) => e.dispose());

await MeshoptSimplifier.ready;
await doc.transform(dedup(), weld());
const welded = count();
if (welded > budget) {
  await doc.transform(simplify({ simplifier: MeshoptSimplifier, ratio: budget / welded, error: 0.002, lockBorder: false }));
}
await doc.transform(prune());
const after = count();
const tmp = outPath.replace(/\.glb$/i, '.simplified.tmp.glb');
await io.write(tmp, doc);
console.log(`  vertices ${before.toLocaleString()} → ${after.toLocaleString()} (budget ${budget.toLocaleString()})`);

const c = spawnSync(process.execPath, [join(HERE, 'compress-model.mjs'), tmp, outPath], { cwd: HERE, stdio: ['ignore', 'pipe', 'inherit'], encoding: 'utf8' });
try { unlinkSync(tmp); } catch {}
const line = (c.stdout || '').split('\n').find((l) => /× smaller|MB \(/.test(l) && /\.glb —/.test(l));
if (line) console.log(line);
process.exit(c.status || 0);
