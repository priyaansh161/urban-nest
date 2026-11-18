// Enma, the Urban Nest assistant: POST /api/chat (18 Nov 2026, adapted from the Motif Labs worker).
//
//   POST /api/chat   { id, message, page }  ->  streamed plain-text reply
//
// The conversation lives in Supabase (table urbannest_chats, see admin/setup-urbannest-chats.sql), so the browser only
// sends the new message. Every message gets the pieces and Nest Edit articles that match the conversation, read live
// from the database, so new listings are known at once and nothing is written into the prompt by hand. After each
// reply a second call rewrites the short note the admin shows under "Enma Chats".
//
// The model: Cloudflare Workers AI (free plan, 10,000 neurons a day; the AI binding is in wrangler.toml). Over the
// allowance the visitor gets an apology and WhatsApp; nothing is ever charged.
// Settings (already in the Pages dashboard for the other functions): SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY; optional
// IP_SALT. MOCK_LLM=1 answers without a model (local testing); with no Supabase vars chats are kept in memory.
import { SYSTEM_PROMPT, SUMMARY_PROMPT, SUMMARY_SCHEMA } from './_enma-knowledge.js';
import { sb, img, shortName } from '../_seo.js';            // the public read-only key the site's own pages use: published pieces and articles only

const UNUrls = globalThis.UNUrls;            // set by urls.js, which _seo.js loads
const ORIGIN = 'https://storeurbannest.in';
const CF_MODEL = '@cf/qwen/qwen3-30b-a3b-fp8';
const MAX_TURNS = 30;            // visitor messages per conversation
const MAX_CHARS = 1500;          // per visitor message
const NEW_CHATS_PER_IP_HOUR = 8; // fresh conversations per visitor per hour
const UUID = /^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;
const WA = 'WhatsApp: +91 85889 44583';

const allowed = (origin, env) => origin === ORIGIN || origin === 'https://www.storeurbannest.in'
  || /^https:\/\/[a-z0-9-]+\.storeurbannest\.pages\.dev$/.test(origin) || (env.LOCAL_DEV === '1');

export async function onRequestPost(ctx) {
  try { return await handleChat(ctx); }
  catch (err) { console.error('chat failed', err); return json({ error: 'Something went wrong. Please try ' + WA + '.' }, 500); }
}
export const onRequest = () => json({ error: 'POST only' }, 405);

