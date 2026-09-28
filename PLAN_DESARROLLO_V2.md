# 🚀 YUIZZ V2 - PLAN DE DESARROLLO

**Objetivo:** MVP funcional en 4 semanas  
**Inicio:** 28 Septiembre 2026  
**Target Launch:** 26 Octubre 2026

---

## 📊 TIMELINE REALISTA

### SEMANA 1: Base + Auth + Perfiles
```
Lunes-Martes:
  ✓ Supabase schema v2 deployed
  ✓ JWT auth endpoints
  ✓ Age verification flow
  ✓ Perfil individual CRUD

Miércoles-Viernes:
  ✓ Perfil de pareja CRUD
  ✓ Profile photos upload
  ✓ Privacidad settings
  ✓ Testing auth
```

### SEMANA 2: Discovery + Interacciones
```
Lunes-Martes:
  ✓ Discovery endpoint (cercanos)
  ✓ Filtros avanzados
  ✓ Like/Pass/SuperLike logic
  ✓ Match detection

Miércoles-Viernes:
  ✓ Frontend discovery UI
  ✓ Cards swipe
  ✓ Buttons (pass/like/superlike)
  ✓ Filter UI
```

### SEMANA 3: Chat + Posts + Galerías
```
Lunes-Martes:
  ✓ Chat endpoints
  ✓ WebSocket realtime
  ✓ Message history
  ✓ Unread indicators

Miércoles:
  ✓ Posts CRUD
  ✓ Feed discovery
  ✓ Post engagement (likes, comments)

Jueves-Viernes:
  ✓ Private galleries
  ✓ Photo unlock system
  ✓ Gallery access requests
```

### SEMANA 4: Monetización + Deploy
```
Lunes-Martes:
  ✓ Coins system
  ✓ Stripe integration
  ✓ Premium subscription
  ✓ Boost system

Miércoles-Jueves:
  ✓ Admin dashboard
  ✓ Moderation tools
  ✓ Analytics
  ✓ Security audit

Viernes:
  ✓ Deploy staging
  ✓ Final testing
  ✓ Launch prep
```

---

## 🏗️ ARQUITECTURA TÉCNICA

### Backend (Node.js + Express)

**Estructura:**
```
src/
├─ routes/
│  ├─ auth.js (login, register, verify)
│  ├─ profiles.js (CRUD perfiles individuales)
│  ├─ couples.js (CRUD perfiles pareja)
│  ├─ discovery.js (descubrimiento, filtros)
│  ├─ interactions.js (like, pass, superlike)
│  ├─ matches.js (matches, chat, unread)
│  ├─ messages.js (chat API)
│  ├─ posts.js (publicaciones)
│  ├─ photos.js (subida fotos)
│  ├─ coins.js (economía)
│  ├─ subscriptions.js (premium)
│  ├─ blocks.js (bloqueos)
│  ├─ reports.js (reportes)
│  └─ admin.js (panel admin)
│
├─ middleware/
│  ├─ auth.js (JWT verification)
│  ├─ validation.js (request validation)
│  ├─ rateLimit.js (anti-abuse)
│  ├─ errorHandler.js
│  └─ logger.js
│
├─ services/
│  ├─ authService.js
│  ├─ profileService.js
│  ├─ discoveryService.js
│  ├─ matchService.js
│  ├─ coinService.js
│  └─ storageService.js
│
└─ server.js (main app)
```

### Frontend (React.js)

