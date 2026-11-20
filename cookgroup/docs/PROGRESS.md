# Registro de progreso (para continuar exactamente donde se dejó)

## Estado a 20-nov-2026 ~12:00 (Madrid)

### 1. Recorrido del cookgroup de referencia (ZESTY CREW)
- **Canales revisados:** 112 de los que publican oportunidades. Lista con mensajes muestreados y fecha más antigua
  alcanzada por canal: `docs/reference_channels.tsv`.
- **Método:** salto a fechas concretas con el ID de mensaje de Discord (que codifica la fecha), en solo lectura.
  - **19 canales agregados** (aio-*, shopify-*, rebajas, mesh, ugg/yeezy especiales, pings, otros-releases…): 4-5 puntos entre hoy y −30 días, con cargas extra hacia atrás. Ventana alcanzada: **19/20-oct → 19-nov**. Algunos llegan más atrás (aio-custom hasta el 2-sep, pings-automaticos hasta el 8-ago).
  - **93 canales de una tienda:** 1-2 puntos para confirmar tienda, dominio y tipo de evento.
- **Resultado:** 436 entradas firmante/dominio → **412 dominios de tienda** (`docs/reference_stores.tsv`, clasificadas en `docs/reference_classified.tsv`).
- **Pendiente en la referencia** (dónde continuar):
  - Canales agregados con mucho volumen (aio-eu, aio-eu-2, aio-world, shopify-eu): en vez de tramos de 10 días, muestrear un punto cada 2 días hacia atrás desde el **20-oct**, porque siguen apareciendo tiendas nuevas.
  - `#important-releases` (foro): el muestreador no recorre hilos de foro. Abrir los hilos uno a uno.
  - Canales de una tienda: solo se vio la ventana actual. Para medir la frecuencia real, muestrear también el −15 y el −30.
  - Categorías sin canal propio visible para esta cuenta (TCG, por rol): no accesibles. No se intenta entrar.

### 2. Monitores
- **Lote 1 (Shopify):** 231 tiendas de la referencia en `config/shopify_stores.csv` (230 activas; milk-store desactivada porque no responde).
  - Verificadas en navegador: 11 de una muestra de 12 (plaza.dk, blackboxstore, shop.rfef.es, 5pm.fr, redgoblin.ro, oneblockdown, flatspot, tascon.es, afew, yellowshop, kith.com).
  - El resto queda como «fuente localizada» hasta que `cookgroup probe` lo confirme en tu PC.
- **Lote 2 (otras fuentes):** RSS Pepper (Mydealz, HotUKDeals, Pepper.pl) y JSON-LD (Snipes ES, Foot Locker ES), todas verificadas.
- **Bloqueadas:** JD Sports (.es/.co.uk). La consulta automatizada falla incluso desde el navegador.

### 3. Siguientes pasos por prioridad
1. **Probar el adaptador JSON-LD** con las tiendas de plataforma propia de mayor volumen en la referencia: aw-lab.com, solebox.com, newbalance.com, schuh.eu, sportsshoes.com, farfetch.com, 24segons.es, warsawsneakerstore.com, elcorteingles.es, aboutyou, breuninger, prm.com, kickz, 43einhalb, basketballemotion, basket4ballers, skatedeluxe, sivasdescalzo, footshop.
   Para cada una hay que localizar la URL del listado y el patrón de las fichas.
2. **Webs de marca:** nike.com (calendario SNKRS en la web), adidas.es, asics.com, newbalance.es, vans.com, ugg.com, timberland.de. Comprobar el JSON-LD de sus fichas y si tienen calendario público.
3. **Zalando y Zalando Privé, Privalia, Amazon:** buscar API de afiliados o programa autorizado. Hoy no hay fuente pública estable.
4. **Investigación propia:** listas oficiales de distribuidores de colaboraciones (New Balance, ASICS, Salomon, Nike/Jordan «stockists») para descubrir raffles fuera de la referencia.
5. **Tiendas físicas en Madrid:** Nike (disponibilidad por tienda) solo vía su API, sin autorización. Buscar fuentes públicas (JSON-LD con `availableAtOrFrom`, páginas de tienda).

### 4. Cómo reanudar el muestreo de la referencia
En la pestaña de Discord del canal, ejecutar el muestreador (código en el historial de esta sesión: `window.__sampleChannel(id, offsets, loads)`)
con desplazamientos mayores que 30 días. Luego regenerar la exportación y ejecutar:
```
python tools/classify_reference.py      # → docs/reference_classified.tsv y config/shopify_stores.csv
python tools/build_inventory.py         # → docs/inventory.csv y docs/inventory.html
```

## Estado a 20-nov-2026 ~12:50 (Madrid) — v0.8, rama `claude/cookgroup-v0.8`
- **Recorrido completo** de la referencia: `docs/v08/reference_sidebar_2026-11-20.txt` (339 canales). Observaciones en `docs/v08/RECORRIDO.md`; tabla en `docs/v08/canales.csv` (`python tools/build_channel_map.py`).
- **Lote 1 (bienvenida, roles y notificaciones): HECHO.** `src/cookgroup/members.py`, `config/miembros.toml`, `tools/lote1.py` (10/10), `tests/test_lote1.py`.
- **Instalador del servidor:** `config/servidor.toml` + `src/cookgroup/server_setup.py` + `INSTALAR_SERVIDOR.bat`. Probado contra un Discord simulado; pendiente del token del bot.
- **Siguiente (en este orden):**
  1. Lote 2, foro de lanzamientos: un hilo por lanzamiento (crearlo con el bot; los webhooks pueden publicar en foros con `thread_name` y en hilos con `thread_id`), actualizarlo si cambia la fecha o aparece una tienda, y la vista de 7 días.
  2. Raffles: apertura, recordatorio, cambio de plazo y cierre; los vencidos fuera de la lista.
  3. Restocks por talla en los lanzamientos de BSTN.
  4. Rebajas por tramos con menciones.
  5. Retomar el histórico de los canales agregados desde el 20-oct y los hilos archivados de #important-releases.
