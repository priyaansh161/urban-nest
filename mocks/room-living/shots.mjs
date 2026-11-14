// Full-HD captures of the living-room viewer, straight from the page (no pane scaling or re-compression).
//   node mocks/room-living/shots.mjs [tag] [target ...]     needs a static server from the project root on :3000 (npx serve)
// target: a view name (wide, overview, sofa ...) or "p:<n>" = click product n's dot (its fixed viewpoint + card).
// With no target: every view and every product. Also reports, per product, whether the camera ends inside a mesh.
import { createRequire } from 'module';
import { mkdirSync } from 'node:fs';
const require = createRequire(import.meta.url);
const { chromium } = require('../../tools/node_modules/playwright-core');
const [tag = 'now', ...targets] = process.argv.slice(2);
const ROOM = process.env.ROOM || 'mocks/room-living/viewer.html';
mkdirSync('mocks/room-living/renders', { recursive: true });
const browser = await chromium.launch({ channel: 'msedge', headless: false, args: ['--window-position=-2400,0'] });
const page = await browser.newPage({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: 1 });
await page.goto('http://localhost:3000/' + ROOM + '?dev=1');
await page.waitForFunction(() => window.__roomReady, null, { timeout: 180000 });
await page.waitForTimeout(8000);
const info = await page.evaluate(() => ({ views: [...document.querySelectorAll('#bar [data-view]')].map(b => b.dataset.view), n: window.__pilot.placed.length, names: window.__pilot.placed.map(p => p.def.name) }));
const list = targets.length ? targets : [...info.views, ...info.names.map((_, i) => 'p:' + i)];
for (const t of list) {
  let label = t;
  if (t.startsWith('p:')) {
    const i = +t.slice(2);
    await page.evaluate((i) => { const p = window.__pilot.placed[i]; p.dot.click(); }, i);
    label = 'prod' + String(i).padStart(2, '0') + '_' + info.names[i].replace(/[^a-z0-9]+/gi, '-').toLowerCase();
    await page.waitForTimeout(3500);
  } else {
    await page.evaluate((v) => window.__pilot.setView(v, true), t);
    await page.waitForTimeout(1500);
  }
  const probe = await page.evaluate(() => {
    const { camera } = window.__pilot; return [camera.position.x, camera.position.y, camera.position.z].map(v => +v.toFixed(2));
  });
  await page.screenshot({ path: `mocks/room-living/renders/${tag}_${label}.png` });
  console.log('shot', label, 'camera', probe.join(','));
}
await browser.close();
