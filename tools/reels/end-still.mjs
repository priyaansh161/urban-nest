/* Blurred last-frame still with the logo end card on top, 1080x1920. */
import { chromium } from 'playwright-core';
import { readFileSync } from 'node:fs';
const [,, bgPath, outPath, mode] = process.argv; // mode "nologo" = blurred room only
const bg = 'data:image/jpeg;base64,' + readFileSync(bgPath).toString('base64');
const card = 'data:image/png;base64,' + readFileSync('C:/Users/priya/OneDrive/Projects/urban-nest-reels/brand-look/end-card-logo-tagline.png').toString('base64');
const b = await chromium.launch({ channel: 'msedge', headless: true });
const t = await b.newPage({ viewport: { width: 1080, height: 1920 } });
await t.setContent('<canvas id="c" width="1080" height="1920" style="display:block"></canvas><body style="margin:0">');
await t.evaluate(([bg, card, noLogo]) => new Promise(res => {
  const load = s => new Promise(r => { const i = new Image(); i.onload = () => r(i); i.src = s; });
  Promise.all([load(bg), load(card)]).then(([i, k]) => {
    const x = document.getElementById('c').getContext('2d');
    const s = Math.max(1080 / i.width, 1920 / i.height) * 1.08, w = i.width * s, h = i.height * s;
    x.filter = 'blur(28px)'; x.drawImage(i, (1080 - w) / 2, (1920 - h) / 2, w, h);
    x.filter = 'none'; x.fillStyle = 'rgba(20,12,6,.32)'; x.fillRect(0, 0, 1080, 1920);
    if (!noLogo) x.drawImage(k, 0, 0, 1080, 1920); res();
  });
}), [bg, card, mode === "nologo"]);
await t.locator('#c').screenshot({ path: outPath }); await b.close(); console.log('ok');
