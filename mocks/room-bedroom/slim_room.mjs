// The bedroom's web copy: the baked room with its roughness maps (fabric, wood, plaster: they only set how glossy a
// surface looks) brought down to 1024 px, then tools/compress-model.mjs (Draco, WebP, 2K everything else).
// At 2K they were ~3.8 MB of the room file for no visible difference (his call, 25 Oct 2026).
//   node mocks/room-bedroom/slim_room.mjs
import { createRequire } from 'node:module';
import { spawnSync } from 'node:child_process';
import { unlinkSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
const HERE = dirname(fileURLToPath(import.meta.url));
const TOOLS = join(HERE, '../../tools');
const require = createRequire(join(TOOLS, 'package.json'));
const { NodeIO } = require('@gltf-transform/core');
const { ALL_EXTENSIONS } = require('@gltf-transform/extensions');
const { textureCompress } = require('@gltf-transform/functions');
const sharp = require('sharp');

const io = new NodeIO().registerExtensions(ALL_EXTENSIONS);
const doc = await io.read(join(HERE, 'bedroom_v1.glb'));
await doc.transform(textureCompress({ encoder: sharp, targetFormat: 'png', resize: [1024, 1024], slots: /metallicRoughness/ }));
const tmp = join(HERE, 'bedroom_v1.slim.tmp.glb');
await io.write(tmp, doc);
const r = spawnSync(process.execPath, [join(TOOLS, 'compress-model.mjs'), tmp, join(HERE, 'bedroom_v1-web.glb'), '--size=2048'], { encoding: 'utf8' });
unlinkSync(tmp);
console.log((r.stdout.match(/bedroom_v1-web\.glb — [^\n]*/) || [r.stdout + r.stderr]).pop());
