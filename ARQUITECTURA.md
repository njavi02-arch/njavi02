# 🏗️ YUIZZ - ARQUITECTURA DEL SISTEMA

## 📐 Diagrama General

```
┌─────────────────────────────────────────────────────────────────┐
│                        USUARIO (FRONTEND)                       │
├─────────────────────────────────────────────────────────────────┤
│  volta-pro.html (navegador) + api-client.js                    │
│  - UI de swiping, mensajes, perfil                             │
│  - localStorage para datos locales temporales                  │
│  - Llamadas HTTP al backend                                    │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         │ HTTP/REST
                         │
┌────────────────────────▼────────────────────────────────────────┐
│                    BACKEND API (Node.js)                         │
├─────────────────────────────────────────────────────────────────┤
│  server.js (Express)                                             │
│  - Autenticación (JWT)                                          │
│  - Endpoints CRUD (users, profiles, interactions, messages)    │
│  - Lógica de matching                                           │
│  - Validación & seguridad                                       │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         │ Query/Mutation
                         │
┌────────────────────────▼────────────────────────────────────────┐
│                    SUPABASE (Cloud)                              │
├─────────────────────────────────────────────────────────────────┤
│  PostgreSQL Database + Auth + Storage                           │
│  - auth.users (autenticación)                                  │
│  - public.profiles (perfiles de usuarios)                      │
│  - public.interactions (likes, passes, super likes)            │
│  - public.messages (chat)                                      │
│  - public.daily_streaks (gamificación)                         │
│  - public.user_coins (economía)                                │
│  - Row Level Security (privacidad)                             │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔄 Flow de Interacción

### 1️⃣ REGISTER (Nuevo usuario)

```
Frontend                 Backend              Supabase
   │                        │                      │
   ├─ Register ────────────>│                      │
   │  (email, password)     │                      │
   │                        ├─ Create Auth ──────>│
   │                        │                      │
   │                        │<─ User ID ───────────┤
   │                        │                      │
   │                        ├─ Create Profile ──>│
   │                        ├─ Create Coins ────>│
   │                        ├─ Create Streak ──>│
   │                        │                      │
   │<─ Token + UserID ──────┤                      │
   │  (salvar en localStorage)                     │
   │                        │                      │
```

### 2️⃣ DISCOVER (Ver perfiles)

```
Frontend                 Backend              Supabase
   │                        │                      │
   ├─ Get Profiles ───────>│                      │
   │  (con token)           │                      │
   │                        ├─ Query Profiles ──>│
   │                        │  (by distance,      │
   │                        │   preferences)      │
   │                        │                      │
   │                        │<─ Perfiles ────────┤
   │<─ Mostrar Swipe UI────┤                      │
   │                        │                      │
```

### 3️⃣ LIKE (Interacción)

```
Frontend                 Backend              Supabase
   │                        │                      │
   ├─ Like Profile ───────>│                      │
   │  (targetUserId)        │                      │
   │                        ├─ Insert Like ────>│
   │                        │                      │
   │                        ├─ Check Mutual ───>│
   │                        │                      │
   │                        │  SI MATCH:           │
   │                        ├─ Create Match ───>│
   │                        ├─ Notify User ────>│
   │                        │                      │
   │<─ Success / Match ─────┤                      │
   │                        │                      │
```

### 4️⃣ MESSAGE (Chat)

```
Frontend                 Backend              Supabase
   │                        │                      │
   ├─ Send Message ───────>│                      │
   │  (receiverId, content) │                      │
   │                        ├─ Insert Message ──>│
   │                        │                      │
   │                        ├─ Create Notif ───>│
   │                        │                      │
   │<─ Message Sent ────────┤                      │
   │                        │                      │
   │ (Receiver see msg)     │                      │
   │ (Future: WebSocket)    │                      │
   │                        │                      │
```

### 5️⃣ CLAIM REWARD (Racha diaria)

```
Frontend                 Backend              Supabase
   │                        │                      │
   ├─ Claim Reward ───────>│                      │
   │  (daily streak)        │                      │
   │                        ├─ Check Last Claim>│
   │                        │  (today?)            │
   │                        │                      │
   │                        │  SI es nuevo día:   │
   │                        ├─ +1 Streak ──────>│
   │                        ├─ +Coins ─────────>│
   │                        │  (rewards[])        │
   │                        │                      │
   │<─ Reward Claimed ──────┤                      │
   │                        │                      │
