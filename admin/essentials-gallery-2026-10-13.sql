-- Essentials: photographs instead of 3D (13 Oct 2026)
--  Each piece gets the photo set from its own Amazon listing (the buy link),
--  shown after its cover photo. The cover (image_url) and spline_url are left
--  as they are; the Essentials page simply stops opening the 3D scene.
--  Run once in Supabase -> SQL Editor.

-- Multi-Purpose Soap Sanitizer Dispenser for Bathroom or Kitchen
update collection_items set gallery = array['https://m.media-amazon.com/images/I/5197521RM1L._SL1280_.jpg', 'https://m.media-amazon.com/images/I/61bpeGT8tJL._SL1280_.jpg', 'https://m.media-amazon.com/images/I/61hMcmVgroL._SL1280_.jpg', 'https://m.media-amazon.com/images/I/61ZkZPkZVsL._SL1500_.jpg', 'https://m.media-amazon.com/images/I/61VRPofTUHL._SL1024_.jpg', 'https://m.media-amazon.com/images/I/51sv747WUaL.jpg', 'https://m.media-amazon.com/images/I/31S4K52+BwL.jpg']::text[]
  where id = 'ac866c8f-ac30-4c44-81b8-fa8ab784ef67' and section = 'essentials';

-- HmiL-U Wall Mounted No Scratch Soft Silicone Toilet Cleaner Bowl Brush
update collection_items set gallery = array['https://m.media-amazon.com/images/I/61TtsUlnETL._SL1000_.jpg', 'https://m.media-amazon.com/images/I/61YPAkEQZCL._SL1000_.jpg', 'https://m.media-amazon.com/images/I/61AQd+m-G7L._SL1000_.jpg', 'https://m.media-amazon.com/images/I/51yXjzRNRJL._SL1001_.jpg', 'https://m.media-amazon.com/images/I/51TO5hc1AJL._SL1004_.jpg', 'https://m.media-amazon.com/images/I/51-OwS38BaL._SL1000_.jpg']::text[]
  where id = '71be9a23-33ab-498e-b517-61f0352b4997' and section = 'essentials';

-- USF Orizon Towel Ring Holder for Bathroom
update collection_items set gallery = array['https://m.media-amazon.com/images/I/81aIsg0QZQL._SL1500_.jpg', 'https://m.media-amazon.com/images/I/81mgAAiuUFL._SL1500_.jpg', 'https://m.media-amazon.com/images/I/81qQErISYXL._SL1500_.jpg', 'https://m.media-amazon.com/images/I/81UUauSyFGL._SL1500_.jpg', 'https://m.media-amazon.com/images/I/81hwnKeVOnL._SL1500_.jpg', 'https://m.media-amazon.com/images/I/817TmocKzzL._SL1500_.jpg']::text[]
  where id = '3209fdd3-7fbf-43d1-8cc2-0fa6858b0971' and section = 'essentials';

-- HomeCloud Memory Foam Bath Mat, Cobblestone Bathroom Rectangular Rugs 
update collection_items set gallery = array['https://m.media-amazon.com/images/I/71nOH09GIVL._SL1500_.jpg', 'https://m.media-amazon.com/images/I/71XMkKLSuWL._SL1500_.jpg', 'https://m.media-amazon.com/images/I/71g-r7UjeAL._SL1500_.jpg', 'https://m.media-amazon.com/images/I/517rUO3XHiL.jpg', 'https://m.media-amazon.com/images/I/81MLPLIf4qL._SL1500_.jpg', 'https://m.media-amazon.com/images/I/71AqaxRArFL._SL1500_.jpg']::text[]
  where id = 'a88c6f8c-08da-43df-9e88-3ef913f7e8ac' and section = 'essentials';

-- ACHRO Self Adhesive and Wall Mount Stainless Steel Toilet Paper Holder
update collection_items set gallery = array['https://m.media-amazon.com/images/I/41YqOPR9L0L._SL1500_.jpg', 'https://m.media-amazon.com/images/I/512jE5EgMQL._SL1280_.jpg', 'https://m.media-amazon.com/images/I/71xvub8OTjL._SL1500_.jpg', 'https://m.media-amazon.com/images/I/61A8n1MYpOL._SL1500_.jpg', 'https://m.media-amazon.com/images/I/81S0L0EFyrL._SL1500_.jpg', 'https://m.media-amazon.com/images/I/41xJF4iFaDL.jpg', 'https://m.media-amazon.com/images/I/81V7w5gUwaL._SL1500_.jpg']::text[]
  where id = 'df0e3f6a-e390-4bf0-a6c6-53d834930869' and section = 'essentials';

