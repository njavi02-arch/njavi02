# Piloto v0.7 — lecturas reales de las 6 fuentes (20-nov-2026, ~12:08–12:10 Madrid)

**Tipo de dato: LECTURA REAL**, hecha desde tu navegador (Chrome) con peticiones de solo lectura a las mismas URLs
públicas que usa cada monitor. El contenedor de trabajo no tiene salida a estas webs, así que la lectura automática
desde el bot (con `COMPROBAR.bat piloto`) queda para tu PC.

| Fuente | Tipo | Resultado | Leídos | Ejemplo de variante (observado) | Siguiente paso |
|---|---|---|---:|---|---|
| FOOTDISTRICT (`footdistrict.com`) | Shopify | ÚTIL | 250 productos (moneda EUR por /cart.js) | Autry Medalist Low Goatskin — talla 40 — 129,00 € (antes 215) — con stock | captura guardada como `tests/fixtures/footdistrict_REAL_2026-11-20.json` y usada en el piloto e2e |
| Asphaltgold (`asphaltgold.com`) | Shopify | ÚTIL | 250 (239 con stock), EUR | Timberland Premium 6-Inch — 40 / Burgundy — 279,00 € — con stock | nada |
| BSTN (`bstn.com/eu_es/men/upcoming`) | BSTN (Next.js) | ÚTIL | 17 lanzamientos, 15 con fecha, **2 raffles abiertos** | Nike × Cactus Jack × GTA VI Air Force 1 «Black» — raffle abierto | nada; el monitor avisa del raffle por sí solo |
| Snipes ES | datos estructurados (JSON-LD) | **FALLO → corregido** | la URL configurada daba **404**; con `/es-es/c/hombre/zapatos-77`: 53 fichas | Air Force 1 '07 — 95,99 € — en stock (JSON-LD sin tallas) | URL corregida en `monitors.toml`; tallas: no las da el JSON-LD → cobertura parcial |
| Solebox (`solebox.com/en-eu/c/footwear-2777`) | datos estructurados (JSON-LD) | ÚTIL (nuevo) | 44 fichas | x solebox 6Inch Premium Boot Pony Hair — 199,99 € — en stock | añadido al piloto; misma plataforma que Snipes |
| Chollometro `/rss/hot` | feed de chollos | ÚTIL | 30 chollos (28 con precio) | «Nuevos códigos y descuentos extras en Samsung» — Samsung — sin precio | nada (un feed sin novedades es normal) |

Notas:
- La URL de Snipes devolvía una página 404 con 8 productos recomendados: por eso hay que mirar el estado HTTP y no solo
  «hay productos». En v0.6 la sonda imprimía «OK» incluso con 0 productos; en v0.7 distingue
  VACÍA / SIN COINCIDENCIAS / ÚTIL / SIN CAMBIOS / LIMITADA / FALLO.
- Ninguna lectura tocó carrito, cuenta, sorteo ni botón de compra.
