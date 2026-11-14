// Paxxol blister card artwork, redrawn from PharmVials' product photos (refs/paxxol-*): the teal dotted
// cover, the "ADHERE RX LABEL(S) HERE" panel, and the dose grids (Jumbo and Tri-Fold 4 x 7, Twin 2 x 7) with
// their grey/teal window borders, dose times across the top and days down the side.
// Each grid also writes a JSON of its window rectangles (fractions of the panel), so the Blender script
// can sit a blister bubble exactly in every window.
//   node make_blister_textures.cjs   (writes tex/pax_*.png + tex/pax_*.json)
const sharp = require('../../tools/node_modules/sharp');
const fs = require('fs');
const T = __dirname + '/tex/';
const TEAL = '#5BC8D6', GREY = '#9AA0A6', INK = '#2a2a2a';
const DAYS = ['MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT', 'SUN'];

const logo = (cx, cy, s) => {                       // Paxxol's dotted mark: a rounded field of teal dots
  let c = ''; const rows = [3, 5, 6, 6, 5, 3];
  rows.forEach((n, r) => { for (let i = 0; i < n; i++) { const big = (i + r) % 3 === 0;
    c += `<circle cx="${cx + (i - (n - 1) / 2) * s}" cy="${cy + (r - 2.5) * s}" r="${s * (big ? 0.42 : 0.3)}" fill="${TEAL}"/>`; } });
  return c;
};

function cover(name, title, W = 1200, H = 1600) {
  return sharp(Buffer.from(`<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${H}">
    <rect width="${W}" height="${H}" fill="#f7f8fa"/>
    ${logo(W / 2, H * 0.22, W * 0.06)}
    <text x="${W / 2}" y="${H * 0.42}" text-anchor="middle" font-family="Arial" font-weight="700" font-size="${W * 0.12}" fill="${TEAL}" letter-spacing="6">PAXXOL</text>
    <text x="${W / 2}" y="${H * 0.455}" text-anchor="middle" font-family="Arial" font-size="${W * 0.022}" fill="${TEAL}" letter-spacing="3">INNOVATING PACKAGING SOLUTION</text>
    <text x="${W / 2}" y="${H * 0.6}" text-anchor="middle" font-family="Arial" font-weight="700" font-size="${W * 0.085}" fill="${INK}">${title}</text>
    <text x="${W / 2}" y="${H * 0.64}" text-anchor="middle" font-family="Arial" font-weight="700" font-size="${W * 0.04}" fill="${INK}">Compliance Management</text>
    <circle cx="${W / 2}" cy="${H * 0.81}" r="${W * 0.035}" fill="none" stroke="#999" stroke-width="6"/>
    <text x="${W / 2}" y="${H * 0.885}" text-anchor="middle" font-family="Arial" font-size="${W * 0.025}" fill="${INK}">Eco-Friendly Future</text>
    <text x="${W / 2}" y="${H * 0.915}" text-anchor="middle" font-family="Arial" font-weight="700" font-size="${W * 0.034}" fill="${INK}">STREAMLINED MEDICATION</text>
    <text x="${W / 2}" y="${H * 0.94}" text-anchor="middle" font-family="Arial" font-size="${W * 0.022}" fill="${INK}">WWW.PAXXOL.COM</text></svg>`)).png().toFile(T + name);
}

function labelPanel(name, W = 1200, H = 1600) {
  const m = (x, y, dx, dy) => `<path d="M ${x} ${y + dy} L ${x} ${y} L ${x + dx} ${y}" fill="none" stroke="#444" stroke-width="6"/>`;
  return sharp(Buffer.from(`<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${H}">
    <rect width="${W}" height="${H}" fill="#f7f8fa"/>
    ${m(80, 90, 120, 120)}${m(W - 80, 90, -120, 120)}${m(80, H - 170, 120, -120)}${m(W - 80, H - 170, -120, -120)}
    <text x="${W / 2}" y="${H * 0.45}" text-anchor="middle" font-family="Arial" font-size="40" fill="#b5b8bc" letter-spacing="2">ADHERE RX LABEL(S) HERE</text>
    <g font-family="Arial" font-size="30" fill="${INK}"><text x="90" y="${H - 60}">Assembled by: ________</text><text x="${W - 90}" y="${H - 60}" text-anchor="end">Pharmacist initials: ____</text></g></svg>`)).png().toFile(T + name);
}

function grid(name, cols, heads, W, H) {
  const top = H * 0.07, bot = H * 0.06, left = W * 0.05, right = W * 0.12;
  const cw = (W - left - right) / cols, rh = (H - top - bot) / 7, pad = Math.min(cw, rh) * 0.08;
  let s = `<rect width="${W}" height="${H}" fill="#f7f8fa"/>`; const wins = [];
  for (let c = 0; c < cols; c++) {
    const col = c % 2 ? TEAL : GREY, x = left + c * cw;
    s += `<rect x="${x + pad * 0.4}" y="${top - pad * 0.2}" width="${cw - pad * 0.8}" height="${H - top - bot + pad * 0.4}" rx="${pad * 1.5}" fill="${col}" opacity="0.9"/>`;
    s += `<text x="${x + cw / 2}" y="${top - pad * 1.6}" text-anchor="middle" font-family="Arial" font-weight="700" font-size="${W * 0.03}" fill="${INK}">${heads[c]}</text>`;
    s += `<text x="${x + cw / 2}" y="${H - bot + pad * 3.2}" text-anchor="middle" font-family="Arial" font-weight="700" font-size="${W * 0.03}" fill="${INK}">${heads[c]}</text>`;
    for (let r = 0; r < 7; r++) {
      const wx = x + pad * 1.6, wy = top + r * rh + pad, ww = cw - pad * 3.2, wh = rh - pad * 2;
      s += `<rect x="${wx}" y="${wy}" width="${ww}" height="${wh}" rx="${pad * 1.8}" fill="#dfe3e6" stroke="#ffffff" stroke-width="${pad * 0.5}"/>`;
      wins.push([wx / W, wy / H, ww / W, wh / H]);
    }
  }
  DAYS.forEach((d, r) => { s += `<text transform="translate(${W - right * 0.62} ${top + (r + 0.5) * rh}) rotate(90)" text-anchor="middle" font-family="Arial" font-weight="700" font-size="${W * 0.034}" fill="${INK}">${d}</text>`; });
  s += `<text transform="translate(${W - right * 0.18} ${H * 0.2}) rotate(90)" font-family="Arial" font-size="${W * 0.022}" fill="${INK}">Client: ______________</text>`;
  fs.writeFileSync(T + name.replace('.png', '.json'), JSON.stringify(wins));
  return sharp(Buffer.from(`<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${H}">${s}</svg>`)).png().toFile(T + name);
}

(async () => {
  await cover('pax_cover_jumbo.png', 'Jumbo');
  await cover('pax_cover_twin.png', 'Twin Pack', 700, 1600);
  await cover('pax_cover_trifold.png', 'Tri-Fold');
  await labelPanel('pax_label_panel.png');
  await labelPanel('pax_label_panel_narrow.png', 700, 1600);
  await grid('pax_grid_jumbo.png', 4, ['Breakfast', 'Lunch', 'Supper', 'Bedtime'], 1200, 1600);
  await grid('pax_grid_trifold.png', 4, ['Bedtime', 'Supper', 'Lunch', 'Breakfast'], 1200, 1600);
  await grid('pax_grid_twin.png', 2, ['Bedtime', 'Breakfast'], 700, 1600);
  console.log('blister textures written');
})();
