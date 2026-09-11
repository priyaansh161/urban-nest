/* The service worker — the piece that makes the site installable as an app.
 *
 * Deliberately cautious. Products, prices, stock and Nest articles live in
 * Supabase and change without a deploy, so nothing here may show a visitor
 * yesterday's shop:
 *
 *   pages, scripts, manifest   network first. The cached copy is used only
 *                              when there is no network at all; a page never
 *                              opened before falls back to offline.html.
 *   images, .splinecode        served from cache and refreshed behind the
 *                              scenes, since they only change with a deploy.
 *   admin, Netlify functions,  not touched. Neither is anything on another
 *   other hosts                host — Supabase, Spline, Google Fonts,
 *                              Razorpay — which the browser handles as usual.
 *
 * Changing how this file behaves? Bump VERSION. Old caches are dropped when
 * the new worker takes over. netlify.toml serves this file with no-cache so
 * phones pick up a new one on their next visit.
 */
const VERSION = 'v1';
const CACHE = `un-${VERSION}`;
const PRECACHE = ['/offline.html', '/favicon.png', '/images/app-icon-192.png'];

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE).then(c => c.addAll(PRECACHE)).then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys()
      .then(keys => Promise.all(keys.filter(k => k.startsWith('un-') && k !== CACHE).map(k => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', event => {
  const req = event.request;
  if (req.method !== 'GET') return;
  // Partial (Range) requests are the browser's business: a cached full file
  // handed back for a byte range, or a 206 fragment cached as the whole
  // file, would corrupt media and 3D downloads.
  if (req.headers.has('range')) return;

  const url = new URL(req.url);
  if (url.origin !== self.location.origin) return;
  if (url.pathname.startsWith('/admin/') || url.pathname.startsWith('/.netlify/')) return;

  if (req.mode === 'navigate' || /\.(html|js|webmanifest)$/.test(url.pathname)) {
    event.respondWith(networkFirst(event, req));
  } else if (/\.(png|jpe?g|webp|svg|splinecode)$/.test(url.pathname)) {
    event.respondWith(cacheFirstThenRefresh(event, req));
  }
});

/* Only plain, same-origin, un-redirected successes are kept. A redirected
   response (e.g. /hello) handed back for a navigation is refused by the
   browser, so caching one would break that page offline rather than help. */
function keep(event, req, res) {
  if (res.ok && res.type === 'basic' && !res.redirected) {
    const copy = res.clone();
    event.waitUntil(caches.open(CACHE).then(c => c.put(req, copy)));
  }
  return res;
}

async function networkFirst(event, req) {
  try {
    return keep(event, req, await fetch(req));
  } catch {
    // ignoreSearch: collection.html?item=… opened offline still gets the
    // collection page it was last seen as, rather than the offline notice.
    const cached = await caches.match(req, { ignoreSearch: req.mode === 'navigate' });
    if (cached) return cached;
    if (req.mode === 'navigate') return caches.match('/offline.html');
    return Response.error();
  }
}

async function cacheFirstThenRefresh(event, req) {
  const cached = await caches.match(req);
  const fresh = fetch(req).then(res => keep(event, req, res));
  if (cached) {
    event.waitUntil(fresh.catch(() => {}));
    return cached;
  }
  return fresh;
}
