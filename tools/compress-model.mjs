/* Meshy .glb → web-ready .glb, in one command.
 *
 *   node tools/compress-model.mjs models/source/whatever-raw.glb
 *
 * Two passes, in this order and for reasons that cost a day to find:
 *
 *   1. Textures, through sharp by hand. gltf-transform's own texture step
 *      (`optimize --texture-compress webp`) throws "colourspace: parameter
 *      space not set" on Meshy exports. Not a libvips version problem — the
 *      same buffers go through sharp fine, so this does that step itself.
 *
 *   2. Geometry, through the gltf-transform CLI's draco command. NOT meshopt:
 *      EXT_meshopt_compression makes model-viewer 3.5 fire loadfailure, so the
 *      file downloads to 100% and then silently never appears. Draco renders,
 *      and is less than half the size anyway.
 *
 * Nothing here simplifies the mesh. Meshy has already decimated it, and
 * simplifying again rounds off exactly the facets that make a chandelier read
 * as crystal.
 */
import { spawn } from 'node:child_process';
import { basename, dirname, join, resolve } from 'node:path';
import { statSync, unlinkSync } from 'node:fs';
import { fileURLToPath } from 'node:url';

import { NodeIO } from '@gltf-transform/core';
import { ALL_EXTENSIONS, EXTTextureWebP } from '@gltf-transform/extensions';
import sharp from 'sharp';

const HERE = dirname(fileURLToPath(import.meta.url));
const MB = (bytes) => (bytes / 1048576).toFixed(2);

// ---------------------------------------------------------------- arguments

const args = process.argv.slice(2).filter((a) => !a.startsWith('--'));
const flag = (name, fallback) => {
  const hit = process.argv.find((a) => a.startsWith(`--${name}=`));
  return hit ? hit.slice(name.length + 3) : fallback;
};

const inPath = args[0];
if (!inPath) {
  console.error('usage: node tools/compress-model.mjs <in.glb> [out.glb] [--size=1024]');
  process.exit(1);
}

// models/source/crystal-chandelier-v2-raw.glb → models/crystal-chandelier-v2.glb
const defaultOut = join(
  HERE, '..', 'models',
  basename(inPath).replace(/\.glb$/i, '').replace(/[-_]raw$/i, '') + '.glb'
);
const outPath = resolve(args[1] || defaultOut);
const SIZE = Number(flag('size', 1024));

const sourceBytes = statSync(inPath).size;
console.log(`\n  ${basename(inPath)} — ${MB(sourceBytes)} MB\n`);

// ------------------------------------------------------- 1. textures (sharp)

const io = new NodeIO().registerExtensions(ALL_EXTENSIONS);
const doc = await io.read(inPath);

doc.createExtension(EXTTextureWebP).setRequired(true);

let texBefore = 0, texAfter = 0;
for (const tex of doc.getRoot().listTextures()) {
  const src = Buffer.from(tex.getImage());
  const name = tex.getName() || '(unnamed)';

  // A normal map encodes direction in RGB, so lossy artifacts read as shading
  // noise rather than blur. Give it more headroom than a colour map.
  const isNormal = /normal/i.test(name);
  const out = await sharp(src)
    .resize(SIZE, SIZE, { fit: 'inside', withoutEnlargement: true })
    .webp({ quality: isNormal ? 95 : 88, effort: 6 })
    .toBuffer();

  tex.setImage(out).setMimeType('image/webp');
  texBefore += src.length;
  texAfter += out.length;
  console.log(
    `  ${name.slice(0, 22).padEnd(23)} ${MB(src.length).padStart(6)} → ` +
    `${MB(out.length).padStart(6)} MB  ${isNormal ? '(q95, normal map)' : '(q88)'}`
  );
}
console.log(`  ${'textures'.padEnd(23)} ${MB(texBefore).padStart(6)} → ${MB(texAfter).padStart(6)} MB\n`);

const tmpPath = outPath.replace(/\.glb$/i, '.textures.tmp.glb');
await io.write(tmpPath, doc);

// -------------------------------------------------------- 2. geometry (draco)

// Reached by path rather than require.resolve: the package does not export
// its own package.json, so resolve() throws before it can be located.
const cli = join(HERE, 'node_modules', '@gltf-transform', 'cli', 'bin', 'cli.js');

const code = await new Promise((done) => {
  spawn(process.execPath, [cli, 'draco', tmpPath, outPath], { stdio: 'inherit' })
    .on('close', done);
});
unlinkSync(tmpPath);
if (code !== 0) process.exit(code);

// ------------------------------------------------------------------- verdict

const finalBytes = statSync(outPath).size;
const mb = finalBytes / 1048576;
console.log(
  `\n  ${basename(outPath)} — ${MB(finalBytes)} MB ` +
  `(${(sourceBytes / finalBytes).toFixed(0)}× smaller)`
);
if (mb > 6)      console.log('  Over 6 MB. Re-export from Meshy with fewer polygons.');
else if (mb > 3) console.log('  Between 3 and 6 MB — acceptable, but try --size=512.');
else             console.log('  Under the 3 MB target.');

console.log(
  `\n  Now open tools/verify.html and pick this file. A model can pass every\n` +
  `  numerical check and still never render — that is how the meshopt\n` +
  `  chandelier survived. It has to be seen loading.\n`
);
