/* The site locally WITH its Pages Functions (/api/chat, /piece, /edit ...), the way Cloudflare runs it.
 *   node tools/pages-dev.mjs            → http://localhost:8788   (build dist/ first: node tools/build-site.mjs)
 * Runs from the project folder so wrangler finds functions/ and .dev.vars (Supabase keys; LOCAL_DEV=1 and
 * CHAT_MEMORY=1 there let Enma answer from localhost without saving chats). The AI binding calls Cloudflare for real.
 */
import { spawn } from 'node:child_process';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');
process.chdir(ROOT);
const p = spawn('npx', ['wrangler', 'pages', 'dev', 'dist', '--port', '8788', '--ip', '127.0.0.1'], { stdio: 'inherit', shell: true });
p.on('exit', (c) => process.exit(c ?? 0));
