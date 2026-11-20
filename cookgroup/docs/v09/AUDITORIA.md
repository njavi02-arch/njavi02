# Bloque 1 · Auditoría de la referencia (20-nov-2026, solo lectura)

La tabla completa, con una fila por canal y su nivel de evidencia, está en `docs/v08/canales.csv` y en la pestaña
«Canales de la referencia» del panel.

## Niveles de evidencia (339 canales)
| Nivel | Canales |
|---|---:|
| Visto en la barra lateral | 210 |
| Función comprobada (abierto y leído el 20-nov) | 18 |
| Función comprobada (muestreo de mensajes en v0.6) | 111 |
| … con equivalente implementado y probado localmente | 146 |
| Verificado en mi Discord | **0** (falta el token del bot o el webhook de pruebas) |

97 canales dependen de algo externo: una fuente comercial, una licencia, un proveedor o moderación humana. La
dependencia de cada uno está en la columna `dependencia`.

## Los 9 foros
| Foro | Hilos visibles | Qué obtiene el miembro | Equivalente |
|---|---:|---|---|
| #important-releases | 12 (dic-2025 → nov-2026) | Un hilo por lanzamiento: veredicto, fecha, mercado, una respuesta por tienda y keywords | #lanzamientos (foro); se construye en esta versión |
| #calls-pokemon | 12 | Un hilo por expansión con veredicto | #pokémon-tcg con hilos por expansión (siguiente lote) |
| #invitaciones-pokemon | 0 visibles | — | pendiente de verificar |
| #guías-pokemon | 7 | Guías de TCG: comprar, vender, tipos de producto, envío | guías propias (editorial) |
| #calls-invest | 30 | Lanzamientos variados (consolas, periféricos, colaboraciones) | #electrónica + foro de lanzamientos |
| #calls-mattel | 6 | Hot Wheels por serie, Monster High | fuera del alcance inicial |
| #calls-funko | 43 | Un hilo por Funko Pop con fecha | fuera del alcance inicial |
| #calls-tcg | 24 | One Piece, Magic, Lorcana, Dragon Ball, Riftbound | #pokémon-tcg (ampliar a otros TCG) |
| #calls-lego | 6 | Un hilo por set, con su número (#75192…) | #lego: la identidad del artículo es el número de set |

## Market de compraventa: valor y qué exigiría
- **Qué es:** #wts, #wtb-wtt, #legit-check, #feedback, #black-list-scammers y tiendas de partners. Los miembros venden
  y compran entre ellos; #wts exige poner precio y talla.
- **Valor para el cliente:** liquidez inmediata (vender sin comisiones de plataforma), comprobación de autenticidad y
  reputación dentro de la comunidad. Retiene mucho.
- **Qué exigiría ofrecerlo:**
  - Normas de compraventa y descargo de responsabilidad.
  - Moderación diaria: retirar fraudes, gestionar la lista negra y validar el legit-check con criterio.
  - Un sistema de reputación (#feedback).
  - Decidir si se permite pago entre particulares sin protección.
  - Revisión legal: posible actividad comercial habitual de los vendedores y responsabilidad del servidor.
- **Propuesta:** lo dejo **fuera de la primera apertura**. Se puede abrir después como «Market» con 2 canales (#vendo-compro
  y #legit-check), con normas fijadas, un moderador asignado y una prueba de 30 días.

## Herramientas de terceros: valor y qué exigiría
| Grupo | Qué aporta | Qué exigiría | Decisión |
|---|---|---|---|
| Bots de compra (#adonis, #cyber, #nsb…: 11 canales) | Se ve qué compran los bots: tienda, precio, talla, hora. Es una señal de demanda | Licencias de bots de pago. Su uso suele infringir las condiciones de las tiendas | **Excluido**: no automatizamos compras. Lo útil (qué se agota) ya lo dan nuestros restocks |
| Partners de proxies y captchas (aycd, 2captcha, proxies) | Descuentos en herramientas de automatización | Acuerdos comerciales; facilitan eludir controles anti-bot | **Excluido** |
| Cashbacks (iGraal, Letyshops…) | Ahorro extra en compras | Programas de afiliación | **Posible**: guía editorial propia con enlaces de afiliado, sin coste |
| Herramientas (neobancos, Excel de inventario, guías de eBay y Vinted) | Ayuda a gestionar la reventa | Contenido editorial | **Posible**: guías propias en #guía-de-avisos |
| Consigna (Monkey) | Vender a través de un intermediario | Acuerdo comercial | Fuera del alcance inicial |

## Agrupación: muchas tiendas en un canal, sin perder control
La referencia tiene un canal por tienda (aio-eu, footdistrict, asics…). Yo propongo agruparlas en #sneakers-eu,
#sneakers-mundo, etc. **Un cliente obtiene la misma información y conserva el control así:**
1. Cada aviso lleva la tienda, el país y el canal de origen. En Discord se puede buscar `from:Cookgroup Footdistrict`.
2. En su perfil puede limitar las menciones a unas tiendas (`tiendas = ["FOOTDISTRICT", "BSTN"]`) o excluir otras
   (`excluir_tiendas`), además de filtrar por marcas, tallas, palabras, precio máximo y canales.
3. La misma señal publicada en dos canales solo le menciona una vez (comprobado en v0.8).
