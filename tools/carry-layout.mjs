// After a room is republished (new "version" in rooms/<room>/placements.json), a layout saved from Admin > Rooms
// (Storage: Models/layouts/<room>.json) stops applying, because the viewer only trusts a layout made from the same
// version. When the republish only changed files (a model fixed, a lightmap patched) and not which pieces are in the
// room, this carries the saved layout over: same pieces and positions, stamped with the new version.
// Run it right AFTER the deploy that ships the new version (before that, the live room still has the old one).
//   node tools/carry-layout.mjs <room key> [--dry]
import { readFileSync } from 'node:fs';
const env = Object.fromEntries(readFileSync('.env', 'utf8').split(/\r?\n/).filter(l => l.includes('=')).map(l => { const i = l.indexOf('='); return [l.slice(0, i).trim(), l.slice(i + 1).trim().replace(/^"|"$/g, '')]; }));
const room = process.argv[2]; if (!room) { console.error('usage: node tools/carry-layout.mjs <room key> [--dry]'); process.exit(1); }
const base = JSON.parse(readFileSync(`rooms/${room}/placements.json`, 'utf8'));
const url = env.SUPABASE_URL + '/storage/v1/object/Models/layouts/' + room + '.json';
const H = { apikey: env.SUPABASE_SERVICE_ROLE_KEY, Authorization: 'Bearer ' + env.SUPABASE_SERVICE_ROLE_KEY };
const r = await fetch(env.SUPABASE_URL + '/storage/v1/object/public/Models/layouts/' + room + '.json', { cache: 'no-store' });
if (!r.ok) { console.log('no saved layout for', room); process.exit(0); }
const saved = await r.json();
if (saved.version === base.version) { console.log('already on', base.version); process.exit(0); }
// only carry it over when the saved layout still names the same files the room ships with
const files = new Set([...base.products, ...base.staging].map(d => d.file));
const missing = [...saved.products, ...saved.staging].map(d => d.file).filter(f => !files.has(f));
if (missing.length) { console.error('saved layout names files the room no longer has:', missing.join(', ')); process.exit(1); }
console.log(`${room}: saved layout ${saved.version} -> ${base.version} (${saved.products.length} products, ${saved.staging.length} staging)`);
if (process.argv.includes('--dry')) process.exit(0);
saved.version = base.version;
const up = await fetch(url, { method: 'PUT', headers: { ...H, 'Content-Type': 'application/octet-stream', 'x-upsert': 'true', 'cache-control': 'max-age=30' }   // as admin/rooms.html saves it, body: JSON.stringify(saved) });
console.log(up.ok ? 'carried over' : 'upload failed ' + up.status + ' ' + (await up.text()));
