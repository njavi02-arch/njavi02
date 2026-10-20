# Devoluciones: auditoría y política propuesta (2026-10-20)

## Qué he podido y qué no
- Leído vía Admin API: las 6 políticas de Shopify, páginas, menús y el código del tema (textos de ficha, FAQ, barra de confianza).
- NO he podido: ver la web real (el entorno no llega a kohiycha.com ni a checkout.shopify.com), ver el checkout, leer la configuración de "Devoluciones" del admin de Shopify (reglas de devolución / devoluciones autoservicio), ni **editar las políticas** (la conexión no tiene el permiso `write_legal_policies`).
- BOE inaccesible desde el entorno: la normativa se contrastó con fuentes secundarias (ver abajo). Hay que validar con un jurista.

## Hallazgos (política vigente, REFUND_POLICY)
1. **HTML escapado (visible como etiquetas).** Las 6 políticas están guardadas como `<p>&lt;div&gt;…&lt;/div&gt;</p>`: es texto con las etiquetas escapadas, por lo que en la tienda probablemente se ven `<h2>`, `<strong>`… como texto. Inferido de los datos guardados; no lo he visto en la web.
2. **Cita legal equivocada.** Cita el art. 103.d) para alimentos abiertos; la letra d) es "bienes que puedan deteriorarse o caducar con rapidez". La excepción aplicable es la **103.e**: bienes precintados no aptos para devolución por salud/higiene **y desprecintados tras la entrega**. Además la política la extiende a "cualquier producto alimenticio" y a "café", y no hay café a la venta.
3. **Reembolso con plazo desfavorable.** Dice "14 días desde que recibimos e inspeccionamos". La ley (art. 107) da 14 días naturales **desde que se comunica el desistimiento**, pudiendo retener hasta recibir el producto o prueba de envío. Falta decir que se reembolsa el **envío estándar inicial**.
4. **Condiciones de estado demasiado estrictas.** "Perfecto estado", "embalaje original", "condiciones que permitan su posterior venta": la ley solo permite descontar la disminución de valor por manipulación más allá de lo necesario (art. 108.2, a confirmar en BOE).
5. **Plazo de 48 h para defectos/daños.** Como condición, limita derechos irrenunciables. Debe ser una recomendación, no un límite.
6. **Falta el modelo de formulario de desistimiento** (obligación de información previa, art. 97 y anexo).
7. **Accesorios y café:** la política y los Términos hablan de termos, tazas, batidores y café; ahora solo se vende RED SMILE.
8. **Envíos (SHIPPING_POLICY):** "paquetes rechazados… se descontarán del reembolso" puede chocar con el desistimiento; y "no nos hacemos responsables de retrasos" conviene revisarlo con un jurista.
9. **Términos:** la garantía "de origen no imputables al uso normal" no coincide con la redacción legal (falta de conformidad, 3 años). Revisar.
10. **Función de desistimiento online (botón).** La Directiva (UE) 2023/2673 (art. 11 bis) es aplicable desde el 19-jun-2026; según OCU, España aún no la había transpuesto. Consultar con un jurista si se necesita un botón/función de desistimiento en la web.
11. **Aviso Legal (página sin publicar)** enlaza a la plataforma ODR europea, que dejó de existir en 2025 (a confirmar). Está sin publicar; no se usa.
12. **Enlaces del menú:** los menús Footer/Ayuda se ven con prefijo `/en/…` en la API (inglés ya despublicado). No he podido comprobar si redirigen bien; revisar en la web real.

## Lo que está bien
- Plazo de 14 días naturales desde la recepción.
- Los gastos de devolución a cargo del cliente están informados (necesario para poder exigirlos).
- Enlace "Devoluciones y reembolsos" en el menú Ayuda y en la ficha de producto; textos de FAQ/barra de confianza/ficha coherentes con la política actual.
- Datos de contacto coherentes en todas las políticas (kohicha@hotmail.com, 619 669 170).

## Cambios hechos
- Copia de seguridad de la política original: `backup/2026-10-20-politica-devoluciones-original.md`.
- Página "Matcha para negocios" (sin publicar): envío gratuito 80 € → 55 € (coincide con Shopify).

## Pendiente (requiere que lo hagas tú)
1. Ajustes → Políticas → Política de devoluciones: pegar el HTML de abajo (en modo `<>` del editor, para que no se escape).
2. Repetir el punto 1 (modo `<>`) con las otras políticas para quitar el escape; si quieres, te preparo el HTML limpio de cada una.
3. Revisar en Ajustes las reglas de devolución de Shopify y qué ve el cliente en la cuenta.
4. Validación jurídica de los puntos 2, 8, 9 y 10.
5. Cuando pegues la política, ajusto los textos del tema (FAQ, barra de confianza, ficha) a la nueva redacción.

## Política propuesta (HTML)
Mantiene lo que ya prometías (devolución a cargo del cliente salvo defecto/error; sin devoluciones gratuitas ni plazos especiales).

