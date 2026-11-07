/* /collection/<slug> and /essentials/<slug>: a category and its pieces as a
 * page of its own. See functions/_seo.js. A category that is hidden, or has
 * nothing published in it, is not found, the same as on the Collection page. */
import { sb, page, notFound, esc, clip, pieceCard, UNUrls, ORIGIN } from './_seo.js';
import { CATEGORY_SEO } from './_category-seo.js';

export async function categoryPage(ctx, section) {
  const slug = String(ctx.params.slug || '').toLowerCase();
  const [cat] = await sb(`collection_categories?select=*&slug=eq.${encodeURIComponent(slug)}&section=eq.${section}&published=eq.true&limit=1`);
  if (!cat) return notFound(ctx);
  const items = await sb(`collection_items?select=id,name,image_url,price,model_url&published=eq.true&category=eq.${encodeURIComponent(slug)}&order=sort_order.asc,name.asc`);
  if (!items.length) return notFound(ctx);

  const home = section === 'essentials' ? 'Essentials' : 'The Collection';
  const path = UNUrls.category(cat);
  const with3d = items.filter((x) => x.model_url).length;
  const seo = CATEGORY_SEO[cat.slug];
  return page(ctx, {
    path, title: seo ? seo.title : `${cat.name}: ${home}`,
    description: seo ? seo.description : clip(cat.about || cat.summary || cat.name, 158),
    image: cat.hero_image_url || cat.tile_image_url || items[0].image_url,
    tag: `<a href="/${section}" style="color:inherit;text-decoration:none">${esc(home.toUpperCase())}</a>`,
    h1: cat.name,
    sub: esc(cat.summary || ''),
    main: `<div class="sv-in">
      ${seo ? `<p class="sv-cat-about">${esc(seo.intro)}</p>` : ''}
      ${cat.about ? `<p class="sv-cat-about">${esc(cat.about)}</p>` : ''}
      <div class="sv-btns"><a class="sv-btn" href="/${section}?c=${encodeURIComponent(cat.slug)}">${with3d ? 'Explore them in 3D' : 'Open in the ' + esc(home.replace('The ', ''))}</a></div>
      <h2 class="sv-h">${items.length} ${items.length === 1 ? 'piece' : 'pieces'}</h2>
      <div class="sv-grid">${items.map((x) => pieceCard(x)).join('')}</div>
    </div>`,
    jsonld: {
      '@context': 'https://schema.org', '@type': 'CollectionPage', name: cat.name, url: ORIGIN + path,
      mainEntity: { '@type': 'ItemList', itemListElement: items.map((x, i) => ({ '@type': 'ListItem', position: i + 1, url: ORIGIN + UNUrls.piece(x), name: x.name })) },
    },
  });
}
