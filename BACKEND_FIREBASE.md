# 🔥 BACKEND CON FIREBASE PARA YUIZZ

## ¿Por Qué Firebase?

✅ **VENTAJAS:**
- Gratis hasta 100 conexiones simultáneas
- Autenticación + Database incluidas
- Real-time database (actualizaciones en vivo)
- Almacenamiento de fotos
- Sin servidor que mantener
- Perfect para startups

❌ **DESVENTAJAS:**
- Vendor lock-in (solo Firebase)
- Precios suben rápido si creces
- No tienes control del servidor

---

## ⚡ SETUP RÁPIDO (10 minutos)

### Paso 1: Crear Proyecto Firebase
```
1. Ir a https://firebase.google.com
2. Click "Comenzar"
3. Click "Crear proyecto"
4. Nombre: "yuizz-app"
5. Deshabilitar Google Analytics (gratis sin él)
6. Click "Crear proyecto"
7. Esperar 2-3 minutos
```

### Paso 2: Configurar Autenticación

```
En Firebase Console:
1. Ir a Authentication → Sign-in method
2. Habilitar:
   - Email/Password
   - Google Sign-In
   - Apple Sign-In
3. Copiar "API Key" de Configuración del proyecto
```

### Paso 3: Configurar Realtime Database

```
En Firebase Console:
1. Ir a Realtime Database
2. Click "Crear base de datos"
3. Empezar en modo prueba
4. Ubicación: us-central1 (gratis)
5. Click "Habilitar"

IMPORTANTE - Configurar Reglas de Seguridad:
{
  "rules": {
    "users": {
      "$uid": {
        ".read": "$uid === auth.uid",
        ".write": "$uid === auth.uid"
      }
    },
    "profiles": {
      "$pid": {
        ".read": true,
        ".write": "root.child('users').child(auth.uid).exists()"
      }
    },
    "matches": {
      "$mid": {
        ".read": "auth.uid in root.child('matches').child($mid).val()",
        ".write": "!data.exists() && auth.uid in $newData.val()"
      }
    }
  }
}
```

### Paso 4: Instalar SDK de Firebase

```bash
# En tu proyecto
npm install firebase

# Crear archivo firebase-config.js
cat > firebase-config.js << 'EOF'
import { initializeApp } from 'firebase/app';
import { getAuth, signInAnonymously, signInWithEmailAndPassword } from 'firebase/auth';
import { getDatabase, ref, set, get, update } from 'firebase/database';
import { getStorage } from 'firebase/storage';

const firebaseConfig = {
  apiKey: "TU_API_KEY",
  authDomain: "yuizz-app.firebaseapp.com",
  projectId: "yuizz-app",
  storageBucket: "yuizz-app.appspot.com",
  messagingSenderId: "XXXXXXXXXX",
  databaseURL: "https://yuizz-app.firebaseio.com",
  appId: "XXXXXXXXXXXXXXXXXXXXXXXXXX"
};

const app = initializeApp(firebaseConfig);
export const auth = getAuth(app);
export const db = getDatabase(app);
export const storage = getStorage(app);

// Login anónimo (para demo)
export const loginAnonymously = async () => {
  try {
    const result = await signInAnonymously(auth);
    return result.user;
  } catch (error) {
    console.error("Auth error:", error);
  }
};

export default app;
EOF
```

---

## 💾 ESTRUCTURA DE DATA EN FIREBASE

```
firebase
├── users/
│   └── {userId}/
│       ├── email: "sofia@example.com"
│       ├── name: "Sofia"
│       ├── age: 24
│       ├── location: "Barcelona"
│       ├── bio: "Aventurera..."
│       ├── favoriteGenre: "Reggaeton"
│       ├── favoriteSong: "Bad Bunny - Tití"
│       ├── coins: 450
│       ├── isPremium: false
│       ├── socials: {
│       │   instagram: "sofia.travels",
│       │   tiktok: "sofiaatravel",
│       │   snapchat: "sofiatv",
│       │   telegram: "sofiavibe"
│       │ }
│       └── createdAt: 1234567890
│
├── profiles/
│   └── {profileId}/
│       ├── userId: "abc123"
│       ├── photo: "https://storage.googleapis.com/..."
│       ├── likes: 234
│       ├── views: 1245
│       ├── communities: ["gym", "sushi", "music"]
│       └── verified: true
│
├── matches/
│   └── {matchId}/
│       ├── user1: "userId1"
│       ├── user2: "userId2"
│       ├── matchedAt: 1234567890
│       └── messageCount: 5
│
├── messages/
│   └── {matchId}/
│       └── {messageId}/
│           ├── from: "userId1"
│           ├── to: "userId2"
│           ├── text: "Hola! Cómo estás?"
│           ├── timestamp: 1234567890
│           └── read: false
│
└── communities/
    └── {communityId}/
        ├── name: "Gym Lovers"
        ├── emoji: "💪"
        ├── members: 3420
        └── lastActivity: 1234567890
```

