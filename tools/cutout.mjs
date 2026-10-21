/* Cut the background out of product photos: a local AI model, no account.
 *
 *   node tools/cutout.mjs <photo url or file> <out.png> [<photo> <out.png> ...]
 *
 * Its own process on purpose: @imgly/background-removal-node brings its own,
 * older sharp/libvips, and two libvips copies in one process crash (GLib
 * "invalid unclassed type"). list-product.mjs calls this and reads the PNGs. */
import { removeBackground } from '@imgly/background-removal-node';
import { readFileSync, writeFileSync } from 'node:fs';

const UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130 Safari/537.36';
const args = process.argv.slice(2);
if (!args.length || args.length % 2) { console.error('usage: node tools/cutout.mjs <photo> <out.png> [...]'); process.exit(1); }
let failed = 0;
for (let i = 0; i < args.length; i += 2) {
  const [src, out] = [args[i], args[i + 1]];
  try {
    const buf = /^https?:/.test(src) ? Buffer.from(await (await fetch(src, { headers: { 'User-Agent': UA } })).arrayBuffer()) : readFileSync(src);
    const type = buf[0] === 0x89 ? 'image/png' : buf[0] === 0x52 ? 'image/webp' : 'image/jpeg';
    const blob = await removeBackground(new Blob([buf], { type }));
    writeFileSync(out, Buffer.from(await blob.arrayBuffer()));
    console.log('ok ' + out);
  } catch (e) { failed++; console.log('failed ' + src + ': ' + e.message); }
}
process.exit(failed === args.length / 2 ? 1 : 0);
