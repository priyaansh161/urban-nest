/* Turns a Nest article's text into HTML.
 *
 * Shared by the public reader (community.html) and the contributors' studio
 * preview (studio/index.html), so a writer's preview is exactly what readers
 * get. Moved here unchanged from community.html. The syntax it reads is what
 * admin/nest-format.js's toolbar writes.
 */
function formatBody(raw) {
  const esc = s => s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
  // Bold before italic: once ** pairs become <strong>, the single *'s
  // left over are unambiguously italic markers, not a leftover half of
  // a bold pair.
  const bold = s => s.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
  const italic = s => s.replace(/\*(.+?)\*/g, '<em>$1</em>');
  const linkify = s => s.replace(/(https?:\/\/[^\s<]+)/g, '<a href="$1" target="_blank" rel="noopener">$1</a>');
  const inline = s => linkify(italic(bold(esc(s))));
  return (raw || '').replace(/\r/g,'').split(/\n\s*\n/).map(block => {
    const lines = block.split('\n').map(l => l.trim()).filter(Boolean);
    if (!lines.length) return '';
    // Heading: 1–3 #'s pick the level — # the biggest, ### the
    // smallest — space after them optional. Four or more #'s is
    // treated the same as three, rather than erroring.
    const hm = lines[0].match(/^(#{1,3})#*\s*(.*)$/);
    if (hm) {
      const tag = hm[1].length === 1 ? 'h2' : hm[1].length === 2 ? 'h3' : 'h4';
      const heading = hm[2].replace(/\s*#+\s*$/, '').trim();
      return '<' + tag + '>' + inline(heading) + '</' + tag + '>' +
        (lines.length > 1 ? '<p>' + lines.slice(1).map(inline).join('<br>') + '</p>' : '');
    }
    if (lines.every(l => /^[-*]\s+/.test(l))) {
      return '<ul>' + lines.map(l => '<li>' + inline(l.replace(/^[-*]\s+/, '')) + '</li>').join('') + '</ul>';
    }
    if (lines.every(l => /^\d+[.)]\s+/.test(l))) {
      return '<ol>' + lines.map(l => '<li>' + inline(l.replace(/^\d+[.)]\s+/, '')) + '</li>').join('') + '</ol>';
    }
    return '<p>' + lines.map(inline).join('<br>') + '</p>';
  }).join('');
}
