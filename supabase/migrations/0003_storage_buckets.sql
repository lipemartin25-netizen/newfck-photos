-- Criar buckets de armazenamento seguro no Supabase Storage
insert into storage.buckets (id, name, public) 
values ('scans', 'scans', false)
on conflict (id) do nothing;

insert into storage.buckets (id, name, public) 
values ('photos', 'photos', false)
on conflict (id) do nothing;

-- RLS policies para buckets de fotos
create policy "Allow owners to upload scans" 
on storage.objects for insert 
with check (bucket_id = 'scans' and auth.role() = 'authenticated');

create policy "Allow owners to read scans" 
on storage.objects for select 
using (bucket_id = 'scans' and auth.role() = 'authenticated');

create policy "Allow owners to upload photos" 
on storage.objects for insert 
with check (bucket_id = 'photos' and auth.role() = 'authenticated');

create policy "Allow owners to read photos" 
on storage.objects for select 
using (bucket_id = 'photos' and auth.role() = 'authenticated');
