# 📱 CÓMO SUBIR LA WEB VITALAIR A SHOPIFY

**Opción A: Como Página Custom (RECOMENDADO - 5 minutos)**

## Paso 1: Acceder a Shopify Admin
1. Entra a tu tienda Shopify: `https://[tu-tienda].myshopify.com/admin`
2. Navega a **Tienda Online** → **Páginas**

## Paso 2: Crear Nueva Página
1. Haz clic en **Agregar página**
2. Título: `VitalAir - Home`
3. En el editor, selecciona **<> HTML** (esquina superior derecha)

## Paso 3: Pegar el HTML
1. Abre el archivo `vitalair-theme-ready.html`
2. Copia TODO el contenido (Ctrl+A → Ctrl+C)
3. En Shopify, pega en el editor HTML
4. Haz clic en **Guardar**

## Paso 4: Ver la página
- Tu página estará en: `https://[tu-tienda].myshopify.com/pages/vitalair-home`
- Puedes cambiar el slug ("vitalair-home") en la sección URL

---

**Opción B: Como Tema Borrador (Más complejo - 15 minutos)**

## Paso 1: Crear Tema Borrador
1. Ir a **Tienda Online** → **Temas**
2. En **Temas duplicados**, haz clic en el menú (⋯) de tu tema actual
3. Selecciona **Duplicar**
4. Nombre: `VitalAir Borrador`

## Paso 2: Editar el Tema
1. En el nuevo tema, haz clic en **Editar código**
2. Busca el archivo `layout/theme.liquid` (o la página de inicio)
3. Reemplaza el contenido con el HTML de `vitalair-theme-ready.html`

## Paso 3: Publicar como Vista Previa
1. No publiques aún (deja como borrador)
2. Haz clic en **Vista previa** para verlo en acción
3. Comparte el enlace de vista previa con quien necesites

---

**Opción C: Como Sección Personalizada (Avanzado)**

Si quieres integrarlo en tu tema actual:

1. Ir a **Temas** → **Editar código**
2. Crear nuevo archivo: `sections/vitalair-home.liquid`
3. Pegar el código HTML (sin los tags `<html>`, `<head>`, `<body>`)
4. Agregar la sección a tu home page

---

## 📊 DIFERENCIAS ENTRE OPCIONES

| Aspecto | Opción A (Página) | Opción B (Tema) | Opción C (Sección) |
|---------|---|---|---|
| **Tiempo** | 5 min | 15 min | 20 min |
| **Complejidad** | Fácil | Media | Avanzada |
| **Vista Previa** | Inmediata | Inmediata | En tu tema |
| **Publicación** | Fácil | Fácil | Integrada |
| **Mobile Responsive** | ✓ | ✓ | ✓ |
| **Editable después** | ✓ Contenido | ✓ Código | ✓ Código |

---

## 🎯 MI RECOMENDACIÓN

**Usa Opción A** porque:
- ✓ Más rápido implementar
- ✓ Puedes previsualizar inmediatamente
- ✓ No afecta tu tema actual
- ✓ Perfecta para testing
- ✓ Luego migras a tema si gusta

---

## 🔧 DESPUÉS DE SUBIR

### Paso 1: Verificar en Desktop + Mobile
- Abre la página en desktop (full screen)
- Abre en teléfono (responsive)
- Verifica que todo se vea bien

### Paso 2: Personalizar (si necesario)
- Cambiar colores: busca `--primary: #1a4d2e` en el `<style>`
- Cambiar textos: busca y reemplaza
- Cambiar precios: edita €19.99, €49.99, €89.99

### Paso 3: Conectar Carrito
- El botón "Comprar ahora" aún es un mock
- Cuando digas "web ok", agrego integración real de Stripe

### Paso 4: Conectar SEO
- Titulo: editar en "Configuración de página"
- Descripción: agregar en "Configuración de página"
- Meta tags: agregar en el `<head>`

---

## ⚠️ NOTAS IMPORTANTES

1. **Sin dependencias externas** - El HTML no depende de librerías o CDNs
2. **Mobile-first** - Está optimizado para teléfono y desktop
3. **Compatible con Shopify** - Funciona en cualquier tema
4. **Fácil de editar** - Todo está en un archivo

---

## 📞 SI ALGO FALLA

### Problema: "HTML no se renderiza correctamente"
**Solución:** Asegúrate de copiar TODO el contenido (desde `<!DOCTYPE>` hasta `</html>`)

### Problema: "Los estilos se ven raros"
**Solución:** Algunos temas de Shopify pueden tener CSS en conflicto. 
- Opción 1: Pon el HTML en una página separada (Opción A)
- Opción 2: Rodea todo con `<style scoped>` (Opción B)

### Problema: "Los colores no son los correctos"
**Solución:** Busca en el HTML los valores de color:
- `#1a4d2e` = Verde oscuro (principal)
- `#27ae60` = Verde claro (secundario)

---

**¿Necesitas ayuda? Responde con qué opción elegiste y te doy instrucciones paso a paso.**
