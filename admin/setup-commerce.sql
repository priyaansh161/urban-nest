-- ═══════════════════════════════════════════════════════════════
--  URBAN NEST — SELLERS, ORDERS & COMMERCE FOUNDATION
--  Run once: Supabase Dashboard → SQL Editor → New Query → paste → Run
--
--  Safe to run more than once. Nothing here drops or rewrites an
--  existing column — every change is additive, so the site keeps
--  rendering exactly as it does now while this sits unused.
--
--  WHAT THIS SETS UP
--    A seller is the thing that owns a product. Urban Nest is itself
--    just another seller row, which is what lets the same cart handle
--    marketplace stock (a showroom ships, money splits to them) and
--    own stock (we ship, money is ours) without a second system.
--
--      kind = 'marketplace'  showroom sells and ships. Buyer sees their
--                            name. Money splits to their account at
--                            checkout via Razorpay Route.
--      kind = 'consignment'  their stock, held and shipped by us. Buyer
--                            sees Urban Nest, sourced from them. We
--                            collect everything and pay their cut on a
--                            cycle. Needs no capital — we never buy it.
--      kind = 'direct'       our own stock, bought and sold by us.
--      kind = 'affiliate'    not sold here at all — an outbound link.
--
--    Who SELLS and who SHIPS are separate questions. kind sets the
--    normal pairing for a seller; fulfilled_by on a single product
--    overrides it when one piece is handled differently.
--
--    The existing price column (free text, e.g. "₹12,999") is left
--    alone. price_paise is the number a cart can actually add up.
--    Both exist until every page reads the number, then the text one
--    can go.
-- ═══════════════════════════════════════════════════════════════


-- ── 1. SELLERS ─────────────────────────────────────────────────

create table if not exists sellers (
  id uuid default gen_random_uuid() primary key,
  name text not null,                  -- shown to visitors: "Sold by …"
  slug text unique,
  kind text not null default 'marketplace',
  logo_url text,                       -- small mark beside the Sold-by line

  -- Money. Only meaningful for marketplace/direct sellers.
  commission_pct numeric(5,2) default 0,   -- what Urban Nest keeps, e.g. 15.00
  razorpay_account_id text,                -- Route linked account (acc_…), null for us

  -- Contact. Required on the public page for marketplace sellers so a
  -- buyer can reach whoever is actually shipping the piece.
  contact_name text,
  phone text,
  email text,
  address text,
  city text,
  state text,
  pincode text,
  gstin text,

  -- Set later, when a showroom gets its own login to see its orders.
  auth_user_id uuid,

  active boolean default true,
  sort_order int default 0,
  created_at timestamptz default now(),

  constraint sellers_kind_check
    check (kind in ('marketplace', 'consignment', 'direct', 'affiliate'))
);

-- How the seller actually gets their money.
--   'route'  — split to their linked account at checkout (marketplace)
--   'manual' — we collect it all and pay them on a cycle (consignment)
alter table sellers
  add column if not exists payout_mode text default 'route';

do $$ begin
  alter table sellers
    add constraint sellers_payout_mode_check
    check (payout_mode in ('route', 'manual'));
exception when duplicate_object then null;
end $$;

-- Two rows to start: us, and Amazon standing in for the existing
-- affiliate catalogue. Add showrooms through the admin.
--  payout_mode is set explicitly on both. Neither is ever paid through a
--  Route split — our own stock owes nobody, and an affiliate link never
--  takes a payment here — so leaving them on the column default of
--  'route' would read as wrong in the admin.
insert into sellers (name, slug, kind, payout_mode, commission_pct, sort_order)
select 'Urban Nest', 'urban-nest', 'direct', 'manual', 0, 0
where not exists (select 1 from sellers where slug = 'urban-nest');

insert into sellers (name, slug, kind, payout_mode, sort_order)
select 'Amazon', 'amazon', 'affiliate', 'manual', 10
where not exists (select 1 from sellers where slug = 'amazon');

-- Corrects the two seeded rows if an earlier run created them before the
-- line above set payout_mode. Harmless on a clean run.
update sellers set payout_mode = 'manual'
 where slug in ('urban-nest', 'amazon')
   and payout_mode <> 'manual';


-- ── 2. PRODUCTS LEARN WHO SELLS THEM ───────────────────────────
--
--  Two separate seller links, because one piece can be both stocked
--  by us and listed on Amazon:
--    seller_id            → who sells it through OUR checkout
--    affiliate_seller_id  → where buy_link sends people instead
--
--  primary_cta decides which button leads when both are set.

alter table collection_items
  add column if not exists seller_id uuid references sellers(id),
  add column if not exists affiliate_seller_id uuid references sellers(id),
  add column if not exists price_paise bigint,
  add column if not exists primary_cta text default 'cart',
  add column if not exists fulfilled_by text,
  add column if not exists in_stock boolean default true;

do $$ begin
  alter table collection_items
    add constraint collection_items_primary_cta_check
    check (primary_cta in ('cart', 'affiliate'));
exception when duplicate_object then null;
end $$;

