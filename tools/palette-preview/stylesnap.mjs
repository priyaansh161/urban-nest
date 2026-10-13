/* Records the computed colours of every element on every public page in one
   theme, so a change can be proven not to touch it.
     node tools/palette-preview/stylesnap.mjs dark before
     node tools/palette-preview/stylesnap.mjs dark after     → compares with "before"
   Needs the local server on :3000. */
import { chromium } from 'playwright-core';
import { readdirSync, writeFileSync, readFileSync, existsSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const HERE = dirname(fileURLToPath(import.meta.url));
const ROOT = join(HERE, '..', '..');
const [theme = 'dark', label = 'before'] = process.argv.slice(2);
const PAGES = readdirSync(ROOT).filter(f => f.endsWith('.html')).sort();
const browser = await chromium.launch({ channel: 'msedge', headless: true });
const result = {};

for (const page of PAGES) for (const vp of [{ width: 1440, height: 900 }, { width: 390, height: 844 }]) {
  const ctx = await browser.newContext({ viewport: vp, colorScheme: theme });
  const tab = await ctx.newPage();
  await tab.addInitScript(t => { try { localStorage.setItem('un-theme', t); } catch (e) {} Math.random = () => 0.42; }, theme);
  await tab.goto(`http://localhost:3000/${page}`, { waitUntil: 'load', timeout: 45000 }).catch(() => {});
  await tab.waitForLoadState('networkidle', { timeout: 10000 }).catch(() => {});
  await tab.addStyleTag({ content: '*,*::before,*::after{transition:none!important;animation:none!important}' }).catch(() => {});
  await tab.waitForTimeout(2500);
  const snap = await tab.evaluate(() => {
    const PROPS = ['color', 'backgroundColor', 'backgroundImage', 'borderTopColor', 'borderRightColor', 'borderBottomColor', 'borderLeftColor', 'boxShadow', 'outlineColor', 'fill', 'stroke', 'textDecorationColor', 'caretColor', 'opacity', 'filter'];
    const key = el => { const p = []; let n = el; while (n && n !== document.documentElement) { let i = 0, s = n; while ((s = s.previousElementSibling)) i++; p.unshift(n.tagName + i + (n.id ? '#' + n.id : '')); n = n.parentElement; } return p.join('>'); };
    const out = {};
    const all = [document.documentElement, ...document.querySelectorAll('body, body *')];
    for (const el of all) {
      if (el.closest('spline-viewer, model-viewer, canvas, svg defs')) continue;
      const cs = getComputedStyle(el), b = getComputedStyle(el, '::before'), a = getComputedStyle(el, '::after');
      out[key(el)] = PROPS.map(p => cs[p]).join('|') + ' ::before ' + b.backgroundColor + b.backgroundImage + b.color + ' ::after ' + a.backgroundColor + a.backgroundImage + a.color;
    }
    return out;
  }).catch(e => ({ __error: String(e) }));
  result[`${page} @${vp.width}`] = snap;
  await ctx.close();
  process.stdout.write('.');
}
await browser.close();

const file = join(HERE, `stylesnap-${theme}-${label}.json`);
writeFileSync(file, JSON.stringify(result));
console.log(`\nsaved ${file}`);

if (label !== 'before') {
  const before = JSON.parse(readFileSync(join(HERE, `stylesnap-${theme}-before.json`), 'utf8'));
  let total = 0;
  for (const k of Object.keys(result)) {
    const A = before[k] || {}, B = result[k];
    const common = Object.keys(B).filter(x => x in A);
    const changed = common.filter(x => A[x] !== B[x]);
    total += changed.length;
    console.log(`${k.padEnd(24)} ${String(common.length).padStart(5)} elements compared   ${changed.length ? changed.length + ' CHANGED  e.g. ' + changed.slice(0, 2).map(c => c.split('>').slice(-2).join('>')).join(' , ') : 'identical'}`);
  }
  console.log(total ? `\n${total} element(s) differ in ${theme} mode` : `\n${theme} mode: every compared element identical`);
}
