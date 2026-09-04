-- ═══════════════════════════════════════════════════════════════
--  URBAN NEST — THE ESSENTIALS
--  Run once: Supabase Dashboard → SQL Editor → New Query → paste → Run
--
--  WHY: the Collection is handpicked decorative pieces — the things that
--  prove the eye is worth trusting. The Essentials is the other half of
--  the idea: a spatula stand costs very little, is sold everywhere, and
--  is found almost only in high-income homes. Not because it is
--  expensive, but because no shop puts it in front of you. That is the
--  gap this section exists to close.
--
--  HOW: not a new table. The Essentials needs exactly what the
--  Collection needs — categories with a hero and a description, items
--  with photographs, prices, buy links, optional 3D and optional
--  seller — so it shares both tables and is told apart by one column.
--  A second pair of tables would mean every future fix applied twice.
--
--  Everything that exists today becomes section = 'collection', which is
--  also the default, so nothing already published moves or changes.
--
--  Safe to run more than once.
-- ═══════════════════════════════════════════════════════════════

-- ── 1. The column, on both tables ──────────────────────────────
alter table collection_items      add column if not exists section text not null default 'collection';
alter table collection_categories add column if not exists section text not null default 'collection';

-- Anything that predates this column belongs to the Collection.
update collection_items      set section = 'collection' where section is null;
update collection_categories set section = 'collection' where section is null;

-- ── 2. Only the two sections, nothing else ─────────────────────
-- Dropped first so the script can be run again after a section is added.
alter table collection_items      drop constraint if exists collection_items_section_check;
alter table collection_categories drop constraint if exists collection_categories_section_check;

alter table collection_items
  add constraint collection_items_section_check
  check (section in ('collection', 'essentials'));

alter table collection_categories
  add constraint collection_categories_section_check
  check (section in ('collection', 'essentials'));

-- ── 3. Both pages filter on it, so it is indexed ───────────────
create index if not exists collection_items_section_idx      on collection_items      (section, sort_order);
create index if not exists collection_categories_section_idx on collection_categories (section, sort_order);

-- ── 4. A slug is only unique within its section ────────────────
-- "storage" can reasonably exist in both. The old table-wide unique
-- constraint on slug would have refused the second one.
alter table collection_categories drop constraint if exists collection_categories_slug_key;
drop index if exists collection_categories_slug_section_idx;
create unique index collection_categories_slug_section_idx
  on collection_categories (section, slug);

-- ── 5. Somewhere to put the first pieces ───────────────────────
-- Starting categories for the Essentials, with the names spelled out
-- rather than derived — "kitchen" is not "The Kitchen" by any rule.
-- Descriptions are placeholders; write the real ones in the admin.
insert into collection_categories (slug, name, summary, sort_order, published, section)
values
  ('kitchen-essentials', 'Kitchen',  'The drawer and the worktop. Things you reach for every day.',        1, true, 'essentials'),
  ('bath-essentials',    'Bath',     'Small fittings and holders that decide how a bathroom feels.',       2, true, 'essentials'),
  ('storage',            'Storage',  'Baskets, boxes and racks. Where the clutter actually goes.',         3, true, 'essentials'),
  ('desk',               'Desk',     'The surface you work at, and what sits on it.',                     4, true, 'essentials'),
  ('entryway',           'Entryway', 'Hooks, trays and mats. The first three feet of a home.',            5, true, 'essentials')
on conflict do nothing;

-- ── What you should see ────────────────────────────────────────
select section, count(*) as categories
from collection_categories group by section order by section;

select section, count(*) as items
from collection_items group by section order by section;
