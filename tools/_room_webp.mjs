/* temp: room jpg -> mocks/shop-<name>.webp (2400w) + -m.webp (1400w) */
import sharp from 'sharp';
const [src, name] = process.argv.slice(2);
const out = 'C:/Users/priya/OneDrive/Projects/urban-nest/mocks/shop-' + name;
await sharp(src).resize({ width: 2400 }).webp({ quality: 78 }).toFile(out + '.webp');
await sharp(src).resize({ width: 1400 }).webp({ quality: 74 }).toFile(out + '-m.webp');
const m = await sharp(src).metadata();
console.log(name, m.width + 'x' + m.height);
