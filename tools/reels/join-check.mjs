/* Puts the last frame of one clip beside the first frame of the next, so a cut
   can be judged before it is cut. Every multi-clip reel needs this: Veo drifts
   away from the last frame it was given, and the gap only shows at the join.

     node reels/join-check.mjs <clipA.mp4> <clipB.mp4> <out.png>

   Decodes in headless Edge, same as contact-sheet.mjs — no ffmpeg needed. Both
   clips must sit in the same folder, because the harness page is written there
   and loads them with relative paths (Chromium blocks file:// video otherwise). */
import { chromium } from 'playwright-core';
import { pathToFileURL } from 'node:url';
import { existsSync, writeFileSync, unlinkSync } from 'node:fs';
import { dirname, basename, join, resolve } from 'node:path';

const [, , aPath, bPath, outPath] = process.argv;
if (!aPath || !bPath || !outPath) {
  console.error('usage: join-check.mjs <clipA.mp4> <clipB.mp4> <out.png>');
  process.exit(1);
}
for (const p of [aPath, bPath]) if (!existsSync(p)) { console.error('no such clip: ' + p); process.exit(1); }
if (resolve(dirname(aPath)) !== resolve(dirname(bPath))) {
  console.error('both clips must be in the same folder'); process.exit(1);
}

const W = 540, H = 960, PAD = 10, LABEL = 40;
const dir = dirname(aPath);
const harness = join(dir, '_join-check.html');
writeFileSync(harness, `<!doctype html><html><body style="margin:0;background:#111">
<canvas id="c" width="${W * 2 + PAD * 3}" height="${H + LABEL + PAD}"></canvas>
<video id="a" src="${encodeURIComponent(basename(aPath))}" muted playsinline style="display:none"></video>
<video id="b" src="${encodeURIComponent(basename(bPath))}" muted playsinline style="display:none"></video>
</body></html>`);

const browser = await chromium.launch({ channel: 'msedge', headless: true });
const page = await browser.newPage({ viewport: { width: W * 2 + PAD * 3, height: H + LABEL + PAD } });
await page.goto(pathToFileURL(harness).href, { waitUntil: 'domcontentloaded' });

const info = await page.evaluate(async ({ W, H, PAD, LABEL }) => {
  const a = document.getElementById('a'), b = document.getElementById('b');
  const c = document.getElementById('c'), x = c.getContext('2d');
  x.fillStyle = '#111'; x.fillRect(0, 0, c.width, c.height);
  const meta = el => new Promise((r, j) => {
    if (el.readyState >= 1) return r();
    el.addEventListener('loadedmetadata', r, { once: true });
    el.addEventListener('error', () => j(new Error('video failed to load')), { once: true });
    setTimeout(() => j(new Error('timed out loading video')), 30000);
  });
  await Promise.all([meta(a), meta(b)]);
  const seek = (el, t) => new Promise(r => { el.addEventListener('seeked', r, { once: true }); el.currentTime = t; });
  await seek(a, Math.max(a.duration - 0.04, 0));
  await seek(b, 0);
  await new Promise(r => setTimeout(r, 300));
  x.drawImage(a, PAD, LABEL, W, H);
  x.drawImage(b, PAD * 2 + W, LABEL, W, H);
  x.fillStyle = '#fff'; x.font = '20px monospace';
  x.fillText('A last frame  ' + a.duration.toFixed(2) + 's', PAD + 4, 26);
  x.fillText('B first frame  0.00s', PAD * 2 + W + 4, 26);
  return { a: a.duration, b: b.duration };
}, { W, H, PAD, LABEL });

await page.locator('#c').screenshot({ path: outPath });
await browser.close();
try { unlinkSync(harness); } catch {}
console.log(`A ${info.a.toFixed(2)}s | B ${info.b.toFixed(2)}s -> ${outPath}`);
