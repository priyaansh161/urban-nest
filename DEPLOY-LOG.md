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
