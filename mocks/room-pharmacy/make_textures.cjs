// Printed artwork for the PharmVials sample counter, drawn as vector art and saved as large PNGs, so the
// lettering stays sharp however close the camera gets. Layouts follow PharmVials' own product drawings
// (refs/*1903*.png): Paxxol green header, 4.625 x 2.125 in Rx label with a stub of auxiliary stickers,
// 3.375 x 4.25 in receipt. Patient, prescriber and pharmacy are invented.
//   node make_textures.cjs        (from mocks/room-pharmacy; writes tex/*.png)
const sharp = require('../../tools/node_modules/sharp');
const fs = require('fs');
fs.mkdirSync(__dirname + '/tex', { recursive: true });
const out = (name, svg) => sharp(Buffer.from(svg)).png().toFile(__dirname + '/tex/' + name);
const GREEN = '#8DC63F', CAPGREEN = '#0A7A52', INK = '#1d1d1b';

// Paxxol mark: a dotted diamond of circles, as on the cards and labels
const dots = (x, y, s, fill = '#2b2b2b') => {
  let c = '';
  const rows = [2, 4, 5, 4, 2];
  rows.forEach((n, r) => { for (let i = 0; i < n; i++) c += `<circle cx="${x + (i - (n - 1) / 2) * s}" cy="${y + (r - 2) * s}" r="${s * 0.36}" fill="${fill}"/>`; });
  return c;
};

// 1. child-resistant cap top: "PUSH DOWN & TURN", OPEN / CLOSE arrows round the edge
out('cap_cr.png', `<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="1024" height="1024">
  <rect width="1024" height="1024" fill="#ffffff"/>
  <defs><path id="top" d="M 190 512 A 322 322 0 0 1 834 512"/><path id="bot" d="M 834 512 A 322 322 0 0 1 190 512"/></defs>
  <g font-family="Arial Narrow, Arial" font-weight="900" fill="${CAPGREEN}" text-anchor="middle">
    <text x="512" y="430" font-size="150" letter-spacing="-4">PUSH</text>
    <text x="512" y="575" font-size="150" letter-spacing="-4">DOWN</text>
    <text x="512" y="720" font-size="150" letter-spacing="-4">&amp; TURN</text>
  </g>
  <g font-family="Arial" font-weight="700" font-size="54" fill="${CAPGREEN}">
    <text><textPath xlink:href="#top" startOffset="62%" text-anchor="middle">OPEN ⟶</textPath></text>
    <text><textPath xlink:href="#bot" startOffset="38%" text-anchor="middle">⟵ CLOSE</textPath></text>
  </g>
</svg>`);

// 2. the Rx label as printed on the vial: Paxxol header + what the thermal printer adds
const rxBody = (w, h, drug, sig, qty, rx) => `
  <rect width="${w}" height="${h}" fill="#fbfbf8"/>
  <rect width="${w}" height="${h * 0.19}" fill="${GREEN}"/>
  ${dots(h * 0.11, h * 0.095, h * 0.026)}
  <text x="${h * 0.2}" y="${h * 0.128}" font-family="Arial" font-weight="700" font-size="${h * 0.085}" fill="${INK}" letter-spacing="2">PAXXOL</text>
  <g font-family="Arial" font-size="${h * 0.034}" fill="${INK}" text-anchor="end">
    <text x="${w - 30}" y="${h * 0.055}">(647)-931-0055</text><text x="${w - 30}" y="${h * 0.105}">www.pharmvials.com</text><text x="${w - 30}" y="${h * 0.155}">order@pharmvials.com</text></g>
  <g font-family="Consolas, Courier New, monospace" fill="#111" font-size="${h * 0.062}">
    <text x="40" y="${h * 0.3}" font-weight="700">MAPLE STREET PHARMACY</text>
    <text x="${w - 40}" y="${h * 0.3}" text-anchor="end">Rx ${rx}</text>
    <text x="40" y="${h * 0.39}" font-size="${h * 0.05}">412 Maple St, Mississauga ON  (905) 555-0142</text>
    <text x="40" y="${h * 0.5}" font-weight="700">JORDAN LEE</text>
    <text x="${w - 40}" y="${h * 0.5}" text-anchor="end" font-size="${h * 0.05}">Dr. A. Patel</text>
    <text x="40" y="${h * 0.62}" font-weight="700" font-size="${h * 0.072}">${drug}</text>
    <text x="40" y="${h * 0.73}">${sig}</text>
    <text x="40" y="${h * 0.86}" font-size="${h * 0.05}">Qty: ${qty}   Refills: 2   Date: 2026-10-30</text>
    <text x="${w - 40}" y="${h * 0.86}" text-anchor="end" font-size="${h * 0.05}">DIN 02238170</text>
  </g>
  <g fill="#111">${[...Array(46)].map((_, i) => `<rect x="${w - 360 + i * 7}" y="${h * 0.9}" width="${i % 3 ? 3 : 5}" height="${h * 0.07}"/>`).join('')}</g>`;
out('rx_label_amox.png', `<svg xmlns="http://www.w3.org/2000/svg" width="1740" height="1024">${rxBody(1740, 1024, 'AMOXICILLIN 500MG CAPSULE', 'Take 1 capsule 3 times daily for 7 days', 21, '1048213')}</svg>`);
out('rx_label_omep.png', `<svg xmlns="http://www.w3.org/2000/svg" width="1740" height="1024">${rxBody(1740, 1024, 'OMEPRAZOLE 20MG CAPSULE', 'Take 1 capsule daily before breakfast', 30, '1048229')}</svg>`);

