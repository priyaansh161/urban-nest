// Appliance faces for the kitchen build, from the real products' listing photos:
//   fridge_front.png: Samsung RS76CG8003S9HL doors, the marketing overlays replaced by each door's own clean brushed steel
//   oven_front.png / microwave_front.png: Elica EPBI 680 MMF and Electrolux EMSB30XCF fronts, cropped to the face
//   node prep_fronts.mjs   (run in mocks/room-kitchen/appliances)
import { createRequire } from 'node:module';
const require = createRequire(new URL('../../../tools/package.json', import.meta.url)); const sharp = require('sharp');
const src = 'fridge/B0BQC4Y4TP-1.jpg';
const { data, info } = await sharp(src).removeAlpha().raw().toBuffer({ resolveWithObject: true });
const W = info.width, C = 3;
const X0 = 75, X1 = 772, Y0 = 56, Y1 = 1430, GAP0 = 384, GAP1 = 416, OW = X1 - X0, OH = Y1 - Y0;
const out = Buffer.alloc(OW * OH * C);
const put = (x, y, sx, sy) => { const i = (sy * W + sx) * C, o = ((y - Y0) * OW + (x - X0)) * C; out[o] = data[i]; out[o + 1] = data[i + 1]; out[o + 2] = data[i + 2]; };
for (let y = Y0; y < Y1; y++) {
  const t = (y - Y0) / (OH - 1);
  for (let x = X0; x < X1; x++) {
    if (x >= GAP0 && x < GAP1) { put(x, y, x, y); continue; }                       // the dark gap between the doors, as it is
    if (x < GAP0) { put(x, y, x, Math.round(190 + t * (600 - 190))); continue; }      // freezer door: its clean band, stretched down the door
    if (y < 165) { put(x, y, x, y); continue; }                                       // fridge door: the SAMSUNG logo strip at the top
    const sy = Math.round(250 + ((y - 165) / (Y1 - 165)) * (520 - 250));              // then its clean band (between the badges), stretched
    if (y < 205) { const f = (y - 165) / 40, i = (Math.min(y, 150) * W + x) * C, j = (sy * W + x) * C, o = ((y - Y0) * OW + (x - X0)) * C; for (let c = 0; c < 3; c++) out[o + c] = data[i + c] * (1 - f) + data[j + c] * f; continue; }
    put(x, y, x, sy);
  }
}
await sharp(out, { raw: { width: OW, height: OH, channels: 3 } }).png().toFile('fridge_front.png');
await sharp('oven/B0DMKN5Q4Q-1.jpg').extract({ left: 12, top: 14, width: 783, height: 776 }).png().toFile('oven_front.png');
await sharp('microwave/B0BX728B4B-1.jpg').extract({ left: 48, top: 283, width: 1404, height: 917 }).png().toFile('microwave_front.png');
console.log('fronts ok');
