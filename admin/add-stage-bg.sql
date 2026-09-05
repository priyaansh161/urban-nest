-- ═══════════════════════════════════════════════════════════════
--  URBAN NEST — WHICH GROUND A PIECE'S 3D SITS ON
--  Run: Supabase Dashboard → SQL Editor → New Query → paste → Run
--
--  WHY: a Spline close-up is an object on a transparent background, and
--  whether it can be seen depends on what is behind it. The Spatula Rest
--  is dark grey and disappears on the near-black stage. The Shower Mat is
--  pale blue and disappears on the cream one. There is no default that
--  suits both, so it has to be a choice per piece.
--
--  room_products has a popup_bg column for exactly this, which is why the
--  rooms get it right — except it is null on all 52 dots, so there was
--  nothing to copy across. This is the same idea on the Essentials piece,
--  set in the admin.
--
--  null means dark, which is what the stage has always defaulted to.
--
--  Safe to run more than once.
-- ═══════════════════════════════════════════════════════════════

alter table collection_items add column if not exists popup_bg text;

alter table collection_items drop constraint if exists collection_items_popup_bg_check;
alter table collection_items
  add constraint collection_items_popup_bg_check
  check (popup_bg is null or popup_bg in ('light', 'dark'));

select count(*) filter (where popup_bg = 'light') as on_light,
       count(*) filter (where popup_bg = 'dark')  as on_dark,
       count(*) filter (where popup_bg is null)   as unset_defaults_to_dark
from collection_items where section = 'essentials';
