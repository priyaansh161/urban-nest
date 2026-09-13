/* Share: one helper for every page that lets a visitor pass something on —
 * product cards, the piece sheet, the room drawers, Nest Edit articles.
 *
 *     UNShare.share({ title, text, url })
 *     UNShare.icon                          the arrow-out-of-a-tray glyph
 *
 * The phone's own share sheet where there is one (WhatsApp, Instagram…);
 * everywhere else the link is copied and a small "Link copied" pill says so.
 * The pill is made here rather than living in each page's markup, and styles
 * itself, so a page needs nothing but this script.
 */
(function () {
  var icon = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 3v13"/><path d="M7 8l5-5 5 5"/><path d="M5 13v6a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2v-6"/></svg>';

  function share(data) {
    if (navigator.share && (!navigator.canShare || navigator.canShare(data))) {
      navigator.share(data).catch(function (err) {
        // Closing the sheet is not a failure. Anything else, fall back.
        if (err && err.name !== 'AbortError') copy(data.url);
      });
    } else {
      copy(data.url);
    }
  }

  function copy(url) {
    var done = function () { toast('Link copied'); };
    var manual = function () { legacyCopy(url) ? done() : window.prompt('Copy this link', url); };
    if (navigator.clipboard && window.isSecureContext) navigator.clipboard.writeText(url).then(done, manual);
    else manual();
  }

  function legacyCopy(text) {
    var ta = document.createElement('textarea');
    ta.value = text; ta.setAttribute('readonly', '');
    ta.style.cssText = 'position:fixed;top:0;left:0;opacity:0;';
    document.body.appendChild(ta); ta.select();
    var ok = false;
    try { ok = document.execCommand('copy'); } catch (e) {}
    ta.remove();
    return ok;
  }

  var pill, timer;
  function toast(msg) {
    if (!pill) {
      var css = document.createElement('style');
      css.textContent =
        '.un-share-toast{position:fixed;left:50%;bottom:28px;z-index:10000;transform:translate(-50%,12px);opacity:0;' +
        'pointer-events:none;background:#0F1F22;color:#F5F7F6;border:.5px solid rgba(234,242,241,.18);' +
        "font:500 11px/1 'DM Sans',system-ui,sans-serif;letter-spacing:.14em;text-transform:uppercase;" +
        'padding:13px 22px;border-radius:100px;transition:opacity .3s,transform .3s;}' +
        '.un-share-toast.show{opacity:1;transform:translate(-50%,0);}';
      document.head.appendChild(css);
      pill = document.createElement('div');
      pill.className = 'un-share-toast';
      pill.setAttribute('role', 'status');
      pill.setAttribute('aria-live', 'polite');
      document.body.appendChild(pill);
    }
    pill.textContent = msg;
    requestAnimationFrame(function () { pill.classList.add('show'); });
    clearTimeout(timer);
    timer = setTimeout(function () { pill.classList.remove('show'); }, 2200);
  }

  window.UNShare = { share: share, icon: icon };
})();
