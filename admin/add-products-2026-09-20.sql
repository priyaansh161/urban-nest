-- ═══════════════════════════════════════════════════════════════
--  URBAN NEST — 19 NEW PIECES + A CATEGORY FOR PAINTINGS
--  Run once: Supabase Dashboard → SQL Editor → New Query → paste → Run
--
--  Everything arrives UNPUBLISHED (drafts). Nothing shows on the site
--  until you publish each piece in Admin → Collection.
--
--  buy_link holds 'TODO-<ASIN>' so you can tell the pieces apart in the
--  admin. Replace each with your SiteStripe short link before publishing.
--
--  Safe to run once. Running it twice creates duplicates.
-- ═══════════════════════════════════════════════════════════════

-- ── The new category ───────────────────────────────────────────
-- Ten of these are paintings, and nothing existing holds them.
-- Rename it in the admin if you'd rather call it Tableaux or Canvases;
-- the slug is what the pieces are attached to, so leave that alone.
-- No ON CONFLICT here: the live table has no unique rule on slug, so the
-- guard is a plain NOT EXISTS. Same effect, and it works either way.
insert into collection_categories (slug, name, summary, about, sort_order, published)
select
  'wall-art',
  'Wall Art',
  'Canvases for the wall you look at most.',
  'A wall carries a room''s mood more than anything standing in it. These are printed canvases and framed pieces — some quiet, some loud — chosen for the wall you face from the sofa or wake up to.',
  10,
  true
where not exists (
  select 1 from collection_categories where slug = 'wall-art'
);

-- ── The pieces ─────────────────────────────────────────────────
insert into collection_items
  (name, description, category, section, price, buy_link, specs,
   primary_cta, in_stock, published, sort_order)
values

-- ── Wall art ──
('Krishna Canvas',
 'Krishna with his flute, printed large on wrapped canvas, for a wall that wants something still.',
 'wall-art', 'collection', '₹2,599', 'TODO-B0H3751BN8',
 '[["Material","Canvas on a wood frame"],["Dimensions","90 × 60 cm"],["Maker","The Hanging Story, Jaipur"],["Made in","India"]]'::jsonb,
 'affiliate', true, false, 170),

('Gond Art, Set of Six',
 'Six framed Gond prints meant to hang together, so one wall becomes the whole arrangement.',
 'wall-art', 'collection', '₹1,879', 'TODO-B0CVL59KZC',
 '[["Material","Print on 300 gsm paper, engineered-wood frames"],["Dimensions","43 × 33 cm each"],["Number of pieces","6"],["Made in","India"]]'::jsonb,
 'affiliate', true, false, 180),

('Sunrise Over Hills',
 'A sun rising behind abstract hills, gallery-wrapped over board so it hangs flat without a frame.',
 'wall-art', 'collection', '₹1,299', 'TODO-B0HH8TQ2C9',
 '[["Material","Canvas on 5.5 mm MDF"],["Dimensions","58 × 45 cm"],["Maker","ArtX, Jaipur"],["Made in","India"]]'::jsonb,
 'affiliate', true, false, 190),

('Countryside Scenery',
 'Blue irises in an open field — a calm piece that sits well against wood, white and grey.',
 'wall-art', 'collection', '₹2,495', 'TODO-B0HJHLNQPD',
 '[["Material","Framed cotton canvas, archival inks"],["Dimensions","70 × 50 cm"],["Maker","Paper Plane Design"],["Made in","India"]]'::jsonb,
 'affiliate', true, false, 200),

('Abstract Landscape',
 'Nature pulled apart into colour and shape, framed and ready to hang.',
 'wall-art', 'collection', '₹2,091', 'TODO-B0D17YSJPJ',
 '[["Material","Canvas in a wood frame"],["Dimensions","69 × 50 cm"],["Finish","Matte"],["Made in","India"]]'::jsonb,
 'affiliate', true, false, 210),

('Butterfly Canvas',
 'A square of colour and butterflies for a smaller wall, or for hanging as a pair.',
 'wall-art', 'collection', '₹1,569', 'TODO-B0CSWS97KP',
 '[["Material","Canvas in a wood frame"],["Dimensions","50 × 50 cm"],["Finish","Matte"],["Made in","India"]]'::jsonb,
 'affiliate', true, false, 220),

('Woman with Flower',
 'A figure and a flower held in the same few strokes, framed in wood.',
 'wall-art', 'collection', '₹2,136', 'TODO-B0DHCPTQQZ',
 '[["Material","Canvas in a wood frame"],["Finish","Matte"],["Maker","Artsense, Faridabad"],["Made in","India"]]'::jsonb,
 'affiliate', true, false, 230),

('Large Abstract Canvas',
 'Four feet of abstract colour in a black floater frame — the piece a room is arranged around.',
 'wall-art', 'collection', '₹12,995', 'TODO-B0H82Z1N3T',
 '[["Material","380 gsm canvas, black floater frame"],["Dimensions","122 × 81 cm"],["Maker","Paper Plane Design"],["Made in","India"]]'::jsonb,
 'affiliate', true, false, 240),

