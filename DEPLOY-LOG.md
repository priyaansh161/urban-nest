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
| 2026-10-14 | 10:43 | 969cca8 (+ uncommitted changes) | Live /look page (Diwali edition); phone room drift resumes after 4s | https://0e45528b.storeurbannest.pages.dev |
| 2026-10-14 | 10:57 | 14b81f1 (+ uncommitted changes) | Tighter spacing between sections, site-wide | https://4ddc4416.storeurbannest.pages.dev |
| 2026-10-16 | 17:58 | 8676d10 (+ uncommitted changes) | Amazon link checker in admin + hide Amazon button for gone products | https://5e768639.storeurbannest.pages.dev |
| 2026-10-20 | 10:46 | 8676d10 (+ uncommitted changes) | Our take: Priyaansh's own rating + verdict on every product (admin forms, collection/essentials/room display) | https://c15e27a5.storeurbannest.pages.dev |
| 2026-10-20 | 10:54 | 8676d10 (+ uncommitted changes) | Admin: search products by name in Collection and room Products lists | https://007ee5db.storeurbannest.pages.dev |
| 2026-10-21 | 14:19 | 7111491 (+ uncommitted changes) | Squircle (Apple-style) corners, site-wide | https://09338456.storeurbannest.pages.dev |
| 2026-10-21 | 16:43 | e65850d (+ uncommitted changes) | Admin Collection: drafts tinted red and listed first | https://4bc21c31.storeurbannest.pages.dev |
| 2026-10-22 | 20:33 | e2aa902 (+ uncommitted changes) | Homepage and /look hero now opens on a random room each visit (never the same twice in a row) | https://5afb4c3f.storeurbannest.pages.dev |
| 2026-10-25 | 12:09 | c5b6b92 | Spaces: old Spline rooms taken down; rebuilt Quiet Bath live at /rooms/quiet-bath/ (own viewer, faster loading, caching) | https://1ec89e7f.storeurbannest.pages.dev |
| 2026-10-25 | 12:23 | 5d7aa12 | Quiet Bath: smaller one-line navigation hint on phones | https://daf236bd.storeurbannest.pages.dev |
| 2026-10-25 | 12:29 | d2c7133 | Quiet Bath: logo loader; Spiral Ribbed Vase taken off the cistern | https://f237cf1b.storeurbannest.pages.dev |
| 2026-10-25 | 23:19 | 589a98c | Sunday Bedroom 3D room live (Spaces + homepage tile, /bedroom redirect); Quiet Bath gets a fourth wall | https://e169dfe8.storeurbannest.pages.dev |
| 2026-10-26 | 12:15 | f7a44da | Rooms: swipe/arrow-key/arrow-button stepping between products (both rooms), bedroom Chandelier view + higher Overview, right nightstand without cup | https://e4c2c8cb.storeurbannest.pages.dev |
| 2026-10-26 | 12:55 | 0043806 | Sunday Bedroom tile gets its Gemini-styled cover photo | https://8e7fbb10.storeurbannest.pages.dev |
| 2026-10-28 | 13:45 | 16bcc23 | Nest Edit: all 14 articles from the database (built-in 7 migrated), em dashes removed | https://3aa1a030.storeurbannest.pages.dev |
| 2026-10-28 | 14:04 | 72e9028 | Own pages for every article, piece and category (+ live sitemap); copy clean-up; Amazon Associates disclosure; homepage join card | https://d297340c.storeurbannest.pages.dev |
| 2026-10-28 | 16:42 | b61234a (+ uncommitted changes) | Amazon seller line + disclosure wording; join card folds to corner button; phone scroll bar; hello@ email | https://46c4d482.storeurbannest.pages.dev |
| 2026-10-28 | 17:26 | 1fb4e92 (+ uncommitted changes) | Rooms: Dots toggle removed | https://26d8b497.storeurbannest.pages.dev |
| 2026-10-29 | 14:19 | 0eeb110 (+ uncommitted changes) | Rooms: fixed product viewpoints + arcing camera moves | https://373fcde0.storeurbannest.pages.dev |
| 2026-10-29 | 15:24 | 1680249 (+ uncommitted changes) | Rooms: fast preview then full-quality images | https://72d04ca4.storeurbannest.pages.dev |
| 2026-11-03 | 10:50 | 1680249 (+ uncommitted changes) | Sunday Bedroom: staging decor (breakfast tray with contact shadow, slippers, detailed snake plant), Qutub planter, Boxy wall shelf, Sunrise Mountain canvas, rebuilt charging dock, decluttered dresser | https://deda54c2.storeurbannest.pages.dev |
| 2026-11-03 | 16:11 | 1680249 (+ uncommitted changes) | Quiet Bath: CARTADEN mango wood stool + Soul & Scents Jasmine reed diffuser (Blender-built products), staging refresh (towels and candle on the stool, plastic bin, marble niche with labelled bottles, terry towels), poppy calla flowers, wider Shower view | https://5a8d99bb.storeurbannest.pages.dev |
| 2026-11-03 | 16:24 | 1680249 (+ uncommitted changes) | Quiet Bath: soft folded towels on the stool | https://c2eaabda.storeurbannest.pages.dev |
| 2026-11-03 | 16:51 | 1680249 (+ uncommitted changes) | Quiet Bath: the stool's dot pinned to its front rail (placements dotAt for placed products) | https://5edc2938.storeurbannest.pages.dev |
| 2026-11-05 | 16:02 | 1680249 (+ uncommitted changes) | SEO: fix price in product structured data (ranges no longer glued into one number); search-wording titles, descriptions and intro paragraph on 15 category pages | https://5457e2eb.storeurbannest.pages.dev |
| 2026-11-05 | 16:42 | 1680249 (+ uncommitted changes) | Room dots: smaller, teal, soft breathing glow (sunday-bedroom, quiet-bath) | https://91ecb8c6.storeurbannest.pages.dev |
| 2026-11-05 | 16:58 | 1680249 (+ uncommitted changes) | Admin: new Rooms editor (move pieces, dots, cards, add from Collection; saves to Storage, no deploy); Spline Scenes + 3D Products tabs removed from nav; room viewers load saved layout + dotAt | https://d14ff6fa.storeurbannest.pages.dev |
| 2026-11-05 | 17:17 | 1680249 (+ uncommitted changes) | Admin Rooms: simpler editing (drag piece, drag dot, arrows push into walls, keyboard arrows) | https://251988da.storeurbannest.pages.dev |
| 2026-11-05 | 19:22 | 1680249 (+ uncommitted changes) | Add Admitad/Mitgo ad-space verification meta tag to homepage head | https://c1c61c73.storeurbannest.pages.dev |
| 2026-11-05 | 21:14 | 1680249 (+ uncommitted changes) | Admin Rooms: picture picker for adding pieces, new pieces land where the camera looks (hang/wall aware), undo/redo, full screen | https://8b53cf04.storeurbannest.pages.dev |
| 2026-11-05 | 21:18 | 1680249 (+ uncommitted changes) | Admin Rooms: fix script crash (broken regex in thumbnail helper) that stopped the page opening | https://bbd18e38.storeurbannest.pages.dev |
| 2026-11-05 | 21:25 | 1680249 (+ uncommitted changes) | Rooms editor: new pieces land within 1.5 m in view, spread out; selection box shows through objects | https://7ace47e5.storeurbannest.pages.dev |
| 2026-11-05 | 21:32 | 1680249 (+ uncommitted changes) | Rooms editor: added pieces get a short card name plus the Collection description and details | https://42159d4b.storeurbannest.pages.dev |
| 2026-11-05 | 21:53 | 1680249 (+ uncommitted changes) | Rooms editor: fix piece list not refreshing when switching rooms | https://9c65579e.storeurbannest.pages.dev |
| 2026-11-05 | 22:04 | 1680249 (+ uncommitted changes) | India/US stores: country detection (/api/country), IN/US switch in the top bar, pieces not sold in the visitor's market show 'India only'/'US only' (market.js); Privacy has India and US versions | https://d495fb4b.storeurbannest.pages.dev |
| 2026-11-06 | 10:59 | 1680249 (+ uncommitted changes) | Phone: short names, sticky price + Shop bar in piece sheet, join card as button, finger-size taps; prices as rupee symbols; typo fixes in Collection data | https://b35a0dd7.storeurbannest.pages.dev |
| 2026-11-06 | 11:01 | 1680249 (+ uncommitted changes) | Phone: bigger IN/US tap targets | https://01c04a17.storeurbannest.pages.dev |
| 2026-11-06 | 11:02 | 1680249 (+ uncommitted changes) | Phone: keep IN/US widening off the narrowest phones | https://2a3bb6d6.storeurbannest.pages.dev |
| 2026-11-06 | 11:57 | 1680249 (+ uncommitted changes) | Phone: undo the IN/US widening, it pushed the menu button off-screen on some pages | https://59fefc99.storeurbannest.pages.dev |
| 2026-11-06 | 12:04 | 1680249 (+ uncommitted changes) | Phone: category intro folds to 3 lines, small labels 10.5px, narrowest-phone header | https://0e9a6636.storeurbannest.pages.dev |
| 2026-11-06 | 12:05 | 1680249 (+ uncommitted changes) | Phone: header fits 320px phones | https://14902761.storeurbannest.pages.dev |
| 2026-11-06 | 12:06 | 1680249 (+ uncommitted changes) | Phone: header fits 320px phones, part 2 | https://d8a33d46.storeurbannest.pages.dev |
| 2026-11-06 | 14:22 | 1680249 (+ uncommitted changes) | Hide the Heritage Lounge cards until /rooms/living-room/ is published | https://9df1bef6.storeurbannest.pages.dev |
| 2026-11-06 | 15:34 | 1680249 (+ uncommitted changes) | Heritage Lounge: third 3D room (rooms/living-room), Spaces + homepage cards | https://cc5c09f0.storeurbannest.pages.dev |
| 2026-11-06 | 16:06 | 1680249 (+ uncommitted changes) | Phone review: header margins and small toggles, landscape-first rooms with rotate prompt, 3D-first product sheet, search (Collection, Essentials, Nest Edit), Join button on every phone page, Essentials loading bug | https://1cb95e75.storeurbannest.pages.dev |
| 2026-11-06 | 17:13 | 1680249 (+ uncommitted changes) | Rooms: turn-phone note shows on every visit; Spaces back link follows touchend so it always presses | https://cd7ae1d7.storeurbannest.pages.dev |
| 2026-11-06 | 17:15 | 1680249 (+ uncommitted changes) | Phone product sheet back to a card (page visible around it); more room above Shop button | https://f133f92c.storeurbannest.pages.dev |
| 2026-11-06 | 22:24 | 1680249 (+ uncommitted changes) | Heritage Lounge v2: his Collection listings, sheesham table, navy walls, sofa fixes, phone viewer | https://d767a931.storeurbannest.pages.dev |
| 2026-11-07 | 00:05 | 1680249 (+ uncommitted changes) | Heritage Lounge v3: painting view, staging, new cushions, resized pieces, lamps moved, window detail | https://6ea7082f.storeurbannest.pages.dev |
| 2026-11-07 | 10:30 | a4d1f70 (+ uncommitted changes) | Deploy script now saves to GitHub after each deploy (no site change) | https://c9721f62.storeurbannest.pages.dev |
