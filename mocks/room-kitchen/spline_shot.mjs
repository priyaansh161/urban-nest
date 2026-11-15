// Screenshots the old Spline kitchens (MK1, MK2) for composition reference.  node mocks/room-kitchen/spline_shot.mjs
import { createRequire } from 'module'; const require = createRequire(import.meta.url);
const { chromium } = require('../../tools/node_modules/playwright-core');
const b = await chromium.launch({ channel: 'msedge', headless: false, args: ['--window-position=-2400,0'] });
const p = await b.newPage({ viewport: { width: 1400, height: 900 } });
for (const mk of ['1', '2']) {
  await p.goto('http://localhost:3000/mocks/room-kitchen/spline_old?mk=' + mk); await p.waitForTimeout(25000);
  await p.screenshot({ path: `mocks/room-kitchen/check/spline_mk${mk}.png` });
  for (const [k, dx] of [['l', -350], ['r', 350]]) {               // drag to turn the camera a little each way
    await p.mouse.move(700, 450); await p.mouse.down(); await p.mouse.move(700 + dx, 450, { steps: 20 }); await p.mouse.up(); await p.waitForTimeout(2500);
    await p.screenshot({ path: `mocks/room-kitchen/check/spline_mk${mk}_${k}.png` });
  }
}
await b.close(); console.log('done');
