/* Builds mocks/homepage-shop.html: the LIVE homepage with its hero replaced
 * by shoppable rooms (Gemini rooms staged with real Collection pieces).
 * Preview only: mocks/ is never deployed.
 *     node mocks/build-shop.mjs
 * A room is included once mocks/shop-<key>.webp exists. Dot x/y are percent
 * of the photo; c is the piece's category slug, id its collection_items id. */
import { readFile, writeFile, access } from 'node:fs/promises';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const HERE = dirname(fileURLToPath(import.meta.url));
let html = (await readFile(join(HERE, '..', 'index.html'), 'utf8')).replace(/\r\n/g, '\n');
const swap = (a, b, label) => { const n = html.split(a).length - 1; if (n !== 1) throw new Error(label + ': ' + n); html = html.replace(a, () => b); };
const swapRe = (re, b, label) => { if (!re.test(html)) throw new Error(label + ': no match'); html = html.replace(re, () => b); };

const ALL = [
  { key: 'living', name: 'Living', label: 'The living room · 7 pieces', ar: 2752 / 1536, alt: 'A warm living room styled with pieces from the Collection', dots: [
    { x: 50.2, y: 21.5, c: 'lighting',   id: 'fc9d3eff-d701-42d7-b047-c63e6f1e4eb1', label: 'Gold rings chandelier' },
    { x: 36.8, y: 39.4, c: 'luminaires', id: 'e570aa03-a749-4f8d-a187-87d1e5cbd7d1', label: 'Arc floor lamp' },
    { x: 53.4, y: 49.5, c: 'wall-art',   id: '9677aca6-246e-4f79-abb7-fd503824369a', label: 'Horse rider canvas' },
    { x: 53.6, y: 69.6, c: 'sculptures', id: '2f299fce-522a-495e-822e-a6d22c100360', label: 'White bull' },
    { x: 82.1, y: 56.8, c: 'amphorae',   id: 'f6355faf-00aa-4420-9166-ca48968b1a3c', label: 'Black vase, brass dogwood' },
    { x: 92.8, y: 81.0, c: 'amphorae',   id: '553c88f9-3698-456e-a618-186c5756b9e1', label: 'Soapstone vase' },
    { x: 69.9, y: 52.6, c: 'sculptures', id: 'fc8422e3-a75c-4479-bd69-72d0ccab8d4b', label: 'Hampi chariot' },
  ] },
  { key: 'bedroom',  name: 'Bedroom',     label: 'The bedroom · 7 pieces',        ar: 2752 / 1536, alt: 'A bedroom styled with pieces from the Collection', dots: [] },
  { key: 'kitchen',  name: 'Kitchen',     label: 'The kitchen · 8 essentials',    ar: 2752 / 1536, alt: 'A kitchen with pieces from the Essentials', dots: [] },
  { key: 'living2',  name: 'Lounge', label: 'The formal living · 7 pieces',  ar: 2752 / 1536, alt: 'A formal living room styled with pieces from the Collection', dots: [] },
  { key: 'bath',     name: 'Bath',        label: 'The bath · 6 essentials',       ar: 2752 / 1536, alt: 'A bathroom with pieces from the Essentials', dots: [] },
  { key: 'bedroom2', name: 'Guest room',     label: 'The guest room · 7 pieces',     ar: 2752 / 1536, alt: 'A guest bedroom styled with pieces from the Collection', dots: [] },
];
// rooms load their dots from shop-<key>.json once measured
const ROOMS = [];
for (const r of ALL) {
  try { await access(join(HERE, `shop-${r.key}.webp`)); } catch { continue; }
  try { Object.assign(r, JSON.parse(await readFile(join(HERE, `shop-${r.key}.json`), 'utf8'))); } catch {}
  ROOMS.push(r);
}

swap('<head>', '<head>\n  <base href="../"/>', 'base');
swapRe(/<title>[^<]*<\/title>/, '<title>Homepage · Shoppable Rooms Mock · Urban Nest</title>', 'title');
swap('<header class="hero">', '<header class="hero shop">', 'hero class');

const ARROW = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12h14M13 6l6 6-6 6"/></svg>';
swapRe(/<picture class="hero-media">[\s\S]*?<\/picture>\n    <div class="hero-scrim"><\/div>/, `${ROOMS.map((r, i) => `<div class="sh-room" data-i="${i}">
      <div class="sh-frame"><div class="sh-zoom">
        <picture><source media="(max-width: 700px)" srcset="mocks/shop-${r.key}-m.webp"/><img src="mocks/shop-${r.key}.webp" alt="${r.alt}"${i ? ' loading="lazy"' : ' fetchpriority="high"'} decoding="async"/></picture>
${r.dots.map((d, n) => `        <button type="button" class="sh-dot" data-n="${n}" style="left:${d.x}%;top:${d.y}%;--i:${n};--dl:${(n * 0.37).toFixed(2)}s" aria-label="${d.label}"></button>`).join('\n')}
      </div></div>
    </div>`).join('\n    ')}
    <div class="hero-scrim"></div>
    <div class="sh-spot" aria-hidden="true"></div>
    <a class="sh-card" href="collection.html"><img alt=""/><span><span class="k"></span><span class="n"></span><span class="p"></span><span class="go">View piece ${ARROW}</span></span></a>`, 'hero media');

/* the words: the tagline, the room being shown, how to use it, the rooms */
swapRe(/<div class="hero-inner shell rv">[\s\S]*?\n    <\/div>\n\n    <span class="hero-scroll"/, `<div class="hero-inner shell rv">
      <span class="hero-eyebrow sh-eyebrow"></span>
      <h1 class="hero-type">
        <span class="mask"><span>Just the right <em>feel.</em></span></span>
      </h1>
      <div class="sh-row">
        <span class="sh-hint"><i></i><span class="sh-hint-t">Every dot is a piece you can own. Tap one.</span></span>
        <div class="sh-tabs" role="tablist">
${ROOMS.map((r, i) => `          <button type="button" class="sh-tab" data-i="${i}" role="tab">${r.name}</button>`).join('\n')}
        </div>
      </div>
    </div>

    <span class="hero-scroll"`, 'hero words');

swap('</body>', `<div class="mockbar"><span><b>MOCK</b> · Shoppable rooms hero · not live</span></div>
<style>${await readFile(join(HERE, 'shop.css'), 'utf8')}</style>
<script>window.SHOP_ROOMS = ${JSON.stringify(ROOMS.map(r => ({ label: r.label, ar: r.ar, dots: r.dots.map(d => ({ id: d.id, c: d.c, s: d.s || 'collection', label: d.label })) })))};</script>
<script>${await readFile(join(HERE, 'shop.js'), 'utf8')}</script>
</body>`, 'tail');

await writeFile(join(HERE, 'homepage-shop.html'), html);
console.log('wrote mocks/homepage-shop.html with ' + ROOMS.length + ' room(s)');
