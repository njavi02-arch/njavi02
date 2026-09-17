# Alcance del MVP y evidencia de pruebas (FASE 6-7)

Este documento recoge **qué se ha probado de verdad** en esta build (no solo revisado a
ojo) y con qué resultado, siguiendo la regla del brief de "no simular funcionalidades".

## 1. Base de datos — validada contra Postgres 16 real

No se dispone de Docker funcional en este entorno (el daemon no está disponible), así que
en vez de levantar el stack completo de Supabase CLI se instaló `postgresql-16` nativo y se
construyó un *shim* de desarrollo (fuera del repo, en el entorno de pruebas) que imita lo
mínimo de Supabase necesario para ejecutar RLS de verdad: esquema `auth.users`, función
`auth.uid()` respaldada por una variable de sesión, y los roles `anon`/`authenticated`/
`service_role`. Con eso se ejecutó `supabase/migrations/0001_init.sql` completo (27 tablas,
~40 policies RLS, 15 funciones, triggers) contra una base de datos limpia.

**Resultado tras iterar:** 25/25 escenarios de comportamiento en verde. Bugs reales
encontrados y corregidos durante esta validación (no eran errores de sintaxis, sino de
lógica/orden):

1. **Orden de creación**: la policy de `profiles` referenciaba `blocks` antes de que la
   tabla existiera → migración fallaba al aplicar. Corregido moviendo `blocks` antes de
   las políticas de `profiles`.
2. **Bug de seguridad real (RLS recursivo)**: la comprobación de bloqueo mutuo
   (`EXISTS (select 1 from blocks where ...)`) escrita directamente dentro de la policy de
   `profiles` quedaba **ella misma filtrada por la RLS de `blocks`** (que solo deja ver a
   cada usuario los bloqueos que él mismo creó). Consecuencia: si A bloqueaba a B, B seguía
   viendo el perfil de A con toda normalidad, porque desde la sesión de B la fila del
   bloqueo (creada por A) era invisible para esa subconsulta. Es decir, **el bloqueo no era
   realmente bidireccional** aunque lo pareciera revisando el código a ojo. Se corrigió
   extrayendo la comprobación a una función `is_blocked_between()` con
   `SECURITY DEFINER`, que no está sujeta a la RLS de `blocks` (patrón recomendado por
   Supabase para este caso exacto). Se añadió también un guard `auth.uid() is not null`
   como defensa en profundidad.
3. **Bug de racha (día 1 vs. resto del ciclo)**: al portar la lógica de
   `computeStreakCheckin` a PL/pgSQL (`claim_daily_streak`), un primer intento tenía el
   mismo *off-by-one* que se detectó y corrigió en `packages/shared` (ver más abajo) — se
   corrigió replicando la fórmula ya validada: `next_day = (claimed_day % 7) + 1`.

Casos cubiertos por el harness de pruebas (ver detalle de cada aserción en el historial de
comandos de esta sesión): alta de perfil y bootstrap de wallets, rechazo de menores de 18,
visibilidad RLS de perfiles (con y sin sesión), bloqueo bidireccional, flujo completo de
solicitud → aceptación → conversación → mensaje, RLS de mensajes (un tercero no
participante no puede leerlos), gasto atómico de monedas con saldo insuficiente, límite de
10 fotos por perfil, cálculo de fotos públicas/bloqueadas (3 públicas + 7 ocultas), racha de
7 días completa día por día incluyendo el reinicio de ciclo en el día 8, y rate limiting
anti-spam con el factor reducido de cuentas nuevas.

**Cómo reproducirlo con las herramientas oficiales** (recomendado para el equipo, en vez del
shim usado aquí): `supabase start` (requiere Docker) y `supabase db push`, o conectar
`psql` directamente a un proyecto Supabase real y ejecutar los archivos de
`supabase/migrations/` en orden seguido de `supabase/seed.sql`.

## 2. Lógica de negocio pura — `packages/shared`

30/30 tests unitarios en verde (`npm run test --workspace=packages/shared`, Vitest).
Durante el desarrollo se encontraron y corrigieron **2 bugs reales** en
`computeStreakCheckin` (el cálculo del "día siguiente" de la racha estaba mal en el primer
check-in y en cualquier check-in consecutivo — devolvía el día equivocado; y el flag
`streakWasReset` se marcaba `true` incluso para el primer check-in de un usuario que nunca
tuvo racha previa). Cobertura: saldos y sus errores, coste de Super Like/desbloqueo de
fotos/admiradores secretos con y sin Premium, visibilidad de fotos bloqueadas, racha
completa de 7 días + reinicio de ciclo, porcentaje de perfil completado, edad mínima
(incluyendo el caso límite de cumplir 18 exactamente hoy vs. mañana), y rate limiting por
antigüedad de cuenta.