```

---

## 🗂️ Estructura de Carpetas

```
/home/user/njavi02/
│
├── volta-pro.html          ← Frontend (web app)
│   ├─ UI de swiping
│   ├─ Chat
│   ├─ Perfil
│   └─ localStorage (temporal)
│
├── server.js               ← Backend API (Node.js)
│   ├─ Routes (auth, profiles, interactions, messages)
│   ├─ Supabase client
│   └─ JWT middleware
│
├── api-client.js           ← Cliente JS para frontend
│   └─ Métodos de fetch
│
├── supabase-schema.sql     ← Schema de BD
│   ├─ Tables (profiles, messages, etc)
│   ├─ Indexes
│   └─ RLS policies
│
├── package-api.json        ← Dependencias backend
├── .env.example            ← Template de variables
│
├── BACKEND_SETUP.md        ← Setup instrucciones
├── ARQUITECTURA.md         ← Este archivo
│
└── [documentación]
    ├── ROADMAP_IMPLEMENTACION.md
    ├── ANALISIS_PRECIOS_PREMIUM.md
    └── PANTALLAS_GUIA_VISUAL.md
```

---

## 🔐 Seguridad

### Authentication
- ✅ JWT tokens (Bearer en headers)
- ✅ Tokens guardados en localStorage (frontend)
- ✅ Supabase Auth maneja haseo de passwords

### Database
- ✅ Row Level Security (RLS) en todas las tablas
- ✅ Usuarios solo ven sus propios datos sensibles
- ✅ Foreign keys para integridad referencial

### API
- ✅ Validación de input (express-validator)
- ✅ CORS habilitado
- ✅ Rate limiting (future)
- ✅ No SQL injection (Supabase parameterizado)

---

## 📊 Flujo de Datos

### Usuarios
```
Register → Create auth.users + profiles
   ↓
Login → JWT token
   ↓
Update profile → PUT /api/users/profile
   ↓
Get discover → GET /api/discover (perfiles recomendados)
```

### Gamificación
```
Like/Pass/SuperLike → INSERT interactions table
   ↓
Activity log → INSERT activity_log (tracking)
   ↓
Calculate rewards → Check daily_streaks
   ↓
Claim reward → Add coins + update streak
```

### Monetización
```
View premium → IN-APP
   ↓
Buy coins → POST /api/coins/purchase
   ↓
Stripe charge (future)
   ↓
Add coins to balance
```

---

## ⚡ Performance

### Índices de BD
```sql
idx_profiles_location        ← Búsqueda geoloc
idx_interactions_user        ← Historial likes
idx_messages_receiver        ← Chat persistente
idx_activity_user            ← Analytics
```

### Caché (future)
```
Redis → Perfiles populares
Redis → Top streaks
Redis → Coins balances
```

---

## 🚀 Escalabilidad

### Ahora (MVP)
- 1000 usuarios → 1 servidor
- Supabase free tier
- API simple REST

### Futuro (1M+ usuarios)
- API con caché Redis
- WebSocket para chat realtime
- Database sharding por región
- CDN para fotos
- Load balancer
- Kubernetes

---

## 📋 Checklist Estado

### FASE 1 ✅ COMPLETA
- [x] Esquema Supabase
- [x] Servidor Express
- [x] Endpoints auth
- [x] Endpoints profiles
- [x] Endpoints interactions
- [x] Endpoints messages
- [x] Cliente JS

### FASE 2 ⬜ EN PROGRESO
- [ ] Conectar frontend a API
- [ ] Eliminar localStorage (usar BD)
- [ ] WebSocket para chat realtime
- [ ] Actualizar UI de login
- [ ] Actualizar UI de swiping

### FASE 3 ⬜ PENDIENTE
- [ ] Integración Stripe
- [ ] Push notifications
- [ ] Admin panel
- [ ] Analytics
- [ ] Desplegar a producción

---

