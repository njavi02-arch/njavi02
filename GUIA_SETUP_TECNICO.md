# 🔧 GUÍA DE SETUP TÉCNICO - AUTOMATIZACIÓN COMPLETA

## 🎯 OBJETIVO
Tener todo configurado en **UNA SEMANA** para comenzar a vender sin hacer nada manualmente.

---

## 📋 CHECKLIST TÉCNICO

### PASO 1: Dominio y Email (Día 1)

- [ ] Registrar dominio `.store` en Namecheap/GoDaddy
  - Nombre: **breathewell.store** o similar
  - Costo: $8-15/año
  - Usa WHOIS Guard (privacidad)

- [ ] Crear email profesional
  - **Opción A:** Gmail + alias personalizado
  - **Opción B:** Zoho Mail gratuito (5 cuentas gratis)
  - Email: **info@breathewell.store**

---

### PASO 2: Tienda Online (Día 1-2)

#### OPCIÓN A: SHOPIFY (Recomendado)
```
1. Ve a https://www.shopify.com/es
2. Haz click en "Comienza prueba"
3. Email/Contraseña
4. Nombre tienda: "BreatheWell Store"
5. País: Tu país
6. Elige plan $29/mes

CONFIGURACIÓN INICIAL:
• Dominio: Conecta tu dominio personalizado
• Tema: Elige "Prestige" o "Brooklyn"
• Productos: Importa desde Oberlo
• Pagos: Configura Stripe + PayPal
• Email: Activa notificaciones automáticas
• Inventory: Synch con Oberlo
```

**Apps necesarias en Shopify:**
1. Oberlo (Dropshipping automático)
2. Wishlist Plus (Clientes guardan items)
3. Email Automation (Recordatorios)
4. Printful (Si quieres custom products)

#### OPCIÓN B: TU PROPIO HTML + FORMA DE PAGO
- Sube **index.html** a tu hosting
- Conecta forma de pago manualmente
- Más trabajo pero control total

---

### PASO 3: Sistema de Pagos (Día 2)

#### STRIPE (Recomendado)
```
1. Ve a https://stripe.com
2. Registrate con tu email
3. Verifica tu identidad
4. Conecta cuenta bancaria
5. Obtén API keys
6. Integra en Shopify o tu sitio
```

**Costos Stripe:**
- 2.9% + $0.30 por transacción
- Ejemplo: Venta de $20 = Te llega $19.10

#### PAYPAL
```
1. Ve a https://www.paypal.com
2. Crea cuenta "Negocios"
3. Conecta cuenta bancaria
4. Obtén botón de pago
5. Integra en tu sitio
```

---

### PASO 4: Dropshipping Setup (Día 3)

#### EN SHOPIFY + OBERLO:
```
1. Instala Oberlo desde App Store de Shopify
2. Conecta tu cuenta AliExpress
3. Busca "smokeless inhaler"
4. Selecciona producto (rating 4.5+)
5. Click "Import to store"
6. Ajusta precio:
   - AliExpress: $3 USD
   - Tu precio: $19.99 USD
   - Markup: 666%
```

#### CONFIGURAR OBERLO:
```
Settings → Oberlo
• Auto-fulfill orders: ACTIVADO
• Shipping time: 20-35 días
• Automático: Cuando pagan, ordena a AliExpress
```

---

### PASO 5: Automatización de Emails (Día 3)

#### EMAIL MARKETING AUTOMÁTICO (Mailchimp)
```
1. Ve a https://mailchimp.com
2. Registrate gratis
3. Crea lista de emails
4. Crea automatizaciones:

SECUENCIA 1: Bienvenida
- Email 1 (0 min): Gracias por visitar
- Email 2 (2 hrs): Primero 10% descuento
- Email 3 (24 hrs): Testimonios

SECUENCIA 2: Carrito abandonado
- Email 1 (1 hr): Olvidaste algo
- Email 2 (24 hrs): Última oportunidad
- Email 3 (48 hrs): Descuento final

SECUENCIA 3: Post-Compra
- Email 1 (0 min): Confirmación
- Email 2 (3 días): ¿Recibiste?
- Email 3 (7 días): Reseña
- Email 4 (30 días): Compra de nuevo
```

---

### PASO 6: Analytics y Seguimiento (Día 4)

#### GOOGLE ANALYTICS (Gratuito)
```
1. Ve a https://analytics.google.com
2. Crea propiedad
3. Obtén Google Tag (código)
4. Integra en tu sitio/Shopify
5. Comienza a trackear:
   - Visitantes
   - Tiempo en página
   - Conversión
   - Productos más vendidos
```

#### FACEBOOK PIXEL (Para publicidad futura)
```
1. Ve a facebook.com/business
2. Crea "Pixel de seguimiento"
3. Obtén código
4. Integra en sitio
5. Comenzará a trackear visitantes
```

---

### PASO 7: Integraciones Automáticas (Día 5)

#### CONECTAR INSTAGRAM A TU TIENDA

**Opción A: Shopify Shop** 
```
Shopify → Settings → Sales Channels
Instala "Instagram"
Conecta tu cuenta Instagram
Publica productos directamente desde Shopify
```

