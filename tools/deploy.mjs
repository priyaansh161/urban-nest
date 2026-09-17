/* Build and deploy the site to Cloudflare Pages, and record it in DEPLOY-LOG.md.
 *
 *     node tools/deploy.mjs "What changed, in a few words"
 *
 * Every deploy goes through this so the log is never behind. It refuses to
 * run without a description, builds dist/, deploys it as production, and
 * appends a row: date, time, the git commit, the description, and the
 * deployment's own address (which keeps serving that exact version, handy
 * for comparing before and after).
 *
 * Deploys are free on Cloudflare Pages (500 a month on the free plan), so
 * this log is for knowing what went live when, not for counting credits.
 */
import { execSync, spawnSync } from 'node:child_process';
import { appendFileSync, existsSync, writeFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');
const LOG = join(ROOT, 'DEPLOY-LOG.md');
const note = process.argv.slice(2).join(' ').trim();
if (!note) {
  console.error('Say what changed:  node tools/deploy.mjs "Branded not-found page"');
  process.exit(1);
}

const run = cmd => execSync(cmd, { cwd: ROOT, encoding: 'utf8' }).trim();
const commit = run('git rev-parse --short HEAD');
const dirty = run('git status --porcelain --untracked-files=no') ? ' (+ uncommitted changes)' : '';

console.log('Building dist/ …');
execSync('node tools/build-site.mjs', { cwd: ROOT, stdio: 'inherit' });

console.log('Deploying to Cloudflare Pages …');
const r = spawnSync('npx', ['wrangler', 'pages', 'deploy', '--branch', 'main', '--commit-hash', commit,
  '--commit-message', note, '--commit-dirty=true'], { cwd: ROOT, encoding: 'utf8', shell: true });
const out = (r.stdout || '') + (r.stderr || '');
process.stdout.write(out);
const url = (out.match(/https:\/\/[a-z0-9]+\.storeurbannest\.pages\.dev/) || [])[0];
if (r.status !== 0 || !url) {
  console.error('\nDeploy failed, so nothing was added to DEPLOY-LOG.md.');
  process.exit(1);
}

if (!existsSync(LOG)) writeFileSync(LOG, '# Deploy log\n\n| Date | Time (IST) | Commit | What changed | Deployment |\n|---|---|---|---|---|\n');
const now = new Date();
const date = now.toLocaleDateString('en-CA', { timeZone: 'Asia/Kolkata' });
const time = now.toLocaleTimeString('en-GB', { timeZone: 'Asia/Kolkata', hour: '2-digit', minute: '2-digit' });
appendFileSync(LOG, `| ${date} | ${time} | ${commit}${dirty} | ${note.replace(/\|/g, '/')} | ${url} |\n`);
console.log(`\nLogged in DEPLOY-LOG.md: ${date} ${time}, ${commit}, ${url}`);
