-- ═══════════════════════════════════════════════════════════════
--  URBAN NEST — STORAGE POLICIES FOR PIECE PHOTOGRAPHS
--  Run once: Supabase Dashboard → SQL Editor → New Query → paste → Run
--
--  WHY: the "Blog Images" bucket is public, so anything already in it is
--  readable — which is why the Oil Bottle photograph shows fine. But it
--  has never had an INSERT policy, because everything in it was put
--  there by hand through the Supabase dashboard. The moment the admin
--  tried to upload into it, row-level security refused.
--
--  This is the same script as setup-model-storage.sql, pointed at the
--  images bucket instead. Read stays open to everyone; writing is the
--  admin only.
--
--  Safe to run more than once.
-- ═══════════════════════════════════════════════════════════════

-- ── The bucket ─────────────────────────────────────────────────
-- It already exists; this only makes sure it is public and will accept
-- the formats the upload button produces. 6 MB is generous — the button
-- shrinks a photograph to 1600px WebP, which lands around 150 KB, and
-- the ceiling is only here to catch something going up unresized.
insert into storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
values ('Blog Images', 'Blog Images', true, 6291456,
        array['image/webp', 'image/jpeg', 'image/png', 'image/avif', 'image/gif'])
on conflict (id) do update
  set public             = true,
      file_size_limit    = 6291456,
      allowed_mime_types = array['image/webp', 'image/jpeg', 'image/png', 'image/avif', 'image/gif'];

-- ── The policies ───────────────────────────────────────────────
-- Same shape as the models bucket: one transaction, so the admin test is
-- chosen at run time rather than referring to a function this project
-- might not have.
do $$
declare
  admin_test text;
begin
  if exists (select 1 from pg_proc where proname = 'is_admin') then
    admin_test := 'is_admin()';
  else
    admin_test := 'auth.role() = ''authenticated''';
  end if;

  execute 'drop policy if exists "Images are readable by anyone" on storage.objects';
  execute 'create policy "Images are readable by anyone" on storage.objects
             for select using (bucket_id = ''Blog Images'')';

  execute 'drop policy if exists "Admin uploads images" on storage.objects';
  execute 'create policy "Admin uploads images" on storage.objects
             for insert with check (bucket_id = ''Blog Images'' and ' || admin_test || ')';

  execute 'drop policy if exists "Admin replaces images" on storage.objects';
  execute 'create policy "Admin replaces images" on storage.objects
             for update using (bucket_id = ''Blog Images'' and ' || admin_test || ')
             with check (bucket_id = ''Blog Images'' and ' || admin_test || ')';

  execute 'drop policy if exists "Admin deletes images" on storage.objects';
  execute 'create policy "Admin deletes images" on storage.objects
             for delete using (bucket_id = ''Blog Images'' and ' || admin_test || ')';
end $$;

-- ── Proof it worked ────────────────────────────────────────────
-- Expect: bucket_public true, policies_created 4.
select
  (select public from storage.buckets where id = 'Blog Images')   as bucket_public,
  (select count(*) from pg_policies
     where schemaname = 'storage' and tablename = 'objects'
       and policyname ilike '%images%')                           as policies_created,
  (select case when exists (select 1 from pg_proc where proname = 'is_admin')
               then 'is_admin() — locked to your email'
               else 'authenticated — run lock-down-rls.sql to tighten' end) as write_rule;
