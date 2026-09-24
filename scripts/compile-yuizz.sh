#!/bin/bash

echo "🚀 YUIZZ - Script de Compilación Automática"
echo "=========================================="
echo ""

# Verificar que estamos en el directorio correcto
if [ ! -f "volta-pro.html" ]; then
    echo "❌ Error: volta-pro.html no encontrado"
    exit 1
fi

echo "✅ Archivos YUIZZ detectados"
echo ""

# Paso 1: Verificar Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js no está instalado"
    exit 1
fi
echo "✅ Node.js v$(node -v) instalado"

# Paso 2: Instalar dependencias
echo ""
echo "📦 Instalando dependencias..."
npm install --silent

# Paso 3: Verificar EAS CLI
if ! command -v eas &> /dev/null; then
    echo "❌ EAS CLI no está instalado"
    exit 1
fi
echo "✅ EAS CLI v$(eas --version) instalado"

# Paso 4: Login (interactivo)
echo ""
echo "🔐 Necesito tu cuenta de Expo para compilar"
echo "   (Ve a https://expo.dev para crear una cuenta gratis si no tienes)"
echo ""
read -p "¿Continuar con login? (s/n): " login_confirm

if [ "$login_confirm" != "s" ]; then
    echo "❌ Compilación cancelada"
    exit 1
fi

echo ""
echo "Ingresa tus credenciales de Expo:"
eas login

# Verificar login
if [ $? -ne 0 ]; then
    echo "❌ Login fallido"
    exit 1
fi

echo "✅ Login exitoso"

# Paso 5: Compilar
echo ""
echo "🔨 Compilando YUIZZ para Android e iOS..."
echo "   (Esto puede tomar 15-20 minutos)"
echo ""

eas build --platform all --type preview

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ ¡COMPILACIÓN EXITOSA!"
    echo ""
    echo "📲 Tus archivos compilados:"
    echo "   - APK (Android): Descargado automáticamente"
    echo "   - IPA (iOS): Descargado automáticamente"
    echo ""
    echo "📖 Próximos pasos:"
    echo "   1. Leer: PUBLICACION_APP_STORE.md"
    echo "   2. Crear Google Developer Account: $25"
    echo "   3. Crear Apple Developer Account: $99/año"
    echo "   4. Subir APK a Google Play"
    echo "   5. Subir IPA a Apple App Store"
    echo ""
    echo "¡Éxito! 🎉"
else
    echo "❌ Compilación fallida"
    exit 1
fi