-- Wall Shelf Organiser
update collection_items set gallery = array['https://m.media-amazon.com/images/I/61ocRcYmuJL._SL1254_.jpg', 'https://m.media-amazon.com/images/I/71qSS8Vj5FL._SL1254_.jpg', 'https://m.media-amazon.com/images/I/71+o9GZcQqL._SL1353_.jpg', 'https://m.media-amazon.com/images/I/71AAUU4+jpL._SL1254_.jpg', 'https://m.media-amazon.com/images/I/71MAOh5q5QL._SL1254_.jpg', 'https://m.media-amazon.com/images/I/71N7Tu-0qpL._SL1254_.jpg', 'https://m.media-amazon.com/images/I/61tdYLMXZnL._SL1125_.jpg']::text[]
  where id = 'f209aed3-b6f6-4754-a417-84d24fb7965f' and section = 'essentials';

-- VHKD PVC Bathroom Door Bath mat Anti Slip Skid
update collection_items set gallery = array['https://m.media-amazon.com/images/I/71ATc0FY0lL._SL1500_.jpg', 'https://m.media-amazon.com/images/I/81nKFUC-6sL._SL1500_.jpg', 'https://m.media-amazon.com/images/I/71o-UIifZlL._SL1500_.jpg', 'https://m.media-amazon.com/images/I/71W84Auca9L._SL1500_.jpg', 'https://m.media-amazon.com/images/I/71GrxwuSh-L._SL1500_.jpg', 'https://m.media-amazon.com/images/I/71wkwUbLq2L._SL1500_.jpg', 'https://m.media-amazon.com/images/I/71hpIB9DbEL._SL1500_.jpg']::text[]
  where id = '089708b7-fff5-40af-a98e-d375cec252d1' and section = 'essentials';

-- HomeCloud Rubber Kitchen Mats for Floor Set of 2 Pcs|Non-Skid, Soft Ab
update collection_items set gallery = array['https://m.media-amazon.com/images/I/61qdR-NBPkL._SL1179_.jpg', 'https://m.media-amazon.com/images/I/61wZc8noh6L._SL1000_.jpg', 'https://m.media-amazon.com/images/I/51Lg20np5BL._SL1187_.jpg', 'https://m.media-amazon.com/images/I/71FNqM8EV+L._SL1179_.jpg', 'https://m.media-amazon.com/images/I/71dGwWD+xDL._SL1179_.jpg', 'https://m.media-amazon.com/images/I/8111LWgufAL._SL1500_.jpg']::text[]
  where id = '643d1344-6c58-40ab-8c2c-3317ed6a4594' and section = 'essentials';

-- Premium 2 In 1 Glass Oil Dispenser For Kitchen
update collection_items set gallery = array['https://m.media-amazon.com/images/I/61VAq8aQKkL._SL1500_.jpg', 'https://m.media-amazon.com/images/I/71K-oKLuoyL._SL1500_.jpg', 'https://m.media-amazon.com/images/I/71Sc83KiO8L._SL1500_.jpg', 'https://m.media-amazon.com/images/I/71FRb-KCP6L._SL1500_.jpg', 'https://m.media-amazon.com/images/I/61eI3omocQL._SL1500_.jpg', 'https://m.media-amazon.com/images/I/81ow99kPTKL._SL1500_.jpg', 'https://m.media-amazon.com/images/I/512tcN3HzfL.jpg']::text[]
  where id = 'b16d9948-b32b-4ad7-b55d-7adbb8273290' and section = 'essentials';

