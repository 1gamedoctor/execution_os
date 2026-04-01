-- supabase_schema.sql
-- Run this once in your Supabase project:
--   Dashboard → SQL Editor → New query → paste this → Run

-- Single key-value table. Stores all app data as JSONB blobs.
-- Simple and requires zero schema changes when you add features.

create table if not exists kv_store (
  key   text primary key,
  value jsonb not null
);

-- Enable Row Level Security, then allow full access via the anon key.
-- Your project's anon key is safe to use here — RLS keeps it scoped.
alter table kv_store enable row level security;

create policy "anon_full_access"
  on kv_store
  for all
  to anon
  using (true)
  with check (true);
