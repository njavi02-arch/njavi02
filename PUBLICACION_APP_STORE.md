# 📱 GUÍA COMPLETA: Publicar YUIZZ en Google Play Store y Apple App Store

## 🎯 RESUMEN RÁPIDO
1. **Google Play Store** - Más fácil, ~2-3 horas
2. **Apple App Store** - Más estricto, ~1-2 días

---

## 📋 REQUISITOS PREVIOS (AMBAS TIENDAS)

### 1. Preparar el APK/IPA
Para convertir tu HTML a una app nativa necesitas:

```bash
# Opción A: Usar React Native (Recomendado)
npm install -g expo-cli
expo init yuizz-app
# Copiar tu código HTML dentro de una pantalla React

# Opción B: Usar Cordova
npm install -g cordova
cordova create yuizz-app
cordova platform add android ios
# Agregar tu HTML en www/index.html

# Opción C: Usar Flutter
flutter create yuizz_app
# Convertir HTML a widgets Flutter
```

### 2. Crear Cuentas Desarrollador

**Google Play Store:**
- Costo: $25 USD (ÚNICO pago)
- Crear cuenta en: https://play.google.com/console
- Tarjeta de crédito requerida
- Verificación de identidad

**Apple App Store:**
- Costo: $99 USD/año
- Crear cuenta en: https://developer.apple.com
- Requiere Mac/MacBook para compilar
- Aprobación manual más estricta

---

## 🤖 OPCIÓN MÁS FÁCIL: Usar Expo (React Native)

### Paso 1: Instalar Expo
```bash
npm install -g expo-cli
expo login  # Crear cuenta gratis en Expo
```

### Paso 2: Crear Proyecto
```bash
expo init yuizz-app --template
cd yuizz-app

# Instalar dependencias
npm install react-native-web
```

### Paso 3: Copiar tu Código HTML
```bash
# En App.js, usar WebView para mostrar tu HTML
npm install react-native-webview

# En App.js:
import { WebView } from 'react-native-webview';

export default function App() {
  return (
    <WebView
      source={{ uri: 'YOUR_APP_URL' }}
      style={{ flex: 1 }}
    />
  );
}
```

### Paso 4: Compilar APK (Android)
```bash
# Opción A: En la nube con Expo (GRATIS)
expo build:android -t apk

# Opción B: Localmente
./gradlew assembleRelease
```

### Paso 5: Compilar IPA (iOS)
```bash
# Requiere Mac
expo build:ios -t archive

# O localmente
xcodebuild -scheme yuizz_app -configuration Release
```

---

## 🟣 GOOGLE PLAY STORE - Paso a Paso

### 1. Crear Cuenta Developer
```
1. Ir a: https://play.google.com/console
2. Crear Nueva Organización
3. Pagar $25 USD
4. Verificar identidad (10-15 min)
```

### 2. Crear App
```
1. Click "Crear aplicación"
2. Nombre: YUIZZ
3. Descripción: "Conexiones Reales - Dating App"
4. Seleccionar "Apps" → "Dating & Social"
```

### 3. Llenar Información
```
Sección: Información de la Aplicación
- Nombre: YUIZZ
- Descripción corta: "Aplicación de citas con 200+ comunidades"
- Descripción completa:
  "YUIZZ es la app de dating más innovadora.
   • 200+ comunidades por intereses
   • Hot Hour: 11 PM - 12 AM GRATIS
   • Filtros de relación: €2.99
   • Redes sociales integradas
   • Premium: €2.99/mes"

Categoría: Dating
Clasificación: 17+ (Mature)

Screenshots (5 mínimo):
- Pantalla Descubrir (perfil con foto)
- Comunidades (200+ grupos)
- Mensajes (chat)
- Perfil (configuración)
- Hot Hour (banner especial)

Icono: 512x512px, PNG
Portada: 1024x500px, PNG
```

### 4. Crear y Subir APK

**Con Expo (RECOMENDADO):**
```bash
# Login en Expo
expo login

# Configurar eas.json
eas build --platform android --type apk

# Descarga automática del APK
```

**Locally (Manual):**
```bash
# Usando Android Studio
1. Tools → Create App Bundle
2. Release Build
3. Generar firma digital (keystore)
4. Output: app-release.apk
```

