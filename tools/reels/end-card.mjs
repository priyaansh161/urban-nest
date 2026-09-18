/* Transparent 1080x1920 end-card overlay for reels: white logo mark,
   URBAN NEST wordmark, tagline. Laid over a blurred last frame in Edits. */
import { chromium } from 'playwright-core';
import { readFileSync } from 'node:fs';
const logo = 'data:image/png;base64,' + readFileSync(new URL('../../logo-icon.png', import.meta.url)).toString('base64');
const OUT = 'C:/Users/priya/OneDrive/Projects/urban-nest-reels/brand-look/end-card-logo-tagline.png';
const b = await chromium.launch({ channel: 'msedge', headless: true });
const t = await b.newPage({ viewport: { width: 1080, height: 1920 } });
await t.setContent(`<!doctype html><html><head>
<link href="https://fonts.googleapis.com/css2?family=Bodoni+Moda:ital,wght@0,500;1,400&family=DM+Sans:wght@400&display=block" rel="stylesheet">
<style>html,body{margin:0;background:transparent}
.w{width:1080px;height:1920px;display:flex;flex-direction:column;align-items:center;justify-content:center;color:#fff;text-shadow:0 2px 18px rgba(0,0,0,.35)}
canvas{width:300px;height:300px;filter:drop-shadow(0 4px 24px rgba(0,0,0,.35))}
.n{font:500 76px 'Bodoni Moda';letter-spacing:.18em;margin-top:48px;padding-left:.18em}
.l{width:90px;height:2px;background:#C9A45C;margin:34px 0}
.t{font:italic 400 58px 'Bodoni Moda';letter-spacing:.02em}</style></head>
<body><div class="w"><canvas id="c" width="600" height="600"></canvas>
<div class="n">URBAN NEST</div><div class="l"></div><div class="t">Just The Right Feel</div></div></body></html>`);
await t.evaluate(src => new Promise(res => { const i = new Image(); i.onload = () => {
  const c = document.getElementById('c'), x = c.getContext('2d');
  x.drawImage(i, 0, 0, 600, 600); const d = x.getImageData(0, 0, 600, 600);
  for (let p = 0; p < d.data.length; p += 4) { const a = 255 - (d.data[p] + d.data[p+1] + d.data[p+2]) / 3;
    d.data[p] = d.data[p+1] = d.data[p+2] = 255; d.data[p+3] = a; }
  x.putImageData(d, 0, 0); res(); }; i.src = src; }), logo);
await t.evaluate(() => document.fonts.ready);
await t.screenshot({ path: OUT, omitBackground: true });
await b.close(); console.log('ok', OUT);
