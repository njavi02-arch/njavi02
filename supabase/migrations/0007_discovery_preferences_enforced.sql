-- ============================================================================
-- Orbita — cierra un hueco real: `user_preferences` (edad mín/máx, género que se busca)
-- se capturaba en el onboarding pero el feed de descubrimiento nunca lo aplicaba (ver
-- PRODUCT_BRAIN.md → PROBLEMAS). Se corrige del lado del cliente (apps/mobile/src/services/
-- discover.ts), y aquí se añade la preferencia "solo verificados" — siguiente ítem del
-- ROADMAP DINÁMICO tras la investigación de mercado (Bumble filtra por verificación).
--
-- `max_distance_km` sigue sin aplicarse: requiere capturar latitude/longitude reales, que
-- ningún flujo de la app rellena todavía (decisión ya documentada de no simular
-- geolocalización precisa). Se deja explícito aquí para no dejarlo como un hueco silencioso.
-- ============================================================================

alter table user_preferences
  add column verified_only boolean not null default false;
