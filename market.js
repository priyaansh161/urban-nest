/* Markets: India and US.
 *
 * Every outbound buy link belongs to a market, worked out from where it points:
 *   amazon.in, pepperfry.com, flipkart.com ...   India
 *   amazon.com, walmart.com ...                  US
 * Admitad links (ad.admitad.com/g/...?ulp=<page>) are read through their ulp= page.
 * A link can also say it outright:  <a data-market="US" ...>.
 * Links to anywhere else (Instagram, email) are left alone. A US link written as a short link
 * (amzn.to) cannot be told apart from an India one, so give it data-market="US".
 * The marketplace cart (Add to Cart, Razorpay) is India only.
 *
 * The visitor's market comes from, in this order:
 *   1. their own choice (the IN | US switch in the top bar, or ?market=us in the address)
 *   2. their country, from /api/country (Cloudflare): US visitors get the US store,
 *      everyone else the India store
 *
 * A piece that is not sold in the visitor's market is still shown, in full, with its buy button
 * swapped for "India only" (or "US only"). Nothing is hidden, nothing is blocked.
 *
 * It works on the page as drawn, so every page that renders buy links (the Collection, the rooms,
 * the piece pages) needs nothing more than this one script. It watches for cards drawn later.
 */
(function () {
  'use strict';
  var KEY = 'un-market', GEO = 'un-geo';
  var NAMES = { IN: 'India', US: 'US' };
  var HOSTS = {
    // amzn.to and link.amazon are the short links our Amazon India Associates links use today.
    IN: ['amazon.in', 'amzn.in', 'amzn.to', 'link.amazon', 'pepperfry.com', 'flipkart.com', 'fkrt.it', 'homecentre.in', 'urbanladder.com', 'ikea.com/in'],
    US: ['amazon.com', 'amzn.com', 'walmart.com', 'wmt.co', 'target.com', 'wayfair.com'],
  };
  var WRAPPERS = /(^|\.)(admitad\.com|alitems\.com|ulp\.)/i;   // affiliate redirectors: the real page is in ulp=

  var visitor = 'IN';
  function read(k, s) { try { return (s || localStorage).getItem(k); } catch (e) { return null; } }
  function write(k, v, s) { try { (s || localStorage).setItem(k, v); } catch (e) {} }

  function norm(m) { m = String(m || '').toUpperCase(); return m === 'US' || m === 'IN' ? m : null; }

  function hostMarket(url) {
    var u;
    try { u = new URL(url, location.href); } catch (e) { return null; }
    if (u.origin === location.origin || !/^https?:$/.test(u.protocol)) return null;
    if (WRAPPERS.test(u.hostname)) {
      var inner = u.searchParams.get('ulp');
      return inner ? hostMarket(inner) : null;
    }
    var host = u.hostname.replace(/^www\./, '');
    for (var m in HOSTS) for (var i = 0; i < HOSTS[m].length; i++) {
      var parts = HOSTS[m][i].split('/');                       // "ikea.com/in" = that host and that path
      var hostOk = host === parts[0] || host.slice(-(parts[0].length + 1)) === '.' + parts[0];
      if (hostOk && (!parts[1] || u.pathname.indexOf('/' + parts[1]) === 0)) return m;
    }
    return null;   // not a shop we know (Instagram, mailto ...): left alone
  }

  /* ── marking pieces ── */
  function label(m) { return NAMES[m] + ' only'; }
  function tip(m) { return 'Not sold in your region. This piece is sold in the ' + NAMES[m] + ' store. Switch store at the top of the page to see its price and shop.'; }

  function handle(el) {
    var isCart = el.hasAttribute('data-add');
    var m = isCart ? 'IN' : (norm(el.getAttribute('data-market')) || (el.hasAttribute('href') ? hostMarket(el.getAttribute('href')) : null));
    var flagged = el.hasAttribute('data-un-away');

    if (flagged) {
      // The page gave the link a new address while we had it switched off: it is a new link.
      if (el.tagName === 'A' && el.hasAttribute('href')) { el.removeAttribute('data-un-away'); el.classList.remove('un-away'); flagged = false; }
      else m = el.getAttribute('data-un-m');
    }
    if (!m) return;

    if (m !== visitor && !flagged) {
      el.setAttribute('data-un-away', '1');
      el.setAttribute('data-un-m', m);
      el.setAttribute('data-un-html', el.innerHTML);
      el.classList.add('un-away');
      el.setAttribute('title', tip(m));
      if (el.tagName === 'A') { el.setAttribute('data-un-href', el.getAttribute('href')); el.removeAttribute('href'); el.setAttribute('role', 'link'); el.setAttribute('aria-disabled', 'true'); }
      else el.disabled = true;
      el.textContent = label(m);
      // Pages with no top bar (the 3D rooms) have no store switch, so the label carries its own.
      if (!document.querySelector('.un-mkt') && el.parentNode) {
        var sw = document.createElement('button');
        sw.type = 'button'; sw.className = 'un-sw'; sw.textContent = 'Switch to the ' + NAMES[m] + ' store';
        sw.addEventListener('click', function (e) { e.stopPropagation(); choose(m); });
        el.parentNode.insertBefore(sw, el.nextSibling);
      }
    } else if (m === visitor && flagged) {
      restore(el);
    } else if (m !== visitor && flagged) {
      // The page redrew this button while it was switched off (a new piece opened in the same sheet):
      // keep what it drew for when the visitor switches store, and put the label back.
      if (el.textContent !== label(m)) { el.setAttribute('data-un-html', el.innerHTML); el.textContent = label(m); }
      if (el.tagName !== 'A' && !el.disabled) el.disabled = true;
    }
  }

  function restore(el) {
    el.innerHTML = el.getAttribute('data-un-html') || el.innerHTML;
    if (el.tagName === 'A') { var h = el.getAttribute('data-un-href'); if (h) el.setAttribute('href', h); el.removeAttribute('role'); el.removeAttribute('aria-disabled'); }
    else el.disabled = false;
    ['data-un-away', 'data-un-m', 'data-un-html', 'data-un-href', 'title'].forEach(function (a) { el.removeAttribute(a); });
    el.classList.remove('un-away');
    var nx = el.nextElementSibling;
    if (nx && nx.classList.contains('un-sw')) nx.remove();
  }

  var busy = false, queued = false;
  function sweep() {
    if (busy) return;
    busy = true;
    try {
      var els = document.querySelectorAll('a[href], a[data-un-away], button[data-add], [data-market]');
      for (var i = 0; i < els.length; i++) handle(els[i]);
    } finally { busy = false; }
  }
  function later() {
    if (queued) return;
    queued = true;
    setTimeout(function () { queued = false; sweep(); }, 30);   // a timer, not requestAnimationFrame: that pauses in background tabs
  }

  /* ── the switch in the top bar ── */
  function paintSwitch() {
    var bs = document.querySelectorAll('.un-mkt button');
    for (var i = 0; i < bs.length; i++) bs[i].setAttribute('aria-pressed', String(bs[i].getAttribute('data-m') === visitor));
  }
  function choose(m) {
    visitor = m;
    write(KEY, m);
    paintSwitch();
    sweep();
    document.documentElement.setAttribute('data-store', m.toLowerCase());
    try { document.dispatchEvent(new CustomEvent('un-market', { detail: m })); } catch (e) {}
  }
  function addSwitch() {
    if (document.querySelector('.un-mkt')) return;
    var right = document.querySelector('nav .nav-right');
    if (!right) return;
    var box = document.createElement('div');
    box.className = 'switch un-mkt';
    box.setAttribute('role', 'group');
    box.setAttribute('aria-label', 'Store');
    box.title = 'Which store you are shopping: India or US';
    box.innerHTML = '<button type="button" data-m="IN" aria-pressed="false"><span class="un-l">India</span><span class="un-s">IN</span></button><button type="button" data-m="US" aria-pressed="false">US</button>';
    box.addEventListener('click', function (e) { var b = e.target.closest && e.target.closest('button[data-m]'); if (b) choose(b.getAttribute('data-m')); });
    right.insertBefore(box, right.firstChild);
    paintSwitch();
  }

  function style() {
    var s = document.createElement('style');
    s.textContent =
      '.un-away{opacity:.55;cursor:default;pointer-events:auto}' +
      '.un-sw{display:block;margin:8px auto 0;background:none;border:0;padding:0;cursor:pointer;color:inherit;font:500 11px/1.2 "DM Sans",system-ui,sans-serif;text-decoration:underline;opacity:.8}' +
      'a.un-away:hover,button.un-away:hover{filter:none!important;transform:none!important}' +
      'nav .switch.un-mkt button,.switch.un-mkt button{width:auto!important;min-width:0;padding:0 9px!important;font:500 10.5px/1 "DM Sans",system-ui,sans-serif;letter-spacing:.04em;text-transform:uppercase}' +
      '.un-mkt .un-s{display:none}' +
      '@media (max-width:600px){nav .switch.un-mkt button{padding:0 8px!important}.un-mkt .un-l{display:none}.un-mkt .un-s{display:inline}}';
    document.head.appendChild(s);
  }

  /* ── start ── */
  function start() {
    style();
    var q = norm(new URLSearchParams(location.search).get('market'));
    if (q) write(KEY, q);
    var chosen = norm(read(KEY));
    var geo = norm(read(GEO, sessionStorage));
    visitor = chosen || geo || 'IN';
    document.documentElement.setAttribute('data-store', visitor.toLowerCase());
    addSwitch();
    sweep();
    new MutationObserver(later).observe(document.documentElement, { childList: true, subtree: true, attributes: true, attributeFilter: ['href'] });

    // On a developer's own machine there is no Cloudflare to ask (and no /api/country to answer).
    if (!chosen && !geo && !/^(localhost|127\.|\[::1\])/.test(location.hostname)) {
      fetch('/api/country', { cache: 'no-store' }).then(function (r) { return r.json(); }).then(function (j) {
        var m = j && j.country === 'US' ? 'US' : 'IN';
        write(GEO, m, sessionStorage);
        if (!norm(read(KEY)) && m !== visitor) { visitor = m; document.documentElement.setAttribute('data-store', m.toLowerCase()); paintSwitch(); sweep(); }
      }).catch(function () {});
    }
  }

  window.UNMarket = { current: function () { return visitor; }, set: choose, of: hostMarket };
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', start); else start();
})();
