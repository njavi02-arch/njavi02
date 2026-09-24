# 🚀 CÓMO LEVANTAR YUIZZ - GUÍA COMPLETA

**Status:** ✅ Listo para usar  
**Tiempo total setup:** 15-20 minutos  
**Requisitos:** Node.js 18+, Python 3

---

## 📋 PASO 0: PREPARAR SUPABASE (5 min)

### Opción A: Supabase Cloud (Recomendado)

#### 1. Crear cuenta
```bash
# Ir a https://app.supabase.com
# Sign up con Google o email
# Crear proyecto nuevo
```

#### 2. Configurar BD
```bash
# En Supabase Dashboard:
# 1. Ir a SQL Editor
# 2. Pegar contenido de supabase-schema.sql
# 3. Ejecutar todas las queries
# Esperar 1-2 minutos
```

#### 3. Obtener credenciales
```bash
# En Settings → API
# Copiar:
# - Project URL → SUPABASE_URL
# - anon public key → SUPABASE_ANON_KEY
```

### Opción B: Supabase Local (Docker)

```bash
# Instalar supabase CLI
npm install -g supabase

# En proyecto
supabase start

# Esperar 2-3 minutos
# Ver output: API URL, Anon Key, etc.
```

---

## 🔧 PASO 1: CONFIGURAR BACKEND (3 min)

### 1.1 Crear archivo .env

```bash
cd /home/user/njavi02

# Copiar template
cp .env.example .env

# Editar .env con tus credenciales
nano .env
```

Contenido .env:
```
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_ANON_KEY=eyJhbGc...
JWT_SECRET=your-secret-key-change-in-production
PORT=3001
NODE_ENV=development
```

### 1.2 Instalar dependencias

```bash
npm install
```

### 1.3 Iniciar servidor

```bash
npm start

# Deberías ver:
# ╔═══════════════════════════════════════╗
# ║   🚀 YUIZZ API BACKEND RUNNING      ║
# ╚═══════════════════════════════════════╝
# 📍 Server: http://localhost:3001
```

✅ Backend listo

---

## 🌐 PASO 2: SERVIR FRONTEND (2 min)

### En otra terminal:

```bash
cd /home/user/njavi02

# Iniciar servidor HTTP
python3 -m http.server 8080

# Deberías ver:
# Serving HTTP on 0.0.0.0 port 8080
```

✅ Frontend listo

---

## 📱 PASO 3: ABRIR APP (1 min)

### En navegador:

```
http://localhost:8080/volta-pro-v2.html
```

Deberías ver:
```
╔════════════════════════════╗
║       YUIZZ                ║
║  Conexiones Reales         ║
╠════════════════════════════╣
║  Email:     [input]        ║
║  Password:  [input]        ║
║  [Iniciar Sesión]          ║
║  Crear Cuenta Nueva        ║
╚════════════════════════════╝
```

✅ App abierta

---

## 👤 PASO 4: CREAR CUENTA DE PRUEBA (2 min)

### 4.1 Registro

```
1. Click "Crear Cuenta Nueva"
2. Llenar formulario:
   - Username:  testuser
   - Email:     test@example.com
   - Password:  password123
   - Nombre:    Test
   - Apellido:  User
3. Click "Crear Cuenta"
```

Resultado esperado:
```
✅ "¡Cuenta creada!"
✅ Redirige a pantalla principal
✅ Automático login
```

### 4.2 Verificar en BD

```bash
# En Supabase Dashboard → SQL Editor:
SELECT * FROM auth.users;
SELECT * FROM profiles;
SELECT * FROM user_coins;
SELECT * FROM daily_streaks;

# Deberías ver tu usuario creado ✅
```

---

## 🧪 PASO 5: TESTEAR FUNCIONALIDADES

### DISCOVER (Swiping)

```
1. En app: verás pantalla "Descubrir"
2. Verás profile card (📷 Test)
3. Click ❤️ (Like):
   - Deberías ver ✅
   - En BD: nuevo registro en "interactions" table
4. Click ⭐ (SuperLike):
   - Deberías ver -10 monedas
   - En BD: coins decrementadas, activity_log registrado
```

### PROFILE (Monedas & Racha)

```
1. Click "Perfil" tab
2. Ver:
   - 🔥 Racha: Día 1 (primera vez)
   - 💰 Monedas: 50 (inicial)
   - 👁️ Visualizaciones: 0
3. Click 🎁 (Claim Reward):
   - ✅ +50 monedas (día 1)
   - ✅ Racha actualizada
   - (Solo 1x al día)
```

### MESSAGES (Chat)

```
1. Click "Mensajes" tab
2. Ver chats (vacío si no hay matches)
3. (Funcionalidad completa = FASE 3)
```

---

## 🔍 VERIFICAR DESDE TERMINAL

### Check API Health

```bash
curl http://localhost:3001/health

# Response:
# {"status":"API running ✅"}
```

### Test Register Endpoint

```bash
curl -X POST http://localhost:3001/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "cli@example.com",
    "password": "password123",
    "username": "cliuser",
    "firstName": "CLI",
    "lastName": "User"
  }'

# Response:
# {
#   "message": "User created successfully",
#   "userId": "uuid-...",
#   "token": "eyJhbGc...",
#   "user": { "id": "...", "email": "...", "username": "..." }
# }
```

### Test Login Endpoint

```bash
curl -X POST http://localhost:3001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123"
  }'

# Response:
# {
#   "token": "eyJhbGc...",
#   "userId": "uuid-...",
#   "email": "test@example.com"
# }
```

