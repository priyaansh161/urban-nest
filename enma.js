/* Enma, the Urban Nest assistant: the small round chat button and its chat window (18 Nov 2026).
 * Talks to POST /api/chat (functions/api/chat.js). Self-contained: brings its own styles and markup, and keeps the
 * conversation id and its messages in localStorage so a reload carries on the same chat.
 *
 * It lives in the bottom-right corner with the Join the Nest envelope (join-nest.js; the home page's own #jn), one circle
 * above the other. Enma always sits just above whatever the Join the Nest corner is showing: its little round button, or
 * the open card, so when the card opens Enma's circle glides up above it, and when it folds the circle comes back down.
 * The chat and the card never cover each other: opening one folds the other.
 */
(function () {
  if (document.getElementById('enma-btn')) return;
  var KEY = 'un-enma-v1';
  var GREETING = "Hi, I'm Enma. I can help you find a piece for your home, show you around the 3D rooms, or explain how buying works. What are you looking for?";
  var CHIPS = ['Find a piece for my room', 'What is Urban Nest?', 'How does buying work?', 'I am a designer or a seller'];
  var GAP = 12, EDGE = 22;

  var state = load() || { id: uuid(), msgs: [] };
  var busy = false;

  var css =
    ':root{--en-bg:#FFFFFF;--en-ink:#0F1F22;--en-dim:#586366;--en-line:#CFDCD9;--en-gold:#735427;--en-teal:#0E3238;--en-soft:#F2F6F5;--en-lift:0 2px 6px rgba(8,8,7,.09),0 18px 40px rgba(8,8,7,.18)}' +
    '@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--en-bg:#0A2429;--en-ink:#EAF2F1;--en-dim:#7F9295;--en-line:#1E4148;--en-gold:#C2934D;--en-teal:#0B343C;--en-soft:#061E23;--en-lift:inset 0 0 0 1px rgba(234,242,241,.11),0 16px 38px rgba(0,0,0,.5)}}' +
    ':root[data-theme="dark"]{--en-bg:#0A2429;--en-ink:#EAF2F1;--en-dim:#7F9295;--en-line:#1E4148;--en-gold:#C2934D;--en-teal:#0B343C;--en-soft:#061E23;--en-lift:inset 0 0 0 1px rgba(234,242,241,.11),0 16px 38px rgba(0,0,0,.5)}' +
    '#enma-btn{position:fixed;right:max(' + EDGE + 'px,env(safe-area-inset-right));bottom:' + EDGE + 'px;z-index:298;width:52px;height:52px;border-radius:50%;border:0;cursor:pointer;display:grid;place-items:center;background:var(--en-bg);color:var(--en-gold);box-shadow:var(--en-lift);transition:bottom .45s cubic-bezier(.16,.7,.2,1),transform .25s,opacity .25s;padding:0;margin:0}' +
    '#enma-btn:hover{transform:translateY(-2px)}#enma-btn svg{width:22px;height:22px}' +
    '#enma-btn .tip{position:absolute;right:62px;top:50%;transform:translateY(-50%);white-space:nowrap;background:var(--en-ink);color:var(--en-bg);font:500 10px/1 "DM Sans",system-ui,sans-serif;letter-spacing:.18em;padding:8px 11px;border-radius:100px;opacity:0;pointer-events:none;transition:opacity .2s}' +
    '#enma-btn:hover .tip{opacity:1}' +
    '#enma-btn.hide{opacity:0;transform:scale(.8);pointer-events:none}' +
    '#enma{position:fixed;right:max(' + EDGE + 'px,env(safe-area-inset-right));bottom:' + EDGE + 'px;z-index:301;width:380px;max-width:calc(100vw - 32px);height:min(600px,calc(100vh - 48px));display:flex;flex-direction:column;background:var(--en-bg);color:var(--en-ink);border-radius:24px;box-shadow:var(--en-lift);overflow:hidden;font:14px/1.6 "DM Sans",system-ui,sans-serif;padding:0;margin:0;opacity:0;transform:translateY(16px) scale(.98);transform-origin:bottom right;pointer-events:none;transition:opacity .3s,transform .45s cubic-bezier(.16,.7,.2,1)}' +
    '#enma.open{opacity:1;transform:none;pointer-events:auto}' +
    '#enma header{display:flex;align-items:center;justify-content:space-between;gap:10px;padding:16px 18px;background:var(--en-teal);color:#F5F7F6;margin:0}' +
    '#enma header b{display:block;font:400 19px/1.1 "Bodoni Moda",serif;letter-spacing:.02em}' +
    '#enma header small{display:block;color:#C2934D;font-size:9px;letter-spacing:.24em;margin-top:5px}' +
    '#enma header>div:last-child{display:flex;align-items:center;gap:2px;flex-shrink:0}' +
    '#enma header button{background:none;border:0;color:#F5F7F6;cursor:pointer;padding:7px 9px;border-radius:100px;font:500 10px/1 "DM Sans",system-ui,sans-serif;letter-spacing:.14em;opacity:.8}' +
    '#enma header button:hover{opacity:1;background:rgba(255,255,255,.1)}#enma header button.x{font-size:18px;letter-spacing:0}' +
    '#enma .log{flex:1;overflow-y:auto;padding:16px;display:flex;flex-direction:column;gap:10px;background:var(--en-soft);margin:0}' +
    '#enma .m{flex-shrink:0;max-width:86%;padding:10px 13px;border-radius:16px;white-space:pre-wrap;word-wrap:break-word;margin:0}' +
    '#enma .m.a{background:var(--en-bg);border:1px solid var(--en-line);align-self:flex-start;border-bottom-left-radius:5px}' +
    '#enma .m.u{background:var(--en-teal);color:#F5F7F6;align-self:flex-end;border-bottom-right-radius:5px}' +
    '#enma .m a{color:var(--en-gold);text-decoration:underline;word-break:break-word}#enma .m.u a{color:#E5C48F}' +
    '#enma .m.err{border-color:#E8B9A4}' +
    // picture cards for the pieces Enma links to: a row you can swipe, tap one to open it
    '#enma .cards{display:flex;flex-shrink:0;gap:8px;overflow-x:auto;align-self:stretch;padding:0 0 4px;margin:-2px 0 0;scrollbar-width:thin}' +
    '#enma .card{flex:0 0 128px;display:flex;flex-direction:column;background:var(--en-bg);border:1px solid var(--en-line);border-radius:14px;overflow:hidden;text-decoration:none;color:var(--en-ink);transition:border-color .2s,transform .2s}' +
    '#enma .card:hover{border-color:var(--en-gold);transform:translateY(-2px)}' +
    '#enma .card img{width:100%;height:104px;object-fit:contain;background:#fff;display:block}' +
    '#enma .card span{display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden;font-size:12px;line-height:1.35;padding:8px 9px 2px}' +
    '#enma .card b{font-weight:500;font-size:12px;color:var(--en-gold);padding:2px 9px 9px}' +
    '#enma .typing{display:inline-flex;gap:4px}#enma .typing i{width:6px;height:6px;border-radius:50%;background:var(--en-dim);animation:enb 1s infinite}#enma .typing i:nth-child(2){animation-delay:.15s}#enma .typing i:nth-child(3){animation-delay:.3s}' +
    '@keyframes enb{0%,80%,100%{opacity:.25}40%{opacity:1}}' +
    '#enma .chips{display:flex;flex-wrap:wrap;gap:6px;padding:0 16px 12px;background:var(--en-soft);margin:0}' +
    '#enma .chips button{border:1px solid var(--en-line);background:var(--en-bg);color:var(--en-ink);border-radius:100px;padding:7px 12px;font:400 12.5px "DM Sans",system-ui,sans-serif;cursor:pointer}' +
    '#enma .chips button:hover{border-color:var(--en-gold)}' +
    '#enma form{display:flex;gap:8px;padding:10px 12px;border-top:1px solid var(--en-line);background:var(--en-bg);margin:0}' +
    // the site styles inputs and textareas for its own forms; undo anything that could leak in
    '#enma textarea{flex:1;width:auto;min-width:0;min-height:0;height:auto;resize:none;background:var(--en-bg);color:var(--en-ink);border:1px solid var(--en-line);border-radius:18px;padding:10px 14px;font:14px/1.4 "DM Sans",system-ui,sans-serif;max-height:110px;outline:none;overflow-y:hidden;margin:0;box-shadow:none}' +
    '#enma textarea::placeholder{color:var(--en-dim)}#enma textarea:focus{border-color:var(--en-gold)}' +
    '#enma form button{border:0;border-radius:100px;background:var(--en-ink);color:var(--en-bg);padding:0 16px;font:500 10px "DM Sans",system-ui,sans-serif;letter-spacing:.18em;cursor:pointer;margin:0}' +
    '#enma form button:disabled{opacity:.45;cursor:default}' +
    '#enma .note{white-space:nowrap;overflow:hidden;text-overflow:ellipsis;font-size:11px;line-height:1.5;color:var(--en-dim);padding:0 14px 10px;background:var(--en-bg);margin:0}#enma .note a{color:inherit}' +
    '@media (max-width:600px){#enma-btn{width:48px;height:48px}#enma-btn .tip{display:none}' +
    '#enma{inset:0;right:0;bottom:0;width:auto;max-width:none;height:100%;height:100dvh;border-radius:0;transform:translateY(24px)}' +
    '#enma header{padding-top:calc(16px + env(safe-area-inset-top))}#enma .note{padding-bottom:calc(10px + env(safe-area-inset-bottom))}' +
    '#enma .m{max-width:90%}#enma textarea{font-size:16px}#enma header button.x{font-size:20px}}' +
    '@media (prefers-reduced-motion:reduce){#enma-btn,#enma{transition:none}}';

  var style = document.createElement('style'); style.textContent = css; document.head.appendChild(style);

  var btn = document.createElement('button');
  btn.id = 'enma-btn'; btn.type = 'button';
  btn.setAttribute('aria-label', 'Ask Enma, the Urban Nest assistant'); btn.title = 'Ask Enma';
  btn.innerHTML = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M20 11.5a7.5 7.5 0 0 1-10.9 6.7L4.5 19.5l1.2-4.3A7.5 7.5 0 1 1 20 11.5z"/><path d="M9 11.5h.01M12.5 11.5h.01M16 11.5h.01" stroke-width="2.2"/></svg><span class="tip">ASK ENMA</span>';

  var box = document.createElement('section');
  box.id = 'enma'; box.setAttribute('role', 'dialog'); box.setAttribute('aria-label', 'Enma, the Urban Nest assistant'); box.setAttribute('aria-hidden', 'true');
  box.innerHTML =
    '<header><div><b>Enma</b><small>URBAN NEST ASSISTANT</small></div>' +
    '<div><button type="button" class="new" title="Start a new chat">NEW CHAT</button><button type="button" class="x" aria-label="Close chat">&times;</button></div></header>' +
    '<div class="log" aria-live="polite"></div><div class="chips"></div>' +
    '<form><textarea rows="1" maxlength="1500" placeholder="Ask Enma anything" aria-label="Your message"></textarea><button type="submit">SEND</button></form>' +
    '<div class="note">AI assistant · chats are saved (<a href="/policies#privacy">privacy</a>) · <a href="https://wa.me/918588944583" target="_blank" rel="noopener">talk to a person</a></div>';
  document.body.appendChild(btn); document.body.appendChild(box);

  var log = box.querySelector('.log'), chips = box.querySelector('.chips');
  var form = box.querySelector('form'), input = box.querySelector('textarea'), send = form.querySelector('button');

  btn.addEventListener('click', open);
  box.querySelector('.x').addEventListener('click', close);
  box.querySelector('.new').addEventListener('click', function () { if (busy) return; state = { id: uuid(), msgs: [] }; save(); render(); });
  document.addEventListener('keydown', function (e) { if (e.key === 'Escape' && box.classList.contains('open')) close(); });
  document.querySelectorAll('[data-enma]').forEach(function (el) { el.addEventListener('click', function (e) { e.preventDefault(); open(); }); });
  input.addEventListener('input', grow);
  input.addEventListener('keydown', function (e) { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); form.requestSubmit ? form.requestSubmit() : submit(e); } });
  form.addEventListener('submit', submit);
  render();

  // ── one circle above the other ────────────────────────────────────────
  // Whatever the Join the Nest corner shows (its round button, or its open card), Enma's circle sits GAP above its top.
  function joinParts() { return ['jn2', 'jn2Dot', 'jn', 'jnDot'].map(function (id) { return document.getElementById(id); }).filter(Boolean); }
  function showing(el) {
    var cs = getComputedStyle(el), r = el.getBoundingClientRect();
    return cs.display !== 'none' && cs.visibility !== 'hidden' && parseFloat(cs.opacity) > 0.05 && r.height > 0 && r.top < innerHeight - 4 && r.right > innerWidth - 120;
  }
  function place() {
    var top = innerHeight - EDGE + GAP;                     // nothing there: Enma sits in the corner itself
    joinParts().forEach(function (el) { if (showing(el)) top = Math.min(top, el.getBoundingClientRect().top); });
    var b = Math.max(EDGE, Math.round(innerHeight - top + GAP));
    btn.style.bottom = 'calc(' + b + 'px + env(safe-area-inset-bottom))';
    if (!matchMedia('(max-width:600px)').matches) box.style.bottom = btn.style.bottom;
  }
  var following = 0;
  function follow() {                                      // the card glides in and out: keep pace for its animation
    var until = performance.now() + 700;
    if (following) return;
    following = 1;
    (function step() { place(); if (performance.now() < until) requestAnimationFrame(step); else following = 0; })();
  }
  var mo = new MutationObserver(function () {
    follow();
    var card = document.getElementById('jn2') || document.getElementById('jn');
    if (card && card.classList.contains('show') && box.classList.contains('open')) close();   // the card opened: fold the chat
  });
  function watch() { joinParts().forEach(function (el) { mo.observe(el, { attributes: true, attributeFilter: ['class', 'style', 'aria-hidden'] }); }); follow(); }
  addEventListener('resize', follow);
  if (document.readyState === 'complete') watch(); else addEventListener('load', watch);
  setTimeout(watch, 1500);                                 // join-nest.js is deferred: catch it if it arrived late

  function foldJoin() {
    var card = document.getElementById('jn2') || document.getElementById('jn');
    if (card && card.classList.contains('show')) { var x = document.getElementById('jn2X') || document.getElementById('jnX'); if (x) x.click(); }
  }
  function open() {
    foldJoin();
    place();
    box.classList.add('open'); box.setAttribute('aria-hidden', 'false'); btn.classList.add('hide');
    if (matchMedia('(max-width:600px)').matches) document.body.style.overflow = 'hidden';
    log.scrollTop = log.scrollHeight;
    if (!matchMedia('(pointer:coarse)').matches) setTimeout(function () { input.focus(); }, 200);
  }
  function close() {
    box.classList.remove('open'); box.setAttribute('aria-hidden', 'true'); btn.classList.remove('hide'); document.body.style.overflow = '';
    follow();
  }

  // ── the conversation ──────────────────────────────────────────────────
  function render() {
    log.innerHTML = '';
    bubble('a', GREETING);
    state.msgs.forEach(function (m) { bubble(m.r, m.t, m.err); if (m.c) cards(m.c); });
    chips.innerHTML = '';
    if (!state.msgs.length) CHIPS.forEach(function (c) {
      var b = document.createElement('button'); b.type = 'button'; b.textContent = c;
      b.addEventListener('click', function () {
        if (c === CHIPS[0]) { input.value = ''; input.placeholder = 'e.g. A calm bedroom, something for the wall'; input.focus(); return; }
        ask(c);
      });
      chips.appendChild(b);
    });
    log.scrollTop = log.scrollHeight;
  }
  function bubble(role, text, err) {
    var d = document.createElement('div'); d.className = 'm ' + role + (err ? ' err' : ''); d.innerHTML = format(text); log.appendChild(d); return d;
  }
  // The pieces Enma linked to, as a row of small picture cards under her message.
  function cards(list) {
    if (!Array.isArray(list) || !list.length) return;
    var row = document.createElement('div'); row.className = 'cards';
    list.forEach(function (p) {
      if (!p || !/^https:\/\/(www\.)?storeurbannest\.in\//.test(p.url || '')) return;
      var a = document.createElement('a'); a.className = 'card'; a.href = p.url;
      a.innerHTML = (p.img ? '<img alt="" src="' + esc(p.img) + '">' : '') + '<span>' + esc(p.name) + '</span>' + (p.price ? '<b>' + esc(p.price) + '</b>' : '');
      var im = a.querySelector('img'); if (im) im.addEventListener('load', function () { log.scrollTop = log.scrollHeight; });   // photos arrive after the scroll
      row.appendChild(a);
    });
    if (row.children.length) { log.appendChild(row); log.scrollTop = log.scrollHeight; }
  }
  // With cards under the message, the links in its text say the same thing twice: take them out and tidy what is left.
  function withoutLinks(text) {
    return text.replace(/\[([^\]\n]+)\]\((https?:\/\/[^)\s]+)\)/g, '$2')
      .replace(/https?:\/\/(www\.)?storeurbannest\.in\/(piece|collection|essentials)\/[^\s<)]*/g, '')
      .replace(/[ \t]*\|[ \t]*(\|[ \t]*)+/g, ' | ').replace(/[ \t]*[|–-][ \t]*(?=\n|$)/g, '').replace(/\([ \t]*\)/g, '').replace(/[ \t]+\n/g, '\n');
  }
  function esc(t) { return String(t == null ? '' : t).replace(/[&<>"']/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]; }); }
  var MARK = '\u001ePIECES';

  function submit(e) { if (e) e.preventDefault(); var t = input.value.trim(); if (t) ask(t); }
  function ask(text) {
    if (busy) return;
    busy = true; send.disabled = true; chips.innerHTML = ''; input.value = ''; grow();
    state.msgs.push({ r: 'u', t: text }); save();
    bubble('u', text);
    var out = bubble('a', ''); out.innerHTML = '<span class="typing"><i></i><i></i><i></i></span>';
    log.scrollTop = log.scrollHeight;
    var got = '';
    fetch('/api/chat', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ id: state.id, message: text, page: location.pathname }) })
      .then(function (res) {
        if (!res.ok) return res.json().catch(function () { return {}; }).then(function (j) { throw new Error(j.error || 'Something went wrong.'); });
        var reader = res.body.getReader(), dec = new TextDecoder();
        return (function pump() { return reader.read().then(function (r) { if (r.done) return; got += dec.decode(r.value, { stream: true }); out.innerHTML = format(got.split(MARK)[0]); log.scrollTop = log.scrollHeight; return pump(); }); })();
      })
      .then(function () {
        var parts = got.split(MARK), list = null;
        if (parts[1]) { try { list = JSON.parse(parts[1]); } catch (e) { list = null; } }
        var text = parts[0].trim() || 'Sorry, no answer came back. Please try again.';
        if (list && list.length) text = withoutLinks(text).trim();
        out.innerHTML = format(text);
        if (list) { cards(list); log.scrollTop = log.scrollHeight; }
        state.msgs.push(list ? { r: 'a', t: text, c: list } : { r: 'a', t: text }); save();
      })
      .catch(function (err) {
        var msg = (err && err.message && err.message !== 'Failed to fetch') ? err.message : 'Could not reach Enma. Please check your connection, or message us on WhatsApp: +91 85889 44583.';
        out.className = 'm a err'; out.innerHTML = format(msg); state.msgs.push({ r: 'a', t: msg, err: 1 }); save();
      })
      .then(function () { busy = false; send.disabled = false; if (!matchMedia('(pointer:coarse)').matches) input.focus(); });
  }
  // Links Enma writes: the site's own open here, anything else in a new tab; the phone number opens WhatsApp.
  function format(t) {
    var s = String(t).replace(/[&<>"']/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]; });
    s = s.replace(/\*\*(.+?)\*\*/g, '<b>$1</b>');
    s = s.replace(/\[([^\]\n]+)\]\((https?:\/\/[^)\s]+)\)/g, '$2');   // a stray [text](link) still becomes a clean link
    s = s.replace(/\b(https?:\/\/[^\s<]+[^\s<.,)!?])/g, function (u) {
      var own = /^https?:\/\/(www\.)?storeurbannest\.in/.test(u);
      var path = u.replace(/^https?:\/\/(www\.)?storeurbannest\.in/, '');
      // the site's own links read as short labels, not long addresses
      var label = !own ? u.replace(/^https?:\/\/(www\.)?/, '').replace(/\/$/, '')
        : /^\/piece\//.test(path) ? 'View the piece' : /^\/rooms\//.test(path) ? 'Step into the room' : /^\/edit\//.test(path) ? 'Read the article'
        : 'storeurbannest.in' + path.replace(/\/$/, '');
      return '<a href="' + u + '"' + (own ? '' : ' target="_blank" rel="noopener"') + '>' + label + '</a>';
    });
    s = s.replace(/\b(hello@storeurbannest\.in)\b/g, '<a href="mailto:$1">$1</a>');
    s = s.replace(/\+91[ -]?85889[ -]?44583/g, '<a href="https://wa.me/918588944583" target="_blank" rel="noopener">$&</a>');
    return s;
  }
  function grow() { input.style.height = 'auto'; input.style.height = Math.min(input.scrollHeight, 110) + 'px'; input.style.overflowY = input.scrollHeight > 110 ? 'auto' : 'hidden'; }
  function load() { try { var s = JSON.parse(localStorage.getItem(KEY)); return s && s.id && Array.isArray(s.msgs) ? s : null; } catch (e) { return null; } }
  function save() { try { localStorage.setItem(KEY, JSON.stringify({ id: state.id, msgs: state.msgs.slice(-60) })); } catch (e) {} }
  function uuid() {
    if (window.crypto && crypto.randomUUID) return crypto.randomUUID();
    var b = crypto.getRandomValues(new Uint8Array(16)); b[6] = (b[6] & 15) | 64; b[8] = (b[8] & 63) | 128;
    var h = Array.prototype.map.call(b, function (x) { return (x + 256).toString(16).slice(1); }).join('');
    return h.slice(0, 8) + '-' + h.slice(8, 12) + '-' + h.slice(12, 16) + '-' + h.slice(16, 20) + '-' + h.slice(20);
  }
})();
