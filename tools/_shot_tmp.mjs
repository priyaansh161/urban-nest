import { chromium } from 'playwright-core';
import { pathToFileURL } from 'node:url';
const b = await chromium.launch({ channel: 'msedge' });
const pg = await b.newPage({ viewport: { width: 1270, height: +(process.argv[4] || 560) } });
await pg.goto(pathToFileURL(process.argv[2]).href);
await pg.waitForTimeout(500);
await pg.screenshot({ path: process.argv[3], fullPage: true });
await b.close();