// 3. the full label sheet as it comes off the roll: label + stub of green and pink auxiliary stickers
const W = 2220, H = 1020, LW = 1740;
out('label_sheet.png', `<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${H}">
  <rect width="${W}" height="${H}" fill="#fbfbf8"/>
  <svg width="${LW}" height="${H}">${rxBody(LW, H, 'AMOXICILLIN 500MG CAPSULE', 'Take 1 capsule 3 times daily for 7 days', 21, '1048213')}</svg>
  <line x1="${LW}" y1="0" x2="${LW}" y2="${H}" stroke="#d8d8d2" stroke-width="4"/>
  <g font-family="Arial" font-weight="700" font-size="34" fill="${INK}" text-anchor="middle">
    <rect x="${LW + 8}" y="${H * 0.2}" width="${W - LW - 16}" height="${H * 0.19}" fill="${GREEN}"/><text x="${(LW + W) / 2}" y="${H * 0.31}">TAKE WITH FOOD</text>
    <rect x="${LW + 8}" y="${H * 0.41}" width="${W - LW - 16}" height="${H * 0.19}" fill="${GREEN}"/><text x="${(LW + W) / 2}" y="${H * 0.52}">FINISH ALL</text>
    <rect x="${LW + 8}" y="${H * 0.62}" width="${W - LW - 16}" height="${H * 0.17}" fill="#F4A7CF"/><text x="${(LW + W) / 2}" y="${H * 0.72}">MAY CAUSE</text>
    <rect x="${LW + 8}" y="${H * 0.81}" width="${W - LW - 16}" height="${H * 0.17}" fill="#F4A7CF"/><text x="${(LW + W) / 2}" y="${H * 0.91}">NO ALCOHOL</text>
  </g>
</svg>`);

// 4. the receipt that prints with each prescription: Paxxol header, then the patient's copy
const RW = 1100, RH = 1386;
const line = (y, a, b, bold) => `<text x="50" y="${y}" ${bold ? 'font-weight="700"' : ''}>${a}</text>${b ? `<text x="${RW - 50}" y="${y}" text-anchor="end" ${bold ? 'font-weight="700"' : ''}>${b}</text>` : ''}`;
out('receipt.png', `<svg xmlns="http://www.w3.org/2000/svg" width="${RW}" height="${RH}">
  <rect width="${RW}" height="${RH}" fill="#fbfbf8"/>
  <rect width="${RW}" height="150" fill="${GREEN}"/>
  ${dots(70, 75, 15)}
  <text x="130" y="96" font-family="Arial" font-weight="700" font-size="58" fill="${INK}" letter-spacing="2">PAXXOL</text>
  <g font-family="Arial" font-size="26" fill="${INK}" text-anchor="end"><text x="${RW - 40}" y="48">(647)-931-0055</text><text x="${RW - 40}" y="84">www.pharmvials.com</text><text x="${RW - 40}" y="120">order@pharmvials.com</text></g>
  <g font-family="Consolas, Courier New, monospace" font-size="38" fill="#111">
    <text x="${RW / 2}" y="230" text-anchor="middle" font-weight="700">MAPLE STREET PHARMACY</text>
    <text x="${RW / 2}" y="278" text-anchor="middle" font-size="30">412 Maple St, Mississauga ON</text>
    <line x1="50" y1="320" x2="${RW - 50}" y2="320" stroke="#111" stroke-dasharray="10 8" stroke-width="3"/>
    ${line(380, 'Patient', 'JORDAN LEE', true)}${line(430, 'Rx', '1048213')}${line(480, 'Date', '2026-10-30')}
    ${line(550, 'AMOXICILLIN 500MG CAP', '', true)}${line(600, 'Qty 21', '')}
    ${line(670, 'Drug cost', '$12.60')}${line(720, 'Dispensing fee', '$11.99')}${line(770, 'Plan paid', '-$19.67')}
    <line x1="50" y1="810" x2="${RW - 50}" y2="810" stroke="#111" stroke-width="3"/>
    ${line(870, 'PATIENT PAYS', '$4.92', true)}
    <text x="${RW / 2}" y="980" text-anchor="middle" font-size="30">Keep for your insurance records</text>
    <text x="${RW / 2}" y="1030" text-anchor="middle" font-size="30">Questions? Ask your pharmacist</text>
  </g>
  <g fill="#111">${[...Array(60)].map((_, i) => `<rect x="${250 + i * 10}" y="1120" width="${i % 3 ? 4 : 7}" height="110"/>`).join('')}</g>
</svg>`);
// 5. Prescription Clear Label Tape: blue lettering printed on the clear film, repeated round the roll
out('tape_print.png', `<svg xmlns="http://www.w3.org/2000/svg" width="2400" height="260">${[0, 1, 2].map((i) => `<g transform="translate(${i * 800 + 40} 0)" font-family="Arial" font-weight="700" fill="#2F4FA2"><circle cx="60" cy="130" r="44" fill="none" stroke="#2F4FA2" stroke-width="8"/><text x="36" y="150" font-size="58">Rx</text><text x="130" y="112" font-size="64">Prescription</text><text x="130" y="190" font-size="64">Clear Label Tape</text></g>`).join('')}</svg>`);
console.log('textures written');
