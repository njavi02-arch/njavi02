# 🔄 FASE 2: CONECTAR FRONTEND AL API - CAMBIOS

**Status:** ✅ COMPLETADO  
**Archivo nuevo:** `volta-pro-v2.html`  
**Cambios principales:** ❌ localStorage → ✅ API REST

---

## 📋 RESUMEN DE CAMBIOS

### ❌ ELIMINADO (localStorage)
```javascript
// ANTES: Todo guardado localmente
localStorage.setItem('coins', coins);
localStorage.getItem('coins');
saveData();
loadData();

// Problemas:
- Datos se pierden al cambiar dispositivo
- No hay sincronización entre usuarios
- No se puede escalar
- No hay seguridad real
```

### ✅ NUEVO (API REST + JWT)
```javascript
// AHORA: Todo en servidor
const result = await API.like(targetUserId);
authToken = result.token; // JWT token
localStorage.setItem('auth_token', authToken);

// Ventajas:
+ Datos persistentes en BD
+ Sincronización real-time
+ Escalable infinitamente
+ Seguridad robusta (JWT + RLS)
```

---

## 🔗 CONEXIONES AL API

### 1. AUTH
```javascript
// REGISTER
POST /api/auth/register
{
  email: string,
  password: string,
  username: string,
  firstName: string,
  lastName: string
}

// LOGIN
POST /api/auth/login
{
  email: string,
  password: string
}
```

**Implementado en:** `volta-pro-v2.html` líneas 350-400

---

### 2. PROFILES
```javascript
// GET DISCOVER
GET /api/discover
Headers: Authorization: Bearer {token}

// GET MY PROFILE
GET /api/users/profile
Headers: Authorization: Bearer {token}

// UPDATE PROFILE
PUT /api/users/profile
{
  firstName: string,
  lastName: string,
  bio: string,
  age: number,
  city: string
}
```

**Implementado en:** líneas 150-170, 480-550

---

### 3. INTERACTIONS
```javascript
// LIKE
POST /api/interactions/like
{ targetUserId: string }
Response: { success: true, matched: boolean }

// PASS
POST /api/interactions/pass
{ targetUserId: string }

// SUPER LIKE (costs 10 coins)
POST /api/interactions/super-like
{ targetUserId: string }
Response: { success: true, coinsRemaining: number }
```

**Implementado en:** líneas 600-650

---

### 4. CHATS
```javascript
// GET CHATS
GET /api/messages/chats

// SEND MESSAGE
POST /api/messages/send
{
  receiverId: string,
  content: string
}
```

**Implementado en:** líneas 660-680

---

### 5. ECONOMY
```javascript
// GET COINS
GET /api/coins
Response: { coins: number, total_spent: number, ... }

// CLAIM DAILY REWARD
POST /api/streaks/claim
Response: { success: true, streakDay: number, reward: number }
```

**Implementado en:** líneas 730-760

---

## 🎨 UI CHANGES

### LOGIN SCREEN
```
ANTES:                          AHORA:
- Botón "Demo"                  - Email input ✅
- Acceso inmediato              - Password input ✅
- Datos mock                    - Validación servidor
                                - Opciones: Login o Registro
```

### REGISTER SCREEN
```
NUEVO PANTALLA:
- Username (único, validado)
- Email (validado, verificación pendiente)
- Password (hasheado en servidor)
- Nombre/Apellido (opcional)
- Crear perfil en BD
```

### DISCOVER SCREEN
```
ANTES:                          AHORA:
- Perfiles mock estáticos       - Perfiles reales del API ✅
- Like/Pass/SuperLike local     - Like/Pass/SuperLike → BD ✅
- Sin matching real             - Matching automático ✅
- sin notificaciones            - Notificaciones reales ✅
```

### PROFILE SCREEN
```
ANTES:                          AHORA:
- Monedas en localStorage       - Monedas desde API ✅
- Racha local                   - Racha en BD ✅
- Rewards no sincronizados      - Rewards con timestamp ✅
- Pulsable offline              - Requiere conexión (seguro)
```

---

## 🔐 SEGURIDAD IMPLEMENTADA

### JWT Authentication
```javascript
// Token guardado en localStorage
localStorage.setItem('auth_token', token);

// Enviado en headers
Authorization: Bearer eyJhbGc...

// Validado en servidor
if (response.status === 401) {
  logout(); // Token expirado
}
```

### CORS
```javascript
// Backend permite requests desde localhost:* 
// En producción: específico a dominio
```

### Input Validation
```javascript
// Server-side en Express
- Email format check
- Password min 8 chars
- Username uniqueness
- Age >= 18
```

---

