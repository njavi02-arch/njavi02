-- ============================================================================
-- Orbita — esquema inicial (FASE 3)
-- Diseñado para Supabase (Postgres 16 + Auth + Realtime + Storage).
-- Convenciones:
--   * Toda tabla de negocio tiene RLS activada con "deny by default".
--   * Los saldos (monedas, créditos de mensaje) son de solo lectura para el cliente;
--     solo se mutan vía funciones SECURITY DEFINER (grant_coins, spend_coins, etc.)
--     para que ningún cliente parcheado pueda escribirse saldo directamente.
--   * Las cifras de negocio configurables viven en app_config, nunca hardcodeadas aquí.
-- Ver docs/03-database.md para la justificación de cada decisión de modelado.
-- ============================================================================

create extension if not exists pgcrypto;

-- ----------------------------------------------------------------------------
-- Helper genérico: mantener updated_at al día en cualquier tabla que lo tenga.
-- ----------------------------------------------------------------------------
create or replace function set_updated_at()
returns trigger
language plpgsql
as $$
begin
  new.updated_at = now();
  return new;
end;
$$;

-- ============================================================================
-- 1. PROFILES
-- ============================================================================

create table profiles (
  id uuid primary key references auth.users (id) on delete cascade,
  display_name text not null check (char_length(display_name) between 1 and 50),
  birth_date date not null,
  gender text not null default 'unspecified'
    check (gender in ('male', 'female', 'non_binary', 'unspecified')),
  seeking text[] not null default '{}'
    check (seeking <@ array['friendship', 'social', 'dating']),
  city text,
  latitude double precision,
  longitude double precision,
  bio text not null default '' check (char_length(bio) <= 500),
  status text not null default 'active'
    check (status in ('active', 'under_review', 'suspended', 'deleted')),
  is_premium boolean not null default false,
  premium_until timestamptz,
  profile_completion_pct smallint not null default 0
    check (profile_completion_pct between 0 and 100),
  onboarding_completed_at timestamptz,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  last_active_at timestamptz not null default now(),
  deleted_at timestamptz,
  -- edad mínima 18 verificada también en la app y en el trigger de abajo (defensa en profundidad)
  constraint chk_min_age check (birth_date <= (current_date - interval '18 years'))
);

create index idx_profiles_status_last_active on profiles (status, last_active_at desc);
create index idx_profiles_city on profiles (city);

create trigger trg_profiles_updated_at
  before update on profiles
  for each row execute function set_updated_at();

-- blocks se crea aquí (adelantada respecto al resto de la sección "Seguridad") porque la
-- policy de visibilidad de profiles, justo debajo, necesita poder consultarla.
create table blocks (
  id uuid primary key default gen_random_uuid(),
  blocker_id uuid not null references profiles (id) on delete cascade,
  blocked_id uuid not null references profiles (id) on delete cascade,
  created_at timestamptz not null default now(),
  check (blocker_id <> blocked_id),
  unique (blocker_id, blocked_id)
);

create index idx_blocks_blocker on blocks (blocker_id);
create index idx_blocks_blocked on blocks (blocked_id);

alter table blocks enable row level security;

create policy blocks_select_own on blocks
  for select to authenticated
  using (blocker_id = auth.uid());

create policy blocks_insert_own on blocks
  for insert to authenticated
  with check (blocker_id = auth.uid());

create policy blocks_delete_own on blocks
  for delete to authenticated
  using (blocker_id = auth.uid());

-- IMPORTANTE: no comprobar bloqueos con un EXISTS inline sobre `blocks` desde OTRA
-- política. `blocks` tiene su propia RLS (blocks_select_own: solo ves los bloqueos que
-- TÚ creaste), así que un EXISTS inline evaluado como el usuario B nunca vería el
-- bloqueo que A creó contra B: el bloqueo dejaría de ser bidireccional. Esta función
-- SECURITY DEFINER se ejecuta con los privilegios del dueño de la tabla (quien aplica
-- las migraciones), que no está sujeto a la RLS de `blocks`, así que sí puede comprobar
-- el bloqueo en ambos sentidos. Confirmado con un test real que falló antes de este fix
-- (ver docs/05-mvp-scope-and-testing.md).
create or replace function is_blocked_between(a uuid, b uuid)
returns boolean
language sql
stable
security definer
set search_path = public
as $$
  select exists (
    select 1 from blocks
    where (blocker_id = a and blocked_id = b)
       or (blocker_id = b and blocked_id = a)
  );
$$;

alter table profiles enable row level security;

-- Perfiles activos son visibles para cualquier usuario autenticado que no esté bloqueado
-- en cualquiera de los dos sentidos.
create policy profiles_select_visible on profiles
  for select to authenticated
  using (
    auth.uid() is not null
    and status = 'active'
    and (id = auth.uid() or not is_blocked_between(auth.uid(), profiles.id))
  );

create policy profiles_update_own on profiles
  for update to authenticated
  using (id = auth.uid())
  with check (id = auth.uid());

create policy profiles_insert_own on profiles
  for insert to authenticated
  with check (id = auth.uid());

-- ----------------------------------------------------------------------------
-- user_preferences: preferencias de descubrimiento (paso final del onboarding)
-- ----------------------------------------------------------------------------
create table user_preferences (
  profile_id uuid primary key references profiles (id) on delete cascade,
  min_age smallint not null default 18 check (min_age >= 18),
  max_age smallint not null default 55 check (max_age >= min_age),
  max_distance_km integer not null default 50 check (max_distance_km > 0),
  show_me_gender text[] not null default array['male', 'female', 'non_binary'],
  updated_at timestamptz not null default now()
);

create trigger trg_user_preferences_updated_at
  before update on user_preferences
  for each row execute function set_updated_at();

alter table user_preferences enable row level security;

create policy user_preferences_owner_all on user_preferences
  for all to authenticated
  using (profile_id = auth.uid())
  with check (profile_id = auth.uid());

