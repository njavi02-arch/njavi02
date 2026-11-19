# Cookgroup — monitores de sneakers, streetwear y chollos con alertas en Discord (v0.4)

## Arrancar en Windows (3 pasos)

Necesitas **Python 3.11+** ([python.org](https://www.python.org/downloads/), marca *"Add python.exe to PATH"*) y un
**webhook** de Discord (Ajustes del canal → Integraciones → Webhooks → Nuevo webhook → Copiar URL).

1. Doble clic en **`INSTALAR.bat`** → se abre `.env`: pega la URL en `DISCORD_WEBHOOK_DEFAULT=` y guarda.
2. Doble clic en **`PROBAR.bat`** → comprueba tiendas y feeds, manda un mensaje de prueba a tu canal y abre la vista previa.
3. Doble clic en **`ARRANCAR.bat`** → monitores en marcha (déjalo abierto; Ctrl+C para parar).

Linux/Mac/VPS: `./iniciar.sh`. Docker: `docker compose up -d --build`.

Con solo `DISCORD_WEBHOOK_DEFAULT` todo llega a un canal. Para separar por canales rellena en `.env`
`DISCORD_WEBHOOK_SNEAKERS`, `_STREETWEAR`, `_CHOLLOS`, `_REBAJAS_30`, `_REBAJAS_60`, `_RELEASES`, `_PINGS`.

## Qué monitoriza (verificado el 19-nov-2026)

| Canal | Fuentes | Qué avisa |
|---|---|---|
| sneakers | Footdistrict, Asphaltgold, Overkill, Sneakersnstuff, Family 3.0, Noirfonce, Naked | Restock, producto nuevo, tallas nuevas, bajadas, posible price error (solo marcas de calzado, sin tallas/modelos de niño) |
| streetwear | Kith EU, Slam Jam, Goodhood, Voo Store, Starcow | Lo mismo para ropa |
| rebajas_30 / rebajas_60 | (copias de las anteriores) | Alertas con ≥30 % / ≥60 % de descuento |
| chollos | Chollometro (hot, ≥100°), Dealabs (hot, ≥150°) | Chollos nuevos con tienda, precio y temperatura |
| releases | `config/releases.toml` (lo edita el staff) | Recordatorios 1 día / 1 h / 10 min y resumen diario 08:00 |
| pings | reglas `[[ping_rule]]` | Menciona a un rol si un producto cumple palabras + precio máx. |

Todo se configura en `config/monitors.toml`. La primera vuelta de cada tienda **solo guarda el catálogo** (no avisa de todo como nuevo).

## Comandos
```
cookgroup probe          # comprueba todas las fuentes sin enviar nada
cookgroup test-webhook   # mensaje de prueba al webhook (--channel sneakers para otro)
cookgroup preview        # preview.html con todos los tipos de alerta
cookgroup check-config   # valida monitors.toml
cookgroup check-releases # valida el calendario
cookgroup run            # arranca
```

## Principios
Solo fuentes públicas pensadas para consumirse (catálogo `/products.json` de Shopify, feeds RSS) con intervalos
conservadores; no se eluden CAPTCHAs, antibots ni límites (ante 403/429 el monitor espera). Nada se inventa:
sin dato → "N/D". El beneficio solo se muestra con dato de mercado verificado en `config/market_data.json`.

**Estado:** 74 tests (muestras reales del 19-nov-2026 + simulados) y prueba de extremo a extremo con un Discord
simulado. Las fuentes se verificaron desde un navegador; el envío real a tu Discord se comprueba con `PROBAR.bat`.

## Docs
`docs/REFERENCE_AUDIT.md` (auditoría del servidor de referencia), `docs/FEATURE_MATRIX.md`, `docs/PENDING.md`.
