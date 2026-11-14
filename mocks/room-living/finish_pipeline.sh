#!/bin/bash
# Waits for the lounge bake, then publishes, deploys, verifies the live site and shuts the PC down (his request, 6 Nov 2026).
# Any failure stops it BEFORE the deploy / shutdown and leaves the PC on.
cd "$(dirname "$0")/../.."
LOG=mocks/room-living/finish_pipeline.log
exec >> "$LOG" 2>&1
echo "== pipeline started $(date)"
until grep -aq BAKE_FINISHED mocks/room-living/bake_living.log; do sleep 30; done
echo "== bake finished $(date)"
grep -aq "^DONE " mocks/room-living/bake_living.log || { echo "FAIL: bake did not export"; exit 1; }
[ mocks/room-living/living_v1-web.glb -nt mocks/room-living/living_v1-web_v2.glb ] || { echo "FAIL: no new web glb"; exit 1; }
node mocks/room-living/publish_room.mjs | head -2 || exit 1
node tools/room-preview.mjs rooms/living-room/room.glb rooms/living-room/room-preview.glb --size=512 || exit 1
curl -sI http://localhost:3000/mocks/room-living/viewer | head -1 | grep -q 200 || { (npx --yes serve -l 3000 . > /dev/null 2>&1 &); sleep 8; }
ROOM=rooms/living-room/ node mocks/room-living/shots.mjs z1 overview painting p:3 || { echo "FAIL: viewer check"; exit 1; }
node tools/check-pages.mjs | tail -2
node tools/deploy.mjs "Heritage Lounge v3: painting view, staging, new cushions, resized pieces, lamps moved, window detail" || { echo "FAIL: deploy"; exit 1; }
sleep 25
ok=1
for u in rooms/living-room/ rooms/living-room/room.glb rooms/living-room/room-preview.glb rooms/living-room/models/liv-seven-horses.glb; do
  c=$(curl -s -o /dev/null -w '%{http_code}' https://storeurbannest.in/$u); echo "$u $c"; [ "$c" = 200 ] || ok=0
done
[ $ok = 1 ] || { echo "FAIL: live check, not shutting down"; exit 1; }
echo "== deployed and verified $(date); shutting down in 90 s (cancel with: shutdown /a)"
shutdown.exe //s //t 90 //c "Heritage Lounge deployed; shutting down as requested"
