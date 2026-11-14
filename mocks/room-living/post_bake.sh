#!/bin/bash
# After a full bake: split the furniture out as movable pieces (keeping their baked light), rebuild the room file without
# them, point placements.json's staging at the new pieces (his positions are now baked in, so no extra turn), publish locally.
set -e
cd "$(dirname "$0")"
B="/c/Program Files/Blender Foundation/Blender 5.2/blender.exe"
cp living_v1.glb living_v1_full.glb
"$B" -b living_v1.blend -P split_furniture.py -- "$(pwd -W)" 2>&1 | grep -a "PIECE\|DONE split\|Error\|Traceback"
cd ../..
for f in liv-sofa liv-loveseat liv-armchair-1 liv-armchair-2 liv-sideboard liv-side-table-b; do
  [ -f mocks/room-living/products/${f}_raw.glb ] || continue
  node tools/compress-model.mjs mocks/room-living/products/${f}_raw.glb mocks/room-living/products/$f.glb --size=1024 | tail -1; rm mocks/room-living/products/${f}_raw.glb
done
cp mocks/room-living/living_v1_nofurn.glb mocks/room-living/living_v1.glb
node mocks/room-living/slim_room.mjs | tail -1
python - <<'EOF'
import json
p = json.load(open('mocks/room-living/placements.json', encoding='utf8')); si = json.load(open('mocks/room-living/split_info.json', encoding='utf8'))
p['staging'] = [dict(name=i['name'], file=i['file'], height=i['height'], pos=i['pos'], lm=True) for i in si]
json.dump(p, open('mocks/room-living/placements.json', 'w', encoding='utf8'), indent=1, ensure_ascii=False)
print('staging', [s['file'] for s in p['staging']])
EOF
node mocks/room-living/publish_room.mjs | head -2
node tools/room-preview.mjs rooms/living-room/room.glb rooms/living-room/room-preview.glb --size=512 | tail -1
echo POST_DONE
