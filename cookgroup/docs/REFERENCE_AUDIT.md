# Auditoría del servidor de referencia

- **Fecha:** 19-nov-2026, ~13:30 (Europe/Madrid)
- **Servidor:** "ZESTY CREW" (cookgroup de sneakers/reventa en español), visto desde la cuenta del usuario en Discord web.
- **Método:** solo lectura. Se recorrió la lista de canales y se abrieron ~18 canales representativos mirando los
  últimos mensajes visibles. No se pulsó ningún botón ni enlace de compra, no se escribió, no se reaccionó, no se
  cambiaron ajustes. En todos los canales abiertos aparece "No tienes permiso para enviar mensajes" (feeds de solo lectura).
- **Acceso:** solo canales visibles para la cuenta. Algunos mensajes enlazan a canales que **no** aparecen en la lista
  (p. ej. `#otros-tcg`, `#pokemon-aio-uk`): se interpreta que existen canales por rol a los que esta cuenta no accede; no se intentó entrar.
- **Privacidad:** no se copian nombres de miembros ni mensajes personales. Los ejemplos de productos son públicos (catálogo de tiendas).
- **Etiquetas:** **[O]** = observado directamente en pantalla. **[I]** = inferido a partir de lo observado (no verificado).
  No se conoce el código ni los proveedores internos del servidor.

## 1. Estructura (≈150 canales) [O]

| Categoría | Canales (resumen) | Naturaleza |
|---|---|---|
| EMPEZAR AQUÍ | bienvenido, checklist, zestyapp, guías, vídeo-guías, roles, auto-pinger, notificaciones, comandos | Onboarding y configuración de pings |
| Recompensas y reglas | recompensas, transparencia, reglas… | Comunidad |
| IMPORTANT | -pings, pings-automaticos, anuncios, importante, updates, releases, weekly-drops, monthly-drops, links, brick-links(-autorizados), steals, risky-calls, instore-info, success(-otros/-ventas), sugerencias(-app/-pings), giveaways, groupbuys, leaks, tickets | Curado por staff + comunidad |
| Releases | cop-or-drop, adidas-releases, nike-releases, z4lando-releases, otros-releases, important-releases (foro), un canal por lanzamiento concreto | Calendario de lanzamientos (staff) |
| Stocks | adidas-stock, nike-stock-drops, nike-stock-daily, nike-stock-cargado, stock-otros-releases | Stock por talla bajo demanda (comando de bot) |
| 🤖Monitores | aio-custom(-2), aio-eu(-2), aio-world, aboutyou-yoox, adidas-es/-eu, asics, asos(-es), basket-shops, basketballemotion, basket4ballers, bstn, end, footlocker-eu/-es, footshop, luisaviaroma, kickz, mesh-frontend/-backend, new-balance, sivasdescalzo, sports-direct, skateshops, skatedeluxe, socials-monitors, ugg(-all-special), uk, yeezy-especial-monitor, web-naranja-españa/-eu (Zalando), 43einhalb, timberland, vans | Monitores por tienda/plataforma |
| Shopify monitors | shopify-eu, shopify-eu-unfiltered, shopify-all + una por tienda (asphaltgold, dsml, footdistrict, kitheu, naked, overkill, slamjam, sneakersnstuff, voostore, starcow, canary-yellow, goodhood) | Shopify agregado + por tienda |
| Shopify clothes | corteiz, supreme, stussy, palace | Streetwear |
| Demandware monitors | info, solebox, snipes, solebox-custom, snipes-custom | Tiendas Salesforce Commerce |
| Nike monitors | nike-inactive, nike-eu-active, snkrs-es/-eu(-backup/-inactive), snkrs-special-releases, nike-us, snkrs-launch-custom | Nike / SNKRS |
| instore monitors | adidas-instore, jd-sports-instore, solebox-instore, nike-instore-{es, italia, holanda, polonia, austria, bélgica, irlanda, dinamarca, portugal} | Stock en tiendas físicas |
| monitores rebajas | aio-rebajas-30/60disc, chollometro, dealabs, mydealz, pepper, hotukdeals, miravia, lidl, pccomponentes, privalia-{campañas, productos, articulos}, jd-rebajas(-2), shopify-rebajas-{eu, 30disc, 60disc, all}, starcow-rebajas, zalando-prive(-campañas), asos-sample | Descuentos / retail / electrónica |
| Amazon rebajas | amazon-haul, amazon-error, amazon-sale, amazon-hasta-30, amazon-31-50, amazon-51-70, amazon-más-70 | Price errors y descuentos por tramo |
| bots checkouts | adonis-monitor, adonis-nike, alpine, antares, caspian, cyber, dislord, nsb, pan-aio, restocks-aio, tsb | Feeds de "checkouts" de bots de compra de terceros |
| General | chat-general, chat-invest, chat-ayuda, off-topic, chat-bots, hold-or-sell, discount-codes, wdywt, comparte-tus-redes, scrapers, spam, chat-de-voz + voz | Comunidad |

