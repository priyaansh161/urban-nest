// Contact sheet: every photo of the given listings, labelled, to model from.
import { createRequire } from 'module'; const sharp = createRequire(import.meta.url)('../../../tools/node_modules/sharp'); import { readdirSync, existsSync } from 'fs';
const ids = process.argv[3].split(','); const T = 260, tiles = [];
for (const [r, id] of ids.entries()) {
  const d = 'src/' + id + '/'; const fs = existsSync(d) ? readdirSync(d).filter(f => f.endsWith('.webp')).sort() : [];
  for (const [c, f] of fs.entries()) tiles.push({ input: await sharp(d + f).resize(T, T, { fit: 'contain', background: '#fff' }).png().toBuffer(), left: c * T + 120, top: r * T });
  tiles.push({ input: Buffer.from(`<svg width="120" height="${T}"><text x="6" y="130" font-size="20" font-family="Arial">${id}</text></svg>`), left: 0, top: r * T });
}
await sharp({ create: { width: 120 + 6 * T, height: ids.length * T, channels: 3, background: '#fff' } }).composite(tiles).png().toFile(process.argv[2]);