-- ----------------------------------------------------------------------------
-- notification_preferences
-- ----------------------------------------------------------------------------
create table notification_preferences (
  profile_id uuid primary key references profiles (id) on delete cascade,
  new_message boolean not null default true,
  new_request boolean not null default true,
  super_like_received boolean not null default true,
  profile_viewed boolean not null default true,
  daily_reward_ready boolean not null default true,
  secret_admirer boolean not null default true,
  promotions boolean not null default true,
  updated_at timestamptz not null default now()
);

create trigger trg_notification_preferences_updated_at
  before update on notification_preferences
  for each row execute function set_updated_at();

alter table notification_preferences enable row level security;

create policy notification_preferences_owner_all on notification_preferences
  for all to authenticated
  using (profile_id = auth.uid())
  with check (profile_id = auth.uid());

-- ============================================================================
-- 2. FOTOS E INTERESES
-- ============================================================================

create table photos (
  id uuid primary key default gen_random_uuid(),
  profile_id uuid not null references profiles (id) on delete cascade,
  storage_path text not null,
  url text not null,
  position smallint not null check (position >= 0),
  moderation_status text not null default 'pending'
    check (moderation_status in ('pending', 'approved', 'rejected')),
  moderation_notes text,
  moderated_by uuid,
  created_at timestamptz not null default now(),
  unique (profile_id, position)
);

create index idx_photos_profile_position on photos (profile_id, position);

alter table photos enable row level security;

-- Las fotos aprobadas de un perfil visible son legibles por cualquier autenticado;
-- el propio dueño ve también las suyas en cualquier estado de moderación.
create policy photos_select_visible on photos
  for select to authenticated
  using (
    profile_id = auth.uid()
    or (
      moderation_status = 'approved'
      and exists (select 1 from profiles p where p.id = photos.profile_id and p.status = 'active')
    )
  );

create policy photos_owner_insert on photos
  for insert to authenticated
  with check (profile_id = auth.uid());

create policy photos_owner_update on photos
  for update to authenticated
  using (profile_id = auth.uid())
  with check (profile_id = auth.uid());

create policy photos_owner_delete on photos
  for delete to authenticated
  using (profile_id = auth.uid());

-- Límite de fotos por perfil (max_photos_count en app_config; se valida también en la app,
-- aquí un tope absoluto defensivo de 10 tal como pide el brief sección 5).
create or replace function enforce_max_photos()
returns trigger
language plpgsql
as $$
begin
  if (select count(*) from photos where profile_id = new.profile_id) >= 10 then
    raise exception 'Máximo de 10 fotos por perfil alcanzado';
  end if;
  return new;
end;
$$;

create trigger trg_photos_max_10
  before insert on photos
  for each row execute function enforce_max_photos();

create table interests (
  id uuid primary key default gen_random_uuid(),
  name text not null unique,
  category text
);

alter table interests enable row level security;

create policy interests_select_all on interests
  for select to authenticated
  using (true);

create table profile_interests (
  profile_id uuid not null references profiles (id) on delete cascade,
  interest_id uuid not null references interests (id) on delete cascade,
  primary key (profile_id, interest_id)
);

alter table profile_interests enable row level security;

create policy profile_interests_select_all on profile_interests
  for select to authenticated
  using (true);

create policy profile_interests_owner_write on profile_interests
  for all to authenticated
  using (profile_id = auth.uid())
  with check (profile_id = auth.uid());

-- ----------------------------------------------------------------------------
-- photo_unlocks: quién ha desbloqueado el paquete de fotos ocultas de quién.
-- ----------------------------------------------------------------------------
create table photo_unlocks (
  id uuid primary key default gen_random_uuid(),
  viewer_id uuid not null references profiles (id) on delete cascade,
  target_profile_id uuid not null references profiles (id) on delete cascade,
  method text not null check (method in ('coins', 'premium', 'admin_grant')),
  created_at timestamptz not null default now(),
  unique (viewer_id, target_profile_id)
);

create index idx_photo_unlocks_viewer on photo_unlocks (viewer_id);

alter table photo_unlocks enable row level security;

create policy photo_unlocks_select_own on photo_unlocks
  for select to authenticated
  using (viewer_id = auth.uid());

-- INSERT solo vía función unlock_photos() (service_role), no directo del cliente,
-- porque implica cobrar monedas de forma atómica.

-- ============================================================================
-- 3. SOLICITUDES DE CONVERSACIÓN, CONVERSACIONES Y MENSAJES
-- ============================================================================

create table conversation_requests (
  id uuid primary key default gen_random_uuid(),
  sender_id uuid not null references profiles (id) on delete cascade,
  receiver_id uuid not null references profiles (id) on delete cascade,
  first_message text not null check (char_length(first_message) between 1 and 1000),
  status text not null default 'pending'
    check (status in ('pending', 'accepted', 'declined', 'expired')),
  created_at timestamptz not null default now(),
  responded_at timestamptz,
  check (sender_id <> receiver_id)
);

create index idx_conversation_requests_receiver on conversation_requests (receiver_id, status, created_at desc);
create index idx_conversation_requests_sender on conversation_requests (sender_id, created_at desc);

alter table conversation_requests enable row level security;

create policy conversation_requests_select_participant on conversation_requests
  for select to authenticated
  using (sender_id = auth.uid() or receiver_id = auth.uid());

-- El INSERT real pasa por la Edge Function start-conversation (rate limit + gasto de
-- créditos de mensaje), pero se deja también una policy de INSERT directo válida para
-- desarrollo/tests: exige que el propio usuario sea el sender.
create policy conversation_requests_insert_own on conversation_requests
  for insert to authenticated
  with check (
    sender_id = auth.uid()
    and not is_blocked_between(auth.uid(), receiver_id)
  );

