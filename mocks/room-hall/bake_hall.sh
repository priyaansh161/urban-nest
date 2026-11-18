#!/bin/bash
# full bake + export of the hall (living + dining). ~2-3 h, takes the whole CPU.
cd "$(dirname "$0")"
python assemble.py
date; "/c/Program Files/Blender Foundation/Blender 5.2/blender.exe" -b -P build_hall_v1.py -- "$(cygpath -w "$PWD")" > bake_hall.log 2>&1; date
grep -iE "Traceback|Error|BAKE gain|DONE" bake_hall.log | tail -5
