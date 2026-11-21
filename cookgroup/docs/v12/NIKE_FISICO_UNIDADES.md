# Fase 3 · Nike/SNKRS (9), stock en tienda física (12) y unidades por talla (5)

Cada aviso usa solo lo que su fuente puede demostrar:

| Tipo de aviso | Qué hace falta para publicarlo | Qué tenemos hoy |
|---|---|---|
| Lanzamiento anunciado | Calendario oficial o ficha de la tienda | Sí: calendario BSTN, KICKZ (Releases) y fichas de las tiendas. Nike solo a través de tiendas autorizadas |
| Talla disponible online | Disponibilidad por talla en la ficha pública | Sí: Shopify (154 tiendas), 43einhalb, Basket4Ballers, New Balance ES y Zalando ES |
| Disponible para recogida en una tienda concreta (local y ciudad) | Una fuente que publique stock por tienda física | No hay fuente pública autorizada (las apps la usan internamente) → proveedor con licencia |
| Número exacto de unidades | Que la fuente publique la cifra | Ninguna fuente pública la da → proveedor con licencia |

**Nike/SNKRS**: Nike no ofrece una API pública para terceros. Hay dos opciones: cubrir Nike a través de las tiendas autorizadas que ya monitorizamos y de #próximos-7-días, o contratar un proveedor.

**Proveedores**: no publican tarifas. Venden por ticket a dueños de grupos («requiere presupuesto»).
- Sole Retriever (raffles, más de 500 tiendas, 75 $/mes publicado). No confirma cobertura de la UE ni de España; hay que preguntarlo.

Integración preparada: un proveedor que envíe webhooks de Discord se conecta pegando su webhook en el canal correspondiente. No hace falta código: el bot no reescribe sus mensajes y el canal queda marcado «fuente: proveedor X».
