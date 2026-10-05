const SUPABASE_URL      = 'https://ifwxgwvsyispkaxzbstg.supabase.co';
const SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imlmd3hnd3ZzeWlzcGtheHpic3RnIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODI3MjI3ODQsImV4cCI6MjA5ODI5ODc4NH0.goQIrgT8-tSbN7nIEvHGifKjczi0JhgY01FVu_lQc4c';

const { createClient } = supabase;
const db = createClient(SUPABASE_URL, SUPABASE_ANON_KEY);

/* Photos uploaded through the admin are stored at full size — some are
   5 MB — and showing them as-is made the Nest Edit page alone 12.6 MB.
   unImg(url, width) asks Supabase for a copy at about the width it is shown
   (doubled for sharp phone screens; WebP when the browser takes it).
   Anything that is not one of our public-storage photos comes back as is. */
function unImg(url, width) {
  if (!url || typeof url !== 'string') return url;
  var STORED = SUPABASE_URL + '/storage/v1/object/public/';
  if (url.indexOf(STORED) !== 0 || /\.(gif|svg)(\?|$)/i.test(url)) return url;
  var w = Math.min(2000, Math.round((width || 800) * Math.min(window.devicePixelRatio || 1, 2)));
  // resize=contain keeps the whole photo: with a width alone Supabase keeps the
  // original height and crops the sides to a sliver.
  return url.replace('/storage/v1/object/public/', '/storage/v1/render/image/public/') +
    (url.indexOf('?') < 0 ? '?' : '&') + 'width=' + w + '&resize=contain&quality=75';
}
