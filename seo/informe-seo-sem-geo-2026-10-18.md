# KOHI & CHA — Informe SEO + SEM + GEO (18/10/2026)

## 0. Qué he podido y qué no he podido revisar

| Fuente | Estado |
|---|---|
| Shopify Admin API (producto, colecciones, blog, páginas, idiomas, mercados, código del tema) | **Revisado de verdad** |
| HTML renderizado de kohiycha.com, robots.txt, sitemap.xml | **No revisado**: desde mi entorno el dominio no resuelve (error DNS). Lo que digo de ellos es hipótesis. |
| Google Search Console, Analytics, Merchant Center, Google Ads, Keyword Planner, Trends | **Sin acceso**. No hay volúmenes, CPC, dificultad ni posiciones reales en este informe. |
| PageSpeed / Core Web Vitals | **No medido** |
| Búsqueda web (SERP) | Revisada con un buscador limitado: sirve para ver quién aparece, no para medir demanda. |

Todo lo marcado **[Comprobado]** viene de Shopify o del código del tema. **[Hipótesis]** debe verificarse. **[Recomendación]** es una mejora sin evidencia de error.

---

## 1. Auditoría

### Problemas comprobados
1. **Título y meta de la home anunciaban productos ocultos.** El tema tenía fijo "Matcha en polvo premium 1 kg y matcha latte" y "5 mezclas de matcha latte". → Corregido en el borrador *KOHI & CHA - SEO RED SMILE*.
2. **Schema Organization con descripción obsoleta** (mencionaba matcha latte). → Corregido en el borrador.
3. **Ficha de RED SMILE sin categoría** ("Uncategorized"). → Corregido: *Food, Beverages & Tobacco > Beverages > Tea & Infusions > Tea*.
4. **Peso de la variante = 0 kg y sin GTIN/código de barras.** Puede afectar a tarifas por peso y a Google Merchant Center. → Necesito el peso real y saber si el producto tiene código de barras.
5. **Imágenes de producto de 412×512 px.** Son pequeñas para una marca premium, para zoom y para Google Shopping. → Necesito originales de mayor resolución.
6. **Descripción de RED SMILE enlazaba a `/collections/matcha-latte`**, que ahora es una página "Próximamente". → Reescrita.
7. **Colecciones con SEO que anuncia productos no disponibles**: *Matcha Latte Sabores | Coco, Mango, Vainilla y Fresa*, *Accesorios*, *Regalos*, etc.
8. **Artículos del blog** enlazan a productos ocultos (Matcha Premium 1 kg, ThermoWave, línea Matcha Latte). Hoy esas URL redirigen (301) a anclas de la home, que Google trata en la práctica como la home. Además no tenían schema `BlogPosting`. → Añadido en el borrador.
9. **Colecciones vacías con riesgo de contenido débil.** → En el borrador llevan `noindex, follow` mientras no tengan productos visibles, y la búsqueda interna también.
10. **El asistente de chat de la web sigue recomendando los 5 Matcha Latte y Matcha Premium** (productos ocultos).

### Hipótesis a verificar
- **Idioma `en` publicado** y enlaces del menú con `/en/…`: si el contenido sigue en español bajo `/en/`, hay contenido duplicado. Comprobar en Ajustes → Idiomas y en Search Console.
- **Sitemap**: Shopify suele listar las colecciones publicadas aunque estén vacías. Comprobar `/sitemap.xml`.
- **robots.txt**: el tema no tiene `robots.txt.liquid` [Comprobado], así que se aplica el de Shopify por defecto. No he podido leerlo.
- Posible duplicación de `Product` schema si la app de reseñas Judge.me añade el suyo [Hipótesis].

### Lo que ya está bien [Comprobado en el código]
- `Product` JSON-LD con precio, disponibilidad, marca, imágenes y política de devolución (14 días); `BreadcrumbList` en producto y colección; `Organization` y `WebSite` en la home.
- Un único H1 por plantilla; textos alternativos presentes en las 3 imágenes de RED SMILE.
- No se inventan reseñas: la valoración (`aggregateRating`) no se emite mientras haya 0 reseñas. Correcto.

---

## 2. Palabras clave

**No tengo volúmenes ni CPC.** Sin Keyword Planner ni Search Console, la columna "Demanda" queda en blanco a propósito. La prioridad se basa en intención, encaje con lo que se vende y competencia observada en el buscador.

