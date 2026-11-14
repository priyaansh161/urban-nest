/* /collection/<slug> and /essentials/<slug>: a category's own address. It answers with the real Collection /
 * Essentials page, opened on that category (see functions/_app.js), with the category's own title, description
 * and structured data for search engines. A category that is hidden, or has nothing published in it, is not
 * found, the same as on the Collection page. */
import { sb, notFound, esc, clip, UNUrls, ORIGIN, shortName } from './_seo.js';
import { appPage } from './_app.js';
import { CATEGORY_SEO } from './_category-seo.js';

export async function categoryPage(ctx, section) {
  const slug = String(ctx.params.slug || '').toLowerCase();
  const [cat] = await sb(`collection_categories?select=*&slug=eq.${encodeURIComponent(slug)}&section=eq.${section}&published=eq.true&limit=1`);
  if (!cat) return notFound(ctx);
  const items = await sb(`collection_items?select=id,name,image_url,price,model_url&published=eq.true&category=eq.${encodeURIComponent(slug)}&order=sort_order.asc,name.asc`);
  if (!items.length) return notFound(ctx);

  const home = section === 'essentials' ? 'Essentials' : 'The Collection';
  const path = UNUrls.category(cat);
  const seo = CATEGORY_SEO[cat.slug];
  return appPage(ctx, {
    section, path, target: `/${section}?c=${encodeURIComponent(cat.slug)}`,
    title: seo ? seo.title : `${cat.name}: ${home}`,
    description: seo ? seo.description : clip(cat.about || cat.summary || cat.name, 158),
    image: cat.hero_image_url || cat.tile_image_url || items[0].image_url,
    staticHtml: `<h1>${esc(cat.name)}</h1>` +
      (cat.summary ? `<p>${esc(cat.summary)}</p>` : '') +
      (seo ? `<p>${esc(seo.intro)}</p>` : '') +
      (cat.about ? `<p>${esc(cat.about)}</p>` : '') +
      `<h2>${items.length} ${items.length === 1 ? 'piece' : 'pieces'}</h2><ul>` +
      items.map((x) => `<li><a href="${esc(UNUrls.piece(x))}">${esc(shortName(x.name))}</a>${x.price ? ' · ' + esc(x.price) : ''}</li>`).join('') + '</ul>',
    jsonld: {
      '@context': 'https://schema.org', '@type': 'CollectionPage', name: cat.name, url: ORIGIN + path,
      mainEntity: { '@type': 'ItemList', itemListElement: items.map((x, i) => ({ '@type': 'ListItem', position: i + 1, url: ORIGIN + UNUrls.piece(x), name: x.name })) },
    },
  });
}
