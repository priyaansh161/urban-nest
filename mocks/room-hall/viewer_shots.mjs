// The published hall in its own viewer (headed Edge, 1600x900): the opening view, then each view button.
//   node mocks/room-hall/viewer_shots.mjs   -> mocks/room-hall/check/view_*.png
import { createRequire } from 'module'; const require = createRequire(import.meta.url);
const { chromium } = require('../../tools/node_modules/playwright-core');
const b = await chromium.launch({ channel: 'msedge', headless: false, args: ['--window-position=-2400,0'] });
const p = await b.newPage({ viewport: { width: 1600, height: 900 } });
await p.goto('http://localhost:3000/rooms/hall/?t=' + Date.now()); await p.waitForTimeout(35000);
const D = 'mocks/room-hall/check/';
await p.screenshot({ path: D + 'view_wide.png' });
for (const v of ['overview', 'living', 'tv', 'dining', 'mandir']) {
  await p.click(`#bar [data-view="${v}"]`); await p.waitForTimeout(4000); await p.screenshot({ path: D + 'view_' + v + '.png' });
}
await b.close(); console.log('shots done');
