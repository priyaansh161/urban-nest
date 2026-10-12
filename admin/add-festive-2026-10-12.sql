-- ═══════════════════════════════════════════════════════════════
--  URBAN NEST — THE FESTIVE EDIT (8 pieces) + 1 PAINTING, 2026-10-12
--  Run once: Supabase Dashboard → SQL Editor → New Query → paste → Run
--
--  Details, prices and photographs taken from the Amazon listings on
--  2026-10-12. Photo-only pieces: no 3D model. image_url is the cover,
--  gallery the photographs after it (add-collection-gallery.sql).
--
--  Everything arrives UNPUBLISHED. Look at each one in Admin →
--  Collection, then publish. Buy links already carry the tag
--  urbannest03b-21, so they earn as they are.
--
--  Running it twice creates duplicate pieces (the category is guarded).
-- ═══════════════════════════════════════════════════════════════

-- ── The category ───────────────────────────────────────────────
-- Named "Festive" rather than "Diwali" so the same shelf carries
-- Christmas, weddings and Holi later; rename it in the admin for the
-- season. sort_order -1 puts it first among the tiles while it is in season.
insert into collection_categories (slug, name, summary, about, sort_order, published, tile_image_url, hero_image_url)
select
  'festive',
  'The Festive Edit',
  'Brass, flame and flowers for the nights the house is lit.',
  'Diwali is the one week a year every home is styled on purpose. These are the pieces that carry it: urlis to float marigolds and diyas in, crystal for tealights to shine through, light for the balcony and the mandir. Chosen to look as right on the table the week after as on the night itself.',
  -1,
  true,
  'https://m.media-amazon.com/images/I/91wZAS0hcLL._SL1500_.jpg',
  'https://m.media-amazon.com/images/I/810ar-CkKCL._SL1500_.jpg'
where not exists (select 1 from collection_categories where slug = 'festive');

-- ── The pieces ─────────────────────────────────────────────────
insert into collection_items
  (name, description, category, section, price, buy_link, image_url, gallery, specs,
   affiliate_seller_id, primary_cta, published, coming_soon, in_stock, sort_order)
values

/* B0DJJPWK3D · ₹3,799 (M.R.P. ₹9,999) · 4.3★ (30) */
('BEHOMA Brass Peacock Urli 9.5 inch | Floating Flower Bowl for Centre Table & Pooja',
 'A golden brass urli with carved peacocks rising from either side as handles. Float marigolds and diyas in it for Diwali; the rest of the year it holds its own as the centrepiece on a coffee table or at the entrance.',
 'festive', 'collection', '₹3,799',
 'https://www.amazon.in/dp/B0DJJPWK3D?tag=urbannest03b-21',
 'https://m.media-amazon.com/images/I/91wZAS0hcLL._SL1500_.jpg',
 array['https://m.media-amazon.com/images/I/81+C-8svV7L._SL1500_.jpg','https://m.media-amazon.com/images/I/81jk77GG12L._SL1500_.jpg','https://m.media-amazon.com/images/I/81kvLb+RBOL._SL1500_.jpg','https://m.media-amazon.com/images/I/91jTSMFtVTL._SL1500_.jpg','https://m.media-amazon.com/images/I/914LzHuFRWL._SL1500_.jpg','https://m.media-amazon.com/images/I/91KmJi10O5L._SL1500_.jpg'],
 '[["Brand","BEHOMA"],["Material","Brass"],["Finish","Golden"],["Size","9.5 inch"],["Pieces","1"]]'::jsonb,
 '7d0dd3e4-02ec-4c2d-a86e-8c78b90aecfe', 'affiliate', false, false, true, 0),

