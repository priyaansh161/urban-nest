/* Builds mocks/homepage-v2.html from the LIVE index.html, so the mock is the
 * real homepage with only the agreed changes swapped in. Re-run after the
 * homepage changes:   node mocks/build-v2.mjs
 * mocks/ is not in tools/build-site.mjs, so none of this can deploy. */
import { readFile, writeFile } from 'node:fs/promises';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const HERE = dirname(fileURLToPath(import.meta.url));
let html = (await readFile(join(HERE, '..', 'index.html'), 'utf8')).replace(/\r\n/g, '\n');

function swap(from, to, label) {
  const n = html.split(from).length - 1;
  if (n !== 1) throw new Error(`${label}: expected 1 match, found ${n}`);
  html = html.replace(from, () => to);
}
function swapRe(re, to, label) {
  if (!re.test(html)) throw new Error(`${label}: no match`);
  html = html.replace(re, () => to);
}

const ARROWS = `<div class="un-arrows" data-arrows>
        <button type="button" aria-label="Previous"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M19 12H5M11 6l-6 6 6 6"/></svg></button>
        <button type="button" aria-label="Next"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14M13 6l6 6-6 6"/></svg></button>
      </div>`;

/* ── 0. relative to mocks/, so it works from the server AND opened as a file ── */
swap('<head>', '<head>\n  <base href="../"/>', 'base');
swapRe(/<title>[^<]*<\/title>/, '<title>Homepage v2 Mock · Urban Nest</title>', 'title');

/* ── 1. the jugaad paragraphs → a before / after you drag ── */
swapRe(/<div class="statement-body">[\s\S]*?<\/div>\n  <\/section>/, `<p class="note">The paragraphs are replaced by one picture you drag. Left of the handle is the same corner, made do with; right of it, done just right. The point is made without a sentence, and jugaad is shown as honest, not mocked. No buttons: on a phone you swipe sideways on the photo to change room (drag near the white handle to compare), or tap the arrows either side. On a laptop, drag anywhere to compare and use the arrows to change room. The left-hand photos here are STAND-INS (the right-hand photo, greyed). The real ones get generated in Gemini from the same camera angle; the prompts are in mocks/before-after-prompts.md.</p>
    <div class="ba" id="ba">
      <div class="ba-row">
      <button type="button" class="ba-arrow" id="baPrev" aria-label="Previous room"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="m15 6-6 6 6 6"/></svg></button>
      <div class="ba-stage" id="baStage">
        <img class="ba-after" id="baAfter" alt=""/>
        <div class="ba-before-wrap"><img class="ba-before" id="baBefore" alt=""/></div>
        <span class="ba-stand">Left side is a stand-in photo</span>
        <span class="ba-tag ba-tag-l">Making do</span>
        <span class="ba-tag ba-tag-r">Just right</span>
        <div class="ba-handle" aria-hidden="true"><span class="ba-knob"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="m9 6-6 6 6 6M15 6l6 6-6 6"/></svg></span></div>
        <input class="ba-range" id="baRange" type="range" min="0" max="100" value="50" aria-label="Drag to compare making do with just right"/>
        <span class="ba-swipe" id="baSwipe" aria-hidden="true">Swipe for the next room</span>
      </div>
      <button type="button" class="ba-arrow" id="baNext" aria-label="Next room"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="m9 6 6 6-6 6"/></svg></button>
      </div>
      <div class="ba-foot">
        <span class="ba-room" id="baRoom"></span>
        <span class="ba-dots" id="baDots"></span>
        <a class="ba-shop" id="baShop" href="essentials.html">Shop this room →</a>
      </div>
    </div>
  </section>`, 'statement');

/* ── 2. collection: three tiles → a framed swipe rail ── */
swap(`<a class="collect-all" href="collection.html">See all →</a>
    </div>
    <div class="wstrip" id="collectGrid"></div>`,
`<span class="collect-right"><a class="collect-all" href="collection.html">See all →</a>
      ${ARROWS}</span>
    </div>
    <p class="note">Your collection, live from the database, as a swipe rail. Each piece now sits in a brass-edged frame with a cream inner border. You can save it with the heart, and its price shows. Swipe on a phone; drag or use the arrows on a laptop.</p>
    <div class="un-rail pc-rail" id="collectGrid" data-rail></div>
    <div class="un-progress" data-progress></div>`, 'collect markup');
swap(".select('id,name,category,image_url,model_url')", ".select('*')", 'collect select');
swap('var rows = sample(pool, 3);', 'var rows = sample(pool, 10);', 'collect count');
swapRe(/grid\.innerHTML = rows\.map\(function \(it\) \{[\s\S]*?\}\)\.join\(''\);\n          document\.getElementById\('collect'\)\.style\.display = '';/,
`grid.innerHTML = rows.map(function (it) {
            var img = it.image_url || 'images/det-vase.webp';
            var params = new URLSearchParams();
            if (it.category) params.set('c', it.category);
            params.set('p', it.id);
            var price = it.price_paise ? '₹' + Math.round(it.price_paise / 100).toLocaleString('en-IN') : (it.price || '');
            return '<a class="pc" href="collection.html?' + params.toString() + '">' +
              '<span class="pc-frame"><img src="' + esc(img) + '" alt="" loading="lazy" decoding="async"/>' +
              (it.model_url ? '<span class="pc-3d">3D</span>' : '') +
              '<button type="button" class="pc-save" aria-label="Save" aria-pressed="false"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M12 20s-7-4.5-7-10a4 4 0 0 1 7-2.6A4 4 0 0 1 19 10c0 5.5-7 10-7 10Z"/></svg></button></span>' +
              '<span class="pc-body"><span class="pc-cat">' + esc(it.category || 'Collection') + '</span>' +
              '<span class="pc-name">' + esc(it.name) + '</span>' +
              '<span class="pc-foot">' + (price ? '<span class="pc-price">' + esc(price) + '</span>' : '<span></span>') + '<span class="pc-go">View →</span></span></span></a>';
          }).join('');
          document.getElementById('collect').style.display = '';
          window.unRail && window.unRail(grid);`, 'collect render');

