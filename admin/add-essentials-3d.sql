-- ═══════════════════════════════════════════════════════════════
--  URBAN NEST — THE ROOM 3D, ON THE ESSENTIALS PIECE
--  Run: Supabase Dashboard → SQL Editor → New Query → paste → Run
--
--  WHY: every dot in a 3D room already has its own Spline close-up —
--  the little scene that opens when you tap the dot. 51 of the 52
--  imported pieces have one. There is no reason for the Essentials page
--  to show a placeholder while that model sits unused in another table.
--
--  IT DOES NOT TOUCH room_products. Same as the import: it only reads.
--  The rooms keep pointing at the same scenes they always did; the
--  Essentials piece now points at the same URL as well. One scene, two
--  places showing it.
--
--  WHY A SEPARATE COLUMN FROM model_url: they are different formats and
--  different viewers. model_url is a .glb rendered by <model-viewer>;
--  spline_url is a .splinecode rendered by <spline-viewer>. Putting a
--  Spline scene in model_url would simply fail to load.
--
--  Requires admin/import-room-products.sql to have been run first —
--  source_product_id is what joins a piece to its dot.
--
--  Safe to run more than once.
-- ═══════════════════════════════════════════════════════════════

alter table collection_items add column if not exists spline_url text;

-- Copy each piece's close-up across from the dot it came from.
-- Only where the piece does not already have one, so a scene set by hand
-- in the admin is never overwritten by a re-run.
update collection_items ci
set    spline_url = rp.spline_url
from   room_products rp
where  ci.source_product_id = rp.id
  and  rp.spline_url is not null
  and  ci.spline_url is null;

-- ── What you should see ────────────────────────────────────────
select
  count(*)                                          as essentials_pieces,
  count(*) filter (where spline_url is not null)    as with_3d,
  count(*) filter (where image_url  is not null)    as with_photo,
  count(*) filter (where published)                 as live
from collection_items
where section = 'essentials';

-- And the rooms, untouched:
select count(*) as room_products_still_there,
       count(*) filter (where spline_url is not null) as room_dots_with_3d
from room_products;
