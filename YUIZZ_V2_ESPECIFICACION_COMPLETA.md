# 🔥 YUIZZ V2 - ESPECIFICACIÓN COMPLETA

**Versión:** 2.0 (Repositorio Adulto)  
**Fecha:** 28 Septiembre 2026  
**Estado:** Especificación (Desarrollo iniciado)  
**Objetivo:** MVP en 3-4 semanas

---

## 🎯 POSICIONAMIENTO

### Tagline
**"Conexiones sin límites. Adultos, sin tabúes."**

### Descripción
YUIZZ es una **plataforma social de citas para adultos** donde personas solteras y parejas pueden:
- Conocer gente
- Descubrir conexiones
- Chatear y ligar
- Explorar intenciones compartidas
- Encontrar citas, encuentros, relaciones abiertas, o simplemente coqueteo
- Sin prejuicios ni etiquetas

**Diferencia clave:** Orientada a adultos con intenciones claras. Flexible para todas las búsquedas. Moderna y elegante, no pornográfica.

---

## 👥 AUDIENCIA OBJETIVO

### Primaria
- Adultos 18-65+ años (foco 25-45)
- Singles buscando: citas, encuentros, relaciones, amigos
- Parejas buscando: parejas, singles, exploración

### Secundaria
- Personas curiosas/exploradores
- Relaciones abiertas
- Personas LGBTQ+
- Amistad entre adultos

### NO incluye
- Menores de 18 años
- Matrimonios cerrados exclusivos
- Transacciones sexuales comerciales

---

## 🏗️ ARQUITECTURA GENERAL

```
YUIZZ V2 (Adulta)
│
├─ FRONTEND
│  ├─ Web (React/TS) - Web principal
│  ├─ Mobile (React Native/Expo) - iOS/Android
│  └─ PWA (Progressive Web App)
│
├─ BACKEND
│  ├─ API (Node.js/Express)
│  ├─ Auth (JWT + Supabase Auth)
│  ├─ Realtime (WebSocket - Supabase Realtime)
│  ├─ Storage (Supabase Storage - Fotos)
│  └─ Messaging (Redis - Cache + Sockets)
│
├─ DATABASE
│  ├─ Supabase PostgreSQL
│  ├─ RLS (Row Level Security)
│  ├─ Full-text search
│  └─ GIS (Geolocation)
│
└─ SERVICES
   ├─ Stripe (Pagos)
   ├─ SendGrid (Email transaccional)
   ├─ Sentry (Error tracking)
   └─ Cloudflare (CDN + DDoS)
```

---

## 📋 SCHEMA DE BASE DE DATOS

### 1. AUTH USERS
```sql
CREATE TABLE auth.users (
  id UUID PRIMARY KEY
  email VARCHAR(255) UNIQUE
  phone VARCHAR(20)
  phone_verified BOOLEAN
  email_verified BOOLEAN
  encrypted_password VARCHAR(255)
  created_at TIMESTAMP
  updated_at TIMESTAMP
  deleted_at TIMESTAMP -- soft delete
);
```

### 2. PROFILES (Perfil Individual)
```sql
CREATE TABLE profiles (
  id UUID PRIMARY KEY → auth.users
  
  -- Identidad
  first_name VARCHAR(100)
  last_name VARCHAR(100)
  username VARCHAR(50) UNIQUE
  bio TEXT
  
  -- Datos personales (privados)
  birth_date DATE
  age INT GENERATED
  gender VARCHAR(50) -- 'm', 'f', 'nb', 'other'
  pronoun VARCHAR(50)
  
  -- Ubicación
  latitude DECIMAL(10,8)
  longitude DECIMAL(11,8)
  city VARCHAR(100)
  country VARCHAR(100)
  
  -- Privacidad
  show_location BOOLEAN DEFAULT true
  location_accuracy VARCHAR(50) -- 'city', 'neighbourhood', 'exact'
  show_age BOOLEAN DEFAULT true
  show_distance BOOLEAN DEFAULT true
  
  -- Verificación
  age_verified BOOLEAN DEFAULT false
  document_verified BOOLEAN DEFAULT false
  selfie_verified BOOLEAN DEFAULT false
  verification_doc_url TEXT
  
  -- Intereses (JSON tags)
  interests VARCHAR[]
  orientations VARCHAR[] -- 'men', 'women', 'nb', 'all'
  languages VARCHAR[]
  
  -- Intenciones (¿QUÉ BUSCAS?)
  seeking VARCHAR[] -- 'dating', 'casual', 'sexting', 'relationship', 'meeting', 'friends', 'explore'
  
  -- Tipo de perfil
  profile_type VARCHAR(50) DEFAULT 'individual' -- 'individual' or 'couple'
  couple_id UUID → couples(id)
  
  -- Metadata
  profile_complete BOOLEAN DEFAULT false
  last_active TIMESTAMP
  is_active BOOLEAN DEFAULT true
  created_at TIMESTAMP
  updated_at TIMESTAMP
);

CREATE INDEX idx_profiles_location ON profiles(latitude, longitude);
CREATE INDEX idx_profiles_city ON profiles(city);
CREATE INDEX idx_profiles_seeking ON profiles USING GIN(seeking);
```

