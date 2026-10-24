-- ═══════════════════════════════════════════════════════════════
--  URBAN NEST — AMAZON LINK STATUS
--  Run this once: Supabase Dashboard → SQL Editor → New Query → paste → Run
--  (Safe to run again — it skips anything that already exists.)
--
--  Adds two columns to BOTH product tables so Admin → Amazon Links can
--  record whether each product is still listed on Amazon:
--
--    amazon_status      'unchecked' (default) | 'ok' | 'gone'
--    amazon_checked_at  when you last looked
--
--  A product marked 'gone' keeps its page on Urban Nest, but the Amazon
--  button is hidden so nobody is sent to a dead listing.
-- ═══════════════════════════════════════════════════════════════

alter table collection_items add column if not exists amazon_status text default 'unchecked';
alter table collection_items add column if not exists amazon_checked_at timestamptz;

alter table room_products add column if not exists amazon_status text default 'unchecked';
alter table room_products add column if not exists amazon_checked_at timestamptz;