```html
<p><strong>Última actualización:</strong> 20 de octubre de 2026</p>
<p>Esta política explica cómo puedes desistir de una compra, devolvernos un producto o reclamar si algo no llega como esperabas. Se rige por el Real Decreto Legislativo 1/2007 (Ley General para la Defensa de los Consumidores y Usuarios) y por la normativa de la Unión Europea sobre contratos a distancia. Nada de lo que aquí se indica limita los derechos que la ley te reconoce como consumidor.</p>
<h2>1. Derecho de desistimiento (14 días)</h2>
<p>Tienes <strong>14 días naturales</strong> para desistir de la compra sin necesidad de justificarlo. El plazo empieza el día en que tú, o un tercero que designes (distinto del transportista), recibe el pedido. Si el pedido llega en varias entregas, cuenta desde la recepción del último bien.</p>
<p>Para ejercerlo, comunícanos tu decisión de forma clara por email a <strong>kohicha@hotmail.com</strong> indicando tu nombre, el número de pedido y los productos. Puedes usar el formulario del punto 8 o cualquier otra declaración inequívoca. Basta con que envíes la comunicación antes de que termine el plazo.</p>
<h2>2. Excepción para alimentos desprecintados</h2>
<p>El desistimiento no es posible para <strong>bienes precintados que no sean aptos para ser devueltos por razones de protección de la salud o de higiene y que hayan sido desprecintados tras la entrega</strong> (art. 103.e del Real Decreto Legislativo 1/2007). En la práctica, si abres el envase sellado de un alimento como el matcha, ya no podemos aceptar su devolución por desistimiento. Mientras el envase siga cerrado y precintado, puedes desistir con normalidad.</p>
<p>Esta excepción <strong>no se aplica</strong> si el producto llega dañado o defectuoso, o si hay un error en tu pedido (ver punto 5).</p>
<h2>3. Cómo devolver el producto</h2>
<ol><li>Escríbenos a kohicha@hotmail.com dentro del plazo de 14 días naturales.</li><li>Te confirmaremos por email los pasos y la dirección a la que enviarlo.</li><li>Devuelve el producto sin demora indebida y, como máximo, en los 14 días naturales siguientes a la fecha en que nos comuniques tu decisión.</li></ol>
<p><strong>Gastos de devolución:</strong> los costes directos de devolver el producto corren a tu cargo, salvo que se trate de un producto defectuoso, dañado o de un error nuestro, en cuyo caso los asumimos nosotros.</p>
<p><strong>Estado del producto:</strong> puedes manipularlo lo necesario para comprobar su naturaleza y características. Si lo manipulas más de lo necesario y eso reduce su valor, podremos descontar esa disminución de valor del reembolso.</p>
<h2>4. Reembolso</h2>
<p>Te reembolsaremos todo lo que hayas pagado por los productos y el coste del envío estándar inicial, sin demora indebida y como máximo en <strong>14 días naturales desde que nos comuniques tu decisión de desistir</strong>. Podemos retener el reembolso hasta recibir los productos o hasta que acredites haberlos enviado, lo que ocurra primero. Si elegiste una modalidad de envío más cara que la estándar, no reembolsamos el coste extra. Lo haremos por el mismo medio de pago que usaste en la compra.</p>
<h2>5. Producto dañado, defectuoso o pedido incorrecto</h2>
<p>Si tu pedido llega dañado, con un defecto o es distinto al que pediste, escríbenos a kohicha@hotmail.com lo antes posible adjuntando fotografías del producto y del embalaje; así podemos reclamar al transportista. Te recomendamos hacerlo en las primeras 48 horas, pero este aviso rápido es solo una ayuda para resolverlo antes y <strong>no limita tus derechos legales</strong>. Asumimos los gastos de devolución y te ofreceremos la reparación, la sustitución o el reembolso que corresponda conforme a la ley. Además, los bienes cuentan con la garantía legal de 3 años frente a faltas de conformidad.</p>
<h2>6. Cancelación antes del envío</h2>
<p>Puedes cancelar tu pedido mientras no lo hayamos enviado escribiéndonos a kohicha@hotmail.com. Te reembolsaremos el importe completo.</p>
<h2>7. Contacto</h2>
<p>KOHI &amp; CHA · kohicha@hotmail.com · 619 669 170</p>
<h2>8. Modelo de formulario de desistimiento</h2>
<p>(Solo si deseas desistir del contrato, rellena y envía este formulario por email a kohicha@hotmail.com.)</p>
<p>— A la atención de KOHI &amp; CHA, kohicha@hotmail.com:<br>— Por la presente le comunico que desisto de mi contrato de venta del siguiente producto: [producto].<br>— Pedido n.º / fecha de recepción: [número de pedido] / [fecha].<br>— Nombre del consumidor: [nombre].<br>— Domicilio del consumidor: [dirección].<br>— Fecha: [fecha].</p>
```

## Fuentes consultadas (secundarias; BOE no accesible)
- Art. 103 TRLGDCU: https://iberley.es/legislacion/articulo-103-ley-defensa-consumidores-usuarios
- Art. 108 TRLGDCU: https://iberley.es/legislacion/articulo-108-ley-defensa-consumidores-usuarios
- Precinto y TJUE C-681/17: https://www.civil-mercantil.com/proteccion-consumidores-usuarios-contratos-distancia-compraventa-online-derecho-desistimiento.html
- Función de desistimiento (Directiva 2023/2673): https://www.ocu.org/consumo-familia/compras-online/noticias/boton-desistimiento-directiva
