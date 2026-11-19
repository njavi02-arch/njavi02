# Cookgroup — monitores de stock/precio con alertas Discord (v0.2)

Núcleo funcional: fuente Shopify (`/products.json` público), detección de restock/producto nuevo/tallas/bajada
de precio, filtros, deduplicación con cooldown, cálculo de beneficio neto, score 0-100 y embeds por webhook.
v0.2 (tras auditar el servidor de referencia): normalización/validación de tallas y mensajes, price errors con
referencia del histórico propio, pings por palabra clave + precio → rol, y fuente RSS/Atom para chollos.
**Estado honesto:** probado con datos simulados (43 tests); no verificado contra tiendas, feeds ni Discord reales. Ver `docs/PENDING.md`.

## Uso
```bash
cd cookgroup && pip install -e '.[dev]' && pytest
cp .env.example .env            # añade webhooks reales (nunca al repo)
cookgroup check-config
cookgroup run                   # o: docker compose up -d --build
```
Configura tiendas en `config/monitors.toml` (intervalo mínimo 30 s; recomendado ≥120 s) y datos de mercado verificados
en `config/market_data.json` (`kind`: `sold` o `listing`). Sin dato de mercado no se muestra beneficio.

## Principios
No se eluden CAPTCHAs/antibots/límites; ante 403/429 el monitor espera con backoff. Nada se inventa: sin dato → "N/D".

## Costes orientativos
VPS pequeño (~5–10 €/mes) basta para decenas de tiendas a 2 min. Sin otros servicios en v1.

## Docs
`docs/REFERENCE_AUDIT.md` (auditoría por canal), `docs/FEATURE_MATRIX.md`, `docs/PENDING.md`.
