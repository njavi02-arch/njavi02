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
