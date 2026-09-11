/* The home-screen icons for the installable app (manifest.webmanifest).
 *
 *     node tools/make-app-icons.mjs
 *
 * Everything is cut from favicon.png, so a new mark means re-running this.
 *
 * WHY FOUR FILES: "any" icons are shown as-is, so the transparent mark is
 * right. A "maskable" icon is cropped by Android to whatever shape the
 * launcher uses — circle, squircle, teardrop — and only a centred circle of
 * 80% of the width is guaranteed to survive, so the mark sits inside that
 * on a solid ground. iOS fills transparency with black, which would swallow
 * a black mark, so apple-touch-icon gets the same solid ground.
 */
import sharp from 'sharp';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');
const SRC = join(ROOT, 'favicon.png');
const OUT = join(ROOT, 'images');
/* Pure white, not the site's #F5F7F6 paper. On an iPhone home screen, next
   to other apps' white icons, the off-white read as faded (seen 2026-09-11),
   and it also showed up the thin light ring around the logo's edge. */
const PAPER = '#FFFFFF';

async function plain(size, name) {
  await sharp(SRC).resize(size, size).png().toFile(join(OUT, name));
}

async function onPaper(size, markFraction, name) {
  const mark = Math.round(size * markFraction);
  const markBuf = await sharp(SRC).resize(mark, mark).png().toBuffer();
  await sharp({ create: { width: size, height: size, channels: 4, background: PAPER } })
    .composite([{ input: markBuf, gravity: 'centre' }])
    .png()
    .toFile(join(OUT, name));
}

await plain(192, 'app-icon-192.png');
await plain(512, 'app-icon-512.png');
// 0.80 is the most the maskable one can take: the circle then just fits the
// guaranteed-visible 80% zone. iOS only rounds the corners, so it can go larger.
await onPaper(512, 0.80, 'app-icon-maskable-512.png');
await onPaper(180, 0.94, 'apple-touch-icon.png');

console.log('  images/app-icon-192.png, app-icon-512.png, app-icon-maskable-512.png, apple-touch-icon.png');
