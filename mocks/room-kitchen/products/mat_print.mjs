// Rebuild the HomeCloud mat print from the rectified photo: the five tile designs cut clean, laid out as on the mat (6 x 5),
// dark grout lines and a dark rubber border. 1250 x 1000 px = 50 x 40 cm.
import { createRequire } from 'module'; const sharp = createRequire(import.meta.url)('../../../tools/node_modules/sharp');
const R = 'ref/mat_rect.png', I = 7;
const cells = { A: [172, 385, 173, 190], B: [350, 380, 170, 190], C: [172, 190, 173, 185], D: [172, 580, 173, 190], E: [350, 190, 170, 185] };
const TW = 192, TH = 182, G = 8, B = 25;
const tile = {};
for (const [k, [x, y, w, h]] of Object.entries(cells))
  tile[k] = await sharp(R).extract({ left: x + I, top: y + I, width: w - 2 * I, height: h - 2 * I }).resize(TW, TH, { fit: 'fill' }).modulate({ saturation: 1.08 }).png().toBuffer();
const L = ['ABCDAB', 'DCEBDC', 'EABCEA', 'CDAECD', 'BEDABE'];
const comp = [];
L.forEach((row, r) => [...row].forEach((k, c) => comp.push({ input: tile[k], left: B + G / 2 + c * (TW + G), top: B + G / 2 + r * (TH + G) })));
await sharp({ create: { width: 1250, height: 1000, channels: 3, background: { r: 52, g: 34, b: 44 } } }).composite(comp).png().toFile('ref/mat_print.png');
console.log('ok');
