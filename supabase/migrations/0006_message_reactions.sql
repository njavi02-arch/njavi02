-- ============================================================================
-- Orbita — reacciones a mensajes de chat.
--
-- Siguiente elemento del ROADMAP DINÁMICO en PRODUCT_BRAIN.md: Wizz permite reaccionar a
-- mensajes al instante (ver PRODUCT_BRAIN.md → INVESTIGACIÓN). Responde a la regla de
-- producto "¿mejora el chat?" (sección 46 del brief). Una reacción por persona y mensaje
-- (como un tapback de iMessage/WhatsApp), no múltiples emojis acumulables — más simple y
-- suficiente para el caso de uso.
-- ============================================================================

create table message_reactions (
  id uuid primary key default gen_random_uuid(),
  message_id uuid not null references messages (id) on delete cascade,
  profile_id uuid not null references profiles (id) on delete cascade,
  emoji text not null check (emoji in ('❤️', '😂', '👍', '😮', '😢', '🔥')),
  created_at timestamptz not null default now(),
  unique (message_id, profile_id)
);

create index idx_message_reactions_message on message_reactions (message_id);

alter table message_reactions enable row level security;

-- Mismas reglas que messages: solo los participantes de la conversación del mensaje
-- pueden ver/reaccionar.
create policy message_reactions_select_participant on message_reactions
  for select to authenticated
  using (
    exists (
      select 1 from messages m
      join conversations c on c.id = m.conversation_id
      where m.id = message_reactions.message_id
        and (c.user_a_id = auth.uid() or c.user_b_id = auth.uid())
    )
  );

create policy message_reactions_insert_participant on message_reactions
  for insert to authenticated
  with check (
    profile_id = auth.uid()
    and exists (
      select 1 from messages m
      join conversations c on c.id = m.conversation_id
      where m.id = message_reactions.message_id
        and (c.user_a_id = auth.uid() or c.user_b_id = auth.uid())
    )
  );

create policy message_reactions_update_own on message_reactions
  for update to authenticated
  using (profile_id = auth.uid())
  with check (profile_id = auth.uid());

create policy message_reactions_delete_own on message_reactions
  for delete to authenticated
  using (profile_id = auth.uid());
