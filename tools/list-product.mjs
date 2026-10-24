/* From an Amazon link to a finished listing, in one command.
 *
 *   node tools/list-product.mjs <amazon link> [<amazon link> ...] [options]
 *
 *   --3d                 also make the 3D model: Meshy (from the cover photo)
 *                        → Draco compression → a real render check → upload
 *                        → attached to the listing
 *   --3d-for=<item id>   make the 3D model for a listing that already exists
 *   --photo=<n>          with --3d-for / --prep-for: build from photo n (1 = cover)
 *                        instead of letting the script choose
 *   --photo-file=<path>  with --3d-for / --prep-for: build from a photo cropped by hand instead
 *   --no-cutout          send the photo as it is (no background removal), for a photo already cropped clean
 *   --section=essentials list into Essentials (default: collection)
 *   --category=<slug>    category slug, when the guess from the title is wrong
 *   --publish            go live at once (default: saved as a draft to check in admin)
 *   --dry                read the page and show what would be listed; change nothing
 *   --update=<item id>   fill an EXISTING listing (e.g. a photo-less draft) from one link instead of
 *                        adding a new one; its published state, section and category are left as they
 *                        are (unless --category is given)
 *   --photos=<n>         keep only n photos: Amazon's main shot plus the plainest of the rest
 *   --pick=1,3,5         keep exactly these photos (numbers as on the --sheet strip), chosen by eye
 *   --sheet=<file.png>   with --dry: save a numbered strip of all the listing's photos, to pick from
 *   --save-photos=<dir>  with --sheet: also save every photo full size (to crop one for --photo-file)
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
import { dirname, join, basename, resolve } from 'node:path';
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
const UPDATE = flag('update');
const PHOTOS = Number(flag('photos')) || 0;
const PICK = flag('pick') ? String(flag('pick')).split(',').map(Number).filter(Boolean) : null;
if (UPDATE && links.length !== 1) { console.error('--update takes exactly one link'); process.exit(1); }
if (!links.length && !MODEL_FOR && !flag('check-render') && !flag('prep-for')) { console.error('usage: node tools/list-product.mjs <amazon link> [...] [--3d] [--section=essentials] [--category=slug] [--publish] [--dry]\n       node tools/list-product.mjs --3d-for=<item id>'); process.exit(1); }

// ─────────────────────────────────────────────────────────── keys
const env = {};
try { for (const l of readFileSync(join(ROOT, '.env'), 'utf8').split(/\r?\n/)) { const m = l.match(/^([A-Z0-9_]+)=(.*)$/); if (m) env[m[1]] = m[2].trim().replace(/^["']|["']$/g, ''); } } catch {}
const SB_URL = env.SUPABASE_URL || 'https://ifwxgwvsyispkaxzbstg.supabase.co';
const SB_KEY = env.SUPABASE_SERVICE_ROLE_KEY;
const MESHY_KEY = env.MESHY_API_KEY;

/* Supabase's newer secret keys (sb_secret_…) go in the apikey header only; the
   older service_role key (a JWT, eyJ…) also goes in Authorization. */
const AUTH = SB_KEY && SB_KEY.startsWith('sb_') ? { apikey: SB_KEY } : { apikey: SB_KEY, Authorization: 'Bearer ' + SB_KEY };
const sb = async (path, opts = {}) => {
  const r = await fetch(SB_URL + path, { ...opts, headers: { ...AUTH, ...(opts.headers || {}) } });
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
    headers: { ...AUTH, 'Content-Type': type, 'Cache-Control': 'max-age=31536000', 'x-upsert': 'false' },
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
  const add = (k, v) => { k = text(k).replace(/\s*:\s*$/, ''); v = text(v); if (!k || !v || seen.has(k.toLowerCase()) || k.length > 40 || v.length > 120) return; if (/customer review|best sellers rank|asin|date first available|manufacturer|packer|importer|generic name|item part number|model number|country of origin|net quantity|included components|^price$|^upc$|country of publication/i.test(k)) return; seen.add(k.toLowerCase()); specs.push([k, v]); };
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
    .normalize('NFKC')                                              // 𝗕𝗢𝗟𝗗 maths letters → plain text
    .replace(/\p{Extended_Pictographic}️?/gu, '').replace(/^[\s\]】)]+/, '')   // emoji, and a bracket left behind
    .trim()
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
/* Meshy builds best from the plainest photo: the piece alone on an even
   background, no hands, props or lifestyle scene. Each photo is scored by how
   much its outer border varies (a plain backdrop barely changes at the edges)
   plus how much a text banner or busy scene adds across the whole frame;
   the lowest score is sent. (His rule, 21 Oct 2026.) */
