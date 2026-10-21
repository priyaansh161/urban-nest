/* From an Amazon link to a finished listing, in one command.
 *
 *   node tools/list-product.mjs <amazon link> [<amazon link> ...] [options]
 *
 *   --3d                 also make the 3D model: Meshy (from the cover photo)
 *                        → Draco compression → a real render check → upload
 *                        → attached to the listing
 *   --3d-for=<item id>   make the 3D model for a listing that already exists
 *   --section=essentials list into Essentials (default: collection)
 *   --category=<slug>    category slug, when the guess from the title is wrong
 *   --publish            go live at once (default: saved as a draft to check in admin)
 *   --dry                read the page and show what would be listed; change nothing
 *
 * Keys, from the project's .env (never committed):
 *   SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY   to upload photos and write the listing
 *   MESHY_API_KEY                             for --3d (Meshy credits per model)
 *
 * What it does for each link:
 *   1. reads the product page: title, brand, price, the listing's own photos,
 *      the bullet points and the specification table
 *   2. skips it if a listing with the same product (ASIN) already exists
 *   3. shrinks the photos to WebP (1600px, as the admin does) and puts them in
 *      the 'Blog Images' bucket, so the site never depends on Amazon's servers
 *   4. writes the listing: long-form name, category, price, description, specs,
 *      cover + gallery, and a clean affiliate link /dp/ASIN?tag=...
 *   5. with --3d: see makeModel() below
 */
import { readFileSync, writeFileSync, mkdirSync, existsSync, statSync } from 'node:fs';
import { spawnSync } from 'node:child_process';
import { createServer } from 'node:http';
import { dirname, join, basename } from 'node:path';
import { fileURLToPath } from 'node:url';
import sharp from 'sharp';

const HERE = dirname(fileURLToPath(import.meta.url));
const ROOT = join(HERE, '..');

// ─────────────────────────────────────────────────────────── settings
const AFFILIATE_TAG = 'urbannest03b-21';
const IMG_BUCKET = 'Blog Images', MODEL_BUCKET = 'Models';
const MAX_GALLERY = 7, IMG_MAX = 1600;
const UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130 Safari/537.36';

// ─────────────────────────────────────────────────────────── arguments
const argv = process.argv.slice(2);
const flag = (n) => { const a = argv.find((x) => x === `--${n}` || x.startsWith(`--${n}=`)); return a === undefined ? undefined : (a.includes('=') ? a.split('=').slice(1).join('=') : true); };
const links = argv.filter((a) => !a.startsWith('--'));
const DRY = !!flag('dry'), WANT_3D = !!flag('3d'), PUBLISH = !!flag('publish');
const SECTION = flag('section') || 'collection';
const FORCE_CAT = flag('category');
const MODEL_FOR = flag('3d-for');
if (!links.length && !MODEL_FOR && !flag('check-render')) { console.error('usage: node tools/list-product.mjs <amazon link> [...] [--3d] [--section=essentials] [--category=slug] [--publish] [--dry]\n       node tools/list-product.mjs --3d-for=<item id>'); process.exit(1); }

