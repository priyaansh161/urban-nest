// Photo-to-texture, the way Meshy dresses a model: take one face of a real product out of a photo (its four
// corners, clockwise from top-left), straighten it with a perspective warp, and save it as a flat texture to
// paste on the matching face of the box model.
//   node rectify.cjs <photo> <out.png> <w> <h> x0,y0 x1,y1 x2,y2 x3,y3
const sharp = require('../../tools/node_modules/sharp');

// homography mapping the unit square (0,0)(1,0)(1,1)(0,1) onto four points
function squareToQuad(p) {
  const [[x0, y0], [x1, y1], [x2, y2], [x3, y3]] = p;
  const dx1 = x1 - x2, dx2 = x3 - x2, dy1 = y1 - y2, dy2 = y3 - y2;
  const sx = x0 - x1 + x2 - x3, sy = y0 - y1 + y2 - y3;
  const den = dx1 * dy2 - dx2 * dy1;
  const g = (sx * dy2 - dx2 * sy) / den, h = (dx1 * sy - sx * dy1) / den;
  return [x1 - x0 + g * x1, x3 - x0 + h * x3, x0, y1 - y0 + g * y1, y3 - y0 + h * y3, y0, g, h];
}

(async () => {
  const [src, out, W, H, ...pts] = process.argv.slice(2);
  const quad = pts.map(s => s.split(',').map(Number));
  const { data, info } = await sharp(src).removeAlpha().raw().toBuffer({ resolveWithObject: true });
  const [a, b, c, d, e, f, g, h] = squareToQuad(quad);
  const w = +W, ht = +H, o = Buffer.alloc(w * ht * 3);
  const px = (x, y, k) => data[(Math.min(info.height - 1, Math.max(0, y)) * info.width + Math.min(info.width - 1, Math.max(0, x))) * 3 + k];
  for (let j = 0; j < ht; j++) for (let i = 0; i < w; i++) {
    const u = (i + 0.5) / w, v = (j + 0.5) / ht, z = g * u + h * v + 1;
    const X = (a * u + b * v + c) / z, Y = (d * u + e * v + f) / z;
    const x0 = Math.floor(X), y0 = Math.floor(Y), fx = X - x0, fy = Y - y0;
    for (let k = 0; k < 3; k++)                                  // bilinear
      o[(j * w + i) * 3 + k] = (px(x0, y0, k) * (1 - fx) + px(x0 + 1, y0, k) * fx) * (1 - fy) + (px(x0, y0 + 1, k) * (1 - fx) + px(x0 + 1, y0 + 1, k) * fx) * fy;
  }
  await sharp(o, { raw: { width: w, height: ht, channels: 3 } }).png().toFile(out);
  console.log('wrote', out);
})();