async function plainScore(u) {
  try {
    const buf = Buffer.from(await (await fetch(u, { headers: { 'User-Agent': UA } })).arrayBuffer());
    const N = 48, { data, info } = await sharp(buf).resize(N, N, { fit: 'fill' }).removeAlpha().greyscale().raw().toBuffer({ resolveWithObject: true });
    const px = (x, y) => data[y * info.width + x];
    const ring = [];
    for (let y = 0; y < N; y++) for (let x = 0; x < N; x++) if (x < 4 || y < 4 || x >= N - 4 || y >= N - 4) ring.push(px(x, y));
    const sd = (a) => { const m = a.reduce((s, v) => s + v, 0) / a.length; return Math.sqrt(a.reduce((s, v) => s + (v - m) ** 2, 0) / a.length); };
    // neighbouring-pixel jumps: high for clutter, lifestyle scenes and text
    let busy = 0; for (let y = 0; y < N; y++) for (let x = 1; x < N; x++) busy += Math.abs(px(x, y) - px(x - 1, y));
    return sd(ring) * 2 + busy / (N * N);
  } catch { return Infinity; }
}
async function plainestPhoto(urls) {
  let best = null;
  for (const u of urls.filter(Boolean)) {
    const score = await plainScore(u);
    if (!best || score < best.score) best = { url: u, score };
  }
  return best ? best.url : urls[0];
}
/* --photos=n: Amazon's main shot (nearly always the piece on white) plus the
   plainest of the rest, so infographics and busy lifestyle shots drop out. */
async function cleanPhotos(urls, n) {
  const [main, ...rest] = urls;
  const scored = [];
  for (const u of rest) scored.push({ u, s: await plainScore(u) });
  return [main, ...scored.sort((a, b) => a.s - b.s).slice(0, n - 1).map((x) => x.u)];
}

/* Meshy is "not the brightest": a lifestyle scene, a text banner or a prop
   gets built into the model. So, when it can, the photo is cleaned first:
     1. every photo has its background cut out (a local AI model, ~8 s each)
     2. only the largest connected shape is kept — a text strip or a loose
        prop that does not touch the piece goes with the background
     3. photos where the piece runs off the edge (cropped) are passed over;
        of the rest, the fullest view of the piece wins
     4. it is centred on plain white with a margin and sent as the image
   Anything touching the piece itself (a hand, a candle in it) stays: those
   need a person, or a better photo. If the cut-out tool is missing, the
   plainest original photo is used instead. (His rule, 21 Oct 2026.) */
