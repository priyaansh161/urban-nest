-- ═══════════════════════════════════════════════════════════════
--  URBAN NEST — CATEGORIES FOR THE COLLECTION
--  Run once: Supabase Dashboard → SQL Editor → New Query → paste → Run
--
--  WHY: the Collection was one flat grid, and the category on an item
--  was a hard-coded list in the admin's markup. A category could not be
--  added without editing and deploying the site, and it carried nothing
--  but its own name — no photograph, no explanation of what it holds.
--
--  Categories are rows now. The Collection page opens on a tile per
--  category; a tile leads to that category's own page, with a hero
--  photograph and a paragraph above its pieces.
--
--  Items already carry collection_items.category as text. That column is
--  the link — a category's slug matches it — so nothing about the items
--  changes and no piece is orphaned. Whatever slugs are already in use
--  are seeded below as categories you can then rename and describe.
--
--  Safe to run more than once.
-- ═══════════════════════════════════════════════════════════════

create table if not exists collection_categories (
  id          uuid primary key default gen_random_uuid(),
  -- The slug is the join. It matches collection_items.category and it is
  -- what appears in the URL, so it is lower-case and hyphenated.
  slug        text not null unique,
  name        text not null,
  -- summary is the line on the tile; about is the paragraph on the
  -- category's own page. One is a label, the other is an introduction,
  -- and writing one to serve both makes it bad at each.
  summary     text,
  about       text,
  tile_image_url text,
  hero_image_url text,
  sort_order  int  default 0,
  published   boolean default true,
  created_at  timestamptz default now()
);

-- Re-runnable for a table that already exists from an earlier version.
alter table collection_categories add column if not exists summary        text;
alter table collection_categories add column if not exists about          text;
alter table collection_categories add column if not exists tile_image_url text;
alter table collection_categories add column if not exists hero_image_url text;
alter table collection_categories add column if not exists sort_order     int default 0;
alter table collection_categories add column if not exists published      boolean default true;

create index if not exists collection_categories_sort_idx
  on collection_categories (sort_order, name);

-- ── Seed from the categories already in use ────────────────────
-- Title-cased from the slug as a starting name. Rename them in the admin;
-- "living" becomes "Living Room" by hand, because no rule turns it into
-- that reliably and a wrong guess is worse than an obvious placeholder.
insert into collection_categories (slug, name, sort_order)
select distinct lower(trim(ci.category)),
       initcap(replace(lower(trim(ci.category)), '-', ' ')),
       0
from collection_items ci
where ci.category is not null and trim(ci.category) <> ''
on conflict (slug) do nothing;

-- ── Two to start with ──────────────────────────────────────────
-- Drafts, so nothing appears on the site until you have written the
-- summary and chosen the photographs in Admin → Collection → Categories.
-- Delete this block if you would rather start from nothing.
--
-- Note the chandeliers already on the site are filed under "lighting" and
-- stay there: creating this category does not move them. Re-file each piece
-- from the item form, or rename the lighting category instead.
insert into collection_categories (slug, name, summary, sort_order, published) values
  ('chandeliers', 'Chandeliers',
   'Crystal, brass and glass, modelled close enough to count the drops.', 10, false),
  ('sculptures',  'Sculptures',
   'Objects that earn a surface of their own.', 20, false)
on conflict (slug) do nothing;

-- ── Row level security ─────────────────────────────────────────
alter table collection_categories enable row level security;

do $$
declare
  admin_test text;
begin
  if exists (select 1 from pg_proc where proname = 'is_admin') then
    admin_test := 'is_admin()';
  else
    -- lock-down-rls.sql has not been run. Any signed-in account, which is
    -- still closed to visitors — the admin has no sign-up form.
    admin_test := 'auth.role() = ''authenticated''';
  end if;

  -- Read: anyone, but only what is published. Visitors are never signed in.
  execute 'drop policy if exists "Public reads published categories" on collection_categories';
  execute 'create policy "Public reads published categories"
             on collection_categories for select using (published = true)';

  -- The admin needs to see drafts too, and to write.
  execute 'drop policy if exists "Admin full access categories" on collection_categories';
  execute 'create policy "Admin full access categories"
             on collection_categories for all
             using (' || admin_test || ') with check (' || admin_test || ')';
end $$;

-- ── Proof it worked ────────────────────────────────────────────
-- Expect the table, 2 policies, and one row per category already in use.
select
  (select count(*) from collection_categories)                         as categories,
  (select count(*) from pg_policies
     where schemaname = 'public' and tablename = 'collection_categories') as policies,
  (select string_agg(slug, ', ' order by slug) from collection_categories) as seeded;