### 3. COUPLES (Perfiles de Pareja)
```sql
CREATE TABLE couples (
  id UUID PRIMARY KEY
  
  name VARCHAR(200) -- "Maria & Juan"
  bio TEXT
  couple_photo_url TEXT
  
  -- Miembros
  primary_user_id UUID → auth.users
  secondary_user_id UUID → auth.users
  
  -- Quiénes son
  person1_name VARCHAR(100)
  person1_gender VARCHAR(50)
  person2_name VARCHAR(100)
  person2_gender VARCHAR(50)
  
  -- Qué buscan
  seeking VARCHAR[] -- 'women', 'men', 'couples', 'groups'
  
  -- Ubicación (conjunta)
  latitude DECIMAL(10,8)
  longitude DECIMAL(11,8)
  city VARCHAR(100)
  
  -- Estado
  is_active BOOLEAN DEFAULT true
  created_at TIMESTAMP
  updated_at TIMESTAMP
  
  CONSTRAINT both_users_different CHECK (primary_user_id != secondary_user_id)
);
```

### 4. PROFILE_PHOTOS (Galerías)
```sql
CREATE TABLE profile_photos (
  id UUID PRIMARY KEY
  user_id UUID → auth.users
  
  -- Foto
  photo_url TEXT NOT NULL
  thumb_url TEXT -- thumbnail
  
  -- Metadatos
  position INT -- orden
  is_public BOOLEAN DEFAULT true -- visible a todos
  is_private BOOLEAN DEFAULT false -- solo matches
  is_blur BOOLEAN DEFAULT false -- desenfocada
  
  -- Acceso privado
  requires_unlock BOOLEAN DEFAULT false
  unlock_price_coins INT DEFAULT 50
  
  -- Moderación
  flagged BOOLEAN DEFAULT false
  flag_reason VARCHAR(255)
  approved_by_moderation BOOLEAN DEFAULT true
  
  created_at TIMESTAMP
);

CREATE INDEX idx_profile_photos_user ON profile_photos(user_id);
```

### 5. PROFILE_GALLERIES (Galerías Privadas)
```sql
CREATE TABLE profile_galleries (
  id UUID PRIMARY KEY
  user_id UUID → auth.users
  
  title VARCHAR(100) -- "Fotos privadas", "Solo para matches", etc.
  description TEXT
  is_public BOOLEAN DEFAULT false
  
  -- Acceso
  access_type VARCHAR(50) -- 'matches_only', 'liked_me', 'request_based', 'coins'
  
  created_at TIMESTAMP
);

CREATE TABLE gallery_access_requests (
  id UUID PRIMARY KEY
  gallery_id UUID → profile_galleries
  requester_id UUID → auth.users
  owner_id UUID → auth.users
  
  status VARCHAR(50) DEFAULT 'pending' -- 'pending', 'approved', 'denied'
  cost_coins INT DEFAULT 0
  
  created_at TIMESTAMP
  responded_at TIMESTAMP
);
```

