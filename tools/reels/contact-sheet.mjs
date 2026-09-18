/* One-image contact sheet of a folder of renders, to check them at a glance. */
import { chromium } from 'playwright-core';
import { readFileSync, readdirSync } from 'node:fs';
const [,, dir, out] = process.argv;
const files = readdirSync(dir).filter(f => f.endsWith('.png')).sort();
const imgs = files.map(f => `<figure><img src="data:image/png;base64,${readFileSync(dir + '/' + f).toString('base64')}"><figcaption>${f}</figcaption></figure>`).join('');
const b = await chromium.launch({ channel: 'msedge', headless: true });
const t = await b.newPage({ viewport: { width: 1600, height: 900 } });
await t.setContent(`<body style="margin:0;display:flex;flex-wrap:wrap;font:14px sans-serif;background:#ddd">${imgs}<style>figure{margin:4px;width:388px;background:#fff}img{width:388px;display:block}</style>`);
await t.waitForTimeout(300); await t.screenshot({ path: out, fullPage: true }); await b.close();
