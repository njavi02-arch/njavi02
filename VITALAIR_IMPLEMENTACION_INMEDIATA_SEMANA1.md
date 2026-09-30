# VitalAir - Plan de Implementación ESTA SEMANA
## Pasos Prioritarios P0 (Críticos)

**Estado Actual:** 3 productos ACTIVOS y publicados en Shopify  
**Objetivo:** Tienda funcional y lista para primera venta en 7 días

---

## ✅ YA COMPLETADO (Hecho por Claude)

### Shopify - Productos (LISTO)
- [x] 3 productos publicados (estado ACTIVE)
- [x] Precios correctos: €19.99, €49.99, €89.99
- [x] Stock disponible: 100 unidades cada uno
- [x] Descripciones completas y optimizadas
- [x] SKUs configurados
- [x] Títulos optimizados para SEO

### Documentación Estratégica (LISTO)
- [x] Diagnóstico completo de la tienda
- [x] Estructura de homepage recomendada
- [x] Copywriting para todas las secciones
- [x] Plan de marketing de 3 fases
- [x] Checklist de optimización

### Páginas Web (LISTO)
- [x] Landing page profesional (vitalair-landing.html)
- [x] Página de producto Premium (vitalair-producto-page.html)
- [x] Página About (vitalair-about.html)
- [x] FAQ (vitalair-faq.html)
- [x] Contacto (vitalair-contact.html)
- [x] Privacidad (vitalair-privacy.html)
- [x] Términos (vitalair-terms.html)

---

## 🚀 TAREAS P0 ESTA SEMANA (TÚ DEBES HACER)

### FASE 1: IMÁGENES (Día 1-2)
**Objetivo:** Agregar 3-5 imágenes por producto

#### Opción A: Canva (Fácil y Rápido)
1. Ir a canva.com
2. Buscar plantilla "product mockup" o "product showcase"
3. Para cada producto:
   - Crear una imagen con nombre, precio, beneficios principales
   - Descargar como PNG/JPG
   - Hacer screenshot de URL pública (opcional: subir a Canva y compartir)

#### Opción B: Imágenes Gratuitas
1. Ir a unsplash.com o pexels.com
2. Buscar: "device", "technology", "modern gadget"
3. Descargar 3-5 imágenes por producto
4. Subir a un CDN gratuito como imgbb.com:
   - Subir imagen
   - Copiar URL pública
   - Usar esa URL en Shopify

#### Opción C: Usar IA (Mejor Resultado)
1. Generar imágenes con Midjourney/DALL-E:
   ```
   "Professional product photography of sleek white tech inhaler device, 
   studio lighting, white background, premium, modern, minimal"
   ```
2. Descargar y subir a imgbb.com
3. Obtener URL pública

#### URLs Necesarias (Ejemplo)
```
Básico:
- https://imgbb.com/YOUR_IMAGE_1 (Producto frontal)
- https://imgbb.com/YOUR_IMAGE_2 (Detalles)
- https://imgbb.com/YOUR_IMAGE_3 (Incluye)

Premium:
- https://imgbb.com/YOUR_IMAGE_4 (Producto)
- https://imgbb.com/YOUR_IMAGE_5 (App)
- https://imgbb.com/YOUR_IMAGE_6 (Unboxing)

Pro:
- https://imgbb.com/YOUR_IMAGE_7
- https://imgbb.com/YOUR_IMAGE_8
- https://imgbb.com/YOUR_IMAGE_9
```

**Acción:**
1. Crear/descargar imágenes
2. Subir a imgbb.com
3. Copiar URL pública
4. Me envías las URLs
5. Yo las agrego a Shopify automáticamente

---

### FASE 2: HOMEPAGE SHOPIFY (Día 2-3)
**Objetivo:** Crear homepage de conversión en Shopify

#### En Shopify Admin:
1. Ir a `Online Store` → `Pages`
2. Crear nueva página llamada "Home"
3. O editar la página de inicio existente

