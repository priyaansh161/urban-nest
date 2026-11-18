-- ═══════════════════════════════════════════════════════════════
--  MOTIF LABS — CHAT ASSISTANT CONVERSATIONS
--  Run once: Supabase Dashboard → SQL Editor → New Query → paste → Run
--
--  One row per website chat on motiflabs.in. The Motif Labs worker
--  writes rows with the service-role key (never from a browser); the
--  Urban Nest admin (admin/motiflabs.html) reads and updates them.
--  Visitors get no access at all: no anon policy exists.
--
--  Needs is_admin() from lock-down-rls.sql (already run on this project).
-- ═══════════════════════════════════════════════════════════════

create table if not exists motiflabs_chats (
  id              uuid primary key,
  created_at      timestamptz not null default now(),
  updated_at      timestamptz not null default now(),
  messages        jsonb not null default '[]',   -- [{role, content, at}]
  turns           int  not null default 0,       -- visitor messages so far
  page            text,                          -- page the chat started on
  ip_hash         text,                          -- salted hash, for rate limits only

  -- written by the summariser after every reply
  summary         text,
  business_name   text,
  business_type   text,
  location        text,
  contact_name    text,
  contact_phone   text,
  contact_email   text,
  needs           text,
  recommendation  text,
  questions       text[],
  lead_stage      text check (lead_stage in ('browsing','interested','ready')),

  -- yours, from the admin
  status          text not null default 'new' check (status in ('new','contacted','won','closed','spam')),
  admin_notes     text
);

create index if not exists motiflabs_chats_updated_idx on motiflabs_chats (updated_at desc);
create index if not exists motiflabs_chats_ip_idx      on motiflabs_chats (ip_hash, created_at);

alter table motiflabs_chats enable row level security;

drop policy if exists "Admin reads motiflabs chats"   on motiflabs_chats;
drop policy if exists "Admin updates motiflabs chats" on motiflabs_chats;
drop policy if exists "Admin deletes motiflabs chats" on motiflabs_chats;
create policy "Admin reads motiflabs chats"   on motiflabs_chats for select using (is_admin());
create policy "Admin updates motiflabs chats" on motiflabs_chats for update using (is_admin()) with check (is_admin());
create policy "Admin deletes motiflabs chats" on motiflabs_chats for delete using (is_admin());
