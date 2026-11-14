#!/bin/bash
# 1 Nov 2026 overnight: bake the Sunday Bedroom and the Quiet Bath with their new staging, slim/compress both,
# then shut the computer down (he asked). Nothing is published or deployed.
B="/c/Program Files/Blender Foundation/Blender 5.2/blender.exe"
R="C:/Users/priya/OneDrive/Projects/urban-nest"
LOG="$R/mocks/overnight_1101.log"
cd "$R"
echo "START $(date)" > "$LOG"
"$B" -b -P "$R/mocks/room-bedroom/build_bedroom_v1.py" -- "$R/mocks/room-bedroom" >> "$R/mocks/room-bedroom/bake_1101.log" 2>&1
echo "BEDROOM baked $(date): $(grep -E 'DONE|Traceback|Error' "$R/mocks/room-bedroom/bake_1101.log" | tail -3)" >> "$LOG"
node mocks/room-bedroom/slim_room.mjs >> "$LOG" 2>&1
echo "BEDROOM slimmed $(date)" >> "$LOG"
"$B" -b -P "$R/mocks/room-pilot/build_bath_v7.py" -- "$R/mocks/room-pilot" >> "$R/mocks/room-pilot/bake_1101.log" 2>&1
echo "BATH baked $(date): $(grep -E 'DONE|Traceback|Error' "$R/mocks/room-pilot/bake_1101.log" | tail -3)" >> "$LOG"
node tools/compress-model.mjs mocks/room-pilot/bath_v7.glb mocks/room-pilot/bath_v7-web.glb --size=2048 >> "$LOG" 2>&1
echo "BATH compressed $(date)" >> "$LOG"
ls -la mocks/room-bedroom/bedroom_v1-web.glb mocks/room-pilot/bath_v7-web.glb >> "$LOG"
echo "SHUTDOWN $(date)" >> "$LOG"
shutdown.exe //s //t 120 //c "Urban Nest bakes finished; shutting down as asked."
