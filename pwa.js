/* Registers sw.js, which is what lets a phone install Urban Nest as an app.
 * Loaded by every public page; the admin deliberately does not load it. */
if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/sw.js').catch(() => {});
  });
}
