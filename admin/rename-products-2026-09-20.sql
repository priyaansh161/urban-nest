-- ═══════════════════════════════════════════════════════════════
--  URBAN NEST — RENAME THE 19 NEW PIECES TO THE HOUSE FORMAT
--  Run after add-products-2026-09-20.sql, in the SQL Editor.
--
--  The names first written were short gallery labels ("Marble Dice"),
--  which dropped the brand and the size. Every piece on the site reads
--      <Brand> <What it is> <size> | <where it goes, what it suits>
--  and both halves carry something a buyer needs, so these are rewritten
--  to match. Every name below names its maker and its size.
--
--  Matched on buy_link, which still holds TODO-<ASIN> and is unique to
--  each piece. Run this BEFORE you replace those with SiteStripe links;
--  if you have already replaced some, those are skipped and the check at
--  the bottom will show fewer than 19.
--
--  Safe to run more than once.
-- ═══════════════════════════════════════════════════════════════

update collection_items set name =
  'The Hanging Story Krishna Canvas Wall Painting 90 x 60 cm | Blue Krishna with Flute Spiritual Wall Art for Living Room & Bedroom'
  where buy_link = 'TODO-B0H3751BN8';

update collection_items set name =
  'kotart Gond Art Wall Paintings 43 x 33 cm, Set of 6 | Framed Tribal Art Prints for Living Room & Home Decor'
  where buy_link = 'TODO-B0CVL59KZC';

update collection_items set name =
  'ArtX Modern Abstract Sunrise Mountain Canvas Wall Art 58 x 45 cm | Gallery Wrapped Landscape Painting for Living Room'
  where buy_link = 'TODO-B0HH8TQ2C9';

update collection_items set name =
  'PAPER PLANE DESIGN Countryside Scenery Framed Canvas 70 x 50 cm | Blue Irises Landscape Painting for Living Room & Bedroom'
  where buy_link = 'TODO-B0HJHLNQPD';

update collection_items set name =
  'Artsense Nature-Inspired Abstract Canvas Painting 69 x 50 cm | Framed Multicolor Wall Art for Living Room & Bedroom'
  where buy_link = 'TODO-B0D17YSJPJ';

update collection_items set name =
  'Artsense Colourful Butterfly Abstract Canvas Painting 50 x 50 cm | Framed Square Wall Art for Living Room & Home Decor'
  where buy_link = 'TODO-B0CSWS97KP';

update collection_items set name =
  'Artsense Woman with Flower Abstract Canvas Wall Art 20 x 30 Inch (50 x 71 cm) | Framed Multicolor Painting for Living Room & Bedroom'
  where buy_link = 'TODO-B0DHCPTQQZ';

update collection_items set name =
  'PAPER PLANE DESIGN Modern Abstract Canvas Painting 122 x 81 cm (32 x 48 Inch) | Large Statement Wall Art with Black Floater Frame'
  where buy_link = 'TODO-B0H82Z1N3T';

update collection_items set name =
  'SAF 3D Textured Leaf Round Wall Art 40 cm (16 Inch) | Golden Framed Botanical Wall Painting for Living Room & Office'
  where buy_link = 'TODO-B0GZK61FFM';

update collection_items set name =
  'PAPER PLANE DESIGN Woman Playing Piano Canvas Painting 75 x 50 cm | Palette Knife Style Modern Art, Framed and Ready to Hang'
  where buy_link = 'TODO-B0DYD1LBW7';

update collection_items set name =
  'Glimpse Homes Crumpled Bag Ceramic Vase 8 Inch (13 x 8 x 21 cm) | Gloss Lilac Decorative Flower Vase for Table & Shelf'
  where buy_link = 'TODO-B0DJ379F37';

update collection_items set name =
  'Art Street White Leaf Ceramic Vase 18 x 18 x 12 cm | Matte Minimalist Tabletop Centerpiece Vase for Home Decor'
  where buy_link = 'TODO-B0H4VM7PWR';

update collection_items set name =
  'VIKSON INTERNATIONAL Coquette Bow Vase 12 x 12 x 20 cm | Flocked Sakura Pink Decorative Vase for Vanity, Desk & Shelf'
  where buy_link = 'TODO-B0H37WVW9S';

update collection_items set name =
  'SHIRSH NOVEXA Handcrafted Wooden Elephant Vase 13 x 6 x 10 cm | Carved Decorative Bud Vase for Home & Office Decor'
  where buy_link = 'TODO-B0H6SSZGDZ';

update collection_items set name =
  'BEHOMA Designer Stainless Steel Vase with Brass Dogwood 17 x 15 x 20.5 cm | Black Textured Decorative Vase for Living Room'
  where buy_link = 'TODO-B0FH598F98';

update collection_items set name =
  'NDECORS Geometric Vase with Artificial Flower Bouquet 14 x 14 x 44 cm | Handmade Faux Floral Arrangement for Living Room & Gifting'
  where buy_link = 'TODO-B0FQNDPZ6W';

update collection_items set name =
  'SILAII Hampi Stone Chariot Sculpture 9 Inch (23 x 16 x 18 cm) | Traditional Indian Temple Art Showpiece for Home & Office'
  where buy_link = 'TODO-B0GCMGPVZ5';

update collection_items set name =
  'Dev Aastha 999 Silver Plated Rearing Horse Statue 18 x 9.5 x 25.5 cm | Vastu Showpiece for Success & Home Decor'
  where buy_link = 'TODO-B0FMP5LFH9';

update collection_items set name =
  'Kiyana Decor Handcrafted White Marble Dice Cube 3 Inch (7.5 cm) | Sculptural Showpiece for Desk, Shelf & Gifting'
  where buy_link = 'TODO-B0HFN7KMNF';

-- ── Check ──────────────────────────────────────────────────────
-- Expect: renamed 19
select count(*) as renamed
from collection_items
where buy_link like 'TODO-%'
  and name like '%|%';