`tsc --noEmit` sin errores en `packages/shared`.

## 3. App móvil — typecheck y smoke test visual real

`npx tsc --noEmit` en `apps/mobile`: **0 errores** sobre todo el código de la app (auth,
onboarding, descubrimiento, chat, economía, navegación). Durante el desarrollo se
encontraron y corrigieron 2 bugs reales de tipos/imports (un import cruzado entre
`services/economy.ts` y `services/discover.ts`, y un conflicto de tipos en la lectura de
`app_config` por la inferencia automática de columnas de `supabase-js`).

Más allá del typecheck, se hizo una comprobación **visual real en navegador**, no solo
estática:

1. `EXPO_OFFLINE=1 npx expo export --platform web` compila los 1252 módulos de la app
   (Reanimated/Worklets, React Navigation, TanStack Query, Zustand, Supabase JS, todas las
   pantallas) a un bundle de producción sin errores. (`EXPO_OFFLINE` fue necesario porque
   la política de red de este entorno bloquea `reactnative.directory` y `api.expo.dev`,
   que Expo CLI consulta por defecto para comprobar compatibilidad de paquetes y telemetría
   — no afecta al bundling en sí.)
2. Ese bundle se sirvió localmente y se abrió con Chromium vía Playwright:
   - Pantalla de bienvenida (`WelcomeScreen`): logo, gradiente, tipografía Sora/Inter y
     botones renderizan correctamente, sin errores de consola ni de página.
   - Navegación a `SignUpScreen`: formulario, validación (botón "Continuar" deshabilitado
     hasta que el email/contraseña son válidos) y textos legales renderizan correctamente.
   - Se detectó y corrigió un bug real de robustez durante esta prueba: si
     `supabase.auth.getSession()` fallaba (sin red o backend mal configurado),
     `authStore.bootstrap()` no capturaba el error y la app se quedaba en la pantalla de
     carga para siempre. Ahora cualquier fallo de red al arrancar cae de forma segura a
     "sin sesión" en vez de colgar la app.
   - Sin credenciales de Supabase, la app muestra el estado explícito
     `BackendNotConfigured` en vez de datos falsos (comportamiento verificado).

Lo que **no** se ha podido probar en este entorno: pantallas que requieren un backend real
conectado (descubrimiento con datos reales, chat en vivo, reclamar racha, etc.) — no se
simulan con datos falsos porque el brief lo prohíbe explícitamente; están verificadas por
tipos y por la lógica de `packages/shared` + las 25 validaciones de base de datos, pero no
visualmente. Tampoco hay simulador iOS/Android en este entorno remoto.

## 4. Panel de administración — build de producción y smoke test real

`npx tsc --noEmit` en `apps/admin`: 0 errores. `next build` (producción, con Turbopack):
compila con éxito, genera `/` y `/login` como estáticas y `/dashboard`, `/users`,
`/reports`, `/photos`, `/config` como dinámicas (correcto: leen `cookies()` en cada
petición para comprobar la sesión de admin).

Comprobación real arrancando el build (`next start`) y con Chromium vía Playwright:

- `/login` renderiza correctamente (formulario, estilos, sin errores de consola).
- `GET /dashboard` sin cookie de sesión responde `307` a `/login` — confirma que
  `requireAdmin()` protege de verdad las rutas del panel, no solo a nivel de UI.

No se ha podido probar el flujo de login completo end-to-end (requiere un usuario real en
`admin_users` de un proyecto Supabase real) ni las acciones de moderación/config contra
datos reales, por la misma razón que en el punto 3: no hay proyecto Supabase desplegado en
este entorno y no se simulan datos.

## 4b. `0002_atomic_actions.sql` — hardening posterior, también validado de verdad

Tras el MVP inicial se detectó que "enviar solicitud de conversación" y "enviar Super
Like" hacían 2-3 llamadas de red separadas desde el cliente (insertar + cobrar), con el
riesgo de que un fallo a mitad de camino dejara el sistema en un estado a medias. Se
corrigió moviendo toda la operación a funciones Postgres `SECURITY DEFINER`
(`create_conversation_request`, `send_super_like`) que hacen todo en una sola transacción
atómica — incluida la regla, documentada pero no implementada hasta ahora, de bloquear
reintentos durante 30 días tras un rechazo (salvo que la otra persona te haya escrito ya).

