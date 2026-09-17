// storeurbannest.in/api/create-order: see functions/_host.js
import handler from '../../netlify/functions/create-order.mjs';
import { serve } from '../_host.js';

export const onRequest = serve(handler);