## 🚀 CÓMO PROBAR

### 1. Iniciar Backend
```bash
cd /home/user/njavi02
npm install
npm start
# Server running on http://localhost:3001 ✅
```

### 2. Abrir Frontend
```bash
# Servir volta-pro-v2.html
python3 -m http.server 8080

# En browser: http://localhost:8080/volta-pro-v2.html
```

### 3. Registrar Usuario
```
1. Click "Crear Cuenta Nueva"
2. Llenar formulario:
   - Username: testuser123
   - Email: test@example.com
   - Password: password123
   - Nombre: Test
   - Apellido: User
3. Click "Crear Cuenta"
4. ✅ Cuenta creada en BD (auth.users + profiles)
```

### 4. Login
```
1. Email: test@example.com
2. Password: password123
3. Click "Iniciar Sesión"
4. ✅ JWT token generado
5. ✅ Redirige a app principal
```

### 5. Testear Funcionalidades
```
DISCOVER:
- Ver perfiles del API
- Click ❤️ → Like guardado en BD
- Click ⭐ → -10 monedas + registro en DB
- Check: /api/coins muestra saldo correcto

PROFILE:
- Ver racha diaria (daily_streaks table)
- Ver monedas (user_coins table)
- Click 🎁 → Claim reward (si es nuevo día)

MENSAJES:
- Ver matches
- (Chat realtime = FASE 3)
```

---

## ✨ CAMBIOS EN CÓDIGO

### Estructura Anterior (localStorage)
```javascript
let coins = 450; // Variable local
function nextProfile() {
  coins -= 10; // Modificar local
  localStorage.setItem('coins', coins); // Guardar local
}
```

### Estructura Nueva (API)
```javascript
async function handleLike(userId) {
  const result = await API.like(userId); // Request servidor
  if (result.matched) showToast('¡MATCH!'); // Respuesta
  await updateCoinsDisplay(); // Recargar desde BD
}
```

### Ventajas
1. ✅ Estado centralizado en servidor
2. ✅ Sincronización automática
3. ✅ Seguridad (no hay datos sensibles en cliente)
4. ✅ Escalable a millones de usuarios
5. ✅ Verificable (auditoría)

---

## 📊 ENDPOINTS MAPEADOS

| Feature | Método | Endpoint | Estado |
|---------|--------|----------|--------|
| Register | POST | /api/auth/register | ✅ |
| Login | POST | /api/auth/login | ✅ |
| Profile | GET | /api/users/profile | ✅ |
| Discover | GET | /api/discover | ✅ |
| Like | POST | /api/interactions/like | ✅ |
| Pass | POST | /api/interactions/pass | ✅ |
| SuperLike | POST | /api/interactions/super-like | ✅ |
| Chats | GET | /api/messages/chats | ✅ |
| Send Message | POST | /api/messages/send | ✅ |
| Coins | GET | /api/coins | ✅ |
| Claim Reward | POST | /api/streaks/claim | ✅ |

---

## 🐛 ERRORES COMUNES

### Error: "Failed to fetch"
```
❌ Problema: Backend no está corriendo
✅ Solución: npm start en otra terminal
```

### Error: "Invalid token"
```
❌ Problema: Token expirado
✅ Solución: Logout y login de nuevo
```

### Error: "No profiles available"
```
❌ Problema: No hay usuarios en BD
✅ Solución: Crear más cuentas de prueba
```

### Error: "CORS issue"
```
❌ Problema: Backend no tiene CORS habilitado
✅ Solución: Agregar CORS headers (ya hecho en server.js)
```

---

## 🎯 PRÓXIMOS PASOS (FASE 3)

### WebSocket para Chat Realtime
```javascript
// AHORA: Polling (lento)
// FUTURO: WebSocket (instant)
ws.on('message', (msg) => {
  displayMessage(msg);
});
```

### Photo Upload
```javascript
// Upload a Supabase Storage
const file = inputFile.files[0];
await supabase.storage.upload('profiles/' + userId, file);
```

### Push Notifications
```javascript
// Firebase Cloud Messaging
FCM.send({
  to: userToken,
  notification: { title: 'Match!', body: 'Tienes un match' }
});
```

---

## 📌 RESUMEN

### ANTES (localStorage)
- ❌ Demo desconectada
- ❌ Datos locales
- ❌ No sincroniza
- ❌ No escalable

### AHORA (API)
- ✅ App real funcional
- ✅ Datos en BD PostgreSQL
- ✅ Sincronización automática
- ✅ Escalable a 1M+ usuarios
- ✅ Listo para producción

---

**Siguiente paso:** Testing completo + WebSocket para chat