#### Usar Shopify Theme Sections:
```
SECCIÓN 1: Hero
- Headline: "Empieza a Respirar el Cambio"
- Subheadline: "Inhaladores de tecnología avanzada"
- CTA: "EXPLORAR AHORA"
- Imagen de fondo (gradiente púrpura)

SECCIÓN 2: Problema (3 tarjetas)
- ❌ Culpa y frustración
- ❌ Falta de alternativas reales
- ❌ Sensación de aislamiento

SECCIÓN 3: Productos (grid 3 columnas)
- Producto 1: Básico
- Producto 2: Premium ⭐ (DESTACADO)
- Producto 3: Pro

SECCIÓN 4: Trust Badges (4 elementos)
- ✅ Envíos Rápidos
- 🔒 Pago Seguro
- ♻️ Devolución Fácil
- 👥 +100K Clientes

SECCIÓN 5: FAQ (accordion)
- ¿Cómo funciona?
- ¿Puedo devolverlo?
- ¿Es legal?
- ¿Cuánto cuesta?

SECCIÓN 6: CTA Final
- "¿Dudas? Hablamos"
- Chat / Email / WhatsApp
```

**Acción:**
- Usar Shopify Dawn theme (gratis)
- Añadir secciones via Shopify admin
- O mandarme feedback si necesitas más personalización

---

### FASE 3: MÉTODOS DE PAGO (Día 3)
**Objetivo:** Habilitar compras reales

#### En Shopify Admin:
1. `Settings` → `Payments`
2. Conectar Stripe:
   - Ir a stripe.com
   - Registrar cuenta (email + teléfono)
   - Conectar a Shopify
   - Validar cuenta bancaria

#### Métodos Soportados:
- ✅ Tarjeta de crédito (Visa, MC, Amex)
- ✅ PayPal (add-on)
- ✅ Apple Pay (automático)
- ✅ Google Pay (automático)

**Acción:**
1. Registrate en stripe.com
2. Conecta a Shopify
3. Valida cuenta bancaria
4. Prueba pago de test

---

### FASE 4: POLÍTICAS (Día 3-4)
**Objetivo:** Configurar políticas obligatorias

#### En Shopify Admin:
1. `Settings` → `Policies`
2. Configurar:

```
PRIVACY POLICY
Usar: vitalair-privacy.html (ya creada)
- Copiar contenido
- Pegar en Shopify

RETURN POLICY
"30 días dinero de vuelta.
Sin preguntas.
Envío de retorno gratis."

SHIPPING POLICY
"Envío gratis a toda Europa.
España: 2-3 días.
Resto de Europa: 3-5 días."

TERMS OF SERVICE
Usar: vitalair-terms.html (ya creada)
- Copiar contenido
- Pegar en Shopify
```

**Acción:**
1. Copiar contenido de archivos HTML
2. Pegar en Shopify policies
3. Guardar

---

### FASE 5: TEST DE COMPRA (Día 5)
**Objetivo:** Verificar que todo funciona

#### Pasos:
1. **Test Mode Stripe:**
   - Ir a Stripe dashboard
   - Activar modo test
   - Copiar tarjeta de test: `4242 4242 4242 4242`

2. **Realizar compra en Shopify:**
   - Ir a tu tienda (bqu0sm-1a.myshopify.com)
   - Seleccionar producto Premium
   - Añadir al carrito
   - Checkout
   - Email: `test@vitalair.online`
   - Dirección: Tu dirección real
   - Pago: `4242 4242 4242 4242`, fecha futura, CVC: cualquiera

3. **Verificar:**
   - Orden aparece en Shopify admin ✅
   - Email de confirmación llega ✅
   - Stripe registra transacción ✅

#### Si algo falla:
- Revisar consola Shopify (`Settings` → `Notifications`)
- Verificar Stripe está conectado
- Contactarme para ayuda

---

### FASE 6: DOMINIO PERSONALIZADO (Día 4-5)
**Objetivo:** Cambiar de bqu0sm-1a.myshopify.com a vitalair.online

