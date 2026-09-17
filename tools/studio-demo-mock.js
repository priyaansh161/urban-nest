/* DEMO MODE for The Nest Studio — local preview only, never shipped.
 *
 *   npx serve .        then open  http://localhost:3000/studio/?demo
 *                      or the page:  http://localhost:3000/designer.html?d=aanya-kapoor&demo
 *
 * Replaces supabase-js with an in-memory stand-in, so the studio can be
 * clicked through before setup-contributors.sql has run and without a writer
 * account. Sign in with ANY email and password. Nothing reaches the real
 * database; changes live in this browser tab (sessionStorage) until it closes.
 * Add ?demo=reset to start again from the sample data.
 *
 * studio/index.html loads this only when the page is on localhost/127.0.0.1
 * AND the address has ?demo. tools/ is not in build-site.mjs's allow list,
 * so this file never reaches the live site anyway.
 */
(function () {
  const KEY = 'un-studio-demo';
  if (/demo=reset/.test(location.search)) sessionStorage.removeItem(KEY);

  const day = n => new Date(Date.now() - n * 86400000).toISOString();
  const img = name => location.origin + '/images/' + name;
  const SAMPLE = {
    session: null,
    seq: 100,
    tables: {
      contributors: [{
        id: 'demo-writer', email: 'writer@example.com', display_name: 'Aanya Kapoor', title: 'Interior Designer',
        city: 'New Delhi', bio: 'I design calm, lived-in homes for families who hate clutter.', avatar_url: null,
        instagram: '@aanyastudio', website: 'aanya.studio', active: true,
        slug: 'aanya-kapoor', services: 'Full home design, Styling & decor, Kitchens, Turnkey projects',
        about: 'I start every project in the room people actually live in, not the one they show guests.\n\nMost of my clients are young families in Delhi and Gurugram who want a home that feels calm without feeling bare: good light, honest materials, and a few pieces with a story.',
        whatsapp: '98765 43210', accepting_projects: true,
      }],
      portfolio_projects: [
        { id: 'proj-1', contributor_id: 'demo-writer', title: 'A calm family home in Vasant Kunj', kind: 'Full home', place: '3BHK · New Delhi', year: 2026,
          summary: 'A family of four wanted the living room back from the television.\n\nWe moved the seating to face the window, layered three kinds of warm light, and kept the palette to teal, oak and brass.',
          photos: [{ url: img('band-living.webp'), caption: 'The living room, facing the light' }, { url: img('det-chandelier2.webp'), caption: 'A brass pendant over the dining table' }, { url: img('band-warm.webp'), caption: '' }],
          published: true, sort_order: 0, created_at: day(30), updated_at: day(12) },
        { id: 'proj-2', contributor_id: 'demo-writer', title: 'A small kitchen that works hard', kind: 'Kitchen', place: '2BHK · Gurugram', year: 2025,
          summary: 'Nine square metres, two cooks, no clutter on the counter.',
          photos: [{ url: img('room-kitchen.webp'), caption: '' }, { url: img('det-knobs.webp'), caption: 'Knurled brass knobs' }],
          published: true, sort_order: 1, created_at: day(60), updated_at: day(50) },
        { id: 'proj-3', contributor_id: 'demo-writer', title: 'Guest bathroom refresh', kind: 'Bathroom', place: 'Noida', year: 2026,
          summary: null, photos: [{ url: img('room-bath.webp'), caption: '' }],
          published: false, sort_order: 2, created_at: day(3), updated_at: day(2) },
      ],
      designer_enquiries: [
        { id: 'enq-1', contributor_id: 'demo-writer', name: 'Rohan Mehta', phone: '+919811122233', email: 'rohan@example.com', city: 'Gurugram',
          project_kind: 'Full home', budget: '₹10–25 lakh', message: 'We move into a 3BHK in November and want the living room and both bedrooms done. Loved the Vasant Kunj project.',
          status: 'new', created_at: day(1) },
        { id: 'enq-2', contributor_id: 'demo-writer', name: 'Sneha Iyer', phone: null, email: 'sneha@example.com', city: 'New Delhi',
          project_kind: 'Styling & decor', budget: 'Not sure yet', message: 'Just the living room, it feels empty.',
          status: 'contacted', created_at: day(6) },
      ],
      nest_posts: [
        { id: 'demo-1', contributor_id: 'demo-writer', author: 'Aanya Kapoor', title: 'Five lamps that fix a flat room', category: 'tips',
          published: true, pinned: false, upvote_count: 14, read_time: '4 min read', image_url: null,
          excerpt: 'Most rooms feel flat because every light is on the ceiling.',
          content: '# Start low\n\nPut light **below** eye level first: a table lamp, a floor lamp.\n\n- One lamp per corner you sit in\n- Warm bulbs, never cool white\n- Shades that glow, not glare',
          created_at: day(9), updated_at: day(6) },
        { id: 'demo-2', contributor_id: 'demo-writer', author: 'Aanya Kapoor', title: 'The rug rule nobody tells you', category: 'trends',
          published: true, pinned: false, upvote_count: 6, read_time: '3 min read', image_url: null,
          excerpt: 'Too small is the most common mistake in Indian living rooms.',
          content: 'A rug should hold the **front legs** of every seat around it.\n\n## Measure first\n\nTape it out on the floor before you buy.',
          created_at: day(20), updated_at: day(18) },
        { id: 'demo-3', contributor_id: 'demo-writer', author: 'Aanya Kapoor', title: 'Monsoon-proofing a balcony garden', category: 'inspiration',
          published: false, pinned: false, upvote_count: 0, read_time: null, image_url: null, excerpt: null,
          content: 'Draft — still writing this one.', created_at: day(2), updated_at: day(1) },
      ],
    },
  };

  let state;
  try { state = JSON.parse(sessionStorage.getItem(KEY) || 'null'); } catch (e) {}
  state = state || JSON.parse(JSON.stringify(SAMPLE));
  const save = () => { try { sessionStorage.setItem(KEY, JSON.stringify(state)); } catch (e) {} };
  const me = () => state.session ? state.tables.contributors[0] : null;

  const RPC = {
    my_contributor_id: () => ({ data: me() ? me().id : null, error: null }),
    is_contributor:    () => ({ data: !!me(), error: null }),
    is_admin:          () => ({ data: false, error: null }),
    send_designer_enquiry: (a) => {
      const c = state.tables.contributors.find(x => x.slug === a.p_slug && x.active && x.accepting_projects);
      if (!c) return { data: null, error: { message: 'designer not taking enquiries' } };
      state.tables.designer_enquiries = state.tables.designer_enquiries || [];
      state.tables.designer_enquiries.unshift({ id: 'enq-' + (++state.seq), contributor_id: c.id, name: a.p_name, phone: a.p_phone || null,
        email: a.p_email || null, city: a.p_city || null, project_kind: a.p_kind || null, budget: a.p_budget || null,
        message: a.p_message || null, status: 'new', created_at: new Date().toISOString() });
      save();
      return { data: { ok: true }, error: null };
    },
  };

  function query(table) {
    const view = table === 'public_contributors';   // the view: contributors without email
    if (view) table = 'contributors';
    const q = { op: 'select', filters: [], payload: null, single: false, order: null };
    const api = {
      select() { return api; },
      eq(c, v) { q.filters.push(r => r[c] === v); return api; },
      in(c, a) { q.filters.push(r => a.includes(r[c])); return api; },
      not(c) { q.filters.push(r => r[c] != null); return api; },
      order(c, o) { q.order = [c, !!(o && o.ascending === false)]; return api; },
      limit() { return api; },
      single() { q.single = true; return api; },
      insert(p) { q.op = 'insert'; q.payload = p; return api; },
      update(p) { q.op = 'update'; q.payload = p; return api; },
      delete() { q.op = 'delete'; return api; },
      then(ok, bad) { return Promise.resolve().then(run).then(ok, bad); },
    };
    function run() {
      const rows = state.tables[table] = state.tables[table] || [];
      const match = r => q.filters.every(f => f(r));
      let out;
      if (q.op === 'insert') {
        const row = Object.assign({ id: 'demo-' + (++state.seq), created_at: new Date().toISOString(), upvote_count: 0, pinned: false }, q.payload);
        if (table === 'nest_posts' && me()) { row.contributor_id = me().id; row.author = me().display_name; }
        rows.push(row); out = [row];
      } else if (q.op === 'update') {
        out = rows.filter(match); out.forEach(r => Object.assign(r, q.payload));
      } else if (q.op === 'delete') {
        out = rows.filter(match); state.tables[table] = rows.filter(r => !match(r));
      } else {
        out = rows.filter(match);
        if (q.order) { const [c, desc] = q.order; out = out.slice().sort((a, b) => (a[c] > b[c] ? 1 : a[c] < b[c] ? -1 : 0) * (desc ? -1 : 1)); }
      }
      save();
      out = JSON.parse(JSON.stringify(out));
      if (view) out = out.filter(r => r.active).map(({ email, ...r }) => r);
      return { data: q.single ? (out[0] || null) : out, error: null };
    }
    return api;
  }

  window.supabase = {
    createClient() {
      return {
        auth: {
          async getSession() { return { data: { session: state.session } }; },
          async signInWithPassword({ email }) { state.session = { user: { email: email || 'writer@example.com' } }; save(); return { data: {}, error: null }; },
          async signOut() { state.session = null; save(); return { error: null }; },
          async updateUser() { return { data: {}, error: null }; },
          async resetPasswordForEmail() { return { error: null }; },
          onAuthStateChange() { return { data: { subscription: { unsubscribe() {} } } }; },
        },
        from: query,
        async rpc(name, args) { return RPC[name] ? RPC[name](args || {}) : { data: null, error: null }; },
        storage: { from() { return {
          async upload() { return { error: null }; },
          getPublicUrl() { return { data: { publicUrl: '/images/app-icon-512.png' } }; },
        }; } },
      };
    },
  };

  // A ribbon, so the demo can never be mistaken for the real thing.
  document.addEventListener('DOMContentLoaded', () => {
    const r = document.createElement('div');
    r.textContent = 'DEMO — sample data, nothing is saved to Urban Nest';
    r.style.cssText = 'position:fixed;bottom:0;left:0;right:0;z-index:999;background:#A37B3F;color:#fff;font:500 11px/1 "DM Sans",sans-serif;letter-spacing:.14em;text-transform:uppercase;text-align:center;padding:7px 10px;pointer-events:none';
    document.body.appendChild(r);
  });
})();
