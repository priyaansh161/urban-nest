// The kitchen viewer = the lounge viewer (mocks/room-living/viewer.html) with the kitchen's title, views and camera bounds.
//   node mocks/room-kitchen/make_viewer.mjs
import { readFileSync, writeFileSync } from 'node:fs';
let s = readFileSync('mocks/room-living/viewer.html', 'utf8').replace(/\r\n/g, '\n');
const R = (a, b) => { if (!s.includes(a)) throw new Error('missing ' + a.slice(0, 70)); s = s.split(a).join(b); };
R('<title>The Heritage Lounge · Urban Nest</title>', '<title>The Oak Kitchen · Urban Nest</title>');
R('content="Step into the Heritage Lounge in 3D: ink-blue walls, cognac leather, rosewood and brass by lamplight, with every piece in it a tap away."',
  'content="Step into a Noida high-rise kitchen in 3D: oak tall units, charcoal-navy cabinets, white marble and a sunny window, with every piece on the counter a tap away."');
R('living-room copy of the bedroom viewer', 'kitchen copy of the lounge viewer');
R('mocks/room-living/ (this file + placements.json); published by mocks/room-living/publish_room.mjs', 'mocks/room-kitchen/ (this file + placements.json); published by mocks/room-kitchen/publish_room.mjs');
R('<h1>The Heritage Lounge</h1><small>Living room · in 3D</small>', '<h1>The Oak Kitchen</h1><small>Kitchen · in 3D</small>');
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
// firmer contact shadows: in the bright daylit kitchen the lounge's soft blobs barely showed (his review, 15 Nov)
R("gr.addColorStop(0, 'rgba(0,0,0,0.55)'); gr.addColorStop(0.55, 'rgba(0,0,0,0.25)');", "gr.addColorStop(0, 'rgba(0,0,0,0.72)'); gr.addColorStop(0.5, 'rgba(0,0,0,0.38)');");
R('sh.scale.set(Math.min(fs.x, fs.z) * 1.35, Math.min(fs.x, fs.z) * 1.35, 1);', 'sh.scale.set(fs.x * 1.15, fs.z * 1.15, 1);');
// the blob hangs in the holder, so it is turned with the piece: measure the piece unturned (a turned chopping board
// got its shadow crosswise, sticking out behind it; his review, 15 Nov)
R('function contactShadow(holder) {\n  const fs = new THREE.Box3().setFromObject(holder).getSize(new THREE.Vector3());',
  'function contactShadow(holder) {\n  const ry = holder.rotation.y; holder.rotation.y = 0; holder.updateMatrixWorld(true);\n  const fs = new THREE.Box3().setFromObject(holder).getSize(new THREE.Vector3());\n  holder.rotation.y = ry; holder.updateMatrixWorld(true);');
// sharp textures at a glancing angle (the TEX-RO rack's wires and plates went soft from across the room): full anisotropic filtering
R('function markShadows(o, cast = true) { o.traverse(m => { if (m.isMesh) { m.castShadow = cast; m.receiveShadow = true;',
  'const ANISO = renderer.capabilities.getMaxAnisotropy();\nfunction markShadows(o, cast = true) { o.traverse(m => { if (m.isMesh) { m.castShadow = cast; m.receiveShadow = true; for (const mt of [].concat(m.material)) for (const k of [\'map\', \'normalMap\', \'roughnessMap\', \'metalnessMap\', \'emissiveMap\']) if (mt && mt[k]) { mt[k].anisotropy = ANISO; mt[k].needsUpdate = true; }');
// the opening line describes the kitchen, not the lounge
R('// glTF is Y-up. The room is 5.2 (x) x 4.2 (z) x 3.0 (y) metres, closed on all four sides (back wall z = -2.1, the\n// front wall z = +2.1): the camera stays inside. Arched windows on the right and front walls, the one door on the left wall.',
  '// glTF is Y-up. The kitchen is 2.9 (x) x 3.4 (z) x 2.9 (y) metres: a U of counters, the window wall at z = -1.7, a 1.6 m opening in the\n// front wall at z = +1.7 to the hall: the camera keeps to the aisle and the doorway. Daylight from the window, LED strips under the uppers.');
writeFileSync('mocks/room-kitchen/viewer.html', s); console.log('viewer ok');