/* ── 3. NEW: the pieces in their setting, as 2D photographs with dots ── */
swap('  <!-- ── PHILOSOPHY ── -->', `  <!-- ── IN THE ROOM (mock) ── -->
  <section class="inroom shell" id="inroom">
    <div class="spaces-head">
      <span class="spaces-label">In the room</span>
      <span class="collect-right"><span class="ir-pills" id="irPills"></span>${ARROWS}</span>
    </div>
    <p class="note">New section. Each piece is shown where it lives, in an ordinary photograph rather than 3D. Tap a dot to see the piece and its price. Swipe sideways, or use the pills, to change rooms. The product names and prices are placeholders; in the real version they would come from the Admin, the same way the 3D room dots do.</p>
    <div class="un-rail ir-rail" id="irRail" data-rail></div>
    <div class="un-progress" data-progress></div>
  </section>

  <!-- ── PHILOSOPHY ── -->`, 'inroom');

/* ── 4. the four stacked pillars → the swipe deck ── */
swapRe(/<div class="pillars">[\s\S]*?\n      <\/div>\n    <\/div>\n  <\/section>/, `<div class="deck-col">
        <p class="note">The four stacked rows become the swipe deck you liked. Swipe the top card away, or use the arrows. Real customer reviews can go into this same deck once you have them; the live site shouldn't show made-up ones.</p>
        <div class="deck" id="deck"></div>
        <div class="deck-ctrl">
          <button type="button" id="deckBack" aria-label="Previous card"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M19 12H5M11 6l-6 6 6 6"/></svg></button>
          <span class="deck-count" id="deckCount">1 / 4</span>
          <button type="button" id="deckNext" aria-label="Next card"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14M13 6l6 6-6 6"/></svg></button>
        </div>
      </div>
    </div>
  </section>`, 'pillars');

/* ── 4b. NEW: The Nest Edit as story covers, live from nest_posts ── */
swap('  <!-- ── CONTACT ── -->', `  <!-- ── THE NEST EDIT (mock) ── -->
  <section class="edit shell" id="edit">
    <div class="spaces-head">
      <span class="spaces-label">The Nest Edit</span>
      <span class="collect-right"><a class="collect-all" href="community.html">All articles →</a>${ARROWS}</span>
    </div>
    <p class="note">The story-cover row you liked, now framed: a brass edge, a mount line over the photo, and the title on its own solid panel instead of floating over the picture. It shows your real published articles, and each one opens in the reader.</p>
    <div class="un-rail ed-rail" id="edRail" data-rail></div>
    <div class="un-progress" data-progress></div>
  </section>

  <!-- ── CONTACT ── -->`, 'nest edit');

/* ── 5. contact rows → three big buttons (footer untouched) ── */
swapRe(/<div class="contact-grid">[\s\S]*?\n    <\/div>\n  <\/section>/, `<p class="note">The contact details become three big buttons, one tap each. WhatsApp now opens a chat instead of dialling. The footer below is unchanged.</p>
    <div class="reach">
      <a href="https://wa.me/918588944583" target="_blank" rel="noopener"><span class="reach-ico"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"><path d="M6.5 3h3l1.5 4-2 1.5a11 11 0 0 0 5.5 5.5L16 12l4 1.5v3a2 2 0 0 1-2.2 2A15.5 15.5 0 0 1 4.5 5.2 2 2 0 0 1 6.5 3Z"/></svg></span><span class="reach-k">WhatsApp</span><span class="reach-v">+91 85889 44583</span></a>
      <a href="mailto:reachus.urbannest@gmail.com"><span class="reach-ico"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"><rect x="2.5" y="5" width="19" height="14" rx="2"/><path d="m3 6.5 9 6 9-6"/></svg></span><span class="reach-k">Email</span><span class="reach-v">reachus.urbannest@gmail.com</span></a>
      <a href="https://instagram.com/store.urbannest" target="_blank" rel="noopener"><span class="reach-ico"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"><rect x="3.5" y="3.5" width="17" height="17" rx="4.5"/><circle cx="12" cy="12" r="3.6"/><circle cx="17" cy="7" r="1" fill="currentColor" stroke="none"/></svg></span><span class="reach-k">Instagram</span><span class="reach-v">@store.urbannest</span></a>
    </div>
  </section>`, 'contact');

/* ── styles + behaviour ── */
const css = await readFile(join(HERE, 'v2.css'), 'utf8');
const js = await readFile(join(HERE, 'v2.js'), 'utf8');
swap('</head>', `<style>\n${css}\n</style>\n</head>`, 'css');
swap('</body>', `<div class="mockbar"><span><b>MOCK v2</b> · your homepage, more interactive · not live</span><button type="button" id="notesBtn" aria-pressed="true">Notes</button></div>
<script>\n${js}\n</script>\n</body>`, 'js');

await writeFile(join(HERE, 'homepage-v2.html'), html);
console.log('wrote mocks/homepage-v2.html');
