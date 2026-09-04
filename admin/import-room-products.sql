-- ═══════════════════════════════════════════════════════════════
--  URBAN NEST — BRING THE ROOM PRODUCTS INTO THE ESSENTIALS
--  Run: Supabase Dashboard → SQL Editor → New Query → paste → Run
--
--  WHY: 52 products are already dotted onto the 3D rooms, with names,
--  descriptions, specs and Amazon links written. The Spatula Rest is
--  among them. None of that work should be done a second time just to
--  list the same object on the Essentials page.
--
--  IT DOES NOT TOUCH room_products. Not one column, not one row. The
--  rooms keep working exactly as they do; this only reads from them.
--
--  IT IS RE-RUNNABLE, and that is the point. Each imported piece
--  remembers which room product it came from, so running this again
--  brings across only what is new. Add a dot to a room today, run this
--  tomorrow, and only that dot arrives.
--
--  EVERYTHING ARRIVES UNPUBLISHED. room_products holds no photograph —
--  the object is shown as a Spline close-up instead — and the Essentials
--  page leads with photographs. Publishing 52 pieces with a placeholder
--  where the picture goes would make a finished page look broken. So
--  they land as drafts: the writing is done, and each one needs a photo
--  and a publish tick.
--
--  Requires admin/add-essentials-section.sql to have been run first.
-- ═══════════════════════════════════════════════════════════════

-- ── 1. Remember where each piece came from ─────────────────────
-- This is what makes the import repeatable rather than duplicating
-- everything every time it runs. It also leaves the door open to a
-- "see it in the kitchen" link on the piece later on.
alter table collection_items add column if not exists source_product_id uuid;

drop index if exists collection_items_source_product_idx;
create unique index collection_items_source_product_idx
  on collection_items (source_product_id)
  where source_product_id is not null;

-- ── 2. A home for the bedroom pieces ───────────────────────────
-- The seeded categories were Kitchen, Bath, Storage, Desk and Entryway;
-- the eight bedroom dots had nowhere to land.
insert into collection_categories (slug, name, summary, sort_order, published, section)
values ('bedroom', 'Bedroom', 'Bedside, wall and floor. What the room is actually made of.', 6, true, 'essentials')
on conflict do nothing;

-- ── 3. Bring across whatever has not come across yet ───────────
insert into collection_items (
  name, description, category, buy_link, specs,
  section, primary_cta, in_stock, published, coming_soon,
  sort_order, source_product_id
)
select
  rp.name,
  rp.description,
  case rp.room
    when 'kitchen' then 'kitchen-essentials'
    when 'bath'    then 'bath-essentials'
    when 'bed'     then 'bedroom'
    else 'storage'                      -- a new room lands somewhere visible
  end,
  rp.buy_link,
  coalesce(rp.specs, '[]'::jsonb),
  'essentials',
  'affiliate',        -- they are Amazon links today; switch a piece to
                      -- 'cart' by hand once it has a seller and a price
  true,
  false,              -- drafts. Add a photograph, then publish.
  false,
  rp.sort_order,
  rp.id
from room_products rp
where rp.published = true
  and rp.buy_link is not null
  and not exists (
    select 1 from collection_items ci where ci.source_product_id = rp.id
  );

-- ── What you should see ────────────────────────────────────────
-- Drafts waiting for a photograph, by category:
select c.name as category,
       count(*) filter (where i.published = false) as drafts,
       count(*) filter (where i.published = true)  as live
from collection_items i
join collection_categories c
  on c.slug = i.category and c.section = i.section
where i.section = 'essentials'
group by c.name, c.sort_order
order by c.sort_order;

-- And confirmation that the rooms are untouched:
select count(*) as room_products_still_there from room_products;
