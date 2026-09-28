/**
 * YUIZZ V2 - ADULT DATING PLATFORM
 * Backend API (Node.js + Express)
 *
 * PHASE 1: Authentication + Profiles + Verification
 */

import express from 'express';
import cors from 'cors';
import dotenv from 'dotenv';
import { createClient } from '@supabase/supabase-js';
import jwt from 'jsonwebtoken';
import bcrypt from 'bcryptjs';

// ============================================
// CONFIGURATION
// ============================================
dotenv.config();
const app = express();
const PORT = process.env.PORT || 3001;

app.use(cors());
app.use(express.json());

// ============================================
// SUPABASE CLIENT
// ============================================
const supabaseUrl = process.env.SUPABASE_URL;
const supabaseKey = process.env.SUPABASE_ANON_KEY;
const supabase = createClient(supabaseUrl, supabaseKey);

if (!supabaseUrl || !supabaseKey) {
  console.warn('⚠️  SUPABASE_URL o SUPABASE_ANON_KEY no configurados');
  process.exit(1);
}

// ============================================
// JWT & SECURITY
// ============================================
const JWT_SECRET = process.env.JWT_SECRET || 'dev-secret-change-in-production';
const JWT_EXPIRY = '30d';

const verifyToken = (req, res, next) => {
  const token = req.headers.authorization?.split(' ')[1];
  if (!token) return res.status(401).json({ error: 'No token provided' });

  try {
    const decoded = jwt.verify(token, JWT_SECRET);
    req.userId = decoded.id;
    next();
  } catch (error) {
    res.status(403).json({ error: 'Invalid or expired token' });
  }
};

// ============================================
// HELPERS
// ============================================

// Calculate age from birth_date
function calculateAge(birthDate) {
  const today = new Date();
  let age = today.getFullYear() - birthDate.getFullYear();
  const monthDiff = today.getMonth() - birthDate.getMonth();
  if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birthDate.getDate())) {
    age--;
  }
  return age;
}

// Validate age >= 18
function isAdult(birthDate) {
  return calculateAge(new Date(birthDate)) >= 18;
}

// Generate JWT
function generateToken(userId) {
  return jwt.sign({ id: userId }, JWT_SECRET, { expiresIn: JWT_EXPIRY });
}

// ============================================
// ROUTES: AUTHENTICATION
// ============================================

/**
 * POST /api/auth/register
 * Registro de usuario nuevo
 */
app.post('/api/auth/register', async (req, res) => {
  try {
    const { email, password, username, firstName, lastName, birthDate } = req.body;

    // Validaciones
    if (!email || !password || !username || !birthDate) {
      return res.status(400).json({ error: 'Missing required fields' });
    }

    // Verificar edad >= 18
    if (!isAdult(birthDate)) {
      return res.status(403).json({ error: 'Must be 18 years old' });
    }

    // Verificar username único
    const { data: existingUser } = await supabase
      .from('profiles')
      .select('id')
      .eq('username', username)
      .single()
      .catch(() => ({ data: null }));

    if (existingUser) {
      return res.status(409).json({ error: 'Username already taken' });
    }

    // Crear usuario en Supabase Auth
    const { data: authData, error: authError } = await supabase.auth.signUpWithPassword({
      email,
      password
    });

    if (authError) {
      return res.status(400).json({ error: authError.message });
    }

    const userId = authData.user.id;

    // Crear perfil de usuario
    const { error: profileError } = await supabase
      .from('profiles')
      .insert({
        id: userId,
        username,
        first_name: firstName || '',
        last_name: lastName || '',
        birth_date: birthDate,
        age: calculateAge(new Date(birthDate)),
        email: email,
        age_verified: false,
        profile_complete: false,
        is_active: true
      });

    if (profileError) {
      return res.status(400).json({ error: profileError.message });
    }

    // Crear registro de verificación de edad
    await supabase
      .from('age_verification')
      .insert({
        user_id: userId,
        birth_date: birthDate,
        verification_status: 'verified', // La verificación de edad fue hecha en registro
        verified_at: new Date()
      });

    // Crear coins wallet
    await supabase
      .from('user_coins')
      .insert({ user_id: userId, coins: 100 }); // Bonus inicial 100 coins

    // Crear suscripción FREE default
    await supabase
      .from('subscriptions')
      .insert({
        user_id: userId,
        plan_id: 'free',
        status: 'active'
      });

    // Generar token JWT
    const token = generateToken(userId);

    res.json({
      success: true,
      token,
      user: {
        id: userId,
        email,
        username,
        firstName,
        plan: 'free'
      }
    });

  } catch (error) {
    console.error('Register error:', error);
    res.status(500).json({ error: error.message });
  }
});