#### Pasos en Shopify:
1. `Settings` → `Domains`
2. Click `Connect existing domain`
3. Seleccionar `vitalair.online`
4. Agregar registros DNS:
   ```
   A record: 23.227.38.32
   O
   CNAME: shops.myshopify.com
   ```

#### Donde editar DNS:
1. Ir a Nominalia (tu proveedor DNS)
2. `Panel de control` → Dominio
3. Editar registros DNS
4. Agregar registros de Shopify
5. Esperar propagación (15-30 min)

**Acción:**
1. En Shopify: agregar dominio
2. En Nominalia: configurar DNS
3. Esperar propagación
4. Verificar que vitalair.online funciona

---

### FASE 7: GOOGLE ANALYTICS (Día 5)
**Objetivo:** Rastrear tráfico y conversiones

#### En Google:
1. Ir a analytics.google.com
2. Crear propiedad: "VitalAir Store"
3. Obtener ID: `G-XXXXXXXXXX`

#### En Shopify:
1. `Settings` → `Apps and integrations`
2. Click `Google Analytics`
3. Conectar cuenta Google
4. Seleccionar propiedad
5. Guardar

#### Qué rastrear:
- Visitantes por día
- Tasa de rechazo (bounce rate)
- Conversiones
- Productos más vistos
- Fuente de tráfico

**Acción:**
1. Crear GA4
2. Conectar a Shopify
3. Hacer test compra
4. Verificar que aparece en analytics

---

## 📊 CHECKLIST SEMANA 1

### Día 1-2
- [ ] Crear/descargar imágenes de productos
- [ ] Subir a imgbb.com
- [ ] Conseguir URLs públicas
- [ ] Enviarme URLs

### Día 2-3
- [ ] Crear homepage en Shopify
- [ ] Añadir secciones
- [ ] Agregar trust badges
- [ ] Agregar FAQ

### Día 3
- [ ] Registrarse en Stripe
- [ ] Conectar a Shopify
- [ ] Validar cuenta bancaria

### Día 3-4
- [ ] Configurar políticas
- [ ] Copiar privacidad
- [ ] Copiar términos

### Día 4-5
- [ ] Configurar dominio personalizado
- [ ] Esperar propagación DNS
- [ ] Verificar vitalair.online

### Día 5
- [ ] Conectar Google Analytics
- [ ] Realizar test de compra
- [ ] Verificar orden en Shopify
- [ ] Verificar email de confirmación
- [ ] Verificar analytics tracking

---

## 🎯 RESULTADO ESPERADO AL FINAL DE LA SEMANA

✅ Tienda completamente funcional  
✅ 3 productos con imágenes y descripciones  
✅ Página de inicio profesional  
✅ Pagos funcionando (Stripe)  
✅ Test de compra completado  
✅ Analytics rastreando  
✅ Dominio personalizado (vitalair.online)  
✅ Listo para: Instagram ads, Google ads, email marketing

---

## 💡 PRÓXIMA FASE (Semana 2+)

Una vez completado esto:

1. **Agregar imágenes** (yo lo hago)
2. **Crear colecciones** (Básico, Premium, Pro)
3. **Setup email marketing** (Klaviyo o similar)
4. **Crear oferta especial** (15% first customer)
5. **Configurar Oberlo** (Dropshipping AliExpress)
6. **Instagram content** (Publicar posts calendar)
7. **Google Ads** (Primer presupuesto pequeño)
8. **Optimización CRO** (A/B testing)

---

## 📞 CONTACTO PARA AYUDA

Si tienes dudas en cualquier paso:
1. Envíame screenshot del error
2. Describe qué intentas hacer
3. Incluye URL de la sección
4. Yo te ayudo a resolver

---

**Versión:** 1.0 Implementation  
**Actualizado:** 30 Sept 2024  
**Tiempo estimado:** 5-7 horas distribuidas en 5 días  
**Dificultad:** Media (mostly clicking in Shopify admin)