### 5. Crear Firma Digital (Signing)
```bash
# IMPORTANTE: Solo la primera vez
keytool -genkey -v -keystore ~/my-release-key.keystore \
  -keyalg RSA -keysize 2048 -validity 10000 \
  -alias my-key-alias
```

### 6. Configurar Privacidad y Seguridad
```
Política de privacidad: Crear en https://www.termsfeed.com
- Recopilas datos de perfiles
- Almacenas ubicación
- Monedas/Pagos

Clasificación de contenido: Enviar encuesta
- Edad mínima: 17+
- Contenido: Dating/Flirting
```

### 7. Revisar Política de Play Store

**IMPORTANTE - RESTRICCIONES:**
- ✅ PERMITIDO: Dating, chat, fotos de perfil
- ❌ NO PERMITIDO: 
  - Desnudos (NSFW)
  - Sexo explícito
  - Dinero real para citas
  - Engaño/Fraude

**Si tu app cumple**: Enviar a revisión

### 8. Enviar a Revisión
```
1. Ir a Tráfico → Lanzamiento → Versión de Producción
2. Crear versión
3. Subir APK
4. Llenar "Release notes"
5. Click: REVISAR Y LANZAR
6. ENVIAR
```

⏱️ **Tiempo de revisión:** 24-48 horas

---

## 🍎 APPLE APP STORE - Paso a Paso

### 1. Crear Cuenta Developer (REQUIERE MAC)
```
1. Ir a: https://developer.apple.com
2. Pagar $99 USD/año
3. Verificación de identidad (2-3 días)
4. Descarga Xcode (gratis, pero 15GB)
```

### 2. Crear Certificados Digitales
```bash
# En Mac
open -a Xcode

# Menú: Xcode → Preferences → Accounts
# Click: Manage Certificates
# Crear: Apple Development Certificate
# Crear: Apple Distribution Certificate
```

### 3. Crear App en App Store Connect
```
1. Ir a: https://appstoreconnect.apple.com
2. Click: + New App
3. Platform: iOS
4. Nombre: YUIZZ
5. SKU: com.yuizz.app
6. Bundle ID: com.yuizz.app
```

### 4. Llenar Información (Igual que Google Play)
```
- Nombre: YUIZZ
- Categoría: Dating
- Edad: 17+
- Descripción completa
- Screenshots (6 para iOS)
- Icono (1024x1024)
```

### 5. Compilar IPA (Requiere Mac)
```bash
# Con Xcode
xcode-select --install

# Compilar
xcodebuild -scheme yuizz_app \
  -configuration Release \
  -arch arm64 \
  -sdk iphoneos \
  -derivedDataPath build

# O con Expo
eas build --platform ios --type ipa
```

### 6. Subir IPA a App Store Connect

**Opción A: Automatizada (Recomendado)**
```bash
# Con xcrun
xcrun altool --upload-app \
  --type ios \
  --file "build/YUIZZ.ipa" \
  --username "tu@email.com" \
  --password "xxxx-xxxx-xxxx-xxxx"
```

**Opción B: Manual en Xcode**
```
1. Xcode → Product → Archive
2. Organizer → Distribute
3. App Store Connect → Upload
```

### 7. Configurar Privacidad
```
App Store Connect → Privacidad y Seguridad:
- Dónde se recopilan datos (Perfiles, Chat)
- Cómo se usan (Matching algorithm)
- Si se comparte con terceros
- Retención de datos (30 días max)
```

### 8. Enviar a Revisión
```
App Store Connect → App Version:
1. Build: Seleccionar tu IPA
2. Información: Llenar detalles
3. Clasificación: 17+
4. Adjuntos legales
5. SAVE → SUBMIT FOR REVIEW
```

⏱️ **Tiempo de revisión:** 24-48 horas (a veces 1-2 días)

---

## 🚨 CHECKLIST ANTES DE PUBLICAR

### Código y Funcionalidad
- [ ] Test en Android real
- [ ] Test en iOS real
- [ ] Sin crashes o bugs
- [ ] Conexión internet verificada
- [ ] Permisos correctos (cámara, galería, ubicación)

