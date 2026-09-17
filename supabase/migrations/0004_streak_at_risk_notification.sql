-- ============================================================================
-- Orbita — notificación real de "racha en riesgo"
--
-- `streak_at_risk` era un valor válido de notifications.type desde 0001_init.sql pero
-- ningún código, ni cliente ni servidor, lo disparaba nunca — otro hueco real encontrado
-- en la auditoría de esta sesión (ver PRODUCT_BRAIN.md → PROBLEMAS). Esta función permite
-- que el cliente la dispare de forma segura (no puede insertar en `notifications`
-- directamente — a propósito, ver 0001_init.sql) con deduplicación: como máximo una
-- notificación de este tipo por usuario y día, aunque se llame varias veces (p. ej. en
-- cada apertura de la app).
-- ============================================================================

create or replace function notify_streak_at_risk_if_needed()
returns boolean
language plpgsql
security definer
set search_path = public
as $$
declare
  v_profile_id uuid := auth.uid();
  v_streak daily_streaks%rowtype;
  v_today date := current_date;
  v_already_notified boolean;
begin
  if v_profile_id is null then
    return false;
  end if;

  select * into v_streak from daily_streaks where profile_id = v_profile_id;

  -- Sin racha activa o ya reclamada hoy: no hay nada en riesgo.
  if v_streak is null or v_streak.current_streak <= 0 or v_streak.last_checkin_date = v_today then
    return false;
  end if;

  select exists (
    select 1 from notifications
    where profile_id = v_profile_id
      and type = 'streak_at_risk'
      and created_at >= v_today::timestamptz
  ) into v_already_notified;

  if v_already_notified then
    return false;
  end if;

  insert into notifications (profile_id, type, payload)
    values (v_profile_id, 'streak_at_risk', jsonb_build_object('currentStreak', v_streak.current_streak));

  return true;
end;
$$;
