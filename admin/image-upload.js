/* Shared image uploader for every admin page.
 *
 * WHY THIS IS ITS OWN FILE: the same control is wanted on the piece
 * photograph, both category photographs, the Nest post cover and the
 * Spline scene cover. Pasted into five places it would drift, the way
 * the top bar drifted into three different heights before it was
 * shared. One copy, loaded like auth.js.
 *
 * WHAT IT REPLACES: download the photograph, open the Supabase
 * dashboard, upload, copy the public URL, paste it back into the form.
 * Now: choose a file.
 *
 * IT SHRINKS ON THE WAY UP. The category tiles in this project are
 * 5600x5600 and up to 3.4 MB apiece, rendered into a 374px box — the
 * heaviest thing about the site. Everything through here is capped at
 * 1600px on its long edge and re-encoded as WebP, so a camera original
 * lands at a couple of hundred KB.
 *
 * HOW TO ADD A FIELD: give the URL input an id, put a button and a
 * hidden file input beside it, and tell the file input where to put
 * things:
 *
 *   <div class="field-row">
 *     <input type="url" id="postImage"/>
 *     <button type="button" id="postImageBtn"
 *             onclick="document.getElementById('postImageFile').click()">Upload</button>
 *   </div>
 *   <input type="file" id="postImageFile" accept="image/*" style="display:none"
 *          data-target="postImage" data-btn="postImageBtn"
 *          data-hint="postImageHint" data-name="postTitle"
 *          onchange="uploadImage(this)"/>
 *   <span class="hint" id="postImageHint">…</span>
 *
 * data-name is optional and only decides what the uploaded file is
 * called. It needs `db` and showToast from auth.js, so load it after.
 */

const IMG_BUCKET = 'Blog Images';   // the bucket the photographs already live in
const IMG_MAX    = 1600;            // px on the long edge

function imgSlugify(s) {
  return String(s || '').toLowerCase().trim()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '')
    .slice(0, 60);
}

/* Draws the file into a canvas no larger than IMG_MAX on its long edge
   and re-encodes it. A browser with no WebP encoder returns null from
   toBlob; the original then goes up unchanged rather than the upload
   failing outright. */
function shrinkImage(file) {
  return new Promise(function (resolve, reject) {
    const url = URL.createObjectURL(file);
    const img = new Image();
    img.onload = function () {
      URL.revokeObjectURL(url);
      const scale = Math.min(1, IMG_MAX / Math.max(img.width, img.height));
      const w = Math.round(img.width * scale), h = Math.round(img.height * scale);
      const c = document.createElement('canvas');
      c.width = w; c.height = h;
      c.getContext('2d').drawImage(img, 0, 0, w, h);
      c.toBlob(function (blob) {
        resolve(blob
          ? { blob: blob, w: w, h: h, type: 'image/webp', ext: 'webp' }
          : { blob: file, w: img.width, h: img.height, type: file.type,
              ext: (file.name.split('.').pop() || 'jpg') });
      }, 'image/webp', 0.82);
    };
    img.onerror = function () { URL.revokeObjectURL(url); reject(new Error('That file could not be read as an image')); };
    img.src = url;
  });
}

/* Says which bucket refused and which script fixes it. The first version
   of this named the models bucket whatever had actually failed, which
   sent me looking in the wrong place entirely. */
function imgStorageError(error) {
  const m = (error && error.message) || '';
  const fix = 'run admin/setup-image-storage.sql';
  if (/bucket not found/i.test(m))          return 'No "' + IMG_BUCKET + '" bucket — create it in Supabase → Storage, then ' + fix;
  if (/row-level security|policy/i.test(m)) return 'The ' + IMG_BUCKET + ' bucket is refusing uploads — ' + fix;
  if (/payload too large|exceeded|size/i.test(m)) return 'Rejected as too large for the ' + IMG_BUCKET + ' bucket';
  if (/mime|content type/i.test(m))         return 'The ' + IMG_BUCKET + ' bucket is refusing this file type — ' + fix;
  return 'Upload failed: ' + (m || 'unknown error');
}

async function uploadImage(input) {
  const file = input.files && input.files[0];
  input.value = '';                  // so picking the same file twice still fires
  if (!file) return;

  const d = input.dataset;
  const target = document.getElementById(d.target || '');
  const btn    = document.getElementById(d.btn    || '');
  const hint   = document.getElementById(d.hint   || '');
  if (!target || !btn) {
    (window.showToast || alert)('That upload button is not wired up', 'error');
    return;
  }

  const hintWas = hint ? hint.textContent : '';
  const label = btn.textContent;
  btn.disabled = true; btn.textContent = 'Uploading…';

  let shrunk;
  try { shrunk = await shrinkImage(file); }
  catch (e) {
    btn.disabled = false; btn.textContent = label;
    (window.showToast || alert)(e.message, 'error');
    return;
  }

  const beforeKb = Math.round(file.size / 1024);
  const afterKb  = Math.round(shrunk.blob.size / 1024);
  if (hint) hint.textContent = 'Uploading — ' + beforeKb + ' KB down to ' + afterKb + ' KB at ' + shrunk.w + '×' + shrunk.h + '.';

  // Named after whatever the form is called, so the bucket stays readable.
  const nameField = d.name ? document.getElementById(d.name) : null;
  const base = imgSlugify(nameField && nameField.value)
            || imgSlugify(file.name.replace(/\.[^.]+$/, ''))
            || 'image';
  const path = base + '-' + Date.now().toString(36) + '.' + shrunk.ext;

  /* Re-wrapped in a Blob that declares its own type: supabase-js puts a
     File into a FormData part and only applies contentType on the raw-body
     path, so the bucket would otherwise see whatever the browser guessed
     from the extension. */
  const body = new Blob([shrunk.blob], { type: shrunk.type });
  const { error } = await db.storage.from(IMG_BUCKET).upload(path, body, {
    contentType: shrunk.type, cacheControl: '31536000', upsert: false,
  });

  btn.disabled = false; btn.textContent = label;

  if (error) {
    if (hint) hint.textContent = hintWas;
    (window.showToast || alert)(imgStorageError(error), 'error');
    return;
  }

  const { data } = db.storage.from(IMG_BUCKET).getPublicUrl(path);
  target.value = data.publicUrl;
  target.dispatchEvent(new Event('input', { bubbles: true }));   // for anything watching the field
  if (hint) hint.textContent = 'Uploaded — ' + afterKb + ' KB at ' + shrunk.w + '×' + shrunk.h + '. The URL is in the field above.';
  (window.showToast || function () {})('Photograph uploaded');
}
