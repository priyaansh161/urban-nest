
(function () {
  var hero = document.querySelector('.hero');
  var slides = [].slice.call(document.querySelectorAll('.reel-slide'));
  var bars = [].slice.call(document.querySelectorAll('.reel-bar'));
  var reduced = matchMedia('(prefers-reduced-motion: reduce)').matches;
  var DUR = 8000, cur = 0, t0 = performance.now(), visible = true, paused = 0;

  requestAnimationFrame(function () { hero.classList.add('go'); });

  function show(i) {
    slides[cur].classList.remove('on');
    cur = (i + slides.length) % slides.length;
    // restart the slow zoom on the incoming slide
    var img = slides[cur].querySelector('img'); img.style.animation = 'none'; void img.offsetWidth; img.style.animation = '';
    slides[cur].classList.add('on');
    t0 = performance.now();
  }
  bars.forEach(function (b) { b.addEventListener('click', function () { show(+b.dataset.i); }); });

  /* the bars fill like stories; the reel waits while the hero is off screen */
  (function tick(now) {
    if (!reduced && visible) {
      var p = Math.min(1, (now - t0) / DUR);
      bars.forEach(function (b, i) { b.style.setProperty('--p', i < cur ? 1 : i === cur ? p : 0); b.classList.toggle('on', i === cur); });
      if (p >= 1) show(cur + 1);
    } else if (!visible) t0 = now - paused;
    requestAnimationFrame(tick);
  })(performance.now());
  new IntersectionObserver(function (es) {
    visible = es[0].isIntersecting;
    if (!visible) paused = performance.now() - t0;
  }).observe(hero);
  if (reduced) bars.forEach(function (b, i) { b.style.setProperty('--p', i === 0 ? 1 : 0); });

  /* the spotlight follows the cursor, eased (lerp 0.07) */
  var spot = document.getElementById('spot');
  if (matchMedia('(hover: hover) and (pointer: fine)').matches && !reduced) {
    var tx = innerWidth / 2, ty = innerHeight * .45, x = tx, y = ty;
    hero.addEventListener('pointermove', function (e) { var r = hero.getBoundingClientRect(); tx = e.clientX - r.left; ty = e.clientY - r.top; });
    (function follow() {
      x += (tx - x) * .07; y += (ty - y) * .07;
      spot.style.setProperty('--sx', x.toFixed(1) + 'px'); spot.style.setProperty('--sy', y.toFixed(1) + 'px');
      requestAnimationFrame(follow);
    })();
  }

  /* gold rules draw in once, as their heading arrives */
  var io = new IntersectionObserver(function (es) {
    es.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add('ruled'); io.unobserve(e.target); } });
  }, { threshold: .6 });
  document.querySelectorAll('.spaces-head, .collect-head').forEach(function (h) { io.observe(h); });
})();
