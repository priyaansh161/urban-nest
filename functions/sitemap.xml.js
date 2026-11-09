/* /sitemap.xml, built on each request so a newly published article, piece or
 * category is listed at once. robots.txt points here. It replaced the
 * hand-kept sitemap.xml on 28 Oct 2026; the fixed pages below are that
 * file's list. Add a line here when a new public page is added. */
import { sb, UNUrls, ORIGIN } from './_seo.js';

const PAGES = ['/', '/collection', '/essentials', '/spaces', '/community', '/rooms/quiet-bath/', '/rooms/sunday-bedroom/', '/about', '/join', '/policies', '/look'];

export async function onRequestGet() {
  const [posts, cats, items] = await Promise.all([
    sb('nest_posts?select=id,slug,created_at,updated_at&published=eq.true&order=created_at.desc'),
    sb('collection_categories?select=slug,section&published=eq.true'),
    sb('collection_items?select=id,name,category,section&published=eq.true'),
  ]);
  // A category page exists only while it holds something published (functions/_category.js).
  const filled = new Set(items.map((x) => x.category));
  const day = (d) => (d ? `<lastmod>${String(d).slice(0, 10)}</lastmod>` : '');
  const urls = [
    ...PAGES.map((p) => `<url><loc>${ORIGIN}${p}</loc></url>`),
    ...posts.map((p) => `<url><loc>${ORIGIN}${UNUrls.post(p)}</loc>${day(p.updated_at || p.created_at)}</url>`),
    ...cats.filter((c) => filled.has(c.slug)).map((c) => `<url><loc>${ORIGIN}${UNUrls.category(c)}</loc></url>`),
    ...items.map((x) => `<url><loc>${ORIGIN}${UNUrls.piece(x)}</loc></url>`),
  ];
  return new Response(`<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n${urls.join('\n')}\n</urlset>\n`,
    { headers: { 'Content-Type': 'application/xml; charset=utf-8', 'Cache-Control': 'public, max-age=900' } });
}