**Opción B: Link en Bio (Más manual)
```
Bio Instagram: https://breathewell.store
Uses Linktree para múltiples enlaces:
- Tienda
- Instagram
- WhatsApp contacto
```

#### WHATSAPP BUSINESS (Automatización de mensajes)
```
1. Descarga WhatsApp Business
2. Verifica número
3. Instala Chatbot: Manychat o MobileMonkey
4. Automatiza respuestas:
   - "Hola, gracias por contactar"
   - "¿Preguntas sobre envío?"
   - "¿Quieres descuento?"
```

---

## ⚙️ FLUJO AUTOMÁTICO COMPLETO

```
CLIENTE VISITA TU WEB
        ↓
   VE EL PRODUCTO
        ↓
   AGREGA AL CARRITO
        ↓
   (EMAIL: Descuento 10%)
        ↓
   REALIZA COMPRA CON STRIPE
        ↓
   (EMAIL: Gracias, confirmación)
        ↓
   OBERLO AUTOMÁTICAMENTE:
   - Compra en AliExpress
   - Con dirección del cliente
   - Envía tracking
        ↓
   PROVEEDOR ENVÍA
        ↓
   CLIENTE RECIBE
        ↓
   (EMAIL 30 DÍAS: Compra de nuevo)
        ↓
   ¡TÚ GANAS!
        ↓
   REPITE PROCESO
```

---

## 💰 PRESUPUESTO MENSUAL INICIAL

| Item | Costo | Obligatorio |
|------|-------|-----------|
| Dominio | $1/mes | ✅ |
| Shopify | $29/mes | ⚠️ |
| Stripe/PayPal | Comisión | ✅ |
| Oberlo | Gratis | ✅ |
| Mailchimp | Gratis | ✅ |
| Google Analytics | Gratis | ✅ |
| **TOTAL** | **$30-35** | |

**NOTA:** Si usas tu HTML + forma de pago manual, puedes bajar a $1-5/mes

---

## 🚀 ORDEN DE IMPLEMENTACIÓN (POR DÍAS)

### DÍA 1: Cimientos
- [ ] Dominio registrado
- [ ] Email profesional creado
- [ ] Shopify cuenta creada (o hosting)

### DÍA 2: Pagos
- [ ] Stripe conectado
- [ ] PayPal conectado
- [ ] Prueba de transacción hecha

### DÍA 3: Productos
- [ ] Oberlo instalado
- [ ] 5 productos importados
- [ ] Precios ajustados
- [ ] Emails automáticos creados

### DÍA 4: Tracking
- [ ] Google Analytics configurado
- [ ] Facebook Pixel puesto
- [ ] Dashboards listos

### DÍA 5: Instagram
- [ ] Cuenta creada
- [ ] Bio optimizada
- [ ] Primeros posts programados
- [ ] Instagram Shop conectado (si aplica)

### DÍA 6: Testing
- [ ] Compra de prueba realizada
- [ ] Verificar email automático
- [ ] Verificar Oberlo compra
- [ ] Verificar tracking

### DÍA 7: Launch
- [ ] Publicar primeros posts Instagram
- [ ] Invitar amigos
- [ ] Monitorear estadísticas
- [ ] Responder comentarios

---

## 🔐 SEGURIDAD Y LEGAL

### Configurar HTTPS
- Shopify lo hace automático
- Si es tu propio sitio: Usa Let's Encrypt (gratis)

### Política de Privacidad
```
Tienda → Configuración → Políticas
Crea:
- Política de Privacidad
- Términos de Servicio
- Política de Devoluciones
- Aviso Legal (NO es medicamento)
```

### Impuestos y Regulación
- Consulta con accountant local
- Declara ingresos en impuestos
- Mantén registros de ventas

---

## 📱 APPS RECOMENDADAS

### SHOPIFY
1. **Oberlo** (Dropshipping) - FREE
2. **Mailchimp** (Email) - FREE
3. **Yotpo** (Reseñas) - $39/mes
4. **Klaviyo** (Email pro) - FREE
5. **Slack** (Notificaciones) - FREE

### GENERAL
1. **Zapier** (Automatización) - $20/mes
2. **Buffer** (Social media) - $5/mes
3. **Canva Pro** (Diseño) - $120/año
4. **Later** (Instagram scheduler) - $15/mes

---

## 🎯 VERIFICACIÓN FINAL (Checklist de Lanzamiento)

ANTES de lanzar públicamente, verifica:

- [ ] Página web funciona en mobile
- [ ] Todos los botones funcionan
- [ ] Carrito y checkout funcionan
- [ ] Pagos procesados correctamente
- [ ] Emails se envían automáticamente
- [ ] Orden llega a Oberlo/AliExpress
- [ ] Tracking se actualiza
- [ ] Analytics trackea visitas
- [ ] Instagram está listo
- [ ] WhatsApp Business responde

---

**Próximo paso:** Comenzar con Día 1 del cronograma

**¿LISTO? ¡VAMOS!**
