/* Cloudflare Pages Functions: the thin door into the real handlers.
 *
 * The handlers themselves live in netlify/functions/ and are unchanged:
 * each is `export default async (request) => Response`, which is plain web
 * standard code that runs on either host. Cloudflare passes settings
 * (Supabase and Razorpay keys) per request rather than in process.env, so
 * this puts them where lib/shared.mjs looks before handing the request on.
 *
 * Files here are named with a leading underscore so Cloudflare does not
 * treat this one as a route of its own.
 */
export function serve(handler) {
  return async (context) => {
    globalThis.UN_ENV = context.env;
    return handler(context.request);
  };
}