### Contenido
- [ ] No hay desnudos ni contenido sexual explícito
- [ ] Política de privacidad publicada
- [ ] Términos de servicio publicados
- [ ] Información de contacto clara
- [ ] Reportar/bloquear usuarios funcional

### Seguridad
- [ ] HTTPS en todos los servidores
- [ ] Datos encriptados
- [ ] No guardar contraseñas en texto plano
- [ ] Rate limiting (anti-spam)
- [ ] Verificación de edad (17+)

### Monetización
- [ ] Precios claros (€2.99)
- [ ] Proceso de compra funcional
- [ ] Reembolsos posibles
- [ ] No engañar con precios
- [ ] Política de devoluciones

### Metadatos
- [ ] Título claro: "YUIZZ - Conexiones Reales"
- [ ] Descripción convincente (máximo 4000 caracteres)
- [ ] 5+ screenshots de buena calidad
- [ ] Video promocional (opcional pero recomendado)
- [ ] Icono nítido 512x512px

---

## 💰 COSTOS TOTALES

```
Google Play Store:
- Cuenta: $25 (UNA VEZ)
- App gratis, monetización en-app: 30% comisión
- Total: $25 + 30% de ingresos

Apple App Store:
- Cuenta: $99/año
- App gratis, monetización in-app: 30% comisión
- Total: $99/año + 30% de ingresos

TOTAL PRIMEROS 2 AÑOS:
- Ambas tiendas: $125 + 30% comisión
```

---

## 📊 TIMELINE ESTIMADO

```
Semana 1:
- Lunes-Martes: Crear cuentas developer
- Miércoles: Compilar APK/IPA
- Jueves-Viernes: Llenar metadatos

Semana 2:
- Lunes: Enviar a revisión ambas tiendas
- Martes-Viernes: Esperar aprobación

TOTAL: 1-2 semanas desde desarrollo a publicación
```

---

## 🎯 DESPUÉS DE PUBLICAR

### Primeros 30 días (Lanzamiento)
1. Pedir reviews a amigos (aiming para 4+ estrellas)
2. Publicar en Twitter/TikTok/Instagram
3. Hacer referral links
4. A/B testing de descripciones

### Semanas 1-4
```
- Monitorear crashes
- Responder reviews
- Fijar bugs reportados
- Optimizar conversión a Premium
```

### Mes 2+
```
- Agregar features nuevas
- Marketing en redes sociales
- Publicidad pagada (Google Ads)
- Colaboraciones con influencers
```

---

## 🆘 PROBLEMAS COMUNES

### "App Rejected - Política de Privacidad"
**Solución:** Crear privacidad en termsfeed.com, enlazar claramente

### "Necesito verificación de edad"
**Solución:** Integrar AGE_VERIFICATION library de terceros

### "El APK es muy grande"
**Solución:** Usar App Bundles, comprimir imágenes, lazy loading

### "Crash en Android 12+"
**Solución:** Actualizar compileSdkVersion a 32+, pedir permisos correctos

### "Rechazado por "contenido sexual""
**Solución:** Remover emoji suggestivos, clarificar "dating no sexual"

---

## 📚 RECURSOS ÚTILES

**Google Play Console:**
- https://play.google.com/console
- https://developer.android.com/docs/publishing

**Apple App Store Connect:**
- https://appstoreconnect.apple.com
- https://developer.apple.com/app-store-connect

**Generadores Metadata:**
- Screenshots: Figma + plugin "App Store Screenshots"
- Privacidad: termsfeed.com
- Términos: termly.io

**Herramientas Compilación:**
- Expo: https://expo.dev
- EAS Build: https://eas.dev
- Xcode (Mac): https://apps.apple.com/app/xcode

---

## ✅ RESUMEN FINAL

**PUBLICAR YUIZZ en 2 pasos:**

1. **Usar Expo EAS** (todo automático):
   ```bash
   eas build --platform all  # Genera APK + IPA
   ```

2. **Subir a ambas tiendas:**
   - Google Play: 2-3 horas
   - Apple: Requiere Mac, 1-2 días

**COSTO TOTAL:** $124 primer año, $99 después

**TIEMPO ESTIMADO:** 1-2 semanas desde ahora a publicación

---

**¡ÉXITO CON YUIZZ! 🚀**
