/* Registers sw.js, which is what lets a phone install Urban Nest as an app.
 * Loaded by every public page; the admin deliberately does not load it. */
/* A login invite or password-reset email from Supabase lands on the site's
 * address with its token after the #. Only the studio knows what to do with
 * it (set a password), so pass the whole link over. */
(function () {
  var h = location.hash || '';
  if (/(^#|&)(type=(invite|recovery)|error_code=)/.test(h) && location.pathname.indexOf('/studio/') !== 0) {
    location.replace('/studio/' + h);
  }
})();

if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/sw.js').catch(() => {});
  });
}
