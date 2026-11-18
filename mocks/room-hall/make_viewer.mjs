// The hall viewer = the lounge viewer (mocks/room-living/viewer.html) with the hall's title, views and camera bounds,
// and the kitchen's fixes (firmer contact shadows measured unturned, sharp textures at a glancing angle).
//   node mocks/room-hall/make_viewer.mjs
import { readFileSync, writeFileSync } from 'node:fs';
let s = readFileSync('mocks/room-living/viewer.html', 'utf8').replace(/\r\n/g, '\n');
const R = (a, b) => { if (!s.includes(a)) throw new Error('missing ' + a.slice(0, 70)); s = s.split(a).join(b); };
R('<title>The Heritage Lounge · Urban Nest</title>', '<title>The Noida Hall · Urban Nest</title>');
R('content="Step into the Heritage Lounge in 3D: ink-blue walls, cognac leather, rosewood and brass by lamplight, with every piece in it a tap away."',
  'content="Step into a Noida high-rise living and dining hall in 3D: an L-sofa by the door, a marble and oak TV wall, a six-seat dining table by the balcony, with every piece a tap away."');
R('living-room copy of the bedroom viewer', 'hall copy of the lounge viewer');
R('mocks/room-living/ (this file + placements.json); published by mocks/room-living/publish_room.mjs', 'mocks/room-hall/ (this file + placements.json); published by mocks/room-hall/publish_room.mjs');
R('<h1>The Heritage Lounge</h1><small>Living room · in 3D</small>', '<h1>The Noida Hall</h1><small>Living + dining · in 3D</small>');
R(`  <button data-view="painting">Painting</button>
  <button data-view="overview">Overview</button>
  <button data-view="sofa">Sofa</button>
  <button data-view="sideboard">Sideboard</button>
  <button data-view="windows">Windows</button>
  <button data-view="door">Door</button>
  <button data-view="chandelier">Chandelier</button>`, `  <button data-view="overview">Overview</button>
  <button data-view="living">Living</button>
  <button data-view="tv">TV wall</button>
  <button data-view="dining">Dining</button>
  <button data-view="mandir">Mandir</button>`);
const a = s.indexOf('const VIEWS = {'), b = s.indexOf('};', a) + 2;
s = s.slice(0, a) + `const VIEWS = {
  wide:    { pos:[1.05, 1.55, 3.45], target:[-0.2, 1.0, -3.9] },        // from the main door, down the whole hall to the balcony
  overview:{ pos:[1.35, 2.45, 3.55], target:[-0.4, 0.6, -0.8] },       // high in the entry corner
  living:  { pos:[0.3, 1.5, -0.3], target:[0.0, 0.95, 3.7] },
  tv:      { pos:[-1.15, 1.15, 2.4], target:[1.75, 1.15, 1.45] },
  dining:  { pos:[0.15, 1.55, 0.7], target:[-0.5, 0.85, -3.3] },
  mandir:  { pos:[0.6, 1.4, -0.9], target:[-1.75, 1.3, -1.6] },
};` + s.slice(b);
R("const ROOM_FILE = PLACEMENTS.room || 'living_v1-web.glb';", "const ROOM_FILE = PLACEMENTS.room || 'hall_v1-web.glb';");
R('scene.background = new THREE.Color(0x0e2a2a);', 'scene.background = new THREE.Color(0x1d2533);');
R('<meta name="theme-color" content="#0e2a2a">', '<meta name="theme-color" content="#1d2533">');
R(`  camera.position.x = THREE.MathUtils.clamp(camera.position.x, -2.0, 2.0);
  camera.position.y = THREE.MathUtils.clamp(camera.position.y, 0.25, 2.6);
  camera.position.z = THREE.MathUtils.clamp(camera.position.z, -1.8, 1.8);`, `  // the hall: 3.5 x 7.8 m, walls at x +-1.75 and z +-3.9 (balcony end -3.9, main door +3.9)
  camera.position.x = THREE.MathUtils.clamp(camera.position.x, -1.55, 1.55);
  camera.position.y = THREE.MathUtils.clamp(camera.position.y, 0.4, 2.6);
  camera.position.z = THREE.MathUtils.clamp(camera.position.z, -3.7, 3.7);`);
R("gr.addColorStop(0, 'rgba(0,0,0,0.55)'); gr.addColorStop(0.55, 'rgba(0,0,0,0.25)');", "gr.addColorStop(0, 'rgba(0,0,0,0.72)'); gr.addColorStop(0.5, 'rgba(0,0,0,0.38)');");
R('sh.scale.set(Math.min(fs.x, fs.z) * 1.35, Math.min(fs.x, fs.z) * 1.35, 1);', 'sh.scale.set(fs.x * 1.15, fs.z * 1.15, 1);');
R('function contactShadow(holder) {\n  const fs = new THREE.Box3().setFromObject(holder).getSize(new THREE.Vector3());',
  'function contactShadow(holder) {\n  const ry = holder.rotation.y; holder.rotation.y = 0; holder.updateMatrixWorld(true);\n  const fs = new THREE.Box3().setFromObject(holder).getSize(new THREE.Vector3());\n  holder.rotation.y = ry; holder.updateMatrixWorld(true);');
R('function markShadows(o, cast = true) { o.traverse(m => { if (m.isMesh) { m.castShadow = cast; m.receiveShadow = true;',
  'const ANISO = renderer.capabilities.getMaxAnisotropy();\nfunction markShadows(o, cast = true) { o.traverse(m => { if (m.isMesh) { m.castShadow = cast; m.receiveShadow = true; for (const mt of [].concat(m.material)) for (const k of [\'map\', \'normalMap\', \'roughnessMap\', \'metalnessMap\', \'emissiveMap\']) if (mt && mt[k]) { mt[k].anisotropy = ANISO; mt[k].needsUpdate = true; }');
R('// glTF is Y-up. The room is 5.2 (x) x 4.2 (z) x 3.0 (y) metres, closed on all four sides (back wall z = -2.1, the\n// front wall z = +2.1): the camera stays inside. Arched windows on the right and front walls, the one door on the left wall.',
  '// glTF is Y-up. The hall is 3.5 (x) x 7.8 (z) x 3.0 (y) metres: the main door at z = +3.9 (living end), the balcony\n// door at z = -3.9 (dining end), the kitchen and the bedroom passage open off the left wall. The camera stays inside.');
// the long hall: the opening view stands at the main door, ~6 m from what it looks at
R('controls.minDistance = 0.3; controls.maxDistance = 4.2;', 'controls.minDistance = 0.3; controls.maxDistance = 8.0;');
// the kitchen and corridor glimpses were built facing away from the hall; draw them from both sides
R(`      m.material = bakedMaterial(m.material);
    }`, `      m.material = bakedMaterial(m.material);
    }
    if (/Kitchen|Corridor/i.test(nm)) m.material.side = THREE.DoubleSide;`);
writeFileSync('mocks/room-hall/viewer.html', s); console.log('viewer ok');
