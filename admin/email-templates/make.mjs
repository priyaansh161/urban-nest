/* Urban Nest's login emails, for Supabase → Authentication → Emails → Templates.
 *
 *   node admin/email-templates/make.mjs
 *
 * Writes one .html per email. Paste each file's contents into the matching
 * template in the Supabase dashboard (Message body → Source), and its SUBJECT
 * into the subject box. {{ .ConfirmationURL }} and {{ .Email }} are Supabase's
 * own placeholders: leave them exactly as they are.
 *
 * Email is not a web page. Most mail apps ignore <style> blocks and web fonts,
 * so everything is inline, laid out with tables, and the serif falls back to
 * Georgia. Colours are the site's: teal #0E3238, paper #F5F7F6, gold #A37B3F.
 */
import { writeFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const HERE = dirname(fileURLToPath(import.meta.url));
const SERIF = "'Bodoni Moda', Didot, Georgia, 'Times New Roman', serif";
const SANS = "'DM Sans', 'Helvetica Neue', Helvetica, Arial, sans-serif";

function email({ preheader, eyebrow, title, paragraphs, button, after }) {
  return `<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<meta name="color-scheme" content="light only"/>
<title>${title.replace(/<[^>]+>/g, '')}</title>
</head>
<body style="margin:0;padding:0;background:#E6EFED;">
<div style="display:none;max-height:0;overflow:hidden;opacity:0;color:#E6EFED;">${preheader}</div>
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="background:#E6EFED;">
  <tr><td align="center" style="padding:32px 16px;">
    <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="max-width:520px;">

      <!-- Brand band -->
      <tr><td align="center" style="background:#0E3238;padding:30px 24px 26px;">
        <img src="https://storeurbannest.in/images/app-icon-192.png" width="52" height="52" alt="" style="display:block;border:0;border-radius:50%;margin:0 auto 14px;"/>
        <div style="font-family:${SERIF};font-size:20px;letter-spacing:5px;color:#F5F7F6;">URBAN NEST</div>
        <div style="font-family:${SANS};font-size:10px;letter-spacing:3px;color:#C2934D;margin-top:6px;">JUST THE RIGHT FEEL</div>
      </td></tr>

      <!-- Message -->
      <tr><td style="background:#FFFFFF;padding:40px 40px 34px;">
        <div style="font-family:${SANS};font-size:10px;letter-spacing:3px;color:#735427;margin-bottom:14px;">${eyebrow}</div>
        <div style="font-family:${SERIF};font-size:28px;line-height:1.2;color:#0F1F22;margin-bottom:22px;">${title}</div>
        ${paragraphs.map(p => `<p style="font-family:${SANS};font-size:15px;line-height:1.75;color:#3F4A4C;margin:0 0 16px;">${p}</p>`).join('\n        ')}
        <table role="presentation" cellpadding="0" cellspacing="0" border="0" style="margin:28px 0 26px;">
          <tr><td align="center" bgcolor="#0E3238" style="border-radius:100px;">
            <a href="{{ .ConfirmationURL }}" style="display:inline-block;padding:15px 36px;font-family:${SANS};font-size:12px;font-weight:bold;letter-spacing:2px;color:#FFFFFF;text-decoration:none;border-radius:100px;">${button}</a>
          </td></tr>
        </table>
        ${after.map(p => `<p style="font-family:${SANS};font-size:13px;line-height:1.7;color:#586366;margin:0 0 12px;">${p}</p>`).join('\n        ')}
        <p style="font-family:${SANS};font-size:12px;line-height:1.7;color:#586366;margin:18px 0 0;padding-top:18px;border-top:1px solid #D9E0DE;">If the button doesn't work, copy this link into your browser:<br/><a href="{{ .ConfirmationURL }}" style="color:#735427;word-break:break-all;">{{ .ConfirmationURL }}</a></p>
      </td></tr>

      <!-- Footer -->
      <tr><td align="center" style="padding:22px 24px 8px;">
        <p style="font-family:${SANS};font-size:11px;line-height:1.7;color:#586366;margin:0;">Sent to {{ .Email }} by Urban Nest<br/><a href="https://storeurbannest.in" style="color:#735427;text-decoration:none;">storeurbannest.in</a></p>
      </td></tr>

    </table>
  </td></tr>
</table>
</body>
</html>
`;
}

const TEMPLATES = {
  'invite-user': {
    subject: "You're invited to write for The Nest Edit",
    html: email({
      preheader: 'Choose a password to open your Nest Studio.',
      eyebrow: 'THE NEST STUDIO',
      title: 'Welcome to <em style="color:#94703A;">The Nest Edit.</em>',
      paragraphs: [
        "Urban Nest has set up your Nest Studio: your own space to publish articles, show your finished projects on a portfolio page, and receive enquiries from people who'd like to work with you.",
        'Tap below to choose your password. That\'s all it takes.',
      ],
      button: 'CHOOSE MY PASSWORD',
      after: [
        'After that, sign in any time at <a href="https://storeurbannest.in/studio/" style="color:#735427;">storeurbannest.in/studio</a>.',
        "This link works once and expires after a while. If it has, ask Urban Nest to send a new one.",
      ],
    }),
  },
  'reset-password': {
    subject: 'Reset your Urban Nest password',
    html: email({
      preheader: 'A link to choose a new password.',
      eyebrow: 'PASSWORD RESET',
      title: 'Choose a new password.',
      paragraphs: [
        'Someone asked to reset the password for this Urban Nest login. If that was you, tap below and pick a new one.',
      ],
      button: 'RESET MY PASSWORD',
      after: [
        "Didn't ask for this? Ignore this email: your password stays exactly as it is.",
        'The link works once and expires after a while.',
      ],
    }),
  },
};

for (const [name, t] of Object.entries(TEMPLATES)) {
  writeFileSync(join(HERE, name + '.html'), t.html);
  console.log(`${name}.html   subject: ${t.subject}`);
}
