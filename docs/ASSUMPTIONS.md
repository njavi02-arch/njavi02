# Registro de decisiones autónomas (ASSUMPTIONS)

Este documento recoge cada decisión tomada de forma autónoma cuando la idea original no
especificaba un detalle concreto, siguiendo la regla del brief: *"si falta información, haz
una suposición razonable, documenta la decisión, continúa, permíteme cambiarla después"*.

Todas estas decisiones son **reversibles** y la mayoría están **parametrizadas** en
`app_config` (base de datos) o en `packages/shared/src/config-defaults.ts`, para poder
cambiarlas sin tocar código.

## Producto

| # | Decisión | Razón | Cómo cambiarla |
|---|---|---|---|
| 1 | Nombre provisional de marca: **Orbita** | Ni Tinder ni Wizz ni otras apps sociales/dating conocidas usan este nombre. Es un placeholder — se recomienda búsqueda de marca registrada antes de publicar. | Buscar/reemplazar `Orbita` / `APP_NAME` |
| 2 | Idioma inicial: español (España/LatAm), infraestructura preparada para i18n futura | Mercado objetivo implícito en el brief (RGPD, España/UE) | Añadir `i18next` cuando se necesite un segundo idioma |
| 3 | Edad mínima: **18 años**, no configurable por debajo de ese umbral | Estándar del sector para apps de descubrimiento social con posible componente romántico; evita responsabilidad legal grave. Revisar con un abogado antes de lanzar. | `app_config.min_age` (mínimo absoluto de 18 fijado en código) |
| 4 | Navegación inferior: **Descubrir · Mensajes · Actividad · Perfil** (4 tabs) | "Solicitudes" se fusiona conceptualmente dentro de "Actividad" junto con Quién-te-ha-visto/Admiradores, para no saturar la tab bar; dentro de Actividad hay sub-tabs. Mensajes ya incluye badge de solicitudes pendientes. | Editar `apps/mobile/src/navigation` |

## Economía / gamificación (valores por defecto, todos en `app_config`)

| Parámetro | Valor por defecto | Nota |
|---|---|---|
| `public_photos_count` | 3 | Fotos visibles sin desbloquear |
| `max_photos_count` | 10 | Máximo total por perfil |
| `starting_message_credits` | 100 | "Créditos para iniciar conversación" nuevos, se dan al completar onboarding |
| `super_like_daily_free` | 1 | Super likes gratis/día |
| `super_like_coin_cost` | 20 | Coste en monedas de un Super Like extra |
| `photo_unlock_coin_cost` | 50 | Desbloquear el paquete de fotos ocultas (7) de un perfil |
| `secret_admirer_reveal_coin_cost` | 30 | Revelar identidad de UN admirador secreto |
| `daily_login_coins` | 10 | Monedas por abrir la app cada día (día base, fuera de racha) |
| `streak_rewards` | día1:10💰, día2:15💰, día3:20💰, día4: **5 Super Likes**, día5:25💰, día6:30💰, día7: **50 créditos de mensaje** | Tal cual describe el brief; día 4 se interpreta como "recompensa especial" = Super Likes, ya que el brief no concreta su contenido |
| `new_conversation_rate_limit` | 20 solicitudes nuevas / hora, 60 / día | Antispam; ver `docs/06-security-and-privacy.md` |
| `report_rate_limit` | 10 reportes / día | Evita abuso del sistema de reportes |

## Reglas de negocio no explícitas en el brief

- **Consumo de créditos de mensaje**: se descuenta 1 crédito al *enviar la primera solicitud* a
  un perfil nuevo (no al enviar cada mensaje). Si la persona nunca responde, el crédito no se
  devuelve (evita explotar el sistema reintentando); si responde, el crédito ya se gastó y el
  chat queda abierto sin más coste. Reenviar solicitud a alguien que ya rechazó antes está
  bloqueado 30 días (antispam) salvo que el otro usuario te escriba primero.
- **Fotos bloqueadas**: se desbloquean *todas a la vez* (no una a una) con monedas o con
  Premium, para simplificar la UX y no generar micro-fricción agresiva. Premium desbloquea
  automáticamente las fotos de todo el mundo mientras la suscripción esté activa.
- **Admiradores secretos vs. Quién te ha visto**: "Quién te ha visto" muestra *siempre* que
  alguien vio tu perfil (gratis), pero solo Premium ve *cuándo* con precisión y accede a
  histórico >7 días. "Admiradores secretos" es un subconjunto (gente que te vio 2+ veces o te
  super-likeó pero no ha iniciado conversación) cuya identidad está oculta salvo pago puntual
  (monedas) o Premium. Ningún patrón oscuro: el usuario gratuito siempre sabe cuántos hay antes
  de que se le pida pagar, nunca se le cobra "a ciegas".
- **Superposición Premium / monedas**: Premium no sustituye monedas, son sistemas paralelos
  (suscripción = acceso a features; monedas = consumibles). Un usuario Premium tiene coste 0 en
  las acciones que Premium desbloquea, pero puede seguir gastando monedas en lo que Premium no
  cubre (p. ej. Boost puntual).
- **Boost**: mencionado como "futuro" en el brief; se deja el modelo de datos preparado
  (`profile_boosts`) pero no se construye la UI en este MVP (ver PENDIENTE).

## Tecnología

Ver `docs/02-architecture.md` para la justificación completa. Resumen: **Expo/React Native +
TypeScript** (móvil), **Supabase** (Postgres + Auth + Realtime + Storage + Edge Functions)
como backend, **Next.js** para el panel de administración, monorepo con **npm workspaces**.
