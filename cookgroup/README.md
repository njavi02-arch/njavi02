# Cookgroup — lanzamientos, raffles, restocks y chollos en Discord (v0.6)

Vigila calendarios de lanzamientos y raffles, catálogos de tiendas y webs de chollos, y te avisa en Discord con
enlace directo, tallas, precio en la moneda original y hora de Madrid. Funciona en tu PC con Windows.

## Ponerlo en marcha (Windows)

Necesitas **Python 3.11+** ([python.org](https://www.python.org/downloads/), marca *"Add python.exe to PATH"*) y
**una URL de webhook** de Discord (Ajustes del canal → Integraciones → Webhooks → Nuevo webhook → Copiar URL).

1. **`INSTALAR.bat`**: instala y abre `.env`. Pega la URL en `DISCORD_WEBHOOK_DEFAULT=` y guarda.
2. **`PROBAR.bat`**: lee todas las tiendas sin avisar, envía **una** alerta de prueba a tu canal y abre la vista previa.
3. **`INSTALAR_AUTOARRANQUE.bat`**: lo deja funcionando en segundo plano y lo vuelve a arrancar cada vez que inicias
   sesión. Si el proceso se cae, se reinicia solo a los 30 s. Pon *Suspensión: Nunca* en Windows (Energía).

Diagnóstico: **`ESTADO.bat`** (último ciclo correcto y errores por tienda, más las últimas líneas del log).
Quitar el arranque automático: `QUITAR_AUTOARRANQUE.bat`. Ver la ventana en directo: `ARRANCAR.bat`.
Logs: `logs/cookgroup.log` (con rotación; la URL del webhook nunca se escribe).

## Qué recibes y dónde

Con solo `DEFAULT` todo llega a un canal. Para organizarlo, crea estos canales y rellena sus webhooks en `.env`:

| Canal | Qué llega |
|---|---|
| 📢 `lanzamientos` | Lanzamiento anunciado · fecha confirmada · fecha cambiada · 🟢 A la venta ahora · resumen del día (09:00) |
| 🎟️ `raffles` | Raffle abierto · enlace nuevo · ⏳ «cierra en X» (3 h antes) |
| 🔄 `restocks` | «Ha vuelto la EU 43 (UK 8.5 / US 9.5)» · bajada de precio en lanzamientos vigilados |
| 🔔 `pings` | Tus reglas: talla, marca, tienda, región, precio máximo, palabras; con mención de rol |
| 👟 `sneakers` / 🌎 `sneakers_world` / 👕 `streetwear` | Catálogos: producto nuevo, restock, tallas, bajadas, posible price error |
| 💸 `rebajas_30` / `rebajas_60` | Copia de alertas con ≥30 % / ≥60 % de descuento |
| 🔥 `chollos` | Chollometro, Dealabs, Mydealz, HotUKDeals, Pepper.pl (solo chollos calientes) |
| 🛹 `skate` / 🏀 `baloncesto` / 🃏 `coleccionables` / 🏷️ `outlet` | Tiendas del lote Shopify según su categoría (TCG: Pokémon, One Piece, Lorcana…) |
| 📆 `releases` | Calendario que edita el staff (`config/releases.toml`) |

En el **primer arranque** no llega una avalancha: el bot guarda lo que existe y manda **un resumen** con los raffles
abiertos y los lanzamientos de los próximos 7 días.

## v0.9 — cookgroup comercial (modo prueba)
- `VER_PANEL.bat`: abre el panel con las pestañas Negocio, Panel del dueño, Alta y baja, Permisos y Mis canales. No necesita Python.
- `PANEL_DUENO.bat`: abre la web local con la página de venta, el alta en modo prueba, la cuenta del cliente y el panel en vivo (`PANEL_PIN`).
- `ENVIAR_PRUEBA.bat`: envía solo a #pruebas-bot. Comprueba servidor y canal antes de enviar y vuelve a leer el mensaje por su ID.
- Guía del dueño: `docs/v09/COMO_OPERO.md` · Apertura: `docs/v09/APERTURA.md` · Plan: `PLAN_MAESTRO.md`.

## v0.7 — qué cambia
Abre **`VER_PANEL.bat`** (o `docs/v07/PANEL.html`): resumen, cifras, piloto, ejemplos de avisos e inventario con buscador.
- `COMPROBAR.bat` lee las fuentes y no envía nada (`COMPROBAR.bat piloto` solo las 6 del piloto; `reanudar` sigue un lote cortado).
- `ENVIAR_PRUEBA.bat` manda 1 mensaje de PRUEBA a tu canal privado (webhook en `.env`).
- `ESTADO.bat` dice si el proceso está vivo y qué fuentes van retrasadas.
- Detalle: `docs/v07/RESUMEN.md`, `docs/v07/COMPARACION_V06.md`, `docs/v07/PILOTO_REGISTRO.md`.

## Tiendas
**260 monitores activos** (230 tiendas Shopify activas de las 231 filas de `config/shopify_stores.csv` + 30 configurados a
mano en `config/monitors.toml`). *Corrección v0.7: v0.6 decía 262 por contar la fila desactivada (milk-store) y 31 monitores
a mano en vez de 30.* Cifras siempre generadas: `python tools/stats.py` → `docs/CIFRAS.md`. Inventario filtrable por tienda, país, categoría, evento y estado: **`docs/inventory.html`**.
Progreso y punto de reanudación: `docs/PROGRESS.md`.

### Configuradas a mano (verificadas el 19/20-nov-2026)
- **Lanzamientos y raffles**: BSTN (calendario completo con fechas y raffles), END. Launches, size? y Footpatrol (colección de lanzamientos).
- **Catálogos Europa**: Footdistrict, Asphaltgold, Overkill, Sneakersnstuff, Family 3.0, Noirfonce, Naked, Kith EU, Slam Jam, Goodhood, Voo Store, Starcow.
- **Catálogos mundo**: Concepts, Undefeated, Social Status, A Ma Maniére, Extra Butter, Up There, Supply Store.
- **Chollos**: Chollometro, Dealabs, Mydealz, HotUKDeals, Pepper.pl.
- **Cadenas sin Shopify (JSON-LD)**: Snipes ES, Foot Locker ES (producto nuevo, vuelta a stock, bajada de precio).

Detalle de cada tienda (región, moneda, qué detecta de verdad y estado): **`docs/STORES.md`**.

## Filtros personales (`[[ping_rule]]` en `config/monitors.toml`)
```toml
[[ping_rule]]
name = "mi-talla-eu43"
keywords = ["*"]                  # todas deben aparecer; "*" = cualquiera
sizes = ["43", "42.5"]            # tallas EU (solo filtra alertas que traen tallas)
brands = ["Nike", "Jordan", "New Balance"]
regions = ["eu"]                  # eu, uk, us, au
max_price = 250
channel = "pings"
role_id = "123456789012345678"    # Discord: Modo desarrollador → clic derecho en el rol → Copiar ID
event_types = ["size_restock", "live", "restock", "new_size", "raffle_open"]
```
Tipos de evento: `announced`, `date_confirmed`, `date_changed`, `raffle_open`, `raffle_link_changed`, `raffle_closing`,
`live`, `size_restock`, `launch_price_drop` (calendarios) · `new_product`, `restock`, `new_size`, `price_drop`,
`price_error` (catálogos).

## Comandos
```
cookgroup probe          # lee todas las fuentes sin enviar nada
cookgroup test-webhook   # una alerta de prueba (--channel raffles para otro canal)
cookgroup status         # diagnóstico por fuente
cookgroup preview        # preview.html con todos los tipos de alerta
cookgroup check-config / check-releases
cookgroup run
```

## Principios
- Solo fuentes públicas pensadas para consultarse: catálogos, listados y RSS. Se respeta `robots.txt`: en BSTN no se
  consultan `/raffle/` ni `/api/`, solo se enlazan.
- Intervalos por fuente (5-15 min) con espera creciente tras errores. No se eluden CAPTCHAs ni bloqueos.
- Un 403, un 429, una página vacía o un listado incompleto **nunca** generan alertas de cierre, cancelación o restock masivo.
- Sin datos no se inventa nada: «N/D» o «la tienda no lo publica».

**Estado:** 113 tests, entre ellos transiciones con muestras reales de BSTN, Family 3.0 y Chollometro, y no duplicación tras
reinicios. Docs: `docs/STORES.md`, `docs/REFERENCE_AUDIT.md`, `docs/FEATURE_MATRIX.md`, `docs/PENDING.md`.
