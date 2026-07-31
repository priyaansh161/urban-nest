-- A collection item can carry a 3D model and a buy link.
--   model_url — path to a .glb, e.g. "models/chandelier.glb". Rendered with
--               <model-viewer>; no Spline scene involved. Empty falls back to
--               the item's photo.
--   buy_link  — where the piece can actually be bought.
alter table collection_items add column if not exists model_url text;
alter table collection_items add column if not exists buy_link  text;
