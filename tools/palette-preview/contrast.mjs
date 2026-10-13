/* Light-mode contrast sweep over every page (and the opened sheets).
   Reports text under 4.5:1 (3:1 at 24px+), with a CSS selector for each. */
import { chromium } from 'playwright-core';
import { readdirSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..', '..');
const theme = process.argv[2] || 'light';
const PAGES = readdirSync(ROOT).filter(f => f.endsWith('.html') && f !== 'offline.html').sort();
const browser = await chromium.launch({ channel: 'msedge', headless: true });

const OPENERS = {
  'collection.html': `(() => { const k = Object.keys(window.ITEMS||{}); if (k.length) openDetail(k[0]); })()`,
  'essentials.html': `(() => { const k = Object.keys(window.ITEMS||{}); if (k.length) openDetail(k[0]); })()`,
  'community.html':  `(() => { const k = Object.keys(window.nestPosts||{}); if (k.length) openNestArticle(k[0]); })()`,
};

let total = 0;
for (const page of PAGES) for (const vp of [{ width: 1440, height: 900 }, { width: 390, height: 844 }]) for (const opened of [false, true]) {
  if (opened && !OPENERS[page]) continue;
  const ctx = await browser.newContext({ viewport: vp, colorScheme: theme });
  const tab = await ctx.newPage();
  await tab.addInitScript(t => { try { localStorage.setItem('un-theme', t); } catch (e) {} }, theme);
  await tab.goto(`http://localhost:3000/${page}`, { waitUntil: 'load' }).catch(() => {});
  await tab.waitForLoadState('networkidle', { timeout: 8000 }).catch(() => {});
  await tab.addStyleTag({ content: '*,*::before,*::after{transition:none!important;animation:none!important}' }).catch(() => {});
  await tab.waitForTimeout(2200);
  if (opened) { await tab.evaluate(OPENERS[page]).catch(() => {}); await tab.waitForTimeout(1200); }
  const bad = await tab.evaluate(() => {
    const rgb = s => { const m = s.match(/[\d.]+/g).map(Number); return { r: m[0], g: m[1], b: m[2], a: m.length > 3 ? m[3] : 1 }; };
    const lum = c => { const q = v => { v /= 255; return v <= .03928 ? v / 12.92 : ((v + .055) / 1.055) ** 2.4; }; return .2126 * q(c.r) + .7152 * q(c.g) + .0722 * q(c.b); };
    const blend = (f, b) => ({ r: f.r * f.a + b.r * (1 - f.a), g: f.g * f.a + b.g * (1 - f.a), b: f.b * f.a + b.b * (1 - f.a), a: 1 });
    const ratio = (a, b) => { const x = lum(a), y = lum(b); return (Math.max(x, y) + .05) / (Math.min(x, y) + .05); };
    const sel = el => { const c = typeof el.className === 'string' && el.className.trim() ? '.' + el.className.trim().split(/\s+/)[0] : ''; const p = el.parentElement; const pc = p && typeof p.className === 'string' && p.className.trim() ? '.' + p.className.trim().split(/\s+/)[0] : (p ? p.tagName.toLowerCase() : ''); return (c ? '' : pc + ' ') + el.tagName.toLowerCase() + (el.id ? '#' + el.id : '') + c; };
    const out = [];
    for (const el of document.querySelectorAll('body *')) {
      if (![...el.childNodes].some(c => c.nodeType === 3 && c.textContent.trim())) continue;
      // text laid over a photograph or a 3D view has no single ground to measure against
      if (el.closest('figure, .sp, .ct-piece, header.hero, .band, .wband, .jband, .nband, .cat-tile-media, .room-media, .d-stage, #scene-wrap, #lobby, .lobby, .modal-hero, .na-media, #welcome')) continue;
      const cs = getComputedStyle(el), rc = el.getBoundingClientRect();
      if (!rc.width || !rc.height || cs.visibility === 'hidden' || +cs.opacity === 0) continue;
      let hidden = false, n = el; while (n) { const s = getComputedStyle(n); if (s.display === 'none' || +s.opacity === 0 || s.visibility === 'hidden') { hidden = true; break; } n = n.parentElement; }
      if (hidden) continue;
      const layers = []; let p = el;
      while (p) { const b = getComputedStyle(p).backgroundColor; if (!/, 0\)$/.test(b) && b !== 'transparent') { const c = rgb(b); layers.push(c); if (c.a === 1) break; } p = p.parentElement; }
      let bg = { r: 255, g: 255, b: 255, a: 1 }; for (let i = layers.length - 1; i >= 0; i--) bg = blend(layers[i], bg);
      const r = ratio(blend(rgb(cs.color), bg), bg), px = parseFloat(cs.fontSize), bold = +cs.fontWeight >= 700;
      const need = (px >= 24 || (px >= 18.66 && bold)) ? 3 : 4.5;
      if (r < need) out.push(`${r.toFixed(2)} <${need}  ${px}px  ${sel(el)}  "${el.textContent.trim().replace(/\s+/g, ' ').slice(0, 30)}"  fg ${cs.color} on rgb(${Math.round(bg.r)},${Math.round(bg.g)},${Math.round(bg.b)})`);
    }
    return [...new Set(out)];
  }).catch(e => ['error ' + e]);
  total += bad.length;
  if (bad.length) { console.log(`\n== ${page} @${vp.width}${opened ? ' (opened)' : ''}`); bad.forEach(b => console.log('   ' + b)); }
  await ctx.close();
}
await browser.close();
console.log(`\n${theme}: ${total} failing text element(s)`);
