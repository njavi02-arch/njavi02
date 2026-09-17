# Base de datos (FASE 3)

El esquema real y ejecutable vive en `supabase/migrations/0001_init.sql` (probado contra un
Postgres 16 local, ver `docs/05-mvp-scope-and-testing.md`). Este documento explica el
**porqué** de las decisiones de modelado; para el detalle columna a columna, leer la
migración, que está comentada.

`supabase/migrations/0002_atomic_actions.sql` añade dos funciones `SECURITY DEFINER` que
convierten "enviar solicitud de conversación" y "enviar Super Like" en transacciones
atómicas de servidor (rate limit + cobro + creación del registro + notificación en un
único paso), en vez de varias llamadas separadas desde el cliente. Ver
`docs/05-mvp-scope-and-testing.md §4b` para el detalle y la evidencia de pruebas.

`supabase/migrations/0003_profile_completion_trigger.sql` añade triggers en `profiles`,
`photos` y `profile_interests` que recalculan `profiles.profile_completion_pct`
automáticamente. Corrige un bug real: ese porcentaje se quedaba en 0% para siempre porque
ningún cliente lo actualizaba nunca — ver `docs/05-mvp-scope-and-testing.md §4c`.

`supabase/migrations/0004_streak_at_risk_notification.sql` añade
`notify_streak_at_risk_if_needed()`, que dispara (deduplicado a 1/día) la notificación
`streak_at_risk` — un tipo definido desde el principio que nunca se usaba.

`supabase/migrations/0005_verification_prompts_boost_flags.sql` añade, tras la
investigación de mercado documentada en `PRODUCT_BRAIN.md`: `verification_requests` +
`profiles.is_verified` (verificación por selfie con cola de moderación manual),
`profile_prompts` (hasta 3 por perfil), lógica real para `profile_boosts` (`activate_boost()`,
pagado con monedas) y un trigger que puebla `suspicious_activity_flags` por acumulación de
reportes — dos tablas que existían desde 0001 sin ninguna lógica que las usara.

`supabase/migrations/0006_message_reactions.sql` añade `message_reactions` (patrón Wizz —
ver `PRODUCT_BRAIN.md`): una reacción de un set fijo de 6 emojis por persona y mensaje
(`unique (message_id, profile_id)`, como un tapback, no acumulable), con RLS que replica
exactamente las reglas de `messages` — solo los participantes de la conversación del mensaje
pueden ver o insertar reacciones.

`supabase/migrations/0007_discovery_preferences_enforced.sql` añade
`user_preferences.verified_only`. La corrección de fondo (que `min_age`/`max_age`/
`show_me_gender` se apliquen de verdad al feed) vive en el cliente
(`apps/mobile/src/services/discover.ts` + `packages/shared/src/discoveryFilters.ts` para la
aritmética de fechas), no en SQL — no había ninguna función de servidor que ignorara estas
columnas, simplemente ningún código las leía todavía.

`supabase/migrations/0008_gdpr_data_export.sql` añade `export_my_data()`: derecho de
acceso/portabilidad RGPD (ver `06-security-and-privacy.md §6`). Es `SECURITY DEFINER` pero
opera siempre sobre `auth.uid()`, nunca recibe un `profile_id` como parámetro — a diferencia
de las funciones de economía (que sí actúan sobre otro perfil, el receptor), esta nunca
podría exportar los datos de otra persona aunque alguien intentara forzarlo.

## 1. Mapa de entidades

```
auth.users (Supabase Auth)
   │ 1:1
   ▼
profiles ──1:N── photos
   │ 1:N                     interests ──N:M── profile_interests
   ├── coin_wallets (1:1) ── coin_transactions (1:N)
   ├── message_credit_wallets (1:1) ── message_credit_transactions (1:N)
   ├── daily_streaks (1:1) ── daily_streak_claims (1:N)
   ├── notification_preferences (1:1)
   ├── push_tokens (1:N)
   ├── premium_subscriptions (1:N, histórico)
   └── user_preferences (1:1, discovery prefs)

conversation_requests (sender_id, receiver_id) ──accepted──▶ conversations (user_a, user_b)
                                                                    │ 1:N
                                                                    ▼
                                                                 messages

super_likes (sender_id, receiver_id)
profile_views (viewer_id, viewed_id)
admirer_reveals (profile_id, revealed_viewer_id)   -- desbloqueo de admirador secreto
photo_unlocks (viewer_id, target_profile_id)        -- desbloqueo de fotos ocultas

reports (reporter_id, reported_id, related_message_id?)
blocks (blocker_id, blocked_id)
notifications (profile_id, type, payload)

app_config (key, value jsonb)                       -- configuración editable desde admin
rate_limit_events (profile_id, action_type, created_at)
admin_users (id, role)
audit_log (actor_admin_id, action, target_table, target_id)
```