Validado con 10 escenarios nuevos contra la base de datos real (35/35 en total sumando la
suite original): solicitud creada + crédito descontado + notificación generada en un solo
paso; sin créditos suficientes **no se crea ninguna solicitud** (antes de este cambio sí
se creaba una, aunque no se cobrara — ver el `git log`); el cooldown de 30 días bloquea
un reintento y dos casos también verificados: si la otra persona ya te escribió, el
cooldown no aplica; y el Super Like cobra monedas correctamente en cuanto se agota el
cupo gratis del día. Además se descubrió y cerró una laguna real: antes de este cambio
**nunca se creaba una notificación** para "nueva solicitud" ni "Super Like recibido"
porque la tabla `notifications` no tiene policy de INSERT para clientes (a propósito) y
nada del lado servidor las estaba generando.

## 4c. Auditoría de código muerto → 8 huecos reales encontrados y cerrados

Tras el MVP, se hizo un barrido sistemático buscando funciones de servicio exportadas que
ningún componente llamaba (`grep` de cada `export function` de `apps/mobile/src/services`
contra el resto del código). El resultado no fue solo limpieza: varias de esas funciones
"muertas" eran features completas que faltaba conectar a la UI, o revelaban bugs reales:

- **`profile_completion_pct` nunca se calculaba** — el bug más importante de este barrido.
  `computeCompletionFromProfile` existía pero nadie la llamaba, así que el porcentaje de
  "perfil completado" que se le promete al usuario en el onboarding se quedaba clavado en
  0% para siempre. Corregido con un trigger de base de datos
  (`0003_profile_completion_trigger.sql`) que recalcula el porcentaje automáticamente en
  cuanto cambian nombre/fecha/género/busca/ciudad/bio/fotos/intereses — más robusto que
  depender de que cada pantalla del cliente se acuerde de llamar a una función, que es
  justo lo que había fallado la primera vez. Validado con 5 escenarios nuevos (40/40 en
  total): perfil mínimo, tras completar campos, con 3 fotos sin intereses, 100% con todo
  completo, y que borrar una foto hace bajar el % de nuevo.
- **`isUserA` hardcodeado a `true`** en `ChatScreen` al silenciar/archivar — para la mitad
  de los usuarios (los que son `user_b` de la conversación) esas acciones actualizaban la
  fila equivocada. Corregido calculando `isUserA` de verdad a partir de la conversación.
- **Sin recuperación de contraseña** — `requestPasswordReset` existía sin ningún enlace en
  `LoginScreen`. Añadido "¿Olvidaste tu contraseña?" con manejo de error real (probado con
  Playwright: sin backend disponible, el fallo de red se captura y se muestra sin que la
  app se rompa).
- **Sin forma de deshacer un bloqueo** — `unblockUser`/`listMyBlocks` existían sin ninguna
  pantalla; una vez bloqueabas a alguien por error no había recurso. Añadida la pantalla
  "Usuarios bloqueados" en Ajustes.
- **Fotos en el chat, pedidas explícitamente en el brief (sección 10), sin botón** —
  `sendImageMessage` existía pero `ChatScreen` no tenía ningún selector de imagen.
  Añadido el botón 📷 en el composer, subida a Storage y renderizado de mensajes de
  imagen en la conversación.
- **`grantCoinsToUser` sin botón** en el panel admin — añadido "+50 🪙" por fila de usuario.
- Limpieza de la función `blockAndExitConversation` (duplicaba `blockUser` sin hacer lo
  que su nombre prometía) y `getCurrentSession` (redundante con lo que ya hace authStore).

## 4d. Investigación de mercado → 6 funcionalidades nuevas, validadas de verdad

Tras investigar Wizz, Tinder, Bumble, Yubo y Hinge (ver `PRODUCT_BRAIN.md` completo, con
fuentes) se construyeron seis funcionalidades y se corrigió, de paso, un bug de datos que
llevaba desde el primer commit:

- **`profiles.last_active_at` nunca se actualizaba** — el feed de descubrimiento decía
  ordenar "por actividad reciente" pero esa columna se quedaba congelada en la fecha de
  creación del perfil para siempre. Corregido con un heartbeat cliente (`touchLastActive`,
  cada 3 min en primer plano + al abrir la app) y usado para un indicador nuevo "Activo
  ahora"/"Activo hoy" (`packages/shared/src/presence.ts`, 7 tests unitarios sobre los
  límites exactos de 2h/24h, incluida la protección ante un reloj de dispositivo adelantado).
