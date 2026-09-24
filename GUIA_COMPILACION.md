# 🚀 GUÍA RÁPIDA: Compilar YUIZZ a App Nativa

## ⚡ OPCIÓN MÁS FÁCIL: Usar Expo EAS (Recomendado)

### Paso 1: Instalar Herramientas
```bash
# Instalar Node.js si no lo tienes
# https://nodejs.org (versión 18+)

# Instalar Expo CLI
npm install -g eas-cli expo-cli

# Verificar instalación
eas --version
expo --version
```

### Paso 2: Crear Proyecto Expo
```bash
# Crear proyecto
expo init yuizz-app --template blank

# O clonar y copiar archivos
cd /path/to/yuizz-app
npm install
```

### Paso 3: Copiar Archivos YUIZZ
```bash
# Copiar estos archivos a tu carpeta del proyecto:
- volta-pro.html → proyecto/
- package.json → proyecto/
- app.json → proyecto/
- eas.json → proyecto/
- App.js → proyecto/

# Instalar dependencias
npm install
```

### Paso 4: Configurar Expo Account
```bash
# Crear cuenta gratis en https://expo.dev
# Luego loguearse:
eas login

# Ingresa tu email
# Ingresa tu contraseña
# ✅ Listo!
```

### Paso 5: Compilar para Android (APK)

**OPCIÓN A: Compilar en la nube con Expo (RECOMENDADO)**
```bash
# Crear perfil de compilación
eas build --platform android

# Selecciona: release
# El servidor de Expo compila automaticamente

# Espera 10-15 minutos
# Descargas el APK automáticamente
```

**OPCIÓN B: Compilar localmente (Requiere Android Studio)**
```bash
# Instalar Android Studio
# https://developer.android.com/studio

# Configurar variables de entorno
export ANDROID_HOME=~/Library/Android/sdk  # Mac/Linux
set ANDROID_HOME=%USERPROFILE%\AppData\Local\Android\sdk  # Windows

# Compilar
eas build --platform android --local
```

### Paso 6: Compilar para iOS (IPA)

**OPCIÓN A: Compilar en la nube (RECOMENDADO)**
```bash
# Requiere Apple Developer Account ($99/año)
# https://developer.apple.com

eas build --platform ios

# Selecciona: release
# Espera 15-20 minutos
# Descargas el IPA automáticamente
```

**OPCIÓN B: Compilar localmente (Requiere Mac)**
```bash
# Solo funciona en Mac con Xcode

# Instalar Xcode (15GB)
xcode-select --install

# Compilar
eas build --platform ios --local
```

---

## 📦 COMPILAR AMBAS PLATAFORMAS A LA VEZ

```bash
# Compilar Android + iOS simultáneamente
eas build --platform all

# O compilar preview para testing
eas build --platform all --type preview
```

---

## 📱 SUBIR A GOOGLE PLAY STORE

### Requisitos:
- Google Developer Account ($25)
- APK compilado

### Pasos:
```bash
# 1. Ir a Google Play Console
# https://play.google.com/console

# 2. Crear app
# Nombre: YUIZZ
# Categoría: Dating

# 3. Subir APK en Testing Internal
# Internal Testing → Create new release → Upload APK

# 4. Revisar metadatos (descripción, screenshots, etc)

# 5. Enviar a producción
# Production → Create new release → Subir APK → Enviar
```

---

## 🍎 SUBIR A APPLE APP STORE

### Requisitos:
- Apple Developer Account ($99/año)
- Mac con Xcode
- IPA compilado

### Pasos:
```bash
# 1. Ir a App Store Connect
# https://appstoreconnect.apple.com

# 2. Crear app
# Nombre: YUIZZ
# Bundle ID: com.yuizz.app (debe coincidir con app.json)

# 3. Configurar credenciales en eas.json
# {
#   "submit": {
#     "production": {
#       "ios": {
#         "appleId": "tu@email.com",
#         "appleTeamId": "XXXXXXXXXX",
#         "appleAppSpecificPassword": "xxxx-xxxx-xxxx-xxxx"
#       }
#     }
#   }
# }

# 4. Subir IPA con Expo (automático)
eas submit --platform ios --latest

# O manualmente en Transporter (app de Mac)
```

---

## 🔧 SOLUCIONAR PROBLEMAS

### "APK o IPA no compilan"

