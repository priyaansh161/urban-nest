/* Confirms a payment actually happened, after the browser says it did.
 *
 * Razorpay hands the browser three values on success. Two of them are just
 * ids; the third is an HMAC of the other two, signed with our secret. Only
 * someone holding the secret could produce it — which is why this check
 * happens here and not on the page.
 *
 * A browser claiming "payment succeeded" is not evidence. This is.
 */
import { json, fail, sb, hmacHex, signatureMatches, assertTestMode, env, cors, originAllowed } from './lib/shared.mjs';

export default async (req) => {
  const origin = req.headers.get('origin') || '';
  if (req.method === 'OPTIONS') return new Response(null, { status: 204, headers: cors(origin) });
  if (req.method !== 'POST') return fail(405, 'Method not allowed', origin);
  if (!originAllowed(origin)) return fail(403, 'Not allowed from here', origin);

  let body;
  try { body = await req.json(); }
  catch { return fail(400, 'Malformed request', origin); }

  const orderId   = body?.razorpay_order_id;
  const paymentId = body?.razorpay_payment_id;
  const signature = body?.razorpay_signature;
  if (!orderId || !paymentId || !signature) return fail(400, 'Incomplete payment details', origin);

  try {
    assertTestMode();

    const expected = hmacHex(env('RAZORPAY_KEY_SECRET'), orderId + '|' + paymentId);
    if (!signatureMatches(expected, signature)) {
      // Worth seeing in the logs: a real visitor never produces this.
      console.warn('Signature mismatch for order', orderId);
      return fail(400, 'This payment could not be verified', origin);
    }

    const rows = await sb('orders?razorpay_order_id=eq.' + encodeURIComponent(orderId) +
                          '&select=id,order_no,payment_status,total_paise');
    const order = rows[0];
    if (!order) return fail(404, 'Order not found', origin);

    // Already settled by the webhook, which often lands first. Confirming
    // twice must not look like a failure to whoever is waiting on the page.
    if (order.payment_status === 'paid') {
      return json(200, { order_no: order.order_no, already: true }, origin);
    }

    await sb('orders?id=eq.' + order.id, {
      method: 'PATCH',
      body: JSON.stringify({
        payment_status: 'paid',
        razorpay_payment_id: paymentId,
        razorpay_signature: signature,
        paid_at: new Date().toISOString()
      })
    });

    // Lines move to confirmed together — nothing is packed before the money
    // is real, and every seller on the order learns about it at once.
    await sb('order_items?order_id=eq.' + order.id, {
      method: 'PATCH',
      body: JSON.stringify({ fulfilment_status: 'confirmed' })
    });

    return json(200, { order_no: order.order_no, already: false }, origin);

  } catch (err) {
    console.error('verify-payment failed:', err);
    return fail(500, 'Payment taken, but confirming it failed. Please contact us with your payment id.', origin);
  }
};
