-- ============================================================================
-- Orbita — recalcular profiles.profile_completion_pct automáticamente
--
-- Bug real encontrado en revisión de código: `profile_completion_pct` se definía con
-- default 0 y ningún sitio lo actualizaba nunca. computeProfileCompletionPct() existía en
-- packages/shared y en apps/mobile/src/services/profiles.ts
-- (computeCompletionFromProfile) pero no estaba conectado a ninguna pantalla — el
-- porcentaje de "perfil completado" que se le promete al usuario en el onboarding
-- (StepPreferencesSummary) y en MyProfileScreen se quedaba clavado en 0% para siempre por
-- mucho que el usuario completara su perfil.
--
-- La solución correcta no es acordarse de llamar a una función desde cada pantalla que
-- edita nombre/bio/foto/interés (eso es justo lo que ya se había olvidado una vez): es un
-- trigger de base de datos que recalcula el porcentaje cada vez que cambia algo relevante,
-- sea cual sea el cliente que lo cambió (app, panel admin, futuros clientes).
--
-- La fórmula replica exactamente computeProfileCompletionPct() de
-- packages/shared/src/economy.ts (9 comprobaciones, ver ese archivo para el razonamiento
-- de cada una) — si cambia una regla allí, debe cambiar aquí también.
-- ============================================================================

create or replace function recompute_profile_completion(p_profile_id uuid)
returns void
language plpgsql
security definer
set search_path = public
as $$
declare
  v_profile profiles%rowtype;
  v_photo_count integer;
  v_interest_count integer;
  v_checks integer;
begin
  select * into v_profile from profiles where id = p_profile_id;
  if not found then
    return;
  end if;

  select count(*) into v_photo_count from photos where profile_id = p_profile_id;
  select count(*) into v_interest_count from profile_interests where profile_id = p_profile_id;

  v_checks :=
    (case when length(trim(v_profile.display_name)) > 0 then 1 else 0 end) +
    (case when v_profile.birth_date is not null then 1 else 0 end) +
    (case when v_profile.gender <> 'unspecified' then 1 else 0 end) +
    (case when coalesce(array_length(v_profile.seeking, 1), 0) > 0 then 1 else 0 end) +
    (case when v_profile.city is not null and length(trim(v_profile.city)) > 0 then 1 else 0 end) +
    (case when v_photo_count >= 1 then 1 else 0 end) +
    (case when length(trim(v_profile.bio)) > 0 then 1 else 0 end) +
    (case when v_interest_count >= 3 then 1 else 0 end) +
    (case when v_photo_count >= 3 then 1 else 0 end);

  -- Solo escribe si el valor cambia: evita disparar de nuevo triggers de auditoría en el
  -- futuro por una actualización que no cambia nada.
  update profiles
    set profile_completion_pct = round((v_checks::numeric / 9) * 100)
    where id = p_profile_id
      and profile_completion_pct is distinct from round((v_checks::numeric / 9) * 100);
end;
$$;

create or replace function trg_recompute_completion_from_profiles()
returns trigger
language plpgsql
as $$
begin
  perform recompute_profile_completion(new.id);
  return new;
end;
$$;

-- Ámbito de columnas explícito: así la propia UPDATE de este trigger (que solo toca
-- profile_completion_pct) no se re-dispara a sí misma en bucle.
create trigger trg_profiles_completion
  after insert or update of display_name, birth_date, gender, seeking, city, bio on profiles
  for each row execute function trg_recompute_completion_from_profiles();

create or replace function trg_recompute_completion_from_photos()
returns trigger
language plpgsql
as $$
begin
  if TG_OP = 'DELETE' then
    perform recompute_profile_completion(old.profile_id);
    return old;
  else
    perform recompute_profile_completion(new.profile_id);
    return new;
  end if;
end;
$$;

create trigger trg_photos_completion
  after insert or delete on photos
  for each row execute function trg_recompute_completion_from_photos();

create or replace function trg_recompute_completion_from_interests()
returns trigger
language plpgsql
as $$
begin
  if TG_OP = 'DELETE' then
    perform recompute_profile_completion(old.profile_id);
    return old;
  else
    perform recompute_profile_completion(new.profile_id);
    return new;
  end if;
end;
$$;

create trigger trg_profile_interests_completion
  after insert or delete on profile_interests
  for each row execute function trg_recompute_completion_from_interests();

-- Perfiles ya existentes (por ejemplo si esta migración se aplica sobre datos creados con
-- 0001/0002): recalcular una vez para que no se queden con el 0% histórico.
do $$
declare
  v_profile_id uuid;
begin
  for v_profile_id in select id from profiles loop
    perform recompute_profile_completion(v_profile_id);
  end loop;
end $$;
