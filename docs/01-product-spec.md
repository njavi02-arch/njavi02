# Orbita — Especificación de producto (FASE 1)

> Nombre provisional de marca — ver `ASSUMPTIONS.md #1`. En el código se usa `APP_NAME`
> como constante única para poder renombrar en un solo sitio.

## 1. Visión

Orbita es una aplicación social móvil cuyo núcleo **no es el "match" sino la conversación**.
El bucle central es:

```
DESCUBRIR → INTERACTUAR → CONSEGUIR RESPUESTA → CONVERSAR → (amistad | conocer gente | ligar,
si ambas personas quieren)
```

A diferencia de un swipe-to-match clásico, cualquier usuario puede intentar iniciar una
conversación directamente con un mensaje real ("Hola, ¿qué tal?"), no solo dar "like" y
esperar. El match no es la meta — es un efecto secundario opcional cuando ambas partes quieren
algo romántico.

## 2. Problema y propuesta de valor

- Las apps de citas clásicas fuerzan una intención romántica desde el primer segundo, lo que
  excluye a quien solo quiere conocer gente o hacer amigos.
- Los sistemas de "match mutuo antes de poder hablar" generan fricción y salas de espera
  infinitas (muchos matches, cero conversación).
- Orbita prioriza **la conversación como objetivo medible del producto**: la métrica estrella
  no es "matches" sino "conversaciones iniciadas → respondidas → activas a 7 días".

## 3. Público objetivo

- Adultos 18+ (ver `ASSUMPTIONS.md #3`), predominantemente 18-32, en entornos urbanos,
  cómodos con apps sociales tipo Instagram/TikTok/Wizz.
- Tres intenciones conviven en la misma base de usuarios: amistad, socializar/conocer gente,
  citas — el usuario declara su intención en el onboarding pero puede tener varias a la vez.

## 4. Bucle central de experiencia (primeros 30 segundos y ciclo recurrente)

```
Registro → Crear perfil (rápido) → Descubrir personas → Ver perfil → Enviar mensaje
   → Recibir respuesta → Entrar al chat → Volver a descubrir
```

Diseño orientado a que un usuario nuevo pueda completar registro + perfil mínimo + primer
mensaje enviado en menos de 3 minutos, y reciba su primera notificación de actividad (vista de
perfil, respuesta, super like) idealmente en la primera sesión.

## 5. Funcionalidades del MVP (alcance de esta build)

1. **Autenticación** — email/password vía Supabase Auth (arquitectura lista para añadir
   OAuth de Google/Apple más adelante; Apple Sign-In es obligatorio por App Store si se
   añade cualquier login social, así que se implementará ese conjunto completo o ninguno).
2. **Onboarding guiado** — 10 pasos tal como se describe en el brief (sección 20).
3. **Descubrimiento de personas** — feed de cards con foto, nombre, edad, ciudad, bio,
   intereses; acciones: Hablar, Super Like, Ver perfil.
4. **Solicitudes de conversación** ("Te han hablado") — bandeja de solicitudes entrantes con
   Responder/Ignorar; al responder se crea un chat normal.
5. **Chat en tiempo real** — texto, fotos, emoji, enviado/recibido/leído, "escribiendo...",
   bloquear, reportar, eliminar, silenciar.
6. **Perfil propio y ajeno** — galería con 3 fotos públicas + resto bloqueado, bio, intereses,
   estadísticas sociales, edición.
7. **Super Likes** — envío, límite diario gratuito, compra con monedas.
8. **Monedas + recompensa de racha de 7 días** — login diario, racha, recompensas crecientes,
   día 7 = 50 créditos de mensaje.
9. **Créditos de mensaje ("100 mensajes")** — consumo solo al iniciar conversación nueva, no
   por mensaje dentro de un chat ya abierto.
10. **Quién te ha visto** y **Admiradores secretos** — con gate freemium tal como se describe
    en `ASSUMPTIONS.md`.
11. **Premium (estructura)** — entidad de suscripción, gates de features, sin checkout de pago
    real conectado todavía (ver PENDIENTE) pero con simulación de compra vía monedas de
    prueba/admin para poder probar el flujo end-to-end.
12. **Seguridad** — bloqueo, reporte, rate limiting anti-spam, RLS en toda la base de datos,
    señales automáticas de cuentas sospechosas por acumulación de reportes.
13. **Panel de administración** — usuarios, contenido/reportes, verificación de perfiles,
    configuración económica (`app_config`), sin valores hardcodeados.
14. **Verificación de perfil** — selfie + cola de moderación manual, badge ✅ visible en
    Descubrir/perfil (añadido tras investigar el patrón estándar del sector — ver
    `PRODUCT_BRAIN.md`).
15. **Prompts de perfil + sugerencias de primer mensaje** — hasta 3 prompts por perfil;
    sugerencias de icebreaker por interés compartido en el composer de "Hablar".
