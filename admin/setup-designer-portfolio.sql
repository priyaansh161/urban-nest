-- ═══════════════════════════════════════════════════════════════
--  URBAN NEST — DESIGNER PORTFOLIOS (a public page per contributor)
--  Run once, AFTER setup-contributors.sql:
--  Supabase Dashboard → SQL Editor → New Query → paste → Run.
--  Safe to run again: everything is "if not exists" / "or replace".
--
--  WHAT IT ADDS
--   • contributors gets what a portfolio page needs: a web address
--     (slug → storeurbannest.in/designers/<slug>), a longer "about",
--     services, an optional public WhatsApp number, and whether they
--     are taking new projects.
--   • portfolio_projects — a designer's finished work: title, place,
--     summary and photos. Drafts are private; published ones are public.
--   • designer_enquiries — the "Enquire" form on their page. Readers can
--     only SEND one (through a function, rate-limited); the designer reads
--     their own, the admin reads all. Every row is a lead Urban Nest sent
--     that designer, which is the number that matters for the B2B pitch.
-- ═══════════════════════════════════════════════════════════════

-- ── 1. Portfolio fields on contributors ────────────────────────
alter table contributors add column if not exists slug               text;
alter table contributors add column if not exists about              text;
alter table contributors add column if not exists services           text;   -- comma-separated
alter table contributors add column if not exists whatsapp           text;   -- public if filled in
alter table contributors add column if not exists accepting_projects boolean not null default true;

create unique index if not exists contributors_slug_idx on contributors(slug);

-- The address is lower-case letters, numbers and single hyphens. Left
-- empty, it is made from the name; a taken one gets -2, -3…
create or replace function contributors_slug() returns trigger
language plpgsql security definer set search_path = public as $$
declare
  base text;
  cand text;
  n    int := 1;
begin
  cand := lower(trim(coalesce(new.slug, '')));
  cand := regexp_replace(cand, '[^a-z0-9]+', '-', 'g');
  cand := trim(both '-' from cand);
  if cand = '' then
    cand := trim(both '-' from regexp_replace(lower(coalesce(new.display_name, '')), '[^a-z0-9]+', '-', 'g'));
  end if;
  if length(cand) < 3 then cand := 'designer' || case when cand = '' then '' else '-' || cand end; end if;
  base := left(cand, 40);
  cand := base;
  while exists (select 1 from contributors where slug = cand and id <> new.id) loop
    n := n + 1;
    cand := left(base, 36) || '-' || n;
  end loop;
  new.slug := cand;
  return new;
end $$;
drop trigger if exists contributors_slug on contributors;
create trigger contributors_slug before insert or update on contributors
  for each row execute function contributors_slug();

-- Existing contributors get an address now (the trigger fills it in).
update contributors set slug = null where slug is null;

alter table contributors drop constraint if exists contributors_about_len;
alter table contributors add constraint contributors_about_len check (about is null or length(about) <= 2000);

-- The public face gains the portfolio fields. Still no email.
-- (New columns go on the end: that is all "or replace" allows for a view.)
create or replace view public_contributors as
  select id, display_name, title, city, bio, avatar_url, instagram, website,
         slug, about, services, whatsapp, accepting_projects
  from contributors where active;
grant select on public_contributors to anon, authenticated;

-- For rules that must see a contributor whatever the reader's own rights.
create or replace function contributor_is_active(p_id uuid) returns boolean
language sql stable security definer set search_path = public as $$
  select exists (select 1 from contributors where id = p_id and active)
$$;
grant execute on function contributor_is_active(uuid) to anon, authenticated;

-- ── 2. Projects ─────────────────────────────────────────────────
create table if not exists portfolio_projects (
  id             uuid primary key default gen_random_uuid(),
  contributor_id uuid not null references contributors(id) on delete cascade,
  title          text not null,
  place          text,                           -- "3BHK · Gurugram"
  kind           text,                           -- "Living room", "Full home"…
  year           int,
  summary        text,
  photos         jsonb not null default '[]',    -- [{ "url": …, "caption": … }], first is the cover
  published      boolean not null default false,
  sort_order     int not null default 0,
  created_at     timestamptz not null default now(),
  updated_at     timestamptz not null default now(),
  constraint portfolio_photos_list check (jsonb_typeof(photos) = 'array' and jsonb_array_length(photos) <= 30),
  constraint portfolio_summary_len check (summary is null or length(summary) <= 2000)
);
create index if not exists portfolio_projects_contributor_idx on portfolio_projects(contributor_id, sort_order);
alter table portfolio_projects enable row level security;

drop policy if exists "Public reads published projects"   on portfolio_projects;
drop policy if exists "Contributor manages own projects"  on portfolio_projects;
drop policy if exists "Admin manages projects"            on portfolio_projects;
create policy "Public reads published projects" on portfolio_projects
  for select using (published and contributor_is_active(contributor_id));
create policy "Contributor manages own projects" on portfolio_projects
  for all using (contributor_id = my_contributor_id())
  with check (contributor_id = my_contributor_id());
create policy "Admin manages projects" on portfolio_projects
  for all using (is_admin()) with check (is_admin());

-- A contributor's project is always theirs, whatever the page sends.
create or replace function portfolio_projects_guard() returns trigger
language plpgsql security definer set search_path = public as $$
begin
  if is_admin() then return new; end if;
  if tg_op = 'INSERT' then
    new.contributor_id := my_contributor_id();
  else
    new.contributor_id := old.contributor_id;
    new.created_at     := old.created_at;
  end if;
  new.updated_at := now();
  return new;
