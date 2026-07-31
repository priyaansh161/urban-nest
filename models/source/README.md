# Raw Meshy exports (not deployed)

Drop the **unoptimised** GLB straight from Meshy here. Nothing in this folder
ships — it is gitignored, so a 100 MB export costs visitors nothing.

The optimised version goes one level up, in `models/`, and that is the one the
site loads.

## Why this folder exists

Meshy exports are built for editing, not for the web. The first chandelier
came in at **101.8 MB / 1.95 million triangles** — around ten minutes to
download on a normal connection. Optimised it is **7 MB**, and the difference
is invisible on a product tile.

Most of the weight is geometry, not textures. Meshy models a chandelier's
crystals as thousands of separate solids; the web needs a fraction of that.
