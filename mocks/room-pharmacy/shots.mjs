// Full-HD captures of the dispensary viewer, straight from the page (no pane scaling or re-compression).
//   node shots.mjs [tag] [view ...]     needs the local server (npx serve) on :3000
// Edge with a real window: headless Edge does not always get the GPU, and the room is WebGL.
import { createRequire } from 'module';
const require = createRequire(import.meta.url);
const { chromium } = require('../../tools/node_modules/playwright-core');

const [tag = 'now', ...views] = process.argv.slice(2);
const list = views.length ? views : ['vials', 'labels', 'blisters', 'machine'];
const browser = await chromium.launch({ channel: 'msedge', headless: false, args: ['--window-position=-2400,0'] });
const page = await browser.newPage({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: 1 });
await page.goto('http://localhost:3000/mocks/room-pharmacy/viewer?shot=1' + (process.env.TM ? '&tm=' + process.env.TM : ''));
await page.waitForFunction(() => window.__pilot, null, { timeout: 90000 });
await page.waitForTimeout(6000);                                  // textures and the environment map settle
for (const v of list) {
  await page.evaluate((v) => window.__pilot.setView(v, true), v);
  await page.waitForTimeout(2500);
  await page.screenshot({ path: `renders/${tag}_${v}.png` });
  console.log('shot', v);
}
await browser.close();
