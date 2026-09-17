# PRODUCT_BRAIN — Orbita

> Documento vivo. Se actualiza durante el desarrollo, no es una foto fija del día 1.
> Última actualización: sesión de desarrollo autónomo, fase de investigación continua.

## VISIÓN

Una app social donde el objetivo medible no es el match sino **la conversación**: iniciarla,
conseguir respuesta y mantenerla viva. Amistad, conocer gente o citas son destinos posibles,
nunca el único punto de entrada. Si un usuario nuevo no ha enviado un primer mensaje en sus
primeros 3 minutos en la app, hemos fallado, independientemente de cuántos "matches" tenga.

## PRINCIPIOS

1. **La conversación es la métrica estrella**, no el número de matches ni de swipes.
2. **Sin patrones oscuros**: el usuario gratuito siempre sabe qué existe (admiradores,
   fotos bloqueadas) antes de que se le pida pagar — nunca un muro sorpresa.
3. **Sin puntuación oculta de "deseabilidad"**: decisión explícita de diferenciación frente
   a Tinder (ver INVESTIGACIÓN). El orden de descubrimiento es transparente: actividad
   reciente + intereses compartidos, nunca un ELO oculto que decide quién ve a quién.
4. **La seguridad no es una capa añadida al final**: RLS desde la primera migración,
   moderación y reportes desde el primer commit.
5. **Nunca simular una funcionalidad conectada a datos reales.** Si algo no se puede
   conectar todavía (pago real, credenciales push), se dice explícitamente en la UI en vez
   de fingir que funciona.
6. **Cada funcionalidad nueva debe responder "sí" a al menos una pregunta** (regla del
   brief, sección 46): ¿ayuda a descubrir personas? ¿ayuda a iniciar conversaciones?
   ¿ayuda a conseguir respuestas? ¿mejora el chat? ¿mejora la seguridad? ¿mejora la
   retención? ¿mejora la monetización sin destruir la experiencia? ¿mejora la calidad de
   usuarios/conversaciones? Si no, no es prioridad, por muy de moda que esté en otra app.

## INVESTIGACIÓN

Resumen de lo estudiado (fuentes en cada búsqueda de esta sesión; nunca se ha copiado
diseño, código ni texto — solo se han extraído patrones y problemas de UX):

### Wizz
Descubrimiento por swipe **de gente conectada ahora mismo**, chat en vivo (texto y video),
reacciones a mensajes, notas de voz, verificación de edad biométrica + moderación por IA,
gratis. El insight central: **priorizan la disponibilidad inmediata** sobre el catálogo
completo — hablas con quien puede responder ya, no con un perfil que no ha abierto la app
en dos semanas.

### Tinder
Super Like (prioriza tu perfil ante esa persona), Boost (10x/100x visibilidad 30 min),
scoring de "deseabilidad" tipo ELO que decide qué perfiles ve cada quien — señalado en la
propia prensa del sector como generador de escasez artificial y opacidad. ~80% de sus
ingresos vienen de suscripción, el resto de Boosts/Super Likes/publicidad. **Oportunidad de
diferenciación clara**: nosotros no ocultamos por qué apareces o no en el feed de alguien.

### Bumble
Verificación de foto por selfie con gesto específico (badge filtrable), "Icebreaker"
(sugerencia automática de tema cuando nadie sabe qué decir) y "Opening Move" (la usuaria
escribe una pregunta una vez y se reutiliza como primer mensaje automático para reducir la
fricción de "quién escribe primero"). Su detector de decepción con IA bloqueó ~95% de
perfiles spam/scam en pruebas. Bumble decidió **no mostrar "última conexión"** por
privacidad — Hinge sí, con dos niveles ("Activo ahora" / "Activo hoy"); Tinder usa un punto
verde a 2h y "activo recientemente" a 24h.

### Yubo
Discovery por intereses (tags), verificación de edad obligatoria al 100% de usuarios,
moderación humana en tiempo real de contenido en vivo. No aplicable a Orbita (no tenemos
video en directo) pero refuerza la idea de que la seguridad para audiencias jóvenes exige
verificación real, no solo autodeclaración — ya implementado en nuestro caso con fecha de
nacimiento estricta + edad mínima dura de 18.

