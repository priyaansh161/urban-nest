#!/bin/bash
# the full headless bake (about 2 h): build, bake, previews, export -> living_v1.glb + living_v1.blend; then slim + compress
cd "$(dirname "$0")"
cat part1b.py part2.py part3.py part4.py > build_living_v1.py
"/c/Program Files/Blender Foundation/Blender 5.2/blender.exe" -b -P build_living_v1.py -- "$(pwd -W)" nopreview > bake_living.log 2>&1
node slim_room.mjs >> bake_living.log 2>&1
echo BAKE_FINISHED >> bake_living.log