async function preparedPhoto(urls) {
  urls = urls.filter(Boolean);
  // the cut-outs run in their own process (tools/cutout.mjs: two libvips copies crash in one)
  const tmp = join(ROOT, 'models', 'source', '.cutouts');
  mkdirSync(tmp, { recursive: true });
  const outs = urls.map((_, i) => join(tmp, `cut-${Date.now().toString(36)}-${i}.png`));
  const run = spawnSync(process.execPath, [join(HERE, 'cutout.mjs'), ...urls.flatMap((u, i) => [u, outs[i]])], { cwd: HERE, encoding: 'utf8', timeout: 600000 });
  if (run.error || !outs.some((o) => existsSync(o))) return { url: await plainestPhoto(urls), note: 'the plainest photo (the cut-out step could not run)' };
  let best = null;
  for (const [i] of urls.entries()) {
    try {
      if (!existsSync(outs[i])) continue;
      const cut = readFileSync(outs[i]);
      // the mask, small enough to label its pieces quickly
      const N = 160;
      const { data: a } = await sharp(cut).ensureAlpha().extractChannel(3).resize(N, N, { fit: 'fill' }).raw().toBuffer({ resolveWithObject: true });
      const on = (k) => a[k] > 128, lab = new Int32Array(N * N).fill(-1), sizes = [];
      for (let k = 0; k < N * N; k++) {
        if (!on(k) || lab[k] >= 0) continue;
        const id = sizes.length, stack = [k]; lab[k] = id; let n = 0;
        while (stack.length) { const p = stack.pop(); n++; const x = p % N, y = (p / N) | 0;
          for (const q of [x > 0 && p - 1, x < N - 1 && p + 1, y > 0 && p - N, y < N - 1 && p + N]) if (q !== false && on(q) && lab[q] < 0) { lab[q] = id; stack.push(q); } }
        sizes.push(n);
      }
      if (!sizes.length) continue;
      const main = sizes.indexOf(Math.max(...sizes)), area = sizes[main] / (N * N), stray = (sizes.reduce((s, v) => s + v, 0) - sizes[main]) / (N * N);
      let x0 = N, y0 = N, x1 = 0, y1 = 0;
      for (let k = 0; k < N * N; k++) if (lab[k] === main) { const x = k % N, y = (k / N) | 0; x0 = Math.min(x0, x); y0 = Math.min(y0, y); x1 = Math.max(x1, x); y1 = Math.max(y1, y); }
      const touches = (x0 <= 1) + (y0 <= 1) + (x1 >= N - 2) + (y1 >= N - 2);
      /* Big enough is enough (a top-down shot fills the frame and still makes a
         poor model), so size counts only up to a quarter of the frame; then a
         clean, uncropped cut-out; then the seller's order — the first photos
         are nearly always the main side or three-quarter view. */
      const score = Math.min(area, 0.25) * 4 - stray * 2 - touches * 0.5 - i * 0.08;
      if (!best || score > best.score) best = { i, score, cut, lab, main, N, box: [x0, y0, x1, y1], touches };
    } catch {}
  }
  if (!best) return { url: await plainestPhoto(urls), note: 'the plainest photo (no cut-out worked)' };
  // keep only the main shape, crop to it, centre it on white with a margin
  const meta = await sharp(best.cut).metadata(), W = meta.width, H = meta.height, { N, lab, main } = best;
  const rgba = await sharp(best.cut).ensureAlpha().raw().toBuffer();
  /* Erase by the coarse labels without stepping the outline: a pixel goes only
     if it belongs to another shape, or to background with no main-shape cell
     beside it. Zeroing every non-main cell cut the piece's soft edge into
     160-px stairs, which Meshy then built as jagged geometry. */
  const nearMain = (cx, cy) => { for (let dy = -1; dy <= 1; dy++) for (let dx = -1; dx <= 1; dx++) { const x = cx + dx, y = cy + dy; if (x >= 0 && y >= 0 && x < N && y < N && lab[y * N + x] === main) return true; } return false; };
  for (let y = 0; y < H; y++) for (let x = 0; x < W; x++) {
    const cx = (x * N / W) | 0, cy = (y * N / H) | 0, l = lab[cy * N + cx];
    if (l === main) continue;
    if (l >= 0 || !nearMain(cx, cy)) rgba[(y * W + x) * 4 + 3] = 0;
  }
  const [x0, y0, x1, y1] = best.box, cx = Math.floor(x0 * W / N), cy = Math.floor(y0 * H / N);
  const cw = Math.min(W - cx, Math.ceil((x1 - x0 + 1) * W / N)), ch = Math.min(H - cy, Math.ceil((y1 - y0 + 1) * H / N));
  const piece = await sharp(rgba, { raw: { width: W, height: H, channels: 4 } }).extract({ left: cx, top: cy, width: cw, height: ch }).png().toBuffer();
  const side = Math.round(Math.max(cw, ch) * 1.25);
  // two steps: sharp resizes before it composites, whatever order they are written in
  const placed = await sharp({ create: { width: side, height: side, channels: 3, background: '#ffffff' } })
    .composite([{ input: piece, left: Math.round((side - cw) / 2), top: Math.round((side - ch) / 2) }])
    .png().toBuffer();
  const square = await sharp(placed).resize(1024, 1024).jpeg({ quality: 92 }).toBuffer();
  mkdirSync(join(ROOT, 'models', 'source'), { recursive: true });
  return { url: 'data:image/jpeg;base64,' + square.toString('base64'), jpg: square,
    note: `photo ${best.i + 1} of ${urls.length}, background removed${best.touches ? ' (piece touches the frame edge)' : ''}` };
}

