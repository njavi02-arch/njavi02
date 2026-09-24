#!/bin/bash

echo "📦 Instalando scripts de despliegue YUIZZ..."
echo ""

# Crear directorio para scripts
mkdir -p scripts

# Copiar scripts
cp compile-yuizz.sh scripts/
cp publish-google.sh scripts/
cp publish-apple.sh scripts/
cp yuizz-deploy-all.sh scripts/

# Dar permisos
chmod +x scripts/*.sh

# Crear README en scripts
cat > scripts/README.md << 'README'
# 🚀 Scripts de Despliegue YUIZZ

Estos scripts automatizan la compilación y publicación de YUIZZ.

## Archivos

- `compile-yuizz.sh` - Compilar a APK + IPA
- `publish-google.sh` - Publicar en Google Play Store
- `publish-apple.sh` - Publicar en Apple App Store
- `yuizz-deploy-all.sh` - Hacer todo automáticamente

## Uso Rápido

```bash
# Opción 1: Compilar y publicar (todo automático)
./yuizz-deploy-all.sh

# Opción 2: Paso a paso
./compile-yuizz.sh
./publish-google.sh
./publish-apple.sh
```

## Requisitos

- Node.js 16+
- npm
- Cuenta de Expo (gratis)
- Cuenta de Google Developer ($25)
- Cuenta de Apple Developer ($99/año)

## Más info

Ver `../AUTOMATIZADO.md` para documentación completa.
README

echo "✅ Scripts instalados en /scripts/"
echo ""
echo "Archivos creados:"
ls -lh scripts/
echo ""
echo "✅ ¡Listo para usar!"
echo ""
echo "Ejecuta: ./scripts/yuizz-deploy-all.sh"
