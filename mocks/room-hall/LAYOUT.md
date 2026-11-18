# The hall: living + dining, a Noida high-rise 3BHK (17 Nov 2026)

No reference photo: the layout follows how Noida / Greater Noida 3BHK plans are drawn (one rectangular living-dining hall,
about 3.4-3.6 m wide x 7-8 m long; the living end opens to the balcony, the dining end sits by the kitchen and the main
door; a false ceiling zones the two without a partition). Research notes: Nirala Aspire (living 10'4" x 17'), Northwind
Sanctuary (living-dining 5.8 x 3.35 m onto the big balcony), Gaur Alaris (dining by the kitchen and living); design
guides: false-ceiling trays to zone living vs dining, TV on the long wall facing the sofa, keep the TV unit close to
the wall with light finishes.

## Shell (Blender metres; x across, y along, z up)
- Hall 3.5 x 7.8 m, slab 3.0 m; x -1.75..1.75, y -3.9 (main-door end) .. 3.9 (balcony end).
- Floor: 80 cm beige vitrified tiles (as the kitchen), tile skirting.
- Balcony end (y 3.9): 2.5 m aluminium sliding door (3 panels, dark grey), 2.45 m high; balcony 1.4 m deep beyond,
  glass railing, potted plants; towers outside. Taupe drapes + sheers on a black rod, gathered both sides.
- Left wall (x -1.75): kitchen opening (y -3.35..-2.45, 2.25 high, a glimpse of the Oak Kitchen's navy/oak/quartz
  beyond); mandir unit (y -2.05..-1.15); passage to the bedrooms (y -0.75..0.25, a corridor and a bedroom door);
  the L-sofa along the living part, wall art over it; split AC high on this wall near the balcony.
- Right wall (x 1.75): shoe cabinet + round brass mirror by the door (y -3.8..-2.9); crockery unit (y -2.55..-0.95:
  oak base, quartz top, marble niche, glass-front uppers with crockery); TV wall (y 1.15..3.55: grey marble centre
  panel, fluted oak each side, floating oak console with a glow under it, 55" TV, soundbar).
- Main-door end (y -3.9): teak main door (x 0.50..1.55) with brass handle; wall clock to its left.
- False ceiling 25 cm drop (underside 2.75): two recessed trays with warm coves, living (x -1.15..1.15, y 0.55..3.35)
  and dining (x -0.95..0.75, y -3.1..-0.95); downlights in the band.

## Furniture
- Staging (built here, no dot): dining table 1.8 x 0.9 walnut + 6 upholstered chairs, rug in the living, curtains,
  TV + soundbar, plants, door mat, crockery, AC.
- Products (placements.json, dots): Torque L-sofa, Enfurnish coffee table, peacock urli, arc floor lamp, abstract
  canvas, running horses on the console, linear glass chandelier over the table, wall clock, brass Ganesh in the
  mandir, soapstone vase on the shoe cabinet.

## Pipeline
build_hall_v1.py (kitchen pipeline: grid shells, LM_ objects, one Cycles diffuse bake, lightmaps as emissive);
`wb` = workbench layout shots, `quick` = Cycles previews without the bake, no flag = full bake (overnight, ~2-3 h).
