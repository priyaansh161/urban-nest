# 3D models (.glb)

**Export format: GLB** — that is what the viewer reads. A .gltf leaves its
textures in separate files the viewer cannot reach.

Raw Meshy exports are 15–100 MB and go in `models/source/`, which is
gitignored. Compress before uploading — this is the same line the admin's
*3D Model URL* field offers to copy, and it runs from any folder:

    node "C:\Users\priya\OneDrive\Projects\urban-nest\tools\compress-model.mjs" "C:\Users\priya\OneDrive\Projects\urban-nest\models\source\whatever-raw.glb"

Or, with a terminal already sitting in the project, the short form:

    cd tools
    node compress-model.mjs ../models/source/whatever-raw.glb

Both run the same script. It writes `models/whatever.glb` — `-raw` dropped from
the name. The chandelier goes 26.16 MB → 1.57 MB with
every one of its 168,703 triangles intact. Then open `tools/verify.html`,
pick the file, and watch it render — see below for why that step is not
optional.

Upload the compressed file through **Admin → Collection**, using the upload
button next to *3D Model URL*. It goes into the Supabase `models` bucket and
fills the field with the public URL, so adding a piece needs no site deploy.

Leave the field empty and the item falls back to its photo, so a piece without
a model still lists correctly.

## Verify by rendering, never by re-parsing

A .glb can report the right triangle count, the right bounding box and a clean
header, and still never appear on screen. `EXT_meshopt_compression` does
exactly that to model-viewer 3.5 — it downloads to 100%, fires `loadfailure`,
shows nothing. The chandelier shipped broken for two days because it was
checked by re-parsing the file. `tools/verify.html` exists to close that gap.

Positions that look like ±32767 are `KHR_mesh_quantization`, not corruption.
Compare `getDimensions()` against the raw export instead — four decimal places
should match.

## Keep them small

These download in full before anything renders, so weight matters more than
it does for images.

| | Target |
|---|---|
| Good | under 3 MB |
| Acceptable | 3–6 MB |
| Too heavy | over 8 MB |

In Meshy, lower the polygon count and texture resolution before exporting —
a chandelier with every crystal modelled will be enormous, and on a product
tile nobody can see the difference.
