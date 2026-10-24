// Captures the Gemini placement assets:
//   1. a 3D render of each Bathroom MK2 product (its Spline scene, screenshotted)
//   2. a clean wide shot of the pilot bathroom (viewer.html?shot=1)
// Needs the local server on :8123 serving the project root. Uses Edge via playwright-core (as tools/list-product.mjs does).
//   node mocks/room-pilot/gemini/capture.mjs
import { createRequire } from 'node:module';
import { mkdirSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
const HERE = dirname(fileURLToPath(import.meta.url));
const require = createRequire(join(HERE, '../../../tools/package.json'));
const { chromium } = require('playwright-core');
const BASE = 'http://localhost:8123/mocks/room-pilot/';
const PRODUCTS = [
  ['01-bathroom-sliders', 'https://prod.spline.design/7Z0hJBfSZSiFmQDK/scene.splinecode'],
  ['02-toilet-paper-holder', 'https://prod.spline.design/ELaAQUQC0ix9C-E5/scene.splinecode'],
  ['03-bathroom-accessories-set', 'https://prod.spline.design/VpF6FZ0xP0PIVZrN/scene.splinecode'],
  ['04-towel-hanger', 'https://prod.spline.design/3XkbfxtHwtfQqFgX/scene.splinecode'],
  ['05-shower-mat', 'https://prod.spline.design/Kd5VWDfAkygLopbm/scene.splinecode'],
  ['06-scented-candles', 'https://prod.spline.design/oxomoxAJqi20U0Zo/scene.splinecode'],
  ['07-toilet-mat', 'https://prod.spline.design/ndfMSNCL1A3f8F2c/scene.splinecode'],
  ['08-toilet-cleaning-brush', 'https://prod.spline.design/8f9ZwJEdpz4ts8G5/scene.splinecode'],
  ['09-vanity-mat', 'https://prod.spline.design/Y01WtpjiANZObKCa/scene.splinecode'],
  ['10-towel-rack', 'https://prod.spline.design/VxIDVT0fVxI8GDjM/scene.splinecode'],
  ['11-wall-shelf-organiser', 'https://prod.spline.design/ysDrMhUaSRiCHfL4/scene.splinecode'],
  ['12-elpheco-dustbin', 'https://prod.spline.design/HTEKmAHQMcmQjuva/scene.splinecode'],
  ['13-wall-soap-dispenser', 'https://prod.spline.design/GE3hQHDF7hiCR66v/scene.splinecode'],
];
const only = process.argv[2];
const out = join(HERE, 'products'); mkdirSync(out, { recursive: true });
const browser = await chromium.launch({ channel: 'msedge', headless: true, args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
try {
  if (!only || only === 'products') {
    const page = await browser.newPage({ viewport: { width: 900, height: 900 } });
    for (const [name, url] of PRODUCTS) {
      await page.goto(BASE + 'gemini/spline-shot.html?url=' + encodeURIComponent(url));
      try { await page.waitForFunction(() => { const v = document.querySelector('spline-viewer'); return v && v.shadowRoot && v.shadowRoot.querySelector('canvas'); }, null, { timeout: 45000 }); } catch {}
      await page.waitForTimeout(6000);                          // let the scene finish drawing
      await page.screenshot({ path: join(out, name + '.png') });
      console.log('PRODUCT', name);
    }
    await page.close();
  }
  if (!only || only === 'room') {
    const page = await browser.newPage({ viewport: { width: 1920, height: 1080 } });
    await page.goto(BASE + 'viewer.html?shot=1&bare=1');
    await page.waitForFunction(() => window.__pilot && window.__pilot.placed.length >= 2, null, { timeout: 120000 });
    await page.waitForTimeout(4000);
    await page.screenshot({ path: join(HERE, '00-room-wide.png') });
    console.log('ROOM saved');
  }
} finally { await browser.close(); }
