/* Turns a cart into a Razorpay order and a pending row in our own tables.
 *
 * The one rule this file exists to enforce: THE BROWSER NEVER SETS A PRICE.
 * It sends ids and quantities. Every rupee is read here, from the database,
 * so a cart edited in devtools buys nothing at a discount.
 */
import { json, fail, sb, razorpay, assertTestMode, cors } from './lib/shared.mjs';

const MAX_QTY   = 20;    // per line; a decor piece is not bought by the crate
const MAX_LINES = 20;

export default async (req) => {
  const origin = req.headers.get('origin') || '';
  if (req.method === 'OPTIONS') return new Response(null, { status: 204, headers: cors(origin) });
  if (req.method !== 'POST') return fail(405, 'Method not allowed', origin);

  let body;
  try { body = await req.json(); }
  catch { return fail(400, 'Malformed request', origin); }

  const lines = Array.isArray(body?.lines) ? body.lines : [];
  const c = body?.customer || {};

  if (!lines.length) return fail(400, 'Your selection is empty', origin);
  if (lines.length > MAX_LINES) return fail(400, 'Too many pieces in one order', origin);
  if (!c.name || !c.phone) return fail(400, 'A name and phone number are required', origin);
  if (!/^[0-9+\-\s]{8,16}$/.test(String(c.phone))) return fail(400, 'That phone number does not look right', origin);

  // Collapse duplicates so the same id sent twice cannot dodge the qty cap.
  const wanted = new Map();
  for (const l of lines) {
    if (typeof l?.id !== 'string') return fail(400, 'Malformed selection', origin);
    const qty = Math.floor(Number(l.qty) || 0);
    if (qty < 1) return fail(400, 'Malformed selection', origin);
    wanted.set(l.id, Math.min((wanted.get(l.id) || 0) + qty, MAX_QTY));
  }

  try {
    assertTestMode();

    const ids = [...wanted.keys()];
    const items = await sb(
      'collection_items?id=in.(' + ids.join(',') + ')' +
      '&select=id,name,image_url,price_paise,seller_id,in_stock,published,fulfilled_by'
    );

    // Everything below is checked against the database, not the request.
    const sellerIds = [...new Set(items.map(i => i.seller_id).filter(Boolean))];
    const sellers = sellerIds.length
      ? await sb('sellers?id=in.(' + sellerIds.join(',') + ')&select=id,name,kind,commission_pct,active')
      : [];
    const sellerById = Object.fromEntries(sellers.map(s => [s.id, s]));

    const priced = [];
    for (const id of ids) {
      const it = items.find(x => x.id === id);
      if (!it)                     return fail(409, 'A piece in your selection is no longer available', origin);
      if (!it.published)           return fail(409, '"' + it.name + '" is no longer available', origin);
      if (it.in_stock === false)   return fail(409, '"' + it.name + '" is out of stock', origin);
      if (!it.price_paise || !it.seller_id) return fail(409, '"' + it.name + '" cannot be bought here', origin);

      const seller = sellerById[it.seller_id];
      if (!seller || seller.active === false) return fail(409, '"' + it.name + '" is not currently for sale', origin);

      const qty = wanted.get(id);
      const lineTotal = it.price_paise * qty;
      // Rounded to the paise, and the seller gets the remainder — never us.
      const commission = Math.round(lineTotal * (Number(seller.commission_pct) || 0) / 100);

      priced.push({
        item: it, seller, qty,
        unit: it.price_paise,
        lineTotal,
        commission,
        payout: lineTotal - commission,
        fulfilledBy: it.fulfilled_by || (seller.kind === 'marketplace' ? 'seller' : 'urban_nest')
      });
    }

    const subtotal = priced.reduce((n, p) => n + p.lineTotal, 0);
    const shipping = 0;                 // flat and free until there is a rate card
    const total    = subtotal + shipping;
    if (total < 100) return fail(400, 'Order total is too small', origin);

    // Our row first. If Razorpay succeeds and this fails we would have taken
    // money with nothing to show for it; this way the worst case is an
    // abandoned pending row, which is harmless.
    const [order] = await sb('orders', {
      method: 'POST',
      headers: { Prefer: 'return=representation' },
      body: JSON.stringify([{
        customer_name: String(c.name).slice(0, 120),
        customer_email: c.email ? String(c.email).slice(0, 160) : null,
        customer_phone: String(c.phone).slice(0, 20),
        address_line1: c.address_line1 ? String(c.address_line1).slice(0, 200) : null,
        address_line2: c.address_line2 ? String(c.address_line2).slice(0, 200) : null,
        city: c.city ? String(c.city).slice(0, 80) : null,
        state: c.state ? String(c.state).slice(0, 80) : null,
        pincode: c.pincode ? String(c.pincode).slice(0, 12) : null,
        subtotal_paise: subtotal,
        shipping_paise: shipping,
        total_paise: total,
        payment_status: 'pending'
      }])
    });

    await sb('order_items', {
      method: 'POST',
      body: JSON.stringify(priced.map(p => ({
        order_id: order.id,
        item_id: p.item.id,
        seller_id: p.seller.id,
        name_snapshot: p.item.name,
        image_snapshot: p.item.image_url,
        unit_price_paise: p.unit,
        qty: p.qty,
        line_total_paise: p.lineTotal,
        commission_paise: p.commission,
        seller_payout_paise: p.payout,
        fulfilled_by: p.fulfilledBy,
        fulfilment_status: 'new',
        payout_status: 'pending'
      })))
    });

    const rzp = await razorpay('orders', {
      method: 'POST',
      body: JSON.stringify({
        amount: total,                  // paise, same unit we store
        currency: 'INR',
        receipt: order.order_no,
        notes: { order_no: order.order_no, order_id: order.id }
      })
    });

    await sb('orders?id=eq.' + order.id, {
      method: 'PATCH',
      body: JSON.stringify({ razorpay_order_id: rzp.id })
    });

    // key_id is public — it is what the checkout script identifies us with.
    // key_secret is not, and never leaves this function.
    return json(200, {
      order_no: order.order_no,
      razorpay_order_id: rzp.id,
      amount: total,
      currency: 'INR',
      key_id: process.env.RAZORPAY_KEY_ID
    }, origin);

  } catch (err) {
    console.error('create-order failed:', err);
    return fail(500, 'Could not start the payment. Nothing has been charged.', origin);
  }
};
