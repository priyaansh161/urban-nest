// Contact sheet of renders/<tag>_*.png (3 columns, 640x360 each), to review many camera views in one image.
//   node mocks/room-living/sheet.mjs <tag> [pattern]
import { createRequire } from 'module';
import { readdirSync } from 'node:fs';
const require = createRequire(import.meta.url);
const sharp = require('../../tools/node_modules/sharp');
const [tag, pat = ''] = process.argv.slice(2);
const dir = 'mocks/room-living/renders/';
const files = readdirSync(dir).filter(f => f.startsWith(tag + '_') && (pat.startsWith('!') ? !f.includes(pat.slice(1)) : f.includes(pat)) && f.endsWith('.png') && !f.includes('sheet'));
const W = 640, Hh = 360, cols = 3, rows = Math.ceil(files.length / cols);
const comps = []; 
for (let i = 0; i < files.length; i++) {
  comps.push({ input: await sharp(dir + files[i]).resize(W, Hh).toBuffer(), left: (i % cols) * W, top: Math.floor(i / cols) * Hh });
  comps.push({ input: { text: { text: `<span foreground="white" background="black" size="large"> ${i}: ${files[i].replace(tag + '_', '').replace('.png', '')} </span>`, rgba: true } }, left: (i % cols) * W + 4, top: Math.floor(i / cols) * Hh + 4 });
}
await sharp({ create: { width: W * cols, height: Hh * rows, channels: 3, background: '#000' } }).composite(comps).jpeg({ quality: 82 }).toFile(dir + `${tag}_sheet${pat}.jpg`);
console.log('sheet of', files.length);