### 6. INTERACTIONS (Likes, Passes, Superlikes)
```sql
CREATE TABLE interactions (
  id UUID PRIMARY KEY
  
  actor_id UUID → auth.users (quien hace la acción)
  target_id UUID → auth.users (quien recibe)
  action VARCHAR(50) -- 'like', 'pass', 'superlike', 'view'
  
  -- Match detection
  match BOOLEAN DEFAULT false -- bidireccional
  match_created_at TIMESTAMP
  
  -- Metadata
  ip_hash VARCHAR(255)
  created_at TIMESTAMP
  
  CONSTRAINT actor_not_target CHECK (actor_id != target_id)
);

CREATE INDEX idx_interactions_actor ON interactions(actor_id, action);
CREATE INDEX idx_interactions_target ON interactions(target_id);
CREATE INDEX idx_interactions_match ON interactions(match) WHERE match = true;
```

### 7. MATCHES (Conexiones)
```sql
CREATE TABLE matches (
  id UUID PRIMARY KEY
  
  user1_id UUID → auth.users
  user2_id UUID → auth.users
  
  match_type VARCHAR(50) -- 'mutual_like', 'superlike'
  status VARCHAR(50) DEFAULT 'active' -- 'active', 'blocked', 'reported'
  
  last_message_id UUID → messages(id)
  last_message_at TIMESTAMP
  
  unread_count_user1 INT DEFAULT 0
  unread_count_user2 INT DEFAULT 0
  
  created_at TIMESTAMP
  updated_at TIMESTAMP
  
  CONSTRAINT user1_less_user2 CHECK (user1_id < user2_id)
);

CREATE INDEX idx_matches_users ON matches(user1_id, user2_id);
```

### 8. MESSAGES (Chat)
```sql
CREATE TABLE messages (
  id UUID PRIMARY KEY
  
  match_id UUID → matches
  sender_id UUID → auth.users
  receiver_id UUID → auth.users
  
  -- Contenido
  content TEXT
  content_type VARCHAR(50) -- 'text', 'image', 'gif', 'emoji'
  
  -- Media
  image_url TEXT
  image_thumb_url TEXT
  
  -- Estado
  is_read BOOLEAN DEFAULT false
  read_at TIMESTAMP
  deleted_by_sender BOOLEAN DEFAULT false
  deleted_by_receiver BOOLEAN DEFAULT false
  
  -- Reportes
  flagged BOOLEAN DEFAULT false
  flag_reason VARCHAR(255)
  
  created_at TIMESTAMP
  
  CONSTRAINT sender_receiver_diff CHECK (sender_id != receiver_id)
);

CREATE INDEX idx_messages_match ON messages(match_id, created_at DESC);
CREATE INDEX idx_messages_receiver ON messages(receiver_id, is_read);
```

### 9. POSTS (Publicaciones/Anuncios)
```sql
CREATE TABLE posts (
  id UUID PRIMARY KEY
  user_id UUID → auth.users
  couple_id UUID → couples(id) (opcional)
  
  -- Contenido
  content TEXT NOT NULL
  post_type VARCHAR(50) -- 'status', 'announcement', 'question', 'event'
  
  -- Intención del post
  seeking VARCHAR[] -- array de intenciones del post
  
  -- Ubicación
  latitude DECIMAL(10,8)
  longitude DECIMAL(11,8)
  city VARCHAR(100)
  show_location BOOLEAN
  
  -- Filtros
  min_age INT
  max_age INT
  gender_preference VARCHAR[]
  
  -- Media
  photos_urls TEXT[] -- max 4 fotos
  
  -- Engagement
  views INT DEFAULT 0
  likes INT DEFAULT 0
  comments INT DEFAULT 0
  shares INT DEFAULT 0
  
  -- Estado
  is_active BOOLEAN DEFAULT true
  flagged BOOLEAN DEFAULT false
  
  -- Expiración
  expires_at TIMESTAMP -- posts expiran en 7 días
  
  created_at TIMESTAMP
  updated_at TIMESTAMP
);

CREATE INDEX idx_posts_user ON posts(user_id, created_at DESC);
CREATE INDEX idx_posts_location ON posts(latitude, longitude);
CREATE INDEX idx_posts_seeking ON posts USING GIN(seeking);
```