### Test Protected Endpoint

```bash
TOKEN="eyJhbGc..." # Copiar token del login
curl -X GET http://localhost:3001/api/users/profile \
  -H "Authorization: Bearer $TOKEN"

# Response: Tu perfil completo
```

---

## ⚠️ TROUBLESHOOTING

### Error: "Failed to fetch" al registrar

```
❌ Problema: Backend no está corriendo
✅ Solución:
   1. Abre otra terminal
   2. cd /home/user/njavi02
   3. npm start
   4. Esperar "API running ✅"
```

### Error: "SUPABASE_URL not configured"

```
❌ Problema: .env sin credenciales
✅ Solución:
   1. Verificar .env existe
   2. Tiene SUPABASE_URL y SUPABASE_ANON_KEY
   3. npm start de nuevo
```

### Error: "404 Not Found" al abrir app

```
❌ Problema: Frontend server no está corriendo
✅ Solución:
   1. Abre otra terminal
   2. cd /home/user/njavi02
   3. python3 -m http.server 8080
   4. Abrir http://localhost:8080/volta-pro-v2.html
```

### Monedas no se restan con SuperLike

```
❌ Problema: SuperLike fallando silenciosamente
✅ Verificar:
   1. Abrir DevTools (F12)
   2. Console → Buscar errores
   3. Network → Ver respuesta del API
   4. Backend logs → Ver qué pasó
```

---

## 📊 ESTRUCTURA FINAL

```
Terminal 1 (Backend):
├─ npm start
├─ Listening on http://localhost:3001
└─ ✅ API running

Terminal 2 (Frontend):
├─ python3 -m http.server 8080
├─ Serving on http://localhost:8080
└─ ✅ Frontend ready

Browser:
├─ http://localhost:8080/volta-pro-v2.html
├─ Conecta a http://localhost:3001 (API)
├─ Conecta a Supabase (BD)
└─ ✅ App funcionando
```

---

## 🎯 CHECKLIST ANTES DE DECLARAR "LISTO"

- [ ] Backend running (npm start)
- [ ] Frontend serving (python3 -m http.server)
- [ ] App abierta en browser
- [ ] Puedo ver login screen
- [ ] Puedo registrar usuario
- [ ] Usuario aparece en BD (Supabase)
- [ ] Puedo hacer login
- [ ] Veo perfiles para swipe
- [ ] Like/Pass/SuperLike funciona
- [ ] Monedas se restan con SuperLike
- [ ] Racha diaria aparece
- [ ] Puedo claim reward

Si marcastes TODO ✅ = **YUIZZ está listo para producción**

---

## 🚀 PRÓXIMOS PASOS

### FASE 3: Chat Realtime
```bash
# WebSocket para mensajes en tiempo real
# Photo upload a Supabase Storage
# Typing indicators
# Read receipts
```

### FASE 4: Notificaciones
```bash
# Push notifications (Firebase Cloud Messaging)
# Email notifications
# In-app alerts
```

### FASE 5: Monetización
```bash
# Integración Stripe
# Premium subscription
# IAP para mensaje packages
```

### FASE 6: Producción
```bash
# Deploy a servidor real
# Custom domain
# SSL certificate
# CI/CD pipeline
# Monitoring & analytics
```

---

## 💡 TIPS PARA DESARROLLO

### Ver logs del backend

```bash
# En terminal del backend, verás en tiempo real:
POST /api/auth/login 200
POST /api/interactions/like 201
GET /api/discover 200
```

### Ver estado de BD

```bash
# Supabase Dashboard → Data Browser
# Click en cada tabla
# Ver datos en tiempo real
```

### Debugger en browser

```bash
# F12 → Console
# Ver errores de JavaScript
# Ver requests HTTP (Network tab)
```

### Resetear BD completa

```bash
# En Supabase SQL Editor:
DROP TABLE IF EXISTS notifications CASCADE;
DROP TABLE IF EXISTS coin_transactions CASCADE;
DROP TABLE IF EXISTS subscriptions CASCADE;
DROP TABLE IF EXISTS messages CASCADE;
DROP TABLE IF EXISTS activity_log CASCADE;
DROP TABLE IF EXISTS daily_streaks CASCADE;
DROP TABLE IF EXISTS user_coins CASCADE;
DROP TABLE IF EXISTS matches CASCADE;
DROP TABLE IF EXISTS interactions CASCADE;
DROP TABLE IF EXISTS preferences CASCADE;
DROP TABLE IF EXISTS profile_photos CASCADE;
DROP TABLE IF EXISTS profiles CASCADE;

# Luego: Pegar supabase-schema.sql y ejecutar
```

---

## 📞 SOPORTE

Si algo no funciona:

1. **Verificar backend está running**
   ```bash
   curl http://localhost:3001/health
   # Debe devolver: {"status":"API running ✅"}
   ```

2. **Verificar frontend accessible**
   ```bash
   curl http://localhost:8080/volta-pro-v2.html | head -20
   # Debe devolver HTML
   ```

3. **Verificar Supabase connected**
   - Ir a Supabase Dashboard
   - Verificar proyecto activo
   - Verificar credenciales en .env

4. **Abrir DevTools (F12)**
   - Console → Buscar errores rojo
   - Network → Ver requests/responses
   - Application → localStorage & cookies

---

**¿Listo para rockear? 🚀 YUIZZ está en vivo!**

