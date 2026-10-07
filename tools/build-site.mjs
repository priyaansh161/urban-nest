/* Assemble dist/ — the folder that actually gets deployed.
 *
 *   node tools/build-site.mjs
 *   npx wrangler pages deploy        (Cloudflare Pages; wrangler.toml says where)
 *
 * WHY THIS EXISTS: `netlify deploy --dir .` uploads the whole project folder.
 * It reads neither .gitignore nor .netlifyignore — netlify-cli 27 has no
 * support for the latter at all — so 298 MB of raw Meshy exports and 436 MB
 * of unedited photographs were being published to the live site, including
 * /models/source/crystal chandelier-raw.glb at 106 MB.
 *
 * An ignore list cannot be trusted here, so this is an ALLOW list instead:
 * nothing reaches the CDN unless it is named below. Adding a page or a new
 * asset type means adding it here — which is the point. Forgetting shows up
 * as a missing file on the site, not as several hundred megabytes quietly
 * going public.
 */
import { cp, mkdir, rm, readdir, stat } from 'node:fs/promises';
import { dirname, extname, join, relative } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');
const DIST = join(ROOT, 'dist');

// Each rule is a folder plus the extensions that ship from it. `deep: false`
// means the folder's own files only — its subfolders are working material.
const RULES = [
  { dir: '.',      exts: ['.html', '.css', '.splinecode', '.png', '.js', '.toml', '.webmanifest'], deep: false },
  /* Named, not by extension. The root folder also holds DEPLOY.txt and
     DEPLOY-CHECKLIST.txt — private working notes — and allowing every .txt
     would have published them. */
  { dir: '.',      names: ['robots.txt', 'sitemap.xml', '_redirects', '_headers'] },
  { dir: 'admin',  exts: ['.html', '.js', '.css'],                                 deep: false },
  { dir: 'studio', exts: ['.html', '.js'],                                 deep: false },
  { dir: 'images', exts: ['.webp', '.png', '.jpg', '.svg'],                deep: false },
  /* models/ is deliberately NOT here. Every one of the 21 listings with a 3D
     view stores an absolute Supabase Storage URL — the admin's upload button
     cannot produce anything else — so nothing on the site ever asks Netlify
     for a .glb. Shipping them anyway put 69 MB on the CDN for files with no
     referrer, which is bandwidth spent on nothing.
     The files stay in the repo as a backup of what is in Supabase.
     If a listing is ever given a RELATIVE path by hand, like
     "models/vase.glb", add { dir: 'models', exts: ['.glb'], deep: false }
     back to this list or that piece will 404. */
];

// A rule ships files by extension, or an exact list of names.
const wanted = (rule, name) => rule.names ? rule.names.includes(name)
  : rule.exts.includes(extname(name).toLowerCase());

await rm(DIST, { recursive: true, force: true });
await mkdir(DIST, { recursive: true });

let count = 0, bytes = 0;
for (const rule of RULES) {
  const from = join(ROOT, rule.dir);
  let entries;
  try { entries = await readdir(from, { withFileTypes: true }); }
  catch { continue; }

  for (const e of entries) {
    if (!e.isFile() || !wanted(rule, e.name)) continue;
    const src = join(from, e.name);
    const dest = join(DIST, relative(ROOT, src));
    await mkdir(dirname(dest), { recursive: true });
    await cp(src, dest);
    bytes += (await stat(src)).size;
    count++;
  }
  console.log(`  ${rule.dir.padEnd(8)} ${String(entries.filter(e => e.isFile() &&
    wanted(rule, e.name)).length).padStart(3)} files${rule.names ? '  (' + rule.names.join(', ') + ')' : ''}`);
}

/* ── VERSION STAMPS ──
   Browsers keep theme.css and the photos for hours (Cloudflare's default
   cache), and the service worker serves photos from its own copy first. So a
   file replaced under the same name, a band photo or the stylesheet, kept
   showing the old one for a while after a deploy. Every reference to a local
   photo, stylesheet or script in the built pages now carries a short hash of
   that file's contents (theme.css?v=3f9a1c2e): a changed file gets a new
   address and is fetched at once, an unchanged one stays cached. Only dist/
   is rewritten; the source files are untouched. */
const { createHash } = await import('node:crypto');
const { readFile, writeFile } = await import('node:fs/promises');
const hashes = new Map();
async function stamp(file) {
  if (!hashes.has(file)) {
    try { hashes.set(file, createHash('sha1').update(await readFile(file)).digest('hex').slice(0, 8)); }
    catch { hashes.set(file, null); }               // not in dist: leave the reference alone
  }
  return hashes.get(file);
}
async function stampHtml(htmlPath) {
  const html = await readFile(htmlPath, 'utf8');
  const base = dirname(htmlPath);
  // a quoted or url()-wrapped reference to a local photo, stylesheet or script
  const RE = /(["'(])(\/?)((?:[\w.-]+\/)*[\w.()% -]+\.(?:webp|png|jpe?g|svg|css|js))(?=["')])/g;
  const jobs = [];
  html.replace(RE, (m, open, slash, path, at) => { jobs.push({ m, open, slash, path, at }); return m; });
  let out = html, shift = 0, stamped = 0;
  for (const j of jobs) {
    if (/^(https?:)?\/\//.test(j.path) || j.path === 'sw.js') continue;
    const file = j.slash ? join(DIST, j.path) : join(base, j.path);
    const h = await stamp(file);
    if (!h) continue;
    const rep = j.open + j.slash + j.path + '?v=' + h;
    out = out.slice(0, j.at + shift) + rep + out.slice(j.at + shift + j.m.length);
    shift += rep.length - j.m.length;
    stamped++;
  }
  if (stamped) await writeFile(htmlPath, out);
  return stamped;
}
let stampedRefs = 0;
for (const dir of [DIST, join(DIST, 'admin'), join(DIST, 'studio')]) {
  let names = [];
  try { names = await readdir(dir); } catch { continue; }
  for (const n of names) if (n.endsWith('.html')) stampedRefs += await stampHtml(join(dir, n));
}
console.log(`  version stamps: ${stampedRefs} references`);

console.log(`\n  dist/ — ${count} files, ${(bytes / 1048576).toFixed(1)} MB`);
console.log('  Deploy it with:  npx wrangler pages deploy\n');

// The .sql files in admin/ are deliberately absent: they are run by hand in
// the Supabase dashboard and nothing on the site fetches them.
