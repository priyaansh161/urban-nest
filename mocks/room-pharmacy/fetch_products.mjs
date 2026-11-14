// The PharmVials products shown on the sample counter, with their card text taken from pharmvials.com itself
// (short description + the attribute table), so every card says what their own site says.
//   node fetch_products.mjs      -> products.json (read by build_pharmacy.py, which adds positions and views)
import { writeFileSync } from 'node:fs';
const P = 'https://pharmvials.com/product/';
const C = 'https://pharmvials.com/product-category/';
// key: how build_pharmacy.py finds the item in the scene; page: where the card's button goes
export const ITEMS = [
  { key: 'amber_cr', name: 'Amber Vials, Child Resistant', tag: 'VIALS', page: P + '13dr-amber-vials-child-resistant/', link: C + 'vials/child-resistant-vials/' },
  { key: 'blue_cr', name: 'Blue Vials, Child Resistant', tag: 'VIALS', page: P + '13dr-blue-vials-child-resistant/', link: C + 'vials/child-resistant-vials/' },
  { key: 'snap', name: 'Snap Cap Vials, Amber and Blue', tag: 'VIALS', page: P + '13dr-amber-vials-snap-cap/', link: C + 'vials/snap-cap-vials/' },
  { key: 'cutter', name: 'Multiple Pill Cutter', tag: 'PHARMACY SUPPLIES', page: P + 'multiple-pill-cutter/' },
  { key: 'scale', name: 'Digital Laboratory Scale, 310 g', tag: 'PHARMACY SUPPLIES', page: P + 'digital-laboratory-scale-310g/' },
  { key: 'boats', name: 'Weighing Boats', tag: 'PHARMACY SUPPLIES', page: P + 'weighing-boat-medium/' },
  { key: 'label', name: 'Paxxol 4.625 x 2.125 in Thermal Direct Label', tag: 'THERMAL LABELS', page: P + 'paxxol-4-625x2-125-thermal-direct-label/' },
  { key: 'receipt', name: 'Paxxol 3.375 x 4.25 in Thermal Direct Receipt', tag: 'THERMAL LABELS', page: P + 'paxxol-3-375x4-25-thermal-direct-receipt/' },
  { key: 'tape', name: 'Prescription Clear Label Tape', tag: 'LABELS', page: P + 'prescription-clear-label-tape/' },
  { key: 'syringes', name: 'Oral Syringes', tag: 'PHARMACY SUPPLIES', page: P + 'oral-syringes-5ml/' },
  { key: 'gloves', name: 'Nitrile Examination Gloves', tag: 'PHARMACY SUPPLIES', page: P + 'nitrile-examination-gloves-medium/' },
  { key: 'jumbo', name: 'Paxxol Jumbo Blister Pack', tag: 'COMPLIANCE PACKAGING', page: P + 'paxxol-jumbo-blister-pack/' },
  { key: 'twin', name: 'Paxxol Twin Blister Pack', tag: 'COMPLIANCE PACKAGING', page: P + 'paxxol-twin-blister-pack/' },
  { key: 'trifold', name: 'Paxxol Tri-Fold Blister Pack', tag: 'COMPLIANCE PACKAGING', page: P + 'paxxol-tri-fold-blister-pack/' },
  { key: 'tray', name: 'Jumbo Assembly Tray', tag: 'COMPLIANCE PACKAGING', page: P + 'jumbo-assembly-tray/' },
  { key: 'roller', name: 'Compliance Pack Roller, 10 cm', tag: 'COMPLIANCE PACKAGING', page: P + 'compliance-pack-roller-10-cm/' },
];
const strip = (s) => s.replace(/<[^>]+>/g, ' ').replace(/&amp;/g, '&').replace(/&#8217;|&rsquo;/g, "'").replace(/&#8211;|&ndash;|&#8212;|&mdash;/g, ',').replace(/&nbsp;|&#160;/g, ' ').replace(/&[a-z#0-9]+;/g, '').replace(/\s+/g, ' ').trim();
const out = [];
for (const it of ITEMS) {
  const html = await (await fetch(it.page, { headers: { 'user-agent': 'Mozilla/5.0' } })).text();
  const short = (html.match(/woocommerce-product-details__short-description">([\s\S]*?)<\/div>/) || [])[1]
             || (html.match(/id="tab-description"[^>]*>([\s\S]*?)<\/div>/) || [])[1] || '';
  let desc = strip(short).replace(/^Description\s*/, '');
  // whole sentences, about two lines of card: cut at the last full stop, or at a word with an ellipsis
  if (desc.length > 200) { const cut = desc.slice(0, 240), p = cut.lastIndexOf('. '); desc = p > 80 ? cut.slice(0, p + 1) : cut.slice(0, cut.lastIndexOf(' ')) + '…'; }
  const specs = [...html.matchAll(/<th[^>]*class="woocommerce-product-attributes-item__label"[^>]*>([\s\S]*?)<\/th>\s*<td[^>]*>([\s\S]*?)<\/td>/g)]
    .map((m) => [strip(m[1]), strip(m[2])]).filter(([k, v]) => v && !/Not Available|Item No|Dimensions/i.test(k + v)).slice(0, 4);
  out.push({ ...it, link: it.link || it.page, desc: desc || it.name, specs });
  console.log(it.key, '·', desc.slice(0, 60), '·', specs.length, 'specs');
  await new Promise((r) => setTimeout(r, 400));                              // politely, one page at a time
}
writeFileSync(new URL('./products.json', import.meta.url), JSON.stringify(out, null, 1));
