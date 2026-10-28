/* The public address of every article and piece, in one place.
 *
 * Read by the pages (to put a real link on each card, for search engines
 * and for ctrl-click) and by the server functions in functions/ (which
 * build the page at that address). Both must agree, so neither writes its
 * own copy of these rules.
 *
 *   /edit/<slug>                   a Nest Edit article
 *   /piece/<name-words>-<id8>      a piece; the first 8 characters of its id
 *                                  find it, the words are for people and
 *                                  Google, so a renamed piece keeps working
 *   /collection/<slug>, /essentials/<slug>   a category
 */
(function () {
  var slugify = function (s) {
    return String(s || '').toLowerCase().normalize('NFKD').replace(/[̀-ͯ]/g, '')
      .replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, '');
  };
  var UNUrls = {
    slugify: slugify,
    post: function (p) { return '/edit/' + (p.slug || p.id); },
    // The words before any "|" (the use, in our long-form names), at most eight of them.
    piece: function (it) {
      var words = slugify(String(it.name || 'piece').split('|')[0]).split('-').filter(Boolean).slice(0, 8).join('-');
      return '/piece/' + (words || 'piece') + '-' + String(it.id).slice(0, 8);
    },
    category: function (c) { return '/' + (c.section === 'essentials' ? 'essentials' : 'collection') + '/' + c.slug; },
  };
  globalThis.UNUrls = UNUrls;
})();