### 10. COINS (Economía)
```sql
CREATE TABLE user_coins (
  id UUID PRIMARY KEY
  user_id UUID → auth.users UNIQUE
  
  coins INT DEFAULT 0
  lifetime_coins_spent INT DEFAULT 0
  lifetime_coins_earned INT DEFAULT 0
  
  updated_at TIMESTAMP
);

CREATE TABLE coin_transactions (
  id UUID PRIMARY KEY
  user_id UUID → auth.users
  
  transaction_type VARCHAR(50) -- 'purchase', 'spent', 'bonus', 'refund'
  amount INT
  reason VARCHAR(255)
  
  -- Para purchase
  stripe_payment_id VARCHAR(255)
  price_usd DECIMAL(10,2)
  
  created_at TIMESTAMP
);

CREATE INDEX idx_coin_trans_user ON coin_transactions(user_id, created_at);
```

### 11. SUBSCRIPTIONS (Premium)
```sql
CREATE TABLE subscriptions (
  id UUID PRIMARY KEY
  user_id UUID → auth.users
  
  plan_id VARCHAR(50) DEFAULT 'free' -- 'free', 'premium'
  billing_period VARCHAR(20) -- 'monthly', 'annual'
  status VARCHAR(50) -- 'active', 'cancelled', 'expired'
  
  start_date TIMESTAMP
  end_date TIMESTAMP
  
  stripe_customer_id VARCHAR(255)
  stripe_subscription_id VARCHAR(255)
  payment_method VARCHAR(50)
  
  created_at TIMESTAMP
  updated_at TIMESTAMP
);
```

### 12. BLOCKS & REPORTS (Privacidad y Seguridad)
```sql
CREATE TABLE blocks (
  id UUID PRIMARY KEY
  blocker_id UUID → auth.users
  blocked_id UUID → auth.users
  
  reason VARCHAR(255)
  created_at TIMESTAMP
  
  CONSTRAINT blocker_not_blocked CHECK (blocker_id != blocked_id)
);

CREATE TABLE reports (
  id UUID PRIMARY KEY
  reporter_id UUID → auth.users
  reported_id UUID → auth.users
  
  report_type VARCHAR(50) -- 'fake_profile', 'spam', 'harassment', 'inappropriate', 'scam'
  description TEXT
  evidence_urls TEXT[]
  
  status VARCHAR(50) DEFAULT 'pending' -- 'pending', 'investigating', 'resolved', 'dismissed'
  moderation_notes TEXT
  action_taken VARCHAR(50) -- 'warning', 'suspend', 'ban'
  
  created_at TIMESTAMP
  resolved_at TIMESTAMP
);

CREATE INDEX idx_reports_reported ON reports(reported_id, status);
```

### 13. AGE_VERIFICATION (18+ Control)
```sql
CREATE TABLE age_verification (
  id UUID PRIMARY KEY
  user_id UUID → auth.users
  
  birth_date DATE NOT NULL
  document_type VARCHAR(50) -- 'passport', 'id_card', 'driving_license'
  document_country VARCHAR(2)
  
  verification_status VARCHAR(50) -- 'pending', 'verified', 'rejected'
  verified_at TIMESTAMP
  verified_by_admin_id UUID
  
  rejection_reason VARCHAR(255)
  
  created_at TIMESTAMP
  updated_at TIMESTAMP
);
```

### 14. ACTIVITY_LOG (Analytics)
```sql
CREATE TABLE activity_log (
  id UUID PRIMARY KEY
  user_id UUID → auth.users
  
  action VARCHAR(100)
  entity_type VARCHAR(50) -- 'profile', 'message', 'like', 'post'
  entity_id UUID
  metadata JSON
  
  ip_address INET
  user_agent TEXT
  
  created_at TIMESTAMP
);

CREATE INDEX idx_activity_log_user ON activity_log(user_id, created_at);
```

