// Printed labels for the Quiet Bath's staging bottles (2 Nov 2026): the reed diffuser on the counter and the
// pump bottle in the shower niche. Generic, no brand: a paper label with a fine border, as on apothecary bottles.
//   node make_staging_labels.cjs        (run in mocks/room-pilot) -> textures/staging/lbl_*.png
const sharp = require('../../tools/node_modules/sharp');
const paper = `<filter id="p"><feTurbulence baseFrequency="0.8" numOctaves="2" seed="3"/><feColorMatrix values="0 0 0 0 0.45  0 0 0 0 0.4  0 0 0 0 0.35  0 0 0 0.08 0"/></filter>`;
const label = (W, H, bg, ink, lines) => `<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${H}"><defs>${paper}</defs>
<rect width="${W}" height="${H}" fill="${bg}"/>
<rect x="18" y="18" width="${W - 36}" height="${H - 36}" fill="none" stroke="${ink}" stroke-width="3" opacity="0.7"/>
${lines.map(([y, size, txt, sp, wt]) => `<text x="${W / 2}" y="${y}" font-family="Georgia, 'Times New Roman', serif" font-size="${size}" font-weight="${wt || 400}" letter-spacing="${sp || 0}" text-anchor="middle" fill="${ink}">${txt}</text>`).join('')}
<rect width="${W}" height="${H}" filter="url(#p)"/></svg>`;
const jobs = [
  ['lbl_diffuser', label(640, 400, '#efe6d6', '#3b2a1c', [[120, 54, 'FIG &amp; CEDAR', 6, 600], [185, 30, 'reed diffuser', 3], [300, 26, '100 ml · 3.4 fl oz', 2]])],
  ['lbl_bodywash', label(400, 640, '#f2efe9', '#1f2226', [[200, 46, 'BODY', 8, 600], [255, 46, 'WASH', 8, 600], [340, 26, 'eucalyptus', 3], [380, 26, '&amp; mint', 3], [540, 24, '300 ml', 2]])],
  ['lbl_serum', label(400, 400, '#e9e2d4', '#2b2118', [[170, 40, 'BATH OIL', 5, 600], [240, 24, 'neroli', 3], [320, 22, '30 ml', 2]])],
];
Promise.all(jobs.map(([n, svg]) => sharp(Buffer.from(svg)).png().toFile(`textures/staging/${n}.png`))).then(() => console.log('labels ok'));
