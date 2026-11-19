# Cookgroup — monitores de stock/precio con alertas Discord (v0.1)

Núcleo funcional: fuente Shopify (`/products.json` público), detección de restock/producto nuevo/tallas/bajada
de precio, filtros, deduplicación con cooldown, cálculo de beneficio neto, score 0-100 y embeds por webhook.
**Estado honesto:** probado con datos simulados (14 tests); no verificado contra tiendas ni Discord reales. Ver `docs/PENDING.md`.

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
`docs/FEATURE_MATRIX.md`, `docs/PENDING.md`.
