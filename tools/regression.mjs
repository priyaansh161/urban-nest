/* Regression check: "did my change break anything I did not touch?"
 *
 *     node tools/regression.mjs --baseline     BEFORE you start a change
 *     node tools/regression.mjs                AFTER it, before you deploy
 *
 * The first photographs every public page, at laptop and phone size, as it
 * is right now. The second photographs them again, compares pixel by pixel,
 * and writes tools/regression/report.html: which pages changed, where on the
 * page, and before / after / difference side by side.
 *
 * READING THE RESULT: the page you edited SHOULD show up as changed. Any
 * other page showing up is exactly what this exists to catch. It also lists
 * script errors and missing files that were not there in the baseline, and
 * runs tools/check-pages.mjs first.
 *
 * WHY BEFORE-AND-AFTER rather than one stored "golden" set: products, prices
 * and Nest articles come from Supabase and change whenever the admin is
 * used. The baseline RECORDS every Supabase answer, photos included, and the
 * check REPLAYS that recording, so both runs see identical data and a
 * difference means the code changed, not the catalogue. Take a fresh
 * baseline for every change, so the recording matches today's database.
 *
 * 3D views (the room scenes, every canvas, video and iframe) are painted
 * over in magenta and room dots are hidden: they never render the same
 * frame twice. The admin is not covered — it sits behind a login.
 *
 * Needs Microsoft Edge (already on Windows) and playwright-core, which is in
 * tools/package.json. It serves the project folder itself, so no server has
 * to be running.
 */
import { chromium } from 'playwright-core';
import sharp from 'sharp';
import http from 'node:http';
import { readFile, writeFile, mkdir, rm } from 'node:fs/promises';
import { existsSync, readdirSync } from 'node:fs';
import { spawnSync } from 'node:child_process';
import { dirname, extname, join, normalize } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');
const OUT = join(ROOT, 'tools', 'regression');
const BASE = join(OUT, 'baseline'), NOW = join(OUT, 'latest'), DIFF = join(OUT, 'diff');
const BASELINE = process.argv.includes('--baseline');

const PAGES = readdirSync(ROOT).filter(f => f.endsWith('.html')).sort();
const VIEWPORTS = {
  desktop: { viewport: { width: 1280, height: 800 } },
  phone:   { viewport: { width: 390, height: 844 }, isMobile: true, hasTouch: true },
};
const JOBS = PAGES.flatMap(page => Object.keys(VIEWPORTS).map(vp =>
  ({ page, vp, name: `${page.replace(/\.html$/, '')}-${vp}` })));

/* A pixel counts as changed past this much total RGB difference, and a page
   only counts as changed past MIN_PIXELS of them — below both is font
   anti-aliasing, not a change anyone could see. */
const PIXEL_THRESHOLD = 60;
const MIN_PIXELS = 100;

if (!BASELINE && !existsSync(join(BASE, 'problems.json'))) {
  console.log('\n  No baseline yet. Run this first, BEFORE making the change:\n\n    node tools/regression.mjs --baseline\n');
  process.exit(1);
}

let markupOk = true;
if (!BASELINE) {
  console.log('\n  1. Markup (tools/check-pages.mjs)\n');
  markupOk = spawnSync(process.execPath, [join(ROOT, 'tools', 'check-pages.mjs')], { stdio: 'inherit' }).status === 0;
}

for (const d of BASELINE ? [BASE, NOW, DIFF] : [NOW, DIFF]) await rm(d, { recursive: true, force: true });
await mkdir(BASELINE ? BASE : NOW, { recursive: true });
await mkdir(DIFF, { recursive: true });