- **Verificación de perfil**: selfie real (cámara frontal, no galería) + cola de moderación
  manual en el panel admin (`/verifications`) + badge ✅ automático al aprobar. 4 escenarios
  reales: no se puede tener 2 solicitudes pendientes a la vez, aprobar marca el badge,
  rechazar/revocar lo quita.
- **Prompts de perfil** (hasta 3, estilo pregunta elegida): 6 tests unitarios de
  `suggestIcebreakers` + 3 escenarios de base de datos, incluido un **bug real encontrado
  antes de llegar a producción**: el trigger que limita a 3 prompts contaba mal y bloqueaba
  editar un prompt ya existente en cuanto había 3 creados — corregido excluyendo la propia
  posición del recuento.
- **Sugerencias de primer mensaje** (icebreakers) por interés compartido o prompt de la
  otra persona — deterministas, sin IA generativa de terceros (ver decisión en
  PRODUCT_BRAIN.md), mostradas como chips tocables en el composer de Descubrir y del perfil.
- **Boost de visibilidad pagado con monedas**: 4 escenarios reales — cobra
  `boost_coin_cost`, bloquea activar un segundo Boost mientras el primero sigue vivo, y los
  perfiles con Boost activo aparecen primero en el feed (`get_active_boosted_profile_ids()`).
- **Señales automáticas de cuentas sospechosas** por acumulación de reportes (sin IA de
  terceros): 4 escenarios — 3 reportes en 30 días generan una señal sin duplicarse en
  reportes sucesivos, 5 reportes escalan a revisión automática del perfil.

**Total acumulado tras esta ronda: 56/56 escenarios de base de datos reales, 43/43 tests
unitarios de `packages/shared`.** `tsc --noEmit` limpio en las tres apps, `next build` y
`eslint` limpios en el panel admin (con las tres páginas nuevas: `/verifications`, la
sección de señales en `/reports`, y los contadores nuevos en `/dashboard`), y bundle web de
la app móvil reconstruido y verificado en Chromium sin errores de consola tras cada tanda
de cambios.

## 4e. Reacciones a mensajes (`0006_message_reactions.sql`) — siguiente ítem del roadmap

Patrón Wizz (tapback, no acumulable — ver `PRODUCT_BRAIN.md`). `message_reactions` con
`unique (message_id, profile_id)` y RLS que replica exactamente las reglas de `messages`.
4 escenarios reales contra Postgres: un participante puede reaccionar, solo una reacción por
persona y mensaje (el `unique` bloquea la segunda), un tercero ajeno a la conversación no ve
ninguna reacción por RLS, un participante puede cambiar su propia reacción (`update`).

UI: long-press sobre un mensaje abre un selector de los 6 emojis permitidos; las reacciones
existentes se agrupan por emoji con contador bajo la burbuja; tocar el emoji con el que ya
reaccionaste lo retira (toggle); sincronizado en tiempo real entre ambos participantes vía un
canal de Realtime sobre `message_reactions` (filtrado en cliente por los ids de mensaje ya
cargados, ya que la tabla no tiene columna `conversation_id` para filtrar en el propio canal;
en `DELETE`, Postgres solo garantiza la clave primaria en el "old row" salvo
`REPLICA IDENTITY FULL`, así que el borrado local se aplica por `id` de la reacción, no por
`message_id`).

**Total acumulado: 60/60 escenarios de base de datos reales, 43/43 tests unitarios de
`packages/shared`, `tsc --noEmit` limpio en `apps/mobile` tras añadir el servicio y la UI de
reacciones.**

## 4f. Preferencias de descubrimiento aplicadas de verdad (`0007_discovery_preferences_enforced.sql`)

Bug real encontrado revisando el propio `discover.ts` (mismo patrón que `last_active_at` y
`profile_completion_pct` en rondas anteriores): `user_preferences.min_age`/`max_age`/
`show_me_gender` se capturaban en el onboarding pero el feed de descubrimiento nunca los leía
— cualquier persona veía perfiles de cualquier edad y género, sin importar lo que hubiera
elegido. Corregido en `apps/mobile/src/services/discover.ts`, que ahora consulta
`user_preferences` y aplica `birth_date` (rango calculado por
`packages/shared/src/discoveryFilters.ts`), `gender in (...)` y, si `verified_only` está
activo, `is_verified = true` (columna nueva, siguiente ítem del roadmap tras la investigación
de mercado — Bumble filtra por verificación). Se añadió también una pantalla real en
Ajustes → "Preferencias de descubrimiento" para poder cambiarlas después del onboarding, algo
que antes no existía.

