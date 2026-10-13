/* Five clocks and one pendant light, added 2026-09-26.
   Details taken from the Amazon listings on that date.

   They go in UNPUBLISHED on purpose: each one still needs its photograph,
   its SiteStripe buy link and (if it gets one) its 3D model, all of which
   are added in the admin. Publish from there once a piece is complete —
   an item with no picture and no buy button is a dead tile.

   The ASIN and the Amazon image are noted above each row so the admin work
   is a copy-and-paste job. */
insert into collection_items
  (name, description, category, section, price, specs, affiliate_seller_id,
   primary_cta, published, coming_soon, in_stock, sort_order)
values

/* B0G1SQZCC8 · ₹599 · https://m.media-amazon.com/images/I/51gqbANwxVL._SL1024_.jpg */
('HOME SKILL Vintage Twin Bell Alarm Clock 11.5 cm | Loud Non-Ticking Bedside Clock for Bedroom & Study',
 'A matte navy metal alarm clock with twin bells, a carrying handle and silver-tipped legs. The hammer-and-bell alarm is loud enough for the heaviest sleeper, while the quartz sweep movement keeps the room silent the rest of the night.',
 'timepieces', 'collection', '₹599',
 '[["Brand","HOME SKILL"],["Colour","Dark Blue Metal"],["Display Type","Analog"],["Product Dimensions","12W x 16H Centimeters"],["Power Source","1x AA Battery (not included)"],["Special Feature","Twin bell alarm, silent non-ticking movement, night light"]]'::jsonb,
 '7d0dd3e4-02ec-4c2d-a86e-8c78b90aecfe', 'affiliate', false, false, true, 0),

/* B0H45BHQMM · ₹1,999 (M.R.P. ₹2,999) · https://m.media-amazon.com/images/I/41X4+Zcy5-L._SX569_.jpg */
('HIRVALL Extra Large Metal Wall Clock 60 cm | Silent Quartz Statement Clock for Living Room',
 'A 60 cm geometric metal clock built to be the one thing on a large wall. The open frame reads as wall art from across the room, and the quartz movement runs without a tick.',
 'timepieces', 'collection', '₹1,999',
 '[["Brand","HIRVALL"],["Colour","Black"],["Display Type","Analog"],["Product Dimensions","60W x 60H Centimeters"],["Power Source","Battery Powered"],["Special Feature","Silent Clock, Metal Construction, Easy Installation"]]'::jsonb,
 '7d0dd3e4-02ec-4c2d-a86e-8c78b90aecfe', 'affiliate', false, false, true, 0),

/* B0F3D95559 · ₹1,399 · https://m.media-amazon.com/images/I/81VDV5wEijL._SL1500_.jpg */
('Arabs Stylish Metal Wall Clock 40 cm | Antique-Modern Analog Clock for Living Room & Office',
 'A 40 cm matte black metal clock that borrows an antique face and sets it in a modern frame. Scratch-resistant, silent-sweep, and at home above a console or beside wall art.',
 'timepieces', 'collection', '₹1,399',
 '[["Brand","Arabs"],["Colour","Matte Black"],["Display Type","Analog"],["Product Dimensions","40 cm diameter"],["Power Source","1 AA battery (not included)"],["Special Feature","Silent Sweep Mechanism, Easy to Hang, Durable Metal Body"]]'::jsonb,
 '7d0dd3e4-02ec-4c2d-a86e-8c78b90aecfe', 'affiliate', false, false, true, 0),

/* B0BVLL412Y · ₹2,649 · https://m.media-amazon.com/images/I/61xMSawugbL._SL1500_.jpg */
('KENJIEY Stainless Steel Retro Flip Clock 23 cm | Mechanical Gear-Operated Desk Clock for Home & Office',
 'A mechanical flip clock in a stainless steel frame, where the minutes fall over one card at a time. The numerals are large enough to read across a room, and the soft flip is the only sound it makes.',
 'timepieces', 'collection', '₹2,649',
 '[["Brand","KENJIEY"],["Colour","White"],["Display Type","Digital flip"],["Product Dimensions","23.1W x 18H Centimeters"],["Power Source","1 x D battery (not included)"],["Special Feature","Mechanical gear-operated flip display, 12-hour AM/PM"]]'::jsonb,
 '7d0dd3e4-02ec-4c2d-a86e-8c78b90aecfe', 'affiliate', false, false, true, 0),

/* B0C8J979PX · ₹233 · https://m.media-amazon.com/images/I/61G+D7XKsUL._SL1000_.jpg */
('SKYLACE Vintage Twin Bell Alarm Clock 16 cm | LED Night Light Table Clock for Bedroom',
 'A small twin bell alarm clock in a brushed silver finish, with a backlight for reading the time at night. The alarm builds in volume rather than starting at full blast.',
 'timepieces', 'collection', '₹233',
 '[["Brand","SKYLACE"],["Colour","Silver"],["Display Type","Analog"],["Product Dimensions","11.5W x 16H Centimeters"],["Power Source","Battery Powered"],["Special Feature","Twin bell alarm, LED night light, silent sweep seconds"]]'::jsonb,
 '7d0dd3e4-02ec-4c2d-a86e-8c78b90aecfe', 'affiliate', false, false, true, 0),

/* B0HGM4WMT5 · ₹4,299 · https://m.media-amazon.com/images/I/61QXEAJLoBL._SL1024_.jpg */
('Craftflux Creation Double Umbrella Rattan Pendant Light 66 cm | Modern Ceiling Chandelier for Living & Dining',
 'A wide woven rattan pendant in two stacked umbrella shades, throwing patterned light across the ceiling. At 66 cm across it hangs as the centrepiece over a dining table or a seating group.',
 'lighting', 'collection', '₹4,299',
 '[["Brand","Craftflux Creation"],["Colour","Off White"],["Material","Rattan"],["Light fixture form","Pendant"],["Product Dimensions","66L x 66W x 25H Centimeters"],["Power Source","Corded Electric"],["Style","Modern"]]'::jsonb,
 '7d0dd3e4-02ec-4c2d-a86e-8c78b90aecfe', 'affiliate', false, false, true, 0);
