# Paleta extraída de la foto de referencia (RED SMILE, 2000×2000)

Medida con promedio de píxeles por zonas (no a ojo).

| Uso | HEX | Origen |
|---|---|---|
| Fondo principal | #211610 | Fondo de la foto (#221711 arriba, #211610 abajo/lados) |
| Fondo secundario (tarjetas, detalles) | #2B1A14 | Variante algo más clara del fondo, para separar bloques |
| Rojo principal (botones, acentos) | #A03430 | Color dominante de la bolsa (22 % de la imagen) |
| Rojo claro (hover, textos sobre oscuro) | #B74E48 / #E4574D | Zona iluminada de la bolsa (#B74E48); #E4574D es una variante aún más clara para que el texto pequeño cumpla contraste sobre #211610 |
| Rojo sombra (hover sobre claro) | #6E2922 | Zona en sombra de la bolsa |
| Texto sobre oscuro | #F3ECE0 | Crema de la marca (el texto impreso de la bolsa es blanco roto) |

Tokens en `config/settings_data.json`: `color_brown_900` = #211610, `color_matcha_700` = #A03430, `color_matcha_500` = #E4574D.
Ficha RED SMILE oscura: se reasignan los tokens dentro de `#MainContent` (layout/theme.liquid), solo si el producto tiene la etiqueta "red smile".

Pendiente: #B3261E (rojo anterior) sigue en assets/theme.css (cursor) y en estilos de otras secciones.
