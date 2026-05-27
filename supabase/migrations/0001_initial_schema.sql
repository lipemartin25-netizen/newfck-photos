-- ============================================================
-- AlbumAI Studio v2.0 - Schema Inicial
-- Cole TUDO isto no SQL Editor do Supabase e clique em RUN
-- ============================================================

-- 1) EXTENSÕES
create extension if not exists "uuid-ossp";
create extension if not exists "pgcrypto";
create extension if not exists "vector";       -- pgvector p/ embeddings CLIP

-- 2) TABELAS PRINCIPAIS

create table if not exists public.scans (
  id uuid primary key default gen_random_uuid(),
  user_id uuid references auth.users not null,
  filename text not null,
  storage_path text not null,
  status text default 'pending',
  detected_count int default 0,
  created_at timestamptz default now(),
  expires_at timestamptz default now() + interval '24 hours'
);

create table if not exists public.photos (
  id uuid primary key default gen_random_uuid(),
  scan_id uuid references public.scans on delete cascade,
  user_id uuid references auth.users not null,
  bbox jsonb not null,
  storage_path text not null,
  enhanced boolean default false,
  retouched boolean default false,
  rotation int default 0,
  year int,
  exif jsonb,
  phash text,
  face_cluster_id uuid,
  event_cluster_id uuid,
  created_at timestamptz default now()
);

create table if not exists public.face_clusters (
  id uuid primary key default gen_random_uuid(),
  user_id uuid references auth.users not null,
  name text,
  cover_photo_id uuid references public.photos,
  centroid_embedding vector(512),
  created_at timestamptz default now()
);

create table if not exists public.event_clusters (
  id uuid primary key default gen_random_uuid(),
  user_id uuid references auth.users not null,
  label text,
  cover_photo_id uuid references public.photos,
  date_start date,
  date_end date,
  created_at timestamptz default now()
);
