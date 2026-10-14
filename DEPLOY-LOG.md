# Deploy log

Every time the site goes live. New rows are added automatically by
`node tools/deploy.mjs "what changed"`: always deploy that way.

Hosting moved from Netlify to **Cloudflare Pages** on 17 Sept 2026. Deploys are
free there (500 a month), so this log is for knowing what went live and when.
Each Cloudflare deployment keeps its own address, which still serves that exact
version, so you can compare before and after.

The rows before `tools/deploy.mjs` existed were filled in afterwards from
`wrangler pages deployment list`; their times are approximate.

| Date | Time (IST) | Commit | What changed | Deployment |
|---|---|---|---|---|
| 2026-09-17 | ~12:30 | 37c51d9 | NETLIFY (last deploy there): Nest Studio, designer portfolios, enquiries, one-step invites, admin colours; also published earlier commits (domain move, light mode, share buttons, search basics) | Netlify deploy 6aab6fedc2c3da1ded9fe40b |
| 2026-09-17 | ~13:00 | 477a26e | First Cloudflare deploy (test address only, before the domain moved) | https://a6cbe1da.storeurbannest.pages.dev |
| 2026-09-17 | ~13:15 | 477a26e | Redeploy after the 4 secrets were added | https://4a945da1.storeurbannest.pages.dev |
| 2026-09-17 | ~15:00 | cee3a1b | Domain now on Cloudflare; sitemap and robots.txt for Cloudflare's addresses | https://9d04081d.storeurbannest.pages.dev |
| 2026-09-17 | ~15:15 | cee3a1b | Redeploy after rotating the Supabase secret key | https://099ccd32.storeurbannest.pages.dev |
| 2026-09-17 | ~17:00 | b4a9f6f | Admin sidebar scrolls, Sign Out pinned | https://9e9c2006.storeurbannest.pages.dev |
| 2026-09-17 | ~17:03 | e887e5b | Forgot-password link on the admin sign-in | https://0ea8e5b7.storeurbannest.pages.dev |
| 2026-09-17 | ~17:06 | a0d6330 | Clean email logo (images/email-logo.png) | https://540690bc.storeurbannest.pages.dev |
| 2026-09-17 | ~17:25 | 5fa18c0 | Branded not-found page (real 404) | https://f863d9b2.storeurbannest.pages.dev |
| 2026-09-17 | 20:57 | cfba91a | Join the Nest landing page at /nest (the "uncommitted" change was only the deploy script fix) | https://3513f437.storeurbannest.pages.dev |
| 2026-09-17 | 21:00 | 6dc7491 | WhatsApp preview tags on /nest | https://d4e0e852.storeurbannest.pages.dev |
| 2026-09-18 | 12:16 | 0d415db | Creator sign-in link in footers + under The Nest Edit articles | https://07c8e56c.storeurbannest.pages.dev |
| 2026-09-18 | 16:52 | 68ae4f0 | Sort and price filters on Collection and Essentials category pages | https://e54416b4.storeurbannest.pages.dev |
| 2026-09-25 | 21:52 | 077d04c | Reel Studio: 3D capture waits for the model to be drawn, loading overlay, Spline viewer loads only for Spline Tour | https://0f949c77.storeurbannest.pages.dev |
| 2026-10-05 | 17:51 | 63f4184 | Rounded corners site-wide; interactive homepage (collection swipe rail, swipe deck, Nest Edit row, contact buttons); card-by-card Collection on phones; two-finger 3D touch fix in rooms | https://95d14080.storeurbannest.pages.dev |
| 2026-10-05 | 19:08 | 022ea4f | Lighter photos (Supabase resizing), depth shadows, flip cards, footer hello, Nest Edit above philosophy, bigger gold Spaces heading, snappier phone cards + Essentials card view, rounded admin and studio | https://a7e4bb1a.storeurbannest.pages.dev |
| 2026-10-05 | 23:12 | ae5c5a3 | Flip card copy: card 2 is now a real question and answer; card 1's answer says why | https://9fb5a253.storeurbannest.pages.dev |
| 2026-10-05 | 23:17 | d76c4bb | Flip card 1: answer stays with the sofa, not the bathroom | https://9468639f.storeurbannest.pages.dev |
| 2026-10-05 | 23:28 | 98427f8 | Warm hero and spaces photos, no thin white lines, panels on listings, rail arrows fixed | https://bcf80775.storeurbannest.pages.dev |
| 2026-10-07 | 09:53 | 6fd1a23 | About page header matches the others (grid, two-line title on the left); phone sections aligned | https://f36a71a5.storeurbannest.pages.dev |
| 2026-10-07 | 11:16 | c47514c | Quote bands: warm on-palette photos matched to each shloka (tea, teal plaster, teal sconce, lantern) | https://11c19013.storeurbannest.pages.dev |
| 2026-10-07 | 11:30 | f59b3cc | Quote bands become narrower centred panels (rounded, with shadow) | https://6b44ee07.storeurbannest.pages.dev |
| 2026-10-07 | 11:50 | 3ada325 | Quote bands: square, no shadow, narrower and shorter, tighter lines | https://ec7075fd.storeurbannest.pages.dev |
| 2026-10-07 | 11:54 | a190d20 | Version-stamped asset URLs so changes show immediately (no stale theme.css or photos); service worker v3 | https://6f15f40a.storeurbannest.pages.dev |
| 2026-10-07 | 12:02 | 1c2a889 | Quote bands: new close-up photos matched to each shloka (chandelier, amber jars, sunlit vase, teal vases, candle) | https://a7b090f4.storeurbannest.pages.dev |
| 2026-10-12 | 11:04 | 32476ea | Photo galleries for no-3D pieces (festive category); admin More Photos strip; footer 3D wording | https://ef943ecc.storeurbannest.pages.dev |
| 2026-10-12 | 11:23 | 0f1c5c2 | Redeploy to switch on Cloudflare Web Analytics (no site changes) | https://fee6f65c.storeurbannest.pages.dev |
| 2026-10-12 | 12:52 | b12711a | Admin: full-size photo viewer in the Collection item form | https://e150f1b6.storeurbannest.pages.dev |
| 2026-10-12 | 15:02 | 853bf3c | Admin Collection: cover photo preview under the Image URL field | https://cdf8f7f1.storeurbannest.pages.dev |
| 2026-10-12 | 15:07 | 642b44d | Quote bands: option B (rounded corners + soft shadow) | https://9ee068e0.storeurbannest.pages.dev |
| 2026-10-12 | 15:32 | abf829d | Creators page live (/creators application form, links from Nest Edit and studio, applications in admin) | https://93dcb22e.storeurbannest.pages.dev |
| 2026-10-12 | 15:57 | 74e89f1 | Rooms: view chooser shows display names, not MK working names | https://c21cd94e.storeurbannest.pages.dev |
| 2026-10-13 | 14:37 | 4832923 | photo gallery for pieces with no 3D model | https://d91feb56.storeurbannest.pages.dev |
| 2026-10-14 | 09:00 | 50eee17 | Link previews on every public page | https://135925b1.storeurbannest.pages.dev |
| 2026-10-14 | 09:36 | 6298384 (+ uncommitted changes) | Homepage hero: shoppable rooms (living room + bedroom) | https://a356ee7e.storeurbannest.pages.dev |
| 2026-10-14 | 09:47 | 6727c77 (+ uncommitted changes) | Homepage hero: third room, the kitchen (Essentials) | https://ffd35063.storeurbannest.pages.dev |
| 2026-10-14 | 09:56 | c44d228 (+ uncommitted changes) | Homepage hero: fourth room, the bath (Essentials) | https://2f53898c.storeurbannest.pages.dev |
| 2026-10-14 | 10:06 | 62bd85e (+ uncommitted changes) | Homepage hero: fifth room, the lounge | https://ff441a8e.storeurbannest.pages.dev |
| 2026-10-14 | 10:15 | 50a2331 (+ uncommitted changes) | Homepage hero: sixth room, the guest room; tabs wrap on phones | https://18468c0e.storeurbannest.pages.dev |
| 2026-10-14 | 10:30 | f798090 (+ uncommitted changes) | Homepage hero: stronger cursor spotlight (warm glow, room dims) | https://2d78c003.storeurbannest.pages.dev |
| 2026-10-14 | 10:33 | 1f28a81 (+ uncommitted changes) | Homepage hero: lighter shadow outside the spotlight | https://e99308c9.storeurbannest.pages.dev |
