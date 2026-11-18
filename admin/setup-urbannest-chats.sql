-- ═══════════════════════════════════════════════════════════════
--  URBAN NEST — ENMA (CHAT ASSISTANT) CONVERSATIONS
--  Run once: Supabase Dashboard → SQL Editor → New Query → paste → Run
--
--  One row per chat with Enma on storeurbannest.in. The site's chat
--  function (functions/api/chat.js) writes rows with the service-role
--  key (never from a browser); the admin (admin/enma.html) reads and
--  updates them. Visitors get no access: no anon policy exists.
--  Kept apart from motiflabs_chats on purpose (18 Nov 2026).
--
--  Needs is_admin() from lock-down-rls.sql (already run on this project).
-- ═══════════════════════════════════════════════════════════════

create table if not exists urbannest_chats (
  id              uuid primary key,
  created_at      timestamptz not null default now(),
  updated_at      timestamptz not null default now(),
  messages        jsonb not null default '[]',   -- [{role, content, at}]
  turns           int  not null default 0,       -- visitor messages so far
  page            text,                          -- page the chat started on
  ip_hash         text,                          -- salted hash, for rate limits only

  -- written by the summariser after every reply
  summary         text,
  visitor_type    text check (visitor_type in ('shopper','designer','seller','business','other')),
  business_name   text,
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

create index if not exists urbannest_chats_updated_idx on urbannest_chats (updated_at desc);
create index if not exists urbannest_chats_ip_idx      on urbannest_chats (ip_hash, created_at);

alter table urbannest_chats enable row level security;

drop policy if exists "Admin reads enma chats"   on urbannest_chats;
drop policy if exists "Admin updates enma chats" on urbannest_chats;
drop policy if exists "Admin deletes enma chats" on urbannest_chats;
create policy "Admin reads enma chats"   on urbannest_chats for select using (is_admin());
create policy "Admin updates enma chats" on urbannest_chats for update using (is_admin()) with check (is_admin());
create policy "Admin deletes enma chats" on urbannest_chats for delete using (is_admin());
