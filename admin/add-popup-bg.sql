-- Per-product backdrop for the product popup's 3D area.
-- 'light' puts a pale ground behind dark products; anything else (or null)
-- keeps the default near-black, which suits pale ceramics and metals.
--
-- NOTE: this only shows through if the product's Spline scene background is
-- set to transparent (Spline → Scene → Background → alpha 0). An opaque scene
-- background is painted by Spline itself and covers whatever we set here.
alter table room_products add column if not exists popup_bg text;
