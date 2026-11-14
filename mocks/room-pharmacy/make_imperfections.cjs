// Imperfection maps (31 Oct 2026): what separates "3D" from "real" up close is that no real surface is evenly
// shiny. These are ROUGHNESS maps (written straight into the green channel glTF reads), tiling, 1024 px:
//   rough_glossy.png    glossy moulded plastic / glass (vials, screen, printer lid): base 0.07, faint fingerprint
//                       whorls and smudges up to ~0.32, a few hairline scratches
//   rough_satin.png     satin plastic (caps, trays, housings): base 0.34, soft blotches and handling wear 0.28-0.5
//   node make_imperfections.cjs
const sharp = require('../../tools/node_modules/sharp');
const T = __dirname + '/tex/';
const N = 1024;
let seed = 11; const rnd = () => (seed = (seed * 16807) % 2147483647) / 2147483647;

function map(base, spots) {
  const a = new Float32Array(N * N).fill(base);
  const add = (cx, cy, f) => { const r = 60; for (let dy = -r; dy <= r; dy++) for (let dx = -r; dx <= r; dx++) {
    const x = (cx + dx + N) % N, y = (cy + dy + N) % N, v = f(dx, dy); if (v) a[y * N + x] = Math.max(a[y * N + x], v); } };
  spots(add);
  // fine grain over everything
  for (let i = 0; i < N * N; i++) a[i] += (rnd() - 0.5) * 0.02;
  const px = Buffer.alloc(N * N * 3);
  for (let i = 0; i < N * N; i++) { const g = Math.round(Math.min(1, Math.max(0, a[i])) * 255); px[i * 3] = 0; px[i * 3 + 1] = g; px[i * 3 + 2] = 0; }
  return px;
}

(async () => {
  // glossy: fingerprints (elliptical whorls of ridges), smudges, hairline scratches
  const glossy = map(0.07, (add) => {
    for (let k = 0; k < 14; k++) {
      const cx = rnd() * N | 0, cy = rnd() * N | 0, rx = 22 + rnd() * 16, ry = rx * (1.25 + rnd() * 0.3), ang = rnd() * Math.PI;
      add(cx, cy, (dx, dy) => { const u = (dx * Math.cos(ang) + dy * Math.sin(ang)) / rx, v = (-dx * Math.sin(ang) + dy * Math.cos(ang)) / ry, d = Math.hypot(u, v);
        if (d > 1) return 0; const ridge = 0.5 + 0.5 * Math.sin(d * 34); return 0.07 + ridge * 0.2 * (1 - d * d); });
    }
    for (let k = 0; k < 10; k++) {
      const cx = rnd() * N | 0, cy = rnd() * N | 0, r = 25 + rnd() * 30;
      add(cx, cy, (dx, dy) => { const d = Math.hypot(dx, dy) / r; return d < 1 ? 0.07 + 0.16 * (1 - d) * (1 - d) : 0; });
    }
  });
  // hairline scratches drawn after, as thin bright lines
  const scratches = [];
  for (let k = 0; k < 18; k++) { const x = rnd() * N, y = rnd() * N, a = rnd() * Math.PI, L = 40 + rnd() * 160; scratches.push(`<line x1="${x}" y1="${y}" x2="${x + Math.cos(a) * L}" y2="${y + Math.sin(a) * L}" stroke="rgb(0,${(0.3 * 255) | 0},0)" stroke-width="${0.6 + rnd()}"/>`); }
  await sharp(glossy, { raw: { width: N, height: N, channels: 3 } })
    .composite([{ input: Buffer.from(`<svg xmlns="http://www.w3.org/2000/svg" width="${N}" height="${N}">${scratches.join('')}</svg>`) }])
    .blur(0.5).png().toFile(T + 'rough_glossy.png');
  // satin: soft handling blotches, slightly glossier worn patches
  const satin = map(0.34, (add) => {
    for (let k = 0; k < 40; k++) {
      const cx = rnd() * N | 0, cy = rnd() * N | 0, r = 20 + rnd() * 40, up = rnd() < 0.6;
      add(cx, cy, (dx, dy) => { const d = Math.hypot(dx, dy) / r; return d < 1 ? (up ? 0.34 + 0.14 * (1 - d) : 0.34) : 0; });
    }
  });
  await sharp(satin, { raw: { width: N, height: N, channels: 3 } }).blur(2).png().toFile(T + 'rough_satin.png');
  console.log('imperfection maps written');
})();