end $$;
drop trigger if exists portfolio_projects_guard on portfolio_projects;
create trigger portfolio_projects_guard before insert or update on portfolio_projects
  for each row execute function portfolio_projects_guard();

-- ── 3. Enquiries ────────────────────────────────────────────────
create table if not exists designer_enquiries (
  id             uuid primary key default gen_random_uuid(),
  contributor_id uuid not null references contributors(id) on delete cascade,
  name           text not null,
  phone          text,
  email          text,
  city           text,
  project_kind   text,
  budget         text,
  message        text,
  status         text not null default 'new' check (status in ('new', 'contacted', 'closed')),
  ip_hash        text,
  created_at     timestamptz not null default now()
);
create index if not exists designer_enquiries_contributor_idx on designer_enquiries(contributor_id, created_at desc);
alter table designer_enquiries enable row level security;

-- No insert rule: an enquiry only arrives through send_designer_enquiry().
drop policy if exists "Contributor reads own enquiries"   on designer_enquiries;
drop policy if exists "Contributor updates own enquiries" on designer_enquiries;
drop policy if exists "Admin manages enquiries"           on designer_enquiries;
create policy "Contributor reads own enquiries" on designer_enquiries
  for select using (contributor_id = my_contributor_id());
create policy "Contributor updates own enquiries" on designer_enquiries
  for update using (contributor_id = my_contributor_id())
  with check (contributor_id = my_contributor_id());
create policy "Admin manages enquiries" on designer_enquiries
  for all using (is_admin()) with check (is_admin());

-- A designer may only move an enquiry along (new → contacted → closed);
-- what the client wrote cannot be edited.
create or replace function designer_enquiries_guard() returns trigger
language plpgsql security definer set search_path = public as $$
declare keep text := new.status;
begin
  if is_admin() then return new; end if;
  new := old;
  new.status := keep;
  return new;
end $$;
drop trigger if exists designer_enquiries_guard on designer_enquiries;
create trigger designer_enquiries_guard before update on designer_enquiries
  for each row execute function designer_enquiries_guard();

-- The Enquire form. Needs a phone or an email to reply to. Five enquiries
-- an hour from one network is plenty for people and stops a script.
create or replace function send_designer_enquiry(
  p_slug text, p_name text, p_phone text, p_email text, p_city text,
  p_kind text, p_budget text, p_message text
) returns json language plpgsql security definer set search_path = public as $$
declare
  v_cid   uuid;
  v_ip    text;
  v_phone text := nullif(regexp_replace(coalesce(p_phone, ''), '[^0-9+]', '', 'g'), '');
  v_email text := nullif(lower(trim(coalesce(p_email, ''))), '');
begin
  select id into v_cid from contributors
    where slug = lower(trim(p_slug)) and active and accepting_projects;
  if v_cid is null then raise exception 'designer not taking enquiries'; end if;

  if length(trim(coalesce(p_name, ''))) < 2 then raise exception 'name required'; end if;
  if v_phone is null and v_email is null then raise exception 'phone or email required'; end if;
  if v_phone is not null and length(regexp_replace(v_phone, '\D', '', 'g')) not between 10 and 15 then
    raise exception 'invalid phone';
  end if;
  if v_email is not null and v_email !~ '^[^@\s]+@[^@\s]+\.[^@\s]+$' then raise exception 'invalid email'; end if;

  v_ip := md5(coalesce(split_part(
            nullif(current_setting('request.headers', true), '')::json ->> 'x-forwarded-for', ',', 1), ''));
  if (select count(*) from designer_enquiries
        where ip_hash = v_ip and created_at > now() - interval '1 hour') >= 5 then
    raise exception 'too many enquiries';
  end if;

  insert into designer_enquiries (contributor_id, name, phone, email, city, project_kind, budget, message, ip_hash)
  values (v_cid, left(trim(p_name), 80), left(v_phone, 20), left(v_email, 120),
          left(nullif(trim(coalesce(p_city, '')), ''), 60), left(nullif(trim(coalesce(p_kind, '')), ''), 60),
          left(nullif(trim(coalesce(p_budget, '')), ''), 40), left(nullif(trim(coalesce(p_message, '')), ''), 1500),
          v_ip);
  return json_build_object('ok', true);
end $$;
grant execute on function send_designer_enquiry(text, text, text, text, text, text, text, text) to anon, authenticated;

-- ── 4. Project photos ───────────────────────────────────────────
-- They go into the same Blog Images/contributors/<id>/ folder as article
-- covers, which setup-contributors.sql already allows. Nothing to add.

-- ═══════════════════════════════════════════════════════════════
--  Check: expect true, true, 3, 3, 1, and every contributor with an address.
-- ═══════════════════════════════════════════════════════════════
select
  to_regclass('public.portfolio_projects') is not null                   as projects_table,
  to_regclass('public.designer_enquiries') is not null                   as enquiries_table,
  (select count(*) from pg_policies where tablename = 'portfolio_projects') as project_policies_3,
  (select count(*) from pg_policies where tablename = 'designer_enquiries') as enquiry_policies_3,
  (select count(*) from pg_proc where proname = 'send_designer_enquiry')  as enquiry_function_1,
  (select count(*) filter (where slug is null) = 0 from contributors)     as all_have_addresses;
