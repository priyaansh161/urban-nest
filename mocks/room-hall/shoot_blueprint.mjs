// Saves the hall blueprint's two cards as PNGs (check/blueprint_plan.png, check/blueprint_model.png). Needs the site on :3000.
//   node mocks/room-hall/shoot_blueprint.mjs
import { createRequire } from 'module';
import { mkdirSync } from 'node:fs';
const require = createRequire(import.meta.url);
const { chromium } = require('../../tools/node_modules/playwright-core');
mkdirSync('mocks/room-hall/check', { recursive: true });
const b = await chromium.launch({ channel: 'msedge', headless: true });
const p = await b.newPage({ viewport: { width: 1500, height: 1000 }, deviceScaleFactor: 2 });
await p.goto('http://localhost:3000/mocks/room-hall/blueprint?t=' + Date.now()); await p.waitForTimeout(2500);
const cards = await p.$$('.card');
await cards[0].screenshot({ path: 'mocks/room-hall/check/blueprint_plan.png' });
await cards[1].screenshot({ path: 'mocks/room-hall/check/blueprint_model.png' });
await b.close(); console.log('shot');
