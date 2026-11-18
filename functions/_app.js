/* The real Collection / Essentials page, served at a category's or piece's own address.
 *
 * /collection/<category>, /essentials/<category> and /piece/<name>-<id8> used to be a plain page built for
 * search engines, with a button to the real page. A visitor arriving from Google had to click again to get
 * the 3D experience, and what they saw did not follow edits made in the admin.
 *
 * Now those addresses answer with the real page itself (collection.html / essentials.html), with three things
 * added for search engines: the title, description, canonical address and structured data of the category or
 * piece; a plain-text list of what is on the page (hidden once the page is drawn); and a one-line script that
 * moves the address bar to the page's usual form (?c=slug&p=id) before anything else runs. The page's own
 * code reads that, opens the category (and the piece), and draws everything live from the database, so an edit
 * in the admin shows at once. Nothing in collection.html / essentials.html needed to change.
 *
 * Files here start with an underscore so Cloudflare does not make them routes.
 */
import { esc, img, ORIGIN } from './_seo.js';

export async function appPage(ctx, o) {
  const res = await ctx.env.ASSETS.fetch(new URL('/' + o.section, ctx.request.url));
  let html = await res.text();
  const url = ORIGIN + o.path;
  const title = o.title + ' · Urban Nest';

  // 1. First thing in <head>: move the address to the page's own form, so every relative link after it
  //    (scripts, styles, images) resolves from the site root and the page reads ?c= / ?p= as it always has.
  const mover = `<script>window.UN_SEO=1;try{history.replaceState(history.state,'',${JSON.stringify(o.target).replace(/</g, '\\u003c')})}catch(e){}</script>`;
  html = /<meta charset="UTF-8"\s*\/?>/i.test(html)
    ? html.replace(/<meta charset="UTF-8"\s*\/?>/i, (m) => m + '\n  ' + mover)
    : html.replace(/<head>/i, (m) => m + '\n  ' + mover);

  // 2. Replace the page's own title, description, social tags and canonical with this page's.
  html = html
    .replace(/<title>[\s\S]*?<\/title>/i, () => '')
    .replace(/<meta\s+name="description"[^>]*>\s*/gi, '')
    .replace(/<meta\s+property="og:[^>]*>\s*/gi, '')
    .replace(/<meta\s+name="twitter:[^>]*>\s*/gi, '')
    .replace(/<link\s+rel="canonical"[^>]*>\s*/gi, '');
  const head = [
    `<title>${esc(title)}</title>`,
    `<meta name="description" content="${esc(o.description)}"/>`,
    `<link rel="canonical" href="${esc(url)}"/>`,
    `<meta property="og:type" content="${o.ogType || 'website'}"/>`,
    `<meta property="og:site_name" content="Urban Nest"/>`,
    `<meta property="og:title" content="${esc(title)}"/>`,
    `<meta property="og:description" content="${esc(o.description)}"/>`,
    `<meta property="og:url" content="${esc(url)}"/>`,
    o.image ? `<meta property="og:image" content="${esc(img(o.image, 1200))}"/>` : '',
    `<meta name="twitter:card" content="summary_large_image"/>`,
    o.jsonld ? `<script type="application/ld+json">${JSON.stringify(o.jsonld).replace(/</g, '\\u003c')}</script>` : '',
  ].filter(Boolean).join('\n  ');
  html = html.replace(/<\/head>/i, () => head + '\n</head>');

  // 3. What is on the page, as plain text and links, for anything that reads the HTML without running the page.
  //    Hidden: the page draws the same things properly once it loads.
  if (o.staticHtml) html = html.replace(/<body[^>]*>/i, (m) => m + `\n<div id="seo-static" hidden>${o.staticHtml}</div>`);

  return new Response(html, {
    headers: {
      'Content-Type': 'text/html; charset=utf-8',
      // Always re-checked: the page itself is live data, and the title and description follow the admin within a minute.
      'Cache-Control': 'public, max-age=0, must-revalidate',
    },
  });
}
