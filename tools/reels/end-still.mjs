/* Blurred last-frame still with the logo end card on top, 1080x1920.
     node reels/end-still.mjs <last-frame.jpg> <out.png> [mode] ["closing line"]
   mode "nologo" = blurred room only; anything else (e.g. "logo") = logo card.
   The optional closing line sits above the logo — the reel's last thought,
   read before the brand signs off underneath. Set in Bodoni Moda italic to
   match the tagline, loaded from Google Fonts because it is not installed. */
import { chromium } from 'playwright-core';
import { readFileSync } from 'node:fs';
const [,, bgPath, outPath, mode, line = ''] = process.argv;
const bg = 'data:image/jpeg;base64,' + readFileSync(bgPath).toString('base64');
const card = 'data:image/png;base64,' + readFileSync('C:/Users/priya/OneDrive/Projects/urban-nest-reels/brand-look/end-card-logo-tagline.png').toString('base64');
const b = await chromium.launch({ channel: 'msedge', headless: true });
const t = await b.newPage({ viewport: { width: 1080, height: 1920 } });
await t.setContent('<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Bodoni+Moda:ital,wght@1,400&display=block"><body style="margin:0"><canvas id="c" width="1080" height="1920" style="display:block"></canvas></body>', { waitUntil: 'networkidle' });
await t.evaluate(([bg, card, noLogo, line]) => new Promise(async res => {
  if (line) await document.fonts.load('italic 400 50px "Bodoni Moda"');
  const load = s => new Promise(r => { const i = new Image(); i.onload = () => r(i); i.src = s; });
  const [i, k] = await Promise.all([load(bg), load(card)]);
  const x = document.getElementById('c').getContext('2d');
  const s = Math.max(1080 / i.width, 1920 / i.height) * 1.08, w = i.width * s, h = i.height * s;
  x.filter = 'blur(28px)'; x.drawImage(i, (1080 - w) / 2, (1920 - h) / 2, w, h);
  x.filter = 'none'; x.fillStyle = 'rgba(20,12,6,.32)'; x.fillRect(0, 0, 1080, 1920);
  if (!noLogo) x.drawImage(k, 0, 0, 1080, 1920);
  if (line) {
    // Wrapped to at most two lines, centred well above the logo (which starts ~y 710).
    x.font = 'italic 400 50px "Bodoni Moda", Georgia, serif';
    x.fillStyle = 'rgba(255,255,255,.95)'; x.textAlign = 'center';
    x.shadowColor = 'rgba(0,0,0,.35)'; x.shadowBlur = 18;
    const words = line.split(' '), rows = []; let r = '';
    for (const wd of words) { const n = r ? r + ' ' + wd : wd; if (x.measureText(n).width > 860 && r) { rows.push(r); r = wd; } else r = n; }
    if (r) rows.push(r);
    const lh = 66, top = 560 - (rows.length - 1) * lh;
    rows.forEach((row, j) => x.fillText(row, 540, top + j * lh));
  }
  res();
}), [bg, card, mode === 'nologo', line]);
await t.locator('#c').screenshot({ path: outPath }); await b.close(); console.log('ok');