async function handleChat({ request, env, waitUntil }) {
  const origin = request.headers.get('Origin') || '';
  if (!allowed(origin, env)) { console.log('chat origin refused:', origin); return json({ error: 'Not allowed' }, 403); }

  let body;
  try { body = await request.json(); } catch { return json({ error: 'Bad request' }, 400); }
  const id = String(body.id || '');
  const message = String(body.message || '').trim().slice(0, MAX_CHARS);
  if (!UUID.test(id) || !message) return json({ error: 'Bad request' }, 400);

  let store = makeStore(env);
  const ipHash = await hashIp(request.headers.get('CF-Connecting-IP') || 'local', env.IP_SALT || 'urban-nest-enma');
  let chat;
  try { chat = await store.get(id); }
  catch (err) {                         // no urbannest_chats table yet (or Supabase down): answer anyway, keep the chat in memory
    console.error('chat store unavailable, not saving', err.message); store = memoryStore(); chat = await store.get(id);
  }
  if (!chat) {
    if (env.LOCAL_DEV !== '1' && (await store.recentFromIp(ipHash)) >= NEW_CHATS_PER_IP_HOUR)
      return json({ error: 'Too many chats from this connection. Please message us on ' + WA + '.' }, 429);
    chat = { id, messages: [], turns: 0, page: String(body.page || '').slice(0, 200), ip_hash: ipHash };
  }
  if (chat.turns >= MAX_TURNS)
    return json({ error: 'This chat has reached its limit. Please continue on ' + WA + ', or email hello@storeurbannest.in.' }, 429);

  chat.messages.push({ role: 'user', content: message, at: new Date().toISOString() });
  chat.turns += 1;

  const history = chat.messages.map(m => ({ role: m.role, content: m.content }));
  const live = await liveContext(env, chat.messages, chat.page);
  const system = SYSTEM_PROMPT + '\n\n' + live;
  const given = /^LIVE LISTS: unavailable/.test(live) ? 'unavailable' : String((live.match(/storeurbannest\.in\/piece\//g) || []).length);
  if (env.LOCAL_DEV === '1') console.log('ENMA CONTEXT\n' + system.slice(SYSTEM_PROMPT.length, SYSTEM_PROMPT.length + 2500));
  const encoder = new TextEncoder();
  const { readable, writable } = new TransformStream();
  const writer = writable.getWriter();

  const work = (async () => {
    let reply = '';
    try {
      for await (const piece of replyStream(env, system, history)) { reply += piece; await writer.write(encoder.encode(piece)); }
    } catch (err) {
      console.error('model call failed', err);
      const sorry = '\n\nSorry, I could not answer just now. You can reach the team on ' + WA + '.';
      reply += sorry; await writer.write(encoder.encode(sorry)).catch(() => {});
    }
    // Picture cards (18 Nov 2026): the pieces Enma linked to go after the text, behind a marker the bubble splits off,
    // as small cards (photo, name, price), so a visitor choosing between similar names can see them. Up to 4.
    try {
      const cards = await piecesIn(reply);
      if (cards.length) await writer.write(encoder.encode(CARD_MARK + JSON.stringify(cards)));
    } catch (err) { console.error('cards failed', err); }
    await writer.close().catch(() => {});
    chat.messages.push({ role: 'assistant', content: reply.trim(), at: new Date().toISOString() });
    await store.save(chat);
    try { const note = await summarise(env, chat.messages); if (note) await store.saveSummary(id, note); }
    catch (err) { console.error('summary failed', err); }
  })();
  waitUntil(work);

  // X-Enma-Pieces: how many matching pieces Enma was given for this answer ("unavailable": the catalogue could not be read)
  return new Response(readable, { headers: { 'Content-Type': 'text/plain; charset=utf-8', 'Cache-Control': 'no-store', 'X-Content-Type-Options': 'nosniff', 'X-Enma-Pieces': given } });
}

// ── the live catalogue and articles, matched to the conversation ────────
// The whole catalogue (~190 pieces) in every prompt would use most of the free daily allowance on reading it, so each
// message gets only the pieces whose name or category share words with what the visitor said lately (plus the page
// they are on), up to 12, and the categories as a map. Read once per worker for 10 minutes.
let cache = null;
async function catalogue(env) {
  if (cache && Date.now() - cache.at < 600e3) return cache;
  const q = (path) => sb(path);
  const [items, cats, posts] = await Promise.all([
    q('collection_items?select=id,name,price,category,section,buy_link,amazon_status,image_url&published=eq.true'),
    q('collection_categories?select=slug,name,section&published=eq.true'),
    q('nest_posts?select=slug,title,category,excerpt,tags&published=eq.true&order=created_at.desc'),
  ]);
  cache = { at: Date.now(), items: Array.isArray(items) ? items : [], cats: Array.isArray(cats) ? cats : [], posts: Array.isArray(posts) ? posts : [] };
  return cache;
}

// The pieces a reply links to, in the order it names them, as cards for the bubble.
const CARD_MARK = '\u001ePIECES';
async function piecesIn(reply) {
  const slugs = [...new Set((reply.match(/\/piece\/[a-z0-9-]+/gi) || []).map(s => s.toLowerCase()))].slice(0, 4);
  if (!slugs.length || !cache) return [];
  const byUrl = new Map(cache.items.map(it => [UNUrls.piece(it).toLowerCase(), it]));
  return slugs.map(s => byUrl.get(s)).filter(Boolean).map(it => ({
    name: shortName(it.name), price: it.price || '', url: ORIGIN + UNUrls.piece(it), img: img(it.image_url, 320),
  }));
}

const STOP = new Set('a an and are as at be but by can do for from have how i in is it me my of on or our please show the this to want what with you your any some something need looking find get buy like love room home hai ka ki ke ko mein mujhe chahiye kya'.split(' '));
const words = (s) => String(s || '').toLowerCase().normalize('NFKD').replace(/[^a-z0-9\s-]/g, ' ').split(/[\s-]+/).filter(w => w.length > 2 && !STOP.has(w)).map(stem);
// plural and singular meet: vases/vase -> vas, lamps -> lamp, dishes -> dish, shelves -> shelf (18 Nov 2026: "vases" used to
// become "vas" while "vase" stayed "vase", so a plural question matched nothing and Enma made pieces up)
function stem(w) { return w.replace(/ies$/, 'y').replace(/ves$/, 'f').replace(/s$/, '').replace(/e$/, ''); }
// the everyday words for each category ("Amphorae" never says vase, "Luminaires" never says lamp)
const CAT_WORDS = {
  amphorae: 'vase vases planter pot flower', luminaires: 'lamp lamps light table lamp floor lamp', lighting: 'light lights chandelier pendant ceiling lamp',
  timepieces: 'clock clocks watch wall clock', 'wall-art': 'wall art painting paintings canvas frame print', sculptures: 'sculpture statue idol murti figurine showpiece',
  furniture: 'furniture table side table shelf stool ottoman', sofas: 'sofa couch seating', festive: 'festive diwali puja decor gift',
  'bath-essentials': 'bathroom bath soap dispenser towel mat', 'kitchen-essentials': 'kitchen jar storage serving', bedroom: 'bedroom bed bedside',
};

// six Collection pieces spread across the catalogue, for when nothing matches (so Enma has real pieces, not invented ones)
const ideas = (items) => { const c = items.filter(it => it.section === 'collection'); const step = Math.max(1, Math.floor(c.length / 6)); return c.filter((_, i) => i % step === 0).slice(0, 6); };

export async function liveContext(env, messages, page) {   // exported for tools/test-enma.mjs
  let data;
  try { data = await catalogue(env); } catch (err) { console.error('catalogue failed', err); return 'LIVE LISTS: unavailable right now. Do not name specific pieces; point to the Collection and Essentials pages.'; }
  const catName = Object.fromEntries(data.cats.map(c => [c.slug, c.name]));
  const recent = messages.filter(m => m.role === 'user').slice(-3).map(m => m.content).join(' ') + ' ' + String(page || '').replace(/[\/._-]/g, ' ');
  const want = new Set(words(recent));
  const score = (text) => { let s = 0; for (const w of words(text)) if (want.has(w)) s++; return s; };
  const ranked = data.items
    .map(it => ({ it, s: score(it.name) * 2 + score((catName[it.category] || it.category) + ' ' + (CAT_WORDS[it.category] || '')) }))
    .filter(x => x.s > 0).sort((a, b) => b.s - a.s);
  const top = ranked.length ? ranked[0].s : 0;            // weak matches (a shared word or two) are dropped when strong ones exist
  const items = ranked.filter(x => x.s >= top / 2).slice(0, 12).map(x => x.it);
  const line = (it) => {
    const buy = it.buy_link && !/^TODO-/i.test(it.buy_link) && it.amazon_status !== 'gone' ? 'buy on Amazon' : 'no Amazon link: team can help';
    return `- ${shortName(it.name)} | ${it.price || 'price not listed'} | ${it.section === 'essentials' ? 'Essentials' : 'Collection'} > ${catName[it.category] || it.category} | ${ORIGIN}${UNUrls.piece(it)} | ${buy}`;
  };
  const posts = data.posts.map(p => ({ p, s: score(p.title) * 2 + score(p.category + ' ' + [].concat(p.tags || []).join(' ') + ' ' + p.excerpt) }))
    .sort((a, b) => b.s - a.s).slice(0, 5).map(x => x.p);
  const catsBySection = (sec) => data.cats.filter(c => c.section === sec).map(c => `${c.name} (${ORIGIN}/${sec}/${c.slug})`).join('; ');
  return [
    `LIVE LISTS (${data.items.length} pieces on the site right now)`,
    `Collection categories: ${catsBySection('collection')}`,
    `Essentials categories: ${catsBySection('essentials')}`,
    items.length ? 'Pieces that match this conversation, best match first:\n' + items.map(line).join('\n')
      : 'No piece matches the words used so far. Do NOT name or invent any piece. Ask what they are looking for (room, mood, budget), or point to a category or a room. If they want ideas, here are a few real statement pieces from the Collection:\n' + ideas(data.items).map(line).join('\n'),
    'Nest Edit articles:\n' + posts.map(p => `- ${p.title} | ${p.category || 'The Nest Edit'} | ${ORIGIN}${UNUrls.post(p)}`).join('\n'),
  ].join('\n\n');
}

// ── model calls (Cloudflare Workers AI, Qwen 3) ─────────────────────────
const NO_THINK = '\n\n/no_think';
async function* replyStream(env, system, messages) {
  if (env.MOCK_LLM === '1') { yield* mockReply(messages); return; }
  const stream = await env.AI.run(env.CF_MODEL || CF_MODEL, { messages: [{ role: 'system', content: system + NO_THINK }, ...messages], stream: true, max_tokens: 700, temperature: 0.4 });
  const reader = stream.getReader(), dec = new TextDecoder();
  let buf = '', inThink = false, pending = '', started = false;
  for (;;) {
    const { done, value } = await reader.read();
    if (done) break;
    buf += dec.decode(value, { stream: true });
    let nl;
    while ((nl = buf.indexOf('\n')) >= 0) {
      const line = buf.slice(0, nl).trim(); buf = buf.slice(nl + 1);
      if (!line.startsWith('data:')) continue;
      const data = line.slice(5).trim();
      if (!data || data === '[DONE]') continue;
      let j; try { j = JSON.parse(data); } catch { continue; }
      let raw = j.response;                                     // a token "0" can arrive as the number 0: keep it
      if (raw == null || raw === '') raw = j.choices?.[0]?.delta?.content;
      const piece = raw == null ? '' : String(raw);
      if (piece === '') continue;
      pending += piece;                                         // drop <think>…</think>, even split across chunks
      let out = '';
      for (;;) {
        if (inThink) { const e = pending.indexOf('</think>'); if (e < 0) { pending = pending.slice(-8); break; } pending = pending.slice(e + 8); inThink = false; }
        else {
          const s = pending.indexOf('<think>');
          if (s >= 0) { out += pending.slice(0, s); pending = pending.slice(s + 7); inThink = true; continue; }
          const keep = partialTag(pending); out += pending.slice(0, pending.length - keep); pending = pending.slice(pending.length - keep); break;
        }
      }
      if (!started) out = out.replace(/^\s+/, '');
      if (out) { started = true; yield out; }
    }
  }
  if (!inThink && pending.trim()) { started = true; yield pending; }
  if (started) return;
  const again = await env.AI.run(env.CF_MODEL || CF_MODEL, { messages: [{ role: 'system', content: system + NO_THINK }, ...messages], max_tokens: 1200, temperature: 0.4 });
  const text = String(again.response ?? again.choices?.[0]?.message?.content ?? '').replace(/<think>[\s\S]*?(<\/think>|$)/g, '').trim();
  yield text || 'Sorry, I could not answer that just now. Could you ask again, or message the team on ' + WA + '?';
}
function partialTag(s) { for (let k = Math.min(6, s.length); k > 0; k--) if ('<think>'.startsWith(s.slice(-k))) return k; return 0; }

async function summarise(env, messages) {
  if (env.MOCK_LLM === '1') return null;
  const transcript = messages.map(m => `${m.role === 'user' ? 'VISITOR' : 'ENMA'}: ${m.content}`).join('\n\n');
  const res = await env.AI.run(env.CF_MODEL || CF_MODEL, {
    messages: [
      { role: 'system', content: SUMMARY_PROMPT + '\n\nReply with only one JSON object with exactly these keys: ' + SUMMARY_SCHEMA.required.join(', ') + '. "questions" is an array of strings; every other value is a string.' + NO_THINK },
      { role: 'user', content: `<chat>\n${transcript}\n</chat>` },
    ],
    max_tokens: 900, temperature: 0.1,
  });
  const text = typeof res.response === 'string' ? res.response : (res.choices?.[0]?.message?.content ?? (typeof res.response === 'object' ? JSON.stringify(res.response) : ''));
  return cleanNote(text);
}

// Only the known fields, as the right types; anything else is dropped.
function cleanNote(text) {
  const m = String(text || '').replace(/<think>[\s\S]*?<\/think>/g, '').match(/\{[\s\S]*\}/);
  if (!m) return null;
  let raw; try { raw = JSON.parse(m[0]); } catch { return null; }
  const note = {};
  for (const k of SUMMARY_SCHEMA.required) {
    if (k === 'questions') note.questions = Array.isArray(raw.questions) ? raw.questions.filter(q => typeof q === 'string').slice(0, 12).map(q => q.slice(0, 300)) : [];
    else note[k] = typeof raw[k] === 'string' ? raw[k].slice(0, 2000) : '';
  }
  if (!SUMMARY_SCHEMA.properties.lead_stage.enum.includes(note.lead_stage)) note.lead_stage = 'browsing';
  if (!SUMMARY_SCHEMA.properties.visitor_type.enum.includes(note.visitor_type)) note.visitor_type = 'other';
  if (note.contact_phone || note.contact_email) note.lead_stage = 'ready';
  return note;
}

// ── storage ─────────────────────────────────────────────────────────────
function sbFetch(env, path, init = {}) {
  return fetch(`${env.SUPABASE_URL}/rest/v1/${path}`, { ...init, headers: { apikey: env.SUPABASE_SERVICE_ROLE_KEY, Authorization: `Bearer ${env.SUPABASE_SERVICE_ROLE_KEY}`, 'Content-Type': 'application/json', ...(init.headers || {}) } });
}
const memory = new Map(); // local testing without Supabase
function makeStore(env) {
  if (!env.SUPABASE_URL || !env.SUPABASE_SERVICE_ROLE_KEY || env.CHAT_MEMORY === '1') return memoryStore();   // CHAT_MEMORY=1: local tests, chats not saved
  return supabaseStore(env);
}
function memoryStore() {
  return {
    get: async id => structuredClone(memory.get(id) || null), recentFromIp: async () => 0,
    save: async chat => { memory.set(chat.id, { ...memory.get(chat.id), ...structuredClone(chat) }); },
    saveSummary: async (id, note) => { memory.set(id, { ...memory.get(id), ...note }); },
  };
}
function supabaseStore(env) {
  const call = async (path, init) => { const res = await sbFetch(env, path, init); if (!res.ok) throw new Error(`supabase ${res.status}: ${await res.text()}`); return res; };
  return {
    async get(id) { return (await (await call(`urbannest_chats?id=eq.${id}&select=id,messages,turns,page,ip_hash`)).json())[0] || null; },
    async recentFromIp(ipHash) {
      const since = new Date(Date.now() - 3600e3).toISOString();
      const res = await call(`urbannest_chats?ip_hash=eq.${ipHash}&created_at=gte.${since}&select=id`, { method: 'HEAD', headers: { Prefer: 'count=exact' } });
      return Number((res.headers.get('content-range') || '*/0').split('/')[1]) || 0;
    },
    async save(chat) {
      await call('urbannest_chats', { method: 'POST', headers: { Prefer: 'resolution=merge-duplicates,return=minimal' },
        body: JSON.stringify({ id: chat.id, messages: chat.messages, turns: chat.turns, page: chat.page, ip_hash: chat.ip_hash, updated_at: new Date().toISOString() }) });
    },
    async saveSummary(id, note) { await call(`urbannest_chats?id=eq.${id}`, { method: 'PATCH', headers: { Prefer: 'return=minimal' }, body: JSON.stringify(note) }); },
  };
}

// ── helpers ─────────────────────────────────────────────────────────────
function json(obj, status = 200) { return new Response(JSON.stringify(obj), { status, headers: { 'Content-Type': 'application/json', 'Cache-Control': 'no-store' } }); }
async function hashIp(ip, salt) {
  const buf = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(salt + '|' + ip));
  return [...new Uint8Array(buf)].slice(0, 12).map(b => b.toString(16).padStart(2, '0')).join('');
}
async function* mockReply(messages) {
  const text = `(test mode) You said: "${messages[messages.length - 1].content.slice(0, 80)}". I would suggest a piece from the Collection.`;
  for (const word of text.split(/(?<= )/)) { await new Promise(r => setTimeout(r, 20)); yield word; }
}
