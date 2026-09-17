-- ============================================================================
-- Orbita — acciones atómicas de servidor (post-MVP hardening)
--
-- En 0001_init.sql, "enviar solicitud de conversación" y "enviar Super Like" se hacían
-- desde el cliente en dos llamadas de red separadas (insertar + cobrar). Documentado en
-- su momento como un compromiso aceptable para el MVP (el peor caso es una solicitud
-- gratis si la segunda llamada falla, nunca un cobro sin efecto), pero no es la forma
-- correcta de hacerlo: docs/02-architecture.md ya explicaba que esta lógica debe vivir
-- en el servidor como una sola transacción atómica. Esta migración lo corrige moviendo
-- toda la operación a funciones SECURITY DEFINER, que además ahora sí generan las
-- notificaciones "new_request" y "super_like_received" — antes no se creaba NINGUNA fila
-- en `notifications` para esos dos eventos porque no hay policy de INSERT para clientes
-- en esa tabla (a propósito, ver 0001_init.sql), así que solo código de servidor puede
-- crearlas. Es una laguna real que cierra esta migración.
--
-- También implementa la regla de negocio documentada en docs/ASSUMPTIONS.md ("Reenviar
-- solicitud a alguien que ya rechazó antes está bloqueado 30 días salvo que el otro
-- usuario te escriba primero") que estaba documentada pero no construida.
-- ============================================================================

create or replace function create_conversation_request(p_receiver_id uuid, p_first_message text)
returns conversation_requests
language plpgsql
security definer
set search_path = public
as $$
declare
  v_sender uuid := auth.uid();
  v_banned_words jsonb;
  v_word text;
  v_cooldown_days integer;
  v_recent_decline timestamptz;
  v_receiver_reached_out boolean;
  v_base_limit integer;
  v_request conversation_requests%rowtype;
begin
  if v_sender is null then
    raise exception 'No autenticado';
  end if;
  if v_sender = p_receiver_id then
    raise exception 'No puedes enviarte una solicitud a ti mismo';
  end if;
  if p_first_message is null or length(trim(p_first_message)) = 0 then
    raise exception 'El mensaje no puede estar vacío';
  end if;
  if is_blocked_between(v_sender, p_receiver_id) then
    raise exception 'No puedes contactar con este perfil';
  end if;

  select value into v_banned_words from app_config where key = 'banned_words';
  if v_banned_words is not null then
    for v_word in select jsonb_array_elements_text(v_banned_words) loop
      if length(v_word) > 0 and p_first_message ilike ('%' || v_word || '%') then
        raise exception 'Tu mensaje contiene contenido no permitido';
      end if;
    end loop;
  end if;

  select coalesce((value #>> '{}')::integer, 30) into v_cooldown_days
    from app_config where key = 'conversation_request_cooldown_days';

  select max(created_at) into v_recent_decline
    from conversation_requests
    where sender_id = v_sender and receiver_id = p_receiver_id and status = 'declined'
      and created_at > now() - make_interval(days => coalesce(v_cooldown_days, 30));

  if v_recent_decline is not null then
    select exists (
      select 1 from conversation_requests
      where sender_id = p_receiver_id and receiver_id = v_sender
    ) into v_receiver_reached_out;

    if not v_receiver_reached_out then
      raise exception 'Esta persona rechazó tu solicitud recientemente. Podrás volver a intentarlo más adelante.';
    end if;
  end if;

  select coalesce((value #>> '{}')::integer, 20) into v_base_limit
    from app_config where key = 'new_conversation_rate_limit_per_hour';

  if not check_and_record_rate_limit(v_sender, 'new_conversation', coalesce(v_base_limit, 20), interval '1 hour') then
    raise exception 'Has enviado demasiadas solicitudes de conversación nuevas. Inténtalo de nuevo en un rato.';
  end if;

  -- Insertar y luego cobrar el crédito referenciando la solicitud creada (mejor rastro de
  -- auditoría: message_credit_transactions.reference_id apunta a la solicitud que pagó).
  -- Sigue siendo todo o nada: si spend_message_credit lanza excepción por falta de saldo,
  -- no hay ningún SAVEPOINT/EXCEPTION que aísle el INSERT anterior, así que Postgres
  -- deshace TODA la transacción de esta llamada — incluida la solicitud recién insertada.
  -- Verificado explícitamente con un test real (ver docs/05-mvp-scope-and-testing.md §4b).
  insert into conversation_requests (sender_id, receiver_id, first_message)
    values (v_sender, p_receiver_id, p_first_message)
    returning * into v_request;

  perform spend_message_credit(v_sender, 'conversation_started', v_request.id);

  insert into notifications (profile_id, type, payload)
    values (p_receiver_id, 'new_request', jsonb_build_object('requestId', v_request.id, 'senderId', v_sender));

  return v_request;
end;
$$;

insert into app_config (key, value, description) values
  ('conversation_request_cooldown_days', '30', 'Días de espera para reintentar contactar a quien te rechazó, salvo que te escriba antes')
on conflict (key) do nothing;

-- ----------------------------------------------------------------------------
-- Super Like atómico: cupo gratis del día -> saldo de racha -> monedas, en ese orden.
-- ----------------------------------------------------------------------------
create or replace function send_super_like(p_receiver_id uuid, p_message text default null)
returns super_likes
language plpgsql
security definer
set search_path = public
as $$
declare
  v_sender uuid := auth.uid();
  v_free_limit integer;
  v_coin_cost integer;
  v_sent_today integer;
  v_super_like_balance integer;
  v_row super_likes%rowtype;
begin
  if v_sender is null then
    raise exception 'No autenticado';
  end if;
  if v_sender = p_receiver_id then
    raise exception 'No puedes enviarte un Super Like a ti mismo';
  end if;
  if is_blocked_between(v_sender, p_receiver_id) then
    raise exception 'No puedes contactar con este perfil';
  end if;

  select coalesce((value #>> '{}')::integer, 1) into v_free_limit
    from app_config where key = 'super_like_daily_free';

  select count(*) into v_sent_today
    from super_likes
    where sender_id = v_sender and created_at >= date_trunc('day', now());

  if v_sent_today >= coalesce(v_free_limit, 1) then
    select balance into v_super_like_balance from super_like_credit_wallets where profile_id = v_sender;

    if coalesce(v_super_like_balance, 0) > 0 then
      perform spend_super_like_credit(v_sender, 'super_like_sent');
    else
      select coalesce((value #>> '{}')::integer, 20) into v_coin_cost
        from app_config where key = 'super_like_coin_cost';
      perform spend_coins(v_sender, v_coin_cost, 'super_like_sent');
    end if;
  end if;

  insert into super_likes (sender_id, receiver_id, message)
    values (v_sender, p_receiver_id, p_message)
    returning * into v_row;

  insert into notifications (profile_id, type, payload)
    values (p_receiver_id, 'super_like_received', jsonb_build_object('senderId', v_sender, 'superLikeId', v_row.id));

  return v_row;
end;
$$;
