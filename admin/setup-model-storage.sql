-- ═══════════════════════════════════════════════════════════════
--  URBAN NEST — STORAGE BUCKET FOR 3D MODELS
--  Run once: Supabase Dashboard → SQL Editor → New Query → paste → Run
--
--  WHY: a .glb kept in the repo means a site deploy every time a piece
--  is added or re-exported. Putting models in Storage instead makes a
--  new product pure data entry — upload, paste, publish — the same way
--  the rest of the collection already works.
--
--  ONLY NEEDED FOR THE UPLOAD BUTTON in Admin → Collection. If you are
--  uploading through the Supabase dashboard by hand, a public bucket is
--  enough on its own and you do not need this script at all.
--
--  Safe to run more than once. Nothing here depends on a script you
--  might not have run yet — see the policy block below.
-- ═══════════════════════════════════════════════════════════════

-- ── The bucket ─────────────────────────────────────────────────
-- public = true so model-viewer can fetch by URL with no auth.
-- 25 MB ceiling guards against an un-decimated Meshy export going up
-- by accident; a good model is under 3 MB.
--
-- application/octet-stream is allowed alongside model/gltf-binary because a
-- browser types an upload from the file extension, and Windows has no registry
-- entry for .glb — so it sends "" and the bucket rejects a perfectly good
-- model. The size limit is the guard that actually matters here.
insert into storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
values ('Models', 'Models', true, 26214400,
        array['model/gltf-binary', 'application/octet-stream'])
on conflict (id) do update
  set public             = true,
      file_size_limit    = 26214400,
      allowed_mime_types = array['model/gltf-binary', 'application/octet-stream'];

-- ── The policies ───────────────────────────────────────────────
-- Wrapped in a block that picks its own admin test, because the whole
-- script runs as ONE transaction: a policy referring to a function this
-- project does not have would fail and roll the bucket back with it.
do $$
declare
  admin_test text;
begin
  if exists (select 1 from pg_proc where proname = 'is_admin') then
    -- lock-down-rls.sql has been run: reuse the same rule the tables use.
    admin_test := 'is_admin()';
  else
    -- It has not. Fall back to any signed-in account — the admin has no
    -- sign-up form, so this is still closed to visitors. Re-run this
    -- script after lock-down-rls.sql to tighten it to your email alone.
    admin_test := 'auth.role() = ''authenticated''';
  end if;

  -- Read: anyone. Visitors are never signed in, so models must be
  -- world-readable. Nothing private goes in this bucket.
  execute 'drop policy if exists "Models are readable by anyone" on storage.objects';
  execute 'create policy "Models are readable by anyone" on storage.objects
             for select using (bucket_id = ''Models'')';

  -- Write: admin only.
  execute 'drop policy if exists "Admin uploads models" on storage.objects';
  execute 'create policy "Admin uploads models" on storage.objects
             for insert with check (bucket_id = ''Models'' and ' || admin_test || ')';

  execute 'drop policy if exists "Admin replaces models" on storage.objects';
  execute 'create policy "Admin replaces models" on storage.objects
             for update using (bucket_id = ''Models'' and ' || admin_test || ')
             with check (bucket_id = ''Models'' and ' || admin_test || ')';

  execute 'drop policy if exists "Admin deletes models" on storage.objects';
  execute 'create policy "Admin deletes models" on storage.objects
             for delete using (bucket_id = ''Models'' and ' || admin_test || ')';
end $$;

-- ── Proof it worked ────────────────────────────────────────────
-- Expect one row: bucket_created 1, policies_created 4.
-- If you get 0 anywhere, the run failed — read the error, do not
-- assume it applied.
select
  (select count(*) from storage.buckets where id = 'Models')      as bucket_created,
  (select count(*) from pg_policies
     where schemaname = 'storage' and tablename = 'objects'
       and policyname ilike '%models%')                           as policies_created,
  (select case when exists (select 1 from pg_proc where proname = 'is_admin')
               then 'is_admin() — locked to your email'
               else 'authenticated — run lock-down-rls.sql to tighten' end) as write_rule;
