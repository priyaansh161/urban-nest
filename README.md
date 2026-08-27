# Urban Nest

Home décor storefront for the Indian market — https://storeurbannest.netlify.app

Visitors walk through rooms rendered in 3D, open individual pieces and turn
them over, and read articles. Everything a visitor sees is either a static
page in this folder or a row in Supabase. There is an admin panel at
`/admin/` for editing the content without touching code.

This file is written for a developer who has never seen the project. If you
are picking this up cold, read **Architecture** and **Deploying** first — the
rest can wait until you need it.

---

## Running it locally

There is no build step and nothing to install.

```
npx serve .
```

Then open http://localhost:3000. The admin is at
http://localhost:3000/admin/login.html.

That is the whole setup. The pages are plain HTML with inline `<style>` and
`<script>`; open one in an editor and it is all there.

**Local dev runs against the live Supabase database.** There is no separate
staging data. Editing a product in the local admin changes the real site
immediately. Be careful.

One local-only quirk: `npx serve` redirects `foo.html` to `/foo` and drops
the query string doing it. Netlify does not. If you are testing something
that reads `location.search` (the collection page does), test against the
extensionless path locally, or against the deployed site.

---

## Architecture

Vanilla HTML, CSS and JavaScript. No framework, no bundler, no dependencies
at runtime beyond two CDN scripts (Supabase, and `<model-viewer>` /
`<spline-viewer>` on pages showing 3D). This is deliberate: the site should
still open and run in ten years without a toolchain to resurrect.

Each page is self-contained — its own styles and scripts live in the file.
That means there is duplication (see **Known rough edges**), but it also
means any page can be understood in isolation without tracing imports.

### Where things live

| Path | What it is |
|---|---|
| `index.html` | Homepage — hero, rooms, collection strip, contact |
| `collection.html` | Product catalogue: category tiles, then pieces, then a 3D detail sheet |
| `bathroom/kitchen/bedroom.html` | The 3D room walkthroughs (Spline scenes with hotspots) |
| `community.html` | "The Nest Edit" — articles, rendered from plain text by `formatBody()` |
| `card.html` | A digital visiting card for sharing the site personally |
| `about.html`, `join.html` | Static pages |
| `admin/` | The content panel — one page per content type |
| `supabase.js` | Database credentials and the `db` client. Loaded by every page that reads data |
| `tools/` | Local-only scripts. Never deployed |
| `images/`, `models/` | Assets. Subfolders are working material and do not ship |

### Data

All content is in Supabase (project `ifwxgwvsyispkaxzbstg`). The anon key in
`supabase.js` is public by design — it is meant to be in client code, and
row-level security is what actually protects writes.

Tables in use:

- `collection_items` — products; `collection_categories` — their groupings
- `nest_posts` — articles
- `spline_scenes` — the 3D room scenes; `room_products` — hotspot dots placed on them
- `feedback` — visitor messages
- `subscribers` — mailing list

**Content changes do not need a deploy.** Anything edited in the admin —
products, articles, photos, 3D models — is live the moment it is saved.
Deploying is only for changes to the pages themselves.

### The admin

`admin/auth.js` gates every admin page (`requireAuth()`); `admin/config.js`
holds its configuration. Beyond the CRUD screens there are three tools that
generate things rather than store them:

- **`social.html` (Reel Studio)** — builds Instagram reels as real MP4s by
  drawing to a `<canvas>` at 1080×1920 and recording it with `MediaRecorder`.
  Six templates share one engine; each supplies scenes as
  `{ secs, draw(t, dur) }` and the engine never knows what a scene contains.
  Anything that animates on its own (a spinning product, a Spline room) is
  captured to still frames first, because a live WebGL canvas cannot be read
  reliably frame by frame.
- **`article-card.html`** — composites a Nest post into an Instagram feed
  image, and drafts the caption text.
- **`caption.html`** — caption and hashtag helper.

---

## Deploying

The site is **not** connected to GitHub. Pushing does nothing. Deploys are
manual, through the Netlify CLI:

```
node tools/build-site.mjs
netlify deploy --prod --dir dist
```

### Two things that will bite you

**1. Never `netlify deploy --dir .`** — that publishes the entire project
folder, including hundreds of megabytes of raw 3D exports and unedited
photographs. It has happened. Netlify reads neither `.gitignore` nor
`.netlifyignore`, so `tools/build-site.mjs` exists to assemble a `dist/`
folder from an **allow list**. If a new file type does not appear on the live
site, it is because it is not in the `RULES` array at the top of that script.

**2. Deploys are metered and the owner's credits are limited.** Batch changes
and deploy once. Git commits are free and do not trigger anything — commit
freely, deploy sparingly. Never deploy just to see whether something works;
serve `dist/` locally and check there first.

Comparing local files to the live site byte-for-byte will always show a
difference — Netlify rewrites HTML on the way out, injecting its own meta
tags and converting links to pretty URLs. To check whether something is
deployed, compare the specific tag or content you care about, not a checksum.

`DEPLOY.txt` covers the same ground in non-technical language for the owner.

---

## Known rough edges

Honest list, in the order worth fixing:

1. **The admin sidebar is copy-pasted into all 10 admin pages.** Adding one
   nav link means editing nine files. Extracting it into a shared include is
   the single highest-value cleanup here.
2. **The colour palette is redeclared in 16 files.** Changing a brand colour
   is a 16-file edit where missing one leaves a page subtly wrong.
3. **`bathroom.html`, `kitchen.html` and `bedroom.html` are ~92% identical** —
   about 51 differing lines out of 670. They could be one page that reads the
   room from the URL.
4. **`admin/social.html` is ~2,000 lines.** Well sectioned internally, but
   large.
5. **No automated tests.** Changes are verified by loading the page. Bear
   this in mind before any large refactor — items 1–3 are exactly the kind of
   change that introduces invisible breakage, so do them one at a time and
   check each.

None of these stop the site working; they make edits cost more than they
should.

## Things that look like bugs but are not

- **Spline Scene Tour in Reel Studio falls back to a cover photo.** Reading
  the Spline viewer's canvas returns blank frames on every scene tested — it
  runs with `preserveDrawingBuffer: false` and exposes no screenshot API. The
  capture code is kept in case a future viewer version behaves differently.
- **`models/` is not deployed.** Every 3D listing stores an absolute Supabase
  Storage URL, so nothing on the site requests a `.glb` from Netlify. The
  files are kept in the repo as a backup of what is in Supabase.
- **Reel Studio stops if the browser tab goes to the background.** A canvas
  does not render there, so the run is abandoned deliberately rather than
  producing a broken video.
