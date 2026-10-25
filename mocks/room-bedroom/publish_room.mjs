// Publishes the Sunday Bedroom from this working folder to the site: rooms/sunday-bedroom/ (as the Quiet Bath's
// mocks/room-pilot/publish_room.mjs does).
//   node mocks/room-bedroom/publish_room.mjs
// Copies only what the room uses: the viewer (as index.html), the compressed room (room.glb), every model that
// placements.json names (+ the vase's flowers) into models/, and placements.json pointing at them. A version
// (a hash of all those files) is stamped into placements.json; the viewer adds it to every file it loads, so
// _headers can let browsers keep the room for a year and a new publish still shows at once.
import { createHash } from 'node:crypto';
import { copyFileSync, mkdirSync, readFileSync, rmSync, statSync, writeFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
const HERE = dirname(fileURLToPath(import.meta.url));
const OUT = join(HERE, '../../rooms/sunday-bedroom');

const pl = JSON.parse(readFileSync(join(HERE, 'placements.json'), 'utf8'));
const files = [['bedroom_v1-web.glb', 'room.glb']];
for (const d of [...pl.staging, ...pl.products].filter((d) => d.file)) {   // inRoom products (the rug) are in room.glb
  files.push(['products/' + d.file, 'models/' + d.file]);
  if (typeof d.flowers === 'string') files.push(['products/' + d.flowers, 'models/' + d.flowers]);
}
const unique = [...new Map(files.map((f) => [f[1], f])).values()];

rmSync(OUT, { recursive: true, force: true });
mkdirSync(join(OUT, 'models'), { recursive: true });
const hash = createHash('sha1');
let bytes = 0;
for (const [src, dst] of unique) {
  const buf = readFileSync(join(HERE, src));
  hash.update(dst).update(buf); bytes += buf.length;
  copyFileSync(join(HERE, src), join(OUT, dst));
}
const version = hash.digest('hex').slice(0, 10);
const { _note, dirs, ...rest } = pl;
writeFileSync(join(OUT, 'placements.json'), JSON.stringify({ room: 'room.glb', dirs: { products: 'models', staging: 'models' }, version, ...rest }));
copyFileSync(join(HERE, 'viewer.html'), join(OUT, 'index.html'));
console.log(`published rooms/sunday-bedroom: ${unique.length} files, ${(bytes / 1e6).toFixed(1)} MB, version ${version}`);
console.log(`  room.glb ${(statSync(join(OUT, 'room.glb')).size / 1e6).toFixed(2)} MB`);
