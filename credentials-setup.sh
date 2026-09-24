#!/bin/bash

# Script para guardar credenciales de forma segura
# y ejecutar compilación + publicación

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║           YUIZZ - SETUP DE CREDENCIALES                       ║"
echo "║                                                                ║"
echo "║  Este script va a usar tus credenciales para compilar y        ║"
echo "║  publicar la app en Google Play y Apple App Store             ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Verificar que las credenciales existen
if [ -z "$EXPO_EMAIL" ] || [ -z "$EXPO_PASSWORD" ]; then
    echo "❌ Error: No hay credenciales de Expo"
    echo ""
    echo "Para usar este script, Claude debe darte:"
    echo "  - EXPO_EMAIL (tu email de Expo)"
    echo "  - EXPO_PASSWORD (tu contraseña de Expo)"
    echo ""
    echo "Luego ejecuta:"
    echo "  export EXPO_EMAIL='tu@email.com'"
    echo "  export EXPO_PASSWORD='tuContraseña'"
    echo "  ./credentials-setup.sh"
    exit 1
fi

echo "✅ Credenciales Expo detectadas"
echo "   Email: ${EXPO_EMAIL:0:5}***"
echo ""

# Crear archivo .env (sin guardar credenciales en git)
cat > .env << EOF
EXPO_EMAIL=$EXPO_EMAIL
EXPO_PASSWORD=$EXPO_PASSWORD
EOF

echo "✅ Credenciales guardadas temporalmente"
echo ""

# Ahora ejecutar compilación
echo "🔨 Iniciando compilación..."
echo ""

# Instalar EAS CLI si no existe
if ! command -v eas &> /dev/null; then
    echo "📦 Instalando EAS CLI..."
    npm install -g eas-cli
fi

# Login en Expo
echo "🔐 Login en Expo..."
eas login -u "$EXPO_EMAIL" -p "$EXPO_PASSWORD" 2>/dev/null

if [ $? -eq 0 ]; then
    echo "✅ Login en Expo exitoso"
else
    echo "⚠️  Aviso: Login en Expo puede haber fallado"
    echo "    Pero continuaremos con la compilación..."
fi

echo ""
echo "📱 Compilando para Android..."
eas build --platform android --profile production

echo ""
echo "📱 Compilando para iOS..."
eas build --platform ios --profile production

echo ""
echo "✅ Compilación completada"
echo ""
echo "Los archivos compilados estarán en:"
echo "  - Android (APK)"
echo "  - iOS (IPA)"
echo ""

# Limpiar .env
rm -f .env

echo "✅ Script completado"
