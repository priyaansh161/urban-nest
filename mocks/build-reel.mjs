/* Builds mocks/homepage-reel.html: the LIVE homepage with AnimatedWebs'
 * "Luxury Listing Reel" (free template) motion ideas applied, palette and
 * fonts untouched. Preview only: mocks/ is never deployed.
 *     node mocks/build-reel.mjs
 *
 * Borrowed from the template:
 *   1. hero = 4 room photos crossfading 1800ms with a slow 1.0 -> 1.06 zoom
 *   2. a soft spotlight that follows the cursor over the hero (lerp 0.07)
 *   3. headline words fading up 20px, 120ms apart, 900ms each
 *   4. story-style progress bars under the hero, click to jump
 *   5. the spaces as tall "doors": the hovered one widens, the rest close up
 *   6. thin gold rules drawing in under section headings
 * Phones: a fixed soft vignette instead of the spotlight, spaces stacked. */
import { readFile, writeFile } from 'node:fs/promises';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const HERE = dirname(fileURLToPath(import.meta.url));
let html = (await readFile(join(HERE, '..', 'index.html'), 'utf8')).replace(/\r\n/g, '\n');
const swap = (a, b, label) => { const n = html.split(a).length - 1; if (n !== 1) throw new Error(label + ': ' + n); html = html.replace(a, () => b); };
const swapRe = (re, b, label) => { if (!re.test(html)) throw new Error(label + ': no match'); html = html.replace(re, () => b); };

swap('<head>', '<head>\n  <base href="../"/>', 'base');
swapRe(/<title>[^<]*<\/title>/, '<title>Homepage · Listing Reel Mock · Urban Nest</title>', 'title');

const SLIDES = [
  ['reel-1-bedroom', 'The bedroom'], ['reel-2-bath', 'The bathroom'],
  ['reel-3-kitchen', 'The kitchen'], ['reel-4-rattan', 'The quiet corner'],
];

/* 1 + 2: the reel and the spotlight replace the single photo */
swapRe(/<picture class="hero-media">[\s\S]*?<\/picture>\n    <div class="hero-scrim"><\/div>/, `<div class="reel" id="reel" aria-hidden="true">
${SLIDES.map(([f], i) => `      <picture class="reel-slide${i === 0 ? ' on' : ''}"><source media="(max-width: 700px)" srcset="mocks/${f}-m.webp"/><img src="mocks/${f}.webp" alt=""${i ? ' loading="lazy"' : ' fetchpriority="high"'} decoding="async"/></picture>`).join('\n')}
    </div>
    <div class="hero-scrim"></div>
    <div class="spot" id="spot" aria-hidden="true"></div>`, 'hero media');

/* 3: the headline, word by word */
const words = (s, start) => s.split(' ').map((w, i) => `<span class="hw" style="--i:${start + i}">${w}</span>`).join(' ');
swapRe(/<h1 class="hero-type">[\s\S]*?<\/h1>/, `<h1 class="hero-type hero-words">
        ${words('Where Your Space', 1)}<br/>
        ${words('Finds Its', 4)} <span class="hw" style="--i:6"><em>Character.</em></span>
      </h1>`, 'h1');

/* 4: progress bars, one per room, at the foot of the hero */
swap('    <span class="hero-scroll" aria-hidden="true">Scroll<i></i></span>\n  </header>', `    <div class="reel-bars shell" id="reelBars">
${SLIDES.map(([, label], i) => `      <button type="button" class="reel-bar" data-i="${i}" aria-label="Show ${label}"><i></i><span>${label}</span></button>`).join('\n')}
    </div>
  </header>`, 'bars');

/* mock chrome */
swap('</body>', `<div class="mockbar"><span><b>MOCK</b> · Luxury Listing Reel ideas on your homepage · not live</span></div>
<style>${await readFile(join(HERE, 'reel.css'), 'utf8')}</style>
<script>${await readFile(join(HERE, 'reel.js'), 'utf8')}</script>
</body>`, 'tail');

await writeFile(join(HERE, 'homepage-reel.html'), html);
console.log('wrote mocks/homepage-reel.html');
