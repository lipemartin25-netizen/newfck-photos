-- 1) Habilitar Row Level Security (RLS) de forma segura
alter table if exists public.scans enable row level security;
alter table if exists public.photos enable row level security;
alter table if exists public.face_clusters enable row level security;
alter table if exists public.event_clusters enable row level security;

-- 2) Limpar políticas antigas se já existirem (evita erro de duplicidade)
drop policy if exists "own_scans" on public.scans;
drop policy if exists "own_photos" on public.photos;
drop policy if exists "own_faces" on public.face_clusters;
drop policy if exists "own_events" on public.event_clusters;

-- 3) Criar Políticas de Isolamento de Usuário (User Isolation)
create policy "own_scans" on public.scans
  for all using (auth.uid() = user_id);

create policy "own_photos" on public.photos
  for all using (auth.uid() = user_id);

create policy "own_faces" on public.face_clusters
  for all using (auth.uid() = user_id);

create policy "own_events" on public.event_clusters
  for all using (auth.uid() = user_id);
