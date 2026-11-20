// Paints a stale baked shadow out of a lightmapped room piece (a product was moved or removed after the bake).
// Finds the up-facing face of the named material at the given height (or the topmost), maps world x/z to lightmap
// pixels through that face's TEXCOORD_1, and refills a circle around (x, z) by interpolating across it from the clean
// pixels on both sides, plus the bake grain copied from beside the hole. Writes the .glb in place (a .bak beside it).
//   node tools/lm-inpaint.mjs <file.glb> <material prefix> <x> <z> <radius m> [--y=<face height>] [--along=x|z] [--preview=out.png]
// x/z are in the glb's own world frame (node translation added), which is the room's frame for room pieces.
import { NodeIO } from '@gltf-transform/core';
import { ALL_EXTENSIONS } from '@gltf-transform/extensions';
import draco3d from 'draco3dgltf';
import sharp from 'sharp';
import { copyFileSync, existsSync } from 'node:fs';

const args = process.argv.slice(2).filter(a => !a.startsWith('--'));
const opt = Object.fromEntries(process.argv.slice(2).filter(a => a.startsWith('--')).map(a => { const [k, ...v] = a.slice(2).split('='); return [k, v.length ? v.join('=') : true]; }));
const [file, prefix, X, Z, R] = [args[0], args[1], +args[2], +args[3], +args[4]];
const io = new NodeIO().registerExtensions(ALL_EXTENSIONS).registerDependencies({
  'draco3d.decoder': await draco3d.createDecoderModule(), 'draco3d.encoder': await draco3d.createEncoderModule() });
const doc = await io.read(file);
const root = doc.getRoot();

// the face's vertices: world x, z and lightmap uv
let pts = [], lmTex = null;
for (const n of root.listNodes()) {
  const me = n.getMesh(); if (!me) continue; const T = n.getWorldMatrix();
  for (const p of me.listPrimitives()) {
    const m = p.getMaterial(); if (!m || !m.getName().startsWith(prefix)) continue;
    lmTex = m.getEmissiveTexture() || lmTex;
    const P = p.getAttribute('POSITION'), N = p.getAttribute('NORMAL'), U = p.getAttribute('TEXCOORD_1');
    const v = [0, 0, 0], nn = [0, 0, 0], u = [0, 0], all = [];
    for (let i = 0; i < P.getCount(); i++) {
      P.getElement(i, v); N.getElement(i, nn); U.getElement(i, u);
      const w = [T[0] * v[0] + T[4] * v[1] + T[8] * v[2] + T[12], T[1] * v[0] + T[5] * v[1] + T[9] * v[2] + T[13], T[2] * v[0] + T[6] * v[1] + T[10] * v[2] + T[14]];
      if (nn[1] > 0.95) all.push([w[0], w[2], u[0], u[1], w[1]]);
    }
    pts.push(...all);
  }
}
const yTarget = opt.y !== undefined ? +opt.y : Math.max(...pts.map(p => p[4]));
pts = pts.filter(p => Math.abs(p[4] - yTarget) < 0.003);
// keep the face piece that contains the spot: nearest vertices only (a material can have several up faces at one height)
pts.sort((a, b) => Math.hypot(a[0] - X, a[1] - Z) - Math.hypot(b[0] - X, b[1] - Z));
pts = pts.slice(0, Math.max(3, Math.min(pts.length, 12)));
if (pts.length < 3 || !lmTex) throw new Error('no up face for ' + prefix + ' at y ' + yTarget);

function fit(k) {   // least squares uv = a x + b z + c
  const A = [[0, 0, 0], [0, 0, 0], [0, 0, 0]], b = [0, 0, 0];
  for (const p of pts) { const r = [p[0], p[1], 1]; for (let i = 0; i < 3; i++) { b[i] += r[i] * p[k]; for (let j = 0; j < 3; j++) A[i][j] += r[i] * r[j]; } }
  const M = A.map((r, i) => [...r, b[i]]);
  for (let i = 0; i < 3; i++) { let mx = i; for (let j = i + 1; j < 3; j++) if (Math.abs(M[j][i]) > Math.abs(M[mx][i])) mx = j; [M[i], M[mx]] = [M[mx], M[i]];
    for (let j = 0; j < 3; j++) if (j !== i) { const f = M[j][i] / M[i][i]; for (let c = i; c < 4; c++) M[j][c] -= f * M[i][c]; } }
  return M.map((r, i) => r[3] / r[i]);
}
const fu = fit(2), fv = fit(3);
let err = 0; for (const p of pts) err = Math.max(err, Math.abs(fu[0] * p[0] + fu[1] * p[1] + fu[2] - p[2]), Math.abs(fv[0] * p[0] + fv[1] * p[1] + fv[2] - p[3]));
if (err > 0.002) throw new Error('face is not one flat uv island near the spot (fit error ' + err.toFixed(4) + ')');

