// Reads one Amazon product page and says what it found (18 Nov 2026), for the admin's "Run full check".
// Used by functions/api/check-amazon.js. It never writes anything; the admin page records the result.
//
// He accepted the risk on 18 Nov 2026: reading Amazon pages automatically is against the Associates terms, so it is
// kept to a manual, about-monthly run, one page at a time with pauses (the admin page spaces the calls), with an
// ordinary browser's headers and no retries on a robot check.
//
//   status  ok           the page shows the product and it can be bought
//           unavailable  the product page exists but says it is unavailable / out of stock
//           gone         Amazon says the page does not exist (a dead link)
//           blocked      Amazon showed a robot check instead of the page: no verdict, try later or check by hand
//           unknown      anything else (the page could not be read)
//   price   "₹2,999" when the page shows one, else ""
const HEADERS = {
  'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36',
  Accept: 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
  'Accept-Language': 'en-IN,en;q=0.9',
};

export async function checkAmazon(url) {
  if (!/^https?:\/\/([a-z0-9-]+\.)*(amazon\.in|amzn\.to|amzn\.in|link\.amazon|a\.co)(\/|$)/i.test(url)) return { status: 'unknown', note: 'not an Amazon link' };
  // a clean product link is opened WITHOUT the affiliate tag, so these checks are not tied to the Associates account
  // (short links like link.amazon carry the tag inside Amazon's redirect, which cannot be avoided)
  const asin = (url.match(/amazon\.in\/(?:.*\/)?(?:dp|gp\/product)\/([A-Z0-9]{10})/i) || [])[1];
  if (asin) url = 'https://www.amazon.in/dp/' + asin.toUpperCase();
  let res, html;
  try {
    res = await fetch(url, { headers: HEADERS, redirect: 'follow', cf: { cacheTtl: 0 } });
    html = await res.text();
  } catch (err) { return { status: 'unknown', note: 'could not reach Amazon: ' + err.message }; }
  const final = res.url || url, http = res.status;
  const base = { http, final };
  if (http === 404) return { ...base, status: 'gone', note: 'Amazon says this page does not exist' };   // first: the 404 page carries robot-check words
  if (/validateCaptcha|Enter the characters you see below|api-services-support@amazon\.com|Type the characters you see in this image/i.test(html))
    return { ...base, status: 'blocked', note: 'Amazon showed a robot check' };
  const title = ((html.match(/id="productTitle"[^>]*>\s*([^<]+?)\s*</) || [])[1] || '').replace(/\s+/g, ' ')
    .replace(/&amp;/g, '&').replace(/&quot;/g, '"').replace(/&#39;/g, "'");
  if ((!title && /Page Not Found|couldn.t find that page|Looking for something\?|The Web address you entered is not a functioning page/i.test(html)))
    return { ...base, status: 'gone', note: 'Amazon says this page does not exist' };
  if (!title) return { ...base, status: 'unknown', note: http >= 500 ? 'Amazon error ' + http : 'no product on the page' };
  const avail = (html.match(/id="availability"[\s\S]{0,600}?<\/div>/) || [''])[0].replace(/<[^>]+>/g, ' ');
  const unavailable = /Currently unavailable|We don.t know when or if this item will be back|out of stock/i.test(avail);
  // the price people are shown: the first whole-rupee figure in the main price block
  const block = (html.match(/id="(?:corePriceDisplay_desktop_feature_div|corePrice_feature_div|apex_desktop)"[\s\S]{0,4000}/) || [''])[0];
  const whole = (block.match(/class="a-price-whole">([\d,]+)/) || [])[1];
  return { ...base, status: unavailable ? 'unavailable' : 'ok', title: title.slice(0, 160), price: whole ? '₹' + whole : '' };
}
