-- ============================================================================
-- Valores por defecto de app_config — deben coincidir con
-- packages/shared/src/config-defaults.ts (DEFAULT_APP_CONFIG). Si cambias un valor
-- aquí para tu entorno, no hace falta tocar el código: el panel admin y la app leen
-- esta tabla en caliente.
-- ============================================================================

insert into app_config (key, value, description) values
  ('public_photos_count', '3', 'Nº de fotos siempre visibles antes de desbloquear el resto'),
  ('max_photos_count', '10', 'Máximo de fotos por perfil'),
  ('starting_message_credits', '100', 'Créditos de mensaje al completar el registro'),
  ('super_like_daily_free', '1', 'Super Likes gratis por día'),
  ('super_like_coin_cost', '20', 'Coste en monedas de un Super Like extra'),
  ('photo_unlock_coin_cost', '50', 'Coste en monedas de desbloquear el paquete de fotos ocultas de un perfil'),
  ('secret_admirer_reveal_coin_cost', '30', 'Coste en monedas de revelar la identidad de un admirador secreto'),
  ('daily_login_coins', '10', 'Monedas por abrir la app cada día (fuera de racha)'),
  ('streak_rewards', '[
    {"day": 1, "coins": 10, "superLikes": 0, "messageCredits": 0, "isSpecial": false, "label": "Día 1"},
    {"day": 2, "coins": 15, "superLikes": 0, "messageCredits": 0, "isSpecial": false, "label": "Día 2"},
    {"day": 3, "coins": 20, "superLikes": 0, "messageCredits": 0, "isSpecial": false, "label": "Día 3"},
    {"day": 4, "coins": 0, "superLikes": 5, "messageCredits": 0, "isSpecial": true, "label": "Día 4 · Especial"},
    {"day": 5, "coins": 25, "superLikes": 0, "messageCredits": 0, "isSpecial": false, "label": "Día 5"},
    {"day": 6, "coins": 30, "superLikes": 0, "messageCredits": 0, "isSpecial": false, "label": "Día 6"},
    {"day": 7, "coins": 0, "superLikes": 0, "messageCredits": 50, "isSpecial": true, "label": "Día 7 · Gran recompensa"}
  ]', 'Recompensas de la racha diaria de 7 días'),
  ('new_conversation_rate_limit_per_hour', '20', 'Máx. solicitudes de conversación nuevas por hora'),
  ('new_conversation_rate_limit_per_day', '60', 'Máx. solicitudes de conversación nuevas por día'),
  ('new_account_rate_limit_factor', '0.3', 'Multiplicador de límites para cuentas nuevas'),
  ('new_account_grace_hours', '48', 'Horas tras el registro en las que aplica el límite reducido'),
  ('report_rate_limit_per_day', '10', 'Máx. reportes emitidos por día'),
  ('photo_upload_rate_limit_per_day', '10', 'Máx. subidas/cambios de foto por día'),
  ('min_age', '18', 'Edad mínima para registrarse'),
  ('conversation_request_expiry_days', '30', 'Días hasta expirar una solicitud sin respuesta'),
  ('banned_words', '[]', 'Palabras prohibidas en bio/primer mensaje (filtro básico anti-abuso)'),
  ('premium_price_monthly_cents', '999', 'Precio Premium mensual en céntimos'),
  ('premium_price_yearly_cents', '5999', 'Precio Premium anual en céntimos'),
  ('premium_currency', '"EUR"', 'Moneda de los precios Premium')
on conflict (key) do nothing;

-- Intereses de ejemplo para poblar el onboarding (chips seleccionables).
insert into interests (name, category) values
  ('Música', 'Cultura'), ('Cine', 'Cultura'), ('Series', 'Cultura'), ('Lectura', 'Cultura'),
  ('Viajar', 'Estilo de vida'), ('Fotografía', 'Estilo de vida'), ('Cocina', 'Estilo de vida'),
  ('Fitness', 'Deporte'), ('Running', 'Deporte'), ('Fútbol', 'Deporte'), ('Yoga', 'Deporte'),
  ('Videojuegos', 'Ocio'), ('Arte', 'Cultura'), ('Baile', 'Ocio'), ('Naturaleza', 'Estilo de vida'),
  ('Mascotas', 'Estilo de vida'), ('Tecnología', 'Ocio'), ('Moda', 'Estilo de vida'),
  ('Voluntariado', 'Valores'), ('Espiritualidad', 'Valores')
on conflict (name) do nothing;
