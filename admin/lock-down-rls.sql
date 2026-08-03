-- ═══════════════════════════════════════════════════════════════
--  URBAN NEST — LOCK DOWN ADMIN ACCESS
--  Run once: Supabase Dashboard → SQL Editor → New Query → paste → Run
--
--  WHY: every table's "admin" rule currently trusts ANY logged-in
--  user (auth.role() = 'authenticated'). Combined with public
--  sign-up, that let anyone create an account and edit your data.
--  This script rewrites those rules so ONLY your admin email may
--  read/write admin data. Public visitors keep read-only access to
--  published content and can still submit feedback.
--
--  ┌─────────────────────────────────────────────────────────────┐
--  │ STEP 1 — put your admin email inside the quotes below, in    │
--  │ the is_admin() function. That is the ONLY edit you make.     │
--  └─────────────────────────────────────────────────────────────┘
-- ═══════════════════════════════════════════════════════════════

-- Helper: true only when the current request is your admin account.
-- ▼▼▼ CHANGE THE EMAIL ON THE NEXT LINE ▼▼▼
create or replace function is_admin() returns boolean as $$
  select coalesce((select auth.jwt() ->> 'email'), '') = 'you@example.com';
$$ language sql stable;
-- ▲▲▲ CHANGE THE EMAIL ON THE LINE ABOVE ▲▲▲

-- ── room_products ──────────────────────────────────────────────
drop policy if exists "Admin full access products" on room_products;
create policy "Admin full access products"
  on room_products for all
  using (is_admin()) with check (is_admin());

-- ── spline_scenes ──────────────────────────────────────────────
drop policy if exists "Admin full access spline" on spline_scenes;
create policy "Admin full access spline"
  on spline_scenes for all
  using (is_admin()) with check (is_admin());

-- ── nest_posts ─────────────────────────────────────────────────
drop policy if exists "Admin full access posts" on nest_posts;
create policy "Admin full access posts"
  on nest_posts for all
  using (is_admin()) with check (is_admin());

-- ── collection_items ───────────────────────────────────────────
drop policy if exists "Admin full access collection" on collection_items;
create policy "Admin full access collection"
  on collection_items for all
  using (is_admin()) with check (is_admin());

-- ── feedback ───────────────────────────────────────────────────
-- Public keeps INSERT (the "Public can submit feedback" policy);
-- only admin may read / update / delete.
-- All four are dropped, not just the first. Getting the email wrong on line
-- 21 locks you out of writing, and the fix is to correct it and run again —
-- which only works if every policy below can be recreated.
drop policy if exists "Admin reads feedback"   on feedback;
drop policy if exists "Admin manages feedback" on feedback;
drop policy if exists "Admin updates feedback" on feedback;
drop policy if exists "Admin deletes feedback" on feedback;
create policy "Admin manages feedback"
  on feedback for select using (is_admin());
create policy "Admin updates feedback"
  on feedback for update using (is_admin()) with check (is_admin());
create policy "Admin deletes feedback"
  on feedback for delete using (is_admin());

-- ═══════════════════════════════════════════════════════════════
--  Done. Verify with:  select is_admin();   (false when run as
--  anon — that's correct). After this, even if public sign-up is
--  ever re-enabled, a stranger's account can read published
--  content only, exactly like a normal visitor.
-- ═══════════════════════════════════════════════════════════════