// ── A throwaway static server over the project folder ──
const TYPES = {
  '.html': 'text/html; charset=utf-8', '.js': 'text/javascript', '.css': 'text/css',
  '.png': 'image/png', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.webp': 'image/webp',
  '.svg': 'image/svg+xml', '.json': 'application/json', '.webmanifest': 'application/manifest+json',
  '.glb': 'model/gltf-binary', '.splinecode': 'application/octet-stream',
};
const server = http.createServer(async (req, res) => {
  let path = decodeURIComponent(new URL(req.url, 'http://x').pathname);
  if (path.endsWith('/')) path += 'index.html';
  const file = join(ROOT, normalize(path));
  if (!file.startsWith(ROOT)) { res.writeHead(403).end(); return; }
  try {
    const body = await readFile(file);
    res.writeHead(200, { 'Content-Type': TYPES[extname(file).toLowerCase()] || 'application/octet-stream' });
    res.end(body);
  } catch { res.writeHead(404).end('not found'); }
});
/* A FIXED port, not a random one: the recorded Supabase answers carry
   "Access-Control-Allow-Origin: <this exact address>", so replaying them to
   a page on a different port gets them blocked by the browser. */
const PORT = 4178;
await new Promise((resolve, reject) => {
  server.once('error', e => reject(e.code === 'EADDRINUSE'
    ? new Error(`Port ${PORT} is busy — is another regression check still running?`) : e));
  server.listen(PORT, '127.0.0.1', resolve);
});
const ORIGIN = `http://127.0.0.1:${server.address().port}`;

const browser = await chromium.launch({ channel: 'msedge', headless: true });

async function shoot({ page, vp, name }) {
  const ctx = await browser.newContext({ ...VIEWPORTS[vp], serviceWorkers: 'block', reducedMotion: 'reduce' });
  // Every Supabase answer (products, articles, their photos) is recorded
  // during the baseline and replayed during the check, so both runs see
  // byte-identical data and neither waits on the network for it.
  const har = join(BASE, `${name}.har`);
  if (BASELINE || existsSync(har)) {
    await ctx.routeFromHAR(har, { url: /supabase\.(co|in)/, update: BASELINE, updateContent: 'embed', notFound: 'fallback' });
  }
  const tab = await ctx.newPage();
  // The homepage shuffles which Collection pieces it shows. Pinning
  // Math.random makes every run shuffle the same way. (A seeded sequence was
  // not enough: other scripts draw from it in whatever order they load.)
  await tab.addInitScript(() => { Math.random = () => 0.42; });
  const problems = new Set();
  const clean = s => s.split(ORIGIN).join('').slice(0, 240);
  tab.on('pageerror', e => problems.add(`script error: ${clean(e.message)}`));
  tab.on('console', m => { if (m.type() === 'error') problems.add(`console error: ${clean(m.text())}`); });
  tab.on('response', r => {
    if (r.url().startsWith(ORIGIN) && r.status() >= 400) problems.add(`missing file: ${clean(r.url())} (${r.status()})`);
  });
  try {
    await tab.goto(`${ORIGIN}/${page}`, { waitUntil: 'load', timeout: 45000 });
    await tab.waitForLoadState('networkidle', { timeout: 8000 }).catch(() => {});
    await tab.evaluate(async () => {
      // Lazy photos only load near the screen, and a full-page shot is not
      // "near the screen" — so whichever happened to start loading showed up.
      // Load every one of them, before and after the walk down.
      const eager = () => document.querySelectorAll('img[loading="lazy"]').forEach(i => { i.loading = 'eager'; });
      // Room pages: the dots track the 3D scene, which never sits still.
      if (document.querySelector('spline-viewer')) {
        const s = document.createElement('style');
        s.textContent = '.dot { visibility: hidden !important; }';
        document.head.appendChild(s);
      }
      eager();
      // Walk down the page so scroll-triggered reveals fire, then come back up.
      for (let y = 0; y < document.documentElement.scrollHeight; y += innerHeight / 2) {
        scrollTo(0, y);
        await new Promise(r => setTimeout(r, 80));
      }
      eager();
      scrollTo(0, 0);
    });
    // Photos come from Supabase and arrive late; a half-loaded grid in one
    // run and a full one in the next is not a change. Wait for them all.
    await tab.waitForFunction(() => [...document.images].every(i => i.complete), null, { timeout: 15000 }).catch(() => {});
    await tab.waitForTimeout(1200);
    const opts = {
      fullPage: true, animations: 'disabled', caret: 'hide',
      // The whole 3D box, not just its canvas: Spline sizes the canvas only
      // once the scene loads, so masking the canvas alone masked a different
      // area depending on how far loading had got.
      mask: [tab.locator('canvas, video, iframe, spline-viewer, model-viewer, #scene-wrap')], maskColor: '#FF00FF',
    };
    /* A STABLE shot, not the first one. Every photo can be fully loaded and
       still come out blank: the browser throws away decoded pixels for images
       far off-screen (some Nest photos are 7680px wide), and a full-page
       capture can grab the page before it has redrawn them. So decode every
       image now, then keep shooting until two captures in a row match. */
    await tab.evaluate(() => Promise.all([...document.images].map(i => i.decode().catch(() => {}))));
    let shot = await tab.screenshot(opts);
    for (let n = 0; n < 5; n++) {
      await tab.waitForTimeout(400);
      const again = await tab.screenshot(opts);
      if (again.equals(shot)) break;
      shot = again;
    }
    await writeFile(join(BASELINE ? BASE : NOW, `${name}.png`), shot);
  } catch (e) {
    problems.add(`page did not load: ${clean(e.message.split('\n')[0])}`);
  }
  await ctx.close();
  return [...problems];
}