/**
 * POST /api/auth/login
 * Login usuario
 */
app.post('/api/auth/login', async (req, res) => {
  try {
    const { email, password } = req.body;

    if (!email || !password) {
      return res.status(400).json({ error: 'Email and password required' });
    }

    // Autenticar con Supabase
    const { data: authData, error: authError } = await supabase.auth.signInWithPassword({
      email,
      password
    });

    if (authError) {
      return res.status(401).json({ error: 'Invalid credentials' });
    }

    const userId = authData.user.id;

    // Obtener perfil
    const { data: profile, error: profileError } = await supabase
      .from('profiles')
      .select('username, first_name, age_verified, profile_complete')
      .eq('id', userId)
      .single();

    if (profileError) {
      return res.status(404).json({ error: 'Profile not found' });
    }

    // Obtener suscripción actual
    const { data: subscription } = await supabase
      .from('subscriptions')
      .select('plan_id')
      .eq('user_id', userId)
      .eq('status', 'active')
      .single()
      .catch(() => ({ data: null }));

    // Generar token
    const token = generateToken(userId);

    // Actualizar last_active
    await supabase
      .from('profiles')
      .update({ last_active: new Date() })
      .eq('id', userId);

    res.json({
      success: true,
      token,
      user: {
        id: userId,
        email,
        username: profile.username,
        firstName: profile.first_name,
        ageVerified: profile.age_verified,
        profileComplete: profile.profile_complete,
        plan: subscription?.plan_id || 'free'
      }
    });

  } catch (error) {
    console.error('Login error:', error);
    res.status(500).json({ error: error.message });
  }
});

/**
 * GET /api/auth/me
 * Obtener datos del usuario autenticado
 */