/* B0GWV15RXC · ₹2,079 (M.R.P. ₹4,999) · 3.8★ (10) */
('Kansakruti Handmade Brass Elephant Urli 6 inch | Floating Flower & Candle Bowl for Mandir & Entrance',
 'A small solid-brass urli standing on four carved elephants, in an antique gold finish. Sized for a mandir shelf, a side table or the corner of a console, where a handful of petals and one floating diya is all it needs.',
 'festive', 'collection', '₹2,079',
 'https://www.amazon.in/dp/B0GWV15RXC?tag=urbannest03b-21',
 'https://m.media-amazon.com/images/I/810ar-CkKCL._SL1500_.jpg',
 array['https://m.media-amazon.com/images/I/816UAz0-eZL._SL1500_.jpg','https://m.media-amazon.com/images/I/81AN1Y0m0ZL._SL1500_.jpg','https://m.media-amazon.com/images/I/81SU1US88KL._SL1500_.jpg','https://m.media-amazon.com/images/I/71CfYqVgb3L._SL1500_.jpg','https://m.media-amazon.com/images/I/71WBsiR1pJL._SL1500_.jpg','https://m.media-amazon.com/images/I/712YQetuK8L._SL1500_.jpg'],
 '[["Brand","Kansakruti"],["Material","Solid brass, handmade"],["Finish","Antique gold"],["Size","6 inch across, 4.5 inch high"],["Weight","650 g"],["Capacity","1 litre"]]'::jsonb,
 '7d0dd3e4-02ec-4c2d-a86e-8c78b90aecfe', 'affiliate', false, false, true, 0),

/* B0DJJYWY6G · ₹2,372 (M.R.P. ₹5,999) · 4.3★ (62) */
('BEHOMA Mango Wood & Metal Urli 11 inch | Centre Table Flower Bowl for Living Room',
 'A wide urli turned from light mango wood and banded in engraved metal, for a festive table that does not want to be all gold. Water, floating flowers and a ring of tealights around it, and it reads as calm rather than loud.',
 'festive', 'collection', '₹2,372',
 'https://www.amazon.in/dp/B0DJJYWY6G?tag=urbannest03b-21',
 'https://m.media-amazon.com/images/I/81iHcD6KkaL._SL1500_.jpg',
 array['https://m.media-amazon.com/images/I/81nLx+QpAFL._SL1500_.jpg','https://m.media-amazon.com/images/I/81LoM5JPPaL._SL1500_.jpg','https://m.media-amazon.com/images/I/914K4zr1SbL._SL1500_.jpg','https://m.media-amazon.com/images/I/81txr7Kd6+L._SL1500_.jpg','https://m.media-amazon.com/images/I/81hLdf7PJXL._SL1500_.jpg','https://m.media-amazon.com/images/I/91B45U8EYRL._SL1500_.jpg'],
 '[["Brand","BEHOMA"],["Material","Mango wood with metal detailing"],["Colour","Natural light brown"],["Size","11 inch"],["Pieces","1"]]'::jsonb,
 '7d0dd3e4-02ec-4c2d-a86e-8c78b90aecfe', 'affiliate', false, false, true, 0),

/* B0CP1YJ89Q · ₹1,710 (M.R.P. ₹2,699) · 4.5★ (80) */
('BEHOMA Golden Lotus Urli 12 inch | Floating Flower Bowl for Diwali, Haldi & Mehendi',
 'A broad urli whose rim opens into lotus petals, in a brass-finish metal. Twelve inches gives room for a full ring of floating diyas, which makes it the one to put where guests come in.',
 'festive', 'collection', '₹1,710',
 'https://www.amazon.in/dp/B0CP1YJ89Q?tag=urbannest03b-21',
 'https://m.media-amazon.com/images/I/81Tc6i+bZvL._SL1500_.jpg',
 array['https://m.media-amazon.com/images/I/81B06ybObQL._SL1500_.jpg','https://m.media-amazon.com/images/I/81xMCdHWA2L._SL1500_.jpg','https://m.media-amazon.com/images/I/71dK-5u0ziL._SL1080_.jpg','https://m.media-amazon.com/images/I/713I1iSNgtL._SL1500_.jpg','https://m.media-amazon.com/images/I/91VPgL+i1fL._SL1500_.jpg','https://m.media-amazon.com/images/I/61bIC4GkBRL._SL1080_.jpg'],
 '[["Brand","BEHOMA"],["Material","Aluminium, brass finish"],["Design","Lotus"],["Size","12 inch"],["Pieces","1"]]'::jsonb,
 '7d0dd3e4-02ec-4c2d-a86e-8c78b90aecfe', 'affiliate', false, false, true, 0),