- **6 tests unitarios** de `ageRangeToBirthDateRange` (`packages/shared/src/
  discoveryFilters.test.ts`): límite superior exacto (cumple la edad mínima hoy mismo queda
  incluido), límite inferior exacto (cumple la edad máxima+1 mañana queda excluido), rango
  coherente para edades típicas.
- **3 escenarios reales contra Postgres** (`08_discovery_prefs_scenarios.sql`): sin
  `verified_only`, entran los perfiles en rango de edad/género (con RLS activa); con
  `verified_only=true`, solo entra la persona verificada dentro de ese rango; un perfil fuera
  de rango de edad queda excluido.
- `max_distance_km` se sigue capturando en el onboarding pero **no se aplica**: ningún flujo
  de la app rellena `profiles.latitude/longitude` con coordenadas reales todavía (decisión ya
  documentada de no simular geolocalización precisa — ver `06-security-and-privacy.md`). Se
  deja explícito en el código y en `PRODUCT_BRAIN.md` en vez de dejarlo como un hueco
  silencioso.

**Total acumulado: 63/63 escenarios de base de datos reales, 49/49 tests unitarios de
`packages/shared`, `tsc --noEmit` limpio en las tres apps, `next build`+`eslint` limpios en
el panel admin.**

## 4g. Exportación de datos personales — RGPD (`0008_gdpr_data_export.sql`)

`export_my_data()`, `SECURITY DEFINER` pero siempre acotada a `auth.uid()` (nunca recibe un
`profile_id`, a diferencia de las funciones de economía que sí actúan sobre otro perfil —
aquí no hay forma de exportar los datos de otra persona). Devuelve un JSON con perfil, fotos,
intereses, prompts, preferencias, saldos y transacciones de monedas/créditos, racha,
conversaciones+mensajes, solicitudes de conversación enviadas/recibidas, Super Likes
enviados, reportes presentados, bloqueos creados, solicitudes de verificación y boosts.

**6 escenarios reales contra Postgres** (`09_gdpr_export_scenarios.sql`): sin sesión activa
lanza excepción (nunca devuelve datos de nadie); el export incluye el perfil propio; incluye
la conversación real con su mensaje; **no** incluye el reporte que otra persona presentó
contra el usuario (mismo principio de "sin represalias" que ya aplica la policy
`reports_select_own`); incluye el saldo de créditos de mensaje.

UI real: Ajustes → "Exportar mis datos" escribe el JSON a un archivo local
(`expo-file-system`, API `File`/`Paths`) y lo comparte con el share sheet nativo
(`expo-sharing`) — el usuario decide dónde guardarlo o a quién enviarlo, sin necesidad de
ningún servicio de envío de email propio.

**Total acumulado: 69/69 escenarios de base de datos reales, 49/49 tests unitarios de
`packages/shared`, `tsc --noEmit` limpio en las tres apps (incluida la reconstrucción del
bundle web tras añadir `expo-file-system`/`expo-sharing`), `next build`+`eslint` limpios en
el panel admin.**

## 5. Qué NO se ha probado (limitaciones honestas de este entorno)

- **No hay simulador iOS/Android ni dispositivo físico** en este entorno remoto: no se
  puede verificar visualmente la app en un simulador nativo. Se compensa con: (a)
  typecheck estricto de todo el código React Native, (b) revisión de cada pantalla contra
  el flujo de UX documentado en `04-ux-ui-flows.md`, y (c) cuando es viable, una comprobación
  en el target `web` de Expo (react-native-web) vía navegador headless.
- **No hay proyecto Supabase real desplegado**: las migraciones están validadas contra
  Postgres puro con un shim de autenticación, no contra el Supabase gestionado real (Auth
  server, Realtime, Storage). Antes de producción, ejecutar `supabase db push` contra un
  proyecto real y repetir al menos el flujo de registro → onboarding → primer mensaje.
- **No hay tests end-to-end de Realtime** (WebSocket de chat en vivo): la lógica de mensajes
  se probó a nivel de base de datos (inserción, RLS, triggers), no el canal de Supabase
  Realtime en sí, que requiere el servidor Realtime real.
