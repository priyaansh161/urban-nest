// Textures for the realism pass (31 Oct 2026, his feedback: "everything looks mushy, cartoonish"): surfaces that
// were procedural in Blender (and so came out plain in the viewer) or plain colour, drawn as real images.
//   roll_side.png     the end of a wound paper roll: fine rings, a brown cardboard core
//   quartz.png        speckled white quartz for the counter top (tiles every 60 cm)
//   vial_box.png      PharmVials' shipping box side (logo, product line, quantity), 33.2 x 37.2 cm face
//   rx_pickup.png     the "Rx Pickup" sign over the baskets
//   node make_refine_textures.cjs
const sharp = require('../../tools/node_modules/sharp');
const fs = require('fs');
const T = __dirname + '/tex/';
(async () => {
  // roll end: 1024 square, rings out to the edge, core hole at 26% of the radius
  {
    const N = 1024, c = N / 2, R = N / 2 - 2, core = R * 0.27, hole = core - 18;
    const px = Buffer.alloc(N * N * 3);
    for (let y = 0; y < N; y++) for (let x = 0; x < N; x++) {
      const r = Math.hypot(x - c, y - c), i = (y * N + x) * 3;
      let v;
      if (r < hole) v = [70, 50, 34];                                         // into the core
      else if (r < core) v = [150 + 12 * Math.sin(r * 0.9), 108, 70];       // cardboard core wall
      else { const ring = 0.5 + 0.5 * Math.sin(r * 2.1) * Math.sin(r * 0.37 + 1.3); const g = 236 - ring * 20; v = [g, g, g - 4]; }
      px[i] = v[0]; px[i + 1] = v[1]; px[i + 2] = v[2];
    }
    await sharp(px, { raw: { width: N, height: N, channels: 3 } }).png().toFile(T + 'roll_side.png');
  }
  // quartz: warm white with grey and a few dark flecks, 1024 square = 60 cm
  {
    const N = 1024, px = Buffer.alloc(N * N * 3);
    let s = 7; const rnd = () => (s = (s * 16807) % 2147483647) / 2147483647;
    for (let i = 0; i < N * N; i++) { const n = 226 + (rnd() - 0.5) * 8; px[i * 3] = n; px[i * 3 + 1] = n; px[i * 3 + 2] = n - 3; }
    const fleck = (r, tone) => { const x = Math.floor(rnd() * N), y = Math.floor(rnd() * N);
      for (let dy = -r; dy <= r; dy++) for (let dx = -r; dx <= r; dx++) if (dx * dx + dy * dy <= r * r) {
        const i = (((y + dy + N) % N) * N + ((x + dx + N) % N)) * 3; px[i] = tone; px[i + 1] = tone; px[i + 2] = tone; } };
    for (let k = 0; k < 2600; k++) fleck(1 + Math.floor(rnd() * 2), 180 + rnd() * 30);
    for (let k = 0; k < 500; k++) fleck(1, 110 + rnd() * 40);
    for (let k = 0; k < 900; k++) fleck(1 + Math.floor(rnd() * 2), 245);
    await sharp(px, { raw: { width: N, height: N, channels: 3 } }).blur(0.6).png().toFile(T + 'quartz.png');
  }
  // the vial box side, with PharmVials' own logo
  {
    const logo = await sharp(__dirname + '/refs/pharmvials-logo.svg', { density: 300 }).resize(360, 360).png().toBuffer();
    const W = 900, H = 1000;
    const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${H}"><rect width="${W}" height="${H}" fill="#c9a77a"/>
      <rect x="40" y="40" width="${W - 80}" height="${H - 80}" fill="none" stroke="#a7865c" stroke-width="3"/>
      <rect x="120" y="520" width="${W - 240}" height="300" fill="#f6f3ee"/>
      <g font-family="Arial" fill="#1f2d36"><text x="${W / 2}" y="590" text-anchor="middle" font-weight="700" font-size="52">13 DR AMBER VIALS</text>
      <text x="${W / 2}" y="650" text-anchor="middle" font-size="38">Child Resistant · Push Down &amp; Turn</text>
      <text x="${W / 2}" y="720" text-anchor="middle" font-size="36">QTY 320 per box</text>
      <text x="${W / 2}" y="785" text-anchor="middle" font-size="30">www.pharmvials.com</text></g>
      <g fill="#7a5d3a" font-family="Arial" font-size="26"><text x="80" y="${H - 70}">THIS SIDE UP ↑</text><text x="${W - 80}" y="${H - 70}" text-anchor="end">KEEP DRY</text></g></svg>`;
    await sharp(Buffer.from(svg)).composite([{ input: logo, left: (W - 360) / 2, top: 110 }]).png().toFile(T + 'vial_box.png');
  }
  // Rx Pickup sign: white acrylic, teal band, Rx mark
  await sharp(Buffer.from(`<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="360"><rect width="1200" height="360" rx="24" fill="#ffffff"/>
    <rect width="300" height="360" rx="24" fill="#1f7a8c"/><rect x="276" width="24" height="360" fill="#1f7a8c"/>
    <text x="150" y="235" text-anchor="middle" font-family="Georgia, serif" font-style="italic" font-weight="700" font-size="190" fill="#fff">℞</text>
    <text x="360" y="215" font-family="Arial" font-weight="700" font-size="140" fill="#1f2d36" letter-spacing="6">PICKUP</text>
    <text x="364" y="295" font-family="Arial" font-size="40" fill="#5a6b75">Prescriptions ready for collection</text></svg>`)).png().toFile(T + 'rx_pickup.png');
  console.log('refine textures written');
})();