### 15. NOTIFICATIONS (Notificaciones)
```sql
CREATE TABLE notifications (
  id UUID PRIMARY KEY
  user_id UUID → auth.users
  
  type VARCHAR(50) -- 'match', 'message', 'like', 'superlike', 'viewed'
  title VARCHAR(200)
  body TEXT
  actor_id UUID → auth.users (quien genera notificación)
  
  data JSON -- metadata adicional
  
  is_read BOOLEAN DEFAULT false
  read_at TIMESTAMP
  
  created_at TIMESTAMP
);

CREATE INDEX idx_notifications_user ON notifications(user_id, created_at DESC);
```

---

## 🔐 SEGURIDAD Y PRIVACIDAD

### Verificación de Edad (Crítico)

**Nivel 1: Autoverificación (Registro)**
```
- Fecha de nacimiento
- Checkbox: "Confirmo que soy mayor de 18"
- Verificar formato fecha
- Guardar en age_verification table
```

**Nivel 2: Verificación Foto (Opcional pero Recomendado)**
```
- Selfie del usuario
- Comparar con foto ID
- ML/Moderación: ¿Es real? ¿Es mayor de 18?
- Status: verified/pending/rejected
```

**Nivel 3: Verificación Documento (Premium Feature)**
```
- Upload de documento (ID, pasaporte, etc.)
- OCR + validación
- Verificación manual
- Badge azul si verificado
```

### Row Level Security (RLS) - Supabase

```sql
-- Perfiles: Solo ver si:
-- 1. Es el propietario
-- 2. Es un match
-- 3. Es público
-- 4. Datos privados solo para matches

CREATE POLICY "Users can view own profile"
  ON profiles FOR SELECT
  USING (auth.uid() = id);

CREATE POLICY "Users can view other profiles if match or public"
  ON profiles FOR SELECT
  USING (
    auth.uid() != id AND
    (is_active OR auth.uid() IN (
      SELECT CASE 
        WHEN user1_id = auth.uid() THEN user2_id
        WHEN user2_id = auth.uid() THEN user1_id
      END
      FROM matches
    ))
  );

-- Mensajes: Solo ver propios
CREATE POLICY "Users can only see own messages"
  ON messages FOR SELECT
  USING (auth.uid() IN (sender_id, receiver_id));

-- Fotos privadas: Solo si match
CREATE POLICY "Can view private photos if match"
  ON profile_photos FOR SELECT
  USING (
    auth.uid() = user_id OR
    (is_private AND auth.uid() IN (
      SELECT CASE 
        WHEN user1_id = auth.uid() THEN user2_id
        ELSE user1_id 
      END FROM matches WHERE status = 'active'
    ))
  );
```

### Privacidad de Ubicación

```
✓ Opción: Mostrar ciudad exacta o rango
✓ Opción: Mostrar distancia o rango (5km, 10km, 50km)
✓ Nunca: Mostrar dirección exacta
✓ Privacidad por defecto: Más restrictivo
✓ Geocaching: No guardar exactas en logs
```

---

## 💰 SISTEMA DE MONETIZACIÓN

### Modelo Hybrid: Suscripción + Monedas

**PLAN FREE**
```
Características:
- Perfil con até 4 fotos públicas
- Descubrimiento (15/día)
- Chat (sin GIFs/fotos)
- Ver matches
- Crear posts (1/semana)
- Sin acceso a galerías privadas
```

**PLAN PREMIUM (€3.99/mes o €35.90/año)**
```
Características:
- TODO de Free +
- Descubrimiento ilimitado
- Chat completo (GIFs, fotos, emojis)
- Hasta 10 fotos públicas
- Galería privada (5 fotos)
- Posts ilimitados
- Ver quién vio tu perfil
- Ver quién te gustó sin reciprocidad
- Filtros avanzados
- Boost mensual gratis
- Monedas bonus: +50 coins/mes
```

### Coins (Micropagos + Gamificación)

**Packs disponibles:**

| Pack | Coins | Precio | €/Coin |
|------|-------|--------|--------|
| Pequeño | 100 | €0.99 | 0.99¢ |
| Medio | 600 | €4.99 | 0.83¢ |
| Grande | 1.500 | €9.99 | 0.67¢ |
| XL | 4.500 | €24.99 | 0.56¢ |

**Con bonus:**
- XL pack: +20% bonus (5.400 coins)
- Premium subscribers: +10% bonus en todos los packs

