/* /edit/<slug>: one Nest Edit article as a page of its own. See functions/_seo.js. */
import { sb, page, notFound, redirect, esc, img, dateIN, clip, postCard, formatBody, UNUrls, ORIGIN, ORG } from '../_seo.js';

const COLS = 'id,slug,title,content,image_url,category,author,read_time,meta_description,excerpt,created_at,updated_at';

export async function onRequestGet(ctx) {
  const slug = decodeURIComponent(String(ctx.params.slug || '')).toLowerCase();
  let [p] = await sb(`nest_posts?select=${COLS}&published=eq.true&slug=eq.${encodeURIComponent(slug)}&limit=1`);
  // A post with no slug yet is reached by its id; one that has a slug moves there for good.
  if (!p && /^[0-9a-f-]{36}$/.test(slug)) {
    [p] = await sb(`nest_posts?select=${COLS}&published=eq.true&id=eq.${slug}&limit=1`);
    if (p && p.slug) return redirect(UNUrls.post(p));
  }
  if (!p) return notFound(ctx);

  const more = await sb(`nest_posts?select=id,slug,title,image_url,category,read_time&published=eq.true&id=neq.${p.id}&order=created_at.desc&limit=3`);
  const description = clip(p.meta_description || p.excerpt || p.content, 158);
  const author = p.author || 'Urban Nest';
  const category = p.category ? p.category.charAt(0).toUpperCase() + p.category.slice(1) : '';

  return page(ctx, {
    path: UNUrls.post(p), title: p.title, description, image: p.image_url, ogType: 'article',
    tag: `<a href="/community" style="color:inherit;text-decoration:none">THE NEST EDIT</a>${category ? ' · ' + esc(category.toUpperCase()) : ''}`,
    h1: p.title,
    sub: [esc(author), dateIN(p.created_at), esc(p.read_time || '')].filter(Boolean).join(' · '),
    main: `<div class="sv-in">
      <article class="sv-art">
        ${p.image_url ? `<img class="sv-art-img" src="${esc(img(p.image_url, 1440))}" alt="${esc(p.title)}" fetchpriority="high"/>` : ''}
        <div class="sv-art-body">${formatBody(p.content)}</div>
        <div class="sv-art-end">Written for The Nest Edit by ${esc(author)}.</div>
        <div class="sv-btns"><a class="sv-btn" href="/collection">Browse the Collection</a><a class="sv-btn sv-ghost" href="/community">All articles</a></div>
      </article>
      ${more.length ? `<h2 class="sv-h">More from The Nest Edit</h2><div class="sv-grid">${more.map(postCard).join('')}</div>` : ''}
    </div>`,
    jsonld: {
      '@context': 'https://schema.org', '@type': 'BlogPosting',
      headline: p.title, description, image: p.image_url ? [img(p.image_url, 1200)] : undefined,
      datePublished: p.created_at, dateModified: p.updated_at || p.created_at,
      author: author === 'Urban Nest Editorial' || author === 'Urban Nest' ? ORG : { '@type': 'Person', name: author },
      publisher: ORG, mainEntityOfPage: ORIGIN + UNUrls.post(p),
    },
  });
}
