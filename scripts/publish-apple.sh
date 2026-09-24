#!/bin/bash

echo "🍎 YUIZZ - Publicar en Apple App Store"
echo "======================================"
echo ""

# Verificar IPA
if [ ! -f "volta-app.ipa" ]; then
    echo "❌ Error: volta-app.ipa no encontrado"
    echo "   Primero ejecuta: ./compile-yuizz.sh"
    exit 1
fi

echo "✅ IPA encontrado"
echo ""

# Verificar credenciales de Apple
echo "🔐 Necesito tus credenciales de Apple Developer:"
echo ""
echo "   1. Ve a https://appstoreconnect.apple.com"
echo "   2. Crea una App ID para YUIZZ"
echo "   3. Genera una App-Specific Password"
echo ""

read -p "Tu Apple ID: " apple_id
read -sp "Apple ID Password: " apple_password
echo ""
read -p "App-Specific Password: " app_password

echo ""
echo "✅ Credenciales ingresadas"
echo ""

# Información de la app
echo "📝 Información de la app:"
echo ""
read -p "Bundle ID (ej: com.yuizz.app): " bundle_id
read -p "Versión (ej: 1.0.0): " version
read -p "Build number (ej: 1): " build_number

echo ""
echo "🔨 Preparando publicación para Apple..."
echo ""

# Validar IPA
echo "📋 Validando IPA..."
xcrun altool --validate-app -f volta-app.ipa -t ios -u "$apple_id" -p "$app_password"

if [ $? -eq 0 ]; then
    echo "✅ Validación exitosa"
    echo ""
    
    # Subir IPA
    echo "📤 Subiendo IPA a App Store Connect..."
    xcrun altool --upload-app -f volta-app.ipa -t ios -u "$apple_id" -p "$app_password"
    
    if [ $? -eq 0 ]; then
        echo ""
        echo "✅ ¡PUBLICACIÓN EN APPLE APP STORE EXITOSA!"
        echo ""
        echo "📊 Próximos pasos:"
        echo "   1. Ve a https://appstoreconnect.apple.com"
        echo "   2. Revisa que la app esté en 'Preparar para envío'"
        echo "   3. Agrega screenshots y descripción"
        echo "   4. Completa información de edad"
        echo "   5. Envía a revisión"
        echo "   6. Espera 24-48 horas"
        echo ""
        echo "🎉 ¡YUIZZ en Apple App Store!"
    else
        echo "❌ Error al subir IPA"
        echo "   Intenta manualmente en https://appstoreconnect.apple.com"
        exit 1
    fi
else
    echo "❌ Validación fallida"
    echo "   Revisa que el IPA sea válido"
    exit 1
fi