create policy conversation_requests_update_receiver on conversation_requests
  for update to authenticated
  using (receiver_id = auth.uid())
  with check (receiver_id = auth.uid());

create table conversations (
  id uuid primary key default gen_random_uuid(),
  user_a_id uuid not null references profiles (id) on delete cascade,
  user_b_id uuid not null references profiles (id) on delete cascade,
  source_request_id uuid references conversation_requests (id),
  created_at timestamptz not null default now(),
  last_message_at timestamptz not null default now(),
  archived_by_a boolean not null default false,
  archived_by_b boolean not null default false,
  muted_by_a boolean not null default false,
  muted_by_b boolean not null default false,
  check (user_a_id <> user_b_id),
  unique (user_a_id, user_b_id)
);

create index idx_conversations_user_a on conversations (user_a_id, last_message_at desc);
create index idx_conversations_user_b on conversations (user_b_id, last_message_at desc);

alter table conversations enable row level security;

create policy conversations_select_participant on conversations
  for select to authenticated
  using (user_a_id = auth.uid() or user_b_id = auth.uid());

create policy conversations_update_participant on conversations
  for update to authenticated
  using (user_a_id = auth.uid() or user_b_id = auth.uid())
  with check (user_a_id = auth.uid() or user_b_id = auth.uid());

create table messages (
  id uuid primary key default gen_random_uuid(),
  conversation_id uuid not null references conversations (id) on delete cascade,
  sender_id uuid not null references profiles (id),
  content text check (char_length(content) <= 2000),
  message_type text not null default 'text' check (message_type in ('text', 'image', 'system')),
  image_url text,
  status text not null default 'sent' check (status in ('sent', 'delivered', 'read')),
  created_at timestamptz not null default now(),
  read_at timestamptz,
  check (
    (message_type = 'text' and content is not null)
    or (message_type = 'image' and image_url is not null)
    or message_type = 'system'
  )
);

create index idx_messages_conversation_created on messages (conversation_id, created_at);

alter table messages enable row level security;

create policy messages_select_participant on messages
  for select to authenticated
  using (
    exists (
      select 1 from conversations c
      where c.id = messages.conversation_id
        and (c.user_a_id = auth.uid() or c.user_b_id = auth.uid())
    )
  );

create policy messages_insert_participant on messages
  for insert to authenticated
  with check (
    sender_id = auth.uid()
    and exists (
      select 1 from conversations c
      where c.id = messages.conversation_id
        and (c.user_a_id = auth.uid() or c.user_b_id = auth.uid())
    )
  );

create policy messages_update_participant on messages
  for update to authenticated
  using (
    exists (
      select 1 from conversations c
      where c.id = messages.conversation_id
        and (c.user_a_id = auth.uid() or c.user_b_id = auth.uid())
    )
  )
  with check (
    exists (
      select 1 from conversations c
      where c.id = messages.conversation_id
        and (c.user_a_id = auth.uid() or c.user_b_id = auth.uid())
    )
  );

-- Actualiza last_message_at de la conversación en cada mensaje nuevo (para ordenar la
-- lista de Mensajes por actividad reciente sin tener que hacer MAX(created_at) en cada query).
create or replace function touch_conversation_on_message()
returns trigger
language plpgsql
as $$
begin
  update conversations set last_message_at = new.created_at where id = new.conversation_id;
  return new;
end;
$$;

create trigger trg_messages_touch_conversation
  after insert on messages
  for each row execute function touch_conversation_on_message();

-- Aceptar una solicitud crea la conversación (orden canónico de ids para respetar el
-- UNIQUE(user_a_id, user_b_id) sin duplicados en ambos sentidos) y el primer mensaje.
create or replace function accept_conversation_request(p_request_id uuid)
returns uuid
language plpgsql
security definer
set search_path = public
as $$
declare
  v_request conversation_requests%rowtype;
  v_conversation_id uuid;
  v_user_a uuid;
  v_user_b uuid;
begin
  select * into v_request from conversation_requests where id = p_request_id for update;

  if v_request is null then
    raise exception 'Solicitud no encontrada';
  end if;
  if v_request.receiver_id <> auth.uid() then
    raise exception 'No autorizado para aceptar esta solicitud';
  end if;
  if v_request.status <> 'pending' then
    raise exception 'La solicitud ya no está pendiente';
  end if;

  v_user_a := least(v_request.sender_id, v_request.receiver_id);
  v_user_b := greatest(v_request.sender_id, v_request.receiver_id);

  insert into conversations (user_a_id, user_b_id, source_request_id)
  values (v_user_a, v_user_b, v_request.id)
  on conflict (user_a_id, user_b_id) do update set last_message_at = now()
  returning id into v_conversation_id;

  insert into messages (conversation_id, sender_id, content, message_type)
  values (v_conversation_id, v_request.sender_id, v_request.first_message, 'text');

  update conversation_requests
    set status = 'accepted', responded_at = now()
    where id = p_request_id;

  insert into notifications (profile_id, type, payload)
  values (
    v_request.sender_id,
    'request_accepted',
    jsonb_build_object('conversationId', v_conversation_id, 'byProfileId', auth.uid())
  );

  return v_conversation_id;
end;
$$;

create or replace function decline_conversation_request(p_request_id uuid)
returns void
language plpgsql
security definer
set search_path = public
as $$
begin
  update conversation_requests
    set status = 'declined', responded_at = now()
    where id = p_request_id and receiver_id = auth.uid() and status = 'pending';

  if not found then
    raise exception 'Solicitud no encontrada o no autorizada';
  end if;
end;
$$;

-- Job periódico (a programar con pg_cron o un scheduler externo) para expirar solicitudes
-- sin respuesta tras conversation_request_expiry_days (app_config).
create or replace function expire_stale_conversation_requests()
returns integer
language plpgsql
security definer
set search_path = public
as $$
declare
  v_days integer;
  v_count integer;
