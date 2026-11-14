import { createRequire } from 'module'; const sharp = createRequire(import.meta.url)('../../../tools/node_modules/sharp');
import { readdirSync } from 'fs';
const fs = readdirSync('out').filter(f => f.endsWith('_look.png')).sort(); const T = 420, C = 6, tiles = [];
for (const [i, f] of fs.entries()) {
  tiles.push({ input: await sharp('out/' + f).resize(T, T).png().toBuffer(), left: (i % C) * T, top: Math.floor(i / C) * (T + 30) + 30 });
  tiles.push({ input: Buffer.from(`<svg width="${T}" height="30"><text x="8" y="22" font-size="20" font-family="Arial">${f.replace('_look.png', '')}</text></svg>`), left: (i % C) * T, top: Math.floor(i / C) * (T + 30) });
}
await sharp({ create: { width: C * T, height: Math.ceil(fs.length / C) * (T + 30), channels: 3, background: '#fff' } }).composite(tiles).png().toFile('looks.png');