16. **Boost de visibilidad** — pagado con monedas (no dinero real), aparece primero en
    Descubrir durante un tiempo limitado.
17. **Estado de actividad** — "Activo ahora"/"Activo hoy" en tarjetas y perfil, y aviso de
    racha en riesgo para no perder la recompensa diaria.
18. **Reacciones a mensajes** — una reacción (de 6 emojis) por persona y mensaje en el chat,
    tipo tapback de iMessage/WhatsApp (patrón investigado en Wizz), sincronizada en tiempo
    real entre ambos participantes.

Ver `PRODUCT_BRAIN.md` para el porqué de cada una de estas últimas (14-18 se añadieron en
una ronda de investigación de mercado posterior al MVP inicial, no estaban en el brief
original palabra por palabra pero responden directamente a la regla de producto de la
sección 46: ayudan a iniciar conversaciones, mejoran la confianza/calidad de usuarios, mejoran
el chat, o dan un nuevo destino de gasto a la economía ya construida).

### Explícitamente fuera de este MVP (ver `07-roadmap-and-scaling.md`)

- Pasarela de pago real (Stripe/RevenueCat) — se deja la interfaz y el modelo de datos
  listos, pero no se contratan servicios de pago sin autorización explícita del usuario
  (implica coste económico real, fuera de lo que la autonomía concedida permite decidir sola).
- Verificación de identidad/selfie liveness.
- Boost de visibilidad (UI).
- Geolocalización precisa en tiempo real (se usa ciudad/aprox., ver `06-security-and-privacy.md`).
- Notificaciones push reales entregadas a dispositivo (se deja el pipeline completo: tokens,
  tabla, Edge Function trigger; falta el paso de credenciales FCM/APNs, que requiere cuentas
  de desarrollador externas).

## 6. Estructura de navegación

Ver `04-ux-ui-flows.md`. Resumen: `Descubrir · Mensajes · Actividad · Perfil` (bottom tabs).

## 7. Sistema de conversación (detalle funcional)

1. Usuario A pulsa "Hablar" sobre el perfil de B y escribe un primer mensaje.
2. Se crea un registro en `conversation_requests` (estado `pending`), se descuenta 1 crédito
   de mensaje de A, se dispara notificación push/in-app a B.
3. B ve la solicitud en su bandeja "Te han hablado" con el mensaje visible de A.
4. B puede **Responder** (crea `conversations` + primer `messages`, estado `accepted`) o
   **Ignorar** (estado `declined`, desaparece de la bandeja activa de B, queda archivada).
5. Una vez `accepted`, es un chat normal: sin coste adicional por mensaje, con lectura,
   tipeo, adjuntos, etc.
6. Si B no responde en 30 días, la solicitud pasa a `expired` automáticamente (job programado).

## 8. Fotos

- Hasta 10 fotos por perfil; **3 primeras siempre públicas**, el resto oculto tras
  `+7 fotos 🔒` (contador dinámico según cuántas suba el usuario).
- El desbloqueo es una acción del **espectador**, no del dueño del perfil: cualquiera puede
  pagar monedas o ser Premium para ver las fotos ocultas de un perfil que le interesa.
- Todas las fotos pasan por un pipeline de moderación (`photos.moderation_status`) antes de
  ser públicas — ver `06-security-and-privacy.md`.

## 9. Gamificación (resumen — detalle económico en `ASSUMPTIONS.md`)

Monedas, Super Likes, racha de 7 días con recompensas crecientes, nivel de "perfil completado"
(%), y logros básicos (primer mensaje enviado, primera respuesta recibida, 7 días de racha,
perfil 100% completo). La gamificación está para reforzar el bucle central, no para
sustituirlo: ningún logro bloquea la funcionalidad básica de conversar.

## 10. Monetización (resumen — detalle en `07-roadmap-and-scaling.md`)

Premium (suscripción), compra de monedas, compra de packs de Super Likes, Boost (futuro).
Todos los precios y cantidades son configurables desde el panel de administración
(`app_config`), nunca hardcodeados.

## 11. Seguridad y privacidad (resumen — detalle en `06-security-and-privacy.md`)

Reportes, bloqueos, moderación de contenido, rate limiting anti-spam, RLS de base de datos,
edad mínima 18, eliminación de cuenta, base preparada para cumplimiento RGPD (pendiente de
revisión legal profesional).

## 12. Métricas de éxito (para iterar tras el MVP)

- % de solicitudes de conversación que reciben respuesta en <24h.
- Conversaciones activas a 7 días / usuarios registrados.
- Tiempo hasta el primer mensaje enviado (objetivo: <3 min desde registro).
- Retención D1/D7/D30, tasa de reclamo de racha diaria.
- Conversión free→premium, ARPU, LTV/CAC (cuando exista monetización real).
