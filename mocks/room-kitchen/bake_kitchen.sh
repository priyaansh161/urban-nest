#!/bin/bash
# full bake + export, then the web copy. ~2 h.
cd "$(dirname "$0")"
date; "/c/Program Files/Blender Foundation/Blender 5.2/blender.exe" -b -P build_kitchen_v1.py -- "$(cygpath -w $PWD)" > bake_kitchen.log 2>&1; date
grep -iE "Traceback|Error|BAKE gain|DONE" bake_kitchen.log | tail -5
