-- ═══════════════════════════════════════════════════════════════
--  URBAN NEST — 3D PRODUCTS & SCENES SETUP
--  Run this once: Supabase Dashboard → SQL Editor → New Query → paste → Run
--  (Safe to run again — it skips anything that already exists.)
--
--  What it does:
--   1. Creates the room_products table (dots + product info) used by
--      admin/products.html and the room pages.
--   2. Registers the existing bathroom & kitchen scenes in spline_scenes
--      so they appear under Admin → Spline Scenes.
--   3. Imports the 11 existing bathroom products so nothing is lost.
-- ═══════════════════════════════════════════════════════════════

create table if not exists room_products (
  id uuid default gen_random_uuid() primary key,
  room text not null,                -- 'bath' | 'kitchen' | 'bed'
  scene_id uuid,                     -- which 3D render the dot sits on (null = all renders of the room)
  name text not null,
  tag text,                          -- small gold label, e.g. BATHROOM ACCESSORIES
  description text,
  spline_url text,                   -- product close-up 3D scene (optional)
  buy_link text,                     -- Amazon affiliate link
  specs jsonb default '[]',          -- [["Material","Ceramic"], ...]
  dot_x numeric default 50,          -- dot position, % from left
  dot_y numeric default 50,          -- dot position, % from top
  object_name text,                  -- optional: Spline object name for 3D dot tracking
  published boolean default false,
  sort_order int default 0,
  created_at timestamptz default now()
);

alter table room_products add column if not exists scene_id uuid;
alter table room_products enable row level security;

do $$ begin
  create policy "Public reads published products"
    on room_products for select using (published = true);
exception when duplicate_object then null; end $$;

do $$ begin
  create policy "Admin full access products"
    on room_products for all using (auth.role() = 'authenticated');
exception when duplicate_object then null; end $$;

-- ── Register the existing room scenes ──────────────────────────
do $$ begin
  if not exists (select 1 from spline_scenes where url = 'https://prod.spline.design/uZpVsuRsjSo8bzao/scene.splinecode') then
    insert into spline_scenes (name, url, page_placement, active, description)
    values ('Bathroom — Main View', 'https://prod.spline.design/uZpVsuRsjSo8bzao/scene.splinecode', 'bath', true, 'Original bathroom render');
  end if;
  if not exists (select 1 from spline_scenes where url = 'https://prod.spline.design/Sj5adFcvg1xrFk7n/scene.splinecode') then
    insert into spline_scenes (name, url, page_placement, active, description)
    values ('Kitchen — Main View', 'https://prod.spline.design/Sj5adFcvg1xrFk7n/scene.splinecode', 'kitchen', true, 'Original kitchen render');
  end if;
end $$;

