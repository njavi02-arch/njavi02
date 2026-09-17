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

## 3. App móvil y panel admin

Ver el resto de esta sección tras completar la Fase 5 (se actualiza al final de la sesión
con los resultados de `tsc --noEmit`, y de la comprobación visual vía `expo start --web` +
capturas de pantalla si el entorno lo permite).

## 4. Qué NO se ha probado (limitaciones honestas de este entorno)

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
