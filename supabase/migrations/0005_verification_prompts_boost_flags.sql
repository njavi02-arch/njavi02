-- ============================================================================
-- Orbita — verificación de perfil, prompts de perfil, Boost con monedas y señales
-- automáticas de cuentas sospechosas.
--
-- Cuatro funcionalidades decididas en PRODUCT_BRAIN.md tras investigar Wizz, Tinder,
-- Bumble, Yubo y Hinge (ver ese documento → INVESTIGACIÓN/DECISIONES para el porqué de
-- cada decisión de diseño). Resumen de las decisiones que more importan a nivel de schema:
--   - Verificación = selfie + cola de moderación MANUAL (no reconocimiento facial de
--     terceros, que implicaría contratar un servicio externo).
--   - Boost se paga con monedas (no con dinero real), para no depender de la pasarela de
--     pago pendiente.
--   - Las señales de cuentas sospechosas se generan por ACUMULACIÓN de reportes, sin IA de
--     terceros — es la misma idea de "cooldown/revisión para cuentas sospechosas" que la
--     investigación de mercado describe como la defensa real frente a bots modernos.
-- ============================================================================

-- ----------------------------------------------------------------------------
-- 1. VERIFICACIÓN DE PERFIL
-- ----------------------------------------------------------------------------

alter table profiles add column if not exists is_verified boolean not null default false;

create table verification_requests (
  id uuid primary key default gen_random_uuid(),
  profile_id uuid not null references profiles (id) on delete cascade,
  selfie_url text not null,
  status text not null default 'pending' check (status in ('pending', 'approved', 'rejected')),
  reviewed_by uuid,
  reviewed_at timestamptz,
  rejection_reason text,
  created_at timestamptz not null default now()
);

-- Como mucho una solicitud pendiente a la vez por perfil (evita spam de reintentos).
create unique index idx_verification_requests_one_pending
  on verification_requests (profile_id)
  where status = 'pending';

create index idx_verification_requests_status on verification_requests (status, created_at);

alter table verification_requests enable row level security;

create policy verification_requests_select_own on verification_requests
  for select to authenticated
  using (profile_id = auth.uid());

create policy verification_requests_insert_own on verification_requests
  for insert to authenticated
  with check (profile_id = auth.uid());
-- UPDATE (aprobar/rechazar) solo vía service_role desde el panel admin — sin policy para
-- "authenticated", igual que el resto de colas de moderación del proyecto.

create or replace function sync_profile_verified_flag()
returns trigger
language plpgsql
as $$
begin
  if new.status = 'approved' and (old.status is distinct from 'approved') then
    update profiles set is_verified = true where id = new.profile_id;
  elsif old.status = 'approved' and new.status <> 'approved' then
    -- Revocar una verificación aprobada por error también revoca el badge.
    update profiles set is_verified = false where id = new.profile_id;
  end if;
  return new;
end;
$$;

create trigger trg_verification_requests_sync
  after update on verification_requests
  for each row execute function sync_profile_verified_flag();

-- ----------------------------------------------------------------------------
-- 2. PROMPTS DE PERFIL (estilo pregunta corta elegida por el usuario, brief implícito en
--    la investigación de Hinge — ver PRODUCT_BRAIN.md). Máximo 3 por perfil.
-- ----------------------------------------------------------------------------

create table profile_prompts (
  id uuid primary key default gen_random_uuid(),
  profile_id uuid not null references profiles (id) on delete cascade,
  question text not null,
  answer text not null check (char_length(answer) between 1 and 200),
  position smallint not null check (position between 0 and 2),
  created_at timestamptz not null default now(),
  unique (profile_id, position)
);

create index idx_profile_prompts_profile on profile_prompts (profile_id, position);

alter table profile_prompts enable row level security;

-- Mismas reglas de visibilidad que el resto del perfil: cualquier autenticado puede leer
-- los prompts de un perfil activo y no bloqueado (reutiliza is_blocked_between()).
create policy profile_prompts_select_visible on profile_prompts
  for select to authenticated
  using (
    profile_id = auth.uid()
    or (
      not is_blocked_between(auth.uid(), profile_prompts.profile_id)
      and exists (select 1 from profiles p where p.id = profile_prompts.profile_id and p.status = 'active')
    )
  );

create policy profile_prompts_owner_write on profile_prompts
  for all to authenticated
  using (profile_id = auth.uid())
  with check (profile_id = auth.uid());

