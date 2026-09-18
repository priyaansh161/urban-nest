/* Renders Collection 3D models to clean square images on white, as reference
   photos for Gemini.
     node reels/render-pieces.mjs <models.json> <outDir> [orbitDeg]
   models.json = { "1-piece-name": "<model_url>", ... }. orbitDeg turns the
   camera (0 = front; ~25–55 shows animals and sculptures side-on). */
import { chromium } from 'playwright-core';
import { readFileSync, mkdirSync } from 'node:fs';

const [,, modelsPath, outDir, orbit = '0'] = process.argv;
const models = JSON.parse(readFileSync(modelsPath, 'utf8'));
const OUT = outDir.replace(/\/g, '/').replace(/\/?$/, '/');
mkdirSync(OUT, { recursive: true });
const browser = await chromium.launch({ channel: 'msedge', headless: true, args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
const tab = await browser.newPage({ viewport: { width: 1200, height: 1200 }, deviceScaleFactor: 1 });

for (const [name, url] of Object.entries(models)) {
  const html = `<!doctype html><html><head>
    <script type="module" src="https://unpkg.com/@google/model-viewer@3.5.0/dist/model-viewer.min.js"></script>
    <style>html,body{margin:0;background:#fff}model-viewer{width:1200px;height:1200px;background:#fff;--poster-color:#fff}</style>
  </head><body>
    <model-viewer id="mv" src="${url}" camera-orbit="${orbit}deg 78deg auto" field-of-view="26deg"
      shadow-intensity="0.8" shadow-softness="1" exposure="1.05" environment-image="neutral" interaction-prompt="none"></model-viewer>
  </body></html>`;
  await tab.setContent(html, { waitUntil: 'domcontentloaded' });
  const ok = await tab.evaluate(() => new Promise(res => {
    const mv = document.getElementById('mv');
    mv.addEventListener('load', () => setTimeout(() => res(true), 2500));
    mv.addEventListener('error', () => res(false));
    setTimeout(() => res(false), 60000);
  }));
  if (!ok) { console.log('  FAILED ' + name); continue; }
  await tab.locator('#mv').screenshot({ path: OUT + name + '.png' });
  console.log('  rendered ' + name);
}
await browser.close();