/* B0BYQ8T4YD · ₹315 (M.R.P. ₹999) · 4.6★ (1,027) */
('CentraLit Crystal Tealight Holders 5.5 cm, Set of 4 | Gold Votives for Diwali Table & Pooja',
 'Four small votives in faceted K9 crystal on gold metal bases. A plain tealight inside throws scattered light across the table, which is the whole point on Diwali night; afterwards they sit just as well on a bedside or a dining table.',
 'festive', 'collection', '₹315',
 'https://www.amazon.in/dp/B0BYQ8T4YD?tag=urbannest03b-21',
 'https://m.media-amazon.com/images/I/61VbS3fMHXL._SL1024_.jpg',
 array['https://m.media-amazon.com/images/I/61O9t7Im-tL._SL1024_.jpg','https://m.media-amazon.com/images/I/61OmksT9r+L._SL1024_.jpg','https://m.media-amazon.com/images/I/61zkbLvsA-L._SL1500_.jpg','https://m.media-amazon.com/images/I/71T+H++SBTL._SL1024_.jpg','https://m.media-amazon.com/images/I/619evGf3iuL._SL1024_.jpg','https://m.media-amazon.com/images/I/71di6vTVPvL._SL1500_.jpg'],
 '[["Brand","CentraLit"],["Material","K9 crystal, metal base"],["Finish","Gold, polished"],["Size","5.5 × 5.5 × 5.5 cm each"],["Pieces","4"]]'::jsonb,
 '7d0dd3e4-02ec-4c2d-a86e-8c78b90aecfe', 'affiliate', false, false, true, 0),

/* B0HFNGNX58 · ₹599 (M.R.P. ₹1,999) · no reviews yet · brand listed as "Generic" */
('The Royal India Golden Urli Set of 3 | Floating Flower Bowl with Tealight Holders for Diwali & Pooja',
 'A golden metal urli with tealight holders, sold as a set of three. Fill the bowl with water and petals, set the tealights around it, and it makes an instant centrepiece for a pooja corner or a dining table.',
 'festive', 'collection', '₹599',
 'https://www.amazon.in/dp/B0HFNGNX58?tag=urbannest03b-21',
 'https://m.media-amazon.com/images/I/81oZuL2fFwL._SL1500_.jpg',
 array['https://m.media-amazon.com/images/I/613BkH821iL._SL1500_.jpg','https://m.media-amazon.com/images/I/81w1gdDg2zL._SL1500_.jpg','https://m.media-amazon.com/images/I/81Jr9BqgpUL._SL1500_.jpg','https://m.media-amazon.com/images/I/81KjBhEwAdL._SL1500_.jpg','https://m.media-amazon.com/images/I/81TIUK3MpvL._SL1500_.jpg','https://m.media-amazon.com/images/I/81aGZBeGSbL._SL1500_.jpg'],
 '[["Material","Metal"],["Finish","Golden"],["Style","Traditional Indian"],["Pieces","3"]]'::jsonb,
 '7d0dd3e4-02ec-4c2d-a86e-8c78b90aecfe', 'affiliate', false, false, true, 0),

