# PLAN MAESTRO · Cookgroup comercial v0.9

Rama `claude/cookgroup-v0.9`, creada desde `claude/cookgroup-v0.8`. Commit de partida comprobado en local y en remoto:
**90a1334**.
Niveles de evidencia: visto en la barra lateral → función comprobada → implementado → probado localmente →
**verificado en mi Discord** (solo con mensajes comprobados en tu servidor).

| # | Bloque | Estado | Evidencia | Bloqueo | Siguiente tarea concreta |
|---|---|---|---|---|---|
| 1 | Auditoría de los 339 canales | **hecho (lectura)** | `docs/v08/canales.csv` con nivel de evidencia y dependencia; `docs/v09/AUDITORIA.md` (9 foros, market, herramientas de terceros) | — | Hilos archivados más antiguos de #important-releases e histórico de los agregados desde el 20-oct |
| 2 | Propiedad, roles y permisos | **probado localmente** | `src/cookgroup/access.py`, `tests/test_access.py`, matriz con 6 identidades (pestaña Permisos) | token del bot para aplicarlo en Discord | INSTALAR_SERVIDOR.bat y comprobar con 2 cuentas reales (visitante y suscriptor) |
| 3 | Venta de membresías (modo prueba) | **probado localmente** | `docs/v09/MEMBRESIAS_REGISTRO.md`: 18/18 (alta, baja, renovación, fallo, duplicado, firma falsa, Discord caído) | claves `sk_test_`, precio, webhook y app OAuth de Discord | Repetir el recorrido con Stripe en modo prueba real (`stripe listen`) |
| 4 | Panel del propietario | **probado localmente** | `/admin` de la web local (PIN, reintento auditado); demo en la pestaña «Panel del dueño» | — | Conectarlo a tu base real cuando haya clientes |
| 5 | Desarrollo de canales | **15 de 33 probados localmente** | `docs/v09/CANALES_MI_SERVIDOR.csv`, `docs/v09/CANALES_REGISTRO.md` (15/15) | fuentes autorizadas (LEGO, electrónica, Madrid); responsables humanos | Prueba propia para sneakers-mundo, baloncesto, skate, outlet, streetwear y pokémon-tcg; foros por expansión TCG |
| 6 | Piloto real de Discord | **bloqueado** | ENVIAR_PRUEBA solo puede ir a #pruebas-bot; comprueba antes y después (`tests/test_real_delivery.py`) | DISCORD_BOT_TOKEN, DISCORD_GUILD_ID (+ INSTALAR_SERVIDOR) | Primer mensaje real y su ID en `docs/v09/ENTREGAS_REALES.csv` |
| 7 | Apertura comercial | **lista para decidir** | `docs/v09/APERTURA.md` (oferta, costes, qué se puede anunciar, pendientes) y `docs/v09/COMO_OPERO.md` | tu decisión sobre precio, hosting y textos legales | Revisar oferta y costes; decidir fecha |

Proyecto Radar: **no existe** entre los repositorios accesibles (búsqueda «radar», 20-nov). La integración de Stripe se
hizo desde cero, sin SDK.
