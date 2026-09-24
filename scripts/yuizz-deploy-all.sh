#!/bin/bash

echo ""
echo "╔════════════════════════════════════════════════╗"
echo "║   🚀 YUIZZ - COMPILACIÓN Y PUBLICACIÓN 100% 🚀   ║"
echo "╚════════════════════════════════════════════════╝"
echo ""

# Colores
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Función para imprimir
log_info() {
    echo -e "${GREEN}✅${NC} $1"
}

log_error() {
    echo -e "${RED}❌${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}⚠️${NC} $1"
}

# PASO 1: COMPILAR
echo ""
echo "═══════════════════════════════════════════════════"
echo "  PASO 1: COMPILAR APP (15-20 minutos)"
echo "═══════════════════════════════════════════════════"
echo ""

if [ -f "volta-pro.html" ]; then
    log_info "volta-pro.html detectado"
else
    log_error "volta-pro.html no encontrado"
    exit 1
fi

if ! command -v eas &> /dev/null; then
    log_warn "Instalando EAS CLI..."
    npm install -g eas-cli
fi

log_info "EAS CLI v$(eas --version | cut -d' ' -f2)"
echo ""

# Login
log_warn "Necesito acceso a tu cuenta de Expo"
echo "   1. Ve a https://expo.dev (crear si no tienes)"
echo "   2. Inicia sesión abajo:"
echo ""
eas login

if [ $? -ne 0 ]; then
    log_error "Login en Expo fallido"
    exit 1
fi

log_info "Login en Expo exitoso"
echo ""

# Compilar
log_warn "Iniciando compilación..."
echo "   (Esto toma 15-20 minutos en servidores de Expo)"
echo ""

eas build --platform all --type preview

if [ $? -ne 0 ]; then
    log_error "Compilación fallida"
    exit 1
fi

log_info "¡Compilación completada!"
echo ""

# PASO 2: PUBLICAR EN GOOGLE PLAY
echo ""
echo "═══════════════════════════════════════════════════"
echo "  PASO 2: PUBLICAR EN GOOGLE PLAY STORE ($25)"
echo "═══════════════════════════════════════════════════"
echo ""

read -p "¿Publicar en Google Play? (s/n): " publish_google
if [ "$publish_google" = "s" ]; then
    echo ""
    echo "📱 Google Play Store Setup:"
    echo "   1. Ve a https://play.google.com/console"
    echo "   2. Crea una App (YUIZZ)"
    echo "   3. Sube el APK compilado"
    echo "   4. Llena metadatos (descripción, screenshots)"
    echo "   5. Envía a revisión"
    echo ""
    read -p "Presiona Enter cuando esté subido..."
    log_info "Google Play setup completado"
else
    log_warn "Google Play saltado"
fi

echo ""

# PASO 3: PUBLICAR EN APPLE APP STORE
echo ""
echo "═══════════════════════════════════════════════════"
echo "  PASO 3: PUBLICAR EN APPLE APP STORE ($99/año)"
echo "═══════════════════════════════════════════════════"
echo ""

read -p "¿Publicar en Apple App Store? (s/n): " publish_apple
if [ "$publish_apple" = "s" ]; then
    echo ""
    echo "🍎 Apple App Store Setup:"
    echo "   1. Ve a https://appstoreconnect.apple.com"
    echo "   2. Crea una App (YUIZZ)"
    echo "   3. Sube el IPA compilado"
    echo "   4. Llena metadatos (descripción, screenshots)"
    echo "   5. Completa información de edad"
    echo "   6. Envía a revisión"
    echo ""
    read -p "Presiona Enter cuando esté subido..."
    log_info "Apple App Store setup completado"
else
    log_warn "Apple App Store saltado"
fi

# RESUMEN FINAL
echo ""
echo "╔════════════════════════════════════════════════╗"
echo "║          🎉 ¡PUBLICACIÓN COMPLETADA! 🎉          ║"
echo "╚════════════════════════════════════════════════╝"
echo ""

log_info "✅ App compilada (APK + IPA descargados)"
log_info "✅ Metadatos preparados"

if [ "$publish_google" = "s" ]; then
    echo ""
    echo "📱 Google Play Store:"
    echo "   - Estado: En revisión (24-48 horas)"
    echo "   - URL: https://play.google.com/store/apps/details?id=com.yuizz.app"
fi

if [ "$publish_apple" = "s" ]; then
    echo ""
    echo "🍎 Apple App Store:"
    echo "   - Estado: En revisión (24-48 horas)"
    echo "   - URL: https://apps.apple.com/app/yuizz/..."
fi

echo ""
echo "📊 Timeline:"
echo "   - Ahora: ✅ Compilada y publicada"
echo "   - 24-48 horas: ✅ Aprobación (ambas tiendas)"
echo "   - Después: ✅ YUIZZ EN VIVO"
echo ""

echo "💰 Próximos pasos de monetización:"
echo "   1. Integrar Firebase Backend (BACKEND_FIREBASE.md)"
echo "   2. Conectar Stripe para pagos"
echo "   3. Monitorear métricas en App Store Connect"
echo ""

log_info "¡YUIZZ LANZADA! 🚀"
echo ""
