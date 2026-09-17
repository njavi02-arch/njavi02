# Seguridad, privacidad y anti-spam (FASE seguridad, integrada desde el diseño)

## 1. Principios

La seguridad no se añade al final: cada tabla nace con RLS activada y `deny by default`
(ver `supabase/migrations/0001_init.sql`), y cada mutación económica pasa por una función
`SECURITY DEFINER` auditable, nunca por escritura directa del cliente.

## 2. Reportes y bloqueos

- `reports`: cualquier usuario puede reportar a otro (razón tipada: `spam`, `fake_profile`,
  `inappropriate_content`, `harassment`, `underage`, `other`) opcionalmente ligado a un
  mensaje concreto. Entra en cola de moderación (`status = pending`) visible en el panel admin.
- `blocks`: bloquear es inmediato y bidireccional a nivel de visibilidad — un usuario
  bloqueado desaparece del descubrimiento, no puede iniciar conversación, y sus mensajes
  existentes quedan ocultos (no borrados, para que quede evidencia si hay reporte asociado).
- Reportar con `reason = underage` o `harassment` marca automáticamente el perfil como
  `under_review` y reduce su visibilidad en el feed hasta revisión manual (mitigación
  automática, no elimina la cuenta sin revisión humana).

## 3. Moderación de contenido

- Fotos: `photos.moderation_status` (`pending → approved/rejected`). En este MVP la
  moderación es **manual desde el panel admin** (cola con aprobar/rechazar); el modelo de
  datos deja el campo `moderation_notes`/`moderated_by` listo para conectar un servicio de
  moderación automática de imágenes (p. ej. detección de NSFW) sin cambiar el esquema — no se
  contrata ningún servicio de terceros sin autorización explícita (implicaría coste).
- Bios/mensajes: filtro básico de palabras prohibidas configurable (`app_config.banned_words`)
  aplicado en el Edge Function `start-conversation` antes de crear una solicitud — bloquea
  contenido evidentemente abusivo sin sustituir la moderación humana.

## 4. Anti-spam / rate limiting

Función `check_and_record_rate_limit(profile_id, action_type, max_count, window)` (Postgres,
`SECURITY DEFINER`) usada por las Edge Functions antes de cada acción sensible:

| Acción | Límite por defecto | Configurable en |
|---|---|---|
| Nuevas solicitudes de conversación | 20/hora, 60/día | `app_config.new_conversation_rate_limit` |
| Super Likes enviados | según saldo + 1 gratis/día (no es "spam" en sí, pero se limita igual a ráfagas) | `app_config.super_like_daily_free` |
| Reportes emitidos | 10/día | `app_config.report_rate_limit` |
| Cambios de foto de perfil | 10/día | `app_config.photo_upload_rate_limit` |
| Intentos de login fallidos | delegado a Supabase Auth (lockout nativo) | Supabase dashboard |

Cuentas nuevas (<48h desde registro) tienen límites más estrictos (multiplicador
`new_account_rate_limit_factor = 0.3` sobre las tablas anteriores) para frenar creación masiva
de cuentas usadas para enviar spam inmediatamente tras registrarse.

Señales adicionales para `suspicious_activity_flags` (no bloquean automáticamente, alimentan
la cola de revisión del panel admin): ráfaga de solicitudes idénticas a múltiples receptores
en poco tiempo, tasa de "ignorado" anormalmente alta, múltiples cuentas desde el mismo hash de
dispositivo/IP (se almacena **hash**, nunca la IP en claro, para minimizar datos personales
retenidos).

## 5. Protección de menores

- Edad mínima dura de 18 años verificada en el registro (fecha de nacimiento, no checkbox de
  autodeclaración simple) — un usuario que declara <18 no puede completar el registro.
- No se ofrece ningún mecanismo de "modo adolescente" ni variante para menores: la app
  simplemente no admite su registro. Esto es una decisión de producto para reducir riesgo
  legal y de seguridad, coherente con `ASSUMPTIONS.md #3`.
- El reporte con motivo `underage` prioriza revisión manual inmediata en el panel admin.

## 6. Privacidad y RGPD (borrador técnico — requiere revisión legal antes de producción)

Lo que la arquitectura ya soporta:
- **Minimización de datos**: ubicación se guarda como ciudad + coordenadas aproximadas
  (redondeadas), nunca tracking continuo de GPS.
- **Derecho de acceso/portabilidad**: estructura relacional permite generar un export por
  `profile_id` (pendiente de construir el endpoint concreto, ver PENDIENTE).
- **Derecho al olvido**: borrado de cuenta = soft delete + anonimización inmediata de campos
  identificables, purga física tras periodo de gracia (ver `03-database.md §2`).
- **Consentimiento**: tabla `notification_preferences` y flags de consentimiento de
  marketing/analítica separados del consentimiento de términos de servicio (no se puede
  "empaquetar" un consentimiento con otro).
- **Base legal y textos**: Términos de Servicio y Política de Privacidad **no se redactan
  aquí** — son documentos legales que debe validar un profesional; se deja
  `apps/mobile/src/screens/legal/` con placeholders claramente marcados como
  `[PENDIENTE DE REVISIÓN LEGAL]` para que el equipo legal los rellene antes de publicar.

## 7. Qué falta para producción real (ver también `07-roadmap-and-scaling.md`)

Verificación de identidad, moderación automática de imágenes con IA, pentesting antes de
lanzamiento, política formal de retención de datos y DPA con subencargados (Supabase, hosting
de imágenes), auditoría legal RGPD completa.