---

## 🔐 FUNCIONES CLAVE

### 1. Registrar Usuario
```javascript
import { createUserWithEmailAndPassword } from 'firebase/auth';

async function registerUser(email, password, userData) {
  try {
    const result = await createUserWithEmailAndPassword(auth, email, password);
    const uid = result.user.uid;
    
    // Guardar datos adicionales
    await set(ref(db, `users/${uid}`), {
      email,
      name: userData.name,
      age: userData.age,
      location: userData.location,
      bio: userData.bio,
      favoriteGenre: userData.favoriteGenre,
      coins: 450,
      isPremium: false,
      createdAt: Date.now()
    });
    
    return uid;
  } catch (error) {
    console.error("Registration error:", error);
  }
}
```

### 2. Dar Like a Perfil
```javascript
async function likeProfile(currentUserId, profileId) {
  try {
    // Guardar like
    await update(ref(db, `profiles/${profileId}`), {
      likes: (await get(ref(db, `profiles/${profileId}/likes`))).val() + 1
    });
    
    // Verificar si es Match
    const userLiked = await get(ref(db, `users/${profileId}/likes/${currentUserId}`));
    
    if (userLiked.exists()) {
      // ¡ES UN MATCH!
      const matchId = [currentUserId, profileId].sort().join('_');
      await set(ref(db, `matches/${matchId}`), {
        user1: currentUserId,
        user2: profileId,
        matchedAt: Date.now()
      });
      
      return { isMatch: true, matchId };
    }
    
    return { isMatch: false };
  } catch (error) {
    console.error("Like error:", error);
  }
}
```

### 3. Enviar Mensaje
```javascript
async function sendMessage(matchId, fromUserId, message) {
  try {
    const messageId = ref(db, `messages/${matchId}`).push().key;
    
    await set(ref(db, `messages/${matchId}/${messageId}`), {
      from: fromUserId,
      text: message,
      timestamp: Date.now(),
      read: false
    });
    
    return messageId;
  } catch (error) {
    console.error("Message error:", error);
  }
}
```

### 4. Obtener Matches
```javascript
async function getUserMatches(userId) {
  try {
    const matchesRef = ref(db, 'matches');
    const snapshot = await get(matchesRef);
    
    const userMatches = [];
    snapshot.forEach(child => {
      const match = child.val();
      if (match.user1 === userId || match.user2 === userId) {
        userMatches.push({
          id: child.key,
          ...match
        });
      }
    });
    
    return userMatches;
  } catch (error) {
    console.error("Matches error:", error);
  }
}
```

---

## 🛒 SISTEMA DE MONEDAS Y PAGOS

### Integrar Stripe (Para pagos reales)

```bash
npm install stripe @stripe/react-stripe-js
```

```javascript
import { loadStripe } from '@stripe/stripe-js';

const stripe = await loadStripe('pk_live_...');

async function buyCoins(amount, userId) {
  try {
    // Crear Checkout Session
    const response = await fetch('/api/create-checkout', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        userId,
        amount,
        priceId: 'price_...' // De tu dashboard Stripe
      })
    });
    
    const { sessionId } = await response.json();
    
    // Redirigir a Stripe Checkout
    await stripe.redirectToCheckout({ sessionId });
  } catch (error) {
    console.error("Payment error:", error);
  }
}
```

**En backend (Node.js/Cloud Functions):**
```javascript
const stripe = require('stripe')(process.env.STRIPE_SECRET_KEY);

exports.createCheckout = async (req, res) => {
  const { userId, amount } = req.body;
  
  const session = await stripe.checkout.sessions.create({
    payment_method_types: ['card'],
    line_items: [
      {
        price_data: {
          currency: 'eur',
          product_data: {
            name: `${amount} YUIZZ Coins`
          },
          unit_amount: amount * 100
        },
        quantity: 1
      }
    ],
    mode: 'payment',
    success_url: `https://yuizz.app/success?session_id={CHECKOUT_SESSION_ID}`,
    cancel_url: 'https://yuizz.app/cancel',
    metadata: { userId }
  });
  
  res.json({ sessionId: session.id });
};

