// Shared Supabase client + auth helpers for all admin pages
const { createClient } = supabase;
const db = createClient(SUPABASE_URL, SUPABASE_ANON_KEY);

/* ── SESSION LIFETIME ────────────────────────────────────────────────
   Supabase keeps a session alive indefinitely by refreshing it in the
   background, so once you sign in on a machine the admin stays open on
   it forever — you never get asked for the password again. Expire the
   session ourselves so returning to the admin means signing in.        */
const IDLE_LIMIT_MS  = 60 * 60 * 1000;       // signed out after 1h idle
const SESSION_MAX_MS = 12 * 60 * 60 * 1000;  // and after 12h regardless

const LAST_SEEN_KEY = 'un-admin-last-seen';
const STARTED_KEY   = 'un-admin-started';

/* ── UI GATE ─────────────────────────────────────────────────────────
   requireAuth() runs after the page has already been parsed, so without
   this the dashboard paints for a moment before redirecting — a signed
   out visitor gets a look at the admin. Hide the page up front and only
   reveal it once a session is confirmed. Failure never reveals.        */
(function gateAdminUI() {
  if (document.getElementById('auth-gate')) return;
  const style = document.createElement('style');
  style.id = 'auth-gate';
  style.textContent = 'body{visibility:hidden !important}';
  (document.head || document.documentElement).appendChild(style);
})();

function revealAdminUI() {
  const gate = document.getElementById('auth-gate');
  if (gate) gate.remove();
}

function markActivity() {
  try { localStorage.setItem(LAST_SEEN_KEY, String(Date.now())); } catch (e) {}
}

// Returns 'idle' | 'max' | null
function expiryReason() {
  let last, started;
  try {
    last    = parseInt(localStorage.getItem(LAST_SEEN_KEY) || '0', 10);
    started = parseInt(localStorage.getItem(STARTED_KEY) || '0', 10);
  } catch (e) { return null; }
  const now = Date.now();
  if (last && now - last > IDLE_LIMIT_MS) return 'idle';
  if (started && now - started > SESSION_MAX_MS) return 'max';
  return null;
}

async function endSession(reason) {
  try {
    localStorage.removeItem(LAST_SEEN_KEY);
    localStorage.removeItem(STARTED_KEY);
  } catch (e) {}
  try { await db.auth.signOut(); } catch (e) {}
  window.location.href = 'login.html' + (reason ? '?ended=' + reason : '');
}

async function requireAuth() {
  let session = null;
  try {
    ({ data: { session } } = await db.auth.getSession());
  } catch (e) {
    session = null;               // treat any failure as signed out
  }
  if (!session) { window.location.href = 'login.html'; return null; }

  const reason = expiryReason();
  if (reason) { await endSession(reason); return null; }

  // First admin page after signing in starts the clock.
  try {
    if (!localStorage.getItem(STARTED_KEY)) localStorage.setItem(STARTED_KEY, String(Date.now()));
  } catch (e) {}
  markActivity();

  // Keep the idle timer honest while the tab is open, and act on expiry
  // even if the person never touches the page again.
  ['pointerdown', 'keydown', 'scroll'].forEach(evt =>
    window.addEventListener(evt, markActivity, { passive: true }));
  setInterval(() => {
    const r = expiryReason();
    if (r) endSession(r);
  }, 60 * 1000);

  revealAdminUI();
  return session;
}

async function adminSignOut() {
  await endSession(null);
}

function showToast(msg, type = 'success') {
  const t = document.createElement('div');
  t.className = 'toast toast-' + type;
  t.textContent = msg;
  document.body.appendChild(t);
  requestAnimationFrame(() => t.classList.add('show'));
  setTimeout(() => { t.classList.remove('show'); setTimeout(() => t.remove(), 300); }, 3000);
}
