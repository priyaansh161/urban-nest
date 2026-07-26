-- Adds the article fields The Nest editor needs for full magazine-style posts.
-- Safe to run more than once (IF NOT EXISTS). Run in Supabase → SQL Editor.

alter table nest_posts add column if not exists excerpt          text;
alter table nest_posts add column if not exists author           text;
alter table nest_posts add column if not exists read_time        text;
alter table nest_posts add column if not exists slug             text;
alter table nest_posts add column if not exists tags             text;
alter table nest_posts add column if not exists meta_description text;
