# VITALAIR — Estrategia de promociones, precios y márgenes (01/10/2026)

## 1. Hipótesis y datos (lo que sé y lo que supongo)
**Datos reales (proveedor, rangos en USD, aún no cerrados):** set sin recambios 7,80–9,30 · set + 3 recambios 9,00–12,00 · set + 6 recambios 10,00–14,50 · recambio suelto 0,55–0,76 · envío de 1–2 sets (0,4 kg) 6,50–8,00 (a confirmar por su transportista tras el festivo chino). Diseños personalizados: MOQ 500+.
**Hipótesis (marcadas, a confirmar):** cambio 0,90 €/USD · precios con IVA 21 % · comisión de pago 1,9 % + 0,25 € · el coste de envío crece con el peso (16–20 USD/kg, peso facturable máx(0,4; 0,2 × nº de sets)) · tarifa de envío cobrada al cliente 6,99 € y gratis desde 55 €.
**Datos que faltan para cerrar márgenes:** precio final por volumen, tarifa de envío por pedido de 3–5 sets, duración de un recambio (necesaria para recurrencia), si el IVA está incluido en tus precios, comisión real de tu pasarela.
Margen = ingresos netos de IVA − comisión − coste del proveedor − envío del proveedor. Se calcula en "mejor caso / peor caso" de costes. Script: ver historial de la sesión (`/tmp/margin.py`, reproducible con los datos de arriba).

## 2. Diagnóstico
- Precios anteriores (19,99 · 39,98 · 44,97 · 57,97 · 64,95) con 15 % apilado: **4x y 5x perdían dinero en el peor caso (−2,7 € y −15,5 €)** y 3x quedaba a ~0 €. Cada set cuesta ~7–8,4 € y el envío crece con el peso, así que el inhalador aguanta poco descuento.
- Los **sabores** cuestan 0,50–0,68 € y se venden a 1,99 €: ahí está el margen para promocionar.

## 3. Estructura definitiva
| Promoción | Precio | Ahorro cliente | €/inhalador | Margen estimado (peor–mejor) | Objetivo |
|---|---:|---:|---:|---:|---|
| 1 inhalador | 19,99 € | — | 19,99 | 6,0–8,8 € | Entrada |
| 2 inhaladores | 36,99 € | 2,99 € (−7,5 %) | 18,50 | 11,3–15,5 € | Subir ticket |
| **3 inhaladores (recomendado)** | **52,99 €** | 7,00 € (−11,7 %) | 17,66 | 12,3–18,5 € | Pack principal |
| 4 inhaladores | 66,99 € | 12,97 € (−16,2 %) | 16,75 | 6,0–14,2 € | Volumen |
| 5 inhaladores | 79,99 € | 19,96 € (−20 %) | 16,00 | 4,5–14,8 € | Mejor precio / ancla |
| Sabor extra | 1,99 € | 3 o más sabores: −15 % | — | 0,5–1,1 € por sabor | Ticket y recurrencia |
Márgenes sin el 15 % de lanzamiento, envío 6,99 € (gratis desde 55 €). Con el 15 % de lanzamiento: 1x 3,5–6,3 · 2x 6,8–11,0 · 3x 5,9–12,1. **4x y 5x quedan excluidos del 15 %** (en el peor caso serían −2,2 y −5,2 €).
Pedidos con sabores (peor–mejor): 1 inhalador + 3 sabores 8,0–11,4 € · 3 inhaladores + 6 sabores 10,7–18,1 € · 5 inhaladores + 10 sabores 11,3–23,6 €.

## 4. Oferta principal: Pack 3 + sabores
- El 3x es el pack recomendado (opinión, no "más vendido": no hay ventas que lo respalden). El tercer inhalador sale a ~16 € frente a ~18,5 € del segundo: empuja de 2 a 3 (quantity break + decoy del dúo).
- El 5x actúa de ancla de precio por inhalador (16 €). El 4x queda como escalón intermedio.
- Los sabores son el upsell: precio visible, "+1,99 €", y a 3 o más sabores −15 % (el selector avisa cuántos faltan).
- Psicología aplicada: precio por inhalador, "ahorras X €" frente a unidades sueltas (único precio tachado legítimo), pack recomendado, progreso hacia el descuento de sabores. Sin "más vendido", sin urgencia falsa.

## 5. Permanentes y temporales
- **Permanentes:** escalones 1/2/3/4/5 y −15 % en sabores desde 3.
- **Temporal (lanzamiento):** 15 % automático en packs de 1 a 3 y en sabores. **Falta fijar fecha de fin** (decisión tuya); sin fecha, no debe presentarse como urgencia.
- Pendiente de datos: envío gratis como palanca (4–5 inhaladores ya superan 55 €): se pausa la comunicación de envío hasta confirmar costes y plazos.

## 6. Embudo (qué hay y qué falta)
- **Home:** packs con ahorro, pack 3 recomendado, precio con 15 % solo donde aplica. ✔
- **Ficha:** selector con precio por inhalador, mensaje de subir al siguiente pack, resumen del pedido. ✔
- **Carrito:** descuentos automáticos visibles; falta módulo de venta cruzada de sabores (requiere tocar el carrito del tema o una app). Pendiente.
- **Checkout:** Shopify Basic no permite upsell propio; alternativa: oferta de sabores en el carrito.
- **Pop-up:** anuncia el 15 % con sus límites reales. ✔ Pop-up de salida con captura de email: pendiente (necesita herramienta de email).
- **Email:** carrito abandonado en 1 h/24 h/72 h con los sabores elegidos; aviso de recambio cuando se sepa la duración. Pendiente (requiere app de email).
- **Retargeting:** visitas a ficha sin compra → pack 3 con sabores. Pendiente de tener tráfico y política de anuncios clara (categoría restringida).
- **Recurrencia:** necesita duración del recambio; test recomendado: "1 sabor incluido con cada inhalador" (coste extra 0,5–0,7 €).
