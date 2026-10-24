/* Refreshes look.html (the live /look page) with the rooms that are live on the homepage.
 *     node mocks/build-look.mjs
 * The homepage is the one place rooms are defined (the sh-room markup for
 * photo and dot positions, window.SHOP_ROOMS for piece ids); this copies them
 * into the Look Around page so the two never drift apart. */
import { readFileSync, writeFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const HERE = dirname(fileURLToPath(import.meta.url));
const index = readFileSync(join(HERE, '..', 'index.html'), 'utf8').replace(/\r\n/g, '\n');
const shop = JSON.parse(index.match(/<script>window\.SHOP_ROOMS = (\[.*\]);<\/script>/)[1]);
const names = [...index.matchAll(/class="sh-tab" data-i="(\d+)" role="tab">([^<]+)</g)].reduce((o, m) => (o[m[1]] = m[2], o), {});
const blocks = [...index.matchAll(/<div class="sh-room" data-i="(\d+)">([\s\S]*?)\n    <\/div>/g)];

const ROOMS = blocks.map(([, i, body]) => {
  const img = body.match(/<img src="(images\/room-[\w-]+)\.webp"/)[1];
  const pos = [...body.matchAll(/style="left:([\d.]+)%;top:([\d.]+)%/g)].map(m => [+m[1], +m[2]]);
  const r = shop[+i];
  if (pos.length !== r.dots.length) throw new Error('room ' + i + ': ' + pos.length + ' dots vs ' + r.dots.length);
  return { img, label: r.label, name: names[i] || 'Room', ar: r.ar,
    dots: r.dots.map((d, n) => ({ x: pos[n][0], y: pos[n][1], id: d.id, s: d.s })) };
});

const raw = readFileSync(join(HERE, '..', 'look.html'), 'utf8'), crlf = raw.includes('\r\n');
let html = raw.replace(/\r\n/g, '\n');
// the rooms are always written on one line, so nothing after them can be caught
const re = /^var ROOMS = .*;$/m;
if (!re.test(html)) throw new Error('ROOMS line');
html = html.replace(re, () => 'var ROOMS = ' + JSON.stringify(ROOMS) + ';');
writeFileSync(join(HERE, '..', 'look.html'), crlf ? html.replace(/\n/g, '\r\n') : html);
console.log('look.html: ' + ROOMS.length + ' rooms, ' + ROOMS.reduce((s, r) => s + r.dots.length, 0) + ' dots');
