/* SHOPPABLE ROOMS HERO
   Rooms staged with real Collection pieces. Each dot sits on a piece (x, y in
   percent of the photo) and opens a small card that links to that piece.
   Laptop: a soft spotlight follows the cursor, and the dots it reaches light up.
   Phone: the room is wider than the screen, so it drifts slowly sideways and
   can be dragged to look around; tap a dot for its card.
   The rooms crossfade on their own and wait while someone is exploring. */
(function () {
  var hero = document.querySelector('.hero.shop');
  if (!hero) return;
  var ROOMS = window.SHOP_ROOMS;
  var rooms = [].slice.call(hero.querySelectorAll('.sh-room'));
  var tabs = [].slice.call(hero.querySelectorAll('.sh-tab'));
  var eyebrow = hero.querySelector('.sh-eyebrow');
  var card = hero.querySelector('.sh-card');
  var fine = matchMedia('(hover: hover) and (pointer: fine)').matches;
  var reduced = matchMedia('(prefers-reduced-motion: reduce)').matches;
  /* after a touch, a phone picks up again sooner than a laptop does */
  var DUR = 10000, IDLE = fine ? 7000 : 4000;
  var cur = 0, t0 = performance.now(), held = 0, lastTouch = -1e9, visible = true;
  var items = {};

  /* ── names, prices and photos come from the live Collection ── */
  var ids = [];
  ROOMS.forEach(function (r) { r.dots.forEach(function (d) { ids.push(d.id); }); });
  if (typeof db !== 'undefined') db.from('collection_items').select('id,name,category,section,price,price_paise,image_url').in('id', ids)
    .then(function (res) { (res.data || []).forEach(function (it) { items[it.id] = it; }); });

  /* ── each frame covers the hero at the photo's own shape ── */
  var pan = rooms.map(function () { return { x: 0, min: 0, user: false }; });
  function layout() {
    var W = hero.clientWidth, H = hero.clientHeight;
    rooms.forEach(function (room, i) {
      var ar = ROOMS[i].ar, w = W, h = W / ar;
      if (h < H) { h = H; w = H * ar; }
      var f = room.querySelector('.sh-frame');
      f.style.width = w + 'px'; f.style.height = h + 'px';
      f.style.top = ((H - h) / 2) + 'px';
      pan[i].min = Math.min(0, W - w);
      if (!pan[i].user) pan[i].x = pan[i].min / 2;
      place(i);
    });
  }
  function place(i) {
    var p = pan[i]; p.x = Math.max(p.min, Math.min(0, p.x));
    rooms[i].querySelector('.sh-frame').style.transform = 'translate3d(' + p.x.toFixed(1) + 'px,0,0)';
  }
  addEventListener('resize', layout); layout();

  /* ── the slideshow ── */
  function show(i) {
    closeCard();
    rooms[cur].classList.remove('on', 'ready');
    cur = (i + rooms.length) % rooms.length;
    var z = rooms[cur].querySelector('.sh-zoom'); z.style.animation = 'none'; void z.offsetWidth; z.style.animation = '';
    rooms[cur].classList.add('on');
    pan[cur].user = false; layout();
    setTimeout(function (r) { r.classList.add('ready'); }, 500, rooms[cur]);
    eyebrow.classList.add('swap');
    setTimeout(function () { eyebrow.textContent = ROOMS[cur].label; eyebrow.classList.remove('swap'); }, 300);
    t0 = performance.now(); held = 0;
  }
  tabs.forEach(function (t) { t.addEventListener('click', function () { show(+t.dataset.i); lastTouch = performance.now(); }); });
  rooms[0].classList.add('on'); eyebrow.textContent = ROOMS[0].label;
  setTimeout(function () { rooms[0].classList.add('ready'); }, 700);

  /* the clock stops while the hero is off screen, a card is open, or someone touched it lately */
  var prev = performance.now();
  (function tick(now) {
    var dt = now - prev; prev = now;
    var busy = !visible || card.classList.contains('show') || now - lastTouch < IDLE || hero.matches(':hover') && fine;
    if (busy || reduced) held += dt;
    var p = Math.min(1, (now - t0 - held) / DUR);
    tabs.forEach(function (t, i) { t.style.setProperty('--p', i === cur ? p : 0); t.classList.toggle('on', i === cur); });
    if (p >= 1 && rooms.length > 1) show(cur + 1);
    /* phone: the wide room drifts slowly from one side to the other. After a
       drag it waits IDLE, then eases back onto its path instead of jumping. */
    if (!fine && !reduced && pan[cur].min < 0 && !card.classList.contains('show') && now - lastTouch >= IDLE) {
      var target = pan[cur].min * (0.2 + 0.6 * p);
      if (pan[cur].user) {
        pan[cur].x += (target - pan[cur].x) * 0.04;
        if (Math.abs(target - pan[cur].x) < 1) pan[cur].user = false;
      } else pan[cur].x = target;
      place(cur);
    }
    requestAnimationFrame(tick);
  })(prev);
  new IntersectionObserver(function (es) { visible = es[0].isIntersecting; }).observe(hero);

  /* ── phone: drag the room sideways to look around (vertical scroll still works) ── */
  var drag = null;
  hero.addEventListener('pointerdown', function (e) {
    if (e.pointerType === 'mouse' || e.target.closest('.sh-card, .sh-tab, a')) return;
    drag = { x: e.clientX, y: e.clientY, px: pan[cur].x, on: false };
  });
  hero.addEventListener('pointermove', function (e) {
    if (!drag) return;
    var dx = e.clientX - drag.x, dy = e.clientY - drag.y;
    if (!drag.on && Math.abs(dx) > 8 && Math.abs(dx) > Math.abs(dy)) { drag.on = true; closeCard(); }
    if (drag.on) { pan[cur].user = true; pan[cur].x = drag.px + dx; place(cur); lastTouch = performance.now(); }
  });
  addEventListener('pointerup', function () { drag = null; });
  addEventListener('pointercancel', function () { drag = null; });

  /* ── laptop: the spotlight, and the dots it reaches ── */
  if (fine && !reduced) {
    var tx = 0, ty = 0, x = 0, y = 0, inside = false;
    hero.addEventListener('pointermove', function (e) { var r = hero.getBoundingClientRect(); tx = e.clientX - r.left; ty = e.clientY - r.top; if (!inside) { x = tx; y = ty; } inside = true; hero.classList.add('lit'); });
    hero.addEventListener('pointerleave', function () { inside = false; hero.classList.remove('lit'); dots().forEach(function (d) { d.classList.remove('near'); }); });
    (function follow() {
      if (inside) {
        x += (tx - x) * .12; y += (ty - y) * .12;
        hero.style.setProperty('--sx', x.toFixed(1) + 'px'); hero.style.setProperty('--sy', y.toFixed(1) + 'px');
        var hr = hero.getBoundingClientRect();
        dots().forEach(function (d) {
          var r = d.getBoundingClientRect(), dx = r.left + r.width / 2 - hr.left - x, dy = r.top + r.height / 2 - hr.top - y;
          d.classList.toggle('near', dx * dx + dy * dy < 150 * 150);
        });
      }
      requestAnimationFrame(follow);
    })();
  }
  function dots() { return [].slice.call(rooms[cur].querySelectorAll('.sh-dot')); }

  /* ── a dot opens its piece's card ── */
  var openDot = null;
  function shortName(n) { return (n || '').split('|')[0].replace(/\s*\(.*?\)/g, '').trim(); }
  function price(it) {
    if (it.price_paise) return '₹' + Math.round(it.price_paise / 100).toLocaleString('en-IN');
    return String(it.price || '').replace(/INR\s*/g, '₹').replace(/\$/g, '₹').replace(/₹\s+/g, '₹').replace(/\s+to\s+/g, ' – ');
  }
  var CAT = { lighting: 'Chandeliers', luminaires: 'Luminaires', 'wall-art': 'Curated Wallscapes', sculptures: 'Sculptures', amphorae: 'Amphorae', timepieces: 'Timepieces', festive: 'Festivities', 'bath-essentials': 'Bath essentials', 'kitchen-essentials': 'Kitchen essentials', bedroom: 'Bedroom essentials' };
  function openCard(dot) {
    var d = ROOMS[cur].dots[+dot.dataset.n], it = items[d.id] || {};
    var page = (it.section || d.s) === 'essentials' ? 'essentials.html' : 'collection.html';
    var href = page + '?c=' + encodeURIComponent(it.category || d.c) + '&p=' + encodeURIComponent(d.id);
    card.href = href;
    card.querySelector('img').src = it.image_url ? unImg(it.image_url, 100) : '';
    card.querySelector('.k').textContent = CAT[it.category || d.c] || 'Collection';
    card.querySelector('.n').textContent = shortName(it.name) || d.label;
    card.querySelector('.p').textContent = price(it);
    if (openDot) openDot.classList.remove('open');
    openDot = dot; dot.classList.add('open');
    /* beside the dot on a laptop, kept inside the hero; a sheet on a phone (CSS) */
    var hr = hero.getBoundingClientRect(), r = dot.getBoundingClientRect();
    var cx = r.left - hr.left + r.width / 2, cy = r.top - hr.top + r.height / 2;
    var left = cx + 26, top = cy - 52;
    if (left + 290 > hr.width) left = cx - 26 - 280;
    top = Math.max(16, Math.min(hr.height - 130, top));
    card.style.left = left + 'px'; card.style.top = top + 'px';
    card.classList.add('show');
  }
  function closeCard() { card.classList.remove('show'); if (openDot) openDot.classList.remove('open'); openDot = null; }
  hero.addEventListener('click', function (e) {
    var dot = e.target.closest('.sh-dot');
    if (dot) { e.preventDefault(); if (dot === openDot) closeCard(); else openCard(dot); lastTouch = performance.now(); return; }
    if (!e.target.closest('.sh-card, .sh-tab, a')) closeCard();
  });
  addEventListener('keydown', function (e) { if (e.key === 'Escape') closeCard(); });
})();
