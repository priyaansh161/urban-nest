// storeurbannest.in/api/razorpay-webhook: see functions/_host.js
import handler from '../../netlify/functions/razorpay-webhook.mjs';
import { serve } from '../_host.js';

export const onRequest = serve(handler);
