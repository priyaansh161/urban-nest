// Clean renders of the published Sunday Bedroom (no header, buttons, dots or hint) for Gemini to turn into the
// Spaces tile photo, as mocks/room-pilot/gemini/capture_cover.mjs did for the Quiet Bath. Needs the local server
// on :8123 serving the project root; Edge via playwright-core.
//   node mocks/room-bedroom/gemini/capture_cover.mjs
import { createRequire } from 'node:module';
import { mkdirSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
const HERE = dirname(fileURLToPath(import.meta.url));
const require = createRequire(join(HERE, '../../../tools/package.json'));
const { chromium } = require('playwright-core');
const OUT = join(HERE, 'cover-kit'); mkdirSync(OUT, { recursive: true });
// [file, camera position, look-at] in the viewer's metres (back wall z = -1.9, door wall z = +1.9)
const SHOTS = [
  ['1-room-wide.png', [0.0, 1.45, 1.75], [0.0, 1.05, -1.9]],
  ['2-room-window.png', [1.55, 1.5, 1.65], [-0.8, 0.95, -0.9]],
  ['3-room-dresser.png', [-1.55, 1.5, 1.65], [0.8, 0.95, -0.9]],
  ['4-room-overview.png', [1.85, 2.55, 1.7], [-0.5, 1.3, -0.8]],   // the viewer's Overview, his pick (26 Oct)
  ['5-overview-dresser.png', [-1.85, 2.55, 1.7], [0.6, 1.3, -0.8]],   // the same, from the window-side corner: the dresser and its canvas in view
  ['6-overview-dresser-wide.png', [-1.85, 2.55, 1.7], [1.0, 1.2, -0.4]],
  ['7-overview-centre.png', [-0.4, 2.3, 1.78], [0.3, 1.4, -1.0]],   // from the middle of the door wall: window left, dresser right
];
const browser = await chromium.launch({ channel: 'msedge', headless: true, args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
try {
  const page = await browser.newPage({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: 1 });
  await page.goto('http://localhost:8123/rooms/sunday-bedroom/index.html?shot=1');
  await page.waitForFunction(() => window.__pilot && window.__pilot.placed.length >= 12, null, { timeout: 300000 });
  await page.waitForTimeout(4000);                                      // the second reflection capture
  for (const [file, pos, tgt] of SHOTS) {
    await page.evaluate(([p, t]) => { const P = window.__pilot; P.camera.position.set(...p); P.controls.target.set(...t); P.controls.update(); }, [pos, tgt]);
    await page.waitForTimeout(2500);
    await page.screenshot({ path: join(OUT, file), timeout: 180000 });   // software rendering at 1080p is slow
    console.log('SHOT', file);
  }
} finally { await browser.close(); }