// Webhook para cuando se completa el pago
exports.handlePaymentWebhook = async (req, res) => {
  const event = req.body;
  
  if (event.type === 'checkout.session.completed') {
    const session = event.data.object;
    const { userId } = session.metadata;
    
    // Agregar monedas al usuario
    const coinsToAdd = calculateCoinsFromAmount(session.amount_total);
    await admin.database()
      .ref(`users/${userId}/coins`)
      .transaction(current => current + coinsToAdd);
  }
  
  res.json({ received: true });
};
```

---

## 📸 ALMACENAMIENTO DE FOTOS

### Subir foto de perfil
```javascript
import { ref as storageRef, uploadBytes, getDownloadURL } from 'firebase/storage';

async function uploadProfilePhoto(userId, file) {
  try {
    const fileRef = storageRef(storage, `profiles/${userId}/photo.jpg`);
    
    // Comprimir imagen (opcional)
    const compressed = await compressImage(file);
    
    // Subir
    await uploadBytes(fileRef, compressed);
    
    // Obtener URL pública
    const photoUrl = await getDownloadURL(fileRef);
    
    // Guardar URL en database
    await update(ref(db, `users/${userId}`), {
      photoUrl
    });
    
    return photoUrl;
  } catch (error) {
    console.error("Upload error:", error);
  }
}

// Función para comprimir imagen
async function compressImage(file) {
  return new Promise(resolve => {
    const reader = new FileReader();
    reader.readAsDataURL(file);
    reader.onload = event => {
      const img = new Image();
      img.src = event.target.result;
      img.onload = () => {
        const canvas = document.createElement('canvas');
        const ctx = canvas.getContext('2d');
        
        canvas.width = 800;
        canvas.height = 800;
        ctx.drawImage(img, 0, 0, 800, 800);
        
        canvas.toBlob(resolve, 'image/jpeg', 0.7);
      };
    };
  });
}
```

---

## 🚀 DEPLOY A PRODUCCIÓN

### Firebase Hosting (Gratis)

```bash
# Instalar Firebase CLI
npm install -g firebase-tools

# Login
firebase login

# Inicializar proyecto
firebase init hosting

# Deploy
npm run build
firebase deploy --only hosting
```

### Cloud Functions (Para lógica del servidor)

```bash
# Inicializar
firebase init functions

# Crear función
firebase deploy --only functions
```

---

## 💰 PRECIOS FIREBASE

```
Tier Gratis (incluido):
- 100 conexiones simultáneas
- 1 GB de almacenamiento
- 10 GB de ancho de banda/mes
- Autenticación ilimitada

Precios si pasas límite:
- $1 por 100,000 escrituras
- $1 por 1,000,000 lecturas
- $0.18 por GB almacenamiento
- $0.12 por GB descargado

Estimado para 10,000 usuarios activos:
- Mes 1: $50-100
- Mes 2-3: $200-500
- Con Stripe: Tomas 70% de la comisión (30% Stripe)
```

---

## ✅ CHECKLIST ANTES DE PRODUCCIÓN

- [ ] Firebase project creado
- [ ] Autenticación configurada
- [ ] Realtime Database con reglas de seguridad
- [ ] Storage para fotos configurado
- [ ] Stripe integrado para pagos
- [ ] Cloud Functions deployment probado
- [ ] Backups automáticos configurados
- [ ] Monitoring y alertas configuradas

---

## 🎯 RESUMEN

**Para agregar backend a YUIZZ:**

1. Crear Firebase project (5 min)
2. Copiar config en tu app (2 min)
3. Implementar login (10 min)
4. Implementar likes/matches (15 min)
5. Integrar Stripe para pagos (20 min)
6. Deploy a Firebase Hosting (5 min)

**TOTAL: 1 hora de trabajo**

**Costo mensual:** $0 a $100+ (según crecimiento)

---

📚 **Documentación:**
- Firebase: https://firebase.google.com/docs
- Stripe: https://stripe.com/docs
- React Firebase: https://github.com/FirebaseExtended/reactfire

¡**YUIZZ LISTA PARA PRODUCCIÓN!** 🚀
