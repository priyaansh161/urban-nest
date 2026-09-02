-- ═══════════════════════════════════════════════════════════════
--  URBAN NEST — UNDO setup-commerce.sql
--  Run only if you want the commerce tables gone again.
--
--  ┌─────────────────────────────────────────────────────────────┐
--  │ THIS ONE REALLY IS DESTRUCTIVE. Supabase's warning is right  │
--  │ about this file, unlike the one it shows for setup.          │
--  │                                                              │
--  │ It permanently deletes every seller and EVERY ORDER EVER     │
--  │ PLACED. Only run it while the commerce side is still empty   │
--  │ — i.e. straight after setup-commerce.sql, before you have    │
--  │ taken a single order.                                        │
--  └─────────────────────────────────────────────────────────────┘
--
--  What it does NOT touch: collection_items rows themselves, and
--  everything the site shows today. Your products, articles, scenes,
--  photos and prices are untouched — only the columns that
--  setup-commerce.sql added are removed.
-- ═══════════════════════════════════════════════════════════════


-- ── 1. The columns added to collection_items ───────────────────
--  Dropped before the tables, because they reference sellers.
--  The original price / buy_link columns are deliberately not here.

alter table collection_items
  drop column if exists seller_id,
  drop column if exists affiliate_seller_id,
  drop column if exists price_paise,
  drop column if exists primary_cta,
  drop column if exists fulfilled_by,
  drop column if exists in_stock;

alter table collection_items
  drop constraint if exists collection_items_primary_cta_check;
alter table collection_items
  drop constraint if exists collection_items_fulfilled_by_check;


-- ── 2. The commerce tables ─────────────────────────────────────
--  order_items goes first — it points at both of the others.

drop table if exists order_items;
drop table if exists orders;
drop table if exists sellers;

drop sequence if exists order_no_seq;


-- ═══════════════════════════════════════════════════════════════
--  Back to where you started. Confirm with:
-- ═══════════════════════════════════════════════════════════════

select
  (select count(*) from collection_items) as items_still_here,
  (select count(*) from information_schema.tables
     where table_schema = 'public'
       and table_name in ('sellers', 'orders', 'order_items')) as commerce_tables_left;