create or replace function enforce_max_prompts()
returns trigger
language plpgsql
as $$
begin
  -- Excluye la propia posición que se está insertando/actualizando (el cliente hace
  -- upsert con onConflict=profile_id,position al editar un prompt existente; sin este
  -- filtro, editar el 3er prompt ya existente se bloquearía a sí mismo).
  if (
    select count(*) from profile_prompts
    where profile_id = new.profile_id and position <> new.position
  ) >= 3 then
    raise exception 'Máximo de 3 prompts por perfil alcanzado';
  end if;
  return new;
end;
$$;

create trigger trg_profile_prompts_max_3
  before insert on profile_prompts
  for each row execute function enforce_max_prompts();

-- ----------------------------------------------------------------------------
-- 3. BOOST PAGADO CON MONEDAS (profile_boosts ya existía en 0001_init.sql sin lógica).
-- ----------------------------------------------------------------------------

insert into app_config (key, value, description) values
  ('boost_coin_cost', '100', 'Coste en monedas de activar un Boost de visibilidad'),
  ('boost_duration_minutes', '30', 'Duración de un Boost en minutos')
on conflict (key) do nothing;

create or replace function activate_boost()
returns profile_boosts
language plpgsql
security definer
set search_path = public
as $$
declare
  v_profile_id uuid := auth.uid();
  v_cost integer;
  v_duration_minutes integer;
  v_existing profile_boosts%rowtype;
  v_boost profile_boosts%rowtype;
begin
  if v_profile_id is null then
    raise exception 'No autenticado';
  end if;

  select * into v_existing from profile_boosts
    where profile_id = v_profile_id and ends_at > now()
    order by ends_at desc limit 1;

  if v_existing is not null then
    raise exception 'Ya tienes un Boost activo hasta las %', to_char(v_existing.ends_at, 'HH24:MI');
  end if;

  select coalesce((value #>> '{}')::integer, 100) into v_cost from app_config where key = 'boost_coin_cost';
  select coalesce((value #>> '{}')::integer, 30) into v_duration_minutes from app_config where key = 'boost_duration_minutes';

  perform spend_coins(v_profile_id, v_cost, 'boost_purchase');

  insert into profile_boosts (profile_id, starts_at, ends_at, coin_cost)
    values (v_profile_id, now(), now() + make_interval(mins => v_duration_minutes), v_cost)
    returning * into v_boost;

  return v_boost;
end;
$$;

create or replace function get_active_boosted_profile_ids()
returns table (profile_id uuid)
language sql
stable
security definer
set search_path = public
as $$
  select pb.profile_id from profile_boosts pb where pb.ends_at > now();
$$;

-- ----------------------------------------------------------------------------
-- 4. SEÑALES AUTOMÁTICAS DE CUENTAS SOSPECHOSAS (suspicious_activity_flags ya existía en
--    0001_init.sql sin ninguna lógica que escribiera en ella).
-- ----------------------------------------------------------------------------

create or replace function flag_profile_on_report_accumulation()
returns trigger
language plpgsql
security definer
set search_path = public
as $$
declare
  v_recent_report_count integer;
  v_already_flagged boolean;
begin
  select count(*) into v_recent_report_count
    from reports
    where reported_id = new.reported_id
      and created_at > now() - interval '30 days';

  -- Umbral bajo (3): es una señal para la cola de revisión humana, no una sanción
  -- automática — el panel admin decide qué hacer, coherente con "moderación no debe
  -- eliminar una cuenta sin revisión humana" (docs/06-security-and-privacy.md).
  if v_recent_report_count < 3 then
    return new;
  end if;

  select exists (
    select 1 from suspicious_activity_flags
    where profile_id = new.reported_id and flag_type = 'multiple_reports' and not resolved
  ) into v_already_flagged;

  if not v_already_flagged then
    insert into suspicious_activity_flags (profile_id, flag_type, score, details)
      values (
        new.reported_id,
        'multiple_reports',
        least(v_recent_report_count, 10),
        jsonb_build_object('reportCount30d', v_recent_report_count, 'triggeredByReportId', new.id)
      );
  end if;

  -- A partir de 5 reportes en 30 días, además de la señal, se reduce la visibilidad
  -- poniendo el perfil en revisión (igual que ya hacíamos para motivos graves individuales).
  if v_recent_report_count >= 5 then
    update profiles set status = 'under_review' where id = new.reported_id and status = 'active';
  end if;

  return new;
end;
$$;

create trigger trg_reports_flag_accumulation
  after insert on reports
  for each row execute function flag_profile_on_report_accumulation();
