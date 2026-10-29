/* A light first copy of a 3D room, so it appears in seconds instead of a minute.
 *
 *   node tools/room-preview.mjs <room.glb> <room-preview.glb> [--size=1024]
 *
 * The same room, node for node, with every image shrunk to at most --size
 * pixels. The viewer shows this first, then swaps the full room's images in
 * place as they arrive (see "ROOM PREVIEW" in rooms/<room>/index.html), so
 * nothing about the room changes but its sharpness. Because the swap pairs
 * the two files mesh by mesh, the preview must come from the same room.glb:
 * remake it whenever the room is republished. */
import { NodeIO } from '@gltf-transform/core';
import { ALL_EXTENSIONS } from '@gltf-transform/extensions';
import { textureCompress } from '@gltf-transform/functions';
import draco3d from 'draco3dgltf';
import sharp from 'sharp';
import { statSync } from 'node:fs';

const [inPath, outPath] = process.argv.slice(2).filter((a) => !a.startsWith('--'));
const size = Number((process.argv.find((a) => a.startsWith('--size=')) || '--size=1024').slice(7));
if (!inPath || !outPath) { console.error('usage: node tools/room-preview.mjs <room.glb> <room-preview.glb> [--size=1024]'); process.exit(1); }

const io = new NodeIO().registerExtensions(ALL_EXTENSIONS).registerDependencies({
  'draco3d.decoder': await draco3d.createDecoderModule(),
  'draco3d.encoder': await draco3d.createEncoderModule(),
});
const doc = await io.read(inPath);
await doc.transform(textureCompress({ encoder: sharp, targetFormat: 'webp', resize: [size, size], quality: 72 }));
await io.write(outPath, doc);
const mb = (f) => (statSync(f).size / 1048576).toFixed(2) + ' MB';
console.log(`${inPath.split(/[\\/]/).pop()} ${mb(inPath)} → preview ${mb(outPath)} (images at most ${size}px)`);
