/* /piece/<words>-<id8>: one piece's own address. It answers with the real Collection / Essentials page, opened
 * on that piece inside its category (see functions/_app.js), with the piece's own title, description and
 * Product data for search engines.
 * The last eight characters are the start of the piece's id, which finds it; the words are for people and
 * search. If the name has changed since a link was made, the old address moves to the new one. */
import { sb, notFound, redirect, esc, img, clip, liveBuyLink, priceNumber, UNUrls, ORIGIN, shortName } from '../_seo.js';
import { appPage } from '../_app.js';

export async function onRequestGet(ctx) {
  const slug = String(ctx.params.slug || '').toLowerCase();
  const m = slug.match(/-([0-9a-f]{8})$/);
  if (!m) return notFound(ctx);
  const lo = `${m[1]}-0000-0000-0000-000000000000`, hi = `${m[1]}-ffff-ffff-ffff-ffffffffffff`;
  const [it] = await sb(`collection_items?select=*&published=eq.true&id=gte.${lo}&id=lte.${hi}&limit=1`);
  if (!it) return notFound(ctx);
  const path = UNUrls.piece(it);
  if (path !== '/piece/' + slug) return redirect(path);

  const [cat] = it.category ? await sb(`collection_categories?select=slug,name,section&slug=eq.${encodeURIComponent(it.category)}&published=eq.true&limit=1`) : [];
  const section = it.section === 'essentials' ? 'essentials' : 'collection';
  const buy = liveBuyLink(it);
  const photos = [it.image_url].concat(Array.isArray(it.gallery) ? it.gallery : []).filter(Boolean);
  const specs = Array.isArray(it.specs) ? it.specs.filter((s) => Array.isArray(s) && s[0] && s[1]) : [];
  const description = clip(it.description || `${it.name}. ${it.price || ''} Seen in 3D at Urban Nest.`, 158);
  const price = priceNumber(it.price);

  return appPage(ctx, {
    section, path, target: `/${section}?c=${encodeURIComponent(it.category || '')}&p=${it.id}`,
    title: shortName(it.name), description, image: it.image_url, ogType: 'product',
    staticHtml: `<h1>${esc(it.name)}</h1>` +
      (it.price ? `<p>${esc(it.price)}</p>` : '') +
      (it.description ? `<p>${esc(it.description)}</p>` : '') +
      (specs.length ? `<ul>${specs.map((s) => `<li>${esc(s[0])}: ${esc(s[1])}</li>`).join('')}</ul>` : '') +
      (cat ? `<p><a href="${esc(UNUrls.category(cat))}">More from ${esc(cat.name)}</a></p>` : ''),
    jsonld: {
      '@context': 'https://schema.org', '@type': 'Product',
      name: it.name, description: it.description || undefined,
      image: photos.slice(0, 5).map((u) => img(u, 1200)),
      category: cat ? cat.name : undefined, url: ORIGIN + path,
      offers: price ? { '@type': 'Offer', price, priceCurrency: 'INR', availability: 'https://schema.org/InStock', url: buy || ORIGIN + path } : undefined,
    },
  });
}
