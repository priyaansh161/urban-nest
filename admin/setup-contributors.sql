-- ═══════════════════════════════════════════════════════════════
--  URBAN NEST — CONTRIBUTORS (designers writing for The Nest Edit)
--  Run once: Supabase Dashboard → SQL Editor → New Query → paste → Run.
--  Safe to run again: everything is "if not exists" / "or replace".
--
--  WHAT IT ADDS
--   • contributors — one row per writer: name, title, bio, photo, links.
--     Their LOGIN is a normal Supabase Auth user with the same email;
--     this table is what makes that login a contributor.
--   • nest_posts.contributor_id — who wrote a post.
--   • nest_posts.upvote_count + nest_upvotes — reader upvotes.
--   • Rules so a contributor can create, edit, publish and delete ONLY
--     their own articles, and upload photos only into their own folder.
--     They still cannot touch products, orders, sellers or other posts:
--     those stay locked to is_admin() (lock-down-rls.sql).
--
--  NEEDS is_admin() from lock-down-rls.sql, already run on this project.
-- ═══════════════════════════════════════════════════════════════

-- ── 1. The contributors table ───────────────────────────────────
create table if not exists contributors (
  id           uuid primary key default gen_random_uuid(),
  email        text not null unique,
  display_name text not null,
  title        text,                 -- e.g. "Interior Designer"
  city         text,
  bio          text,
  avatar_url   text,
  instagram    text,                 -- handle or full URL
  website      text,
  active       boolean not null default true,
  created_at   timestamptz not null default now()
);
alter table contributors enable row level security;

-- Emails are compared lower-cased everywhere, so store them that way.
create or replace function contributors_lower_email() returns trigger
language plpgsql as $$
begin
  new.email := lower(trim(new.email));
  return new;
end $$;
drop trigger if exists contributors_lower_email on contributors;
create trigger contributors_lower_email before insert or update on contributors
  for each row execute function contributors_lower_email();

-- ── 2. Who is asking? ───────────────────────────────────────────
-- security definer so they can read contributors despite its rules.
create or replace function my_contributor_id() returns uuid
language sql stable security definer set search_path = public as $$
  select id from contributors
  where active and email = lower(coalesce(auth.jwt() ->> 'email', ''))
$$;

create or replace function is_contributor() returns boolean
language sql stable security definer set search_path = public as $$
  select my_contributor_id() is not null
$$;
grant execute on function my_contributor_id() to anon, authenticated;
grant execute on function is_contributor()   to anon, authenticated;

-- ── 3. Rules on contributors ────────────────────────────────────
drop policy if exists "Admin manages contributors"   on contributors;
drop policy if exists "Contributor reads own profile" on contributors;
drop policy if exists "Contributor edits own profile" on contributors;
create policy "Admin manages contributors" on contributors
  for all using (is_admin()) with check (is_admin());
create policy "Contributor reads own profile" on contributors
  for select using (id = my_contributor_id());
create policy "Contributor edits own profile" on contributors
  for update using (id = my_contributor_id()) with check (id = my_contributor_id());

-- A contributor may edit their profile, but not their email, and cannot
-- switch themselves back on after being deactivated.
create or replace function contributors_guard() returns trigger
language plpgsql security definer set search_path = public as $$
begin
  if is_admin() then return new; end if;
  new.email      := old.email;
  new.active     := old.active;
  new.created_at := old.created_at;
  return new;
end $$;
drop trigger if exists contributors_guard on contributors;
create trigger contributors_guard before update on contributors
  for each row execute function contributors_guard();

-- The public face of a contributor, for the author card on articles.
-- No email: only what a reader should see.
create or replace view public_contributors as
  select id, display_name, title, city, bio, avatar_url, instagram, website
  from contributors where active;
grant select on public_contributors to anon, authenticated;

-- ── 4. Posts know who wrote them, and how many upvotes they have ─
alter table nest_posts add column if not exists contributor_id uuid
  references contributors(id) on delete set null;
alter table nest_posts add column if not exists upvote_count integer not null default 0;
create index if not exists nest_posts_contributor_idx on nest_posts(contributor_id);

drop policy if exists "Contributor reads own posts"   on nest_posts;
drop policy if exists "Contributor creates posts"     on nest_posts;
drop policy if exists "Contributor edits own posts"   on nest_posts;
drop policy if exists "Contributor deletes own posts" on nest_posts;
create policy "Contributor reads own posts" on nest_posts
  for select using (contributor_id = my_contributor_id());
create policy "Contributor creates posts" on nest_posts
  for insert with check (is_contributor());
create policy "Contributor edits own posts" on nest_posts
  for update using (contributor_id = my_contributor_id())
  with check (contributor_id = my_contributor_id());
create policy "Contributor deletes own posts" on nest_posts
  for delete using (contributor_id = my_contributor_id());

-- What a contributor can't set on a post, whatever the page sends:
-- the owner (always themselves), pinning, the upvote count, and the byline
-- (always their own name). Publishing is theirs: posts go live directly.
create or replace function nest_posts_guard() returns trigger
language plpgsql security definer set search_path = public as $$
declare
  cid   uuid;
  cname text;
