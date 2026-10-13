# Instagram Insights puller — one-time setup

`tools/ig-insights.mjs` pulls views, reach, saves, shares and average watch time for
every Urban Nest post into `insights/ig-posts.csv`. It reads nothing but our own
account. Setup is about twenty minutes of clicking, once.

## What you need first

- The Instagram account must be a **Business or Creator** account
  (Instagram → Settings → Account type).
- It must be **linked to a Facebook Page**. Any page will do; make one called
  "Urban Nest" if there isn't one. Instagram → Settings → Linked accounts.

## 1. Make a Meta app

1. Go to <https://developers.facebook.com/apps> and log in with the Facebook account
   that owns the Page.
2. **Create App** → use case **Other** → type **Business** → name it `Urban Nest Insights`.
3. In the app dashboard, **Add product → Instagram Graph API**.

## 2. Get a token

1. Open the **Graph API Explorer**: <https://developers.facebook.com/tools/explorer>
2. Top right, select your app.
3. **Add permissions** — tick these four:
   - `instagram_basic`
   - `instagram_manage_insights`
   - `pages_show_list`
   - `pages_read_engagement`
4. **Generate Access Token** and approve the dialog. You now have a token that
   expires in about an hour.
5. Swap it for a long-lived one (60 days) at the
   **Access Token Debugger**: <https://developers.facebook.com/tools/debug/accesstoken>
   → paste the token → **Debug** → **Extend Access Token** → copy the new one.

## 3. Find the Instagram account id

In the Graph API Explorer, with the long-lived token selected, run:

```
me/accounts?fields=instagram_business_account,name
```

The response has your Page and an `instagram_business_account.id` — a long number.
That is the `userId`.

## 4. Save the credentials

Create `tools/.ig-credentials.json`:

```json
{
  "token": "PASTE_THE_LONG_LIVED_TOKEN",
  "userId": "PASTE_THE_INSTAGRAM_BUSINESS_ACCOUNT_ID"
}
```

This file is gitignored and must never be committed.

## 5. Run it

```bash
node tools/ig-insights.mjs --show
```

It writes `insights/ig-posts.csv` and prints the reels sorted by views.

## Using it

- Re-run **weekly**, not just after posting — reels keep earning views for weeks, and
  the script refreshes the numbers on rows already in the file.
- Two columns are yours to fill in by hand: **song** and **trending_y_n**. Meta does
  not expose the audio on your own posts through the API. The script preserves
  whatever you type there across runs, so fill them in once per post.
- The token expires every 60 days. When the script starts erroring about an invalid
  token, repeat step 2.

## What to look at

Not views. Views follow audio. The columns that tell you whether the *content*
worked are **saves** and **shares** per reach, and **average watch time** against the
reel's length. A reel with lower views but a higher watch-through is the better reel,
and is the one worth making more of.
