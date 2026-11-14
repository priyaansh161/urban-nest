// big.mjs <out.png> <id8> [photo indices]  — the listing's photos at 700 px, 3 per row
import { createRequire } from 'module'; const sharp = createRequire(import.meta.url)('../../../tools/node_modules/sharp');
import { readdirSync } from 'fs';
const [out, id, which] = process.argv.slice(2); const d = 'src/' + id + '/';
let fs = readdirSync(d).filter(f => f.endsWith('.webp')).sort(); if (which) fs = which.split(',').map(i => i + '.webp');
const T = 700, tiles = [];
for (const [i, f] of fs.entries()) tiles.push({ input: await sharp(d + f).resize(T, T, { fit: 'contain', background: '#fff' }).png().toBuffer(), left: (i % 3) * T, top: Math.floor(i / 3) * T });
await sharp({ create: { width: 3 * T, height: Math.ceil(fs.length / 3) * T, channels: 3, background: '#fff' } }).composite(tiles).png().toFile(out);