// --photo=n: the photo was chosen by eye; the scorer above only guesses.
// --photo-file=<path>: a photo cropped by hand (e.g. the one clean mat out of a size diagram), when none of the
// listing's own photos shows the piece alone
const pickPhoto = (photos) => (flag('photo-file') ? [resolve(flag('photo-file'))]
  : flag('photo') ? [photos[Number(flag('photo')) - 1]].filter(Boolean) : photos);

// --no-cutout: send the photo as it is, only squared up on white. The cut-out can mistake part of the piece for
// background (it erased the brown slats of a shower mat and holed a stone mat), so a photo already cropped
// clean by hand skips it.
async function plainPhoto(src) {
  const buf = /^https?:/.test(src) ? Buffer.from(await (await fetch(src, { headers: { 'User-Agent': UA } })).arrayBuffer()) : readFileSync(src);
  const jpg = await sharp(buf).flatten({ background: '#ffffff' }).resize(1024, 1024, { fit: 'contain', background: '#ffffff' }).jpeg({ quality: 92 }).toBuffer();
  return { url: 'data:image/jpeg;base64,' + jpg.toString('base64'), jpg, note: 'the photo as given (no cut-out)' };
}
const photoForMeshy = (photos) => (flag('no-cutout') ? plainPhoto(pickPhoto(photos)[0]) : preparedPhoto(pickPhoto(photos)));

