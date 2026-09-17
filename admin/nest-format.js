/* ── FORMATTING TOOLBAR for Nest articles ──
 *
 * Shared by the admin's editor (admin/nest.html) and the contributors'
 * studio (studio/index.html). It used to live inline in nest.html; moved
 * here, unchanged, the moment a second page needed it, so the two editors
 * can never drift into writing different syntax.
 *
 * Operates on the textarea's own selection rather than opening any kind of
 * editor — the syntax typed in is exactly what nest-body.js's formatBody()
 * reads, so what you see here is genuinely what controls the output, just
 * without having to remember "how many #'s was it again".
 *
 * The page needs: a .fmt-toolbar with .fmt-btn[data-fmt] buttons, a
 * select#fmtStyle, and the textarea#postContent.
 */
function fmtCurrentLines(ta) {
  const { selectionStart: s, selectionEnd: e, value } = ta;
  const lineStart = value.lastIndexOf('\n', s - 1) + 1;
  let lineEnd = value.indexOf('\n', Math.max(e - 1, s));
  if (lineEnd === -1) lineEnd = value.length;
  return { lineStart, lineEnd, block: value.slice(lineStart, lineEnd) };
}
function fmtStripMarkers(line) {
  return line.replace(/^#{1,4}\s*/, '').replace(/^[-*]\s+/, '').replace(/^\d+[.)]\s+/, '');
}
function fmtFireInput(ta) {
  ta.focus();
  ta.dispatchEvent(new Event('input', { bubbles: true }));
}
function fmtHeading(ta, hashes) {
  const { lineStart, lineEnd, block } = fmtCurrentLines(ta);
  const lines = block.split('\n').map(l => l.trim() === '' ? l : hashes + ' ' + fmtStripMarkers(l));
  ta.setRangeText(lines.join('\n'), lineStart, lineEnd, 'end');
  fmtFireInput(ta);
}
// Clicking the same list button again turns it back off, the way a word
// processor's list toggle does — so `test` decides the direction.
function fmtList(ta, test, marker) {
  const { lineStart, lineEnd, block } = fmtCurrentLines(ta);
  const lines = block.split('\n');
  const already = lines.filter(l => l.trim()).every(l => test.test(l.trim()));
  let n = 0;
  const next = lines.map(l => {
    if (l.trim() === '') return l;
    const bare = fmtStripMarkers(l);
    return already ? bare : marker(++n) + bare;
  });
  ta.setRangeText(next.join('\n'), lineStart, lineEnd, 'end');
  fmtFireInput(ta);
}
function fmtParagraph(ta) {
  const { lineStart, lineEnd, block } = fmtCurrentLines(ta);
  const next = block.split('\n').map(l => l.trim() === '' ? l : fmtStripMarkers(l));
  ta.setRangeText(next.join('\n'), lineStart, lineEnd, 'end');
  fmtFireInput(ta);
}
// Wraps the selection in `mark`, or unwraps it if it's already wrapped —
// the Ctrl+B-twice behaviour. With nothing selected it drops in placeholder
// text and selects it, so the next keystroke replaces it.
function fmtWrap(ta, mark, placeholder) {
  const start = ta.selectionStart, end = ta.selectionEnd;
  const hasSelection = start !== end;
  const sel = ta.value.slice(start, end);
  const m = mark.length;

  if (hasSelection && sel.startsWith(mark) && sel.endsWith(mark) && sel.length > m * 2) {
    const inner = sel.slice(m, -m);
    ta.setRangeText(inner, start, end, 'select');
    fmtFireInput(ta);
    return;
  }
  const outer = ta.value.slice(start - m, end + m);
  if (hasSelection && outer === mark + sel + mark) {
    ta.setRangeText(sel, start - m, end + m, 'select');
    fmtFireInput(ta);
    return;
  }
  const text = hasSelection ? sel : placeholder;
  ta.setRangeText(mark + text + mark, start, end, 'end');
  ta.selectionStart = start + m;
  ta.selectionEnd = start + m + text.length;
  fmtFireInput(ta);
}

const FMT_ACTIONS = {
  bold:      ta => fmtWrap(ta, '**', 'bold text'),
  italic:    ta => fmtWrap(ta, '*', 'italic text'),
  h2:        ta => fmtHeading(ta, '#'),
  h3:        ta => fmtHeading(ta, '##'),
  h4:        ta => fmtHeading(ta, '###'),
  paragraph: ta => fmtParagraph(ta),
  bullets:   ta => fmtList(ta, /^[-*]\s+/, () => '- '),
  numbers:   ta => fmtList(ta, /^\d+[.)]\s+/, n => n + '. '),
};

/* The style dropdown reads as well as writes: it shows what the line the
   cursor sits on already is, so it answers "what am I typing in?" and not
   only "what do I want next?" — the half of a word processor's style box
   people actually rely on. */
function fmtStyleOfLine(line) {
  const m = line.match(/^(#{1,3})#*\s*/);
  if (!m) return 'paragraph';
  return m[1].length === 1 ? 'h2' : m[1].length === 2 ? 'h3' : 'h4';
}
function fmtSyncStyle() {
  const ta = document.getElementById('postContent');
  const sel = document.getElementById('fmtStyle');
  if (!ta || !sel) return;
  const { block } = fmtCurrentLines(ta);
  sel.value = fmtStyleOfLine(block.split('\n')[0] || '');
}

function fmtInit() {
  const ta = document.getElementById('postContent');
  const style = document.getElementById('fmtStyle');
  if (!ta) return;

  document.querySelectorAll('.fmt-toolbar .fmt-btn').forEach(btn => {
    // mousedown, not click: the textarea would lose its selection to the
    // button before a click handler ever ran.
    btn.addEventListener('mousedown', (e) => {
      e.preventDefault();
      const run = FMT_ACTIONS[btn.dataset.fmt];
      if (run) run(ta);
      fmtSyncStyle();
    });
  });

  if (style) style.addEventListener('change', (e) => {
    const run = FMT_ACTIONS[e.target.value];
    if (run) run(ta);
  });
  ['click', 'keyup', 'focus'].forEach(evt => ta.addEventListener(evt, fmtSyncStyle));

  ta.addEventListener('keydown', (e) => {
    if (!(e.ctrlKey || e.metaKey) || e.altKey) return;
    const key = e.key.toLowerCase();
    if (key !== 'b' && key !== 'i') return;
    e.preventDefault();
    FMT_ACTIONS[key === 'b' ? 'bold' : 'italic'](e.target);
  });
}

if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', fmtInit);
else fmtInit();
