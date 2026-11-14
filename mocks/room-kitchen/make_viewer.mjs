// The kitchen viewer = the lounge viewer (mocks/room-living/viewer.html) with the kitchen's title, views and camera bounds.
//   node mocks/room-kitchen/make_viewer.mjs
import { readFileSync, writeFileSync } from 'node:fs';
let s = readFileSync('mocks/room-living/viewer.html', 'utf8').replace(/\r\n/g, '\n');
const R = (a, b) => { if (!s.includes(a)) throw new Error('missing ' + a.slice(0, 70)); s = s.split(a).join(b); };
R('<title>The Heritage Lounge · Urban Nest</title>', '<title>The NCR Kitchen · Urban Nest</title>');
R('content="Step into the Heritage Lounge in 3D: ink-blue walls, cognac leather, rosewood and brass by lamplight, with every piece in it a tap away."',
  'content="Step into a Noida high-rise kitchen in 3D: oak tall units, charcoal-navy cabinets, white marble and a sunny window, with every piece on the counter a tap away."');
R('living-room copy of the bedroom viewer', 'kitchen copy of the lounge viewer');
R('mocks/room-living/ (this file + placements.json); published by mocks/room-living/publish_room.mjs', 'mocks/room-kitchen/ (this file + placements.json); published by mocks/room-kitchen/publish_room.mjs');
R('<h1>The Heritage Lounge</h1><small>Living room · in 3D</small>', '<h1>The NCR Kitchen</h1><small>Kitchen · in 3D</small>');
R(`  <button data-view="painting">Painting</button>
  <button data-view="overview">Overview</button>
  <button data-view="sofa">Sofa</button>
  <button data-view="sideboard">Sideboard</button>
  <button data-view="windows">Windows</button>
  <button data-view="door">Door</button>
  <button data-view="chandelier">Chandelier</button>`, `  <button data-view="overview">Overview</button>
  <button data-view="hob">Hob</button>
  <button data-view="sink">Sink</button>
  <button data-view="prep">Prep</button>
  <button data-view="ovens">Ovens</button>`);
const a = s.indexOf('const VIEWS = {'), b = s.indexOf('};', a) + 2;
s = s.slice(0, a) + `const VIEWS = {
  wide:    { pos:[0.0, 1.55, 2.2], target:[0.0, 1.05, -1.7] },          // from the way in, like his reference photo
  overview:{ pos:[-0.6, 2.3, 1.95], target:[0.45, 0.8, -0.6] },        // high in the doorway: the whole U at once
  hob:     { pos:[-0.35, 1.55, 0.55], target:[1.25, 0.95, -0.45] },
  sink:    { pos:[0.05, 1.6, 0.35], target:[0.0, 1.0, -1.7] },
  prep:    { pos:[0.15, 1.5, -0.1], target:[1.2, 0.92, 0.75] },
  ovens:   { pos:[0.55, 1.4, -0.35], target:[-1.45, 1.1, 0.55] },
};` + s.slice(b);
R("const ROOM_FILE = PLACEMENTS.room || 'living_v1-web.glb';", "const ROOM_FILE = PLACEMENTS.room || 'kitchen_v1-web.glb';");
R('scene.background = new THREE.Color(0x0e2a2a);', 'scene.background = new THREE.Color(0x1d2533);');
R('<meta name="theme-color" content="#0e2a2a">', '<meta name="theme-color" content="#1d2533">');
R(`  camera.position.x = THREE.MathUtils.clamp(camera.position.x, -2.0, 2.0);
  camera.position.y = THREE.MathUtils.clamp(camera.position.y, 0.25, 2.6);
  camera.position.z = THREE.MathUtils.clamp(camera.position.z, -1.8, 1.8);`, `  // the kitchen aisle: between the tall units (x -0.83) and the right run (x 0.85), in front of the back run (z -1.08),
  // and out through the 1.6 m opening (x +-0.8) into the hall as far as z 2.3
  camera.position.z = THREE.MathUtils.clamp(camera.position.z, -0.95, 2.3);
  const xl = camera.position.z > 1.62 ? 0.68 : 0.72;
  camera.position.x = THREE.MathUtils.clamp(camera.position.x, -xl, xl);
  camera.position.y = THREE.MathUtils.clamp(camera.position.y, 0.4, 2.6);`);
writeFileSync('mocks/room-kitchen/viewer.html', s); console.log('viewer ok');