begin
  if current_setting('un.bypass', true) = 'on' then return new; end if;  -- the upvote function
  if is_admin() then return new; end if;
  select id, display_name into cid, cname from contributors
    where active and email = lower(coalesce(auth.jwt() ->> 'email', ''));
  if cid is null then return new; end if;   -- not a contributor: the rules above refuse it
  if tg_op = 'INSERT' then
    new.contributor_id := cid;
    new.pinned         := false;
    new.upvote_count   := 0;
  else
    new.contributor_id := old.contributor_id;
    new.pinned         := old.pinned;
    new.upvote_count   := old.upvote_count;
    new.created_at     := old.created_at;
  end if;
  new.author := cname;
  return new;
end $$;
drop trigger if exists nest_posts_guard on nest_posts;
create trigger nest_posts_guard before insert or update on nest_posts
  for each row execute function nest_posts_guard();

-- A contributor who renames themselves is renamed on every article card too.
create or replace function contributors_sync_author() returns trigger
language plpgsql security definer set search_path = public as $$
begin
  if new.display_name is distinct from old.display_name then
    perform set_config('un.bypass', 'on', true);
    update nest_posts set author = new.display_name where contributor_id = new.id;
    perform set_config('un.bypass', 'off', true);
  end if;
  return new;
end $$;
drop trigger if exists contributors_sync_author on contributors;
create trigger contributors_sync_author after update on contributors
  for each row execute function contributors_sync_author();

-- ── 5. Upvotes ──────────────────────────────────────────────────
-- One vote per device (a random id the browser keeps). No rules on the
-- table at all: nobody reads or writes it directly, only the functions.
create table if not exists nest_upvotes (
  post_id    uuid not null references nest_posts(id) on delete cascade,
  voter      text not null,
  ip_hash    text,
  created_at timestamptz not null default now(),
  primary key (post_id, voter)
);
alter table nest_upvotes enable row level security;

-- Tap once to upvote, again to take it back. Returns the new count.
-- The per-address cap (20 a post) only stops someone scripting votes;
-- it is high because a whole office or mobile network can share one address.
create or replace function toggle_nest_upvote(p_post uuid, p_voter text)
returns json language plpgsql security definer set search_path = public as $$
declare
  v_count int;
  v_voted boolean;
  v_ip    text;
begin
  if p_voter is null or p_voter !~ '^[A-Za-z0-9-]{16,64}$' then
    raise exception 'invalid voter';
  end if;
  if not exists (select 1 from nest_posts where id = p_post and published) then
    raise exception 'article not found';
  end if;
  v_ip := md5(coalesce(split_part(
            nullif(current_setting('request.headers', true), '')::json ->> 'x-forwarded-for', ',', 1), ''));

  if exists (select 1 from nest_upvotes where post_id = p_post and voter = p_voter) then
    delete from nest_upvotes where post_id = p_post and voter = p_voter;
    v_voted := false;
  else
    if (select count(*) from nest_upvotes where post_id = p_post and ip_hash = v_ip) >= 20 then
      raise exception 'too many votes from this network';
    end if;
    insert into nest_upvotes (post_id, voter, ip_hash) values (p_post, p_voter, v_ip);
    v_voted := true;
  end if;

  select count(*) into v_count from nest_upvotes where post_id = p_post;
  perform set_config('un.bypass', 'on', true);
  update nest_posts set upvote_count = v_count where id = p_post;
  perform set_config('un.bypass', 'off', true);
  return json_build_object('count', v_count, 'voted', v_voted);
end $$;
grant execute on function toggle_nest_upvote(uuid, text) to anon, authenticated;

-- Which articles has this device already upvoted? (to fill the button in)
create or replace function my_nest_upvotes(p_voter text)
returns setof uuid language sql stable security definer set search_path = public as $$
  select post_id from nest_upvotes where voter = p_voter
$$;
grant execute on function my_nest_upvotes(text) to anon, authenticated;

-- ── 6. Contributors upload photos into their own folder only ────
-- Blog Images/contributors/<their id>/…  (admin uploads are unaffected)
drop policy if exists "Contributors upload own images" on storage.objects;
create policy "Contributors upload own images" on storage.objects
  for insert with check (
    bucket_id = 'Blog Images'
    and (storage.foldername(name))[1] = 'contributors'
    and (storage.foldername(name))[2] = my_contributor_id()::text
  );

-- ═══════════════════════════════════════════════════════════════
--  Check: expect true, 4, 3, 5.
-- ═══════════════════════════════════════════════════════════════
select
  to_regclass('public.contributors') is not null                        as contributors_table,
  (select count(*) from pg_policies where tablename = 'nest_posts'
     and policyname like 'Contributor%')                                 as post_policies_4,
  (select count(*) from pg_policies where tablename = 'contributors')   as contributor_policies_3,
  (select count(*) from pg_proc where proname in ('my_contributor_id', 'is_contributor',
     'toggle_nest_upvote', 'my_nest_upvotes', 'nest_posts_guard'))       as functions_5;