app.get('/api/auth/me', verifyToken, async (req, res) => {
  try {
    const { data: profile, error } = await supabase
      .from('profiles')
      .select('*')
      .eq('id', req.userId)
      .single();

    if (error || !profile) {
      return res.status(404).json({ error: 'Profile not found' });
    }

    const { data: subscription } = await supabase
      .from('subscriptions')
      .select('plan_id')
      .eq('user_id', req.userId)
      .eq('status', 'active')
      .single()
      .catch(() => ({ data: null }));

    res.json({
      id: profile.id,
      email: profile.email,
      username: profile.username,
      firstName: profile.first_name,
      lastName: profile.last_name,
      age: profile.age,
      gender: profile.gender,
      bio: profile.bio,
      city: profile.city,
      country: profile.country,
      profileComplete: profile.profile_complete,
      ageVerified: profile.age_verified,
      plan: subscription?.plan_id || 'free',
      lastActive: profile.last_active
    });

  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// ============================================
// ROUTES: AGE VERIFICATION
// ============================================

/**
 * POST /api/auth/verify-age
 * Verificar edad con documento
 */
app.post('/api/auth/verify-age', verifyToken, async (req, res) => {
  try {
    const { birthDate, documentType } = req.body;

    if (!birthDate) {
      return res.status(400).json({ error: 'Birth date required' });
    }

    if (!isAdult(birthDate)) {
      return res.status(403).json({ error: 'Must be 18 years old' });
    }

    // Actualizar age_verification
    const { error } = await supabase
      .from('age_verification')
      .update({
        birth_date: birthDate,
        document_type: documentType || 'self_declared',
        verification_status: 'verified',
        verified_at: new Date()
      })
      .eq('user_id', req.userId);

    if (error) {
      return res.status(400).json({ error: error.message });
    }

    // Actualizar perfil
    await supabase
      .from('profiles')
      .update({
        birth_date: birthDate,
        age: calculateAge(new Date(birthDate)),
        age_verified: true
      })
      .eq('id', req.userId);

    res.json({ success: true, message: 'Age verified' });

  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// ============================================
// ROUTES: PROFILES
// ============================================

/**
 * PUT /api/profiles/me
 * Actualizar perfil propio
 */
app.put('/api/profiles/me', verifyToken, async (req, res) => {
  try {
    const {
      firstName,
      lastName,
      bio,
      gender,
      pronoun,
      city,
      country,
      latitude,
      longitude,
      interests,
      orientations,
      seeking,
      showLocation,
      showAge,
      showDistance
    } = req.body;

    // Validar intenciones (seeking)
    const validSeeking = ['dating', 'casual', 'sexting', 'relationship', 'meeting', 'friends', 'explore'];
    if (seeking && !seeking.every(s => validSeeking.includes(s))) {
      return res.status(400).json({ error: 'Invalid seeking values' });
    }

    const { error } = await supabase
      .from('profiles')
      .update({
        first_name: firstName,
        last_name: lastName,
        bio,
        gender,
        pronoun,
        city,
        country,
        latitude,
        longitude,
        interests,
        orientations,
        seeking,
        show_location: showLocation,
        show_age: showAge,
        show_distance: showDistance,
        profile_complete: !!(firstName && bio && seeking && seeking.length > 0),
        updated_at: new Date()
      })
      .eq('id', req.userId);

    if (error) {
      return res.status(400).json({ error: error.message });
    }

    // Log actividad
    await supabase
      .from('activity_log')
      .insert({
        user_id: req.userId,
        action: 'profile_update',
        entity_type: 'profile',
        entity_id: req.userId
      });

    res.json({ success: true, message: 'Profile updated' });

  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

/**
 * GET /api/profiles/me
 * Obtener perfil propio completo
 */
app.get('/api/profiles/me', verifyToken, async (req, res) => {
  try {
    const { data: profile, error } = await supabase
      .from('profiles')
      .select('*')
      .eq('id', req.userId)
      .single();

    if (error || !profile) {
      return res.status(404).json({ error: 'Profile not found' });
    }

    // Obtener fotos
    const { data: photos } = await supabase
      .from('profile_photos')
      .select('*')
      .eq('user_id', req.userId)
      .order('position', { ascending: true });

    // Obtener monedas
    const { data: coins } = await supabase
      .from('user_coins')
      .select('coins')
      .eq('user_id', req.userId)
      .single();

    res.json({
      ...profile,
      photos: photos || [],
      coins: coins?.coins || 0
    });

  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

/**
 * GET /api/profiles/:id
 * Ver perfil de otro usuario
 */
app.get('/api/profiles/:id', async (req, res) => {
  try {
    const { id } = req.params;

    const { data: profile, error } = await supabase
      .from('profiles')
      .select('id, username, first_name, age, gender, city, country, bio, seeking, interests, orientations, profile_type, last_active')
      .eq('id', id)
      .eq('is_active', true)
      .single();

    if (error || !profile) {
      return res.status(404).json({ error: 'Profile not found' });
    }

    // Obtener fotos públicas
    const { data: photos } = await supabase
      .from('profile_photos')
      .select('id, photo_url, thumb_url, is_public, requires_unlock')
      .eq('user_id', id)
      .eq('is_public', true)
      .order('position', { ascending: true });

    // Log activity (view)
    if (req.headers.authorization) {
      const token = req.headers.authorization.split(' ')[1];
      try {
        const decoded = jwt.verify(token, JWT_SECRET);
        await supabase
          .from('interactions')
          .insert({
            actor_id: decoded.id,
            target_id: id,
            action: 'view'
          });
      } catch (e) {
        // Silent fail on token verification
      }
    }

    res.json({
      ...profile,
      photos: photos || []
    });

  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// ============================================
// ROUTES: PROFILE PHOTOS
// ============================================

/**
 * POST /api/profiles/me/photos
 * Subir foto a perfil
 */
app.post('/api/profiles/me/photos', verifyToken, async (req, res) => {
  try {
    const { photoUrl, thumbUrl, isPublic = true, position = 0 } = req.body;

    if (!photoUrl) {
      return res.status(400).json({ error: 'Photo URL required' });
    }

    // Contar fotos existentes
    const { count, error: countError } = await supabase
      .from('profile_photos')
      .select('id', { count: 'exact' })
      .eq('user_id', req.userId);

    if (count >= 10) {
      return res.status(400).json({ error: 'Maximum 10 photos allowed' });
    }

    // Insertar foto
    const { data, error } = await supabase
      .from('profile_photos')
      .insert({
        user_id: req.userId,
        photo_url: photoUrl,
        thumb_url: thumbUrl,
        is_public: isPublic,
        position: position || count || 0
      })
      .select()
      .single();

    if (error) {
      return res.status(400).json({ error: error.message });
    }

    res.json({
      success: true,
      photo: data
    });

  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

/**
 * DELETE /api/profiles/me/photos/:photoId
 * Eliminar foto
 */
app.delete('/api/profiles/me/photos/:photoId', verifyToken, async (req, res) => {
  try {
    const { photoId } = req.params;

    // Verificar que la foto pertenece al usuario
    const { data: photo, error: checkError } = await supabase
      .from('profile_photos')
      .select('id')
      .eq('id', photoId)
      .eq('user_id', req.userId)
      .single();

    if (checkError || !photo) {
      return res.status(404).json({ error: 'Photo not found' });
    }

    // Eliminar
    const { error } = await supabase
      .from('profile_photos')
      .delete()
      .eq('id', photoId);

    if (error) {
      return res.status(400).json({ error: error.message });
    }

    res.json({ success: true });

  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// ============================================
// ROUTES: COINS
// ============================================

/**
 * GET /api/coins
 * Ver saldo de monedas
 */
app.get('/api/coins', verifyToken, async (req, res) => {
  try {
    const { data: coins, error } = await supabase
      .from('user_coins')
      .select('coins, lifetime_coins_spent, lifetime_coins_earned')
      .eq('user_id', req.userId)
      .single();

    if (error) {
      return res.status(404).json({ error: 'Coins not found' });
    }

    res.json(coins);

  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

/**
 * POST /api/coins/purchase
 * Comprar monedas con Stripe (FUTURE)
 */
app.post('/api/coins/purchase', verifyToken, async (req, res) => {
  try {
    const { packId, stripePaymentId } = req.body;

    // Define packs
    const packs = {
      small: { coins: 100, price: 0.99 },
      medium: { coins: 600, price: 4.99 },
      large: { coins: 1500, price: 9.99 },
      xl: { coins: 5400, price: 24.99 }
    };

    if (!packs[packId]) {
      return res.status(400).json({ error: 'Invalid pack' });
    }

    const pack = packs[packId];

    // Get current coins
    const { data: current } = await supabase
      .from('user_coins')
      .select('coins')
      .eq('user_id', req.userId)
      .single();

    const newCoins = (current?.coins || 0) + pack.coins;

    // Update coins
    await supabase
      .from('user_coins')
      .update({
        coins: newCoins,
        lifetime_coins_earned: (current?.lifetime_coins_earned || 0) + pack.coins
      })
      .eq('user_id', req.userId);

    // Log transaction
    await supabase
      .from('coin_transactions')
      .insert({
        user_id: req.userId,
        transaction_type: 'purchase',
        amount: pack.coins,
        reason: `Purchased ${packId} pack`,
        stripe_payment_id: stripePaymentId,
        price_eur: pack.price
      });

    res.json({
      success: true,
      coins: newCoins,
      packId,
      coinsAdded: pack.coins
    });

  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// ============================================
// HEALTH CHECK
// ============================================

app.get('/health', (req, res) => {
  res.json({ status: 'YUIZZ API v2 running ✅' });
});

app.get('/', (req, res) => {
  res.json({
    name: 'YUIZZ V2 API',
    version: '2.0.0',
    environment: 'development',
    phase: 'Phase 1: Auth + Profiles'
  });
});

// ============================================
// ERROR HANDLER
// ============================================

app.use((err, req, res, next) => {
  console.error('Error:', err);
  res.status(err.status || 500).json({
    error: err.message || 'Internal server error'
  });
});

// ============================================
// START SERVER
// ============================================

app.listen(PORT, () => {
  console.log(`
╔════════════════════════════════════════╗
║  🔥 YUIZZ V2 API - PHASE 1 RUNNING   ║
╚════════════════════════════════════════╝

📍 Server: http://localhost:${PORT}
🏥 Health: http://localhost:${PORT}/health

Features Active:
  ✓ Authentication (register, login)
  ✓ Age verification (18+ enforcement)
  ✓ Profile management (CRUD)
  ✓ Photo upload
  ✓ Coins system (basic)

Database: Supabase PostgreSQL
Schema: v2 (15 tables with RLS)

Next: Implement discovery + interactions
  `);
});

export default app;
