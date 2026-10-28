/* /collection/<slug>: see functions/_category.js. */
import { categoryPage } from '../_category.js';
export const onRequestGet = (ctx) => categoryPage(ctx, 'collection');
