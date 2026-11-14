// Abstract print for the Quiet Bath's framed picture (staging, Nov 2026): soft overlapping arches in sand,
// clay and stone, like the cover's print. 840 x 1120 (3:4).
const sharp = require('../../tools/node_modules/sharp');
const W = 840, H = 1120;
const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${H}">
<defs><filter id="g"><feTurbulence baseFrequency="0.9" numOctaves="2" seed="4"/><feColorMatrix values="0 0 0 0 0.5  0 0 0 0 0.45  0 0 0 0 0.4  0 0 0 0.06 0"/></filter></defs>
<rect width="${W}" height="${H}" fill="#efe7dc"/>
<path d="M80 1120 V560 a260 260 0 0 1 520 0 V1120 Z" fill="#d9c6b0"/>
<path d="M330 1120 V700 a215 215 0 0 1 430 0 V1120 Z" fill="#c4a589"/>
<circle cx="610" cy="300" r="110" fill="#e2d2bf"/>
<path d="M0 860 C 220 780 420 960 840 820 V1120 H0 Z" fill="#b89a80" opacity="0.85"/>
<path d="M180 1120 V820 a120 120 0 0 1 240 0 V1120 Z" fill="#e9dccd"/>
<rect width="${W}" height="${H}" filter="url(#g)"/>
</svg>`;
sharp(Buffer.from(svg)).png().toFile('textures/staging/stg_print.png').then(() => console.log('ok'));
