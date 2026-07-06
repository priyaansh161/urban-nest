// ═══════════════════════════════════════════════════════════════
//  URBAN NEST — SUPABASE CONFIGURATION
// ═══════════════════════════════════════════════════════════════
//  SETUP STEPS (do this once):
//
//  1. Go to https://supabase.com → New Project
//  2. Dashboard → Settings → API
//     Copy "Project URL" and "anon/public" key below
//  3. Dashboard → SQL Editor → New Query → paste & run this SQL:
//
//  ── SQL TO RUN IN SUPABASE ─────────────────────────────────
//
//  create table nest_posts (
//    id uuid default gen_random_uuid() primary key,
//    title text not null,
//    content text,
//    image_url text,
//    category text default 'general',
//    published boolean default false,
//    pinned boolean default false,
//    created_at timestamptz default now(),
//    updated_at timestamptz default now()
//  );
//
//  create table collection_items (
//    id uuid default gen_random_uuid() primary key,
//    name text not null,
//    description text,
//    image_url text,
//    category text,
//    price text,
//    coming_soon boolean default true,
//    published boolean default false,
//    sort_order int default 0,
//    created_at timestamptz default now()
//  );
//
//  create table feedback (
//    id uuid default gen_random_uuid() primary key,
//    name text,
//    email text,
//    message text not null,
//    rating int check (rating between 1 and 5),
//    page text default 'general',
//    status text default 'unread',
//    created_at timestamptz default now()
//  );
//
//  create table spline_scenes (
//    id uuid default gen_random_uuid() primary key,
//    name text not null,
//    url text not null,
//    description text,
//    page_placement text default 'home',
//    active boolean default false,
//    created_at timestamptz default now()
//  );
//
//  -- Row Level Security: allow public reads of published content
//  alter table nest_posts enable row level security;
//  alter table collection_items enable row level security;
//  alter table feedback enable row level security;
//  alter table spline_scenes enable row level security;
//
//  create policy "Public reads published posts"
//    on nest_posts for select using (published = true);
//  create policy "Admin full access posts"
//    on nest_posts for all using (auth.role() = 'authenticated');
//
//  create policy "Public reads published items"
//    on collection_items for select using (published = true);
//  create policy "Admin full access collection"
//    on collection_items for all using (auth.role() = 'authenticated');
//
//  create policy "Public can submit feedback"
//    on feedback for insert with check (true);
//  create policy "Admin reads feedback"
//    on feedback for all using (auth.role() = 'authenticated');
//
//  create policy "Public reads active scenes"
//    on spline_scenes for select using (active = true);
//  create policy "Admin full access spline"
//    on spline_scenes for all using (auth.role() = 'authenticated');
//
//  ─────────────────────────────────────────────────────────────
//  4. Dashboard → Authentication → Users → Add User
//     Create your admin email + password
//  5. Fill in your credentials below, then deploy
// ═══════════════════════════════════════════════════════════════

const SUPABASE_URL      = 'https://ifwxgwvsyispkaxzbstg.supabase.co';
const SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imlmd3hnd3ZzeWlzcGtheHpic3RnIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODI3MjI3ODQsImV4cCI6MjA5ODI5ODc4NH0.goQIrgT8-tSbN7nIEvHGifKjczi0JhgY01FVu_lQc4c';
