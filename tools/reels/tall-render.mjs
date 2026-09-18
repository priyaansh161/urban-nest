/* Square product render -> 1080x1920 white frame, product centred, for Flow first frames. */
import { chromium } from 'playwright-core';
import { readFileSync } from 'node:fs';
const [,, inPath, outPath] = process.argv;
const src = 'data:image/png;base64,' + readFileSync(inPath).toString('base64');
const b = await chromium.launch({ channel: 'msedge', headless: true });
const t = await b.newPage({ viewport: { width: 1080, height: 1920 } });
await t.setContent(`<body style="margin:0;background:#fff"><div style="width:1080px;height:1920px;display:flex;align-items:center;justify-content:center"><img src="${src}" style="width:1060px"></div>`);
await t.waitForTimeout(300); await t.screenshot({ path: outPath }); await b.close(); console.log('ok');
