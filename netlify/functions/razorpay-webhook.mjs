/* Razorpay telling us directly what happened, server to server.
 *
 * Why this exists when verify-payment already confirms the payment: the
 * browser is not reliable. Someone pays and the phone dies, or the tab is
 * closed on the "processing" screen, or the network drops on the way back.
 * The money moved regardless. This is the path that does not depend on the
 * visitor's device surviving the transaction.
 *
 * It is also the only one that hears about failures and refunds.
 */
import { sb, hmacHex, signatureMatches } from './lib/shared.mjs';

export default async (req) => {
  if (req.method !== 'POST') return new Response('Method not allowed', { status: 405 });

  const secret = process.env.RAZORPAY_WEBHOOK_SECRET;
  // Unset means the webhook has not been configured yet. Refuse rather than
  // accept unverified calls — an endpoint that writes orders on request is
  // worse than one that is temporarily switched off.
  if (!secret) {
    console.warn('Webhook called with no RAZORPAY_WEBHOOK_SECRET set — refused.');
    return new Response('Not configured', { status: 503 });
  }

  // The signature covers the exact bytes sent, so it must be checked against
  // the raw body. Parsing first and re-serialising would change them.
  const raw = await req.text();
  const got = req.headers.get('x-razorpay-signature') || '';
  if (!signatureMatches(hmacHex(secret, raw), got)) {
    console.warn('Webhook signature mismatch — refused.');
    return new Response('Invalid signature', { status: 400 });
  }

  let event;
  try { event = JSON.parse(raw); }
  catch { return new Response('Malformed', { status: 400 }); }

  const kind = event?.event;
  const payment = event?.payload?.payment?.entity;
  const orderId = payment?.order_id;
  if (!orderId) return new Response('Ignored', { status: 200 });

  try {
    const rows = await sb('orders?razorpay_order_id=eq.' + encodeURIComponent(orderId) +
                          '&select=id,order_no,payment_status,total_paise');
    const order = rows[0];
    if (!order) return new Response('Unknown order', { status: 200 });

    if (kind === 'payment.captured' && order.payment_status !== 'paid') {
      await sb('orders?id=eq.' + order.id, {
        method: 'PATCH',
        body: JSON.stringify({
          payment_status: 'paid',
          razorpay_payment_id: payment.id,
          paid_at: new Date().toISOString()
        })
      });
      await sb('order_items?order_id=eq.' + order.id, {
        method: 'PATCH',
        body: JSON.stringify({ fulfilment_status: 'confirmed' })
      });
    }

    if (kind === 'payment.failed' && order.payment_status === 'pending') {
      await sb('orders?id=eq.' + order.id, {
        method: 'PATCH',
        body: JSON.stringify({ payment_status: 'failed' })
      });
    }

    if (kind === 'refund.processed') {
      // amount_refunded is the running total across every refund on the
      // payment, so this stays right when a second partial one arrives.
      const refunded = Number(payment.amount_refunded || event?.payload?.refund?.entity?.amount || 0);
      if (refunded >= Number(order.total_paise || 0)) {
        await sb('orders?id=eq.' + order.id, {
          method: 'PATCH',
          body: JSON.stringify({ payment_status: 'refunded' })
        });
      } else {
        console.warn('Partial refund on', order.order_no + ':', refunded, 'of', order.total_paise,
                     '— order left as paid.');
      }
    }

    // Always 200 once handled. A non-2xx makes Razorpay retry, and retrying
    // an event we have already applied is pointless noise.
    return new Response('OK', { status: 200 });

  } catch (err) {
    console.error('webhook failed:', err);
    // Here a retry IS wanted — the event was valid, we just could not store it.
    return new Response('Storage failed', { status: 500 });
  }
};
