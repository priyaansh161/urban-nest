/* Pages built on the server, one per article, piece and category.
 *
 * Until 28 Oct 2026 every article and piece opened in an overlay drawn by
 * the browser, at /community?a=… or /collection?c=…&p=…. Google saw two
 * pages, not fifty: nothing had its own address, title or description, and
 * none of it was in the sitemap. These functions answer
 *
 *   /edit/<slug>          functions/edit/[slug].js
 *   /piece/<words>-<id8>  functions/piece/[slug].js
 *   /collection/<slug>    functions/collection/[slug].js
 *   /essentials/<slug>    functions/essentials/[slug].js
 *   /sitemap.xml          functions/sitemap.xml.js
 *
 * with a complete page, read straight from the database, so anything
 * published in the admin has a page (and a sitemap line) the moment it is
 * published, with no deploy. The overlays stay exactly as they were for
 * visitors; cards now also carry a real link to these addresses.
 *
 * The page around the content is seo-page.html: the site's own top bar,
 * footer and theme, filled in here. The address rules are urls.js, shared
 * with the pages, and an article's text is formatted by nest-body.js, the
 * same code the overlay uses.
 *
 * Files here start with an underscore so Cloudflare does not make them routes.
 */
import '../urls.js';
import '../nest-body.js';

export const UNUrls = globalThis.UNUrls;
export const formatBody = globalThis.formatBody;
export const ORIGIN = 'https://storeurbannest.in';

// The public (anon) key, as in supabase.js: it reads only what is published.
const SB = 'https://ifwxgwvsyispkaxzbstg.supabase.co';
const ANON = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imlmd3hnd3ZzeWlzcGtheHpic3RnIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODI3MjI3ODQsImV4cCI6MjA5ODI5ODc4NH0.goQIrgT8-tSbN7nIEvHGifKjczi0JhgY01FVu_lQc4c';

export async function sb(path) {
  const r = await fetch(SB + '/rest/v1/' + path, {
    headers: { apikey: ANON, Authorization: 'Bearer ' + ANON },
    cf: { cacheTtl: 60, cacheEverything: true },        // a minute at the edge, so a save in the admin shows soon
  });
  if (!r.ok) throw new Error('Supabase ' + r.status + ' on ' + path.split('?')[0]);
  return r.json();
}

export const esc = (s) => String(s == null ? '' : s)
  .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');

// The same resizing the pages ask Supabase for (supabase.js's unImg), at a fixed width.
export function img(url, width) {
  const STORED = SB + '/storage/v1/object/public/';
  if (!url || url.indexOf(STORED) !== 0 || /\.(gif|svg)(\?|$)/i.test(url)) return url || '';
  return url.replace('/storage/v1/object/public/', '/storage/v1/render/image/public/') +
    (url.indexOf('?') < 0 ? '?' : '&') + 'width=' + Math.min(2000, width) + '&resize=contain&quality=75';
}

export const dateIN = (d) => new Date(d).toLocaleDateString('en-IN', { day: 'numeric', month: 'long', year: 'numeric', timeZone: 'Asia/Kolkata' });
export const plain = (s) => String(s || '').replace(/[#*_>]/g, ' ').replace(/\s+/g, ' ').trim();
export const clip = (s, n) => { s = plain(s); return s.length <= n ? s : s.slice(0, n - 1).replace(/[\s,.;:]+\S*$/, '') + '…'; };
export const priceNumber = (p) => { const n = parseFloat(String(p || '').replace(/[^0-9.]/g, '')); return isFinite(n) && n > 0 ? n : null; };

// A buy link that leads somewhere: not a TODO placeholder, not marked gone in Admin → Amazon Links.
export const liveBuyLink = (it) => it.buy_link && !/^TODO-/i.test(it.buy_link) && it.amazon_status !== 'gone' ? it.buy_link : null;

export function pieceCard(it, catName) {
  return `<a class="sv-card" href="${esc(UNUrls.piece(it))}">` +
    `<img src="${esc(img(it.image_url, 600))}" alt="${esc(it.name)}" loading="lazy" decoding="async"/>` +
    `<div class="sv-card-b"><div class="sv-card-k">${esc(catName || '')}${it.model_url ? (catName ? ' · ' : '') + '3D' : ''}</div>` +
    `<div class="sv-card-t">${esc(it.name)}</div>${it.price ? `<div class="sv-card-p">${esc(it.price)}</div>` : ''}</div></a>`;
}

export function postCard(p) {
  return `<a class="sv-card sv-wide" href="${esc(UNUrls.post(p))}">` +
    (p.image_url ? `<img src="${esc(img(p.image_url, 700))}" alt="" loading="lazy" decoding="async"/>` : '') +
    `<div class="sv-card-b"><div class="sv-card-k">${esc(p.category || 'The Nest Edit')}</div>` +
    `<div class="sv-card-t">${esc(p.title)}</div>${p.read_time ? `<div class="sv-card-p">${esc(p.read_time)}</div>` : ''}</div></a>`;
}

/* Fill seo-page.html. Every slot is replaced with split/join rather than
   String.replace, so a "$" in a title or price cannot be read as a pattern. */
export async function page(ctx, o) {
  const shell = await (await ctx.env.ASSETS.fetch(new URL('/seo-page', ctx.request.url))).text();
  const url = ORIGIN + o.path;
  const head = [
    `<meta name="description" content="${esc(o.description)}"/>`,
    `<link rel="canonical" href="${esc(url)}"/>`,
    `<meta property="og:type" content="${o.ogType || 'website'}"/>`,
    `<meta property="og:site_name" content="Urban Nest"/>`,
    `<meta property="og:title" content="${esc(o.title)}"/>`,
    `<meta property="og:description" content="${esc(o.description)}"/>`,
    `<meta property="og:url" content="${esc(url)}"/>`,
    o.image ? `<meta property="og:image" content="${esc(img(o.image, 1200))}"/>` : '',
    `<meta name="twitter:card" content="summary_large_image"/>`,
    o.jsonld ? `<script type="application/ld+json">${JSON.stringify(o.jsonld).replace(/</g, '\\u003c')}</script>` : '',
  ].filter(Boolean).join('\n  ');
  const fill = {
    '{{TITLE}}': esc(o.title + ' · Urban Nest'),
    '{{TAG}}': o.tag, '{{H1}}': esc(o.h1), '{{H1CLASS}}': o.h1.length > 48 ? ' sv-is-long' : '',
    '{{SUB}}': o.sub ? `<p class="page-sub">${o.sub}</p>` : '',
    '{{MAIN}}': o.main, '{{SCRIPTS}}': o.scripts || '',
  };
  let html = shell.replace(/<!--HEAD-->[\s\S]*?<!--\/HEAD-->/, () => head);
  for (const [k, v] of Object.entries(fill)) html = html.split(k).join(v);
  return new Response(html, { headers: { 'Content-Type': 'text/html; charset=utf-8', 'Cache-Control': 'public, max-age=300' } });
}

export async function notFound(ctx) {
  const r = await ctx.env.ASSETS.fetch(new URL('/404', ctx.request.url));
  return new Response(await r.text(), { status: 404, headers: { 'Content-Type': 'text/html; charset=utf-8' } });
}

export const redirect = (path) => new Response(null, { status: 301, headers: { Location: path } });

export const ORG = { '@type': 'Organization', name: 'Urban Nest', url: ORIGIN, logo: ORIGIN + '/logo-icon.png' };