const img = sharp(Buffer.from(lmTex.getImage()));
const { data, info } = await img.clone().raw().toBuffer({ resolveWithObject: true });
const W = info.width, H = info.height, C = info.channels;
const px = (x, z) => [(fu[0] * x + fu[1] * z + fu[2]) * W - 0.5, (fv[0] * x + fv[1] * z + fv[2]) * H - 0.5];
const [cu, cv] = px(X, Z);
const ru = Math.hypot(fu[0], fu[1]) * W * R, rv = Math.hypot(fv[0], fv[1]) * H * R;   // radius in pixels on each image axis
// which image axis runs along world x / z: interpolate along the axis asked for (default: the face's longer side is avoided)
const uIsX = Math.abs(fu[0]) > Math.abs(fu[1]);
const along = opt.along || 'z';
const interpAlongU = (along === 'x') === uIsX;
const get = (u, v, c) => data[(v * W + u) * C + c];
// an edge sample: the mean of 7 pixels along the edge, so one grain speck doesn't streak across the fill
const edge = (u, v, c) => { let s = 0, k = 0; for (let d = -3; d <= 3; d++) { const uu = interpAlongU ? u : u + d, vv = interpAlongU ? v + d : v; if (uu >= 0 && vv >= 0 && uu < W && vv < H) { s += get(uu, vv, c); k++; } } return s / k; };
const out = Buffer.from(data);
let n = 0;
// --rect=u0,v0,u1,v1 (lightmap pixels, from the preview): fill that box straight across along --along instead of the circle
if (opt.rect) {
  const [u0, v0, u1, v1] = opt.rect.split(',').map(Number);
  for (let v = v0; v <= v1; v++) for (let u = u0; u <= u1; u++) {
    const t = interpAlongU ? (u - u0 + 3) / (u1 - u0 + 6) : (v - v0 + 3) / (v1 - v0 + 6);
    const a = interpAlongU ? [u0 - 3, v] : [u, v0 - 3], b = interpAlongU ? [u1 + 3, v] : [u, v1 + 3];
    for (let c = 0; c < C; c++) out[(v * W + u) * C + c] = Math.round(edge(a[0], a[1], c) * (1 - t) + edge(b[0], b[1], c) * t);
    n++;
  }
}
const r0 = interpAlongU ? rv : ru, r1 = interpAlongU ? ru : rv;
if (!opt.rect) for (let dv = -Math.ceil(rv); dv <= Math.ceil(rv); dv++) for (let du = -Math.ceil(ru); du <= Math.ceil(ru); du++) {
  const e = (du / ru) ** 2 + (dv / rv) ** 2; if (e > 1) continue;
  const u = Math.round(cu + du), v = Math.round(cv + dv); if (u < 0 || v < 0 || u >= W || v >= H) continue;
  // chord through this pixel along the interpolation axis
  const off = interpAlongU ? dv / rv : du / ru, half = Math.sqrt(Math.max(0, 1 - off * off)) * r1 + 2;
  let a, b, t;
  if (interpAlongU) { a = [Math.round(cu - half), v]; b = [Math.round(cu + half), v]; t = (u - a[0]) / (b[0] - a[0]); }
  else { a = [u, Math.round(cv - half)]; b = [u, Math.round(cv + half)]; t = (v - a[1]) / (b[1] - a[1]); }
  // grain: the pixel the same distance beyond the edge minus its own smooth value is noise; borrow it
  const g = interpAlongU ? [u, Math.round(cv + (dv >= 0 ? -1 : 1) * (rv * 2 + 2))] : [Math.round(cu + (du >= 0 ? -1 : 1) * (ru * 2 + 2)), v];
  for (let c = 0; c < C; c++) {
    const base = edge(a[0], a[1], c) * (1 - t) + edge(b[0], b[1], c) * t;
    let noise = 0;
    if (g[0] > 1 && g[1] > 1 && g[0] < W - 2 && g[1] < H - 2) {
      let s = 0; for (let k = -1; k <= 1; k++) for (let l = -1; l <= 1; l++) s += get(g[0] + k, g[1] + l, c);
      noise = get(g[0], g[1], c) - s / 9;
    }
    const soft = Math.min(1, (1 - e) * 4);            // feather the last quarter of the circle into what's there
    out[(v * W + u) * C + c] = Math.max(0, Math.min(255, Math.round((base + noise * 0.8) * soft + get(u, v, c) * (1 - soft))));
  }
  n++;
}
const mime = lmTex.getMimeType();
const raw = sharp(out, { raw: { width: W, height: H, channels: C } });
const enc = mime === 'image/webp' ? await raw.webp({ quality: 92 }).toBuffer() : mime === 'image/jpeg' ? await raw.jpeg({ quality: 92 }).toBuffer() : await raw.png().toBuffer();
console.log(`${lmTex.getName()} ${W}x${H}: spot at px ${cu.toFixed(1)},${cv.toFixed(1)}, radius ${ru.toFixed(1)}x${rv.toFixed(1)} px, ${n} px refilled`);
if (opt.preview) {
  const L = Math.max(0, Math.round(cu - ru * 4)), T = Math.max(0, Math.round(cv - rv * 4));
  const w = Math.min(W - L, Math.round(ru * 8)), h = Math.min(H - T, Math.round(rv * 8));
  const before = await sharp(data, { raw: { width: W, height: H, channels: C } }).extract({ left: L, top: T, width: w, height: h }).resize(w * 4, h * 4, { kernel: 'nearest' }).png().toBuffer();
  const after = await sharp(out, { raw: { width: W, height: H, channels: C } }).extract({ left: L, top: T, width: w, height: h }).resize(w * 4, h * 4, { kernel: 'nearest' }).png().toBuffer();
  await sharp({ create: { width: w * 8 + 8, height: h * 4, channels: 3, background: '#f00' } }).composite([{ input: before, left: 0, top: 0 }, { input: after, left: w * 4 + 8, top: 0 }]).png().toFile(opt.preview);
}
if (opt.dry) process.exit(0);
lmTex.setImage(new Uint8Array(enc));
if (!existsSync(file + '.bak')) copyFileSync(file, file + '.bak');
await io.write(file, doc);
console.log('written', file);
