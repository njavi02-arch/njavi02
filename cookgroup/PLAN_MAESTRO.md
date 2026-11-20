# PLAN MAESTRO · Cookgroup comercial v0.9

Rama `claude/cookgroup-v0.9`, creada desde `claude/cookgroup-v0.8`. Commit de partida comprobado en local y en
remoto: **90a1334**.
Etiquetas de evidencia: «visto en la barra lateral» · «función comprobada» · «implementado» · «probado localmente» ·
«verificado en mi Discord» (reservada a mensajes comprobados en tu servidor).

| # | Bloque | Estado | Evidencia | Bloqueo | Siguiente tarea concreta |
|---|---|---|---|---|---|
| 1 | Auditoría de los 339 canales | en curso | `docs/v08/canales.csv` (339 filas, del recorrido del 20-nov) | — | Leer los 9 foros, los hilos archivados de #important-releases, el market y las herramientas |
| 2 | Propiedad, roles y permisos | en curso | — | token del bot para aplicarlo en Discord | Matriz de permisos + visitante y suscriptor de prueba |
| 3 | Venta de membresías (modo prueba) | pendiente | — | claves de prueba de Stripe y app OAuth de Discord en `.env` | Flujo completo con eventos de Stripe firmados en local |
| 4 | Panel del propietario | pendiente | — | — | Miembros, ingresos, accesos inconsistentes, alertas y tareas |
| 5 | Desarrollo de canales | pendiente | lote 1 hecho en v0.8 | — | Foro de lanzamientos → raffles → restocks por talla → rebajas |
| 6 | Piloto real de Discord | bloqueado | — | DISCORD_BOT_TOKEN / DISCORD_WEBHOOK_PRUEBAS | Corregir ENVIAR_PRUEBA para que solo pueda ir a #pruebas-bot |
| 7 | Apertura comercial | pendiente | — | — | Oferta, costes, guía del dueño y lista de pendientes |

Proyecto Radar: **no existe** entre los repositorios accesibles (búsqueda «radar», 20-nov). La integración de Stripe se
hace desde cero, sin SDK, con verificación de firma propia.