### Hinge
Prompts de perfil (preguntas cortas que la persona elige responder, no huecos genéricos de
bio) y "Convo Starters" con IA que sugiere de qué hablar según la foto/prompt concreto de la
otra persona. La parte de IA generativa personalizada requiere un servicio de pago externo
(fuera de alcance autónomo); la parte de **prompts de perfil + sugerencias curadas por
intereses compartidos** es perfectamente construible ya con nuestro modelo de datos.

### Patrones transversales de seguridad
Los bots ya no se detectan bien por imagen inversa (las fotos ahora son generadas por IA);
la defensa real es conductual: cooldowns y periodos de prueba para cuentas nuevas
sospechosas (que ya tenemos vía `new_account_rate_limit_factor`), y limitar visibilidad
hasta que una cuenta demuestre comportamiento normal.

### Gamificación y retención
Las apps que combinan rachas + hitos ven un 40-60% más de DAU que las que solo usan una
mecánica; una racha de 7+ días hace que un usuario vuelva ~2,3x más. Confirma que nuestro
sistema de racha de 7 días (ya construido) es una apuesta acertada — el hueco real es que
**nunca avisamos si la racha está a punto de romperse**, justo el mecanismo de aversión a la
pérdida que hace funcionar a Duolingo.

## MATRIZ DE FUNCIONALIDADES (uso interno, no determinismo automático)

| Funcionalidad | Orbita | Wizz | Tinder | Bumble | Hinge/Yubo | Aporta a... |
|---|---|---|---|---|---|---|
| Descubrimiento por actividad reciente | ✓ | ✓ (online ahora) | ✓ (scoring oculto) | ✓ | ✓ | Descubrir |
| Solicitud de conversación con mensaje | ✓ | - (chat directo) | - | Parcial (Opening Move) | - | Iniciar conversación |
| Chat tiempo real + fotos + reacciones | Parcial (sin reacciones) | ✓ | ✓ | ✓ | ✓ | Chat |
| Monedas | ✓ | - | - | - | - | Monetización |
| Super Like | ✓ | - | ✓ | - | - | Conseguir respuesta |
| Boost | Tabla lista, sin UI | - | ✓ | - | - | Monetización |
| Admiradores secretos | ✓ | - | - | - | - | Retención/monetización |
| Racha diaria | ✓ | - | - | - | - | Retención |
| Verificación de perfil (selfie) | ✗ | ✓ (biométrica) | ✓ | ✓ | ✓ | Seguridad/calidad |
| Estado "activo ahora" / última conexión | ✗ (dato existe, sin UI) | ✓ | ✓ | ✗ (decisión de privacidad) | ✓ | Descubrir/respuesta |
| Prompts de perfil / icebreakers | ✗ | - | - | ✓ | ✓ | Iniciar conversación |
| Señales automáticas de cuentas sospechosas | Tabla lista, sin lógica | - | ✓ (IA) | ✓ (IA) | - | Seguridad |

## DECISIONES (de esta ronda de investigación)

1. **No implementar scoring oculto de deseabilidad.** Descubrimiento ordenado por actividad
   reciente + intereses compartidos, visible y explicable. Es una decisión de producto, no
   solo técnica: la opacidad de Tinder es un problema de UX señalado por la propia prensa
   del sector, y contradice nuestro principio de "sin patrones oscuros".
2. **Verificación de perfil = selfie + cola de moderación manual**, no reconocimiento facial
   automático de terceros (implicaría contratar un servicio externo con coste real). Reutiliza
   la infraestructura de moderación que ya existe en el panel admin para fotos/reportes.
3. **Icebreakers = prompts de perfil + sugerencias curadas por interés compartido**, no IA
   generativa (Hinge necesita un servicio de pago externo para eso). Sigue sirviendo al
   mismo objetivo — reducir la fricción de "no sé qué escribir" — con lo que ya tenemos.
4. **Boost se paga con monedas, no con dinero real.** Evita depender de la pasarela de pago
   pendiente y le da a las monedas un nuevo destino de gasto además de Super Likes y
   desbloqueo de fotos.
5. **Estado "activo ahora"/"activo hoy" sí, "visto por última vez" exacto no.** Punto medio
   entre el enfoque de Hinge (útil para saber si vale la pena escribir) y la privacidad de
   Bumble (nunca mostramos la hora exacta de la última conexión a otro usuario).

## FUNCIONALIDADES (estado tras esta sesión de investigación — antes de implementar lo nuevo)

