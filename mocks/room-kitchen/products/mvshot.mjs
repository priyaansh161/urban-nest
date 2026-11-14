// The model as the website shows it (model-viewer 3.5, default light, shadow 0.9), two angles, beside its listing photo.
//   node mocks/room-kitchen/products/mvshot.mjs <key>[:photo.webp|jpg] ...     (needs the site served on :3000)
// Writes mocks/room-kitchen/products/check/<key>_vs.png
import { createRequire } from 'module';
import { existsSync, readdirSync } from 'node:fs';
const require = createRequire(import.meta.url);
const { chromium } = require('../../../tools/node_modules/playwright-core');
const sharp = require('../../../tools/node_modules/sharp');
const D = 'mocks/room-kitchen/products/';
const ids = Object.fromEntries(require('fs').readFileSync(D + 'attach_map.txt', 'utf8').trim().split(/\n/).map(l => { const [k, id] = l.trim().split(' '); return [k, id.slice(0, 8)]; }));
const photoFor = (k, pick) => {
  if (pick) return D + pick;
  const a = D + 'amz/' + k + '/'; if (existsSync(a)) { const f = readdirSync(a).filter(x => /\.(jpe?g|webp|png)$/i.test(x) && x !== 'sheet.png').sort()[0]; if (f) return a + f; }
  return D + 'src/' + ids[k] + '/0.webp';
};
const browser = await chromium.launch({ channel: 'msedge', headless: false, args: ['--window-position=-2400,0'] });
const page = await browser.newPage({ viewport: { width: 900, height: 900 }, deviceScaleFactor: 1 });
for (const arg of process.argv.slice(2)) {
  const [k, pick] = arg.split(':');
  const glb = process.env.GLB_DIR ? `${process.env.GLB_DIR}/${k}.glb` : `${D}web/${k}.glb`;
  const shots = [];
  for (const orbit of ['30deg 70deg auto', '-50deg 45deg auto']) {
    await page.goto(`http://localhost:3000/${D}mv?o=${encodeURIComponent(orbit)}&src=${encodeURIComponent('/' + glb + '?t=' + Date.now())}`);
    await page.waitForFunction(() => window.__ok || window.__err, null, { timeout: 60000 });
    console.log(k, await page.evaluate(() => [window.__ok, window.__err, document.querySelector('model-viewer').src]));
    await page.waitForTimeout(2500);
    shots.push(await page.screenshot());
  }
  const photo = await sharp(photoFor(k, pick)).resize(900, 900, { fit: 'contain', background: '#fff' }).png().toBuffer();
  await sharp({ create: { width: 2700, height: 900, channels: 3, background: '#fff' } })
    .composite([{ input: photo, left: 0, top: 0 }, { input: shots[0], left: 900, top: 0 }, { input: shots[1], left: 1800, top: 0 }])
    .png().toFile(D + 'check/' + k + '_vs.png');
  console.log('shot', k);
}
await browser.close();