-- ── Import existing bathroom products (tied to the main bathroom view) ──
do $$
declare bath_scene uuid;
begin
  if exists (select 1 from room_products where room = 'bath') then return; end if;
  select id into bath_scene from spline_scenes
    where url = 'https://prod.spline.design/uZpVsuRsjSo8bzao/scene.splinecode' limit 1;

  insert into room_products (room, scene_id, name, tag, description, spline_url, buy_link, specs, dot_x, dot_y, object_name, published, sort_order) values
  ('bath',bath_scene,'Soap Dispenser','BATHROOM ACCESSORIES','A sleek ceramic dispenser for your liquid soap or handwash. Clean lines, matte black pump, perfect for any modern vanity.','https://prod.spline.design/GE2Lq8Cg0wgaAZjS/scene.splinecode','https://amzn.to/4gAUBxh','[["Material","Ceramic"],["Pump","Matte black"],["Capacity","300 ml"]]',40.1249,49.8715,'Soap Dispenser',true,1),
  ('bath',bath_scene,'Soap Dish','BATHROOM ACCESSORIES','A ribbed ceramic soap dish with drainage grooves. Keeps your soap dry and your counter clean.','https://prod.spline.design/htz3mYXdulTmsqtL/scene.splinecode','https://amazon.in','[["Material","Ceramic"],["Finish","Matte white"],["Size","12 × 8 cm"]]',44.7593,53.1597,'Soap Dish',true,2),
  ('bath',bath_scene,'Vanity Tray','VANITY ACCESSORIES','A white marble vanity tray with a polished gold rim. Organise your counter essentials with effortless elegance.','https://prod.spline.design/ReoocyAwE8Yvhmpu/scene.splinecode','https://amazon.in','[["Material","Marble"],["Rim","Polished gold"],["Size","30 × 20 cm"]]',44.1763,52.3608,'Tray',true,3),
  ('bath',bath_scene,'Toilet Mat','BATH TEXTILES','A soft cotton loop pile mat with non-slip latex backing. Machine washable and moisture absorbent.','https://prod.spline.design/666Wti0U3yF-wPvt/scene.splinecode','https://amazon.in','[["Material","100% cotton"],["GSM","900"],["Backing","Non-slip latex"]]',54.1982,69.6905,'Toilet Mat',true,4),
  ('bath',bath_scene,'Teal Rug','BATH TEXTILES','A plush tufted rectangle rug in teal. Soft underfoot, moisture absorbent, anti-skid base.','https://prod.spline.design/nsVngQY8mZwEoJ5k/scene.splinecode','https://amazon.in','[["Material","Cotton tufted"],["Size","60 × 90 cm"],["Base","Anti-skid"]]',41.0926,69.5693,'Teal Rug',true,5),
  ('bath',bath_scene,'Shower Mat','BATH TEXTILES','A quick-dry microfibre mat that keeps your shower area dry and slip-free after every use.','https://prod.spline.design/NRQZO3lqB-RA4ogV/scene.splinecode','https://amazon.in','[["Material","Microfibre"],["Size","45 × 75 cm"],["Feature","Quick-dry"]]',63.6311,69.9588,'Shower Mat',true,6),
  ('bath',bath_scene,'Shower Caddy','SHOWER ACCESSORIES','A rust-proof aluminium hanging caddy with 3 shelves and hooks. Fits all standard shower heads.','https://prod.spline.design/b5XDOSq8WFuWr1Dd/scene.splinecode','https://amazon.in','[["Material","Aluminium"],["Shelves","3"],["Install","No drilling"]]',67.6259,41.0653,'Shower Caddy',true,7),
  ('bath',bath_scene,'Waste Basket','BATHROOM ESSENTIALS','A fingerprint-resistant matte waste basket with a soft-close lid and removable inner bucket.','https://prod.spline.design/VQefV2V4jnLNtF5l/scene.splinecode','https://amazon.in','[["Finish","Matte"],["Capacity","5 litres"],["Lid","Soft-close"]]',47.8217,61.2219,'Waste Basket',true,8),
  ('bath',bath_scene,'Tissue Holder','BATHROOM ESSENTIALS','A matte black stainless steel wall-mounted tissue holder. All mounting hardware included.','https://prod.spline.design/sP3ZQLmrTKIyG1rB/scene.splinecode','https://amazon.in','[["Material","Stainless steel"],["Finish","Matte black"],["Mount","Wall-mount"]]',37.7079,52.0565,'Tissue Holder',true,9),
  ('bath',bath_scene,'Brush Holder','VANITY ESSENTIALS','A ceramic brush and cup holder with a matte glaze finish. Keeps toothbrushes and razors neatly organised.','https://prod.spline.design/2Ts6Qsis8U6196K2/scene.splinecode','https://amazon.in','[["Material","Ceramic"],["Finish","Matte glaze"],["Slots","4"]]',44.9676,51.1812,'Brush Holder',true,10),
  ('bath',bath_scene,'White Vase','BATHROOM DECOR','A clean minimal white vase that adds a touch of life and elegance to your bathroom counter or shelf.','https://prod.spline.design/GE2Lq8Cg0wgaAZjS/scene.splinecode','https://amazon.in','[["Material","Ceramic"],["Finish","Gloss white"],["Style","Minimal"]]',43,46,'White Vase',true,11);
end $$;
