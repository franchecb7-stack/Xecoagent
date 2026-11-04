-- Xecoagent sin registro. Ejecutar completo en SQL Editor de Supabase.
-- No requiere Supabase Auth ni correo, contraseña o claves de administrador.
begin;

-- El navegador posee un secreto aleatorio de 256 bits; solo su hash se almacena en filas.
-- PostgREST proporciona los encabezados de la petición a cada transacción.
create or replace function public.xeco_browser_hash()
returns text language sql stable
set search_path = ''
as $$
    select case when token ~ '^[a-f0-9]{64}$'
        then pg_catalog.encode(pg_catalog.sha256(pg_catalog.convert_to(token, 'UTF8')), 'hex')
        else null end
    from (
        select (nullif(pg_catalog.current_setting('request.headers', true), '')::jsonb)
            ->> 'x-xeco-browser-token' as token
    ) as request;
$$;
revoke all on function public.xeco_browser_hash() from public;
grant execute on function public.xeco_browser_hash() to anon;

create table if not exists public.xeco_browser_conversations (
    id uuid primary key default gen_random_uuid(),
    owner_hash text not null check (owner_hash ~ '^[a-f0-9]{64}$'),
    title text not null default 'Nueva conversación' check (char_length(title) <= 80),
    messages jsonb not null default '[]'::jsonb check (jsonb_typeof(messages) = 'array'),
    version integer not null default 1 check (version > 0),
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);
create index if not exists xeco_browser_conversations_owner_updated
on public.xeco_browser_conversations(owner_hash, updated_at desc);

alter table public.xeco_browser_conversations enable row level security;
revoke all on public.xeco_browser_conversations from anon, authenticated;
grant select, insert, update on public.xeco_browser_conversations to anon;

drop policy if exists xeco_browser_owner_only on public.xeco_browser_conversations;
create policy xeco_browser_owner_only on public.xeco_browser_conversations
for all to anon
using (owner_hash = (select public.xeco_browser_hash()))
with check (owner_hash = (select public.xeco_browser_hash()));

create or replace function public.xeco_browser_set_updated_at()
returns trigger language plpgsql
set search_path = ''
as $$
begin
    new.updated_at = now();
    return new;
end;
$$;
drop trigger if exists xeco_browser_conversations_updated_at on public.xeco_browser_conversations;
create trigger xeco_browser_conversations_updated_at
before update on public.xeco_browser_conversations
for each row execute function public.xeco_browser_set_updated_at();

commit;