**Error: Android SDK not found**
```bash
# Descargar Android SDK
# https://developer.android.com/studio

# Configurar path
export ANDROID_SDK_ROOT=$HOME/Library/Android/sdk
export PATH=$PATH:$ANDROID_SDK_ROOT/platform-tools
```

**Error: Xcode not found (macOS)**
```bash
# Instalar Xcode completo
xcode-select --install
sudo xcode-select --switch /Applications/Xcode.app/Contents/Developer
```

### "App compila pero no muestra la interfaz"

**Problema:** WebView no carga el HTML

**Solución:**
```javascript
// En App.js, verificar que el source sea correcto
// Option 1: Cargar desde URL
source={{ uri: 'http://localhost:8899/volta-pro.html' }}

// Option 2: Cargar HTML inline
const htmlContent = `
  <!DOCTYPE html>
  <html>
  ...tu HTML aquí...
  </html>
`;
source={{ html: htmlContent }}
```

### "App se ve pequeña o rota en tablet"

```javascript
// En App.js
<WebView
  source={...}
  scalesPageToFit={true}
  allowsFullscreenVideo={true}
  style={{ flex: 1 }}
/>
```

### "Falta permiso de cámara/galería"

**En app.json:**
```json
{
  "expo": {
    "plugins": [
      [
        "expo-image-picker",
        {
          "photosPermission": "Acceso a fotos"
        }
      ]
    ]
  }
}
```

---

## ✅ CHECKLIST ANTES DE COMPILAR

### Código
- [ ] volta-pro.html sin errores
- [ ] App.js configurado correctamente
- [ ] package.json con dependencias correctas
- [ ] app.json con nombre y versión correcta

### Credenciales
- [ ] Expo account creado y configurado
- [ ] Google Developer Account ($25) si publicas Android
- [ ] Apple Developer Account ($99/año) si publicas iOS

### Metadatos (Para publicar)
- [ ] Screenshots 5+ (1080x1920 para Android, 1242x2208 para iOS)
- [ ] Icono 512x512px
- [ ] Descripción completa (máximo 4000 caracteres)
- [ ] Política de privacidad publicada
- [ ] Términos de servicio

---

## 📊 TIMELINE ESTIMADO

```
Día 1:
- Instalar herramientas (30 min)
- Crear proyecto (15 min)
- Copiar archivos YUIZZ (10 min)
- Configurar Expo account (10 min)
TOTAL: ~1 hora

Día 2:
- Compilar Android (15 min + esperar compilación: 15 min)
- Compilar iOS (15 min + esperar compilación: 20 min)
TOTAL: ~1.5 horas

Día 3:
- Subir a Google Play (1 hora)
- Subir a Apple Store (1 hora)
- Esperar aprobación (24-48 horas)
TOTAL: ~2 horas

TOTAL TIEMPO: 4.5 horas de trabajo + 24-48 horas de aprobación
```

---

## 💡 TIPS PRO

### 1. Probar en Android/iPhone antes de publicar
```bash
# Instalar Expo Go app en tu teléfono
# https://expo.dev/client

# Ejecutar en desarrollo
expo start

# Escanear QR con tu teléfono
# ¡App corre en tiempo real!
```

### 2. Agregar versión en app.json antes de cada publicación
```json
{
  "expo": {
    "version": "1.0.0",
    "ios": {
      "buildNumber": "1"
    },
    "android": {
      "versionCode": 1
    }
  }
}
```

### 3. Automatizar compilación con GitHub Actions
```yaml
# .github/workflows/build.yml
name: Build and Release
on:
  push:
    tags: ['v*']

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - run: npm ci
      - run: eas build --platform all --auto-submit
```

---

## 🎯 RESUMEN RÁPIDO

**Para compilar YUIZZ a app nativa:**

```bash
# 1. Instalar
npm install -g eas-cli

# 2. Crear proyecto Expo
expo init yuizz-app

# 3. Copiar archivos
# volta-pro.html, App.js, package.json, app.json, eas.json

# 4. Login
eas login

# 5. Compilar
eas build --platform all

# 6. Subir (después de compilar)
eas submit --platform all
```

**Costos:**
- Expo: GRATIS (compilación en nube)
- Google Play: $25 (único)
- Apple Store: $99/año

**¡LISTO PARA PUBLICAR! 🚀**
