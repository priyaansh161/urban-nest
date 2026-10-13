/* Pulls Instagram Insights for the Urban Nest account into a CSV, one row per post.
     node tools/ig-insights.mjs            — update insights/ig-posts.csv
     node tools/ig-insights.mjs --show     — update, then print the table sorted by views

   Credentials live in tools/.ig-credentials.json (gitignored, never committed):
     { "token": "<long-lived access token>", "userId": "<instagram business account id>" }
   See tools/IG-INSIGHTS-SETUP.md for how to get both.

   Rows are keyed by media id, so running it again refreshes the numbers on posts
   already in the file and appends anything new. Reels keep earning views for weeks,
   so re-running weekly is the point. */

import { readFileSync, writeFileSync, existsSync, mkdirSync } from 'node:fs';

const API = 'https://graph.facebook.com/v21.0';
const HERE = new URL('.', import.meta.url).pathname.replace(/^\/([A-Za-z]:)/, '$1');
const CRED = HERE + '.ig-credentials.json';
const OUT_DIR = HERE + '../insights';
const OUT = OUT_DIR + '/ig-posts.csv';

if (!existsSync(CRED)) {
  console.error('No credentials at ' + CRED + '\nSee tools/IG-INSIGHTS-SETUP.md');
  process.exit(1);
}
const { token, userId } = JSON.parse(readFileSync(CRED, 'utf8'));

const get = async (path, params = {}) => {
  const u = new URL(API + path);
  for (const [k, v] of Object.entries(params)) u.searchParams.set(k, v);
  u.searchParams.set('access_token', token);
  const r = await fetch(u);
  const j = await r.json();
  if (j.error) throw new Error(j.error.message);
  return j;
};

/* Insight metric names have churned (plays -> views). Ask for the full set, and on
   rejection drop whatever Meta named in the error and retry, so this keeps working
   as they rename things again. */
const insightsFor = async (id, isReel) => {
  let metrics = isReel
    ? ['views', 'reach', 'likes', 'comments', 'saved', 'shares', 'total_interactions',
       'ig_reels_avg_watch_time', 'ig_reels_video_view_total_time']
    : ['views', 'reach', 'likes', 'comments', 'saved', 'shares', 'total_interactions'];
  for (let attempt = 0; attempt < 5; attempt++) {
    try {
      const j = await get(`/${id}/insights`, { metric: metrics.join(',') });
      return Object.fromEntries(j.data.map(m => [m.name, m.values?.[0]?.value ?? '']));
    } catch (e) {
      const bad = metrics.find(m => e.message.includes(m));
      if (!bad) return {};
      metrics = metrics.filter(m => m !== bad);
      if (!metrics.length) return {};
    }
  }
  return {};
};

const media = [];
let url = `/${userId}/media`;
let params = { fields: 'id,caption,media_type,media_product_type,permalink,timestamp', limit: '50' };
for (let page = 0; page < 10; page++) {
  const j = await get(url, params);
  media.push(...(j.data || []));
  if (!j.paging?.next) break;
  const next = new URL(j.paging.next);
  url = next.pathname.replace(/^\/v\d+\.\d+/, '');
  params = Object.fromEntries([...next.searchParams].filter(([k]) => k !== 'access_token'));
}

const rows = [];
for (const m of media) {
  const isReel = m.media_product_type === 'REELS';
  const ins = await insightsFor(m.id, isReel);
  const watchMs = +ins.ig_reels_avg_watch_time || 0;
  rows.push({
    id: m.id,
    date: (m.timestamp || '').slice(0, 10),
    type: isReel ? 'reel' : (m.media_type || '').toLowerCase(),
    views: ins.views ?? '',
    reach: ins.reach ?? '',
    likes: ins.likes ?? '',
    comments: ins.comments ?? '',
    saves: ins.saved ?? '',
    shares: ins.shares ?? '',
    avgWatchSec: watchMs ? (watchMs / 1000).toFixed(1) : '',
    caption: (m.caption || '').split('\n')[0].slice(0, 70),
    permalink: m.permalink || '',
  });
  process.stdout.write('.');
}

/* Song and whether it was trending can't come from the API — Meta does not expose
   the audio of your own post. Those two columns stay yours to fill in, and are
   preserved across runs. */
const manual = new Map();
if (existsSync(OUT)) {
  const lines = readFileSync(OUT, 'utf8').split('\n').slice(1).filter(Boolean);
  for (const line of lines) {
    const cells = line.match(/("([^"]|"")*"|[^,]*)/g).filter((_, i) => i % 2 === 0);
    const id = (cells[1] || '').replace(/^"|"$/g, '');
    manual.set(id, { song: cells[12] || '', trending: cells[13] || '' });
  }
}

const q = s => '"' + String(s ?? '').replace(/"/g, '""') + '"';
const header = ['date', 'id', 'type', 'views', 'reach', 'likes', 'comments', 'saves',
                'shares', 'avg_watch_sec', 'caption', 'permalink', 'song', 'trending_y_n'];
rows.sort((a, b) => b.date.localeCompare(a.date));
const csv = [header.join(','), ...rows.map(r => {
  const m = manual.get(r.id) || {};
  return [q(r.date), q(r.id), q(r.type), r.views, r.reach, r.likes, r.comments, r.saves,
          r.shares, r.avgWatchSec, q(r.caption), q(r.permalink), m.song || '""', m.trending || '""'].join(',');
})].join('\n');

mkdirSync(OUT_DIR, { recursive: true });
writeFileSync(OUT, csv);
console.log('\n' + rows.length + ' posts -> ' + OUT);

if (process.argv.includes('--show')) {
  const reels = rows.filter(r => r.type === 'reel').sort((a, b) => (+b.views || 0) - (+a.views || 0));
  console.log('\ndate        views   reach  saves shares  watch  caption');
  for (const r of reels.slice(0, 20)) {
    console.log([r.date, String(r.views).padStart(6), String(r.reach).padStart(7),
                 String(r.saves).padStart(6), String(r.shares).padStart(6),
                 String(r.avgWatchSec).padStart(6), r.caption.slice(0, 40)].join(' '));
  }
}