console.log(`\n  ${BASELINE ? 'Baseline' : '2. Photographing'}: ${PAGES.length} pages × laptop + phone`);
const problems = {};
let next = 0;
async function worker() {
  while (next < JOBS.length) {
    const job = JOBS[next++];
    problems[job.name] = await shoot(job);
    process.stdout.write('.');
  }
}
await Promise.all(Array.from({ length: 3 }, worker));
await browser.close();
server.close();
console.log('');

if (BASELINE) {
  await writeFile(join(BASE, 'problems.json'), JSON.stringify(problems, null, 2));
  console.log(`\n  Baseline saved — ${JOBS.length} screenshots in tools/regression/baseline.`);
  console.log('  Make the change, then run:  node tools/regression.mjs\n');
  process.exit(0);
}

// ── Compare ──
async function diff(name) {
  const [A, B] = await Promise.all([BASE, NOW].map(d =>
    sharp(join(d, `${name}.png`)).ensureAlpha().raw().toBuffer({ resolveWithObject: true })));
  const aw = A.info.width, bw = B.info.width;
  const w = Math.min(aw, bw), h = Math.min(A.info.height, B.info.height);
  const out = Buffer.alloc(w * h * 4);
  let changed = 0, top = -1, bottom = -1;
  for (let y = 0; y < h; y++) {
    for (let x = 0; x < w; x++) {
      const i = (y * aw + x) * 4, j = (y * bw + x) * 4, o = (y * w + x) * 4;
      const d = Math.abs(A.data[i] - B.data[j]) + Math.abs(A.data[i + 1] - B.data[j + 1]) + Math.abs(A.data[i + 2] - B.data[j + 2]);
      if (d > PIXEL_THRESHOLD) {
        changed++;
        if (top < 0) top = y;
        bottom = y;
        out[o] = 230; out[o + 1] = 30; out[o + 2] = 60;
      } else {
        // The unchanged page, faded right back so the red reads at a glance.
        out[o] = out[o + 1] = out[o + 2] = 200 + ((A.data[i] + A.data[i + 1] + A.data[i + 2]) / 3) * 0.2;
      }
      out[o + 3] = 255;
    }
  }
  const resized = A.info.height !== B.info.height || aw !== bw;
  const flagged = changed > MIN_PIXELS || resized;
  if (flagged) await sharp(out, { raw: { width: w, height: h, channels: 4 } }).png().toFile(join(DIFF, `${name}.png`));
  return { flagged, changed, pct: changed / (w * h) * 100, top, bottom, before: A.info.height, after: B.info.height };
}

const before = JSON.parse(await readFile(join(BASE, 'problems.json'), 'utf8'));
const results = [];
for (const job of JOBS) {
  const r = { ...job, newProblems: problems[job.name].filter(p => !(before[job.name] || []).includes(p)) };
  if (existsSync(join(BASE, `${job.name}.png`)) && existsSync(join(NOW, `${job.name}.png`))) Object.assign(r, await diff(job.name));
  else r.missing = true;
  results.push(r);
}