-- Wooden Spatula Rest
update collection_items set gallery = array['https://m.media-amazon.com/images/I/71aSRYIbEbL._SL1000_.jpg', 'https://m.media-amazon.com/images/I/71rhwtUsnDL._SL1000_.jpg', 'https://m.media-amazon.com/images/I/71eDEfv8-pL.jpg', 'https://m.media-amazon.com/images/I/61wxL0M9+FL._SL1000_.jpg', 'https://m.media-amazon.com/images/I/61t8IQA67oL._SL1000_.jpg', 'https://m.media-amazon.com/images/I/6131MN8g7QL._SL1000_.jpg']::text[]
  where id = '2759a7b9-b18d-4395-8ae1-69d02c064ab5' and section = 'essentials';

-- Butter Dish with Lid, Durable Butter Container for Fridge
update collection_items set gallery = array['https://m.media-amazon.com/images/I/61HIhWeGPBL._SL1500_.jpg', 'https://m.media-amazon.com/images/I/61qkOfvPuvL._SL1500_.jpg', 'https://m.media-amazon.com/images/I/51ov42wzZwL._SL1500_.jpg', 'https://m.media-amazon.com/images/I/61jEQzRe+XL._SL1500_.jpg', 'https://m.media-amazon.com/images/I/71bDWSkFEPL._SL1500_.jpg', 'https://m.media-amazon.com/images/I/61f5t9QozJL._SL1500_.jpg']::text[]
  where id = '3bc04eb5-4cd9-4a4b-888d-8044c7fea590' and section = 'essentials';

-- Coffee Mugs
update collection_items set gallery = array['https://m.media-amazon.com/images/I/71hPULbCwdL._SL1500_.jpg', 'https://m.media-amazon.com/images/I/618ccliHiQL._SL1500_.jpg', 'https://m.media-amazon.com/images/I/61w4gF+3mtL._SL1500_.jpg', 'https://m.media-amazon.com/images/I/81kl0-IiU9L._SL1500_.jpg', 'https://m.media-amazon.com/images/I/61h5TUAdvRL._SL1500_.jpg', 'https://m.media-amazon.com/images/I/71Jp-5FgSnL._SL1500_.jpg', 'https://m.media-amazon.com/images/I/61SfjIgv2eL._SL1500_.jpg']::text[]
  where id = '04283da4-9167-45c5-9612-437410f87051' and section = 'essentials';

-- Green Knife Set
update collection_items set gallery = array['https://m.media-amazon.com/images/I/61XP4fTvAZL.jpg', 'https://m.media-amazon.com/images/I/512V1zlZKyL.jpg', 'https://m.media-amazon.com/images/I/51fHxAlGw-L.jpg', 'https://m.media-amazon.com/images/I/61svLclkUEL.jpg', 'https://m.media-amazon.com/images/I/61Kq8uivh0L.jpg']::text[]
  where id = 'c65af49f-f8d4-402c-981e-6af2ae270066' and section = 'essentials';

-- Pickle Jar With Spoons | Achar Jar Set for Dining Table
update collection_items set gallery = array['https://m.media-amazon.com/images/I/71aMB1f01TL._SL1500_.jpg', 'https://m.media-amazon.com/images/I/71cMEu0YAiL._SL1500_.jpg', 'https://m.media-amazon.com/images/I/71GPjIxe9QL._SL1500_.jpg', 'https://m.media-amazon.com/images/I/71czoeClXFL._SL1500_.jpg', 'https://m.media-amazon.com/images/I/61wl4Jqxt4L._SL1500_.jpg', 'https://m.media-amazon.com/images/I/61r9RKUw3mL._SL1500_.jpg', 'https://m.media-amazon.com/images/I/617q6cmdGcL._SL1500_.jpg']::text[]
  where id = 'ace72caf-f295-447d-9d8e-afe036d494dc' and section = 'essentials';

-- Primeway® PP Spoon Rest for Home & Kitchen
update collection_items set gallery = array['https://m.media-amazon.com/images/I/515bKIcW4QL._SL1200_.jpg', 'https://m.media-amazon.com/images/I/51vJ4dt-tLL._SL1200_.jpg', 'https://m.media-amazon.com/images/I/71kyzfdpRGL._SL1200_.jpg', 'https://m.media-amazon.com/images/I/71G2F0B7ZAL._SL1200_.jpg']::text[]
  where id = '5c8fc071-b2a2-44c6-a097-9af06f0f3df3' and section = 'essentials';

