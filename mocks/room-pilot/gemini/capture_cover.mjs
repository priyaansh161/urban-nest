// Clean renders of the published Quiet Bath (no header, buttons, dots or hint) for Gemini to turn into the
// Spaces tile photo. Needs the local server on :8123 serving the project root; Edge via playwright-core.
//   node mocks/room-pilot/gemini/capture_cover.mjs
import { createRequire } from 'node:module';
import { mkdirSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
const HERE = dirname(fileURLToPath(import.meta.url));
const require = createRequire(join(HERE, '../../../tools/package.json'));
const { chromium } = require('playwright-core');
const OUT = join(HERE, 'cover-kit'); mkdirSync(OUT, { recursive: true });
// [file, camera position, look-at] in the viewer's metres
const SHOTS = [
  ['1-room-wide.png', [0.0, 1.45, 1.6], [0.0, 1.15, -1.4]],
  ['2-room-angle.png', [1.35, 1.5, 1.25], [-0.8, 1.0, -1.2]],
];
const browser = await chromium.launch({ channel: 'msedge', headless: true, args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
try {
  const page = await browser.newPage({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: 1 });
  await page.goto('http://localhost:8123/rooms/quiet-bath/index.html?shot=1');
  await page.waitForFunction(() => window.__pilot && window.__pilot.placed.length >= 11, null, { timeout: 300000 });
  await page.waitForTimeout(4000);                                      // the second reflection capture
  for (const [file, pos, tgt] of SHOTS) {
    await page.evaluate(([p, t]) => { const P = window.__pilot; P.camera.position.set(...p); P.controls.target.set(...t); P.controls.update(); }, [pos, tgt]);
    await page.waitForTimeout(2500);
    await page.screenshot({ path: join(OUT, file) });
    console.log('SHOT', file);
  }
} finally { await browser.close(); }
