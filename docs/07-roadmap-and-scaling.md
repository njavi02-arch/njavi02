# Roadmap, pendientes y preparación para escalar (FASE 8-9)

## 1. Pendiente antes de un lanzamiento real

Ordenado por lo que más bloquea un lanzamiento real:

1. **Proyecto Supabase real** — crear el proyecto, ejecutar
   `supabase/migrations/0001_init.sql` + `supabase/seed.sql`, configurar Storage (bucket
   `photos`, público de lectura, con política de subida solo al propio dueño), y activar
   Realtime en la tabla `messages`. Ninguna de estas decisiones tiene coste ni compromete
   nada hasta que el usuario decide crear la cuenta — no se ha hecho de forma autónoma
   porque implica "crear una cuenta externa" (fuera de la autonomía concedida).
2. **Pasarela de pago real** (Stripe / RevenueCat / IAP de Apple-Google) — el modelo de
   datos (`premium_subscriptions`, `coin_transactions`) y la UI (`WalletScreen`,
   `PremiumScreen`) ya están listos; falta contratar el servicio y conectar el webhook.
   Implica coste económico real → decisión explícita del usuario.
3. **Edge Functions** (`start-conversation`, `send-super-like`, `redeem-daily-reward`,
   `push-dispatcher`) — **actualizado**: la atomicidad ya no depende de desplegarlas.
   `supabase/migrations/0002_atomic_actions.sql` mueve "enviar solicitud" y "enviar Super
   Like" a funciones Postgres `SECURITY DEFINER` (`create_conversation_request`,
   `send_super_like`) que hacen toda la operación — rate limit, filtro de palabras,
   cooldown de 30 días, cobro y creación del registro + notificación — en una única
   transacción de base de datos, validado con tests reales (ver `05-mvp-scope-and-
   testing.md`). Las Edge Functions siguen siendo la vía recomendada para añadir
   validaciones que necesiten un servicio externo (moderación de texto con IA,
   verificación de dispositivo, envío de push) que Postgres no puede hacer por sí solo, y
   para el dispatcher de push notifications, pero ya no son necesarias solo para
   garantizar que estas dos acciones sean atómicas.
4. **Push notifications reales** — requiere credenciales de Apple Push (APNs) y Firebase
   Cloud Messaging, dadas de alta en el proyecto Expo. La tabla `push_tokens` y las
   `notification_preferences` ya existen; falta el paso de registrar el dispositivo desde
   la app (`expo-notifications` ya está instalado) y el envío server-side.
5. **Revisión legal** — Términos de Servicio, Política de Privacidad y cumplimiento RGPD
   completo (ver `06-security-and-privacy.md §6`) por un profesional. No se han redactado
   textos legales definitivos, solo la arquitectura que los soporta.
6. **Moderación automática de imágenes** (NSFW/menores) antes de que una foto llegue
   siquiera a la cola de revisión humana del panel admin — reduce carga de moderación y
   riesgo. Requiere contratar un servicio de terceros.
7. **Verificación de identidad / selfie liveness** — mencionada como buena práctica del
   sector para reducir perfiles falsos; no estaba en el alcance del MVP del brief.

## 2. Deuda técnica y pulido conocido (no bloquea el MVP)

- **Selector de fecha nativo** en el onboarding (`StepBasics`): ahora mismo es un campo de
  texto validado (`AAAA-MM-DD`); un `DateTimePicker` nativo mejoraría la UX.
- **Gesto de swipe** en Descubrir: implementado con botones (`Pasar`/`Hablar`/`Super Like`),
  tal como pide el brief como interacción principal; el swipe lateral opcional mencionado
  en `04-ux-ui-flows.md` no está implementado todavía.
- **Logros/badges** más allá del porcentaje de perfil completado y la racha: el brief pide
  gamificación "integrada de forma natural, sin elementos innecesarios" — se ha priorizado
  monedas + racha + Super Likes (los sistemas explícitamente detallados) antes que añadir
  más mecánicas no especificadas.
- **Captura real de geolocalización**: `user_preferences.max_distance_km` se captura en el
  onboarding pero no se aplica al feed — ningún flujo rellena `profiles.latitude/longitude`
  con coordenadas reales todavía. Requiere permiso de ubicación + geocodificación; evaluar
  coste/beneficio y privacidad antes de construir (ver `06-security-and-privacy.md`).
- **Rate limiting a escala**: `rate_limit_events` en Postgres es válido para el volumen de
  un MVP; con tráfico alto, migrar a un almacén en memoria (Upstash Redis, por ejemplo) con
  la misma interfaz (`check_and_record_rate_limit`) para no reescribir las llamadas.

Ya resuelto en rondas posteriores de esta misma sesión (se deja constancia aquí porque este
documento los listaba como pendientes): **Boost de visibilidad** tiene UI completa
(`WalletScreen`, tag "🚀 Destacado" en Descubrir, pagado con monedas) · **exportación de
datos del usuario** (RGPD) está construida (`export_my_data()` + Ajustes → "Exportar mis
datos", ver `06-security-and-privacy.md §6`) · **CI** existe en
`.github/workflows/ci.yml` (tests + typecheck de `packages/shared`, typecheck de
`apps/mobile`, typecheck+lint de `apps/admin` en cada push/PR).

## 3. Preparación para escalar

- **Índices**: ya cubren los patrones de consulta principales (ver `03-database.md §3`);
  revisar con `EXPLAIN ANALYZE` sobre datos reales antes de un lanzamiento con volumen.
- **Particionado**: `messages`, `notifications` y `rate_limit_events` son las tablas de
  mayor crecimiento — candidatas a particionar por fecha si el volumen lo justifica
  (Postgres declarative partitioning), sin cambiar el modelo lógico.
- **Realtime**: Supabase Realtime escala por proyecto; si el volumen de conversaciones
  concurrentes crece mucho, evaluar limitar el número de canales activos por cliente
  (agrupar en un único canal con multiplexado en vez de un canal por conversación).
- **CDN de imágenes**: Supabase Storage sirve directamente; para volumen alto, poner un CDN
  delante (Cloudflare, por ejemplo) reduce coste y latencia — no requiere cambiar el modelo
  de datos, solo la URL pública que se guarda en `photos.url`.
- **Separar panel admin del tráfico de producto**: ya están en apps separadas
  (`apps/admin` vs `apps/mobile`), lo que permite desplegarlos y escalarlos de forma
  independiente desde el primer día.

## 4. Métricas para iterar tras el lanzamiento

Ver `01-product-spec.md §12`. Prioridad: tasa de respuesta a solicitudes de conversación
y tiempo hasta el primer mensaje — son las métricas que más reflejan si el "bucle central"
(descubrir → hablar → responder → conversar) está funcionando de verdad.