Ver `docs/01-product-spec.md` para el detalle completo. Resumen de lo ya construido y
probado: auth, onboarding 7 pasos, descubrimiento, perfil con fotos bloqueadas, solicitudes
de conversación (atómicas), chat en tiempo real con fotos, monedas, racha de 7 días, Super
Likes, quién-te-ha-visto, admiradores secretos, notificaciones (bandeja + push), bloqueo/
reporte, panel admin completo, CI.

## IDEAS (descubiertas en investigación, evaluadas contra la REGLA DE PRODUCTO)

| Idea | ¿A qué pregunta responde? | Decisión |
|---|---|---|
| Estado activo ahora/hoy | Descubrir + conseguir respuesta | **Construir ya** — dato ya existe, coste bajísimo |
| Verificación de perfil | Seguridad + calidad | **Construir ya** — reutiliza infra de moderación |
| Prompts de perfil + icebreakers sugeridos | Iniciar conversación | **Construir ya** — núcleo de la propuesta de valor |
| Aviso de racha en riesgo | Retención | **Construir ya** — cierra un hueco real (enum sin usar) |
| Boost pagado con monedas | Monetización | **Construir ya** — reutiliza tabla ya existente |
| Señales automáticas de cuentas sospechosas | Seguridad | **Construir ya** — cierra hueco real (tabla sin lógica) |
| Reacciones a mensajes (Wizz) | Mejora el chat | **Construida** — una reacción por persona y mensaje, con RLS y Realtime |
| Video/voz en directo (Yubo) | Descubrir | Descartado — cambia el modelo de infraestructura por completo |
| IA generativa para sugerir conversación (Hinge) | Iniciar conversación | Descartado por ahora — requiere servicio de pago externo |
| Grupos/eventos sociales | Descubrir | Backlog — no mencionado en el brief, evaluar demanda real primero |
| Rankings/niveles públicos | Retención | Descartado — puede generar comparación tóxica, contradice principio 2 |

## PROBLEMAS (detectados y su estado)

- ~~Bloqueo no era bidireccional (bug de RLS recursivo)~~ — corregido.
- ~~`profile_completion_pct` nunca se calculaba~~ — corregido con trigger.
- ~~Silenciar/archivar chat afectaba al usuario equivocado~~ — corregido.
- ~~Solicitudes/Super Likes no atómicos~~ — corregidos con funciones SECURITY DEFINER.
- ~~`profiles.last_active_at` nunca se actualizaba~~ (detectado investigando el patrón
  "activo ahora/hoy" de Hinge/Tinder) — corregido: `touchLastActive()` + heartbeat cada 3
  min en primer plano. Sin esto, el orden "más activos primero" del feed no significaba
  nada desde el primer commit.
- ~~`suspicious_activity_flags` existía sin ninguna lógica que escribiera en ella~~ —
  corregido: trigger de acumulación de reportes (3+/30 días → señal; 5+/30 días → revisión
  automática), sin depender de IA de terceros.
- ~~`streak_at_risk` era un tipo de notificación que nunca se disparaba~~ — corregido
  (`notify_streak_at_risk_if_needed()`, deduplicado a 1/día) + banner en Descubrir.
- ~~No había verificación de perfil~~ — corregido: selfie + cola de moderación manual en
  el panel admin, badge ✅ automático al aprobar.
- ~~Fake profiles/desconfianza no tenían ninguna señal visible en el perfil~~ — el badge de
  verificado y "Destacado" (Boost) dan señales visuales que la investigación de mercado
  identifica como relevantes para la confianza del usuario.
- ~~`user_preferences` (edad mín/máx, género que se busca) se capturaba en el onboarding pero
  el feed de descubrimiento nunca lo aplicaba~~ — el mismo patrón de bug que
  `last_active_at`/`profile_completion_pct`: el dato existía, nadie lo leía. Corregido:
  `fetchDiscoverProfiles()` ahora filtra por rango de `birth_date` (lógica pura y probada en
  `packages/shared/discoveryFilters.ts`) y `gender`, y hay una pantalla real en
  Ajustes → "Preferencias de descubrimiento" para poder cambiarlas después del onboarding
  (antes no existía ninguna forma de editarlas una vez completado el registro).

## OPORTUNIDADES

