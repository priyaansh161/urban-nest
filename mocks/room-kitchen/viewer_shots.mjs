// The published kitchen in its own viewer (headed Edge, 1600x900): the opening view, then each view button, then two close-ups.
//   node mocks/room-kitchen/viewer_shots.mjs   -> mocks/room-kitchen/check/view_*.png
import { createRequire } from 'module'; const require = createRequire(import.meta.url);
const { chromium } = require('../../tools/node_modules/playwright-core');
const b = await chromium.launch({ channel: 'msedge', headless: false, args: ['--window-position=-2400,0'] });
const p = await b.newPage({ viewport: { width: 1600, height: 900 } });
await p.goto('http://localhost:3000/rooms/kitchen/?t=' + Date.now()); await p.waitForTimeout(30000);
const D = 'mocks/room-kitchen/check/';
await p.screenshot({ path: D + 'view_wide.png' });
for (const v of ['overview', 'hob', 'sink', 'prep', 'ovens']) {
  await p.click(`#bar [data-view="${v}"]`); await p.waitForTimeout(4000); await p.screenshot({ path: D + 'view_' + v + '.png' });
}
await p.evaluate(() => { const c = window.__cam || null; });
await b.close(); console.log('shots done');
