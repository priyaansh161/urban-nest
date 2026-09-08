-- ═══════════════════════════════════════════════════════════════
--  URBAN NEST — STOP STRANGERS LISTING THE BUCKETS
--  Run: Supabase Dashboard → SQL Editor → New Query → paste → Run
--
--  WHAT WENT WRONG: setup-model-storage.sql and setup-image-storage.sql
--  each created a broad SELECT policy on storage.objects so that files
--  would be "readable by anyone". That was unnecessary and it did more
--  than intended.
--
--  A PUBLIC bucket already serves its files through /object/public/…,
--  which bypasses row-level security. The SELECT policy adds nothing to
--  that — but it does grant list(), which lets an unauthenticated caller
--  ask for a complete inventory of the bucket. Checked before writing
--  this: 32 files in Blog Images and all 28 models came back to a plain
--  anon-key request.
--
--  The files were never private. The list is the thing worth closing:
--  it hands over every asset name including work not yet on the site.
--
--  Nothing in the site lists a bucket. It only calls upload (INSERT,
--  kept below) and getPublicUrl, which builds a string and never
--  touches the API. Images and models keep loading exactly as now.
--
--  Safe to run more than once.
-- ═══════════════════════════════════════════════════════════════

drop policy if exists "Images are readable by anyone" on storage.objects;
drop policy if exists "Models are readable by anyone" on storage.objects;

-- ── What should be left: the admin write policies, and nothing that
--    grants a public read or list. ─────────────────────────────────
select policyname, cmd
from pg_policies
where schemaname = 'storage' and tablename = 'objects'
order by policyname;
