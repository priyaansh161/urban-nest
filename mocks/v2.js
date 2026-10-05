(function () {
  /* ── mock chrome ── */
  var notesBtn = document.getElementById('notesBtn');
  notesBtn.onclick = function () {
    var hidden = document.body.classList.toggle('hide-notes');
    notesBtn.setAttribute('aria-pressed', String(!hidden));
  };
  /* <base href="/"> would send "#rooms" to the live homepage; keep it here */
  document.addEventListener('click', function (e) {
    var a = e.target.closest && e.target.closest('a[href^="#"]');
    if (!a) return;
    var t = document.querySelector(a.getAttribute('href'));
    if (t) { e.preventDefault(); t.scrollIntoView({ behavior: 'smooth' }); }
  });

  var esc = function (s) {
    return String(s == null ? '' : s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/"/g, '&quot;');
  };

  /* ── THE SWIPE RAIL ──
     Touch scrolls natively with snap. A mouse can drag it or use the
     arrows. The dots underneath show where you are and hide themselves
     when everything already fits. */
  function unRail(rail) {
    if (!rail || rail.dataset.ready || !rail.children.length) return;
    rail.dataset.ready = '1';
    var sec = rail.closest('section');
    var arrows = sec && sec.querySelector('[data-arrows]');
    var progress = rail.nextElementSibling && rail.nextElementSibling.matches('[data-progress]') ? rail.nextElementSibling : null;
    var items = function () { return Array.prototype.slice.call(rail.children); };
    if (progress) progress.innerHTML = items().map(function () { return '<i></i>'; }).join('');

    function startOf(el) { return el.offsetLeft - rail.offsetLeft - 2; }
    function current() {
      var x = rail.scrollLeft, best = 0, bd = Infinity;
      items().forEach(function (it, i) { var d = Math.abs(startOf(it) - x); if (d < bd) { bd = d; best = i; } });
      if (x + rail.clientWidth >= rail.scrollWidth - 4) best = items().length - 1;
      return best;
    }
    function paint() {
      var fits = rail.scrollWidth <= rail.clientWidth + 4, c = current();
      if (progress) {
        progress.classList.toggle('idle', fits);
        Array.prototype.forEach.call(progress.children, function (d, i) { d.classList.toggle('on', i === c); });
      }
      if (arrows) {
        arrows.style.visibility = fits ? 'hidden' : '';
        arrows.children[0].disabled = rail.scrollLeft < 4;
        arrows.children[1].disabled = rail.scrollLeft + rail.clientWidth >= rail.scrollWidth - 4;
      }
      rail.dispatchEvent(new CustomEvent('railchange', { detail: c }));
    }
    function go(i) {
      var list = items();
      i = Math.max(0, Math.min(list.length - 1, i));
      rail.scrollTo({ left: startOf(list[i]), behavior: 'smooth' });
    }
    rail.unGo = go;
    if (arrows) {
      arrows.children[0].onclick = function () { go(current() - 1); };
      arrows.children[1].onclick = function () { go(current() + 1); };
    }
    rail.addEventListener('scroll', function () { requestAnimationFrame(paint); }, { passive: true });
    addEventListener('resize', paint);
    paint();

    var down = false, sx = 0, sl = 0, moved = false;
    rail.addEventListener('pointerdown', function (e) {
      if (e.pointerType !== 'mouse' || e.button !== 0) return;
      if (e.target.closest('button')) return;
      down = true; moved = false; sx = e.clientX; sl = rail.scrollLeft;
      e.preventDefault();
    });
    addEventListener('pointermove', function (e) {
      if (!down) return;
      var dx = e.clientX - sx;
      if (!moved && Math.abs(dx) > 5) { moved = true; rail.classList.add('dragging'); }
      if (moved) rail.scrollLeft = sl - dx;
    });
    addEventListener('pointerup', function () {
      if (!down) return;
      down = false;
      if (moved) { rail.classList.remove('dragging'); go(current()); setTimeout(function () { moved = false; }, 0); }
    });
    rail.addEventListener('click', function (e) { if (moved) { e.preventDefault(); e.stopPropagation(); } }, true);
  }
  window.unRail = unRail;

  /* ── saving a piece (the heart) ── */
  var saved = {};
  try { saved = JSON.parse(localStorage.getItem('un-saved') || '{}'); } catch (e) {}
  document.addEventListener('click', function (e) {
    var b = e.target.closest && e.target.closest('.pc-save');
    if (!b) return;
    e.preventDefault(); e.stopPropagation();
    var href = b.closest('a').getAttribute('href');
    var on = b.getAttribute('aria-pressed') !== 'true';
    b.setAttribute('aria-pressed', String(on));
    if (on) saved[href] = 1; else delete saved[href];
    try { localStorage.setItem('un-saved', JSON.stringify(saved)); } catch (e2) {}
  }, true);
  new MutationObserver(function () {
    document.querySelectorAll('.pc-save').forEach(function (b) {
      var a = b.closest('a');
      if (a && saved[a.getAttribute('href')]) b.setAttribute('aria-pressed', 'true');
    });
  }).observe(document.body, { childList: true, subtree: true });

  /* ── IN THE ROOM ──
     x / y are percentages of the photograph. Each photo keeps its own shape,
     so a dot sits on its object at every screen size without any maths.
     Names and prices are placeholders for the mock. */
  var ROOMS = [
    { room: 'Bedroom', title: 'The <em>bedroom.</em>', img: 'images/room-bedroom.webp', ar: '1100/1375', h: '600px', spots: [
      { x: 42, y: 36, n: 'Crystal rod chandelier, gold ring · 60 cm', p: '₹8,499', i: 'images/det-chandelier2.webp' },
      { x: 65, y: 34, n: 'Gold and black circles wall art, set of 2', p: '₹3,299', i: 'images/room-bedroom.webp' },
      { x: 88, y: 47, n: 'Glass table lamp, linen shade · 58 cm', p: '₹2,199', i: 'images/det-vase.webp' },
      { x: 19, y: 66, n: 'Velvet bench, brass frame · 120 cm', p: '₹11,999', i: 'images/room-bedroom.webp' },
      { x: 56, y: 63, n: 'Geometric knit throw · 130×170 cm', p: '₹1,499', i: 'images/band-warm.webp' },
      { x: 64, y: 87, n: 'Distressed grey rug · 5×8 ft', p: '₹6,799', i: 'images/band-calm.webp' } ] },
    { room: 'Bathroom', title: 'The <em>bathroom.</em>', img: 'images/room-bath.webp', ar: '1100/1375', h: '600px', spots: [
      { x: 87, y: 28, n: 'Round black-rim mirror · 80 cm', p: '₹4,299', i: 'images/room-bath.webp' },
      { x: 76, y: 60, n: 'Matte black basin mixer', p: '₹3,899', i: 'images/det-tap.webp' },
      { x: 36, y: 46, n: 'Matte black towel rail · 60 cm', p: '₹1,199', i: 'images/room-bath.webp' },
      { x: 65, y: 82, n: 'Walnut wall-hung vanity · 120 cm', p: '₹28,999', i: 'images/room-bath.webp' } ] },
    { room: 'Kitchen', title: 'The <em>kitchen.</em>', img: 'images/room-kitchen.webp', ar: '1100/1375', h: '600px', spots: [
      { x: 37, y: 32, n: 'Linen drum ceiling light · 40 cm', p: '₹3,499', i: 'images/room-kitchen.webp' },
      { x: 69, y: 47, n: 'Oak floating shelf, brass brackets · 90 cm', p: '₹1,899', i: 'images/room-kitchen.webp' },
      { x: 70, y: 60, n: 'Blush ceramic canister set of 3', p: '₹1,299', i: 'images/det-jug.webp' },
      { x: 34, y: 87, n: 'Flatweave cotton runner · 2×5 ft', p: '₹999', i: 'images/room-kitchen.webp' } ] },
    { room: 'Living', title: 'The <em>living room.</em>', img: 'images/tile-living.webp', ar: '1400/900', h: '520px', spots: [
      { x: 61, y: 22, n: 'Rattan sunburst mirrors, set of 2', p: '₹3,999', i: 'images/tile-living.webp' },
      { x: 86, y: 35, n: 'Tripod floor lamp, linen shade', p: '₹4,499', i: 'images/tile-living.webp' },
      { x: 26, y: 43, n: 'Dried pampas in white floor vase', p: '₹1,799', i: 'images/tile-vase.webp' },
      { x: 14, y: 68, n: 'Bouclé accent armchair', p: '₹14,999', i: 'images/tile-living.webp' },
      { x: 27, y: 80, n: 'Knitted cotton pouf · 45 cm', p: '₹2,299', i: 'images/tile-living.webp' },
      { x: 52, y: 68, n: 'White ceramic bud vase · 25 cm', p: '₹899', i: 'images/tile-vase.webp' },
      { x: 84, y: 72, n: 'Seagrass basket with handles', p: '₹1,199', i: 'images/tile-living.webp' } ] }
  ];
  var irRail = document.getElementById('irRail');
  var irPills = document.getElementById('irPills');
  irRail.innerHTML = ROOMS.map(function (r, ri) {
    return '<div class="ir-slide" data-room="' + ri + '">' +
      '<div class="ir-photo" style="--ar:' + r.ar + ';--h:' + r.h + '"><img src="' + r.img + '" alt="" loading="lazy" decoding="async"/>' +
        r.spots.map(function (s, si) {
          return '<button type="button" class="ir-dot" data-s="' + si + '" style="left:' + s.x + '%;top:' + s.y + '%" aria-label="' + esc(s.n) + '"></button>';
        }).join('') +
        '<a class="ir-pop" href="collection.html"><img alt=""/><span><span class="ir-pop-n"></span><span class="ir-pop-f"><span></span><span>View piece →</span></span></span></a>' +
      '</div>' +
      '<div class="ir-side"><div class="ir-side-room">' + r.title + '</div><div class="ir-side-count">' + r.spots.length + ' pieces in this photo</div>' +
        '<ul class="ir-list">' + r.spots.map(function (s, si) {
          return '<li><button type="button" data-s="' + si + '"><span>' + esc(s.n.split(' · ')[0]) + '</span><span>' + s.p + '</span></button></li>';
        }).join('') + '</ul></div>' +
    '</div>';
  }).join('');
  irPills.innerHTML = ROOMS.map(function (r, i) { return '<button type="button" data-i="' + i + '">' + r.room + '</button>'; }).join('');

  function openSpot(slide, si) {
    var r = ROOMS[+slide.dataset.room], s = r.spots[si];
    var photo = slide.querySelector('.ir-photo'), pop = slide.querySelector('.ir-pop');
    slide.querySelectorAll('.ir-dot, .ir-list button').forEach(function (b) { b.classList.toggle('on', +b.dataset.s === si); });
    pop.querySelector('img').src = s.i;
    pop.querySelector('.ir-pop-n').textContent = s.n;
    pop.querySelector('.ir-pop-f span').textContent = s.p;
    var pw = photo.clientWidth, ph = photo.clientHeight;
    var x = s.x / 100 * pw, y = s.y / 100 * ph;
    pop.classList.add('open');
    var w = pop.offsetWidth, h = pop.offsetHeight;
    pop.style.left = Math.min(Math.max(12, x - w / 2), pw - w - 12) + 'px';
    var top = y - h - 24; if (top < 12) top = Math.min(y + 24, ph - h - 12);
    pop.style.top = top + 'px';
  }
  function closeSpots(slide) {
    slide.querySelector('.ir-pop').classList.remove('open');
    slide.querySelectorAll('.on').forEach(function (b) { b.classList.remove('on'); });
  }
  irRail.addEventListener('click', function (e) {
    var slide = e.target.closest('.ir-slide');
    if (!slide) return;
    var b = e.target.closest('.ir-dot, .ir-list button');
    if (b) { e.preventDefault(); openSpot(slide, +b.dataset.s); return; }
    if (!e.target.closest('.ir-pop')) closeSpots(slide);
  });
  if (matchMedia('(hover: hover) and (pointer: fine)').matches) {
    irRail.addEventListener('mouseover', function (e) {
      var b = e.target.closest('.ir-list button');
      if (b) openSpot(b.closest('.ir-slide'), +b.dataset.s);
    });
  }
  irPills.addEventListener('click', function (e) {
    var b = e.target.closest('button');
    if (b && irRail.unGo) irRail.unGo(+b.dataset.i);
  });
  irRail.addEventListener('railchange', function (e) {
    Array.prototype.forEach.call(irPills.children, function (b, i) { b.classList.toggle('on', i === e.detail); });
  });

  /* ── the deck: the four pillars, one card at a time ── */
  var CARDS = [
    { c: 'c0', t: 'Small things, big impact', d: 'A soap dispenser, a bath rug, a cotton jar. The little things that quietly transform a home.' },
    { c: 'c2', t: 'See it before you buy it', d: 'Walk through curated rooms. Discover products in context, not on a shelf.' },
    { c: 'c3', t: 'Curated, not catalogued', d: 'Every item is chosen for how it functions, how it looks, and how it fits your life.' },
    { c: 'c1', t: 'The complete look', d: 'Buy the feeling, not just the product. Collections designed to work together.' }
  ];
  var deck = document.getElementById('deck'), count = document.getElementById('deckCount'), top = 0;
  function renderDeck() {
    deck.innerHTML = '';
    for (var k = 2; k >= 0; k--) {
      var i = (top + k) % CARDS.length, d = CARDS[i];
      var el = document.createElement('div');
      el.className = 'dcard ' + d.c;
      el.innerHTML = '<span class="dcard-n">0' + (i + 1) + ' / 04</span>' +
        '<div><div class="dcard-t">' + d.t + '</div><p class="dcard-d">' + d.d + '</p></div>' +
        '<span class="dcard-hint">' + (k === 0 ? 'Swipe →' : '') + '</span>';
      el.style.transform = 'translate(' + (k * 12) + 'px,' + (k * 12) + 'px)';
      el.style.zIndex = 10 - k;
      if (k === 0) drag(el);
      deck.appendChild(el);
    }
    count.textContent = (top + 1) + ' / ' + CARDS.length;
  }
  function fling(el, dir) {
    el.style.transform = 'translateX(' + dir * 130 + '%) rotate(' + dir * 18 + 'deg)';
    el.style.opacity = '0';
    setTimeout(function () { top = (top + 1) % CARDS.length; renderDeck(); }, 300);
  }
  function drag(el) {
    var sx = 0, dx = 0, on = false;
    el.addEventListener('pointerdown', function (e) { on = true; sx = e.clientX; dx = 0; el.setPointerCapture(e.pointerId); el.style.transition = 'none'; });
    el.addEventListener('pointermove', function (e) { if (!on) return; dx = e.clientX - sx; el.style.transform = 'translateX(' + dx + 'px) rotate(' + dx / 20 + 'deg)'; });
    function end() {
      if (!on) return; on = false; el.style.transition = '';
      if (Math.abs(dx) > 80) fling(el, dx > 0 ? 1 : -1); else el.style.transform = '';
    }
    el.addEventListener('pointerup', end);
    el.addEventListener('pointercancel', end);
  }
  document.getElementById('deckNext').onclick = function () { fling(deck.lastElementChild, 1); };
  document.getElementById('deckBack').onclick = function () { top = (top - 1 + CARDS.length) % CARDS.length; renderDeck(); };
  renderDeck();

  /* ── The Nest Edit, from the live articles ── */
  var edRail = document.getElementById('edRail');
  var FALLBACK = [
    { title: 'Why your bathroom still feels unfinished', category: 'Bathroom', read_time: '3 min', image_url: 'images/cover-bath-2.webp' },
    { title: 'Three lamps, one mood', category: 'Light', read_time: '4 min', image_url: 'images/det-pendants.webp' },
    { title: 'The ₹500 kitchen fix', category: 'Kitchen', read_time: '2 min', image_url: 'images/cover-kitchen-2.webp' },
    { title: 'Jugaad, outgrown', category: 'Ideas', read_time: '5 min', image_url: 'images/det-vase.webp' },
    { title: 'One flower, one jug, done', category: 'Styling', read_time: '3 min', image_url: 'images/tile-peony.webp' }
  ];
  function paintEdit(rows) {
    edRail.innerHTML = rows.map(function (p) {
      var href = p.id != null ? 'community.html?a=' + encodeURIComponent(p.id) : 'community.html';
      return '<a class="ed" href="' + href + '"><span class="ed-ph"><img src="' + esc(p.image_url || 'images/det-vase.webp') + '" alt="" loading="lazy" decoding="async"/>' +
        '<span class="ed-tag">' + esc(p.category || 'The Nest') + '</span></span>' +
        '<span class="ed-panel"><span class="ed-t">' + esc(p.title) + '</span>' +
        '<span class="ed-m"><span>' + esc(p.read_time || '') + '</span><span>Read →</span></span></span></a>';
    }).join('');
    unRail(edRail);
  }
  if (typeof db !== 'undefined') {
    db.from('nest_posts').select('*').eq('published', true)
      .order('pinned', { ascending: false }).order('created_at', { ascending: false }).limit(10)
      .then(function (r) { paintEdit((r && r.data && r.data.length) ? r.data : FALLBACK); }, function () { paintEdit(FALLBACK); });
  } else paintEdit(FALLBACK);

  /* ── making do / just right ──
     Mouse: drag anywhere to compare; arrows change room.
     Touch: a drag that starts near the handle compares; a sideways swipe
     anywhere else changes room; a tap moves the handle there. Up/down
     always scrolls the page (touch-action: pan-y).
     "before" is a stand-in until the real making-do photos exist. */
  var PAIRS = [
    { k: 'Living room', after: 'images/tile-living.webp',  before: 'images/tile-living.webp',  shop: 'essentials.html' },
    { k: 'Bathroom',    after: 'images/room-bath.webp',    before: 'images/room-bath.webp',    shop: 'essentials.html' },
    { k: 'Bedroom',     after: 'images/room-bedroom.webp', before: 'images/room-bedroom.webp', shop: 'essentials.html' },
    { k: 'Kitchen',     after: 'images/room-kitchen.webp', before: 'images/room-kitchen.webp', shop: 'essentials.html' }
  ];
  var baStage = document.getElementById('baStage'), baRange = document.getElementById('baRange');
  var baDots = document.getElementById('baDots'), baRoom = document.getElementById('baRoom');
  var cur = 0, pos = 50, touched = false;
  baDots.innerHTML = PAIRS.map(function () { return '<i></i>'; }).join('');
  function setPos(v) { pos = Math.max(0, Math.min(100, v)); baStage.style.setProperty('--pos', pos + '%'); baRange.value = Math.round(pos); }
  function paintPair() {
    var p = PAIRS[cur];
    document.getElementById('baAfter').src = p.after;
    document.getElementById('baBefore').src = p.before;
    document.getElementById('baShop').href = p.shop;
    baRoom.textContent = p.k;
    Array.prototype.forEach.call(baDots.children, function (d, j) { d.classList.toggle('on', j === cur); });
    setPos(50);
  }
  function goRoom(dir) {
    touched = true;
    document.getElementById('baSwipe').classList.add('gone');
    baStage.classList.add(dir > 0 ? 'out-l' : 'out-r');
    setTimeout(function () {
      cur = (cur + dir + PAIRS.length) % PAIRS.length;
      paintPair();
      baStage.classList.remove('out-l', 'out-r');
    }, 220);
  }
  paintPair();
  document.getElementById('baPrev').onclick = function () { goRoom(-1); };
  document.getElementById('baNext').onclick = function () { goRoom(1); };
  baStage.addEventListener('keydown', function (e) {
    if (e.key === 'PageDown') { e.preventDefault(); goRoom(1); }
    if (e.key === 'PageUp') { e.preventDefault(); goRoom(-1); }
  });

  function pct(e) { var r = baStage.getBoundingClientRect(); return (e.clientX - r.left) / r.width * 100; }
  var g = null;   // the gesture in progress
  baStage.addEventListener('pointerdown', function (e) {
    touched = true;
    var r = baStage.getBoundingClientRect();
    var nearHandle = Math.abs(e.clientX - (r.left + pos / 100 * r.width)) < 44;
    var mouse = e.pointerType === 'mouse';
    g = { id: e.pointerId, x: e.clientX, y: e.clientY, mode: (mouse || nearHandle) ? 'drag' : 'pending' };
    baStage.setPointerCapture(e.pointerId);
    if (g.mode === 'drag') { baStage.classList.add('dragging'); setPos(pct(e)); }
  });
  baStage.addEventListener('pointermove', function (e) {
    if (!g || e.pointerId !== g.id) return;
    if (g.mode === 'drag') { setPos(pct(e)); return; }
    var dx = e.clientX - g.x, dy = e.clientY - g.y;
    if (g.mode === 'pending' && Math.abs(dx) > 10 && Math.abs(dx) > Math.abs(dy)) g.mode = 'swipe';
    if (g.mode === 'swipe') baStage.style.transform = 'translateX(' + dx * 0.25 + 'px)';
  });
  function end(e) {
    if (!g || e.pointerId !== g.id) return;
    var dx = e.clientX - g.x, dy = e.clientY - g.y;
    baStage.classList.remove('dragging');
    baStage.style.transform = '';
    if (g.mode === 'swipe' && Math.abs(dx) > 50 && e.type === 'pointerup') goRoom(dx < 0 ? 1 : -1);
    else if (g.mode === 'pending' && Math.abs(dx) < 8 && Math.abs(dy) < 8 && e.type === 'pointerup') {
      setPos(pct(e));
    }
    g = null;
  }
  baStage.addEventListener('pointerup', end);
  baStage.addEventListener('pointercancel', end);
  baRange.addEventListener('input', function () { touched = true; setPos(+baRange.value); });

  /* the first time it scrolls into view the handle sweeps once, so people
     see that it moves; it stops the moment anyone touches it */
  if ('IntersectionObserver' in window && !matchMedia('(prefers-reduced-motion: reduce)').matches) {
    var io = new IntersectionObserver(function (es) {
      if (!es[0].isIntersecting) return;
      io.disconnect();
      var t0 = null;
      (function step(t) {
        if (touched) return;
        if (t0 == null) t0 = t;
        var k = (t - t0) / 2200;
        if (k >= 1) { setPos(50); return; }
        setPos(50 + Math.sin(k * Math.PI * 2) * 22);
        requestAnimationFrame(step);
      })(performance.now());
    }, { threshold: 0.6 });
    io.observe(baStage);
  }

  document.querySelectorAll('[data-rail]').forEach(unRail);
})();
