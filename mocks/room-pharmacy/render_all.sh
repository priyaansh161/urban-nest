#!/bin/sh
# Final renders of the PharmVials sample counter, one after another (CPU Cycles, ~30 min in all).
B="/c/Program Files/Blender Foundation/Blender 5.2/blender.exe"; D="$(pwd -W)"
"$B" -b -P vial_station.py -- "$D/vial_station_v3.png" 200 | grep -E "DONE|Error"
"$B" -b -P label_station.py -- "$D/label_station_v2.png" 200 | grep -E "DONE|Error"
"$B" -b -P blister_station.py -- "$D/blister_station_v2.png" 200 | grep -E "DONE|Error"
"$B" -b blister_station.blend -P cards_closeup.py -- "$D/cards_closeup_v2.png" 200 | grep -E "DONE|Error"
"$B" -b -P counter_wall.py -- "$D/counter_wall_v2.png" 200 | grep -E "DONE|Error"
