// Drops named staging nodes from the baked room (e.g. the spice jars the painted pickle set replaced) without a rebake.
//   node mocks/room-kitchen/strip_nodes.mjs <in.glb> <out.glb> <name-prefix> [...]
import { createRequire } from 'node:module';
const require = createRequire(new URL('../../tools/package.json', import.meta.url));
const { NodeIO } = require('@gltf-transform/core'); const { ALL_EXTENSIONS } = require('@gltf-transform/extensions'); const { prune } = require('@gltf-transform/functions');
const [inp, out, ...pre] = process.argv.slice(2);
const io = new NodeIO().registerExtensions(ALL_EXTENSIONS); const doc = await io.read(inp);
let n = 0; for (const node of doc.getRoot().listNodes()) if (pre.some(p => node.getName().startsWith(p))) { node.dispose(); n++; }
await doc.transform(prune()); await io.write(out, doc); console.log('removed', n, 'nodes');
