# Punto de reanudación — 23-nov-2026

Rama `claude/cookgroup-v1.0`. Pruebas: **605 passed, 0 skipped**. Monitores configurados: 285 (198 con canal propio, 275 con fuente comprobada).
Inventario de referencia: 339 funciones (147 probadas en local, 87 construidas, 105 investigadas; 0 instaladas en Discord). El inventario lee ahora el estado de config/lote*_tiendas.toml y de las muestras Shopify, no de una tabla a mano.

## Lotes del brief del 23-nov
| Lote | Estado | Commits |
|---|---|---|
| 1 · Foot Locker ES/FR/DE y ASICS ES por talla y color; prueba 44,5 con reinicio | hecho | 5e8eb6c |
| 2 · Descubrimiento comprobado en vivo por tienda; Zalando ES filtra /faq/ y parámetros; raffles abiertos visibles para un miembro nuevo | hecho | 6d4ccd8, 30f3424 |
| 3 · ASOS, About You, Sivasdescalzo, GAME, El Corte Inglés, DRIM, Toys"R"Us, UGG, Sports Direct, Alcampo, Basketball Emotion y Footshop | hecho | 12cb84d…e03b325, 2d80951 |
| 3 · Bloqueadas (desafío anti-bot sin cookies, no se tocó): Carrefour, Fnac, YOOX, LuisaViaRoma. Darizard sin dominio | registrado en docs/v12/TIENDAS_LOTE3.md | 2d80951 |
| 4 · Fiabilidad (1 de 10 fichas caída, página incompleta, orden, dos colores, canal pendiente tras reinicio, envío incierto) y velocidad de inicio a inicio | hecho | 7cbb903, 4489881, 2cf123c |
| Pruebas omitidas: Yellowshop (título = código → nombre desde el handle, muestra nueva del 23-nov) y Childsplay (tienda solo infantil → desactivada) | hecho | este commit |
| 5 · Windows: `VERIFICAR.bat` con pasos separados (tienda / Discord / alerta / arranque), guía docs/v12/VERIFICAR_EN_WINDOWS.md | hecho aquí con simulación; **falta ejecutarlo en el PC del dueño** | ver git log |

## Para verificar en el PC (no se puede desde aquí: la red del entorno solo llega a registros de paquetes)
- Footshop: la ficha pedida sin navegador devolvió 400. Si el ciclo real lo repite, el panel lo marca en error y no hay avisos falsos.
- adidas ES (ficha) y New Balance ES (listado) dan desafío anti-bot sin cookies.
- `tools/medir_intervalos.py` en modo real: intervalo observado por tienda.

## Punto 2 · monitores sin hacer (23-nov, en curso)
- Hecho: Supreme EU, Mattel Creations, MilfShakes, Funko ES, contador «Miembros: N» (probado), sorteos internos (SORTEO.bat + resolución automática).
- Bloqueados con motivo en el inventario: Zara, Uniqlo, H&M y Sephora (ficha con desafío), Pop Mart (permiso de la extensión), Steiff (sin tienda ES), Amazon (afiliado con ventas), X/Twitter (API de pago), Nike/stock en tienda/cifras de unidades (sin fuente pública a 0 €).
- Siguiente: adaptador «solo listado» para H&M y Sephora (aviso de producto nuevo sin precio); 28 tiendas TCG sin muestra propia.

## Pendiente por decisión del dueño (23-nov 10:53)
- Canales del staff y del mercado entre miembros (71 de las 87 funciones construidas): necesitan el servidor instalado y personas.

## Siguiente acción exacta
1. Pendientes del inventario con los accesos actuales: canales «construidos» sin prueba (docs/v12/INVENTARIO_MAESTRO.csv, estado_tecnico=construido), flujos editoriales, guías y permisos del mercado.
2. El dueño ejecuta en su PC: INSTALAR.bat → .env → VERIFICAR.bat → INSTALAR_SERVIDOR.bat → VERIFICAR.bat alerta → INSTALAR_AUTOARRANQUE.bat. Con el resultado de logs\verificar.txt, corregir lo que falle.
