/* Fewer draw calls for a room built from many small loose pieces (3 Nov 2026: the PharmVials dispensary drew
 * ~1,850 times a frame, 1,067 meshes, against ~60 for the Quiet Bath, and felt less fluid).
 *
 *   node tools/merge-static.mjs <in.glb> <out.glb> --keep=<placements.json> [--keep-names=Glass,Shell_,LM_]
 *
 * Every mesh is moved to the scene root at its world position, then all meshes that nothing looks up by name are
 * joined, one mesh per material. Kept separate: each placements.json product's "node" (its dot and card find it by
 * name), and anything whose name contains one of --keep-names (the viewer recognises baked surfaces by Shell_ and
 * LM_, and the dot ray ignores Glass). The look is unchanged; only the number of objects drops. Draco + the
 * images as they were. */
import { NodeIO } from '@gltf-transform/core';
import { ALL_EXTENSIONS } from '@gltf-transform/extensions';
import { join, dedup, prune } from '@gltf-transform/functions';
import draco3d from 'draco3dgltf';
import { readFileSync, statSync } from 'node:fs';

const args = process.argv.slice(2);
const [inPath, outPath] = args.filter((a) => !a.startsWith('--'));
const opt = (n) => (args.find((a) => a.startsWith(`--${n}=`)) || '').split('=').slice(1).join('=');
if (!inPath || !outPath) { console.error('usage: node tools/merge-static.mjs <in.glb> <out.glb> --keep=<placements.json> [--keep-names=Glass,Shell_,LM_]'); process.exit(1); }
const keepNodes = new Set();
if (opt('keep')) {
  const pl = JSON.parse(readFileSync(opt('keep'), 'utf8'));
  for (const d of [...(pl.products || []), ...(pl.staging || [])]) if (d.node) keepNodes.add(d.node);
  for (const h of pl.hideInRoom || []) keepNodes.add(h);
}
const keepParts = (opt('keep-names') || 'Glass,Shell_,LM_').split(',').filter(Boolean);

const io = new NodeIO().registerExtensions(ALL_EXTENSIONS).registerDependencies({
  'draco3d.decoder': await draco3d.createDecoderModule(), 'draco3d.encoder': await draco3d.createEncoderModule(),
});
const doc = await io.read(inPath);
const root = doc.getRoot();
const count = () => root.listNodes().filter((n) => n.getMesh()).length;
const before = count();

// a kept name may sit on a group (the viewer also matches a mesh by its parent's name): that whole group stays as it
// is, where it is. Every other mesh moves to the scene root at its world position, nameless, free to join.
// three.js tidies names as it loads them (PropertyBinding.sanitizeNodeName): placements.json holds the tidied ones
const tidy = (s) => (s || '').replace(/\s/g, '_').replace(/[\[\]\.:\/]/g, '');
const isKept = (n) => { const nm = tidy(n.getName()), mn = tidy(n.getMesh()?.getName()); return keepNodes.has(nm) || keepNodes.has(mn) || keepParts.some((k) => nm.includes(k) || mn.includes(k)); };
const inKeptGroup = (n) => { for (let p = n; p; p = p.getParentNode()) if (isKept(p)) return true; return false; };
const scene = root.getDefaultScene() || root.listScenes()[0];
const found = [...keepNodes].filter((k) => root.listNodes().some((n) => tidy(n.getName()) === k || tidy(n.getMesh()?.getName()) === k));
console.log(`products found by name: ${found.length} of ${keepNodes.size}` + (found.length < keepNodes.size ? ', missing: ' + [...keepNodes].filter((k) => !found.includes(k)).join(', ') : ''));
let kept = 0;
for (const n of root.listNodes()) {
  const m = n.getMesh(); if (!m) continue;
  if (isKept(n)) { kept++; continue; }
  if (inKeptGroup(n)) { n.setName(''); m.setName(''); continue; }   // inside a kept group: stays in it, joins its siblings
  const p = n.getParentNode();
  if (p) { const w = n.getWorldMatrix(); p.removeChild(n); n.setMatrix(w); scene.addChild(n); }
  for (const c of n.listChildren()) { const w = c.getWorldMatrix(); n.removeChild(c); c.setMatrix(w); scene.addChild(c); }
  n.setName(''); m.setName('');
}
await doc.transform(dedup(), join({ keepNamed: true }), prune());
for (const n of root.listNodes()) if (n.getMesh() && !n.getName()) n.setName('Merged_' + (n.getMesh().listPrimitives()[0]?.getMaterial()?.getName() || 'static'));

doc.createExtension(ALL_EXTENSIONS.find((e) => e.EXTENSION_NAME === 'KHR_draco_mesh_compression'))
  .setRequired(true).setEncoderOptions({ method: 'edgebreaker', encodeSpeed: 5, decodeSpeed: 5 });
await io.write(outPath, doc);
console.log(`meshes ${before} -> ${count()} (${kept} kept by name), ${(statSync(outPath).size / 1e6).toFixed(2)} MB`);