function describe(r) {
  if (r.missing) return 'no screenshot — the page failed to load in one of the two runs';
  const parts = [];
  if (r.changed > MIN_PIXELS) parts.push(`${r.pct < 0.1 ? '<0.1' : r.pct.toFixed(1)}% of the page, from ${r.top}px to ${r.bottom}px down`);
  if (r.before !== r.after) parts.push(`page length ${r.before}px → ${r.after}px, so everything below the change moves`);
  return parts.join('; ');
}

const changedPages = [...new Set(results.filter(r => r.flagged || r.missing).map(r => r.page))];
const samePages = PAGES.filter(p => !changedPages.includes(p));
const withProblems = results.filter(r => r.newProblems.length);

console.log('\n  3. Result\n');
for (const page of changedPages) {
  console.log(`  CHANGED     ${page}`);
  for (const r of results.filter(r => r.page === page && (r.flagged || r.missing))) console.log(`                ${r.vp.padEnd(8)} ${describe(r)}`);
}
if (samePages.length) console.log(`  unchanged   ${samePages.join(', ')}`);
for (const r of withProblems) {
  console.log(`  NEW ERROR   ${r.page} (${r.vp})`);
  for (const p of r.newProblems) console.log(`                ${p}`);
}
if (!markupOk) console.log('  MARKUP      tools/check-pages.mjs found problems — see above');

// ── The report ──
const esc = s => String(s).replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
const shots = results.filter(r => r.flagged || r.missing).map(r => `
  <section>
    <h2>${esc(r.page)} <span>${r.vp}</span></h2>
    <p>${esc(describe(r))}</p>
    ${r.missing ? '' : `<div class="trio">
      <figure><figcaption>Before</figcaption><img loading="lazy" src="baseline/${r.name}.png"></figure>
      <figure><figcaption>After</figcaption><img loading="lazy" src="latest/${r.name}.png"></figure>
      <figure><figcaption>Difference (red)</figcaption><img loading="lazy" src="diff/${r.name}.png"></figure>
    </div>`}
  </section>`).join('');
const errors = withProblems.map(r => `<li><b>${esc(r.page)} (${r.vp})</b><ul>${r.newProblems.map(p => `<li>${esc(p)}</li>`).join('')}</ul></li>`).join('');

await writeFile(join(OUT, 'report.html'), `<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8">
<title>Regression report · Urban Nest</title>
<style>
  body { margin: 0; padding: 32px; font: 14px/1.5 system-ui, sans-serif; background: #F5F7F6; color: #0F1F22; }
  h1 { font-size: 22px; margin: 0 0 4px; } h2 { font-size: 16px; margin: 0 0 4px; } h2 span { color: #586366; font-weight: 400; }
  .sum { margin: 0 0 28px; color: #586366; }
  .box { background: #fff; border: 1px solid #D9E0DE; border-radius: 8px; padding: 16px 20px; margin-bottom: 20px; }
  .bad { border-color: #C0392B; } .good { border-color: #2E8B57; }
  section { background: #fff; border: 1px solid #D9E0DE; border-radius: 8px; padding: 16px 20px; margin-bottom: 20px; }
  .trio { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; align-items: start; }
  figure { margin: 0; } figcaption { font-size: 12px; color: #586366; margin-bottom: 4px; }
  img { width: 100%; border: 1px solid #D9E0DE; display: block; }
</style></head><body>
<h1>Regression report</h1>
<p class="sum">${new Date().toLocaleString('en-IN')} · ${PAGES.length} pages × laptop + phone</p>
<div class="box ${changedPages.length ? '' : 'good'}"><b>Changed:</b> ${changedPages.length ? changedPages.map(esc).join(', ') : 'nothing'}<br>
<b>Unchanged:</b> ${samePages.map(esc).join(', ') || 'none'}<br>
<small>The page you edited should be in "Changed". Anything else there is worth a look before deploying.</small></div>
${errors ? `<div class="box bad"><b>New errors since the baseline</b><ul>${errors}</ul></div>` : ''}
${markupOk ? '' : '<div class="box bad"><b>tools/check-pages.mjs found markup problems</b> — see the terminal.</div>'}
${shots}
</body></html>`);

console.log(`\n  Report: tools/regression/report.html\n`);
process.exit(markupOk && !withProblems.length && !results.some(r => r.missing) ? 0 : 1);
