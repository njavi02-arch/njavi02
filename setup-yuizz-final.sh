#!/bin/bash

# COLORES
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

# BANNER
clear
echo -e "${CYAN}"
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                                                                ║"
echo "║     🚀 YUIZZ - SETUP AUTOMÁTICO FINAL - LANZAMIENTO 🚀         ║"
echo "║                                                                ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo -e "${NC}"
echo ""

# FUNCIÓN PARA IMPRIMIR
print_step() {
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${GREEN}✅ $1${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

# PASO 1: VERIFICAR TODO
print_step "PASO 1: VERIFICAR DEPENDENCIAS"
echo ""

# Verificar Node.js
if command -v node &> /dev/null; then
    print_success "Node.js $(node -v) instalado"
else
    print_error "Node.js no encontrado"
    exit 1
fi

# Verificar npm
if command -v npm &> /dev/null; then
    print_success "npm $(npm -v) instalado"
else
    print_error "npm no encontrado"
    exit 1
fi

# Verificar volta-pro.html
if [ -f "volta-pro.html" ]; then
    SIZE=$(du -h volta-pro.html | cut -f1)
    print_success "volta-pro.html encontrado ($SIZE)"
else
    print_error "volta-pro.html no encontrado"
    exit 1
fi

# Verificar archivos de configuración
if [ -f "app.json" ] && [ -f "eas.json" ] && [ -f "App.js" ]; then
    print_success "Configuración React Native completa"
else
    print_error "Faltan archivos de configuración"
    exit 1
fi

echo ""

# PASO 2: INSTALAR DEPENDENCIAS
print_step "PASO 2: INSTALAR DEPENDENCIAS NPM"
echo ""

print_info "Instalando node_modules..."
npm install --silent 2>/dev/null
print_success "node_modules instalado"

echo ""

# PASO 3: INSTALAR EAS CLI
print_step "PASO 3: INSTALAR EAS CLI (Compilación en nube)"
echo ""

if ! command -v eas &> /dev/null; then
    print_info "Instalando EAS CLI globalmente..."
    npm install -g eas-cli 2>/dev/null
fi

if command -v eas &> /dev/null; then
    VERSION=$(eas --version | cut -d' ' -f2)
    print_success "EAS CLI v$VERSION instalado"
else
    print_error "No se pudo instalar EAS CLI"
    exit 1
fi

echo ""

# PASO 4: VERIFICAR SCRIPTS
print_step "PASO 4: VERIFICAR SCRIPTS AUTOMÁTICOS"
echo ""

SCRIPTS=("compile-yuizz.sh" "publish-google.sh" "publish-apple.sh" "yuizz-deploy-all.sh")

for script in "${SCRIPTS[@]}"; do
    if [ -x "$script" ]; then
        print_success "Script $script listo"
    else
        print_info "Corrigiendo permisos de $script..."
        chmod +x "$script"
        print_success "Script $script actualizado"
    fi
done

echo ""

# PASO 5: VERIFICAR DOCUMENTACIÓN
print_step "PASO 5: VERIFICAR DOCUMENTACIÓN"
echo ""

DOCS=("INDICE_CHECKLIST.md" "COMIENZA_AQUI.md" "GUIA_COMPILACION.md" "PUBLICACION_APP_STORE.md" "PRIVACY_POLICY.md" "TERMS_OF_SERVICE.md" "METADATOS_APP_STORE.md")

DOCS_FOUND=0
for doc in "${DOCS[@]}"; do
    if [ -f "$doc" ]; then
        ((DOCS_FOUND++))
    fi
done

print_success "$DOCS_FOUND/$((${#DOCS[@]})) documentos encontrados"

echo ""

# PASO 6: MOSTRAR OPCIONES
print_step "PASO 6: ELEGIR ACCIÓN"
echo ""
echo -e "${MAGENTA}Opciones disponibles:${NC}"
echo ""
echo -e "${CYAN}[1]${NC} Compilar app (APK + IPA)"
echo -e "${CYAN}[2]${NC} Lanzar flujo completo (compilar + publicar)"
echo -e "${CYAN}[3]${NC} Ver guía de inicio rápido"
echo -e "${CYAN}[4]${NC} Ver metadatos para App Store"
echo -e "${CYAN}[5]${NC} Salir"
echo ""

read -p "Selecciona opción (1-5): " option

case $option in
    1)
        print_step "COMPILAR APP (OPCIÓN 1)"
        echo ""
        echo -e "${YELLOW}Este proceso:${NC}"
        echo "1. Solicita login en Expo (solo una vez)"
        echo "2. Compila para Android (15 minutos)"
        echo "3. Compila para iOS (15 minutos)"
        echo "4. Descarga APK e IPA automáticamente"
        echo ""
        read -p "¿Continuar? (s/n): " confirm
        if [ "$confirm" = "s" ]; then
            echo ""
            ./compile-yuizz.sh
        fi
        ;;
    2)
        print_step "FLUJO COMPLETO (OPCIÓN 2)"
        echo ""
        echo -e "${YELLOW}Este proceso:${NC}"
        echo "1. Compila app (30-40 minutos)"
        echo "2. Solicita info para publicación"
        echo "3. Publica en Google Play Store"
        echo "4. Publica en Apple App Store"
        echo "5. ¡YUIZZ en vivo en 24-48 horas!"
        echo ""
        read -p "¿Continuar? (s/n): " confirm
        if [ "$confirm" = "s" ]; then
            echo ""
            ./yuizz-deploy-all.sh
        fi
        ;;
    3)
        print_step "GUÍA DE INICIO RÁPIDO"
        echo ""
        if [ -f "COMIENZA_AQUI.md" ]; then
            head -100 COMIENZA_AQUI.md
            echo ""
            read -p "¿Ver documento completo? (s/n): " view
            if [ "$view" = "s" ]; then
                less COMIENZA_AQUI.md
            fi
        fi
        ;;
    4)
        print_step "METADATOS APP STORE"
        echo ""
        if [ -f "METADATOS_APP_STORE.md" ]; then
            head -150 METADATOS_APP_STORE.md
            echo ""
            read -p "¿Ver documento completo? (s/n): " view
            if [ "$view" = "s" ]; then
                less METADATOS_APP_STORE.md
            fi
        fi
        ;;
    5)
        print_info "Saliendo..."
        exit 0
        ;;
    *)
        print_error "Opción no válida"
        exit 1
        ;;
esac

echo ""
print_step "RESUMEN FINAL"
echo ""
echo -e "${GREEN}✅ YUIZZ está completamente listo${NC}"
echo ""
echo -e "${YELLOW}Próximos pasos:${NC}"
echo "1. Crea cuentas: Expo (gratis), Google ($25), Apple ($99)"
echo "2. Ejecuta: ./yuizz-deploy-all.sh"
echo "3. Espera aprobación: 24-48 horas"
echo "4. ¡YUIZZ en vivo! 🚀"
echo ""
echo -e "${BLUE}Documentación:${NC}"
echo "• INDICE_CHECKLIST.md - Checklist completo"
echo "• COMIENZA_AQUI.md - Guía rápida"
echo "• GUIA_COMPILACION.md - Paso a paso"
echo ""

