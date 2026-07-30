-- A scene needs two names: the one you file it under and the one visitors read.
--   name         — internal, e.g. "Bathroom MK2". Stays in the admin.
--   display_name — public, e.g. "The Stone Bath". Shown on the site.
--   cover_url    — the photo used for its tile on the homepage.
--
-- display_name and cover_url are optional. Where they are empty the site falls
-- back to the internal name and a stock photo for that room, so nothing looks
-- broken before they are filled in.
alter table spline_scenes add column if not exists display_name text;
alter table spline_scenes add column if not exists cover_url    text;
