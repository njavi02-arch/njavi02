-- ============================================================================
-- Orbita — exportación de datos personales (derecho de acceso/portabilidad RGPD, ver
-- docs/06-security-and-privacy.md §6, que ya documentaba esto como "pendiente de construir
-- el endpoint concreto"). Siguiente ítem del ROADMAP DINÁMICO tras el filtro de verificados.
--
-- export_my_data() es SECURITY DEFINER pero SIEMPRE opera sobre auth.uid() — nunca recibe
-- un profile_id como parámetro, así que no hay forma de que un usuario autenticado exporte
-- los datos de otra persona (a diferencia de las funciones de economía, que sí reciben un
-- id de receptor porque actúan sobre OTRO perfil).
--
-- Alcance: todo lo que un usuario razonablemente reconocería como "mis datos" — perfil,
-- fotos, intereses, prompts, preferencias, economía (saldos + historial de transacciones),
-- racha, conversaciones/mensajes en los que participa, solicitudes de conversación enviadas
-- y recibidas, reportes que ha presentado, bloqueos que ha creado, solicitudes de
-- verificación y boosts comprados. Deliberadamente NO incluye push_tokens (son credenciales
-- técnicas del dispositivo, no datos personales en el sentido del RGPD) ni los reportes
-- presentados POR OTROS contra este usuario (para no exponer quién le reportó — mismo
-- principio de "sin represalias" que ya aplica la policy reports_select_own).
-- ============================================================================

create or replace function export_my_data()
returns jsonb
language plpgsql
security definer
set search_path = public
stable
as $$
declare
  v_uid uuid := auth.uid();
  v_result jsonb;
begin
  if v_uid is null then
    raise exception 'Debes iniciar sesión para exportar tus datos';
  end if;

  select jsonb_build_object(
    'exported_at', now(),
    'profile', (select to_jsonb(p) from profiles p where p.id = v_uid),
    'photos', (select coalesce(jsonb_agg(to_jsonb(ph) order by ph.position), '[]'::jsonb)
               from photos ph where ph.profile_id = v_uid),
    'interests', (select coalesce(jsonb_agg(i.name), '[]'::jsonb)
                  from profile_interests pi join interests i on i.id = pi.interest_id
                  where pi.profile_id = v_uid),
    'prompts', (select coalesce(jsonb_agg(to_jsonb(pp) order by pp.position), '[]'::jsonb)
                from profile_prompts pp where pp.profile_id = v_uid),
    'discovery_preferences', (select to_jsonb(up) from user_preferences up where up.profile_id = v_uid),
    'notification_preferences', (select to_jsonb(np) from notification_preferences np where np.profile_id = v_uid),
    'wallets', jsonb_build_object(
      'coins', (select balance from coin_wallets where profile_id = v_uid),
      'message_credits', (select balance from message_credit_wallets where profile_id = v_uid),
      'super_like_credits', (select balance from super_like_credit_wallets where profile_id = v_uid)
    ),
    'coin_transactions', (select coalesce(jsonb_agg(to_jsonb(ct) order by ct.created_at), '[]'::jsonb)
                          from coin_transactions ct where ct.profile_id = v_uid),
    'message_credit_transactions', (select coalesce(jsonb_agg(to_jsonb(mct) order by mct.created_at), '[]'::jsonb)
                                    from message_credit_transactions mct where mct.profile_id = v_uid),
    'daily_streak', (select to_jsonb(ds) from daily_streaks ds where ds.profile_id = v_uid),
    'daily_streak_claims', (select coalesce(jsonb_agg(to_jsonb(dsc) order by dsc.claimed_at), '[]'::jsonb)
                            from daily_streak_claims dsc where dsc.profile_id = v_uid),
    'conversations', (select coalesce(jsonb_agg(jsonb_build_object(
                        'id', c.id,
                        'other_profile_id', case when c.user_a_id = v_uid then c.user_b_id else c.user_a_id end,
                        'created_at', c.created_at,
                        'last_message_at', c.last_message_at,
                        'messages', (select coalesce(jsonb_agg(to_jsonb(m) order by m.created_at), '[]'::jsonb)
                                    from messages m where m.conversation_id = c.id)
                      )), '[]'::jsonb)
                      from conversations c where c.user_a_id = v_uid or c.user_b_id = v_uid),
    'conversation_requests_sent', (select coalesce(jsonb_agg(to_jsonb(cr) order by cr.created_at), '[]'::jsonb)
                                   from conversation_requests cr where cr.sender_id = v_uid),
    'conversation_requests_received', (select coalesce(jsonb_agg(to_jsonb(cr) order by cr.created_at), '[]'::jsonb)
                                       from conversation_requests cr where cr.receiver_id = v_uid),
    'super_likes_sent', (select coalesce(jsonb_agg(to_jsonb(sl) order by sl.created_at), '[]'::jsonb)
                         from super_likes sl where sl.sender_id = v_uid),
    'reports_filed', (select coalesce(jsonb_agg(to_jsonb(r) order by r.created_at), '[]'::jsonb)
                      from reports r where r.reporter_id = v_uid),
    'blocks_created', (select coalesce(jsonb_agg(to_jsonb(b) order by b.created_at), '[]'::jsonb)
                       from blocks b where b.blocker_id = v_uid),
    'verification_requests', (select coalesce(jsonb_agg(to_jsonb(vr) order by vr.created_at), '[]'::jsonb)
                              from verification_requests vr where vr.profile_id = v_uid),
    'boosts_purchased', (select coalesce(jsonb_agg(to_jsonb(pb) order by pb.starts_at), '[]'::jsonb)
                         from profile_boosts pb where pb.profile_id = v_uid)
  ) into v_result;

  return v_result;
end;
$$;

grant execute on function export_my_data() to authenticated;