/* B0FHF27T7Q · ₹261 (M.R.P. ₹999) · 4.0★ (924) */
('Gesto Rose LED String Lights 10 ft, 14 LEDs | Plug-in Fairy Lights for Mandir, Balcony & Diwali',
 'Ten feet of copper wire strung with fourteen rose-shaped LEDs that glow from every side. Plug-in, so it stays lit all evening round a mandir, a doorway or a balcony railing without batteries running down.',
 'festive', 'collection', '₹261',
 'https://www.amazon.in/dp/B0FHF27T7Q?tag=urbannest03b-21',
 'https://m.media-amazon.com/images/I/71m00aB2K+L._SL1254_.jpg',
 array['https://m.media-amazon.com/images/I/81zzlhpMZBL._SL1254_.jpg','https://m.media-amazon.com/images/I/71yGKSafoML._SL1254_.jpg','https://m.media-amazon.com/images/I/81Szepg1ubL._SL1254_.jpg','https://m.media-amazon.com/images/I/71u9K7HSlAL._SL1254_.jpg','https://m.media-amazon.com/images/I/71F2tJJBDsL._SL1254_.jpg','https://m.media-amazon.com/images/I/71Im5r8LzjL._SL1254_.jpg'],
 '[["Brand","Gesto"],["Length","10 feet"],["LEDs","14, rose-shaped"],["Wire","Copper"],["Power","Plug-in (AC)"],["Use","Indoor"]]'::jsonb,
 '7d0dd3e4-02ec-4c2d-a86e-8c78b90aecfe', 'affiliate', false, false, true, 0),

/* B0HF7DNXST · ₹749 (M.R.P. ₹1,599) · 3.5★ (4) */
('JASCIA Willow Vine LED Branch Lights | USB Wall Light with Remote for Bedroom & Living Room',
 'Bendable dark branches with orange and yellow leaves, each lit from within. Shape it across a bare wall or above a bed; it runs off USB and dims from a remote, so it can stay up long after the festival.',
 'festive', 'collection', '₹749',
 'https://www.amazon.in/dp/B0HF7DNXST?tag=urbannest03b-21',
 'https://m.media-amazon.com/images/I/71K3E6As0-L._SL1500_.jpg',
 array['https://m.media-amazon.com/images/I/71MpwL5Vh9L._SL1500_.jpg','https://m.media-amazon.com/images/I/71fAdhJCFKL._SL1500_.jpg','https://m.media-amazon.com/images/I/81xpVEXIi5L._SL1500_.jpg','https://m.media-amazon.com/images/I/71i544L0eLL._SL1500_.jpg','https://m.media-amazon.com/images/I/61h039w8bxL._SL1000_.jpg','https://m.media-amazon.com/images/I/71FGW4BhL3L._SL1500_.jpg'],
 '[["Brand","JASCIA"],["Design","Branches with leaves"],["Colour","Multicolour"],["Power","USB"],["Control","Remote"],["Weight","150 g"]]'::jsonb,
 '7d0dd3e4-02ec-4c2d-a86e-8c78b90aecfe', 'affiliate', false, false, true, 0),

-- ── Curated Wallscapes ──
/* B0H2F82ZQC · ₹3,149 (M.R.P. ₹6,000) · 5.0★ (1) */
('Artsense Abstract Geometric Textured Canvas 60 × 68 cm | Black-Framed Wall Art for Living Room',
 'Layered geometric blocks with a raised, textured surface, set in a slim black frame. Large enough to carry the wall behind a sofa or a bed on its own, and quiet enough in colour not to fight the room.',
 'wall-art', 'collection', '₹3,149',
 'https://www.amazon.in/dp/B0H2F82ZQC?tag=urbannest03b-21',
 'https://m.media-amazon.com/images/I/71N54N6WpdL._SL1500_.jpg',
 array['https://m.media-amazon.com/images/I/71Osug7xexL._SL1500_.jpg','https://m.media-amazon.com/images/I/718QnGjb6YL._SL1500_.jpg','https://m.media-amazon.com/images/I/71LVQ7ad7UL._SL1500_.jpg'],
 '[["Brand","Artsense"],["Material","Textured canvas"],["Frame","Black"],["Size","60 × 68 cm"],["Orientation","Portrait"],["Weight","4 kg"]]'::jsonb,
 '7d0dd3e4-02ec-4c2d-a86e-8c78b90aecfe', 'affiliate', false, false, true, 0);

-- Expect: the category, and 8 festive + 1 new wall-art draft.
select category, count(*) as pieces, count(*) filter (where published) as live
from collection_items
where category in ('festive', 'wall-art')
group by category;