-- HomeWiz Hung Curd Maker 1100ml with Fine Steel Mesh
update collection_items set gallery = array['https://m.media-amazon.com/images/I/818UG2S-R-L._SL1500_.jpg', 'https://m.media-amazon.com/images/I/71v34UKsK5L._SL1500_.jpg', 'https://m.media-amazon.com/images/I/71+36JIXztL._SL1500_.jpg', 'https://m.media-amazon.com/images/I/717id9rfpPL._SL1500_.jpg', 'https://m.media-amazon.com/images/I/813PjMQ0ouL._SL1500_.jpg', 'https://m.media-amazon.com/images/I/81JOy3v+0TL._SL1500_.jpg', 'https://m.media-amazon.com/images/I/71mx57EfXpL._SL1500_.jpg']::text[]
  where id = 'b4bd8136-6639-49d6-ab75-397f4027d88e' and section = 'essentials';

-- OrganizeMee Garbage Bag Holder & Dispenser - Wall Mounted Trash Bag Or
update collection_items set gallery = array['https://m.media-amazon.com/images/I/71k4dQxUYML._SL1500_.jpg', 'https://m.media-amazon.com/images/I/71rYwLuI04L._SL1500_.jpg', 'https://m.media-amazon.com/images/I/81tO4Kbx2ML._SL1500_.jpg', 'https://m.media-amazon.com/images/I/71FXboE7XzL._SL1500_.jpg', 'https://m.media-amazon.com/images/I/71LBS6CnPqL._SL1500_.jpg', 'https://m.media-amazon.com/images/I/71LLT5eJOSL._SL1500_.jpg', 'https://m.media-amazon.com/images/I/71XIwBKLNAL._SL1500_.jpg']::text[]
  where id = '6970f7d6-2c64-4e7f-a0c3-41e8de7d56b0' and section = 'essentials';

-- TEX-RO Utensils Drying Rack|Dish Drying Rack with Drainer Tray
update collection_items set gallery = array['https://m.media-amazon.com/images/I/812MpnrhpqL._SL1500_.jpg', 'https://m.media-amazon.com/images/I/71giAOIKQuL._SL1500_.jpg', 'https://m.media-amazon.com/images/I/71rw55W7DaL._SL1500_.jpg', 'https://m.media-amazon.com/images/I/81BtGSgQ8KL._SL1500_.jpg', 'https://m.media-amazon.com/images/I/81-TPi6UH5L._SL1500_.jpg', 'https://m.media-amazon.com/images/I/71X0Xw1GBIL._SL1500_.jpg', 'https://m.media-amazon.com/images/I/71W2GQhgVtL._SL1500_.jpg']::text[]
  where id = '6410bafe-88fe-46b1-b92b-1942b384949d' and section = 'essentials';

-- Vintageware® Wooden Kitchen Tissue Roll Holder Stand
update collection_items set gallery = array['https://m.media-amazon.com/images/I/61VKFyyGAHL._SL1024_.jpg', 'https://m.media-amazon.com/images/I/5160nKFytjL._SL1024_.jpg', 'https://m.media-amazon.com/images/I/61xLjnd-UQL._SL1024_.jpg', 'https://m.media-amazon.com/images/I/419eCYDQR1L._SL1024_.jpg', 'https://m.media-amazon.com/images/I/61S4NPzTsBL._SL1024_.jpg', 'https://m.media-amazon.com/images/I/51Z0JzF1JgL._SL1024_.jpg', 'https://m.media-amazon.com/images/I/51cqn37kVCL._SL1080_.jpg']::text[]
  where id = '7419de18-ae70-4a51-8835-6e8645a84a38' and section = 'essentials';

-- HomeCloud Dish Drying Mat for Kitchen Counter Hide Stain Super Absorbe
update collection_items set gallery = array['https://m.media-amazon.com/images/I/51YW7sawdQL.jpg', 'https://m.media-amazon.com/images/I/81pF8VPWYBL._SL1500_.jpg', 'https://m.media-amazon.com/images/I/61yCgrssF9L.jpg', 'https://m.media-amazon.com/images/I/81l6F9i5A6L._SL1500_.jpg']::text[]
  where id = '3e046e4a-7300-495a-b6b3-3235b78f4b0c' and section = 'essentials';

select name, cardinality(gallery) as photos from collection_items where section = 'essentials' order by category, sort_order;
