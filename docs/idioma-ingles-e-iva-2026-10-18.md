# Idioma inglés e IVA — análisis (18/10/2026)

## 1. Idioma inglés: estado real (comprobado vía API de Shopify)

- **Publicado** en los dos dominios (kohiycha.com y el myshopify) como idioma alternativo de los mercados *Spain* y *Unión Europea*.
- **Cobertura de traducción al inglés:**

| Contenido | Traducido |
|---|---|
| Tema (textos de interfaz y checkout) | 4.320 de 4.554 campos. De los 234 que faltan, 160 son formas plurales que el inglés no usa; faltan 74 textos reales, todos de **secciones de la home** (hero, tarjetas "Próximamente", confianza, historia, certificaciones) y de "Sobre nosotros" |
| **Ficha de RED SMILE** | **0 de 6** (título, descripción, handle, tipo, título y descripción SEO) |
| Menús (principal, pie, ayuda) | 0 de 4 |
| Páginas (Contacto, Sobre nosotros…) | 0 de 4 |
| Artículos del blog | 0 de 4 |
| Colecciones | parcial (4 de 8 con algo; Matcha Latte sin nada) |
| Fichas de productos archivados | parcial, algunas marcadas como desactualizadas (no visibles en la tienda) |

**Resultado:** la tienda en inglés es **una tienda en español con la interfaz (botones, carrito, checkout) en inglés**. El producto único, la home, los menús, el blog y "Sobre nosotros" aparecen en español.
También hay textos del carrito escritos a mano en español dentro de `cart.js` ("Tu carrito está vacío", "Quitar"…) que no pasan por traducción.

### Opciones
**A. Mantener inglés y completar traducciones.** + Cubre mercado UE angloparlante y futuras ventas; + una sola tienda multilingüe. − Hay que traducir y **revisar** ~6 campos de producto, ~74 textos de la home, 4 menús, páginas, 4 artículos y políticas; − las traducciones automáticas sin revisar dañan la marca premium; − mantenimiento en cada lanzamiento (cada categoría nueva = más traducción).
**B. Despublicar el inglés temporalmente.** + Elimina de golpe las URL `/en` con contenido en español (mala experiencia y señal de baja calidad/duplicación para Google: hreflang declara un contenido inglés que realmente está en español); + sin riesgo de textos mal traducidos; + cero coste ahora. − Los visitantes que prefieren inglés ven solo español; − si Google ya indexó `/en`, hay que vigilar la transición (comprobar en Search Console antes). Las traducciones existentes **no se borran**; se puede republicar cuando se quiera.

**Mi recomendación: B ahora, y A más adelante.** Mercado principal España, 1 producto, 50 unidades, ninguna traducción de producto/home/menús revisada. Republicar inglés cuando RED SMILE, home, menús, políticas y artículos estén traducidos y revisados por una persona (idealmente cuando haya demanda real de la UE).
**No lo he despublicado. Necesito tu autorización.**

### Preparado, sin publicar
`docs/traducciones-en-borrador.md` contiene propuestas en inglés para ficha, menú y home. **No se han registrado en Shopify**: registrarlas las publicaría de inmediato mientras el inglés siga activo.

---

## 2. IVA — no he cambiado nada

**No he elegido ningún tipo.** No hay pedidos aún (no se puede deducir lo que aplica Shopify) y la configuración fiscal no se lee por la API de administración. Esto es lo que determina el tipo:

| Producto | Naturaleza | Tratamiento probable (a confirmar) |
|---|---|---|
| RED SMILE y Matcha Premium (matcha en polvo / té) | Alimento / infusión | General de alimentos: **10 %** (art. 91 LIVA), salvo que encaje en alimentos básicos al 4 % (no lo parece). **No he encontrado una consulta vinculante de la DGT sobre matcha**; el 10 % es lo más probable, no una certeza. |
| Matcha Latte (mezclas con sabor, posible azúcar o leche en polvo) | Preparado en polvo que se disuelve en bebida | **Duda real:** si se asimila a "bebida refrescante/azucarada" por analogía con consultas de la DGT sobre polvos para reconstituir con azúcar, podría ir al **21 %**. Depende de la composición. |
| Accesorios (chawan, chasen, chashaku, colador, tazas, ThermoWave) | No alimentarios | **21 %** (tipo general) |
| Packs y sets regalo | Mezcla de alimentos y accesorios | Hay que decidir cómo tributa cada componente o si es una operación única; **consultar al gestor** |

**Jurisdicción:**
- **Península y Baleares:** IVA español.
- **Canarias:** IGIC, no IVA. **Ceuta y Melilla:** IPSI. Tienes envíos configurados a esas zonas (14,99 €, "gestión aduanera"); el tratamiento del IVA/IGIC en esas ventas debe fijarlo tu gestor.
- **Resto de la UE (consumidores):** desde el 1/7/2021 el umbral único es de **10.000 €** anuales de ventas a distancia intracomunitarias. Por debajo se aplica IVA español; por encima, el tipo del país de destino, declarado por la **ventanilla única (OSS)**. Fuente de resumen: [AEAT – IVA comercio electrónico](https://sede.agenciatributaria.gob.es/Sede/iva/iva-comercio-electronico/quienes-afectan.html).
- **Empresas (cafeterías) de la UE con NIF-IVA válido:** entrega intracomunitaria exenta (inversión del sujeto pasivo). Relevante para el formato de 1 kg.

**Fuentes que he podido consultar:** solo resultados de búsqueda (no he podido abrir BOE ni la sede de la AEAT desde mi entorno). Referencias para que tu gestor las compruebe: Ley 37/1992, art. 91; [tipos de IVA 2023 (AEAT, PDF)](https://www3.agenciatributaria.gob.es/static_files/Sede/Tema/IVA/Novedades/Empresas/2023/Tipos_IVA%20_2023.pdf); buscador de consultas de la DGT (PETETE, `petete.tributos.hacienda.gob.es`) para "matcha", "té en polvo", "infusiones".

**Qué debes confirmar antes de tocar la configuración fiscal de Shopify:**
1. Tipo aplicable al **matcha en polvo** (RED SMILE / Matcha Premium): 4 %, 10 % o 21 %.
2. Tipo de las **mezclas Matcha Latte** según su composición (¿azúcar, edulcorantes, leche en polvo?).
3. Tratamiento de **packs/sets**.
4. Tratamiento en **Canarias, Ceuta y Melilla**.
5. Si prevés superar **10.000 €** de ventas a consumidores de otros países UE (OSS).
6. Si los **2.008,60 €** de coste incluyen IVA soportado deducible.

**Cómo se configuraría en Shopify, cuando lo confirmes:** Ajustes → Impuestos y aranceles → España: tipo base (21 % para no alimentación) y **anulación de impuestos por colección/producto** para los alimentos; precios ya incluyen impuestos (`taxesIncluded: true`, comprobado).

---
## Actualización (18/10/2026)
Con la autorización del propietario ("haz todo eso"), el inglés se ha **despublicado** (`shopLocaleUpdate`, `published: false`). Para republicarlo: Ajustes → Idiomas → English → Publicar. Las traducciones existentes no se han borrado.