**Estructura:**
```
src/
├─ components/
│  ├─ Auth/
│  │  ├─ Login.jsx
│  │  ├─ Register.jsx
│  │  └─ AgeVerification.jsx
│  │
│  ├─ Onboarding/
│  │  ├─ ProfileSetup.jsx
│  │  ├─ PhotoUpload.jsx
│  │  └─ IntentionsSelect.jsx
│  │
│  ├─ Discovery/
│  │  ├─ DiscoveryCard.jsx
│  │  ├─ FilterPanel.jsx
│  │  └─ ProfileModal.jsx
│  │
│  ├─ Chat/
│  │  ├─ MatchesList.jsx
│  │  ├─ ChatWindow.jsx
│  │  └─ MessageInput.jsx
│  │
│  ├─ Profile/
│  │  ├─ MyProfile.jsx
│  │  ├─ ProfileEdit.jsx
│  │  └─ PhotoGallery.jsx
│  │
│  ├─ Posts/
│  │  ├─ PostFeed.jsx
│  │  ├─ CreatePost.jsx
│  │  └─ PostCard.jsx
│  │
│  ├─ Premium/
│  │  ├─ CoinsShop.jsx
│  │  ├─ SubscriptionPlans.jsx
│  │  └─ PaymentModal.jsx
│  │
│  └─ Common/
│     ├─ Navigation.jsx
│     ├─ Button.jsx
│     └─ Modal.jsx
│
├─ pages/
│  ├─ HomePage.jsx
│  ├─ DiscoveryPage.jsx
│  ├─ ChatPage.jsx
│  ├─ ProfilePage.jsx
│  └─ SettingsPage.jsx
│
├─ services/
│  ├─ apiClient.js
│  ├─ authService.js
│  └─ storageService.js
│
├─ styles/
│  ├─ theme.css
│  ├─ variables.css
│  └─ responsive.css
│
└─ App.jsx
```

---

## 🔧 ENDPOINTS CORE

### Auth
```
POST   /api/auth/register
POST   /api/auth/login
POST   /api/auth/verify-age
POST   /api/auth/logout
GET    /api/auth/me
```

### Profiles
```
GET    /api/profiles/:id
PUT    /api/profiles/:id
POST   /api/profiles/:id/photos
DELETE /api/profiles/:id/photos/:photoId
GET    /api/profiles/:id/photos
```

### Couples
```
POST   /api/couples
GET    /api/couples/:id
PUT    /api/couples/:id
POST   /api/couples/:id/invite
```

### Discovery
```
GET    /api/discovery?filters={...}
POST   /api/discovery/interactions/:targetId/like
POST   /api/discovery/interactions/:targetId/pass
POST   /api/discovery/interactions/:targetId/superlike
```

### Matches & Chat
```
GET    /api/matches
GET    /api/matches/:matchId/messages
POST   /api/matches/:matchId/messages
DELETE /api/messages/:messageId
GET    /api/matches/:matchId/unread
```

### Posts
```
GET    /api/posts?filter={...}
POST   /api/posts
PUT    /api/posts/:id
DELETE /api/posts/:id
POST   /api/posts/:id/like
```

### Coins & Premium
```
GET    /api/coins
POST   /api/coins/purchase
POST   /api/coins/spend/:reason
POST   /api/subscriptions/upgrade
GET    /api/subscriptions/current
```

---

## 📱 SCREENS MVP

### Autenticación (2 screens)
- [x] Login
- [x] Registro + Verificación edad
- [x] Onboarding (foto + intenciones)

### Discovery (2 screens)
- [ ] Cards discovery
- [ ] Filtros avanzados

### Chat (2 screens)
- [ ] Lista de matches
- [ ] Ventana de conversación

### Perfil (3 screens)
- [ ] Ver mi perfil
- [ ] Editar perfil
- [ ] Galería fotos

### Posts (2 screens)
- [ ] Feed de posts
- [ ] Crear post

### Premium (2 screens)
- [ ] Tienda de coins
- [ ] Planes de suscripción

### Settings (1 screen)
- [ ] Privacidad, bloqueos, reportes

---

## 🔐 SEGURIDAD - CHECKLIST

- [ ] Rate limiting (5 likes/min, etc.)
- [ ] CSRF tokens
- [ ] SQL injection protection
- [ ] XSS protection
- [ ] Age verification mandatory
- [ ] Email verification
- [ ] JWT secret strong
- [ ] HTTPS only
- [ ] CORS configured
- [ ] Password hashing (bcrypt)
- [ ] File upload validation
- [ ] API key rotation
- [ ] Sentry error tracking
- [ ] WAF rules (Cloudflare)

