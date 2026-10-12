-- ════════════════════════════════════════════════════════════════
--  More than one photograph per piece
-- ════════════════════════════════════════════════════════════════
--  WHY: the festive pieces (Diwali gifts and the like) are listed the
--  ordinary e-commerce way — photographs, no 3D model. One photograph is
--  not enough to judge a gift box or a diya set; a buyer wants the front,
--  the detail, the packaging, the thing in a room.
--
--  image_url stays the cover — the card, the share preview and the first
--  slide. gallery holds the photographs AFTER it, in the order shown.
--  Pieces that have a 3D model ignore gallery; the model is their view.
--
--  Safe to run twice. Nothing existing changes: every row gets an empty list.
-- ════════════════════════════════════════════════════════════════

alter table collection_items
  add column if not exists gallery text[] not null default '{}';

-- Expect 0 rows with photographs yet, and the column listed.
select count(*) filter (where cardinality(gallery) > 0) as pieces_with_gallery,
       count(*)                                         as all_pieces
from collection_items;
