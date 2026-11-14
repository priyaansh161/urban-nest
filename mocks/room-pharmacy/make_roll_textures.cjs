// The outside of the Paxxol rolls: blank labels and receipts as they sit on the roll, before printing.
// Label roll: 4.625 in wide, labels 2.125 in apart round the roll (green header runs ACROSS the roll,
// as in PharmVials' photos 13-15). Receipt roll: 3.375 in wide, receipts 4.25 in apart.
//   node make_roll_textures.cjs   (after make_textures.cjs; writes tex/roll_labels.png, tex/roll_receipts.png)
const sharp = require('../../tools/node_modules/sharp');
const T = __dirname + '/tex/';
const GREEN = '#8DC63F', INK = '#1d1d1b';
const dots = (x, y, s) => { let c = ''; [2, 4, 5, 4, 2].forEach((n, r) => { for (let i = 0; i < n; i++) c += `<circle cx="${x + (i - (n - 1) / 2) * s}" cy="${y + (r - 2) * s}" r="${s * 0.36}" fill="#2b2b2b"/>`; }); return c; };
const head = (w, h) => `<rect width="${w}" height="${h}" fill="${GREEN}"/>${dots(h * 0.55, h / 2, h * 0.13)}
  <text x="${h * 1.05}" y="${h * 0.66}" font-family="Arial" font-weight="700" font-size="${h * 0.45}" fill="${INK}" letter-spacing="2">PAXXOL</text>`;

(async () => {
  // one blank label, landscape 4.625 x 2.125 (1740 x 800), with the stub of green and pink stickers
  const LW = 1740, LH = 800, MAIN = 1360;
  const label = Buffer.from(`<svg xmlns="http://www.w3.org/2000/svg" width="${LW}" height="${LH}">
    <rect width="${LW}" height="${LH}" fill="#fbfbf8"/>${head(MAIN, LH * 0.19)}
    <line x1="${MAIN}" y1="0" x2="${MAIN}" y2="${LH}" stroke="#ddddd6" stroke-width="5"/>
    <rect x="${MAIN + 8}" y="${LH * 0.03}" width="${LW - MAIN - 16}" height="${LH * 0.2}" fill="${GREEN}"/>
    <rect x="${MAIN + 8}" y="${LH * 0.26}" width="${LW - MAIN - 16}" height="${LH * 0.2}" fill="${GREEN}"/>
    <rect x="${MAIN + 8}" y="${LH * 0.5}" width="${LW - MAIN - 16}" height="${LH * 0.2}" fill="#F4A7CF"/>
    <rect x="${MAIN + 8}" y="${LH * 0.74}" width="${LW - MAIN - 16}" height="${LH * 0.2}" fill="#F4A7CF"/></svg>`);
  // on the roll the label's long side runs across the roll, so turn it a quarter and line 7 up with a gap
  const one = await sharp(label).rotate(90).png().toBuffer();           // 800 wide x 1740 tall
  const GAP = 40, N = 7, W = N * (LH + GAP);
  await sharp({ create: { width: W, height: LW, channels: 3, background: '#f2f2ee' } })
    .composite([...Array(N)].map((_, i) => ({ input: one, left: i * (LH + GAP) + GAP / 2, top: 0 }))).png().toFile(T + 'roll_labels.png');

  // receipts: 3.375 wide across the roll, 4.25 long round it; 3 to a turn
  const RW = 860, RH = 1084;
  const rec = Buffer.from(`<svg xmlns="http://www.w3.org/2000/svg" width="${RH}" height="${RW}">
    <rect width="${RH}" height="${RW}" fill="#fbfbf8"/><rect width="120" height="${RW}" fill="${GREEN}"/></svg>`);
  await sharp({ create: { width: 3 * (RH + GAP), height: RW, channels: 3, background: '#f2f2ee' } })
    .composite([0, 1, 2].map((i) => ({ input: rec, left: i * (RH + GAP) + GAP / 2, top: 0 }))).png().toFile(T + 'roll_receipts.png');
  console.log('roll textures written');
})();
