// Builds the numbered product sheets Gemini gets (it caps how many images one prompt can take):
// each render's own background (read from its corner) becomes one light colour, it is cropped to the
// product, and laid in a labelled 4 x 2 grid.   node mocks/room-pilot/gemini/make_sheets.mjs
import { createRequire } from 'node:module';
import { readdirSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
const HERE = dirname(fileURLToPath(import.meta.url));
const sharp = createRequire(join(HERE, '../../../tools/package.json'))('sharp');
const BG = { r: 242, g: 240, b: 236 };
const NAMES = {
  '01': 'Bathroom Sliders', '02': 'Toilet Paper Holder', '03': 'Bathroom Accessories Set', '04': 'Towel Hanger',
  '05': 'Shower Mat', '06': 'Scented Candles', '07': 'Toilet Mat', '08': 'Toilet Cleaning Brush',
  '09': 'Vanity Mat', '10': 'Towel Rack', '11': 'Wall Shelf Organiser', '12': 'Elpheco Dustbin',
  '13': 'Wall Soap Dispenser', '14': 'Ribbed Vase + flowers', '15': 'Spring Vase + flowers',
};
async function cell(file, n, size = 480) {
  const m0 = await sharp(file).metadata();
  const flat = m0.hasAlpha ? await sharp(file).flatten({ background: BG }).png().toBuffer() : null;   // transparent cut-outs need no background matching
  const { data, info } = await sharp(flat || file).removeAlpha().raw().toBuffer({ resolveWithObject: true });
  const [r0, g0, b0] = [data[0], data[1], data[2]];
  // dark scene backgrounds need a tight match (black metal on the towel rack and shelf is only a few levels
  // off them); the light, slightly grainy Blender renders need a loose one
  const tol = flat ? 0 : r0 + g0 + b0 > 300 ? 45 : 4;
  for (let i = 0; i < data.length; i += 3) {
    if (Math.abs(data[i] - r0) + Math.abs(data[i + 1] - g0) + Math.abs(data[i + 2] - b0) < tol) { data[i] = BG.r; data[i + 1] = BG.g; data[i + 2] = BG.b; }
  }
  const piece = await sharp(data, { raw: info }).trim({ background: BG, threshold: 10 }).png().toBuffer();
  const fit = await sharp(piece).resize(size - 70, size - 110, { fit: 'inside' }).png().toBuffer();
  const meta = await sharp(fit).metadata();
  const label = Buffer.from(`<svg width="${size}" height="70" xmlns="http://www.w3.org/2000/svg"><text x="20" y="46" font-family="Arial" font-size="30" font-weight="700" fill="#1f3a39">${n}. ${NAMES[n]}</text></svg>`);
  return sharp({ create: { width: size, height: size, channels: 3, background: BG } })
    .composite([{ input: fit, left: Math.round((size - meta.width) / 2), top: 70 + Math.round((size - 90 - meta.height) / 2) }, { input: label, left: 0, top: 0 }])
    .png().toBuffer();
}
const files = readdirSync(join(HERE, 'products')).filter((f) => /^\d\d-.*\.png$/.test(f)).sort();
const groups = [files.slice(0, 8), files.slice(8)];
for (const [gi, group] of groups.entries()) {
  const cells = await Promise.all(group.map((f) => cell(join(HERE, 'products', f), f.slice(0, 2))));
  const sheet = sharp({ create: { width: 4 * 480 + 5 * 12, height: 2 * 480 + 3 * 12, channels: 3, background: { r: 210, g: 206, b: 198 } } });
  await sheet.composite(cells.map((c, i) => ({ input: c, left: 12 + (i % 4) * 492, top: 12 + Math.floor(i / 4) * 492 }))).jpeg({ quality: 90 })
    .toFile(join(HERE, `0${gi + 1}-products-${gi === 0 ? '01-08' : '09-15'}.jpg`));
  console.log('SHEET', gi + 1, group.length, 'items');
}
