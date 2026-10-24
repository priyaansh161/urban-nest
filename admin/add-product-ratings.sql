-- ═══════════════════════════════════════════════════════════════
--  URBAN NEST — "OUR TAKE" ON EVERY PRODUCT
--  Run once: Supabase Dashboard → SQL Editor → New Query → paste → Run
--  (Safe to run again.)
--
--  Priyaansh's own rating and verdict, written in Admin:
--    un_rating  0.5 – 5, in half steps
--    un_take    a short paragraph: how the piece really is
--    un_pros    what is good, one point per line
--    un_cons    what to watch for, one point per line
--
--  Added to BOTH product tables (Collection + Essentials share
--  collection_items; the rooms use room_products).
-- ═══════════════════════════════════════════════════════════════

alter table collection_items add column if not exists un_rating numeric(2,1)
  check (un_rating is null or (un_rating >= 0.5 and un_rating <= 5));
alter table collection_items add column if not exists un_take text;
alter table collection_items add column if not exists un_pros text;
alter table collection_items add column if not exists un_cons text;

alter table room_products add column if not exists un_rating numeric(2,1)
  check (un_rating is null or (un_rating >= 0.5 and un_rating <= 5));
alter table room_products add column if not exists un_take text;
alter table room_products add column if not exists un_pros text;
alter table room_products add column if not exists un_cons text;
