// Clock face (numbers, ticks, hands at 10:10) and the left-wall dispensary sign, 1 Nov 2026.
const sharp = require('../../tools/node_modules/sharp');
const S = 1024, c = S / 2;
let t = '';
for (let k = 0; k < 60; k++) {
  const a = k * Math.PI / 30, big = k % 5 === 0, r0 = big ? 430 : 455, r1 = 486;
  t += `<line x1="${c + r0 * Math.sin(a)}" y1="${c - r0 * Math.cos(a)}" x2="${c + r1 * Math.sin(a)}" y2="${c - r1 * Math.cos(a)}" stroke="#1d1f20" stroke-width="${big ? 14 : 5}"/>`;
}
for (let n = 1; n <= 12; n++) {
  const a = n * Math.PI / 6, r = 360;
  t += `<text x="${c + r * Math.sin(a)}" y="${c - r * Math.cos(a) + 30}" font-family="Arial, Helvetica, sans-serif" font-size="88" font-weight="600" text-anchor="middle" fill="#1d1f20">${n}</text>`;
}
const hand = (deg, len, w, col) => `<line x1="${c - 0.18 * len * Math.sin(deg * Math.PI / 180)}" y1="${c + 0.18 * len * Math.cos(deg * Math.PI / 180)}" x2="${c + len * Math.sin(deg * Math.PI / 180)}" y2="${c - len * Math.cos(deg * Math.PI / 180)}" stroke="${col}" stroke-width="${w}" stroke-linecap="round"/>`;
const clock = `<svg xmlns="http://www.w3.org/2000/svg" width="${S}" height="${S}"><rect width="${S}" height="${S}" fill="#f3f2ee"/>${t}
<text x="${c}" y="${c + 175}" font-family="Arial" font-size="34" letter-spacing="6" text-anchor="middle" fill="#7a7d7f">QUARTZ</text>
${hand(305, 250, 22, '#1d1f20')}${hand(60, 370, 14, '#1d1f20')}${hand(200, 400, 5, '#b3261e')}<circle cx="${c}" cy="${c}" r="20" fill="#1d1f20"/></svg>`;
const sign = `<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="360"><rect width="1200" height="360" fill="#fafafa"/>
<rect width="300" height="360" fill="#1f7a8c"/><text x="150" y="235" font-family="Georgia, serif" font-size="190" font-weight="700" text-anchor="middle" fill="#fff">R<tspan font-size="120" dx="-14" dy="20">x</tspan></text>
<text x="365" y="200" font-family="Arial, Helvetica, sans-serif" font-size="108" font-weight="700" letter-spacing="8" fill="#1e2b33">DISPENSARY</text>
<text x="368" y="290" font-family="Arial, Helvetica, sans-serif" font-size="40" fill="#5e6b73">Prescriptions prepared and checked here</text></svg>`;
(async () => {
  await sharp(Buffer.from(clock)).png().toFile('tex/clock_face.png');
  await sharp(Buffer.from(sign)).png().toFile('tex/rx_dispensary.png');
  console.log('ok');
})();
