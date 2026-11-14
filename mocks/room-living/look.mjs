import { createRequire } from 'module';
const require = createRequire(import.meta.url);
const { chromium } = require('../../tools/node_modules/playwright-core'); const sharp = require('../../tools/node_modules/sharp');
const shots = { oldsideboard: [[-0.2, 1.3, 0.8], [-1.3, 0.3, -2.0]], painting: [[-0.55, 1.55, -1.43], [1.75, 1.9, 2.08]], ceiling: [[0.0, 1.5, 1.2], [0.0, 2.95, -1.6]], corner: [[0.4, 1.6, 0.3], [2.3, 0.3, -1.9]] };
const b = await chromium.launch({ channel: 'msedge', headless: false, args: ['--window-position=-2400,0'] });
const p = await b.newPage({ viewport: { width: 1920, height: 1080 } }); await p.goto('http://localhost:3000/rooms/living-room/?dev=1');
await p.waitForFunction(() => window.__roomReady, null, { timeout: 120000 }); await p.waitForTimeout(8000);
await p.addStyleTag({ content: '#bar,#hint,header,#stats,#dots{display:none!important}' });
const out = [];
for (const [k, [pos, tgt]] of Object.entries(shots)) {
  await p.evaluate(([pos, tgt]) => { const { camera, controls } = window.__pilot; camera.position.set(...pos); controls.target.set(...tgt); controls.update(); }, [pos, tgt]); await p.waitForTimeout(1200);
  const f = `mocks/room-living/renders/look_${k}.png`; await p.screenshot({ path: f }); out.push(f);
}
await sharp({ create: { width: 1920, height: 1080, channels: 3, background: '#000' } }).composite(out.map((f, i) => ({ input: f, left: 0, top: 0 }))).toFile('x.png').catch(() => {});
for (const f of out) await sharp(f).resize(960, 540).toFile(f.replace('.png', '_s.png'));
await sharp({ create: { width: 1920, height: 1080, channels: 3, background: '#000' } }).composite(out.map((f, i) => ({ input: f.replace('.png', '_s.png'), left: (i % 2) * 960, top: Math.floor(i / 2) * 540 }))).jpeg({ quality: 85 }).toFile('mocks/room-living/renders/look_sheet.jpg');
await b.close(); console.log('ok');
