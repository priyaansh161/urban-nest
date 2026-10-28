/* /piece/<words>-<id8>: one piece as a page of its own. See functions/_seo.js.
 * The last eight characters are the start of the piece's id, which finds it;
 * the words are for people and search. If the name has changed since a link
 * was made, the old address moves to the new one. */
import { sb, page, notFound, redirect, esc, img, clip, pieceCard, liveBuyLink, priceNumber, UNUrls, ORIGIN } from '../_seo.js';

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
  const more = it.category ? await sb(`collection_items?select=id,name,image_url,price,model_url&published=eq.true&category=eq.${encodeURIComponent(it.category)}&id=neq.${it.id}&order=sort_order.asc,name.asc&limit=8`) : [];
  const section = it.section === 'essentials' ? 'essentials' : 'collection';
  const buy = liveBuyLink(it);
  const photos = [it.image_url].concat(Array.isArray(it.gallery) ? it.gallery : []).filter(Boolean);
  const specs = Array.isArray(it.specs) ? it.specs.filter((s) => Array.isArray(s) && s[0] && s[1]) : [];
  const interactive = `/${section}?c=${encodeURIComponent(it.category || '')}&p=${it.id}`;
  const description = clip(it.description || `${it.name}. ${it.price || ''} Seen in 3D at Urban Nest.`, 158);
  const price = priceNumber(it.price);

  const stage = it.model_url
    ? `<model-viewer src="${esc(it.model_url)}" poster="${esc(img(it.image_url, 900))}" alt="${esc(it.name)}" camera-controls auto-rotate shadow-intensity="1" touch-action="pan-y" loading="eager"></model-viewer><div class="sv-pc-hint">DRAG TO TURN</div>`
    : (it.image_url ? `<img src="${esc(img(it.image_url, 1100))}" alt="${esc(it.name)}" fetchpriority="high"/>` : '');

  return page(ctx, {
    path, title: it.name, description, image: it.image_url, ogType: 'product',
    tag: `<a href="/${section}" style="color:inherit;text-decoration:none">${section === 'essentials' ? 'ESSENTIALS' : 'THE COLLECTION'}</a>` +
      (cat ? ` · <a href="${esc(UNUrls.category(cat))}" style="color:inherit;text-decoration:none">${esc(cat.name.toUpperCase())}</a>` : ''),
    h1: it.name,
    main: `<div class="sv-in">
      <div class="sv-pc">
        <div>
          <div class="sv-pc-stage">${stage}</div>
          ${photos.length > 1 ? `<div class="sv-pc-thumbs">${photos.slice(0, 8).map((u, i) => `<img src="${esc(img(u, 240))}" alt="${esc(it.name)}, photo ${i + 1}" loading="lazy" decoding="async"/>`).join('')}</div>` : ''}
        </div>
        <div>
          ${it.price ? `<div class="sv-pc-price">${esc(it.price)}</div>` : ''}
          ${it.description ? `<p class="sv-pc-desc">${esc(it.description)}</p>` : ''}
          <div class="sv-btns">
            ${buy ? `<a class="sv-btn" href="${esc(buy)}" target="_blank" rel="noopener sponsored nofollow">Shop on Amazon →</a>` : ''}
            <a class="sv-btn ${buy ? 'sv-ghost' : ''}" href="${esc(interactive)}">${it.model_url ? 'Open in the 3D viewer' : 'See it in the Collection'}</a>
          </div>
          ${specs.length ? `<table class="sv-pc-specs">${specs.map((s) => `<tr><th>${esc(s[0])}</th><td>${esc(s[1])}</td></tr>`).join('')}</table>` : ''}
          ${buy ? `<p class="sv-pc-note">Sold and delivered by Amazon. Urban Nest may earn a small commission if you buy through this link, at no cost to you.</p>` : ''}
        </div>
      </div>
      ${more.length ? `<h2 class="sv-h">More from ${esc(cat ? cat.name : 'the Collection')}</h2><div class="sv-grid">${more.map((x) => pieceCard(x, cat && cat.name)).join('')}</div>` : ''}
    </div>`,
    scripts: it.model_url ? '<script type="module" src="https://unpkg.com/@google/model-viewer@3.5.0/dist/model-viewer.min.js"></script>' : '',
    jsonld: {
      '@context': 'https://schema.org', '@type': 'Product',
      name: it.name, description: it.description || undefined,
      image: photos.slice(0, 5).map((u) => img(u, 1200)),
      category: cat ? cat.name : undefined, url: ORIGIN + path,
      offers: price ? { '@type': 'Offer', price, priceCurrency: 'INR', availability: 'https://schema.org/InStock', url: buy || ORIGIN + path } : undefined,
    },
  });
}
