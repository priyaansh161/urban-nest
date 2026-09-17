// storeurbannest.in/api/verify-payment: see functions/_host.js
import handler from '../../netlify/functions/verify-payment.mjs';
import { serve } from '../_host.js';

export const onRequest = serve(handler);
