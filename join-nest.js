/* The "Join the Nest" envelope, on every page, on a phone.
 *
 * The home page has its own copy (index.html: a card that opens after a few seconds on a laptop, and only this button on a
 * phone). This is the same button for every other page, so nobody has to go back to the home page to find it. Phones only: a
 * laptop keeps the pages exactly as they were. It shares the home page's memory (localStorage "un-join-card"), so someone
 * who has joined never sees it again. It stays the size it was: it is the thing we want people to use. 6 Nov 2026.
 */
(function () {
  if (!window.matchMedia || !matchMedia('(max-width: 600px)').matches) return;
  if (document.getElementById('jn') || document.getElementById('jn2')) return;      // the home page brings its own
  var KEY = 'un-join-card', state = null;
  try { state = JSON.parse(localStorage.getItem(KEY) || 'null'); } catch (e) {}
  if (state && state.joined) return;

  var css = document.createElement('style');
  css.textContent =
    ':root{--jn-bg:#FFFFFF;--jn-ink:#0F1F22;--jn-dim:#586366;--jn-line:#CFDCD9;--jn-gold:#735427;--jn-lift:0 2px 6px rgba(8,8,7,.09),0 18px 40px rgba(8,8,7,.18)}' +
    '@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--jn-bg:#0A2429;--jn-ink:#EAF2F1;--jn-dim:#7F9295;--jn-line:#1E4148;--jn-gold:#C2934D;--jn-lift:inset 0 0 0 1px rgba(234,242,241,.11),0 16px 38px rgba(0,0,0,.5)}}' +
    ':root[data-theme="dark"]{--jn-bg:#0A2429;--jn-ink:#EAF2F1;--jn-dim:#7F9295;--jn-line:#1E4148;--jn-gold:#C2934D;--jn-lift:inset 0 0 0 1px rgba(234,242,241,.11),0 16px 38px rgba(0,0,0,.5)}' +
    '.jn2{position:fixed;left:18px;right:18px;bottom:calc(18px + env(safe-area-inset-bottom));z-index:300;padding:20px 18px 16px;background:var(--jn-bg);color:var(--jn-ink);border-radius:24px;box-shadow:var(--jn-lift);transform:translateY(20px);opacity:0;pointer-events:none;transition:transform .45s cubic-bezier(.16,.7,.2,1),opacity .3s;font-family:"DM Sans",system-ui,sans-serif}' +
    '.jn2.show{transform:none;opacity:1;pointer-events:auto}' +
    '.jn2-x{position:absolute;top:8px;right:8px;width:36px;height:36px;border:0;background:none;color:var(--jn-dim);font-size:22px;line-height:1;cursor:pointer;border-radius:50%}' +
    '.jn2-k{font-size:10px;letter-spacing:.24em;color:var(--jn-gold);font-weight:500}' +
    '.jn2-t{font-family:"Bodoni Moda",serif;font-size:21px;font-weight:400;line-height:1.2;margin:8px 30px 8px 0}' +
    '.jn2-d{font-size:13px;line-height:1.7;color:var(--jn-dim)}' +
    '.jn2-f{display:flex;gap:8px;margin-top:16px}' +
    '.jn2-f input{flex:1;min-width:0;padding:12px 14px;border-radius:100px;border:1px solid var(--jn-line);background:transparent;color:var(--jn-ink);font:inherit;font-size:16px}' +
    '.jn2-f button{padding:0 18px;border-radius:100px;border:0;background:var(--jn-ink);color:var(--jn-bg);font:inherit;font-size:10px;letter-spacing:.18em;font-weight:500;cursor:pointer}' +
    '.jn2-m{font-size:12px;color:var(--jn-dim);margin-top:10px;min-height:1em}' +
    '.jn2-dot{position:fixed;right:max(22px,env(safe-area-inset-right));bottom:calc(22px + env(safe-area-inset-bottom));z-index:299;width:48px;height:48px;border-radius:50%;border:0;cursor:pointer;display:grid;place-items:center;background:var(--jn-bg);color:var(--jn-gold);box-shadow:var(--jn-lift)}' +
    '.jn2-dot svg{width:22px;height:22px}';
  document.head.appendChild(css);

  var wrap = document.createElement('div');
  wrap.innerHTML =
    '<div class="jn2" id="jn2" role="dialog" aria-label="Join the Nest" aria-hidden="true">' +
      '<button class="jn2-x" type="button" id="jn2X" aria-label="Fold away">&times;</button>' +
      '<div class="jn2-k">JOIN THE NEST</div>' +
      '<div class="jn2-t" id="jn2T">New pieces, before anyone else.</div>' +
      '<div class="jn2-d" id="jn2D">The odd email when a piece or a room is worth seeing. No spam.</div>' +
      '<form class="jn2-f" id="jn2F" novalidate><input type="email" id="jn2E" placeholder="Your email" autocomplete="email" aria-label="Your email"/><button type="submit" id="jn2B">JOIN</button></form>' +
      '<div class="jn2-m" id="jn2M" aria-live="polite"></div>' +
    '</div>' +
    '<button class="jn2-dot" type="button" id="jn2Dot" aria-label="Join the Nest: get new pieces by email" title="Join the Nest">' +
      '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="5.5" width="18" height="13" rx="2.5"/><path d="M3.8 7l8.2 6 8.2-6"/></svg>' +
    '</button>';
  document.body.appendChild(wrap);

  var card = document.getElementById('jn2'), dot = document.getElementById('jn2Dot');
  var save = function (v) { try { localStorage.setItem(KEY, JSON.stringify(v)); } catch (e) {} };
  function open() { dot.style.display = 'none'; card.classList.add('show'); card.setAttribute('aria-hidden', 'false'); setTimeout(function () { document.getElementById('jn2E').focus(); }, 350); }
  function fold() { card.classList.remove('show'); card.setAttribute('aria-hidden', 'true'); dot.style.display = ''; }
  dot.addEventListener('click', open);
  document.getElementById('jn2X').addEventListener('click', fold);
  document.addEventListener('keydown', function (e) { if (e.key === 'Escape' && card.classList.contains('show')) fold(); });

  // The same table and the same public key the home page writes with (see supabase.js).
  var SB = 'https://ifwxgwvsyispkaxzbstg.supabase.co/rest/v1/subscribers';
  var ANON = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imlmd3hnd3ZzeWlzcGtheHpic3RnIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODI3MjI3ODQsImV4cCI6MjA5ODI5ODc4NH0.goQIrgT8-tSbN7nIEvHGifKjczi0JhgY01FVu_lQc4c';
  document.getElementById('jn2F').addEventListener('submit', function (e) {
    e.preventDefault();
    var email = document.getElementById('jn2E').value.trim(), m = document.getElementById('jn2M'), b = document.getElementById('jn2B');
    if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email)) { m.textContent = 'That email doesn’t look right.'; return; }
    b.disabled = true; m.textContent = '';
    fetch(SB, { method: 'POST', headers: { apikey: ANON, Authorization: 'Bearer ' + ANON, 'Content-Type': 'application/json', Prefer: 'return=minimal' }, body: JSON.stringify({ email: email, source: 'popup-phone' }) })
      .then(function (r) { return r.ok ? '' : r.text(); })
      .then(function (err) {
        b.disabled = false;
        var dup = err && /unique|duplicate/i.test(err);
        if (err && !dup) { m.textContent = 'That didn’t go through. Try again in a moment.'; return; }
        save({ joined: true });
        document.getElementById('jn2F').hidden = true;
        document.getElementById('jn2T').textContent = dup ? 'You’re already in.' : 'You’re in. Welcome to the Nest.';
        document.getElementById('jn2D').textContent = 'We’ll write when there’s something worth your inbox.';
        setTimeout(function () { card.classList.remove('show'); setTimeout(function () { wrap.remove(); }, 500); }, 4000);
      })
      .catch(function () { b.disabled = false; m.textContent = 'That didn’t go through. Try again in a moment.'; });
  });
})();
