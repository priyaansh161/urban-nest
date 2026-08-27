/* Build the image that messaging apps show when the site's link is pasted.
 *
 *   node tools/make-share-card.mjs
 *
 * WHY THIS IS JUST THE LOGO, AND WHY IT IS SQUARE:
 * The first two attempts were 1200×630 cards carrying the wordmark and the
 * tagline. WhatsApp Desktop does not show a wide banner — it squashes the
 * whole frame into a ~80px square, which turned the round mark into an oval
 * and the type into a smear. Scaling the type up helped and did not fix it,
 * because the shape itself was the problem.
 *
 * A square image containing only the mark cannot be squashed (there is no
 * aspect to lose) and needs no legible type at thumbnail size. The wordmark
 * and tagline are already carried by the title and description text WhatsApp
 * prints beside the image, so nothing is lost by dropping them from it.
 *
 * OUTPUT: images/share-card.jpg — JPEG on purpose. Several preview fetchers
 * still will not read the .webp the rest of the site uses.
 */
import sharp from 'sharp';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');

const LOGO = join(ROOT, 'logo-icon.png');
const OUT  = join(ROOT, 'images', 'share-card.jpg');

const SIZE  = 1200;          // square: what a preview thumbnail actually is
const PAPER = '#FFFFFF';
// A little air around the mark so it reads as a considered icon rather than
// something cropped to its own edges. 78% of the frame, centred.
const MARK = Math.round(SIZE * 0.78);

/* .trim() first: the source is a 500×500 file with the mark floating in a
   wide white margin. Resizing it directly would shrink the circle and keep
   the padding, so MARK would not mean the circle's real diameter. */
const mark = await sharp(LOGO)
  .flatten({ background: PAPER })
  .trim()
  .resize(MARK, MARK, { fit: 'contain', background: PAPER })
  .toBuffer();

const offset = Math.round((SIZE - MARK) / 2);

const info = await sharp({
    create: { width: SIZE, height: SIZE, channels: 3, background: PAPER },
  })
  .composite([{ input: mark, top: offset, left: offset }])
  // Hard black on flat white is exactly where JPEG artefacts show worst, and
  // the file is tiny either way, so quality stays high and chroma unsampled.
  .jpeg({ quality: 95, mozjpeg: true, chromaSubsampling: '4:4:4' })
  .toFile(OUT);

console.log(`share-card.jpg — ${info.width}×${info.height}, ${(info.size / 1024).toFixed(0)} KB`);