**Usos de coins:**

| Acción | Costo |
|--------|-------|
| Boost 1h | 50 coins |
| Boost 8h | 200 coins |
| Boost 24h | 400 coins |
| Destacar post | 100 coins |
| Desbloquear galería (10 fotos) | 100 coins |
| Mensaje a no-match (opcional) | 10 coins |
| Ver quién gustó (si free) | 50 coins |

**Gamificación:**
- Completar perfil: +10 coins
- Primer match: +20 coins
- Primer mensaje: +5 coins
- Racha diaria: +5 coins/día (max 50)

---

## 🎯 FUNCIONALIDADES CORE

### 1. AUTENTICACIÓN Y REGISTRO

**Flow:**
```
1. Email o teléfono
2. Verificación (OTP)
3. Contraseña
4. Fecha nacimiento (validar 18+)
5. Foto de perfil
6. Nombre
7. Género + pronombre
8. ¿Buscas? (checkboxes múltiples)
9. Términos + privacidad
10. ¡Bienvenido!
```

**Validaciones:**
```
✓ Email único
✓ Edad >= 18
✓ Foto claramente visible
✓ Foto real (no AI, no de otros)
✓ Términos aceptados
✓ Privacidad aceptada
```

### 2. PERFILES INDIVIDUALES

**Estructura:**
```
[Foto principal grande]

Nombre, Edad, Ciudad
[verificado con badge]

Bio (máx 500 caracteres)

¿Qué buscas?
☑ Citas
☑ Casual
☑ Sexting
☑ Relación
☑ Encuentros
☑ Amistad

Intereses: #viajes #cine #deporte

Orientación: Mujeres, Hombres, Todos

Galería (4-5 fotos públicas)

[Bloquear] [Reportar]
```

**Privacidad personalizable:**
```
☐ Mostrar edad exacta
☐ Mostrar ubicación (ciudad)
☐ Mostrar distancia
☐ Mostrar en búsquedas públicas
☐ Permitir solicitudes de fotos privadas
```

### 3. PERFILES DE PAREJA

**Crear:**
```
1. "¿Sois pareja?" → Sí
2. Agregar pareja (email/usuario)
3. Pareja confirma (link/código)
4. Nombre conjunto: "Maria & Juan"
5. Foto de pareja
6. Bio conjunta
7. Quiénes son (María - mujer / Juan - hombre)
8. ¿Qué buscáis? (checkboxes)
9. Preferencias (buscamos hombres/mujeres/parejas)
```

**Perfil:**
```
[Foto pareja]

Maria & Juan
27 & 29 años, Madrid

Bio: "Pareja con curiosidad. Sin prejuicios."

Buscamos: 👩 Mujeres para encuentros
          👫 Parejas para conocer

Intereses: #swinging #coqueteo #viajes

Galería:
- 3 fotos públicas pareja
- 4 fotos privadas (María)
- 4 fotos privadas (Juan)
```

**Chat:**
- Ambos pueden ver/responder
- Opcional: Un "admin" principal
- Historial compartido

### 4. DESCUBRIMIENTO

**Vista principal:**
```
DESCUBRIMIENTO
┌─────────────────────┐
│ [Foto grande]       │
│ María, 28, Madrid   │
│ 2.3 km              │
│                     │
│ "Buscando citas..." │
│                     │
│ 👋 ❤️  ⭐           │
└─────────────────────┘

Filtros avanzados:
- Edad: 18-45
- Género: Mujer
- Distancia: 5km
- Qué buscan: Citas, Casual
- Orientación: Mujeres
- Verificado: Sí
```

**Acciones:**
- 👋 Pass (siguiente)
- ❤️ Like (interés)
- ⭐ SuperLike (premium)

### 5. POSTS / ANUNCIOS

**Crear:**
```
¿Qué está en tu mente?

[Textarea: "Busco pareja para..."]

Añadir fotos (máx 4)
Ubicación: [Madrid] [Mostrar]

Qué buscas:
☑ Casual
☑ Coqueteo
☑ Encuentros

Edad objetivo: 20-35
Género: Mujeres, Hombres

[Publicar]
```

