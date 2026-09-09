/* Structural check over every page in this project.
 *
 * WHY THIS EXISTS: the site is hand-written HTML with no build step and
 * nothing validating the markup, so a mistyped tag is silent. The browser
 * quietly repairs it into something that merely looks wrong. That is how
 * the admin dashboard lost its "3D Products" link: two nav groups were
 * pasted inside a still-open <a>, HTML closed that anchor early, and the
 * link ended up holding the wrong words. Nothing errored. Reading the
 * source did not show it either — only parsing did.
 *
 * These are the checks that would have caught it, plus the neighbours of
 * the same kind. No dependencies, no build; run it before a deploy:
 *
 *     node tools/check-pages.mjs
 *
 * Exits 1 if anything is found, so it can gate a deploy later.
 *
 * IT IS NOT A VALIDATOR. It catches the specific mistakes this codebase
 * actually makes. Loading the pages in a browser is still the other half:
 * console errors, layout, and anything the database fills in.
 */
import { readFileSync, readdirSync, existsSync } from 'node:fs';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), '..');

const pages = [
  ...readdirSync(ROOT).filter(f => f.endsWith('.html')),
  ...readdirSync(join(ROOT, 'admin')).filter(f => f.endsWith('.html')).map(f => 'admin/' + f),
  ...readdirSync(join(ROOT, 'tools')).filter(f => f.endsWith('.html')).map(f => 'tools/' + f),
];

/* Names that are not page functions, so an inline handler mentioning one
   proves nothing either way. */
const BUILTIN = new Set(['if', 'for', 'while', 'return', 'typeof', 'function', 'new', 'catch',
  'switch', 'this', 'void', 'delete', 'in', 'of', 'do', 'else', 'try', 'confirm', 'alert',
  'prompt', 'parseInt', 'parseFloat', 'Number', 'String', 'Boolean', 'Array', 'Object', 'JSON',
  'Math', 'Date', 'encodeURIComponent', 'decodeURIComponent', 'setTimeout', 'clearTimeout',
  'fetch', 'event', 'console']);

/* Blanks out everything that is not markup — HTML comments, inline
   scripts, and style blocks — so prose about tags does not read as tags.
   That last one is not hypothetical: a CSS comment in collection.html
   reads "the affiliate one an <a>", which the first version of this
   script happily reported as an unclosed link.
   Newlines are kept so the line numbers below stay true. */
const blank = m => m.replace(/[^\n]/g, ' ');
const stripped = s => s
  .replace(/<!--[\s\S]*?-->/g, blank)
  .replace(/<script(?![^>]*\ssrc=)[^>]*>[\s\S]*?<\/script>/g, blank)
  .replace(/<style[^>]*>[\s\S]*?<\/style>/g, blank);

let found = 0;
const report = (page, list) => {
  if (!list.length) return;
  found += list.length;
  console.log('\n' + page);
  list.forEach(l => console.log('   ' + l));
};

