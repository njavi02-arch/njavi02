# Arquitectura técnica (FASE 2)

## 1. Decisión de stack

| Capa | Elección | Alternativas descartadas | Por qué |
|---|---|---|---|
| App móvil | **React Native + Expo (TypeScript)** | Flutter | Un único lenguaje (TS) compartido con backend/admin, ecosistema RN más maduro para chat en tiempo real, Expo permite build cloud (EAS) sin macOS, y target `web` de Expo sirve para smoke-testing en este entorno sin simulador. |
| Backend / datos | **Supabase** (Postgres + Auth + Realtime + Storage + Edge Functions) | Firebase, backend Node custom | Postgres relacional real (las relaciones del brief —usuarios, conversaciones, monedas, reportes— son intrínsecamente relacionales, no documentales), Row Level Security da seguridad a nivel de fila desde el primer día, Realtime nativo sobre Postgres sirve para chat sin infra adicional, y evita mantener un servidor propio para el MVP. Firebase (NoSQL) obligaría a modelar a mano relaciones e integridad que Postgres da gratis. |
| Lógica de negocio sensible | **Supabase Edge Functions (Deno/TS)** + Postgres functions/triggers | Node/Express dedicado | Mismo lenguaje que el resto del monorepo, despliegue serverless sin gestionar servidores, y las funciones de Postgres (`SECURITY DEFINER`) permiten operaciones atómicas (descontar monedas, comprobar rate limit) sin condiciones de carrera. |
| Panel admin | **Next.js (App Router) + TypeScript + Tailwind** | Retool, Directus | Control total del modelo de datos y de las reglas de negocio ya construidas en `packages/shared`; Retool/Directus son más rápidos al inicio pero menos flexibles para lógica custom (rachas, moderación). |
| Gestión de estado / datos remotos (móvil) | **TanStack Query + Zustand** | Redux | Query cubre cache/sincronización con Supabase; Zustand para estado de UI local (formularios de onboarding, tema). Menos boilerplate que Redux. |
| Monorepo | **npm workspaces** | Turborepo/Nx | El proyecto tiene 3 paquetes (mobile, admin, shared): Turborepo/Nx añadirían complejidad de configuración sin beneficio real a esta escala. Se puede migrar más adelante sin romper nada. |
| Notificaciones push | **Expo Notifications** + tabla `push_tokens` + Edge Function despachadora | Firebase Cloud Messaging directo | Expo Push Service abstrae FCM/APNs con una sola API; sigue funcionando si más adelante se hace "eject" a RN puro. |

## 2. Diagrama de componentes

```
┌──────────────────────────┐        ┌──────────────────────────┐
│   apps/mobile (Expo)      │        │   apps/admin (Next.js)    │
│  React Native + TS        │        │  Server Components + API  │
│  TanStack Query + Zustand │        │  routes protegidas admin  │
└──────────┬────────────────┘        └──────────┬────────────────┘
           │  supabase-js (REST/Realtime/Storage)│  service-role key
           ▼                                     ▼
┌─────────────────────────────────────────────────────────────────┐
│                          Supabase                                │
│  ┌───────────────┐ ┌───────────────┐ ┌───────────────────────┐   │
│  │ Postgres 16    │ │ Auth (GoTrue) │ │ Realtime (WAL→WS)     │   │
│  │ + RLS + fns    │ │               │ │ canal por conversación │   │
│  └───────────────┘ └───────────────┘ └───────────────────────┘   │
│  ┌───────────────┐ ┌────────────────────────────────────────┐   │
│  │ Storage        │ │ Edge Functions (Deno)                  │   │
│  │ (fotos, buckets│ │ start-conversation · redeem-daily-     │   │
│  │  público/priv.)│ │ reward · send-super-like · moderate-   │   │
│  │                │ │ photo · push-dispatcher                │   │
│  └───────────────┘ └────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
           ▲
           │ webhook / push
┌──────────┴────────────────┐
│ Expo Push Service → APNs/FCM│  (pendiente credenciales reales)
└─────────────────────────────┘
```

## 3. Por qué la lógica sensible no vive solo en el cliente

Aunque Supabase permite que el cliente móvil escriba directamente a Postgres protegido por
RLS, **las operaciones económicas (gastar monedas, consumir créditos de mensaje, comprobar
rate limit) pasan por Edge Functions o Postgres functions `SECURITY DEFINER`**, nunca por un
`UPDATE` directo del cliente. Razón: un `UPDATE profiles SET coins = coins + 999` disparado
desde un cliente modificado (app parcheada) sería indetectable si la tabla fuera escribible
directamente. Con RLS, la tabla de monedas es de **solo lectura para el usuario**, y todo
cambio de saldo pasa por una función que valida la operación server-side y dispara un evento
auditable en `coin_transactions`.

## 4. Realtime del chat

Cada conversación tiene su propio canal de Supabase Realtime (`postgres_changes` sobre
`messages` filtrado por `conversation_id`, más un canal de **Presence** para
"escribiendo..." y estado online, que no necesita persistirse en tabla). Los ticks de
enviado/recibido/leído se guardan en `messages.status` y `messages.read_at`, actualizados vía
RPC cuando el cliente abre el chat.

## 5. Seguridad por capas

1. **RLS en Postgres** — cada tabla tiene políticas explícitas (ver migraciones); por defecto
   `deny all`.
2. **Edge Functions** para mutaciones con reglas de negocio (rate limit, economía).
3. **Moderación** — cola de revisión (`photos.moderation_status`, `reports`) consumida desde
   el panel admin.
4. **Rate limiting** — tabla `rate_limit_events` + función `check_and_record_rate_limit`,
   ver `06-security-and-privacy.md`.

## 6. Configuración sin hardcodear

Toda cifra de negocio (nº de fotos públicas, coste de super like, recompensas de racha,
límites de rate limiting, precio de premium, etc.) vive en la tabla `app_config`
(clave/valor JSONB) con defaults sembrados en `supabase/seed.sql` y tipados en
`packages/shared/src/config-defaults.ts`. El admin panel escribe en `app_config`; el cliente
móvil y las Edge Functions la leen (con cache corta) — nunca hay una constante de negocio
hardcodeada en el código de producto.

## 7. Estructura de carpetas del monorepo

```
/
├─ apps/
│  ├─ mobile/         Expo app (React Native + TS)
│  └─ admin/           Next.js admin panel
├─ packages/
│  └─ shared/          Tipos + lógica de negocio pura + tests
├─ supabase/
│  ├─ migrations/       SQL versionado
│  ├─ seed.sql
│  └─ functions/        Edge Functions (Deno)
├─ docs/                Esta documentación
└─ package.json         Workspaces raíz
```

## 8. Entornos y despliegue (previsto, no ejecutado en este MVP)

- **Móvil**: Expo Application Services (EAS Build) para iOS/Android, sin necesidad de macOS
  local. Requiere cuentas de Apple Developer / Google Play (coste económico real → decisión
  del usuario, no autónoma).
- **Backend**: proyecto Supabase gestionado (o self-host vía su Docker Compose oficial si se
  prefiere no depender de su nube).
- **Admin**: Vercel o cualquier host Node estándar.
- **CI** (propuesto, no implementado aún): typecheck + tests en cada PR (ver PENDIENTE).
