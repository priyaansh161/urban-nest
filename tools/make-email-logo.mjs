/* The logo in the login emails (admin/email-templates).
 *
 *     node tools/make-email-logo.mjs
 *
 * favicon.png is a black disc on an opaque WHITE square. Cropped to a circle
 * in an email, the crop landed just outside the disc and left a thin white
 * and grey ring around the logo. This cuts the disc out with a clean
 * anti-aliased edge a few pixels inside the original, and bakes it onto the
 * email's teal band, so no mail app has to handle transparency or rounding.
 * 208px: shown at 52px, so sharp on 4x phone screens.
 */
import sharp from 'sharp';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');
const TEAL = '#0E3238';
const S = 512;              // favicon.png is 512 square, disc edge at radius ~246
const R = 241;              // inside the grey anti-aliasing, so no light fringe

const mask = Buffer.from(`<svg xmlns="http://www.w3.org/2000/svg" width="${S}" height="${S}"><circle cx="${S / 2}" cy="${S / 2}" r="${R}" fill="#fff"/></svg>`);
const disc = await sharp(join(ROOT, 'favicon.png')).ensureAlpha()
  .composite([{ input: mask, blend: 'dest-in' }]).png().toBuffer();
const flat = await sharp({ create: { width: S, height: S, channels: 3, background: TEAL } })
  .composite([{ input: disc }]).png().toBuffer();
await sharp(flat)
  .resize(208, 208, { kernel: 'lanczos3' })
  .png({ compressionLevel: 9 })
  .toFile(join(ROOT, 'images', 'email-logo.png'));
console.log('images/email-logo.png written');