('Round Leaf Wall Art',
 'A round panel of raised leaves in a gold frame, for a narrow wall or above a console.',
 'wall-art', 'collection', '₹445', 'TODO-B0GZK61FFM',
 '[["Material","Engineered wood with a PVC frame"],["Dimensions","40 cm across"],["Shape","Round"],["Made in","India"]]'::jsonb,
 'affiliate', true, false, 250),

('Woman at the Piano',
 'A pianist built from thick palette-knife strokes, printed on textured canvas to keep the brushwork.',
 'wall-art', 'collection', '₹2,495', 'TODO-B0DYD1LBW7',
 '[["Material","Textured canvas, wood frame"],["Dimensions","75 × 50 cm"],["Maker","Paper Plane Design"],["Made in","India"]]'::jsonb,
 'affiliate', true, false, 260),

-- ── Amphorae ──
('Crumpled Bag Vase',
 'Ceramic folded to look like a paper bag someone has just set down, glazed to a high gloss.',
 'amphorae', 'collection', '₹1,347', 'TODO-B0DJ379F37',
 '[["Material","Ceramic"],["Dimensions","13 × 8 × 21 cm"],["Finish","Gloss, lilac"],["Made in","India"]]'::jsonb,
 'affiliate', true, false, 270),

('White Leaf Vase',
 'A low ceramic vase carved into a leaf, matte white, for a table that needs one quiet thing.',
 'amphorae', 'collection', '₹1,099', 'TODO-B0H4VM7PWR',
 '[["Material","Ceramic"],["Dimensions","18 × 18 × 12 cm"],["Finish","Matte white"],["Made in","India"]]'::jsonb,
 'affiliate', true, false, 280),

('Bow Vase',
 'A small vase tied into a bow and flocked so it reads as fabric rather than plastic.',
 'amphorae', 'collection', '₹999', 'TODO-B0H37WVW9S',
 '[["Material","Moulded polymer, flocked finish"],["Dimensions","12 × 12 × 20 cm"],["Colour","Sakura pink"],["Made in","India"]]'::jsonb,
 'affiliate', true, false, 290),

('Carved Elephant Vase',
 'An elephant carved in wood with a well cut into its back for a few stems.',
 'amphorae', 'collection', '₹1,299', 'TODO-B0H6SSZGDZ',
 '[["Material","Carved wood, lacquered"],["Dimensions","13 × 6 × 10 cm"],["Made in","India"]]'::jsonb,
 'affiliate', true, false, 300),

('Steel and Brass Vase',
 'A faceted black steel vase with brass dogwood branches standing in it, so it is full whether or not you add flowers.',
 'amphorae', 'collection', '₹2,999', 'TODO-B0FH598F98',
 '[["Material","Stainless steel with brass"],["Dimensions","17 × 15 × 20.5 cm"],["Maker","Behoma"],["Made in","India"]]'::jsonb,
 'affiliate', true, false, 310),

('Geometric Vase with Blooms',
 'A faceted vase that arrives already arranged, with handmade faux stems cut to its height.',
 'amphorae', 'collection', '₹1,399', 'TODO-B0FQNDPZ6W',
 '[["Material","Moulded polymer with silk flowers"],["Dimensions","14 × 14 × 44 cm, with the stems"],["Number of pieces","2"],["Made in","India"]]'::jsonb,
 'affiliate', true, false, 320),

-- ── Sculptures ──
('Hampi Stone Chariot',
 'The chariot at Hampi cut down to nine inches, in marble powder and resin with an antique bronze finish.',
 'sculptures', 'collection', '₹5,699', 'TODO-B0GCMGPVZ5',
 '[["Material","Marble powder with resin"],["Dimensions","23 × 16 × 18 cm"],["Weight","3.8 kg"],["Maker","Silaii"],["Made in","India"]]'::jsonb,
 'affiliate', true, false, 330),

('Rearing Horse',
 'A horse caught mid-rear, silver-plated over a resin core, heavy enough to hold a console on its own.',
 'sculptures', 'collection', '₹7,999', 'TODO-B0FMP5LFH9',
 '[["Material","999 silver plate over a resin core"],["Dimensions","18 × 9.5 × 25.5 cm"],["Weight","1.17 kg"],["Made in","India"]]'::jsonb,
 'affiliate', true, false, 340),

('Marble Dice',
 'A three-inch cube of white marble, hand-carved and veined, for a desk or a stack of books.',
 'sculptures', 'collection', '₹999', 'TODO-B0HFN7KMNF',
 '[["Material","White marble"],["Dimensions","7.5 cm cube"],["Weight","800 g"],["Made in","India"]]'::jsonb,
 'affiliate', true, false, 350);

-- ── Check ──────────────────────────────────────────────────────
-- Expect: new_drafts 19 · wall_art_pieces 10 · still_live 65
select
  (select count(*) from collection_items
     where sort_order between 170 and 350
       and buy_link like 'TODO-%')                     as new_drafts,
  (select count(*) from collection_items
     where category = 'wall-art')                      as wall_art_pieces,
  (select count(*) from collection_items
     where published = true)                           as still_live;
