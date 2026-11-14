// Small printed surfaces for the staging props (pv_staging.py): the scale's LCD reading, the gloves box,
// a handwritten sticky note, the sanitizer label. Brand-free except PharmVials' own item names.
//   node make_staging_textures.cjs   (writes tex/lcd.png, gloves_box.png, note.png, sanitizer.png)
const sharp = require('../../tools/node_modules/sharp');
const T = __dirname + '/tex/';
const out = (n, svg) => sharp(Buffer.from(svg)).png().toFile(T + n);
(async () => {
  await out('lcd.png', `<svg xmlns="http://www.w3.org/2000/svg" width="500" height="180"><rect width="500" height="180" fill="#9fb59a"/>
    <text x="400" y="128" text-anchor="end" font-family="Consolas, monospace" font-weight="700" font-size="110" fill="#1d261b">12.60</text>
    <text x="470" y="128" text-anchor="end" font-family="Arial" font-weight="700" font-size="54" fill="#1d261b">g</text></svg>`);
  // the box is mapped as one image on every face, so keep it centred and readable from any side
  await out('gloves_box.png', `<svg xmlns="http://www.w3.org/2000/svg" width="1024" height="512"><rect width="1024" height="512" fill="#e9eef8"/>
    <rect y="0" width="1024" height="120" fill="#2E5BBA"/><rect y="440" width="1024" height="72" fill="#2E5BBA"/>
    <text x="512" y="250" text-anchor="middle" font-family="Arial" font-weight="700" font-size="74" fill="#1d3a7a">NITRILE</text>
    <text x="512" y="330" text-anchor="middle" font-family="Arial" font-size="46" fill="#1d3a7a">EXAMINATION GLOVES</text>
    <text x="512" y="400" text-anchor="middle" font-family="Arial" font-weight="700" font-size="40" fill="#2E5BBA">MEDIUM  ·  100</text></svg>`);
  await out('note.png', `<svg xmlns="http://www.w3.org/2000/svg" width="512" height="512"><rect width="512" height="512" fill="#fbe27a"/>
    <g font-family="Segoe Print, Comic Sans MS, cursive" font-size="44" fill="#2a3a8a"><text x="40" y="120">J. Lee: pick up</text><text x="40" y="190">Fri 4 pm</text><text x="40" y="300">reorder 13DR</text><text x="40" y="370">amber x2 cases</text></g></svg>`);
  await out('sanitizer.png', `<svg xmlns="http://www.w3.org/2000/svg" width="400" height="520"><rect width="400" height="520" fill="#ffffff"/>
    <rect y="40" width="400" height="90" fill="#3aa0c8"/><text x="200" y="105" text-anchor="middle" font-family="Arial" font-weight="700" font-size="58" fill="#fff">HAND</text>
    <text x="200" y="210" text-anchor="middle" font-family="Arial" font-weight="700" font-size="56" fill="#1f5f78">SANITIZER</text>
    <text x="200" y="280" text-anchor="middle" font-family="Arial" font-size="34" fill="#1f5f78">70% alcohol</text>
    <text x="200" y="450" text-anchor="middle" font-family="Arial" font-size="30" fill="#1f5f78">500 mL</text></svg>`);
  console.log('staging textures written');
})();
