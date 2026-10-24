/* "Our take" — Priyaansh's own rating and verdict on a piece.
 *
 * These are Urban Nest's opinions, written in Admin and stored on the product
 * row (un_rating, un_take, un_pros, un_cons). They are not scraped or copied
 * from any retailer's reviews.
 *
 *   UNTake.block(item)  → HTML for a detail sheet / room panel ('' if unrated)
 *   UNTake.chip(item)   → small "★ 4.5" for a card            ('' if unrated)
 *
 * Colours inherit from the page, so it works on the dark and light themes
 * and inside the always-white room panels.
 */
(function () {
  var css = document.createElement('style');
  css.textContent =
    '.un-take{margin:18px 0 6px;padding:16px 18px;border:.5px solid color-mix(in srgb,currentColor 18%,transparent);border-radius:10px}' +
    '.un-take-head{display:flex;align-items:baseline;gap:10px;flex-wrap:wrap}' +
    '.un-take-label{font-size:10px;letter-spacing:.26em;text-transform:uppercase;opacity:.65}' +
    '.un-stars{letter-spacing:2px;font-size:16px;white-space:nowrap;color:transparent;-webkit-background-clip:text;background-clip:text}' +
    '.un-score{font-size:15px;font-weight:600}' +
    '.un-take-text{margin:10px 0 0;font-size:14px;line-height:1.8}' +
    '.un-lists{display:grid;grid-template-columns:1fr 1fr;gap:14px;margin-top:12px}' +
    '.un-lists h4{margin:0 0 4px;font-size:10px;letter-spacing:.22em;text-transform:uppercase;opacity:.65;font-weight:500}' +
    '.un-lists ul{margin:0;padding:0;list-style:none;font-size:13px;line-height:1.65}' +
    '.un-lists li{padding-left:14px;position:relative}' +
    '.un-lists .pro li:before{content:"+";position:absolute;left:0;color:#3E8A6B}' +
    '.un-lists .con li:before{content:"–";position:absolute;left:0;color:#B5583F}' +
    '@media(max-width:480px){.un-lists{grid-template-columns:1fr}}' +
    '.un-chip{font-size:12px;color:#A37B3F;white-space:nowrap}';
  document.head.appendChild(css);

  function esc(s) {
    return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  }
  function score(item) {
    var n = item && item.un_rating != null ? Number(item.un_rating) : NaN;
    return n >= 0.5 && n <= 5 ? Math.round(n * 2) / 2 : null;
  }
  function lines(s) {
    return String(s || '').split('\n').map(function (x) { return x.trim(); }).filter(Boolean);
  }
  function list(cls, title, s) {
    var l = lines(s);
    return l.length
      ? '<div class="' + cls + '"><h4>' + title + '</h4><ul>' +
        l.map(function (x) { return '<li>' + esc(x) + '</li>'; }).join('') + '</ul></div>'
      : '';
  }

  window.UNTake = {
    chip: function (item) {
      var n = score(item);
      return n == null ? '' : '<span class="un-chip" title="Urban Nest rating">★ ' + n.toFixed(1) + '</span>';
    },
    block: function (item) {
      var n = score(item), take = (item && item.un_take || '').trim();
      var pros = list('pro', 'Good', item && item.un_pros);
      var cons = list('con', 'Watch for', item && item.un_cons);
      if (n == null && !take && !pros && !cons) return '';
      return '<div class="un-take">' +
        '<div class="un-take-head"><span class="un-take-label">Our take</span>' +
        (n == null ? '' : '<span class="un-stars" aria-hidden="true" style="background-image:linear-gradient(90deg,#A37B3F ' + (n * 20) + '%,color-mix(in srgb,currentColor 22%,transparent) ' + (n * 20) + '%)">★★★★★</span>' +
          '<span class="un-score">' + n.toFixed(1) + ' / 5</span>') + '</div>' +
        (take ? '<p class="un-take-text">' + esc(take) + '</p>' : '') +
        (pros || cons ? '<div class="un-lists">' + pros + cons + '</div>' : '') +
        '</div>';
    }
  };
})();