// ─────────────────────────────────────────────────────────── keys
const env = {};
try { for (const l of readFileSync(join(ROOT, '.env'), 'utf8').split(/\r?\n/)) { const m = l.match(/^([A-Z0-9_]+)=(.*)$/); if (m) env[m[1]] = m[2].trim().replace(/^["']|["']$/g, ''); } } catch {}
const SB_URL = env.SUPABASE_URL || 'https://ifwxgwvsyispkaxzbstg.supabase.co';
const SB_KEY = env.SUPABASE_SERVICE_ROLE_KEY;
const MESHY_KEY = env.MESHY_API_KEY;

const sb = async (path, opts = {}) => {
  const r = await fetch(SB_URL + path, { ...opts, headers: { apikey: SB_KEY, Authorization: 'Bearer ' + SB_KEY, ...(opts.headers || {}) } });
  const text = await r.text();
  if (!r.ok) throw new Error(`Supabase ${r.status} on ${path.split('?')[0]}: ${text.slice(0, 200)}`);
  return text ? JSON.parse(text) : null;
};
async function checkSupabase() {
  if (!SB_KEY) throw new Error('No SUPABASE_SERVICE_ROLE_KEY in .env');
  try { await sb('/rest/v1/collection_items?select=id&limit=1'); }
  catch (e) { throw new Error('The Supabase key in .env was refused (' + e.message.slice(0, 40) + '). Copy a fresh service_role key from Supabase → Project Settings → API into .env.'); }
}
async function upload(bucket, path, body, type) {
  const r = await fetch(`${SB_URL}/storage/v1/object/${encodeURIComponent(bucket)}/${path}`, {
    method: 'POST', body,
    headers: { apikey: SB_KEY, Authorization: 'Bearer ' + SB_KEY, 'Content-Type': type, 'Cache-Control': 'max-age=31536000', 'x-upsert': 'false' },
  });
  if (!r.ok) throw new Error(`upload to ${bucket} failed ${r.status}: ${(await r.text()).slice(0, 200)}`);
  return `${SB_URL}/storage/v1/object/public/${encodeURIComponent(bucket)}/${path}`;
}

// ─────────────────────────────────────────────────────────── reading the page
const decode = (s) => String(s || '').replace(/&amp;/g, '&').replace(/&#39;|&apos;/g, "'").replace(/&quot;/g, '"').replace(/&lt;/g, '<').replace(/&gt;/g, '>').replace(/&nbsp;|&#160;/g, ' ').replace(/&#(\d+);/g, (_, n) => String.fromCharCode(+n));
const text = (s) => decode(String(s || '').replace(/<script[\s\S]*?<\/script>|<style[\s\S]*?<\/style>/g, '').replace(/<[^>]+>/g, ' ')).replace(/[‎‏]/g, '').replace(/\s+/g, ' ').trim();
const slugify = (s) => String(s || '').toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, '').slice(0, 60);

async function readAmazon(link) {
  const r = await fetch(link, { headers: { 'User-Agent': UA, 'Accept-Language': 'en-IN,en;q=0.9' }, redirect: 'follow' });
  const html = await r.text();
  if (/captcha/i.test(html) && !/productTitle/.test(html)) throw new Error('Amazon showed a captcha for ' + link + ' — try again in a few minutes');
  const asin = (r.url.match(/\/(?:dp|gp\/product)\/([A-Z0-9]{10})/) || html.match(/name="ASIN" value="([A-Z0-9]{10})"/) || html.match(/"asin"\s*:\s*"([A-Z0-9]{10})"/) || [])[1];
  const title = text((html.match(/id="productTitle"[^>]*>([\s\S]*?)<\/span>/) || [])[1]);
  if (!title) throw new Error('Could not read a product title from ' + link);
  const byline = text((html.match(/id="bylineInfo"[^>]*>([\s\S]*?)<\/a>/) || [])[1]);
  const brand = byline.replace(/^Visit the\s+/i, '').replace(/\s+Store$/i, '').replace(/^Brand:\s*/i, '').trim();
  const whole = (html.match(/class="a-price-whole">([\d,]+)/) || [])[1];
  const price = whole ? '₹' + whole : '';
  // the listing's own photo set
  let photos = [];
  const a = html.indexOf("'colorImages': { 'initial'");
  if (a >= 0) {
    const seg = html.slice(a, html.indexOf("')", a));
    photos = seg.split('{"hiRes":').slice(1).map((s) => { const hr = s.match(/^"([^"]+)"/); const lg = s.match(/"large":"([^"]+)"/); return hr ? hr[1] : lg && lg[1]; }).filter(Boolean);
  }
  if (!photos.length) { const lm = html.match(/data-old-hires="([^"]+)"/) || html.match(/"landingImageUrl":"([^"]+)"/); if (lm) photos = [lm[1]]; }
  photos = [...new Set(photos)];
  // bullet points
  const fb = (html.match(/id="feature-bullets"[\s\S]*?<\/ul>/) || [''])[0];
  const bullets = [...fb.matchAll(/<span class="a-list-item">([\s\S]*?)<\/span>/g)].map((m) => text(m[1])).filter((b) => b && b.length > 12);
  // specification rows, from either of Amazon's two layouts
  const specs = [];
  const seen = new Set();
  const add = (k, v) => { k = text(k).replace(/\s*:\s*$/, ''); v = text(v); if (!k || !v || seen.has(k.toLowerCase()) || k.length > 40 || v.length > 120) return; if (/customer review|best sellers rank|asin|date first available|manufacturer|packer|importer|generic name|item part number|model number|country of origin|net quantity|included components/i.test(k)) return; seen.add(k.toLowerCase()); specs.push([k, v]); };
  for (const m of html.matchAll(/<tr[^>]*>\s*<th[^>]*>([\s\S]*?)<\/th>\s*<td[^>]*>([\s\S]*?)<\/td>/g)) add(m[1], m[2]);
  for (const m of html.matchAll(/<span class="a-text-bold">([\s\S]*?)<\/span>\s*<span[^>]*>([\s\S]*?)<\/span>/g)) add(m[1].replace(/[:‏‎\s]+$/g, ''), m[2]);
  for (const m of html.matchAll(/<tr class="a-spacing-small[^"]*">\s*<td[^>]*>([\s\S]*?)<\/td>\s*<td[^>]*>([\s\S]*?)<\/td>/g)) add(m[1], m[2]);
  return { link, url: r.url.split('?')[0], asin, title, brand, price, photos, bullets, specs: specs.slice(0, 10) };
}

// ─────────────────────────────────────────────────────────── shaping the listing
const CATS = SECTION === 'essentials'
  ? [['bath-essentials', /bath|toilet|towel|soap|shower|wash ?basin/i], ['kitchen-essentials', /kitchen|spatula|spoon|knife|oil|jar|mug|cup|plate|dish|cutting|chopping|masala|spice|butter|curd|rack/i], ['bedroom', /bed|pillow|duvet|blanket|bedside/i], ['desk', /desk|laptop|pen|study|organi[sz]er/i], ['entryway', /shoe|entry|key holder|doormat|coat/i], ['storage', /storage|basket|box|bin|container/i]]
  : [['festive', /diwali|diya|urli|rangoli|toran|tealight|pooja|puja|festive|string light|fairy light/i], ['lighting', /chandelier|pendant|ceiling light|jhumar|hanging (?:lamp|light)/i], ['luminaires', /floor lamp|table lamp|desk lamp|bedside lamp|lamp/i], ['timepieces', /clock/i], ['wall-art', /canvas|painting|wall art|frame|print/i], ['amphorae', /vase|planter|pot\b|urn/i], ['sculptures', /sculpture|statue|idol|figurine|showpiece|bust/i]];
const guessCategory = (title) => FORCE_CAT || (CATS.find(([, re]) => re.test(title)) || [CATS[0][0]])[0];

/* Long-form name, as the Collection uses them: brand, item and size, then a
   short use after a bar. Amazon titles are usually most of the way there, so
   this trims rather than rewrites: at most two bar-separated parts, ~140 chars. */
function longName(p) {
  let parts = p.title.split('|').map((s) => s.trim()).filter(Boolean);
  let name = parts.slice(0, 2).join(' | ');
  if (p.brand && !name.toLowerCase().startsWith(p.brand.toLowerCase()) && !/^generic$/i.test(p.brand)) name = p.brand + ' ' + name;
  if (name.length > 140) name = name.slice(0, 140).replace(/[\s,|-]+\S*$/, '');
  // a bracket the cut left open goes, with what followed it
  if ((name.match(/\(/g) || []).length > (name.match(/\)/g) || []).length) name = name.slice(0, name.lastIndexOf('(')).trim();
  return name;
}
const description = (p) => {
  const b = p.bullets.map((x) => x
    .replace(/^\d+\.\s*[^:\-–]{2,40}?\s*[:\-–]\s+/, '')            // '1. Charging Bull - '
    .replace(/^[A-Z0-9][A-Z0-9 &'.,/-]{3,70}[:\-–]\s*/, '')         // '6 INCH COMPACT BRASS URLI BOWL: '
    .replace(/^【[^】]*】\s*/, '').trim()).filter(Boolean);
  let d = b.slice(0, 2).join(' ');
  if (d.length > 320) d = d.slice(0, 320).replace(/\s+\S*$/, '') + '…';
  return d || null;
};

async function photoToWebp(url) {
  const r = await fetch(url, { headers: { 'User-Agent': UA } });
  if (!r.ok) throw new Error('photo ' + r.status);
  return sharp(Buffer.from(await r.arrayBuffer())).resize(IMG_MAX, IMG_MAX, { fit: 'inside', withoutEnlargement: true }).webp({ quality: 82 }).toBuffer();
}

// ─────────────────────────────────────────────────────────── 3D
/* Meshy (image → 3D, from the cover photo) → download the GLB → Draco
   compression (tools/compress-model.mjs, the recipe that renders) → load it in
   a real model-viewer and wait for its load event → upload → model_url. */
async function makeModel(item) {
  if (!MESHY_KEY) throw new Error('No MESHY_API_KEY in .env');
  const slug = slugify(item.name) || 'piece';
  console.log(`   3D · asking Meshy to build "${item.name.slice(0, 50)}…"`);
  const mr = await fetch('https://api.meshy.ai/openapi/v1/image-to-3d', {
    method: 'POST', headers: { Authorization: 'Bearer ' + MESHY_KEY, 'Content-Type': 'application/json' },
    body: JSON.stringify({ image_url: item.image_url, ai_model: 'latest', should_texture: true, enable_pbr: true, should_remesh: true, target_polycount: 60000, target_formats: ['glb'] }),
  });
  const mj = await mr.json();
  if (!mr.ok || !mj.result) throw new Error('Meshy refused the task: ' + JSON.stringify(mj).slice(0, 200));
  const taskId = mj.result;
  let task, last = -1;
  for (let i = 0; i < 180; i++) {                         // up to 30 minutes
    await new Promise((r) => setTimeout(r, 10000));
    task = await (await fetch('https://api.meshy.ai/openapi/v1/image-to-3d/' + taskId, { headers: { Authorization: 'Bearer ' + MESHY_KEY } })).json();
    if (task.progress !== last) { last = task.progress; process.stdout.write(`   3D · Meshy ${task.status.toLowerCase()} ${task.progress || 0}%\r`); }
    if (['SUCCEEDED', 'FAILED', 'CANCELED'].includes(task.status)) break;
  }
  console.log('');
  if (!task || task.status !== 'SUCCEEDED' || !task.model_urls?.glb) throw new Error('Meshy did not finish: ' + (task?.status || 'timeout') + ' ' + JSON.stringify(task?.task_error || ''));
  console.log(`   3D · Meshy done (${task.consumed_credits ?? '?'} credits)`);

  mkdirSync(join(ROOT, 'models', 'source'), { recursive: true });
  const raw = join(ROOT, 'models', 'source', slug + '-raw.glb');
  const out = join(ROOT, 'models', slug + '.glb');
  writeFileSync(raw, Buffer.from(await (await fetch(task.model_urls.glb)).arrayBuffer()));
  const c = spawnSync(process.execPath, [join(HERE, 'compress-model.mjs'), raw, out], { cwd: HERE, stdio: 'inherit' });
  if (c.status !== 0 || !existsSync(out)) throw new Error('compression failed');
  const mb = (statSync(out).size / 1048576).toFixed(2);
  const dims = await renderCheck(out);
  console.log(`   3D · compressed to ${mb} MB and rendered fine (${dims})`);
  const url = await upload(MODEL_BUCKET, slug + '-' + Date.now().toString(36) + '.glb', readFileSync(out), 'model/gltf-binary');
  await sb('/rest/v1/collection_items?id=eq.' + item.id, { method: 'PATCH', headers: { 'Content-Type': 'application/json', Prefer: 'return=minimal' }, body: JSON.stringify({ model_url: url }) });
  console.log('   3D · attached to the listing');
  return url;
}

/* Re-parsing a GLB proves nothing (the meshopt build that never displayed
   parsed fine). This loads it in model-viewer, the same viewer the site uses,
   and only passes when its load event fires. */
async function renderCheck(file) {
  const { chromium } = await import('playwright-core');
  const page = `<!doctype html><script type="module" src="https://unpkg.com/@google/model-viewer@3.5.0/dist/model-viewer.min.js"></script><model-viewer id="m" loading="eager" style="width:400px;height:400px"></model-viewer>`;
  const srv = createServer((req, res) => {
    if (req.url.startsWith('/m.glb')) { res.writeHead(200, { 'Content-Type': 'model/gltf-binary' }); res.end(readFileSync(file)); }
    else { res.writeHead(200, { 'Content-Type': 'text/html' }); res.end(page); }
  }).listen(0);
  const port = srv.address().port;
  const b = await chromium.launch({ channel: 'msedge' });
  try {
    const pg = await b.newPage();
    await pg.goto(`http://127.0.0.1:${port}/`);
    const result = await pg.evaluate(() => new Promise((res) => {
      customElements.whenDefined('model-viewer').then(() => {
        const m = document.getElementById('m');
        m.addEventListener('load', () => { const d = m.getDimensions(); res('ok ' + [d.x, d.y, d.z].map((v) => v.toFixed(2)).join(' × ')); });
        m.addEventListener('error', () => res('error'));
        m.src = '/m.glb';
        setTimeout(() => res('timeout'), 60000);
      });
    }));
    if (!result.startsWith('ok')) throw new Error('the model did not render (' + result + ')');
    return result.slice(3);
  } finally { await b.close(); srv.close(); }
}

// ─────────────────────────────────────────────────────────── run
// node tools/list-product.mjs --check-render=models/x.glb   (the render check on its own)
if (flag('check-render')) { console.log('renders: ' + await renderCheck(flag('check-render'))); process.exit(0); }
if (!DRY) await checkSupabase();

if (MODEL_FOR) {
  const [item] = await sb(`/rest/v1/collection_items?id=eq.${MODEL_FOR}&select=id,name,image_url,model_url`);
  if (!item) { console.error('No listing with id ' + MODEL_FOR); process.exit(1); }
  if (item.model_url) console.log('   (it already has a 3D model; this replaces it)');
  await makeModel(item);
}

let ok = 0, failed = 0;
for (const link of links) {
  console.log('\n→ ' + link);
  try {
    const p = await readAmazon(link);
    const name = longName(p);
    const category = guessCategory(p.title);
    const buy = p.asin ? `https://www.amazon.in/dp/${p.asin}?tag=${AFFILIATE_TAG}` : link;
    console.log(`   ${name}\n   ${category} · ${p.price || 'no price shown'} · ${p.photos.length} photos · ${p.specs.length} specs · ASIN ${p.asin || '?'}`);
    if (DRY) { console.log('   description: ' + (description(p) || '—')); console.log('   specs: ' + p.specs.map((s) => s.join(': ')).join(' · ')); ok++; continue; }

    if (p.asin) {
      const dup = await sb(`/rest/v1/collection_items?select=id,name&buy_link=ilike.*${p.asin}*`);
      if (dup.length) { console.log(`   already listed as "${dup[0].name.slice(0, 60)}" (${dup[0].id}) — skipped`); continue; }
    }
    // the photos, into our own storage
    const slug = slugify(name) || 'piece';
    const urls = [];
    for (const [i, src] of p.photos.slice(0, MAX_GALLERY + 1).entries()) {
      try { urls.push(await upload(IMG_BUCKET, `${slug}-${Date.now().toString(36)}${i}.webp`, await photoToWebp(src), 'image/webp')); }
      catch (e) { console.log('   a photo was skipped: ' + e.message); }
    }
    if (!urls.length) throw new Error('no photo could be saved');
    // the Amazon affiliate seller, the same one every Amazon listing uses
    const [aff] = await sb('/rest/v1/collection_items?select=affiliate_seller_id&affiliate_seller_id=not.is.null&limit=1');
    const row = {
      name, category, section: SECTION, price: p.price || null, description: description(p),
      image_url: urls[0], gallery: urls.slice(1), specs: p.specs, buy_link: buy,
      primary_cta: 'affiliate', affiliate_seller_id: aff?.affiliate_seller_id || null,
      in_stock: true, coming_soon: false, published: PUBLISH, sort_order: 0,
    };
    const [item] = await sb('/rest/v1/collection_items', { method: 'POST', headers: { 'Content-Type': 'application/json', Prefer: 'return=representation' }, body: JSON.stringify(row) });
    console.log(`   listed ${PUBLISH ? '(live)' : '(draft — publish it in admin)'} · ${urls.length} photos · id ${item.id}`);
    if (WANT_3D) await makeModel(item);
    ok++;
  } catch (e) { failed++; console.log('   ✗ ' + e.message); }
  await new Promise((r) => setTimeout(r, 1500));            // unhurried, one page at a time
}
if (links.length) console.log(`\n${ok} done${failed ? ', ' + failed + ' failed' : ''}.`);
