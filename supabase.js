const SUPABASE_URL      = 'https://ifwxgwvsyispkaxzbstg.supabase.co';
const SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imlmd3hnd3ZzeWlzcGtheHpic3RnIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODI3MjI3ODQsImV4cCI6MjA5ODI5ODc4NH0.goQIrgT8-tSbN7nIEvHGifKjczi0JhgY01FVu_lQc4c';

const { createClient } = supabase;
const db = createClient(SUPABASE_URL, SUPABASE_ANON_KEY);