**Feed:**
```
Posts recientes cerca tuyo

🔥 Nueva - María, 28
"Pareja buscando tercera..."
[foto] [foto]
❤️ 24  💬 3

⭐ Destacado - Juan, 31
"¿Alguien para esta noche?"
[foto]
❤️ 156  💬 28
```

**Interacción:**
- Like
- Comentar (primeros 2 gratis, después coin)
- DM directo al autor
- Compartir
- Reportar

### 6. CHAT

**Vista de matches:**
```
MATCHES

Maria, 28 — 2 min ago
"Hola! Me gustaste..."
[unread badge]

Juan & Laura, 29/31 — online
"¿Qué tal?"

Sandra, 25 — 3 hours ago
"..." (sin nuevos)
```

**Conversación:**
```
[Maria]
▲ 2.3 km | Verificada | ❤️ mutual match

"Hola! Me gustaste mucho!"
[seen 2m ago]

[yo]
"¡Hola! Tú también me gustaste!"

[emoji picker] [GIF] [🖼️] [enviar]
```

**Funciones:**
- GIFs (Giphy)
- Emojis reacción
- Fotos inline
- Borrar conversación
- Bloquear/reportar

---

## 🎨 DISEÑO Y UX

### Identidad Visual

**Color Palette:**
```
Primary: #FF1F5B (Fucsia/Rosa - Adulto, Sexual)
Secondary: #FFB800 (Oro - Premium, Lujo)
Accent: #00D4FF (Cian - Moderno)
Dark: #1A1A1A
Light: #FFFFFF
Text: #333333
```

**Tipografía:**
```
Headings: Inter (Sans-serif, moderno)
Body: -apple-system, BlinkMacSystemFont
Monospace: Courier Prime
```

**Componentes:**
```
- Cards con sombra suave
- Bordes redondeados (8px)
- Transiciones fluidas (0.3s)
- Iconos: SF Symbols + Custom
- Botones: Full width, altos (48px)
```

### Screens Principales

1. **Auth:** Login/Registro
2. **Onboarding:** Foto + Intenciones
3. **Discovery:** Cards
4. **Matches:** Lista
5. **Chat:** Conversación
6. **Posts:** Feed
7. **Profile:** Perfil propio
8. **Settings:** Privacidad, etc.

---

## 📊 ANALYTICS

Métricas clave a trackear:
```
- Registros/día
- Verificación tasa
- Perfiles completos %
- Matches/usuario
- Retención (D1, D7, D30)
- Mensajes enviados
- Coins gastados
- Premium conversion %
```

---

## 🚀 ROADMAP DE DESARROLLO

### Fase 1 (Semanas 1-2): MVP Básico
```
✓ Auth + Verificación edad
✓ Perfiles individuales
✓ Discovery (cards)
✓ Like/Pass/SuperLike
✓ Matches básicos
✓ Chat texto
```

### Fase 2 (Semanas 3-4): Perfiles + Fotos
```
✓ Galerías públicas/privadas
✓ Perfiles de pareja
✓ Fotos privadas desbloqueable
✓ Posts/anuncios
✓ Reportes + bloqueos
```

### Fase 3 (Semana 5): Monetización
```
✓ Stripe integration
✓ Coins system
✓ Premium subscription
✓ Boosts
✓ Analytics dashboard
```

### Fase 4 (Semana 6): Polish + Deploy
```
✓ Performance optimization
✓ Security audit
✓ Moderation tools
✓ Admin dashboard
✓ Production deploy
```

---

## ✅ CHECKLIST ANTES DE LAUNCH

- [ ] 18+ verification working
- [ ] SSL/TLS certificados
- [ ] GDPR compliant
- [ ] Terms of Service
- [ ] Privacy Policy
- [ ] Community guidelines
- [ ] Moderación spam/CSAM
- [ ] Rate limiting
- [ ] DDoS protection
- [ ] Backup automated
- [ ] Error tracking (Sentry)
- [ ] Support email funcional

---

**Especificación completada:** 28 Septiembre 2026  
**Lista para desarrollo:** ✅ SÍ
**Estimación MVP:** 4-6 semanas

