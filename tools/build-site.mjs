/* Assemble dist/ — the folder that actually gets deployed.
 *
 *   node tools/build-site.mjs
 *   netlify deploy --prod --dir dist
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
  { dir: '.',      exts: ['.html', '.splinecode', '.png', '.js', '.toml'], deep: false },
  { dir: 'admin',  exts: ['.html', '.js'],                                 deep: false },
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

await rm(DIST, { recursive: true, force: true });
await mkdir(DIST, { recursive: true });

let count = 0, bytes = 0;
for (const rule of RULES) {
  const from = join(ROOT, rule.dir);
  let entries;
  try { entries = await readdir(from, { withFileTypes: true }); }
  catch { continue; }

  for (const e of entries) {
    if (!e.isFile() || !rule.exts.includes(extname(e.name).toLowerCase())) continue;
    const src = join(from, e.name);
    const dest = join(DIST, relative(ROOT, src));
    await mkdir(dirname(dest), { recursive: true });
    await cp(src, dest);
    bytes += (await stat(src)).size;
    count++;
  }
  console.log(`  ${rule.dir.padEnd(8)} ${String(entries.filter(e => e.isFile() &&
    rule.exts.includes(extname(e.name).toLowerCase())).length).padStart(3)} files`);
}

console.log(`\n  dist/ — ${count} files, ${(bytes / 1048576).toFixed(1)} MB`);
console.log('  Deploy it with:  netlify deploy --prod --dir dist\n');

// The .sql files in admin/ are deliberately absent: they are run by hand in
// the Supabase dashboard and nothing on the site fetches them.
