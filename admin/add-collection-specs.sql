-- ═══════════════════════════════════════════════════════════════
--  URBAN NEST — SPECIFICATIONS ON COLLECTION ITEMS
--  Run once: Supabase Dashboard → SQL Editor → New Query → paste → Run
--
--  Same shape room_products already uses, so the admin behaves the
--  same way in both places: an ordered list of label/value pairs.
--    [["Material","Crystal glass"], ["Drop","82 cm"], ...]
--
--  Safe to run more than once.
-- ═══════════════════════════════════════════════════════════════

alter table collection_items
  add column if not exists specs jsonb default '[]';

-- Existing rows get an empty list rather than null, so the page never
-- has to tell the two apart.
update collection_items set specs = '[]' where specs is null;

select count(*) as items, count(*) filter (where specs is not null) as with_specs
from collection_items;
