/* The scroll bar for the one-card-at-a-time phone view (Collection and
 * Essentials, html.reel). Asked for on 28 Oct 2026: swiping up one card at a
 * time is right, but someone who wants the piece at the bottom needs a way
 * to get there without twenty swipes.
 *
 * A thin bar on the right edge, shown while the cards are on screen and
 * fading out when nothing moves, the way iOS does. Drag its thumb:
 *   - the thumb stays under the finger and the page glides after it, eased
 *     every frame, so it never jumps or shudders;
 *   - the speed adapts: a slow drag moves about one card per 40px, so a
 *     single piece can be picked out of a long list, while a quick drag
 *     covers the list in proportion to the bar. However many pieces a
 *     category grows to, slow stays precise and fast stays fast;
 *   - a label beside the thumb says "7 / 15" while dragging;
 *   - letting go settles on the nearest card, and the page's normal
 *     swipe-one-card snapping comes straight back.
 * A tap on the bar jumps to that point. Laptops never see any of this. */
(function () {
  if (!window.matchMedia || !matchMedia('(max-width: 700px)').matches) return;
  var root = document.documentElement;
  if (!root.classList.contains('reel')) return;

  var css = document.createElement('style');
  css.textContent =
    '.rs{position:fixed;right:2px;width:30px;z-index:60;touch-action:none;opacity:0;pointer-events:none;transition:opacity .35s}' +
    '.rs.on{opacity:1;pointer-events:auto}' +
    '.rs-line{position:absolute;top:0;bottom:0;right:7px;width:3px;border-radius:3px;background:rgba(128,140,142,.28)}' +
    '.rs-thumb{position:absolute;right:4px;width:9px;height:44px;border-radius:9px;background:var(--gold,#A37B3F);box-shadow:0 1px 6px rgba(0,0,0,.3);transition:transform .2s,width .2s}' +
    '.rs.drag .rs-thumb{width:11px;right:3px}' +
    '.rs-tip{position:absolute;right:26px;padding:6px 10px;border-radius:100px;font:500 11px/1 "DM Sans",sans-serif;letter-spacing:.06em;white-space:nowrap;background:rgba(8,8,7,.78);color:#F5F7F6;opacity:0;transition:opacity .2s;pointer-events:none}' +
    '.rs.drag .rs-tip{opacity:1}' +
    '@media (prefers-reduced-motion: reduce){.rs,.rs-tip{transition:none}}';
  document.head.appendChild(css);

  var bar = document.createElement('div');
  bar.className = 'rs';
  bar.setAttribute('aria-hidden', 'true');          // a touch convenience; the cards themselves stay the way to read the page
  bar.innerHTML = '<div class="rs-line"></div><div class="rs-thumb"></div><div class="rs-tip"></div>';
  document.body.appendChild(bar);
  var thumb = bar.querySelector('.rs-thumb'), tip = bar.querySelector('.rs-tip');

  var cards = [], len = 0, pos = 0, dragging = false, hideT = 0;
  var navH = function () { return parseFloat(getComputedStyle(root).getPropertyValue('--navh')) || 64; };
  var topOf = function (i) { return cards[i].getBoundingClientRect().top + scrollY - navH() - 10; };

  function collect() {
    cards = [].filter.call(document.querySelectorAll('.grid > .item, .cats > .cat-tile'), function (c) { return c.offsetParent !== null; });
  }
  function place() {
    var top = navH() + 12, bottom = 28;
    bar.style.top = top + 'px'; bar.style.bottom = bottom + 'px';
    len = innerHeight - top - bottom - 44;          // travel of the thumb
  }
  // Where the page is, as a card index with a fraction (2.5 = halfway from the third card to the fourth).
  function indexAtScroll() {
    var y = scrollY;
    for (var i = cards.length - 1; i >= 0; i--) {
      var t = topOf(i);
      if (y >= t) { var next = i + 1 < cards.length ? topOf(i + 1) : t + 1; return Math.min(cards.length - 1, i + Math.min(1, (y - t) / Math.max(1, next - t))); }
    }
    return 0;
  }
  function draw() {
    var n = cards.length - 1;
    thumb.style.transform = 'translateY(' + (n > 0 ? pos / n * len : 0) + 'px)';
    tip.style.top = (n > 0 ? pos / n * len : 0) + 14 + 'px';
    tip.textContent = Math.round(pos) + 1 + ' / ' + cards.length;
  }
  function show() {
    clearTimeout(hideT);
    bar.classList.add('on');
    if (!dragging) hideT = setTimeout(function () { bar.classList.remove('on'); }, 1400);
  }

  // Following the page: the bar appears only once the cards are on screen, and only for a list worth scrubbing.
  addEventListener('scroll', function () {
    if (dragging) return;
    collect();
    if (cards.length < 4 || scrollY < topOf(0) - innerHeight * 0.5 || scrollY > topOf(cards.length - 1) + innerHeight) { bar.classList.remove('on'); return; }
    pos = indexAtScroll(); draw(); show();
  }, { passive: true });
  addEventListener('resize', place);
  place();

  // Dragging. The page eases toward where the thumb says, every frame.
  var lastY = 0, lastT = 0, target = 0, raf = 0;
  function glide() {
    var d = target - scrollY;
    if (Math.abs(d) < 0.5) { scrollTo(0, target); raf = 0; return; }
    scrollTo(0, scrollY + d * 0.32);
    raf = requestAnimationFrame(glide);
  }
  function aim() {
    var i = Math.floor(pos), f = pos - i, a = topOf(i), b = i + 1 < cards.length ? topOf(i + 1) : a;
    target = a + (b - a) * f;
    if (!raf) raf = requestAnimationFrame(glide);
  }
  function setFromFinger(clientY) {        // the tap: straight to that point of the bar
    var y = clientY - bar.getBoundingClientRect().top - 22;
    pos = Math.max(0, Math.min(cards.length - 1, y / Math.max(1, len) * (cards.length - 1)));
  }

  bar.addEventListener('pointerdown', function (e) {
    collect(); if (cards.length < 2) return;
    dragging = true; bar.classList.add('drag'); show();
    bar.setPointerCapture(e.pointerId);
    root.style.scrollSnapType = 'none';       // snapping would fight the glide
    var r = thumb.getBoundingClientRect();
    if (e.clientY < r.top - 6 || e.clientY > r.bottom + 6) setFromFinger(e.clientY);   // not on the thumb: jump there
    lastY = e.clientY; lastT = e.timeStamp;
    draw(); aim();
    e.preventDefault();
  });
  bar.addEventListener('pointermove', function (e) {
    if (!dragging) return;
    var dy = e.clientY - lastY, dt = Math.max(1, e.timeStamp - lastT);
    lastY = e.clientY; lastT = e.timeStamp;
    var n = cards.length - 1;
    var whole = n / Math.max(1, len);          // cards per px if the bar spans the whole list
    var fine = 1 / 40;                         // cards per px when picking one out
    var gain = whole <= fine ? whole : fine + (whole - fine) * Math.min(1, Math.max(0, (Math.abs(dy) / dt - 0.25) / 0.9));
    pos = Math.max(0, Math.min(n, pos + dy * gain));
    draw(); aim();
  });
  function release() {
    if (!dragging) return;
    dragging = false; bar.classList.remove('drag');
    pos = Math.round(pos); draw();
    cancelAnimationFrame(raf); raf = 0;
    scrollTo({ top: topOf(pos), behavior: 'smooth' });
    setTimeout(function () { root.style.scrollSnapType = ''; }, 450);
    show();
  }
  bar.addEventListener('pointerup', release);
  bar.addEventListener('pointercancel', release);
})();
