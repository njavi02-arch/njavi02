# v0.6 → v0.7

| Tema | v0.6 | v0.7 |
|---|---|---|
| Discord cae al enviar | instantánea guardada antes de enviar → **aviso perdido** (reproducido) | bandeja de salida persistente: se reintenta, sobrevive a reinicios, sin duplicados |
| Fuente sin cambios / en error | lo pendiente no se reintentaba | se entrega lo pendiente también en ciclos 304 o con error de la fuente |
| Sonda (`probe`) | «OK» aunque leyera 0 productos | 6 estados, CSV por dominio, `--solo/--buscar/--limite/--reanudar` |
| Scripts | PROBAR.bat mezclaba comprobar + enviar + vista previa | COMPROBAR / ENVIAR_PRUEBA / VER_PANEL |
| ESTADO | solo último OK por fuente | latido del proceso (vivo/parado) + retraso respecto al intervalo de cada fuente |
| Beneficio | admitía anuncios con aviso; un único ROI | solo ventas cerradas verificadas (≥3/30 días, misma talla/estado/mercado, EUR, envío ES); margen s/venta y ROI s/compra por separado; si no, «beneficio sin verificar» |
| Calendario | 2 lanzamientos sin confirmar podían avisar | `status = pendiente` por defecto; `confirmado` exige `official_source` |
| Cifras | escritas a mano (262, erróneo) | `tools/stats.py` → `docs/CIFRAS.md` (260) |
| Snipes ES | URL de listado devolvía 404 | corregida (`/es-es/c/hombre/zapatos-77`) |
| Piloto | — | `config/piloto.toml` (6 fuentes) + `tools/piloto.py` e2e (9/9) |
| Tests | 113 | 122 |