---

## 📊 MÉTRICAS A TRACKEAR

```
Daily:
  - Nuevos registros
  - Usuarios verificados %
  - Matches creados
  - Mensajes enviados
  - Activos (DAU)

Weekly:
  - Retención (D7)
  - Premium conversión
  - Coins gastados
  - Likes promedio/usuario
  - Chat rate

Monthly:
  - MRR (Monthly Recurring Revenue)
  - LTV (Lifetime Value)
  - CAC (Customer Acquisition Cost)
  - Churn rate
  - User satisfaction
```

---

## 🎯 CRITERIOS DE ÉXITO MVP

✅ **Funcionales:**
- Auth + verificación edad 18+
- Perfiles individuales y pareja
- Discovery con 100+ usuarios
- Chat funcional
- Coins + Premium basic
- Posts/anuncios

✅ **Seguridad:**
- RLS implementado
- Age verification strict
- Bloqueos y reportes
- Moderación basic

✅ **UX:**
- Mobile-responsive
- <2s load times
- Offline resilience (PWA)
- Notificaciones push basic

✅ **Monetización:**
- Stripe integration
- Coins purchasing
- Premium subscription
- Analytics dashboard

---

## ⚠️ RIESGOS Y MITIGACIONES

| Riesgo | Impacto | Mitigación |
|--------|---------|-----------|
| Spam/fake users | Alto | Verificación fuerte + moderación |
| Abuse sexual | Crítico | Reportes + AI moderation + ban |
| Data breach | Crítico | Encryption + RLS + audits |
| Churn alto | Medio | Gamificación + notifications |
| Competencia | Bajo | Pricing + community + features |
| Escalabilidad | Medio | Índices DB + cache + CDN |

---

## 💡 DIFERENCIADORES CLAVE

vs Pure:
- ✅ 30% precio más barato
- ✅ Diseño más moderno
- ✅ Perfiles pareja mejor UX
- ✅ Posts mejorados

vs Wizz:
- ✅ Mejor para adultos orientados
- ✅ Fotos privadas sistema
- ✅ Intenciones más claras
- ✅ Premium con valor

vs Connected2.me:
- ✅ Más moderna
- ✅ Mejor móvil experience
- ✅ Más opciones (no solo parejas)
- ✅ Precios competitivos

---

## 🚀 GO-TO-MARKET

### Pre-Launch (Semana 4)
- Closed beta (100 usuarios reales)
- Feedback loops
- Bug fixes
- Performance tuning

### Launch (Semana 5)
- Open beta en App Store/Play Store
- Landing page
- Influencer seeding
- Community building
- PR reach out

### Post-Launch
- Monitoring 24/7
- Hotfix procedures
- Weekly updates
- Community engagement

---

## 📈 GROWTH TARGETS

```
Semana 1-2:    100 usuarios
Semana 3-4:    500 usuarios
Mes 1:        2,000 usuarios
Mes 2:       10,000 usuarios
Mes 3:       50,000 usuarios
Mes 6:      200,000 usuarios
```

**Assumption:** 10% conversion a Premium = revenue

---

## ✅ FASE 0: SETUP (HOY)

- [x] Schema v2 creado
- [ ] Supabase project setup
- [ ] Backend estructura
- [ ] Frontend boilerplate
- [ ] CI/CD setup
- [ ] Monitoring setup

**Tiempo estimado:** 2-3 horas

---

## 🎉 FASE POSTERIOR: FUTURE

### Semana 5+
- [ ] WebSocket mejorado (typing, online status)
- [ ] Push notifications
- [ ] Video calls
- [ ] Advanced AI matching
- [ ] Mobile app nativo
- [ ] Analytics avanzado

### Mes 2+
- [ ] Integración Instagram/Spotify
- [ ] Referral system
- [ ] Ambassadors program
- [ ] API para developers
- [ ] Web3/blockchain features

---

**Estado:** ✅ Plan completado  
**Siguiente:** Implementación semana 1  
**Owner:** Claude + Usuario  