## 2. Decisiones de modelado clave

- **`profiles` separado de `auth.users`**: Supabase Auth gestiona credenciales; `profiles`
  guarda todo lo de negocio. Esto permite borrar/anonimizar datos de perfil (derecho al
  olvido RGPD) sin tocar el sistema de autenticación, y mantiene `auth.users` fuera del
  alcance de RLS de aplicación.
- **Wallets separados de `profiles`**: `coin_wallets` y `message_credit_wallets` son tablas
  propias (no columnas en `profiles`) para poder aplicarles políticas RLS distintas
  (solo lectura para el usuario, escritura solo vía función `SECURITY DEFINER`) sin afectar
  a la tabla de perfil, que sí es editable por su dueño.
- **`conversation_requests` vs `conversations`**: se separan porque tienen ciclos de vida y
  permisos distintos — una solicitud pendiente es visible solo por el receptor y el emisor con
  campos limitados; una conversación aceptada abre un canal Realtime y una tabla `messages`
  con throughput mucho mayor. Fusionarlas obligaría a políticas RLS condicionales mucho más
  complejas.
- **`photo_unlocks` y `admirer_reveals` como tablas de desbloqueo, no como flags**: permiten
  auditar quién pagó por ver qué y cuándo (necesario para soporte/disputas de cobro), y
  hacen trivial comprobar "¿ya pagué esto?" con un índice único `(viewer_id, target_id)`.
- **`rate_limit_events`**: tabla append-only con índice `(profile_id, action_type,
  created_at)`; una función cuenta eventos en la ventana y limpia filas viejas con un job
  periódico. Documentado como solución **suficiente para el MVP**, no como la solución final
  de escala (ver `07-roadmap-and-scaling.md` → recomendación de mover a Redis/Upstash cuando
  el volumen lo justifique).
- **`app_config` como tabla clave/valor JSONB** en vez de columnas sueltas: permite añadir
  nuevos parámetros de negocio sin migraciones, y el admin panel puede editar un JSON con
  validación de esquema en la capa de aplicación (`packages/shared/src/config-defaults.ts`
  define el tipo `AppConfig` que valida la forma esperada).
- **Borrado**: `profiles.status` incluye `deleted`; el borrado de cuenta es **soft delete +
  anonimización** de campos personales (nombre, fotos, bio) en vez de `DELETE` físico
  inmediato, para no romper integridad referencial en conversaciones de terceros; un job
  programado purga físicamente tras el periodo de gracia legal correspondiente (a definir con
  asesoría legal).

## 3. Índices y rendimiento

Cada tabla de alto volumen (`messages`, `profile_views`, `coin_transactions`,
`rate_limit_events`, `notifications`) tiene índices compuestos alineados con sus patrones de
consulta reales (ver comentarios `-- idx:` en la migración). `profiles` tiene índice sobre
`(status, last_active_at)` para el feed de descubrimiento y sobre `city` para filtrado por
ubicación aproximada.

## 4. RLS (resumen — políticas completas en la migración)

- **Deny-by-default**: `ALTER TABLE ... ENABLE ROW LEVEL SECURITY` en todas las tablas de
  negocio, sin política = sin acceso.
- **`profiles`**: SELECT público limitado a perfiles `active` y no bloqueados por el
  solicitante (vía función `is_visible_to(viewer, target)`); UPDATE solo del propio dueño.
- **`messages` / `conversations`**: SELECT/INSERT solo si `auth.uid()` es `user_a_id` o
  `user_b_id` de la conversación.
- **`coin_wallets`, `message_credit_wallets`**: SELECT del propio dueño; sin política de
  INSERT/UPDATE/DELETE para el rol `authenticated` — solo `service_role` (Edge Functions)
  puede mutar saldo.
- **`reports`, `blocks`**: INSERT solo con `reporter_id`/`blocker_id` = `auth.uid()`; sin
  SELECT para el denunciado (no puede ver quién lo reportó).
- **`app_config`**: SELECT para `authenticated` (el cliente necesita leer límites), sin
  INSERT/UPDATE salvo `service_role`/admin.

## 5. Validación

El esquema se ejecutó de verdad contra Postgres 16 local (con un *shim* mínimo de
`auth.uid()`/`auth.users` que imita el entorno de Supabase) para confirmar que las 25+ tablas,
claves foráneas, índices y políticas RLS son sintácticamente correctas y se pueden crear sin
errores. Detalle del harness de pruebas en `05-mvp-scope-and-testing.md`.
