import { createRequire } from 'module';
const require = createRequire(import.meta.url);
const { chromium } = require('../../tools/node_modules/playwright-core');
const b = await chromium.launch({ channel: 'msedge', headless: false, args: ['--window-position=-2400,0'] });
for (const [tag, w, h] of [['land', 844, 390], ['port', 390, 844]]) {
  const ctx = await b.newContext({ viewport: { width: w, height: h }, deviceScaleFactor: 2, isMobile: true, hasTouch: true });
  const p = await ctx.newPage(); await p.goto('http://localhost:3000/rooms/living-room/'); await p.waitForFunction(() => window.__roomReady, null, { timeout: 180000 }); await p.waitForTimeout(6000);
  await p.screenshot({ path: `mocks/room-living/renders/phone_${tag}_wide.png` });
  await p.evaluate(() => window.__pilot.placed[2].dot.click()); await p.waitForTimeout(3500);
  await p.screenshot({ path: `mocks/room-living/renders/phone_${tag}_card.png` });
  await ctx.close();
}
await b.close();