**No observado:** canales dedicados a *raffles* (se agrupan bajo releases/"Release Method"), ni categoría separada de
coleccionables/electrónica (aparecen mezclados en rebajas, Amazon y "otros-releases"; TCG va a canales no visibles para esta cuenta [I]).

## 2. Detalle por monitor/canal muestreado

### 2.1 Shopify — `#shopify-eu`
- **Productos/tiendas [O]:** sneakers de tiendas Shopify europeas (p. ej. una Nike Air Max 95 en una tienda FR, Nike Mind 001 en otra tienda).
- **Bot/autor [O]:** cada mensaje llega con el **nombre de la tienda como autor** del webhook (etiqueta APP). Pie: "zesty x Yeet Monitors" + hora.
  → **[I]** monitor de un proveedor externo ("Yeet Monitors") reetiquetado; no se conoce su implementación.
- **Campos [O]:** dominio de la tienda, título enlazado, imagen miniatura, precio, una línea por talla con enlaces **ATC | QT | talla**,
  bloque "Links" (Quicktask, Set up QT, StockX, GOAT, Removal request).
- **Enriquecimiento [O]:** para algunos productos aparece un **segundo mensaje** de otro bot ("Zesty | Herramientas") con SKU en bloque
  de código, *Reason: New*, precio, y por talla: punto de color + **beneficio estimado tras comisiones (texto: "12% + 5€") y nº de ventas
  de StockX (últimos 90 días)**, más botones de quicktask para varios bots, "Useful Links" (StockX, Idealo, eBay, Kaufland) y un gráfico de precio.
- **Nuevo vs restock [O]:** campo *Reason/Type* ("New", "Restock") en el mensaje enriquecido.
- **Duplicados [O]:** el mismo producto (Mind 001, misma tienda, 13:22) se publica **dos veces** (mensaje base + mensaje enriquecido) y
  minutos después vuelve a aparecer otro producto de la primera tienda con dominio `.eu` en lugar de `.fr` → **[I]** misma tienda, dos dominios, sin unificar.
- **Frecuencia [O]:** banner "Más de 10 mensajes nuevos desde las 13:19" → varios mensajes por minuto en hora punta.

### 2.2 Nike SNKRS — `#snkrs-es`
- **[O]** Autor "SNKRS". Campos: título, imagen, **Status** (ACTIVE ✅), **Style code**, **Exclusive** (False), **Max quantity**, **Promo excluded**,
  **Commerce date** (fecha + "hace 4 horas"), enlaces por país (IT·ES·FR·DE·NL·GB·DK·PT·PL), **Region** (bandera), **Type: New add**,
  tabla **Size [stock]** con niveles LOW/MEDIUM(/HIGH), Links (SNKRS, Nike app, Add to Favorites, Quicktask, StockX, eBay).
- **[I]** la información de nivel de stock por talla viene de datos públicos de producto de Nike; no verificado cómo se obtiene.