for (const page of pages) {
  const file = join(ROOT, page);
  const src = readFileSync(file, 'utf8');
  const markup = stripped(src);
  const bugs = [];

  /* ── an anchor opened while another was still open ──
     The one that bit us. HTML has no nested links: the browser ends the
     outer anchor where the inner one starts, and the outer one keeps
     whatever happened to be in between. */
  const lineOf = i => markup.slice(0, i).split('\n').length;
  const open = [];
  for (const m of markup.matchAll(/<a\b|<\/a\s*>/g)) {
    if (m[0][1] === '/') { open.pop(); continue; }
    if (open.length) bugs.push('line ' + lineOf(m.index) + ': <a> opened inside the one at line ' +
      open[open.length - 1] + ' — the browser closes that one here and it keeps the wrong content');
    open.push(lineOf(m.index));
  }
  if (open.length) bugs.push('<a> never closed, opened at line ' + open.join(', '));

  /* ── a link or button with nothing to click ──
     Usually the tail of the mistake above: the words went elsewhere. */
  for (const m of markup.matchAll(/<(a|button)\b([^>]*)>([\s\S]*?)<\/\1\s*>/g)) {
    const [, tag, attrs, inner] = m;
    const text = inner.replace(/<[^>]+>/g, '').replace(/&[a-z]+;/gi, ' ').trim();
    if (text || /<(img|svg|picture)\b/.test(inner) || /\b(aria-label|title)=/.test(attrs)) continue;
    bugs.push('empty <' + tag + '>: ' + (attrs.match(/(href|id|class)="([^"]*)"/) || [, , '?'])[2]);
  }

  /* ── an empty src or href ──
     Not blank: it resolves to the page itself, which the browser fetches
     and then rejects as an image. A wasted request on every visit. */
  for (const m of markup.matchAll(/\s(src|href|poster|srcset)=""/g))
    bugs.push('empty ' + m[1] + '="" — this requests the page itself');

  /* ── two elements answering to one id ── */
  const ids = [...markup.matchAll(/\sid="([^"]+)"/g)].map(m => m[1]);
  const dupes = ids.filter((id, i) => ids.indexOf(id) !== i);
  [...new Set(dupes)].forEach(id => bugs.push('duplicate id: ' + id));

  /* ── a label or aria attribute pointing at nothing ── */
  const idSet = new Set(ids);
  for (const attr of ['for', 'aria-labelledby', 'aria-controls', 'aria-describedby'])
    for (const m of markup.matchAll(new RegExp('\\s' + attr + '="([^"]+)"', 'g')))
      m[1].split(/\s+/).filter(Boolean).forEach(id => {
        if (!idSet.has(id)) bugs.push(attr + '="' + id + '" points at no element');
      });

  /* ── a handler wired to a function that does not exist ──
     Looks perfectly fine in the source; the button simply does nothing,
     and nothing is logged until someone presses it. */
  const inlineJs = [...src.matchAll(/<script(?![^>]*\ssrc=)[^>]*>([\s\S]*?)<\/script>/g)].map(m => m[1]).join('\n');
  let js = inlineJs;
  for (const m of src.matchAll(/<script[^>]*\ssrc=["']([^"']+)["']/g)) {
    const rel = m[1].split('?')[0];
    if (/^https?:|^\/\//.test(rel)) continue;
    const p = rel.startsWith('/') ? join(ROOT, rel) : join(dirname(file), rel);
    if (existsSync(p)) js += '\n' + readFileSync(p, 'utf8');
  }
  const defined = new Set();
  for (const re of [/\bfunction\s+([A-Za-z_$][\w$]*)/g, /\b(?:const|let|var)\s+([A-Za-z_$][\w$]*)\s*=/g, /\bwindow\.([A-Za-z_$][\w$]*)\s*=/g])
    for (const m of js.matchAll(re)) defined.add(m[1]);
  const missingFns = new Set();
  for (const m of src.matchAll(/\son[a-z]+\s*=\s*"([^"]*)"/g))
    for (const c of m[1].matchAll(/(?:^|[^.\w$'"])([A-Za-z_$][\w$]*)\s*\(/g))
      if (!BUILTIN.has(c[1]) && !defined.has(c[1])) missingFns.add(c[1]);
  missingFns.forEach(n => bugs.push('handler calls ' + n + '() — never defined on this page'));

  /* ── script asking for an id the markup does not have ──
     The page's own scripts only. A shared file like auth.js names ids it
     creates itself, and image-upload.js documents ids belonging to other
     pages; neither is this page's problem. Ids assembled at runtime, like
     'o-' + id, do not match the pattern and are skipped. */
  const wanted = new Set();
  for (const m of inlineJs.matchAll(/getElementById\(\s*['"]([^'"]+)['"]\s*\)/g)) wanted.add(m[1]);
  for (const m of inlineJs.matchAll(/querySelector(?:All)?\(\s*['"]#([A-Za-z][\w-]*)['"]\s*\)/g)) wanted.add(m[1]);
  [...wanted].forEach(id => { if (!idSet.has(id)) bugs.push('script asks for #' + id + ' — not in the markup'); });

  /* ── a local file that is not there ── */
  for (const m of markup.matchAll(/\s(?:src|href)="([^"]+)"/g)) {
    const v = m[1];
    if (/^(https?:|mailto:|tel:|data:|blob:|javascript:|#|\/\/)/i.test(v)) continue;
    const clean = v.split('#')[0].split('?')[0];
    if (!clean) continue;
    const p = clean.startsWith('/') ? join(ROOT, clean) : join(dirname(file), clean);
    if (!existsSync(p)) bugs.push('missing file: ' + v);
  }

  report(page, bugs);
}

console.log('\n' + pages.length + ' pages checked — ' +
  (found ? found + ' problem' + (found === 1 ? '' : 's') + ' above' : 'nothing found'));
process.exit(found ? 1 : 0);
