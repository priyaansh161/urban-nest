// storeurbannest.in/api/contributor-login: see functions/_host.js
import handler from '../../netlify/functions/contributor-login.mjs';
import { serve } from '../_host.js';

export const onRequest = serve(handler);