-- Null means "however this seller normally works". Set it only for the
-- odd piece handled differently — a showroom that ships its own stock
-- but left one heavy sculpture with us, or the reverse.
do $$ begin
  alter table collection_items
    add constraint collection_items_fulfilled_by_check
    check (fulfilled_by is null or fulfilled_by in ('seller', 'urban_nest'));
exception when duplicate_object then null;
end $$;

-- Everything with an outbound link today is an Amazon affiliate item.
-- Point it at that seller row so the button can say "Shop at Amazon".
update collection_items
   set affiliate_seller_id = (select id from sellers where slug = 'amazon'),
       primary_cta = 'affiliate'
 where buy_link is not null
   and affiliate_seller_id is null;


-- ── 3. ORDERS ──────────────────────────────────────────────────
--
--  Two statuses, deliberately separate. A paid order that has not
--  shipped is a completely different thing from an unpaid one, and
--  collapsing them into one column is painful to undo later.

create sequence if not exists order_no_seq start 1001;

create table if not exists orders (
  id uuid default gen_random_uuid() primary key,
  order_no text unique default ('UN-' || nextval('order_no_seq')),

  customer_name text not null,
  customer_email text,
  customer_phone text not null,

  address_line1 text,
  address_line2 text,
  city text,
  state text,
  pincode text,

  subtotal_paise bigint not null default 0,
  shipping_paise bigint not null default 0,
  total_paise bigint not null default 0,

  payment_status text not null default 'pending',
  razorpay_order_id text,
  razorpay_payment_id text,
  razorpay_signature text,

  notes text,
  created_at timestamptz default now(),
  paid_at timestamptz,

  constraint orders_payment_status_check
    check (payment_status in ('pending', 'paid', 'failed', 'refunded'))
);


-- ── 4. ORDER LINES ─────────────────────────────────────────────
--
--  Each line carries its own seller and its own fulfilment status,
--  because in a marketplace order every showroom ships its own items.
--
--  The _snapshot columns are not duplication. Products get renamed and
--  repriced; an order must stay a record of what was actually bought,
--  so the line keeps its own copy and never follows the product.

create table if not exists order_items (
  id uuid default gen_random_uuid() primary key,
  order_id uuid not null references orders(id) on delete cascade,
  item_id uuid references collection_items(id) on delete set null,
  seller_id uuid references sellers(id),

  name_snapshot text not null,
  image_snapshot text,
  unit_price_paise bigint not null,
  qty int not null default 1,
  line_total_paise bigint not null,

  commission_paise bigint not null default 0,      -- Urban Nest keeps
  seller_payout_paise bigint not null default 0,   -- seller receives

  -- Snapshotted too. Who packs this line is decided when the order is
  -- placed and must not change afterwards, even if the arrangement with
  -- that seller changes next month.
  fulfilled_by text not null default 'seller',

  fulfilment_status text not null default 'new',
  tracking_ref text,

  -- Only used when payout_mode is 'manual' (consignment). Route splits
  -- settle themselves at checkout and are 'not_applicable'.
  payout_status text not null default 'pending',
  paid_out_at timestamptz,

  created_at timestamptz default now(),

  constraint order_items_fulfilled_by_check
    check (fulfilled_by in ('seller', 'urban_nest')),
  constraint order_items_fulfilment_check
    check (fulfilment_status in
      ('new', 'confirmed', 'shipped', 'delivered', 'cancelled', 'returned')),
  constraint order_items_payout_status_check
    check (payout_status in ('pending', 'paid', 'not_applicable'))
);

create index if not exists order_items_order_idx  on order_items (order_id);
create index if not exists order_items_seller_idx on order_items (seller_id);
create index if not exists orders_status_idx      on orders (payment_status);
create index if not exists collection_seller_idx  on collection_items (seller_id);


-- ── 5. ACCESS RULES ────────────────────────────────────────────
--
--  Visitors need to read sellers — the "Sold by" line and its logo
--  are on the public product card. They must never read orders.
--
--  Orders are written by the serverless checkout function using the
--  service-role key, which bypasses RLS entirely. So no insert policy
--  is granted here on purpose: nothing in a browser can create,
--  read or alter an order.

alter table sellers     enable row level security;
alter table orders      enable row level security;
alter table order_items enable row level security;

drop policy if exists "Public reads active sellers" on sellers;
create policy "Public reads active sellers"
  on sellers for select
  using (active = true);

drop policy if exists "Admin full access sellers" on sellers;
create policy "Admin full access sellers"
  on sellers for all
  using (is_admin()) with check (is_admin());

drop policy if exists "Admin full access orders" on orders;
create policy "Admin full access orders"
  on orders for all
  using (is_admin()) with check (is_admin());

drop policy if exists "Admin full access order items" on order_items;
create policy "Admin full access order items"
  on order_items for all
  using (is_admin()) with check (is_admin());


-- ═══════════════════════════════════════════════════════════════
--  Done. Check it landed:
-- ═══════════════════════════════════════════════════════════════

select
  (select count(*) from sellers)                                   as sellers,
  (select count(*) from collection_items)                          as items,
  (select count(*) from collection_items where buy_link is not null) as affiliate_items,
  (select count(*) from collection_items where price_paise is not null) as priced_items,
  (select count(*) from orders)                                    as orders;
