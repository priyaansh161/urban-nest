// Any model beside any photo, as the website shows it (model-viewer, two angles): mvshot.mjs without the kitchen's key map.
//   node mocks/sofas/vs.mjs <model.glb> <photo.jpg> <out.png> [...repeat]      (needs the site served on :3000)
import { createRequire } from 'module';
const require = createRequire(import.meta.url);
const { chromium } = require('../../tools/node_modules/playwright-core');
const sharp = require('../../tools/node_modules/sharp');
const a = process.argv.slice(2);
const browser = await chromium.launch({ channel: 'msedge', headless: false, args: ['--window-position=-2400,0'] });
const page = await browser.newPage({ viewport: { width: 900, height: 900 }, deviceScaleFactor: 1 });
for (let i = 0; i < a.length; i += 3) {
  const [glb, photoF, out] = a.slice(i, i + 3), shots = [];
  for (const orbit of ['30deg 70deg auto', '-50deg 70deg auto']) {
    await page.goto(`http://localhost:3000/mocks/room-kitchen/products/mv?o=${encodeURIComponent(orbit)}&src=${encodeURIComponent('/' + glb + '?t=' + Date.now())}`);
    await page.waitForFunction(() => window.__ok || window.__err, null, { timeout: 60000 });
    await page.waitForTimeout(2500);
    shots.push(await page.screenshot());
  }
  const photo = await sharp(photoF).resize(900, 900, { fit: 'contain', background: '#fff' }).png().toBuffer();
  await sharp({ create: { width: 2700, height: 900, channels: 3, background: '#fff' } })
    .composite([{ input: photo, left: 0, top: 0 }, { input: shots[0], left: 900, top: 0 }, { input: shots[1], left: 1800, top: 0 }])
    .png().toFile(out);
  console.log('shot', out);
}
await browser.close();
