# 🔧 YUIZZ Backend Setup - Quick Start

## Opción 1: Supabase Cloud (Recomendado - 5 minutos)

### 1. Crear cuenta Supabase
```bash
# Ir a https://app.supabase.com
# Sign up con Google o email
# Crear nuevo proyecto
```

### 2. Obtener credenciales
```bash
# En Settings → API
# Copiar:
# - Project URL → SUPABASE_URL
# - anon public key → SUPABASE_ANON_KEY
```

### 3. Crear BD
```bash
# En SQL Editor, pegar el contenido de supabase-schema.sql
# Ejecutar todas las queries
```

### 4. Configurar variables
```bash
# En el proyecto:
cp .env.example .env

# Editar .env con tus credenciales de Supabase
nano .env
```

### 5. Instalar dependencias
```bash
npm install
```

### 6. Iniciar server
```bash
npm start
# O en desarrollo:
npm run dev
```

Servidor corriendo en: **http://localhost:3001**

---

## Opción 2: Supabase Local (Docker - Desarrollo)

### 1. Instalar Docker
```bash
# macOS/Windows:
brew install docker-desktop  # macOS
# o descargar desde docker.com

# Linux:
sudo apt-get install docker.io
```

### 2. Iniciar Supabase local
```bash
# Instalar supabase CLI
npm install -g supabase

# En el proyecto
supabase start

# Verá credencales como:
# API URL: http://127.0.0.1:54321
# Anon Key: eyJhbGci...
```

### 3. Crear BD
```bash
# En el dashboard local (http://127.0.0.1:54323)
# Ir a SQL Editor
# Pegar supabase-schema.sql
# Ejecutar
```

### 4. Actualizar .env
```bash
SUPABASE_URL=http://127.0.0.1:54321
SUPABASE_ANON_KEY=eyJhbGci...
```

### 5. Instalar y correr
```bash
npm install
npm start
```

---

## Probar API

### Health Check
```bash
curl http://localhost:3001/health
# Response: { "status": "API running ✅" }
```

### Registrar usuario
```bash
curl -X POST http://localhost:3001/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123",
    "username": "testuser",
    "firstName": "Test",
    "lastName": "User"
  }'
```

### Login
```bash
curl -X POST http://localhost:3001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123"
  }'
```

Copiar el `token` del response.

### Obtener perfil (con token)
```bash
curl -X GET http://localhost:3001/api/users/profile \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

---

## Endpoints Disponibles

### Auth
- `POST /api/auth/register` - Registrar usuario
- `POST /api/auth/login` - Login

### Profiles
- `GET /api/users/profile` - Mi perfil
- `PUT /api/users/profile` - Editar perfil
- `GET /api/discover` - Perfiles para swipe

### Interactions
- `POST /api/interactions/like` - Like
- `POST /api/interactions/pass` - Pass
- `POST /api/interactions/super-like` - Super Like

### Messages
- `GET /api/messages/chats` - Mis chats
- `POST /api/messages/send` - Enviar mensaje

### Economy
- `GET /api/coins` - Ver monedas
- `POST /api/coins/purchase` - Comprar monedas
- `POST /api/streaks/claim` - Reclamar recompensa diaria

---

## Próximos pasos

1. ✅ Backend funcionando
2. ⬜ Conectar frontend al API
3. ⬜ Implementar WebSocket para chat realtime
4. ⬜ Integrar Stripe para pagos
5. ⬜ Desplegar a producción

