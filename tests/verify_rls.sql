-- OPCIONAL: ejecutar en SQL Editor, después de supabase_setup.sql.
-- Usa dos credenciales ficticias; todas las filas de prueba se revierten.
begin;
select set_config('xeco_test.row_id', gen_random_uuid()::text, true);
set local role anon;
select set_config('request.headers', json_build_object('x-xeco-browser-token', repeat('a', 64))::text, true);

insert into public.xeco_browser_conversations (id, owner_hash, title)
values (current_setting('xeco_test.row_id')::uuid, public.xeco_browser_hash(), 'Prueba RLS temporal');

do $$
begin
    if (select count(*) from public.xeco_browser_conversations where id=current_setting('xeco_test.row_id')::uuid) <> 1 then
        raise exception 'FALLO: el navegador A no puede leer su fila';
    end if;
    begin
        insert into public.xeco_browser_conversations(owner_hash, title)
        values (repeat('0',64), 'Debe fallar');
        raise exception 'FALLO: se permitió insertar una fila de otro propietario';
    exception when insufficient_privilege then null;
    end;
end;
$$;

select set_config('request.headers', json_build_object('x-xeco-browser-token', repeat('b',64))::text, true);
do $$
declare affected integer;
begin
    if exists(select 1 from public.xeco_browser_conversations where id=current_setting('xeco_test.row_id')::uuid) then
        raise exception 'FALLO: el navegador B puede leer la fila de A';
    end if;
    update public.xeco_browser_conversations set title='Debe quedar sin cambios'
    where id=current_setting('xeco_test.row_id')::uuid;
    get diagnostics affected = row_count;
    if affected <> 0 then
        raise exception 'FALLO: el navegador B puede modificar la fila de A';
    end if;
end;
$$;

select set_config('request.headers', '{}', true);
do $$
begin
    if exists(select 1 from public.xeco_browser_conversations where id=current_setting('xeco_test.row_id')::uuid) then
        raise exception 'FALLO: una petición sin credencial puede leer conversaciones';
    end if;
end;
$$;
rollback;
select 'Comprobaciones RLS completadas; no se conservaron filas de prueba.' as resultado;