begin
  select coalesce((value #>> '{}')::integer, 30) into v_days
    from app_config where key = 'conversation_request_expiry_days';

  update conversation_requests
    set status = 'expired', responded_at = now()
    where status = 'pending'
      and created_at < now() - make_interval(days => coalesce(v_days, 30));

  get diagnostics v_count = row_count;
  return v_count;
end;
$$;

-- ============================================================================
-- 4. SUPER LIKES Y VISTAS DE PERFIL
-- ============================================================================

create table super_likes (
  id uuid primary key default gen_random_uuid(),
  sender_id uuid not null references profiles (id) on delete cascade,
  receiver_id uuid not null references profiles (id) on delete cascade,
  message text check (char_length(message) <= 300),
  is_seen boolean not null default false,
  created_at timestamptz not null default now(),
  check (sender_id <> receiver_id)
);

create index idx_super_likes_receiver on super_likes (receiver_id, created_at desc);
create index idx_super_likes_sender_day on super_likes (sender_id, created_at);

alter table super_likes enable row level security;

create policy super_likes_select_participant on super_likes
  for select to authenticated
  using (sender_id = auth.uid() or receiver_id = auth.uid());

-- INSERT real vía Edge Function send-super-like (valida cupo/gasto de monedas de forma
-- atómica); no se expone policy de INSERT directo para evitar bypass del cobro.

create table profile_views (
  id uuid primary key default gen_random_uuid(),
  viewer_id uuid not null references profiles (id) on delete cascade,
  viewed_id uuid not null references profiles (id) on delete cascade,
  created_at timestamptz not null default now(),
  check (viewer_id <> viewed_id)
);

create index idx_profile_views_viewed on profile_views (viewed_id, created_at desc);
create index idx_profile_views_viewer on profile_views (viewer_id, created_at desc);

alter table profile_views enable row level security;

-- El dueño del perfil ve quién le vio ("Quién te ha visto" — brief sección 7);
-- el visor también puede ver su propio historial.
create policy profile_views_select on profile_views
  for select to authenticated
  using (viewed_id = auth.uid() or viewer_id = auth.uid());

create policy profile_views_insert_own on profile_views
  for insert to authenticated
  with check (viewer_id = auth.uid());

-- admirer_reveals: desbloqueo de la identidad de un admirador secreto (brief sección 8).
create table admirer_reveals (
  id uuid primary key default gen_random_uuid(),
  profile_id uuid not null references profiles (id) on delete cascade,
  revealed_viewer_id uuid not null references profiles (id) on delete cascade,
  method text not null check (method in ('coins', 'premium', 'admin_grant')),
  created_at timestamptz not null default now(),
  unique (profile_id, revealed_viewer_id)
);

alter table admirer_reveals enable row level security;

create policy admirer_reveals_select_own on admirer_reveals
  for select to authenticated
  using (profile_id = auth.uid());

-- INSERT solo vía función reveal_secret_admirer() (cobra monedas atómicamente).

-- ============================================================================
-- 5. ECONOMÍA: MONEDAS Y CRÉDITOS DE MENSAJE
-- ============================================================================

create table coin_wallets (
  profile_id uuid primary key references profiles (id) on delete cascade,
  balance integer not null default 0 check (balance >= 0),
  updated_at timestamptz not null default now()
);

alter table coin_wallets enable row level security;

create policy coin_wallets_select_own on coin_wallets
  for select to authenticated
  using (profile_id = auth.uid());
-- Sin policy de INSERT/UPDATE/DELETE para "authenticated": el saldo solo lo muta
-- service_role a través de las funciones grant_coins/spend_coins.

create table coin_transactions (
  id uuid primary key default gen_random_uuid(),
  profile_id uuid not null references profiles (id) on delete cascade,
  amount integer not null check (amount <> 0),
  balance_after integer not null check (balance_after >= 0),
  reason text not null check (reason in (
    'daily_login', 'streak_bonus', 'purchase', 'super_like_sent', 'super_like_purchase',
    'photo_unlock', 'secret_admirer_reveal', 'admin_grant', 'boost_purchase', 'refund'
  )),
  reference_id uuid,
  created_at timestamptz not null default now()
);

create index idx_coin_transactions_profile on coin_transactions (profile_id, created_at desc);

alter table coin_transactions enable row level security;

create policy coin_transactions_select_own on coin_transactions
  for select to authenticated
  using (profile_id = auth.uid());

create table message_credit_wallets (
  profile_id uuid primary key references profiles (id) on delete cascade,
  balance integer not null default 0 check (balance >= 0),
  updated_at timestamptz not null default now()
);

alter table message_credit_wallets enable row level security;

create policy message_credit_wallets_select_own on message_credit_wallets
  for select to authenticated
  using (profile_id = auth.uid());

create table message_credit_transactions (
  id uuid primary key default gen_random_uuid(),
  profile_id uuid not null references profiles (id) on delete cascade,
  amount integer not null check (amount <> 0),
  balance_after integer not null check (balance_after >= 0),
  reason text not null check (reason in (
    'signup_grant', 'conversation_started', 'streak_bonus', 'purchase', 'admin_grant', 'refund'
  )),
  reference_id uuid,
  created_at timestamptz not null default now()
);

create index idx_message_credit_transactions_profile on message_credit_transactions (profile_id, created_at desc);

alter table message_credit_transactions enable row level security;

create policy message_credit_transactions_select_own on message_credit_transactions
  for select to authenticated
  using (profile_id = auth.uid());

-- ----------------------------------------------------------------------------
-- Funciones atómicas de economía (SECURITY DEFINER — solo se llaman desde Edge
-- Functions con service_role, o directamente para grants administrativos).
-- Replican la lógica pura de packages/shared/src/economy.ts (applyBalanceDelta).
-- ----------------------------------------------------------------------------

create or replace function grant_coins(p_profile_id uuid, p_amount integer, p_reason text, p_reference_id uuid default null)
returns integer
language plpgsql
security definer
set search_path = public
as $$
declare
  v_balance integer;
begin
  if p_amount <= 0 then
    raise exception 'grant_coins requiere un importe positivo';
  end if;

  insert into coin_wallets (profile_id, balance) values (p_profile_id, 0)
    on conflict (profile_id) do nothing;

  update coin_wallets set balance = balance + p_amount, updated_at = now()
    where profile_id = p_profile_id
    returning balance into v_balance;

  insert into coin_transactions (profile_id, amount, balance_after, reason, reference_id)
    values (p_profile_id, p_amount, v_balance, p_reason, p_reference_id);

  return v_balance;
end;
$$;

create or replace function spend_coins(p_profile_id uuid, p_amount integer, p_reason text, p_reference_id uuid default null)
returns integer
language plpgsql
security definer
set search_path = public
as $$
declare
  v_balance integer;
begin
  if p_amount <= 0 then
    raise exception 'spend_coins requiere un importe positivo';
  end if;

  update coin_wallets set balance = balance - p_amount, updated_at = now()
    where profile_id = p_profile_id and balance >= p_amount
    returning balance into v_balance;

  if not found then
    raise exception 'Saldo de monedas insuficiente';
  end if;

  insert into coin_transactions (profile_id, amount, balance_after, reason, reference_id)
    values (p_profile_id, -p_amount, v_balance, p_reason, p_reference_id);

  return v_balance;
end;
$$;

create or replace function grant_message_credits(p_profile_id uuid, p_amount integer, p_reason text, p_reference_id uuid default null)
returns integer
language plpgsql
security definer
set search_path = public
as $$
declare
  v_balance integer;
begin
  if p_amount <= 0 then
    raise exception 'grant_message_credits requiere un importe positivo';
  end if;

  insert into message_credit_wallets (profile_id, balance) values (p_profile_id, 0)
    on conflict (profile_id) do nothing;

  update message_credit_wallets set balance = balance + p_amount, updated_at = now()
    where profile_id = p_profile_id
    returning balance into v_balance;

  insert into message_credit_transactions (profile_id, amount, balance_after, reason, reference_id)
    values (p_profile_id, p_amount, v_balance, p_reason, p_reference_id);

  return v_balance;
end;
$$;

create or replace function spend_message_credit(p_profile_id uuid, p_reason text default 'conversation_started', p_reference_id uuid default null)
returns integer
language plpgsql
security definer
set search_path = public
as $$
declare
  v_balance integer;
begin
  update message_credit_wallets set balance = balance - 1, updated_at = now()
    where profile_id = p_profile_id and balance >= 1
    returning balance into v_balance;

  if not found then
    raise exception 'No quedan créditos de mensaje disponibles';
  end if;

  insert into message_credit_transactions (profile_id, amount, balance_after, reason, reference_id)
    values (p_profile_id, -1, v_balance, p_reason, p_reference_id);

  return v_balance;
end;
$$;

create or replace function unlock_photos(p_target_profile_id uuid, p_method text)
returns void
language plpgsql
security definer
set search_path = public
as $$
declare
  v_cost integer;
  v_viewer_premium boolean;
begin
  select is_premium into v_viewer_premium from profiles where id = auth.uid();

  if p_method = 'premium' then
    if not coalesce(v_viewer_premium, false) then
      raise exception 'Se requiere Premium para este método de desbloqueo';
    end if;
  elsif p_method = 'coins' then
    select coalesce((value #>> '{}')::integer, 50) into v_cost
      from app_config where key = 'photo_unlock_coin_cost';
    perform spend_coins(auth.uid(), v_cost, 'photo_unlock', p_target_profile_id);
  else
    raise exception 'Método de desbloqueo no soportado: %', p_method;
  end if;

  insert into photo_unlocks (viewer_id, target_profile_id, method)
    values (auth.uid(), p_target_profile_id, p_method)
    on conflict (viewer_id, target_profile_id) do nothing;
end;
$$;

create or replace function reveal_secret_admirer(p_admirer_profile_id uuid)
returns void
language plpgsql
security definer
set search_path = public
as $$
declare
  v_cost integer;
  v_is_premium boolean;
begin
  select is_premium into v_is_premium from profiles where id = auth.uid();

  if not coalesce(v_is_premium, false) then
    select coalesce((value #>> '{}')::integer, 30) into v_cost
      from app_config where key = 'secret_admirer_reveal_coin_cost';
    perform spend_coins(auth.uid(), v_cost, 'secret_admirer_reveal', p_admirer_profile_id);
  end if;

  insert into admirer_reveals (profile_id, revealed_viewer_id, method)
    values (auth.uid(), p_admirer_profile_id, case when v_is_premium then 'premium' else 'coins' end)
    on conflict (profile_id, revealed_viewer_id) do nothing;
end;
$$;

-- ============================================================================
-- 6. RACHA DIARIA DE 7 DÍAS
-- ============================================================================

create table daily_streaks (
  profile_id uuid primary key references profiles (id) on delete cascade,
  current_streak integer not null default 0,
  longest_streak integer not null default 0,
  last_checkin_date date,
  next_reward_day smallint not null default 1 check (next_reward_day between 1 and 7),
  updated_at timestamptz not null default now()
);

alter table daily_streaks enable row level security;

create policy daily_streaks_select_own on daily_streaks
  for select to authenticated
  using (profile_id = auth.uid());

create table daily_streak_claims (
  id uuid primary key default gen_random_uuid(),
  profile_id uuid not null references profiles (id) on delete cascade,
  day_number smallint not null check (day_number between 1 and 7),
  coins_awarded integer not null default 0,
  super_likes_awarded integer not null default 0,
  message_credits_awarded integer not null default 0,
  claimed_at timestamptz not null default now()
);

create index idx_daily_streak_claims_profile on daily_streak_claims (profile_id, claimed_at desc);

alter table daily_streak_claims enable row level security;

create policy daily_streak_claims_select_own on daily_streak_claims
  for select to authenticated
  using (profile_id = auth.uid());

-- Nota: el cálculo del día de racha (consecutivo / roto / ciclo 1-7) replica
-- exactamente computeStreakCheckin() de packages/shared/src/economy.ts — mantener
-- ambas implementaciones sincronizadas si cambia la regla de negocio.
create or replace function claim_daily_streak()
returns jsonb
language plpgsql
security definer
set search_path = public
as $$
declare
  v_state daily_streaks%rowtype;
  v_today date := current_date;
  v_days_since integer;
  v_is_consecutive boolean;
  v_claimed_day smallint;
  v_next_day smallint;
  v_reward jsonb;
  v_coins integer;
  v_super_likes integer;
  v_message_credits integer;
  v_new_balance integer;
begin
  select * into v_state from daily_streaks where profile_id = auth.uid() for update;

  if v_state is null then
    insert into daily_streaks (profile_id) values (auth.uid())
      returning * into v_state;
  end if;

  if v_state.last_checkin_date = v_today then
    raise exception 'Ya se ha reclamado la recompensa diaria de hoy';
  end if;

  v_days_since := case when v_state.last_checkin_date is null then null
                        else v_today - v_state.last_checkin_date end;
  v_is_consecutive := (v_days_since = 1);
  v_claimed_day := case when v_is_consecutive then v_state.next_reward_day else 1 end;
  v_next_day := ((v_claimed_day) % 7) + 1;

  select value into v_reward from app_config where key = 'streak_rewards';
  v_reward := (
    select r from jsonb_array_elements(v_reward) r where (r ->> 'day')::smallint = v_claimed_day
  );

  if v_reward is null then
    raise exception 'No hay recompensa configurada para el día % de la racha', v_claimed_day;
  end if;

  v_coins := coalesce((v_reward ->> 'coins')::integer, 0);
  v_super_likes := coalesce((v_reward ->> 'superLikes')::integer, 0);
  v_message_credits := coalesce((v_reward ->> 'messageCredits')::integer, 0);

  update daily_streaks set
    current_streak = case when v_is_consecutive then current_streak + 1 else 1 end,
    longest_streak = greatest(longest_streak, case when v_is_consecutive then current_streak + 1 else 1 end),
    last_checkin_date = v_today,
    next_reward_day = v_next_day,
    updated_at = now()
  where profile_id = auth.uid();

  insert into daily_streak_claims (profile_id, day_number, coins_awarded, super_likes_awarded, message_credits_awarded)
    values (auth.uid(), v_claimed_day, v_coins, v_super_likes, v_message_credits);

  if v_coins > 0 then
    perform grant_coins(auth.uid(), v_coins, 'streak_bonus');
  end if;
  if v_message_credits > 0 then
    perform grant_message_credits(auth.uid(), v_message_credits, 'streak_bonus');
  end if;
  -- Los Super Likes de racha se acreditan como saldo extra vía coin_transactions-like
  -- ledger dedicado: se representan como monedas "virtuales" 1:1 en super_like_credits
  -- para no crear otra tabla de wallet; ver super_like_credits más abajo.
  if v_super_likes > 0 then
    perform grant_super_like_credits(auth.uid(), v_super_likes, 'streak_bonus');
  end if;

  return jsonb_build_object(
    'day', v_claimed_day,
    'coins', v_coins,
    'superLikes', v_super_likes,
    'messageCredits', v_message_credits,
    'currentStreak', (select current_streak from daily_streaks where profile_id = auth.uid())
  );
end;
$$;

-- ----------------------------------------------------------------------------
-- super_like_credits: saldo de Super Likes comprados/ganados (independiente del cupo
-- gratuito diario, que se calcula contando filas de super_likes de hoy).
-- ----------------------------------------------------------------------------
create table super_like_credit_wallets (
  profile_id uuid primary key references profiles (id) on delete cascade,
  balance integer not null default 0 check (balance >= 0),
  updated_at timestamptz not null default now()
);

alter table super_like_credit_wallets enable row level security;

create policy super_like_credit_wallets_select_own on super_like_credit_wallets
  for select to authenticated
  using (profile_id = auth.uid());

create or replace function grant_super_like_credits(p_profile_id uuid, p_amount integer, p_reason text default 'admin_grant')
returns integer
language plpgsql
security definer
set search_path = public
as $$
declare
  v_balance integer;
begin
  if p_amount <= 0 then
    raise exception 'grant_super_like_credits requiere un importe positivo';
  end if;

  insert into super_like_credit_wallets (profile_id, balance) values (p_profile_id, 0)
    on conflict (profile_id) do nothing;

  update super_like_credit_wallets set balance = balance + p_amount, updated_at = now()
    where profile_id = p_profile_id
    returning balance into v_balance;

  return v_balance;
end;
$$;

-- Simétrica a spend_coins/spend_message_credit — evita que el cliente tenga que "gastar"
-- llamando a grant_ con un importe negativo (inconsistente con el resto de la economía).
create or replace function spend_super_like_credit(p_profile_id uuid, p_reason text default 'super_like_sent')
returns integer
language plpgsql
security definer
set search_path = public
as $$
declare
  v_balance integer;
begin
  update super_like_credit_wallets set balance = balance - 1, updated_at = now()
    where profile_id = p_profile_id and balance >= 1
    returning balance into v_balance;

  if not found then
    raise exception 'No quedan Super Likes de racha disponibles';
  end if;

  return v_balance;
end;
$$;

-- ============================================================================
-- 7. PREMIUM
-- ============================================================================

create table premium_subscriptions (
  id uuid primary key default gen_random_uuid(),
  profile_id uuid not null references profiles (id) on delete cascade,
  plan text not null check (plan in ('monthly', 'yearly')),
  status text not null check (status in ('active', 'canceled', 'expired', 'in_grace_period')),
  store text not null check (store in ('ios', 'android', 'stripe', 'admin_grant')),
  external_subscription_id text,
  started_at timestamptz not null default now(),
  current_period_end timestamptz not null,
  canceled_at timestamptz
);

create index idx_premium_subscriptions_profile on premium_subscriptions (profile_id, status);

alter table premium_subscriptions enable row level security;

create policy premium_subscriptions_select_own on premium_subscriptions
  for select to authenticated
  using (profile_id = auth.uid());

-- Mantiene profiles.is_premium/premium_until sincronizados con la suscripción activa
-- más reciente, para no tener que hacer JOIN en cada consulta de gating de features.
create or replace function sync_profile_premium_flag()
returns trigger
language plpgsql
as $$
begin
  update profiles set
    is_premium = exists (
      select 1 from premium_subscriptions ps
      where ps.profile_id = new.profile_id and ps.status = 'active' and ps.current_period_end > now()
    ),
    premium_until = (
      select max(current_period_end) from premium_subscriptions ps
      where ps.profile_id = new.profile_id and ps.status in ('active', 'in_grace_period')
    )
  where id = new.profile_id;
  return new;
end;
$$;

create trigger trg_premium_subscriptions_sync
  after insert or update on premium_subscriptions
  for each row execute function sync_profile_premium_flag();

-- profile_boosts: modelo de datos preparado para la función "Boost" mencionada como
-- futura en el brief (sección 15); sin UI en este MVP — ver docs/07-roadmap-and-scaling.md.
create table profile_boosts (
  id uuid primary key default gen_random_uuid(),
  profile_id uuid not null references profiles (id) on delete cascade,
  starts_at timestamptz not null default now(),
  ends_at timestamptz not null,
  coin_cost integer not null default 0
);

alter table profile_boosts enable row level security;

create policy profile_boosts_select_own on profile_boosts
  for select to authenticated
  using (profile_id = auth.uid());

-- ============================================================================
-- 8. NOTIFICACIONES
-- ============================================================================

create table push_tokens (
  id uuid primary key default gen_random_uuid(),
  profile_id uuid not null references profiles (id) on delete cascade,
  expo_push_token text not null,
  platform text not null check (platform in ('ios', 'android', 'web')),
  created_at timestamptz not null default now(),
  last_used_at timestamptz not null default now(),
  unique (profile_id, expo_push_token)
);

alter table push_tokens enable row level security;

create policy push_tokens_owner_all on push_tokens
  for all to authenticated
  using (profile_id = auth.uid())
  with check (profile_id = auth.uid());

create table notifications (
  id uuid primary key default gen_random_uuid(),
  profile_id uuid not null references profiles (id) on delete cascade,
  type text not null check (type in (
    'new_message', 'new_request', 'request_accepted', 'super_like_received',
    'profile_viewed', 'daily_reward_ready', 'streak_at_risk', 'secret_admirer', 'promotion'
  )),
  payload jsonb not null default '{}'::jsonb,
  is_read boolean not null default false,
  created_at timestamptz not null default now()
);

create index idx_notifications_profile on notifications (profile_id, is_read, created_at desc);

alter table notifications enable row level security;

create policy notifications_select_own on notifications
  for select to authenticated
  using (profile_id = auth.uid());

create policy notifications_update_own on notifications
  for update to authenticated
  using (profile_id = auth.uid())
  with check (profile_id = auth.uid());

-- ============================================================================
-- 9. SEGURIDAD: REPORTES, BLOQUEOS, MODERACIÓN
-- ============================================================================
-- Nota: la tabla `blocks` ya se creó más arriba (sección 1), justo antes de las
-- políticas de `profiles`, porque estas la necesitan.

create table reports (
  id uuid primary key default gen_random_uuid(),
  reporter_id uuid not null references profiles (id) on delete cascade,
  reported_id uuid not null references profiles (id) on delete cascade,
  reason text not null check (reason in (
    'spam', 'fake_profile', 'inappropriate_content', 'harassment', 'underage', 'other'
  )),
  details text check (char_length(details) <= 1000),
  related_message_id uuid references messages (id),
  status text not null default 'pending'
    check (status in ('pending', 'reviewed', 'actioned', 'dismissed')),
  reviewed_by uuid,
  reviewed_at timestamptz,
  created_at timestamptz not null default now(),
  check (reporter_id <> reported_id)
);

create index idx_reports_status on reports (status, created_at desc);
create index idx_reports_reported on reports (reported_id);

alter table reports enable row level security;

-- El denunciante ve sus propios reportes; el denunciado NO puede ver que fue reportado
-- (evita represalias). El panel admin usa service_role, que ignora RLS.
create policy reports_select_own on reports
  for select to authenticated
  using (reporter_id = auth.uid());

create policy reports_insert_own on reports
  for insert to authenticated
  with check (reporter_id = auth.uid());

-- Reportar por 'underage' o 'harassment' pone el perfil denunciado en revisión automática
-- (mitigación inmediata de visibilidad, sin eliminar la cuenta sin revisión humana).
create or replace function flag_profile_on_severe_report()
returns trigger
language plpgsql
security definer
set search_path = public
as $$
begin
  if new.reason in ('underage', 'harassment') then
    update profiles set status = 'under_review' where id = new.reported_id and status = 'active';
  end if;
  return new;
end;
$$;

create trigger trg_reports_flag_severe
  after insert on reports
  for each row execute function flag_profile_on_severe_report();

create table suspicious_activity_flags (
  id uuid primary key default gen_random_uuid(),
  profile_id uuid not null references profiles (id) on delete cascade,
  flag_type text not null,
  score smallint not null default 1,
  details jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  resolved boolean not null default false
);

create index idx_suspicious_activity_profile on suspicious_activity_flags (profile_id, resolved);

alter table suspicious_activity_flags enable row level security;
-- Sin policies para "authenticated": tabla de uso exclusivo de service_role/admin.

-- ============================================================================
-- 10. CONFIGURACIÓN DE NEGOCIO (app_config) Y RATE LIMITING
-- ============================================================================

create table app_config (
  key text primary key,
  value jsonb not null,
  description text,
  updated_by uuid,
  updated_at timestamptz not null default now()
);

alter table app_config enable row level security;

create policy app_config_select_all on app_config
  for select to authenticated
  using (true);
-- Sin policy de UPDATE/INSERT/DELETE para authenticated: solo el panel admin
-- (service_role) puede escribir configuración. Ver supabase/seed.sql para los defaults.

create table rate_limit_events (
  id uuid primary key default gen_random_uuid(),
  profile_id uuid not null references profiles (id) on delete cascade,
  action_type text not null,
  created_at timestamptz not null default now()
);

create index idx_rate_limit_events_lookup on rate_limit_events (profile_id, action_type, created_at desc);

alter table rate_limit_events enable row level security;
-- Sin policies para "authenticated": solo se escribe/lee desde funciones SECURITY DEFINER.

-- Antispam (brief sección 17): cuenta eventos de una acción en una ventana de tiempo y
-- registra el intento si no se ha superado el límite. Las cuentas nuevas (< new_account_
-- grace_hours) usan un límite reducido por new_account_rate_limit_factor — misma regla que
-- effectiveRateLimit() en packages/shared/src/economy.ts.
create or replace function check_and_record_rate_limit(
  p_profile_id uuid,
  p_action_type text,
  p_base_limit integer,
  p_window interval
)
returns boolean
language plpgsql
security definer
set search_path = public
as $$
declare
  v_account_age_hours numeric;
  v_grace_hours numeric;
  v_factor numeric;
  v_effective_limit integer;
  v_current_count integer;
begin
  select extract(epoch from (now() - created_at)) / 3600 into v_account_age_hours
    from profiles where id = p_profile_id;

  select coalesce((value #>> '{}')::numeric, 48) into v_grace_hours
    from app_config where key = 'new_account_grace_hours';
  select coalesce((value #>> '{}')::numeric, 0.3) into v_factor
    from app_config where key = 'new_account_rate_limit_factor';

  if v_account_age_hours is not null and v_account_age_hours < coalesce(v_grace_hours, 48) then
    v_effective_limit := greatest(1, floor(p_base_limit * coalesce(v_factor, 0.3))::integer);
  else
    v_effective_limit := p_base_limit;
  end if;

  select count(*) into v_current_count
    from rate_limit_events
    where profile_id = p_profile_id
      and action_type = p_action_type
      and created_at > now() - p_window;

  if v_current_count >= v_effective_limit then
    return false;
  end if;

  insert into rate_limit_events (profile_id, action_type) values (p_profile_id, p_action_type);
  return true;
end;
$$;

-- Limpieza periódica (a programar) de eventos antiguos para no crecer sin límite.
create or replace function cleanup_old_rate_limit_events()
returns integer
language plpgsql
security definer
set search_path = public
as $$
declare
  v_count integer;
begin
  delete from rate_limit_events where created_at < now() - interval '7 days';
  get diagnostics v_count = row_count;
  return v_count;
end;
$$;

-- ============================================================================
-- 11. PANEL DE ADMINISTRACIÓN
-- ============================================================================

create table admin_users (
  id uuid primary key references auth.users (id) on delete cascade,
  role text not null check (role in ('superadmin', 'moderator', 'support')),
  created_at timestamptz not null default now()
);

alter table admin_users enable row level security;
-- Sin policies para "authenticated": el panel admin usa service_role exclusivamente,
-- de modo que ni siquiera un admin autenticado por el cliente público puede leer/escribir
-- esta tabla directamente vía la API pública.

create table audit_log (
  id uuid primary key default gen_random_uuid(),
  actor_admin_id uuid references admin_users (id),
  action text not null,
  target_table text not null,
  target_id uuid,
  before jsonb,
  after jsonb,
  created_at timestamptz not null default now()
);

create index idx_audit_log_target on audit_log (target_table, target_id, created_at desc);

alter table audit_log enable row level security;
-- Solo service_role (panel admin) lee/escribe.

-- ============================================================================
-- 12. ALTA DE USUARIO: crea perfil + wallets + preferencias en un solo trigger
-- (se invoca tras el INSERT en profiles que hace la app al terminar el paso 1 del
-- onboarding; auth.users ya existe gracias a Supabase Auth).
-- ============================================================================

create or replace function handle_new_profile()
returns trigger
language plpgsql
security definer
set search_path = public
as $$
declare
  v_starting_credits integer;
begin
  insert into coin_wallets (profile_id, balance) values (new.id, 0)
    on conflict (profile_id) do nothing;
  insert into super_like_credit_wallets (profile_id, balance) values (new.id, 0)
    on conflict (profile_id) do nothing;
  insert into user_preferences (profile_id) values (new.id)
    on conflict (profile_id) do nothing;
  insert into notification_preferences (profile_id) values (new.id)
    on conflict (profile_id) do nothing;
  insert into daily_streaks (profile_id) values (new.id)
    on conflict (profile_id) do nothing;

  select coalesce((value #>> '{}')::integer, 100) into v_starting_credits
    from app_config where key = 'starting_message_credits';

  insert into message_credit_wallets (profile_id, balance) values (new.id, 0)
    on conflict (profile_id) do nothing;
  perform grant_message_credits(new.id, coalesce(v_starting_credits, 100), 'signup_grant');

  return new;
end;
$$;

create trigger trg_profiles_bootstrap
  after insert on profiles
  for each row execute function handle_new_profile();