async function makeModel(item) {
  if (!MESHY_KEY) throw new Error('No MESHY_API_KEY in .env');
  const slug = slugify(item.name) || 'piece';
  const photos = [item.image_url].concat(Array.isArray(item.gallery) ? item.gallery : []);
  const prep = await photoForMeshy(photos);
  const source = prep.url;
  if (prep.jpg) writeFileSync(join(ROOT, 'models', 'source', slug + '-meshy-input.jpg'), prep.jpg);   // what Meshy saw, to check
  console.log(`   3D · building from ${prep.note}`);
  console.log(`   3D · asking Meshy to build "${item.name.slice(0, 50)}…"`);
  const mr = await fetch('https://api.meshy.ai/openapi/v1/image-to-3d', {
    method: 'POST', headers: { Authorization: 'Bearer ' + MESHY_KEY, 'Content-Type': 'application/json' },
    /* Meshy's best (his call, 22 Oct 2026): 7.1 with Ultra 4K geometry and 4K
       textures, and no Meshy remesh (its docs: off = highest quality). ~35
       credits. The raw model is heavy; shrink-model.mjs below brings it to web size. */
    body: JSON.stringify({ image_url: source, ai_model: 'meshy-7.1', geometry_resolution: '4k', texture_resolution: '4k', should_texture: true, enable_pbr: true, should_remesh: false, target_formats: ['glb'] }),
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
  const c = spawnSync(process.execPath, [join(HERE, 'shrink-model.mjs'), raw, out], { cwd: HERE, stdio: 'inherit' });
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

// node tools/list-product.mjs --prep-for=<item id>   (shows the photo Meshy would get; spends no credits)
if (flag('prep-for')) {
  const [item] = await sb('/rest/v1/collection_items?id=eq.' + flag('prep-for') + '&select=name,image_url,gallery');
  const prep = await photoForMeshy([item.image_url].concat(item.gallery || []));
  const out = join(ROOT, 'models', 'source', (slugify(item.name) || 'piece') + '-meshy-input.jpg');
  if (prep.jpg) writeFileSync(out, prep.jpg);
  console.log('would build from ' + prep.note + (prep.jpg ? '\nsaved: ' + out : ''));
  process.exit(0);
}

if (MODEL_FOR) {
  const [item] = await sb(`/rest/v1/collection_items?id=eq.${MODEL_FOR}&select=id,name,image_url,gallery,model_url`);
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
    if (DRY) {
      console.log('   description: ' + (description(p) || '—')); console.log('   specs: ' + p.specs.map((s) => s.join(': ')).join(' · '));
      if (flag('sheet')) {                          // numbered strip of every photo, to choose from with --pick
        const T = 300, tiles = [], keep = flag('save-photos');   // --save-photos=<dir>: the full-size photos too, to crop for --photo-file
        if (keep) mkdirSync(keep, { recursive: true });
        for (const [i, u] of p.photos.entries()) {
          try {
            const full = Buffer.from(await (await fetch(u, { headers: { 'User-Agent': UA } })).arrayBuffer());
            if (keep) writeFileSync(join(keep, `${p.asin || 'photo'}-${i + 1}.jpg`), full);
            const img = await sharp(full).resize(T, T, { fit: 'contain', background: '#fff' }).png().toBuffer();
            const num = Buffer.from(`<svg width="60" height="44" xmlns="http://www.w3.org/2000/svg"><rect width="60" height="44" fill="#14302f"/><text x="30" y="31" font-family="Arial" font-size="26" font-weight="700" fill="#fff" text-anchor="middle">${i + 1}</text></svg>`);
            tiles.push(await sharp(img).composite([{ input: num, left: 0, top: 0 }]).png().toBuffer());
          } catch {}
        }
        await sharp({ create: { width: tiles.length * (T + 8), height: T, channels: 3, background: '#ccc' } })
          .composite(tiles.map((t, i) => ({ input: t, left: i * (T + 8), top: 0 }))).png().toFile(flag('sheet'));
        console.log('   sheet: ' + flag('sheet'));
      }
      ok++; continue;
    }

    if (p.asin) {
      const dup = await sb(`/rest/v1/collection_items?select=id,name&buy_link=ilike.*${p.asin}*` + (UPDATE ? `&id=neq.${UPDATE}` : ''));
      if (dup.length) { console.log(`   already listed as "${dup[0].name.slice(0, 60)}" (${dup[0].id}) — skipped`); continue; }
    }
    // the photos, into our own storage
    const slug = slugify(name) || 'piece';
    const urls = [];
    const chosen = PICK ? PICK.map((n) => p.photos[n - 1]).filter(Boolean)
      : PHOTOS ? await cleanPhotos(p.photos, PHOTOS) : p.photos.slice(0, MAX_GALLERY + 1);
    for (const [i, src] of chosen.entries()) {
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
    let item;
    if (UPDATE) {                                   // fill the existing listing; its published state and order stay as they are
      delete row.published; delete row.sort_order; delete row.section;
      if (!FORCE_CAT) delete row.category;
      [item] = await sb('/rest/v1/collection_items?id=eq.' + UPDATE, { method: 'PATCH', headers: { 'Content-Type': 'application/json', Prefer: 'return=representation' }, body: JSON.stringify(row) });
      if (!item) throw new Error('no listing with id ' + UPDATE);
      console.log(`   updated ${item.published ? '(live)' : '(still a draft)'} · ${urls.length} photos · id ${item.id}`);
    } else {
      [item] = await sb('/rest/v1/collection_items', { method: 'POST', headers: { 'Content-Type': 'application/json', Prefer: 'return=representation' }, body: JSON.stringify(row) });
      console.log(`   listed ${PUBLISH ? '(live)' : '(draft — publish it in admin)'} · ${urls.length} photos · id ${item.id}`);
    }
    if (WANT_3D) await makeModel(item);
    ok++;
  } catch (e) { failed++; console.log('   ✗ ' + e.message); }
  await new Promise((r) => setTimeout(r, 1500));            // unhurried, one page at a time
}
if (links.length) console.log(`\n${ok} done${failed ? ', ' + failed + ' failed' : ''}.`);
