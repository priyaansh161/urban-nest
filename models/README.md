# 3D models (.glb)

Drop Meshy exports here. **Export format: GLB** — that is what the viewer reads.

    Meshy → Export → GLB → save into this folder

Then in **Admin → Collection**, put the path in *3D Model URL*:

    models/chandelier.glb

Leave it empty and the item falls back to its photo, so a piece without a
model still lists correctly.

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