### 2.3 Zalando ("web naranja") — `#web-naranja-españa`
- **[O]** Dos formatos conviven: (a) autor "Zal": precio, SKU, **Regions** (enlaces a ~20 países), Region, **Type: Restock**,
  "QT | Size [stock]" con unidades por talla (p. ej. 4Y [1]); (b) autor "www.zalando.es" con SKU en bloque, Reason, precio, tallas con color.
- **[O]** Tallas de niño ("4Y", "5.5Y") y tallas con stock 1 → alertas de muy bajo valor mezcladas con las útiles.

### 2.4 adidas — `#adidas-es`
- **[O]** Autor "www.adidas.es", título en mayúsculas, SKU (p. ej. JQ…), **Reason: Restock**, precio, tallas EU con **fracciones** ("36 2/3", "43 1/3")
  y stock entre corchetes, "15+" como tope, Region Links por país, Useful Links y **gráfico de precio de reventa** con línea "Buy €77".

### 2.5 Demandware — `#snipes`
- **[O]** Autor "Snipes". Precio con **tachado + % de descuento** ("€100 (30%) €70"), enlaces por país, Type: Restock, talla [stock].
- **Calidad de datos [O]:** tallas mal parseadas visibles: "375 [36]" (debería ser 37.5) y "36666 [1]" (fracción 36 2/3 concatenada).

### 2.6 Monitor global — `#aio-world`
- **[O]** Tiendas fuera de la UE (AU, UK…). Producto Schuh publicado con **título = código numérico** (sin nombre de producto). Tallas UK con stock grande.

### 2.7 Nike instore — `#nike-instore-es`
- **[O]** Autor "Nike". Style code, **Store** (Nike Factory Store + ciudad), **Stock** (4+, 48+), Type: Sale,
  tabla **"Size – Stock – Last change"** con fecha del último cambio por talla.

### 2.8 Rebajas Shopify — `#shopify-rebajas-30disc`
- **[O]** Mismo formato Shopify con precio tachado y "-33%". Incluye **cartas sueltas de TCG** (Pokémon) donde la "talla" es el número
  de carta → **[I]** filtro por % de descuento sin filtro de categoría; mezcla coleccionables con calzado.

### 2.9 Chollos — `#chollometro`
- **[O]** Autor "Chollometro", pie "Zesty custom monitor | Chollometro | hora". En el momento de la visita **los mensajes salían vacíos**:
  "(Sin título)", "Precio: —", "Vendedor: —", "Link directo: —", solo con imagen, varios en el mismo segundo.
  → **[I]** el parser del monitor está roto o la fuente cambió; los mensajes vacíos se publican igualmente (falta validación).

### 2.10 Price errors — `#amazon-error`
- **[O]** Autor "Amazon", pie "Amazon price error monitor | Zesty". Campos: Precio actual, **Precio anterior**, **Descuento**, Vendedor, Marca,
  "Añadir a la cesta" 1x | 2x | 4x | 10x | 100x.
- **[O] Falsos positivos:** artículos de vendedores marketplace con "precio anterior" de **miles de euros** frente a ~36 € → "-100 %".
  → **[I]** el "precio anterior" se toma tal cual de la ficha sin validar si es creíble.

### 2.11 Electrónica — `#pccomponentes`
- **[O]** "Pccomponentes custom monitor": Precio anterior, Precio actual, Rebaja (%), Vendedor, Tipo: Rebaja. Último mensaje visible de **julio 2026** → canal inactivo.

### 2.12 Redes sociales — `#socials-monitors`
- **[O]** Autor "www.instagram.com": "New <tienda> post!", Reason: New, **Caption** completo e imagen. Último mensaje de octubre 2026.

### 2.13 Pings por palabra clave — `#pings-automaticos`
- **[O]** Bot "Zesty Pings": título, **Palabra** (regla tipo "texto ≤ precio_máx"), **Rol** mencionado, **Canal** de origen, Precio,
  **"Por qué se avisa"** (p. ej. precio de referencia de mercado, "UPC!"), y **botones enlace** "Ir al mensaje" / "Ir al producto".
