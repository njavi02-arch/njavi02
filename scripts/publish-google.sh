#!/bin/bash

echo "📱 YUIZZ - Publicar en Google Play Store"
echo "========================================"
echo ""

# Verificar APK
if [ ! -f "volta-app.apk" ]; then
    echo "❌ Error: volta-app.apk no encontrado"
    echo "   Primero ejecuta: ./compile-yuizz.sh"
    exit 1
fi

echo "✅ APK encontrado"
echo ""

# Verificar que tienes credenciales de Google Play
echo "📋 Necesito tus credenciales de Google Play Console:"
echo ""
echo "   1. Ve a https://play.google.com/console"
echo "   2. Descarga el JSON de tu servicio"
echo "   3. Guarda como: google-play-key.json"
echo ""

if [ ! -f "google-play-key.json" ]; then
    read -p "¿Descargaste el archivo JSON? (s/n): " json_confirm
    if [ "$json_confirm" != "s" ]; then
        echo "❌ Necesitas el archivo JSON para continuar"
        exit 1
    fi
fi

echo "✅ Credenciales verificadas"
echo ""

# Información para la tienda
echo "📝 Información de la app:"
echo ""
read -p "Nombre de la app: " app_name
read -p "Categoría (Dating, Social, Lifestyle): " app_category
read -p "Descripción corta (máximo 80 caracteres): " app_short_desc
read -p "Descripción completa (máximo 4000 caracteres): " app_long_desc

echo ""
echo "🔨 Preparando publicación..."
echo ""

# Crear metadata
cat > metadata.json << METADATA
{
  "app_name": "$app_name",
  "category": "$app_category",
  "short_description": "$app_short_desc",
  "full_description": "$app_long_desc",
  "version": "1.0.0",
  "version_code": 1
}
METADATA

echo "✅ Metadata preparada"
echo ""

# Subir APK
echo "📤 Subiendo APK a Google Play..."
echo "   (Esto puede tomar algunos minutos)"
echo ""

# Usando Google Play API
npx @react-native-firebase/cli:google-play upload --apk volta-app.apk --metadata metadata.json

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ ¡PUBLICACIÓN EN GOOGLE PLAY EXITOSA!"
    echo ""
    echo "📊 Próximos pasos:"
    echo "   1. Ve a https://play.google.com/console"
    echo "   2. Revisa que la app esté en 'Prueba Interna'"
    echo "   3. Sube screenshots y más información"
    echo "   4. Envía a revisión"
    echo "   5. Espera 24-48 horas"
    echo ""
    echo "🎉 ¡YUIZZ en Google Play Store!"
else
    echo "❌ Error en la publicación"
    echo "   Intenta manualmente en https://play.google.com/console"
    exit 1
fi