**Hallazgo clave de posicionamiento.** RED SMILE cuesta 79,90 € por 1 kg: unos 0,08 €/g. En la SERP española, una guía de [Que.es](https://www.que.es/2025/03/16/matcha-sin-enganos-comprar-el-mejo/) avisa de que un ceremonial auténtico difícilmente baja de 1 €/g, y [Druni](https://www.druni.es/blog/cual-es-el-mejor-te-matcha-del-mercado/) analiza Matcha & CO desde ~10–16 € por bote pequeño. **No conviene posicionar RED SMILE como "ceremonial"** ni competir por las búsquedas genéricas contra Druni, Amazon y marcas establecidas. Su hueco es el **formato de 1 kg** (uso diario intensivo, latte, cafeterías).

**"Matcha rojo" no es un término que describa el producto.** Según los datos de la ficha, RED SMILE es matcha en polvo en **bolsa roja**. Una búsqueda de "matcha rojo" no devolvió ninguna definición de producto. No lo uso como keyword ni como afirmación. Si el polvo en sí fuera rojo, dímelo.

### Tabla priorizada (demanda: sin dato)

| # | Keyword | Intención | Competencia observada | Página | Prioridad | Uso |
|---|---|---|---|---|---|---|
| 1 | matcha 1 kg | Compra | Pocos vendedores españoles visibles; sí extranjeros ([Ocha & Co](https://www.ochaandco.com/en-gb/products/matcha-wholesale-1kg-japanese-green-tea-powder), Usetorg) | Ficha RED SMILE | Alta | Título SEO, H1/H2, alt |
| 2 | comprar matcha 1 kg | Compra | ídem | Ficha RED SMILE | Alta | Descripción, meta |
| 3 | matcha en polvo 1 kg | Compra | ídem | Ficha RED SMILE | Alta | Descripción |
| 4 | RED SMILE matcha | Marca/producto | Ninguna (término propio) | Home + ficha | Alta | Título home, alt |
| 5 | KOHI & CHA | Marca | Ninguna | Home | Alta | Título home |
| 6 | Kohi y Cha / kohicha / kohi cha matcha | Marca (variantes) | Ninguna | Home | Alta | Texto de "Sobre nosotros" |
| 7 | matcha edición limitada | Compra | Hipótesis: baja | Home + ficha | Media | Una vez, natural |
| 8 | matcha para cafeterías | Compra B2B | Hipótesis: media | Página *Matcha para negocios* (hoy sin publicar) | Alta | Publicarla cuando esté lista |
| 9 | matcha al por mayor / proveedor de matcha hostelería | Compra B2B | Hipótesis: media | ídem | Media | ídem |
| 10 | cuántas tazas salen de 1 kg de matcha | Informativa | Hipótesis: baja | Blog (existe) | Media | Enlace a la ficha |
| 11 | cuánto matcha por taza | Informativa | Hipótesis: media | Blog (nuevo) | Media | Guía |
| 12 | cómo preparar matcha | Informativa | Alta (muchos medios) | Blog (existe) | Media | Mantener y mejorar |
| 13 | cómo hacer matcha latte | Informativa | Alta | Blog (nuevo) | Media | Guía |
| 14 | diferencia matcha y té verde | Informativa | Alta | Blog (nuevo) | Baja | Guía |
| 15 | matcha ceremonial vs culinario | Informativa | Alta | Blog (existe) | Baja | Revisar claims |
| 16 | qué es el matcha | Informativa | Muy alta | Blog (nuevo) | Baja | Guía de entidad (GEO) |
| 17 | matcha para principiantes | Informativa | Media | Blog (nuevo) | Media | Guía |
| 18 | cómo elegir un matcha de calidad | Informativa | Alta | Blog (nuevo) | Media | Guía honesta con precio por gramo |
| 19 | comprar matcha en polvo | Compra | Alta (Druni, Amazon) | Colección *Matcha* | Baja a corto plazo | No forzar |
| 20 | comprar matcha / matcha premium / matcha online | Compra genérica | Muy alta | Home/colección | Baja a corto plazo | No priorizar |

**Qué NO hacer:** no crear páginas vacías para *Matcha Premium* o *Matcha Latte*. Mantenerlas accesibles como "Próximamente" y fuera del índice (`noindex`) hasta que haya productos; entonces se indexan solas, conservando la URL.

### Reparto por zonas
- **Home:** KOHI & CHA, RED SMILE, edición limitada.
- **Ficha RED SMILE:** matcha 1 kg / en polvo 1 kg, formato, edición limitada.
- **Colección Matcha:** matcha en polvo (genérico).
- **Blog:** informativas, con enlace interno a la ficha.
- **Páginas futuras (Premium/Latte):** su contenido se prepara en el lanzamiento, no antes.

---

## 3. Ficha de RED SMILE

**Análisis de la versión anterior.** Correcta pero corta; sin encabezados H2, sin FAQ, categoría vacía, enlaza a una colección que ya no vende. Título SEO de 63 caracteres (se trunca en Google).

**Cambios aplicados en Shopify (reversibles, copia en `backup/2026-10-18-red-smile-seo-original.json`):**
- **Título SEO (53 car.):** `RED SMILE · Matcha 1 kg edición limitada | KOHI & CHA`
- **Metadescripción (154 car.):** `Matcha en polvo en formato de 1 kg, para tomar tradicional o en latte. Bolsa roja con cierre zip. Edición limitada de 50 unidades. Envío a España y la UE.`
- **Descripción larga:** H2 *RED SMILE en un vistazo / Cómo prepararlo / Conservación / Preguntas frecuentes* + 5 FAQ (rendimiento, latte, cafeterías, envío, devoluciones). Solo contiene datos que ya figuraban en tu tienda.
- **Categoría:** Tea. **Título comercial (H1) sin cambios.**
- **Enlaces internos:** guía de preparación, guía de tazas por kilo, políticas y *Sobre KOHI & CHA*. Eliminado el enlace a Matcha Latte.

**Lo que no he afirmado** porque no lo sé: origen, grado, ingredientes, notas de sabor, ecológico, alérgenos, certificaciones aplicables a RED SMILE, fecha de consumo, país de procesado. Con esos datos se escribe una descripción mucho más fuerte.

---

## 4. GEO (Google AI y buscadores con IA)

Qué hacer, sin prometer citas:
- **Hechos claros y verificables** en texto visible (formato, peso, unidades, preparación, envío, devoluciones). Ya aplicado en la ficha.
- **Entidad de marca coherente**: mismo nombre y descripción en la web, `Organization`, redes y Merchant Center. Mejorado en el borrador.
- **Guías útiles y propias** en el blog (qué es el matcha, cómo elegir, precio por gramo), que son lo que los sistemas de respuesta suelen citar.
- **Datos estructurados**: `Product`, `BreadcrumbList`, `Organization`, `BlogPosting` (añadido).
- **FAQ**: las dejo como contenido visible. **No añado marcado `FAQPage`**, porque Google limitó esos resultados enriquecidos a sitios gubernamentales y de salud (cambio de 2023, conocido por mí; no lo he vuelto a verificar hoy).
- **Bing**: se suele citar que ChatGPT Search se apoya en índices como el de Bing; conviene dar de alta el sitio en Bing Webmaster Tools. [Hipótesis no verificada hoy.]
- **Limitaciones**: ninguna optimización garantiza aparecer en AI Overviews ni ser citado por una IA; con una sola referencia y sin menciones externas, la visibilidad será baja al principio.

---

## 5. SEM — recomendación para los primeros 100 €

**Recomendación: no gastar todavía.** Falta lo necesario para que el gasto no se pierda:
1. **Margen y CAC máximo** (no los conozco). Con RED SMILE a 79,90 € y envío gratis en España peninsular desde 55 € (configuración real de Shopify), el coste del envío lo asumes tú y se come parte del margen.
2. **Medición**: no sé si GA4 y la etiqueta de conversión de Ads están instaladas.
3. **Merchant Center**: RED SMILE ya está publicado en el canal *Google & YouTube*, pero faltan peso real, GTIN (o declarar que no lo tiene) e imágenes de mayor resolución.
4. **Sin CPC real.** No tengo datos de Keyword Planner.

**Plan propuesto (requiere tu aprobación expresa):**
- **Semanas 1–2, 0 €:** activar las **fichas gratuitas de Google Shopping** (Merchant Center) y recoger datos.
- **Después, si la medición funciona:** una campaña de **Búsqueda** pequeña, concordancia **de frase y exacta** en "matcha 1 kg", "comprar matcha 1 kg", "matcha en polvo 1 kg" y la marca; negativas: gratis, receta, infusión, bolsitas, ceremonial japonés, mayorista (si no vendes); destino: ficha de RED SMILE. Con 100 €, el objetivo sería **aprender**, no escalar: unas decenas de clics a lo sumo, no una cifra de ventas garantizada.
- **No** Performance Max con 100 €.

---

## 6. Competencia (observada, no auditada)

| Competidor | Qué hace | Hueco para KOHI & CHA |
|---|---|---|
| [Druni](https://www.druni.es/te-matcha-ceremonial-premium-matcha-co-100-puro) / Matcha & CO | Bote pequeño, ceremonial y culinario, blog comparativo propio | No compiten en 1 kg ni en marca de lanzamientos |
| Amazon (Matcha & CO) | Precio y ofertas | Sin experiencia de marca |
| Ocha & Co (UK), Usetorg | 1 kg, B2B, desde fuera de España | Envío rápido desde España |
| Medios ([Que.es](https://www.que.es/2025/03/16/matcha-sin-enganos-comprar-el-mejo/)) | Guías de compra | Contenido propio con transparencia de precio por gramo |

No he analizado páginas competidoras en profundidad (el buscador no devuelve su HTML). Es una primera foto.

---

## 7. Plan de 30 días

| Sem. | Acción | Impacto | Esfuerzo | Coste | Dependencia | Cómo medir |
|---|---|---|---|---|---|---|
| 1 | Verificar Search Console y enviar sitemap | Alto | Bajo | 0 | Tu acceso | Cobertura de páginas |
| 1 | Publicar el borrador *SEO RED SMILE* | Alto | Bajo | 0 | Tu clic | Título y meta en Google (tras recrawl) |
| 1 | Peso real, GTIN, imágenes ≥1000 px | Alto | Bajo | 0 | Tus datos | Merchant Center sin avisos |
| 1 | Decidir sobre idioma `en` | Medio | Medio | 0 | Tu decisión | Duplicados en GSC |
| 2 | Completar descripción con origen, grado e ingredientes | Alto | Bajo | 0 | Tus datos | CTR, conversión |
| 2 | Merchant Center + fichas gratuitas | Alto | Medio | 0 | Peso/GTIN | Impresiones en Shopping |
| 2 | Cambiar el menú y reescribir el asistente | Medio | Bajo | 0 | Publicar tema | Rebote |
| 3 | 3 guías nuevas (qué es, latte, elegir) | Medio (lento) | Medio | 0–tiempo | — | Impresiones en GSC |
| 3 | Publicar *Matcha para negocios* | Medio | Medio | 0 | Tus datos B2B | Consultas B2B |
| 3 | Configurar medición de conversión | Alto | Medio | 0 | GA4/Ads | Compra registrada |
| 4 | Revisar indexación y consultas | Alto | Bajo | 0 | Datos de GSC | Páginas indexadas |
| 4 | Decidir campaña de Búsqueda | Medio | Bajo | hasta 100 € | Medición + margen | CPA vs. margen |

Corto plazo: títulos/meta, Merchant, medición. Largo plazo: guías, enlaces y autoridad de marca (meses).

---

## 8. Cuadro de métricas

| Métrica | Dónde | Frecuencia |
|---|---|---|
| Impresiones, clics, CTR, posición media (marca / producto / informativas) | Search Console | Semanal |
| Páginas indexadas vs. excluidas | Search Console | Semanal |
| Impresiones y clics de fichas gratuitas | Merchant Center | Semanal |
| Sesiones orgánicas y conversión | GA4 | Semanal |
| Pedidos y valor de RED SMILE | Shopify | Diario |
| Suscriptores a "próximos lanzamientos" | Shopify (clientes con etiqueta) | Semanal |
| Búsquedas de marca | Search Console | Mensual |
| Resultados enriquecidos válidos (Product, Breadcrumb) | Prueba de resultados enriquecidos | Tras cada cambio |
| CPA / ROAS | Google Ads (si se activa) | Diario |

---

## 9. Acciones ejecutadas en Shopify
**En producción:** ficha de RED SMILE (título SEO, metadescripción, descripción, categoría). Reversible desde `backup/2026-10-18-red-smile-seo-original.json`.

**En un tema borrador sin publicar** (*KOHI & CHA - SEO RED SMILE (borrador)*): título y meta de la home, schema Organization, `noindex` en colecciones vacías y búsqueda, schema `BlogPosting`, estilo de H2 en descripciones.

**No he hecho**: activar campañas, tocar precios/inventario, cambiar el menú, el idioma `en`, ni el asistente.

## 10. Lo que necesito de ti
1. ¿RED SMILE es el **mismo matcha** que "Matcha Premium 1 kg" (origen China, Jingshan/Wuyi, ISO 22000/HACCP)? Si sí, puedo trasladar esos datos a la ficha. Si no, dime origen, grado, ingredientes y sabor.
2. **Peso real** del envío y si tiene **código de barras**.
3. **Fotos** más grandes de RED SMILE (≥1000 px).
4. **Margen** por unidad y **coste máximo por venta** aceptable.
5. ¿Tienes **Search Console, GA4 y Merchant Center**? Necesito saber si están conectados y darme acceso o exportar datos.
6. ¿Mantienes el idioma **inglés** publicado?
7. ¿Aprobáis el `noindex` en colecciones vacías (afecta a tráfico de esas URL)?

---

## 11. Actualización: datos aportados por ti (18/10/2026)

**Aplicado en Shopify:**
- Peso de la variante: **1 kg** (antes 0). Tus tarifas de envío no dependen del peso, así que no cambia ningún precio.
- Ficha de RED SMILE: **origen China (Jingshan/Wuyi), molido a la piedra** (mismo matcha que Matcha Premium 1 kg), añadido a descripción, lista y FAQ; metadescripción actualizada.
- No he incluido la certificación ISO 22000/HACCP en la ficha: tu artículo del blog la menciona para el Matcha Premium, pero no sé a quién certifica exactamente (proveedor, planta, lote).

**Economía de RED SMILE** (50 kg a 2.008,60 € → **40,17 € por bolsa**; ingresos si se vende todo a 79,90 € IVA incluido: 3.995 €):

| IVA aplicable (confírmalo con tu gestor) | Precio sin IVA | Margen bruto por bolsa | Margen % | 50 bolsas |
|---|---|---|---|---|
| 4 % | 76,83 € | 36,66 € | 48 % | 1.833 € |
| 10 % | 72,64 € | 32,47 € | 45 % | 1.624 € |
| 21 % | 66,03 € | 25,86 € | 39 % | 1.293 € |

Es margen **bruto**: aún hay que restar envío (gratis desde 55 € en España peninsular), embalaje, comisión de pago y publicidad. No sé si los 2.008,60 € incluyen IVA, transporte o aranceles.

**Consecuencia para la publicidad:** el margen disponible por venta (≈25–36 € antes de envío y comisiones) es el techo para el coste por adquisición. Con 100 € de prueba y un clic a 0,50 € (cifra supuesta, no medida), harían falta ~2 % de conversión para quedar en el punto de equilibrio; con menos, perderías dinero. Por eso recomiendo seguir empezando por canales gratuitos.

**Incoherencia detectada:** la barra de anuncios y el carrito dicen "Envío gratis desde 80 €", pero Shopify aplica envío gratis en España peninsular y Baleares desde **55 €**. Hay que alinear una de las dos.

### Aclaración posterior (18/10/2026)
- Los 2.008,60 € son el **coste total** de las 50 bolsas (40,17 € por bolsa). Los márgenes de la tabla anterior se mantienen.
- Si ese total incluye IVA soportado que puedas deducir, tu coste neto real es menor y el margen, mayor. A modo de ejemplo: con 21 % incluido, serían ~33,20 € por bolsa.
- El **tipo de IVA aplicable a la venta (4 %, 10 % o 21 %) no está confirmado**: mi búsqueda no encontró una fuente que lo fije para el té matcha. Hay que confirmarlo con tu gestor o con la Agencia Tributaria (Ley 37/1992, art. 91).
- No se ha podido publicar el tema ni revisar el menú renderizado desde este entorno (publicar temas está bloqueado para las herramientas y el dominio no es accesible desde aquí).
