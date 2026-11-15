/* /rooms/<room>/: the 3D room page itself, with search and share wording added on the way out.
 *
 * The room pages are published from the mocks/room-... folders by their own scripts, which would overwrite any edit made
 * to rooms/<room>/index.html. So the search title, description, canonical address and share picture live
 * here instead and are written into the page as it is served. The room itself is untouched.
 * Titles lead with what people search for ("bedroom decor ideas"), then the room's own name.
 * A room not listed here is served exactly as published.
 */
import { esc, ORIGIN } from '../../_seo.js';

const ROOMS = {
  'sunday-bedroom': {
    title: 'Bedroom Decor Ideas in 3D: The Sunday Bedroom',
    description: 'Bedroom decor ideas you can walk through in 3D: a calm bedroom in bouclé, oak and linen. Tap any piece to see what it is and what it costs.',
  },
  'quiet-bath': {
    title: 'Bathroom Decor Ideas in 3D: The Quiet Bath',
    description: 'Bathroom decor ideas you can walk through in 3D: marble, walnut and soft light. Tap any bathroom accessory in the room to see what it is and what it costs.',
  },
  'living-room': {
    title: 'Living Room Decor Ideas in 3D: The Heritage Lounge',
    description: 'Living room decor ideas you can walk through in 3D: ink-blue walls, cognac leather, rosewood and brass. Tap any piece to see what it is and what it costs.',
  },
  kitchen: {
    title: 'Kitchen Design Ideas in 3D: The Oak Kitchen',
    description: 'Kitchen design ideas you can walk through in 3D: oak tall units, charcoal-navy cabinets and white marble. Tap any piece on the counter to see what it is and what it costs.',
  },
};

export async function onRequestGet(ctx) {
  const room = String(ctx.params.room || '');
  const res = await ctx.env.ASSETS.fetch(new URL(`/rooms/${room}/`, ctx.request.url));
  const seo = ROOMS[room];
  if (!seo || !res.ok || !(res.headers.get('Content-Type') || '').includes('text/html')) return res;

  const url = `${ORIGIN}/rooms/${room}/`;
  const image = `${ORIGIN}/images/share-room-${room}.jpg`;
  const title = seo.title + ' · Urban Nest';
  const tags = [
    `<link rel="canonical" href="${url}"/>`,
    `<meta property="og:type" content="website"/>`,
    `<meta property="og:site_name" content="Urban Nest"/>`,
    `<meta property="og:title" content="${esc(title)}"/>`,
    `<meta property="og:description" content="${esc(seo.description)}"/>`,
    `<meta property="og:url" content="${url}"/>`,
    `<meta property="og:image" content="${image}"/>`,
    `<meta property="og:image:width" content="1200"/>`,
    `<meta property="og:image:height" content="630"/>`,
    `<meta name="twitter:card" content="summary_large_image"/>`,
  ].join('\n');

  const html = (await res.text())
    .replace(/<title>[\s\S]*?<\/title>/i, () => `<title>${esc(title)}</title>`)
    .replace(/<meta\s+name="description"[^>]*>/i, () => `<meta name="description" content="${esc(seo.description)}">`)
    .replace(/<link\s+rel="canonical"[^>]*>\s*/gi, '')
    .replace(/<meta\s+(property="og:|name="twitter:)[^>]*>\s*/gi, '')
    .replace(/<\/head>/i, () => tags + '\n</head>');

  const headers = new Headers(res.headers);
  headers.delete('Content-Length');
  return new Response(html, { status: res.status, headers });
}