- **[I]** reglas de palabra clave + precio máximo que re-publican alertas de otros canales con ping a un rol.

### 2.14 Stock bajo demanda — `#nike-stock-drops`
- **[O]** Resultado de un **comando de barra** ("X ha utilizado /nike-stock"), bot "zesty | Herramientas": SKU, **Release Date**, precio,
  color, Region, Site, **Release Method (LEO)**, tabla tallas/stock (HIGH/LOW/OOS), Useful Links.

### 2.15 Calendario — `#nike-releases`, `#releases`, `#important-releases`
- **[O]** Publicaciones **manuales del staff**: por drop, enlace a la tienda, enlace a StockX, emoji de semáforo (🔴🟠🟢 = recomendación),
  canal de stock relacionado, horario ("08:45–09:00", "17:00", "Durante el día"), método de drop, banner "DROPS DIARIOS".
  `#important-releases` es un **foro** con un hilo por lanzamiento (fecha en el título).

### 2.16 Comunidad — `#steals`
- **[O]** Mensajes de miembros con enlace + tallas + precio y reacciones de validación; un rol `@steals` se menciona. (No se reproducen.)

### 2.17 Checkouts de bots — `#adonis-monitor`
- **[O]** Bot "Adonis": producto, Store, Mode, Payment method, Price, Size, Checkout Time, enlace "Start quicktask", pie "The zesty chefs".
- **Duplicados [O]:** el **mismo checkout** (mismo producto, tienda, precio y segundo exacto) aparece **3+ veces seguidas** sin agrupar.

## 3. Conclusiones útiles para el diseño propio

1. **Formato que vale la pena replicar [O]:** tipo de evento explícito (New/Restock/Sale), SKU copiable, tallas con stock, región,
   precio con tachado y %, enlaces útiles, y **beneficio estimado por talla con comisiones explícitas**.
2. **Fallos a evitar [O]:** mensajes vacíos (Chollometro), tallas mal parseadas (Snipes), títulos numéricos (Schuh),
   price errors falsos por "precio anterior" no creíble (Amazon), duplicados exactos (Adonis, Shopify base+enriquecido).
3. **Ruido [O]:** tallas de niño y stock 1, TCG mezclado con calzado en canales de % descuento.
4. **Lo que NO replicamos:** botones ATC/Quicktask y feeds de checkouts de bots de compra (dependen de software de terceros
   para comprar automáticamente; fuera de alcance), monitores que requieran saltarse antibot, y el contenido de Instagram completo.

## 4. Propuesta de orden de implementación

| # | Monitor / función | Por qué primero | Fuente autorizada |
|---|---|---|---|
| 1 | **Validación + normalización de tallas** | Corrige los 3 fallos más visibles de la referencia | — (interno) |
| 2 | **Shopify restock/nuevo/precio** (ya existe) + SKU, % descuento, `compare_at_price` | Mayor volumen observado; endpoint público | `/products.json` público de cada tienda, revisando sus condiciones |
| 3 | **Price error con precio de referencia validado** | La referencia publica falsos positivos | Historial propio de precios (no el "precio anterior" de la ficha) |
| 4 | **Pings por palabra clave + precio máx → rol** | Muy útil y barato; reutiliza eventos existentes | — (interno) |
| 5 | **Feeds RSS de chollos** | Cubre retail/electrónica sin scraping | RSS/Atom públicos que la propia web ofrece |
| 6 | Calendario de lanzamientos | En la referencia es manual; empezar con fichero editable por staff | Config propia |
| 7 | Nike/adidas/Zalando/Demandware/instore | Requiere revisar condiciones y APIs; mayor riesgo | Solo APIs oficiales/afiliados |

Los puntos 1–5 se implementan en esta iteración (ver `FEATURE_MATRIX.md`).

## 5. Segunda pasada (19-nov-2026, tarde) y lo que se ha incorporado

