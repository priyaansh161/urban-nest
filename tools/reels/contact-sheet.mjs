/* Builds a contact sheet from a video clip, so a Flow render can actually be
   inspected without ffmpeg. Decodes in headless Edge (real browser, so H.264
   works) and seeks to evenly spaced timestamps.

     node reels/contact-sheet.mjs <clip.mp4> <out.png> [tiles]

   Default 8 tiles in a 4x2 grid, each labelled with its timestamp. */
import { chromium } from 'playwright-core';
import { pathToFileURL } from 'node:url';
import { existsSync, writeFileSync, unlinkSync } from 'node:fs';
import { dirname, basename, join } from 'node:path';

const [, , clipPath, outPath, tilesArg = '8'] = process.argv;
if (!clipPath || !outPath) { console.error('usage: contact-sheet.mjs <clip> <out.png> [tiles]'); process.exit(1); }
if (!existsSync(clipPath)) { console.error('no such clip: ' + clipPath); process.exit(1); }
const TILES = +tilesArg;
const COLS = 4, ROWS = Math.ceil(TILES / COLS), TW = 300, TH = 534, PAD = 6, LABEL = 22;

const browser = await chromium.launch({ channel: 'msedge', headless: true });
const page = await browser.newPage({
  viewport: { width: COLS * (TW + PAD) + PAD, height: ROWS * (TH + LABEL + PAD) + PAD },
});

/* Chromium blocks a file:// video inside a setContent page, so the harness HTML
   is written next to the clip and loaded over file:// with a relative src. */
const harness = join(dirname(clipPath), '_contact-sheet.html');
writeFileSync(harness, `<!doctype html><html><body style="margin:0;background:#111">
  <canvas id="sheet" width="${COLS * (TW + PAD) + PAD}" height="${ROWS * (TH + LABEL + PAD) + PAD}"></canvas>
  <video id="v" src="${encodeURIComponent(basename(clipPath))}" muted playsinline style="display:none"></video>
</body></html>`);
await page.goto(pathToFileURL(harness).href, { waitUntil: 'domcontentloaded' });

const result = await page.evaluate(async ({ TILES, COLS, TW, TH, PAD, LABEL }) => {
  const v = document.getElementById('v');
  const c = document.getElementById('sheet');
  const ctx = c.getContext('2d');
  ctx.fillStyle = '#111'; ctx.fillRect(0, 0, c.width, c.height);

  await new Promise((res, rej) => {
    if (v.readyState >= 1) return res();
    v.addEventListener('loadedmetadata', res, { once: true });
    v.addEventListener('error', () => rej(new Error('video failed to load — codec unsupported?')), { once: true });
    setTimeout(() => rej(new Error('timed out loading video')), 30000);
  });

  const dur = v.duration;
  const seek = t => new Promise(res => { v.addEventListener('seeked', res, { once: true }); v.currentTime = t; });

  for (let i = 0; i < TILES; i++) {
    const t = Math.min(dur * (i / (TILES - 1)), Math.max(dur - 0.05, 0));
    await seek(t);
    await new Promise(r => setTimeout(r, 120));
    const col = i % COLS, row = Math.floor(i / COLS);
    const x = PAD + col * (TW + PAD), y = PAD + row * (TH + LABEL + PAD);
    ctx.drawImage(v, x, y + LABEL, TW, TH);
    ctx.fillStyle = '#fff';
    ctx.font = '14px monospace';
    ctx.fillText(t.toFixed(2) + 's', x + 4, y + 15);
  }
  return { duration: dur, w: v.videoWidth, h: v.videoHeight };
}, { TILES, COLS, TW, TH, PAD, LABEL });

await page.locator('#sheet').screenshot({ path: outPath });
await browser.close();
try { unlinkSync(harness); } catch {}
console.log(`${result.w}x${result.h}, ${result.duration.toFixed(2)}s -> ${outPath}`);
