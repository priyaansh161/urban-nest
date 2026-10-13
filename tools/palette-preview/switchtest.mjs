import { chromium } from 'playwright-core';
const PAGES = ['about','bathroom','bedroom','checkout','collection','community','essentials','index','join','kitchen','policies','spaces'];
const browser = await chromium.launch({ channel: 'msedge', headless: true });
const state = tab => tab.evaluate(() => ({
  attr: document.documentElement.getAttribute('data-theme'),
  sun: document.getElementById('themeLight').getAttribute('aria-pressed'),
  moon: document.getElementById('themeDark').getAttribute('aria-pressed'),
  stored: (() => { try { return localStorage.getItem('un-theme'); } catch (e) { return 'x'; } })(),
  ground: getComputedStyle(document.body).backgroundColor,
}));
const fmt = s => `sun:${s.sun === 'true' ? 'ON ' : 'off'} moon:${s.moon === 'true' ? 'ON ' : 'off'} attr:${s.attr || '-'} saved:${s.stored || '-'}`;
let fails = 0;
const expect = (label, s, sun, moon) => { const ok = (s.sun === String(sun)) && (s.moon === String(moon)); if (!ok) fails++; return (ok ? '  ok  ' : ' FAIL ') + label.padEnd(26) + fmt(s); };
for (const p of PAGES) {
  const out = [];
  for (const scheme of ['dark', 'light']) {
    const ctx = await browser.newContext({ viewport: { width: 1280, height: 800 }, colorScheme: scheme });
    const tab = await ctx.newPage();
    const errs = []; tab.on('pageerror', e => errs.push(e.message));
    await tab.goto(`http://localhost:3000/${p}.html`, { waitUntil: 'load' }).catch(() => {});
    await tab.waitForTimeout(700);
    out.push(expect(`first visit, phone ${scheme}`, await state(tab), scheme === 'light', scheme === 'dark'));
    if (scheme === 'dark') {
      await tab.emulateMedia({ colorScheme: 'light' }); await tab.waitForTimeout(250);
      out.push(expect('phone flips to light', await state(tab), true, false));
      await tab.emulateMedia({ colorScheme: 'dark' }); await tab.waitForTimeout(250);
      await tab.evaluate(() => document.getElementById('themeLight').click()); await tab.waitForTimeout(250);
      out.push(expect('taps sun', await state(tab), true, false));
      await tab.evaluate(() => document.getElementById('themeLight').click()); await tab.waitForTimeout(250);
      out.push(expect('taps sun again', await state(tab), true, false));
      await tab.emulateMedia({ colorScheme: 'dark' }); await tab.waitForTimeout(250);
      out.push(expect('choice beats the phone', await state(tab), true, false));
      await tab.reload({ waitUntil: 'load' }); await tab.waitForTimeout(700);
      out.push(expect('reload keeps choice', await state(tab), true, false));
      await tab.evaluate(() => document.getElementById('themeDark').click()); await tab.waitForTimeout(250);
      out.push(expect('taps moon', await state(tab), false, true));
    }
    if (errs.length) { fails++; out.push(' FAIL  script error: ' + errs.join(' | ').slice(0, 160)); }
    await ctx.close();
  }
  console.log('\n' + p); out.forEach(l => console.log(l));
}
await browser.close();
console.log(fails ? `\n${fails} FAILURE(S)` : '\nall checks passed on all pages');