**Acceso:** al volver al servidor, la sesión de Discord del navegador había caducado («Inicia sesión de nuevo»).
Para entrar hace falta la contraseña del usuario, así que no se continuó dentro del grupo. Lo que sigue combina la
auditoría de la mañana con la investigación de las fuentes públicas de las tiendas.

### Secuencia de un lanzamiento: AF1 Cactus Jack x GTA VI, reconstruida
| Paso | En la referencia [O] | En la tienda (BSTN, fuente pública) [O] | En nuestro bot |
|---|---|---|---|
| 1. Primer anuncio | Hilo del staff en `#important-releases` «21/11 – Nike Air Force 1 Low Travis Scott x Rockstar Games GTA 6», con enlace a StockX | Aparece en «Coming Soon» (alta del producto en la tienda: 18-nov 07:03 UTC) | 📢 Anuncio / 🎟️ Raffle abierto en cuanto aparece en el listado |
| 2. Apertura de inscripciones | — (no visto) | `raffle_is_active = Yes`, enlace a raffle.bstn.com | 🎟️ Raffle abierto con enlace directo y cierre en hora de Madrid |
| 3. Recordatorio | — | `raffleends = 20. Nov · 15:00 CET` | ⏳ «El raffle cierra en X», una vez, 3 h antes |
| 4. Salida a la venta | Resumen «Drops diarios» del staff con horarios | Página del raffle: «RELEASE 21. Nov · 9:00 CET» | La fecha de salida de un raffle solo está en la página del raffle (excluida por robots.txt): no se lee. La de los lanzamientos normales sí (🟢 A la venta) |
| 5. Reposición | Monitores por tienda | Ficha con tallas y unidades | 🔄 «Ha vuelto la EU 43» |
| 6. Cierre | — | `raffle_is_expired = Yes` | Sale del resumen de «abiertos ahora» (no se envía alerta) |

**Qué llega primero [I]:** el calendario de la tienda se adelanta al resumen manual del staff, que publica el día
anterior o el mismo día. Los monitores de catálogo solo reaccionan cuando ya hay stock. Por eso el anuncio se vigila
en el calendario y no en el catálogo.

### Mejoras incorporadas gracias a la referencia
| Hallazgo | Implementación |
|---|---|
| Canales separados por tipo (releases, raffles, stocks, monitores por tienda, rebajas por tramo, pings por rol) | Estructura `LANZAMIENTOS / RAFFLES / RESTOCKS / PINGS / SNEAKERS / SNEAKERS_WORLD / STREETWEAR / REBAJAS_30/60 / CHOLLOS / RELEASES`, todo opcional con un único `DEFAULT` |
| «Drops diarios» y foro de lanzamientos | Resumen inicial y diario a las 09:00 con «raffles abiertos ahora» y «próximos 7 días», a partir de fuentes verificadas |
| `#pings-automaticos` (palabra ≤ precio → rol) | Reglas con marcas, tallas EU, regiones, tiendas, precio máximo y tipos de evento |
| Separación por región (`snkrs-es`, `-eu`, `nike-us`…) | Región en cada alerta y en los filtros. BSTN eu_es frente a uk_en: misma hora, otra zona horaria y otro precio (verificado) |
| Tallas mal leídas, mensajes vacíos, price errors falsos, duplicados | Validación, normalización EU/US/UK, referencia de precio propia y claves estables que sobreviven a reinicios |
| Staff anota «Release Method», «hora sin confirmar» | Modalidad online, app o tienda física en cada alerta; si la tienda solo da el día, se respeta |

### Tareas que quedan, con su motivo
- **Volver a entrar en el grupo** (necesita al usuario): revisar `#bstn`, `#raffles`, si existen, y los hilos de `#important-releases`, para medir qué aviso llega antes que el nuestro.
- **SVD**: es la tienda española con raffles propios y la referencia la sigue con un canal propio; falta su adaptador.
- **Raffles de EQL** (size?, Footpatrol): plataforma aparte; hay que comprobar si ofrece una fuente pública estable.