- El propio Tinder es criticado en la prensa del sector por su opacidad de scoring — Orbita
  puede usar "por qué apareces en el feed de alguien" como argumento de marketing honesto
  ("sin scoring oculto") una vez tenga usuarios reales.
- El "Opening Move" de Bumble resuelve un problema que Orbita ya resuelve de otra forma
  (cualquiera puede escribir primero con un mensaje real) — nuestra propia solución al mismo
  problema, sin copiarla, es más simple y ya está construida.
- Las apps que muestran verificación de forma filtrable (Bumble) convierten la verificación
  en una ventaja competitiva visible, no solo en un sello decorativo — al construir la
  nuestra, dejar preparado un filtro "solo verificados" en preferencias de descubrimiento
  (aunque el MVP no lo exponga todavía en UI).

## ROADMAP DINÁMICO

### Completado en esta sesión (investigación → decisión → construcción → prueba)

1. ~~Estado activo ahora/hoy en Descubrir y perfil~~ — construido, probado (7 tests).
2. ~~Aviso de racha en riesgo~~ — banner + notificación deduplicada, construido y probado.
3. ~~Verificación de perfil~~ — selfie + cola de moderación admin, construido y probado
   (4 escenarios reales contra la base de datos).
4. ~~Prompts de perfil + sugerencias de primer mensaje~~ — construido y probado (6 tests +
   3 escenarios de base de datos, incluido un bug real de "editar tu 3er prompt te bloquea
   a ti mismo" encontrado y corregido antes de llegar a producción).
5. ~~Boost pagado con monedas~~ — construido y probado (4 escenarios: cobro, bloqueo de
   doble activación, orden de aparición en el feed).
6. ~~Señales automáticas de cuentas sospechosas~~ — construido y probado (4 escenarios:
   umbral de señal, no duplicar, escalado a revisión automática).
7. ~~Reacciones a mensajes en el chat~~ (patrón Wizz — tapback tipo iMessage/WhatsApp, una
   reacción por persona y mensaje, no acumulable) — `message_reactions` con RLS espejo de
   `messages` (solo participantes ven/reaccionan), long-press en el mensaje abre el selector
   de 6 emojis, badges agregados por emoji bajo cada burbuja, sincronizado en tiempo real vía
   Realtime entre ambos participantes. Construido y probado (4 escenarios reales: reaccionar,
   unicidad por persona/mensaje, aislamiento por RLS frente a terceros, cambiar la propia
   reacción).

8. ~~Filtro "solo verificados" + aplicar de verdad edad/género en el feed~~ — `user_preferences.
   verified_only` (nueva columna) + corrección del bug real de que edad/género nunca se
   aplicaban al feed (ver PROBLEMAS) + pantalla de edición en Ajustes. Construido y probado
   (3 escenarios reales de integración contra Postgres + 6 tests unitarios de la aritmética
   de fechas de `discoveryFilters.ts`).
9. ~~Exportación de datos personales (RGPD)~~ — `export_my_data()`, SECURITY DEFINER acotada
   siempre a `auth.uid()` (nunca puede exportar los datos de otra persona), con UI real en
   Ajustes que escribe el JSON a un archivo y lo comparte vía el share sheet nativo
   (`expo-file-system` + `expo-sharing`, dependencias nuevas instaladas esta ronda).
   Construido y probado (6 escenarios reales contra Postgres, incluido que el export de una
   persona nunca incluye los reportes que otros presentaron contra ella).

Total tras esta sesión: 69 escenarios de base de datos reales + 49 tests unitarios de
`packages/shared`, todos en verde (ver `docs/05-mvp-scope-and-testing.md`).

### Siguiente (no abordado todavía, con criterio de prioridad)

1. **Edge Functions con moderación de texto por IA** — cuando haya presupuesto para un
   servicio externo; hasta entonces, el filtro de `banned_words` cubre el caso básico.
2. **Captura real de geolocalización** — `max_distance_km` sigue sin aplicarse: se captura en
   el onboarding pero ningún flujo rellena `profiles.latitude/longitude` todavía. Requiere
   permiso de ubicación + geocodificación, evaluar coste/beneficio y privacidad antes de
   construir (ver `06-security-and-privacy.md`).
3. **Grupos/eventos sociales** — backlog, sin señal de demanda todavía, evaluar tras tener
   usuarios reales antes de construir.
