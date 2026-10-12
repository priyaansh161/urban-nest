-- ═══════════════════════════════════════════════════════════════
--  URBAN NEST — CREATOR APPLICATIONS (the /creators page)
--  Run once: Supabase Dashboard → SQL Editor → New Query → paste → Run.
--  Safe to run again.
--
--  Designers apply on storeurbannest.in/creators. An application lands
--  here; Priyaansh reviews it in Admin → Contributors, and "Add as
--  contributor" turns it into a writer with a studio invite.
--
--  Nobody can read or write this table except the admin. Applications
--  arrive only through apply_to_creator_studio(), which checks the fields,
--  allows five an hour from one network, and never stores the same email
--  twice while an application is still waiting.
--
--  NEEDS is_admin() (lock-down-rls.sql) and contributors
--  (setup-contributors.sql), both already run on this project.
-- ═══════════════════════════════════════════════════════════════

create table if not exists creator_applications (
  id             uuid primary key default gen_random_uuid(),
  name           text not null,
  email          text not null,
  phone          text,
  city           text,
  work           text,                 -- what they do: Interior designer, Architect …
  link           text,                 -- Instagram handle or portfolio address
  message        text,                 -- what they'd write about
  source         text,                 -- creators-page, or creators-page:<src>
  status         text not null default 'new' check (status in ('new', 'added', 'declined')),
  contributor_id uuid references contributors(id) on delete set null,
  ip_hash        text,
  created_at     timestamptz not null default now()
);
alter table creator_applications enable row level security;
create index if not exists creator_applications_status_idx on creator_applications(status, created_at desc);

drop policy if exists "Admin manages creator applications" on creator_applications;
create policy "Admin manages creator applications" on creator_applications
  for all using (is_admin()) with check (is_admin());

create or replace function apply_to_creator_studio(
  p_name text, p_email text, p_phone text, p_city text,
  p_work text, p_link text, p_message text, p_source text
) returns json language plpgsql security definer set search_path = public as $$
declare
  v_email text := lower(trim(coalesce(p_email, '')));
  v_phone text := nullif(regexp_replace(coalesce(p_phone, ''), '[^0-9+]', '', 'g'), '');
  v_ip    text;
begin
  if length(trim(coalesce(p_name, ''))) < 2 then raise exception 'name required'; end if;
  if v_email !~ '^[^@\s]+@[^@\s]+\.[^@\s]+$' then raise exception 'invalid email'; end if;
  if v_phone is not null and length(regexp_replace(v_phone, '\D', '', 'g')) not between 10 and 15 then
    raise exception 'invalid phone';
  end if;

  -- Already a writer, or already waiting: say yes, store nothing new.
  if exists (select 1 from contributors where email = v_email) then
    return json_build_object('ok', true, 'already', 'contributor');
  end if;
  if exists (select 1 from creator_applications where email = v_email and status = 'new') then
    return json_build_object('ok', true, 'already', 'applied');
  end if;

  v_ip := md5(coalesce(split_part(
            nullif(current_setting('request.headers', true), '')::json ->> 'x-forwarded-for', ',', 1), ''));
  if (select count(*) from creator_applications
        where ip_hash = v_ip and created_at > now() - interval '1 hour') >= 5 then
    raise exception 'too many applications';
  end if;

  insert into creator_applications (name, email, phone, city, work, link, message, source, ip_hash)
  values (left(trim(p_name), 80), left(v_email, 120), left(v_phone, 20),
          left(nullif(trim(coalesce(p_city, '')), ''), 60),
          left(nullif(trim(coalesce(p_work, '')), ''), 60),
          left(nullif(trim(coalesce(p_link, '')), ''), 200),
          left(nullif(trim(coalesce(p_message, '')), ''), 1000),
          left(nullif(trim(coalesce(p_source, '')), ''), 40),
          v_ip);
  return json_build_object('ok', true);
end $$;
grant execute on function apply_to_creator_studio(text, text, text, text, text, text, text, text) to anon, authenticated;

-- Check: expect true, 1, 1.
select
  to_regclass('public.creator_applications') is not null                         as table_created,
  (select count(*) from pg_policies where tablename = 'creator_applications')    as policies_1,
  (select count(*) from pg_proc where proname = 'apply_to_creator_studio')       as function_1;
