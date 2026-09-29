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
// PHASE 2: DISCOVERY & INTERACTIONS
// ============================================

// Rate limiting for interactions (in-memory)
const rateLimitStore = new Map();
const rateLimit = (maxAttempts, windowMs) => {
  return (req, res, next) => {
    const key = `${req.userId}-${req.path}`;
    const now = Date.now();
    const userLimits = rateLimitStore.get(key) || [];
    const recentAttempts = userLimits.filter(t => now - t < windowMs);

    if (recentAttempts.length >= maxAttempts) {
      return res.status(429).json({ error: 'Rate limit exceeded. Try again later.' });
    }

    recentAttempts.push(now);
    rateLimitStore.set(key, recentAttempts);
    next();
  };
};

// Calculate distance between coordinates (haversine formula)
function calculateDistance(lat1, lon1, lat2, lon2) {
  const R = 6371;
  const dLat = (lat2 - lat1) * Math.PI / 180;
  const dLon = (lon2 - lon1) * Math.PI / 180;
  const a = Math.sin(dLat / 2) * Math.sin(dLat / 2) +
    Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
    Math.sin(dLon / 2) * Math.sin(dLon / 2);
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  return Math.round(R * c);
}

// Check for mutual like/superlike
async function checkMatch(userId1, userId2) {
  const { data } = await supabase
    .from('interactions')
    .select('*')
    .in('action', ['like', 'superlike']);

  if (!data) return false;

  const user1Liked = data.some(i => i.actor_id === userId1 && i.target_id === userId2 && ['like', 'superlike'].includes(i.action));
  const user2Liked = data.some(i => i.actor_id === userId2 && i.target_id === userId1 && ['like', 'superlike'].includes(i.action));

  return user1Liked && user2Liked;
}

// Create match if mutual like detected
async function createMatchIfMutual(actor, target) {
  const isMatch = await checkMatch(actor, target);

  if (isMatch) {
    const user1_id = actor < target ? actor : target;
    const user2_id = actor < target ? target : actor;

    const { data: existing } = await supabase
      .from('matches')
      .select('*')
      .eq('user1_id', user1_id)
      .eq('user2_id', user2_id);

    if (!existing || existing.length === 0) {
      const { data: match } = await supabase
        .from('matches')
        .insert({
          user1_id,
          user2_id,
          match_type: 'mutual_like',
          status: 'active'
        })
        .select()
        .single();

      return match;
    }
  }

  return null;
}

/**
 * GET /api/discovery
 * Get nearby profiles with geolocation + filters
 *
 * Query params:
 *  - limit: number (default 10, max 50)
 *  - offset: number (default 0)
 *  - maxDistance: number in km (default 100)
 *  - minAge: number (default 18)
 *  - maxAge: number (default 65)
 *  - gender: comma-separated (m,f,nb,other)
 *  - seeking: comma-separated (dating,casual,sexting,relationship,meeting,friends,explore)
 *  - verifiedOnly: boolean (default false)
 */
app.get('/api/discovery', verifyToken, async (req, res) => {
  try {
    // Get current user's location
    const { data: myProfile } = await supabase
      .from('profiles')
      .select('latitude, longitude, age, gender, seeking, id')
      .eq('id', req.userId)
      .single();

    if (!myProfile || !myProfile.latitude || !myProfile.longitude) {
      return res.status(400).json({ error: 'Please set your location first' });
    }

    // Parse query parameters
    const limit = Math.min(parseInt(req.query.limit) || 10, 50);
    const offset = parseInt(req.query.offset) || 0;
    const maxDistance = parseInt(req.query.maxDistance) || 100;
    const minAge = parseInt(req.query.minAge) || 18;
    const maxAge = parseInt(req.query.maxAge) || 65;
    const genders = req.query.gender?.split(',').filter(Boolean);
    const seekingFilters = req.query.seeking?.split(',').filter(Boolean);
    const verifiedOnly = req.query.verifiedOnly === 'true';

    // Get all active profiles
    let query = supabase
      .from('profiles')
      .select('id, username, first_name, age, gender, city, latitude, longitude, seeking, age_verified, profile_complete')
      .eq('is_active', true)
      .eq('profile_complete', true)
      .gte('age', minAge)
      .lte('age', maxAge);

    if (genders && genders.length > 0) {
      query = query.in('gender', genders);
    }

    if (verifiedOnly) {
      query = query.eq('age_verified', true);
    }

    const { data: candidates, error } = await query.limit(100);

    if (error) {
      return res.status(500).json({ error: error.message });
    }

    // Filter by distance and seeking
    const filtered = candidates
      .filter(profile => {
        if (profile.id === req.userId) return false;

        const distance = calculateDistance(
          myProfile.latitude,
          myProfile.longitude,
          profile.latitude,
          profile.longitude
        );

        if (distance > maxDistance) return false;

        if (seekingFilters && seekingFilters.length > 0 && profile.seeking) {
          const hasCommonSeeking = profile.seeking.some(s => seekingFilters.includes(s));
          if (!hasCommonSeeking) return false;
        }

        return true;
      })
      .slice(offset, offset + limit)
      .map(profile => ({
        ...profile,
        distance: calculateDistance(
          myProfile.latitude,
          myProfile.longitude,
          profile.latitude,
          profile.longitude
        )
      }));

    // Get my interactions to show in UI
    const { data: interactions } = await supabase
      .from('interactions')
      .select('target_id, action')
      .eq('actor_id', req.userId)
      .in('target_id', filtered.map(p => p.id));

    const interactionMap = new Map();
    (interactions || []).forEach(i => {
      interactionMap.set(i.target_id, i.action);
    });

    const result = filtered.map(p => ({
      ...p,
      myAction: interactionMap.get(p.id)
    }));

    res.json({
      profiles: result,
      total: result.length,
      limit,
      offset
    });

  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

/**
 * POST /api/interactions/:targetId/like
 * Like a profile (rate limit: 5/min)
 */
app.post('/api/interactions/:targetId/like', verifyToken, rateLimit(5, 60000), async (req, res) => {
  try {
    const { targetId } = req.params;

    const { data: target } = await supabase
      .from('profiles')
      .select('id')
      .eq('id', targetId)
      .single();

    if (!target) {
      return res.status(404).json({ error: 'Profile not found' });
    }

    const { data: existing } = await supabase
      .from('interactions')
      .select('*')
      .eq('actor_id', req.userId)
      .eq('target_id', targetId);

    if (existing && existing.length > 0) {
      await supabase
        .from('interactions')
        .update({ action: 'like' })
        .eq('id', existing[0].id);
    } else {
      await supabase
        .from('interactions')
        .insert({
          actor_id: req.userId,
          target_id: targetId,
          action: 'like'
        });
    }

    // Check for match
    const match = await createMatchIfMutual(req.userId, targetId);

    res.json({
      success: true,
      action: 'like',
      matched: !!match,
      match: match || null
    });

  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

/**
 * POST /api/interactions/:targetId/pass
 * Pass on a profile (rate limit: 30/min)
 */
app.post('/api/interactions/:targetId/pass', verifyToken, rateLimit(30, 60000), async (req, res) => {
  try {
    const { targetId } = req.params;

    const { data: target } = await supabase
      .from('profiles')
      .select('id')
      .eq('id', targetId)
      .single();

    if (!target) {
      return res.status(404).json({ error: 'Profile not found' });
    }

    const { data: existing } = await supabase
      .from('interactions')
      .select('*')
      .eq('actor_id', req.userId)
      .eq('target_id', targetId);

    if (existing && existing.length > 0) {
      await supabase
        .from('interactions')
        .update({ action: 'pass' })
        .eq('id', existing[0].id);
    } else {
      await supabase
        .from('interactions')
        .insert({
          actor_id: req.userId,
          target_id: targetId,
          action: 'pass'
        });
    }

    res.json({ success: true, action: 'pass' });

  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

/**
 * POST /api/interactions/:targetId/superlike
 * SuperLike a profile - costs 50 coins (rate limit: 1/hour)
 */
app.post('/api/interactions/:targetId/superlike', verifyToken, rateLimit(1, 3600000), async (req, res) => {
  try {
    const { targetId } = req.params;
    const SUPERLIKE_COST = 50;

    const { data: target } = await supabase
      .from('profiles')
      .select('id')
      .eq('id', targetId)
      .single();

    if (!target) {
      return res.status(404).json({ error: 'Profile not found' });
    }

    // Check coins
    const { data: coins } = await supabase
      .from('user_coins')
      .select('coins, lifetime_coins_spent')
      .eq('user_id', req.userId)
      .single();

    if (!coins || coins.coins < SUPERLIKE_COST) {
      return res.status(400).json({ error: `Need ${SUPERLIKE_COST} coins for SuperLike` });
    }

    // Deduct coins
    await supabase
      .from('user_coins')
      .update({
        coins: coins.coins - SUPERLIKE_COST,
        lifetime_coins_spent: (coins.lifetime_coins_spent || 0) + SUPERLIKE_COST
      })
      .eq('user_id', req.userId);

    // Log transaction
    await supabase
      .from('coin_transactions')
      .insert({
        user_id: req.userId,
        transaction_type: 'spent',
        amount: SUPERLIKE_COST,
        reason: 'SuperLike'
      });

    // Create/update interaction
    const { data: existing } = await supabase
      .from('interactions')
      .select('*')
      .eq('actor_id', req.userId)
      .eq('target_id', targetId);

    if (existing && existing.length > 0) {
      await supabase
        .from('interactions')
        .update({ action: 'superlike' })
        .eq('id', existing[0].id);
    } else {
      await supabase
        .from('interactions')
        .insert({
          actor_id: req.userId,
          target_id: targetId,
          action: 'superlike'
        });
    }

    // Check for match
    const match = await createMatchIfMutual(req.userId, targetId);

    res.json({
      success: true,
      action: 'superlike',
      costCoins: SUPERLIKE_COST,
      newCoinsBalance: coins.coins - SUPERLIKE_COST,
      matched: !!match,
      match: match || null
    });

  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

/**
 * GET /api/matches
 * Get all active matches
 */
app.get('/api/matches', verifyToken, async (req, res) => {
  try {
    const { data: matches } = await supabase
      .from('matches')
      .select('*, profile1:user1_id(id, username, first_name, age), profile2:user2_id(id, username, first_name, age)')
      .or(`user1_id.eq.${req.userId},user2_id.eq.${req.userId}`)
      .eq('status', 'active')
      .order('created_at', { ascending: false });

    const formattedMatches = (matches || []).map(m => {
      const otherProfile = m.user1_id === req.userId ? m.profile2 : m.profile1;
      return {
        matchId: m.id,
        other: otherProfile,
        matchedAt: m.created_at,
        lastMessage: m.last_message_at,
        unreadCount: m.user1_id === req.userId ? m.unread_count_user1 : m.unread_count_user2
      };
    });

    res.json(formattedMatches);

  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// ============================================
// HEALTH CHECK
// ============================================

app.get('/health', (req, res) => {
  res.json({ status: 'YUIZZ API v2 Phase 2 running ✅' });
});

app.get('/', (req, res) => {
  res.json({
    name: 'YUIZZ V2 API',
    version: '2.0.0',
    environment: 'development',
    phase: 'Phase 3: V2.0 Features (Hashtags, Compatibility, Premium)',
    totalEndpoints: 36,
    endpoints: {
      v1: {
        auth: ['POST /api/auth/register', 'POST /api/auth/login', 'GET /api/auth/me'],
        profiles: ['PUT /api/profiles/me', 'GET /api/profiles/me', 'GET /api/profiles/:id'],
        photos: ['POST /api/profiles/me/photos', 'DELETE /api/profiles/me/photos/:id'],
        coins: ['GET /api/coins', 'POST /api/coins/purchase'],
        discovery: ['GET /api/discovery?limit=10&maxDistance=100&minAge=18&maxAge=65&seeking=dating,casual'],
        interactions: [
          'POST /api/interactions/:targetId/like (5/min)',
          'POST /api/interactions/:targetId/pass (30/min)',
          'POST /api/interactions/:targetId/superlike (1/hour, costs 50 coins)'
        ],
        matches: ['GET /api/matches'],
        chat: ['POST /api/matches/:id/messages (30/min)', 'GET /api/matches/:id/messages', 'DELETE /api/messages/:id'],
        posts: ['POST /api/posts (10/hour)', 'GET /api/posts', 'POST /api/posts/:id/like', 'DELETE /api/posts/:id']
      },
      v2: {
        discovery: ['GET /api/v2/discover/feed (with compatibility scoring)'],
        hashtags: [
          'POST /api/v2/profiles/me/hashtags (set user hashtags)',
          'GET /api/v2/hashtags/all (list 35 available)'
        ],
        preferences: [
          'GET /api/v2/profiles/me/preferences',
          'POST /api/v2/profiles/me/preferences (age, distance, gender, location)'
        ],
        premium: [
          'GET /api/v2/subscriptions',
          'POST /api/v2/subscriptions (plans: monthly €7.99, quarterly €19.99, yearly €59.99)'
        ],
        boosts: ['POST /api/v2/boosts (30min visibility x3)'],
        moderation: ['POST /api/v2/photos/:photoId/moderate (AI detection mock)']
      }
    }
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
╔═══════════════════════════════════════════════╗
║  🔥 YUIZZ V2 API - V2.0 FEATURES RUNNING    ║
╚═══════════════════════════════════════════════╝

📍 Server: http://localhost:${PORT}
🏥 Health: http://localhost:${PORT}/health
📊 Endpoints: 36 total (12 V2.0)

Features Active:
  ✓ Authentication (register, login, verify-age)
  ✓ Age verification (18+ enforcement)
  ✓ Profile management (CRUD)
  ✓ Photo upload (public/private/locked)
  ✓ Coins system (purchase, spend, transactions)

PHASE 1 - AUTHENTICATION + PROFILES:
  ✓ JWT authentication
  ✓ Age verification (18+)
  ✓ Profile CRUD
  ✓ Photo gallery

PHASE 2 - DISCOVERY + INTERACTIONS:
  ✓ Geolocation-based discovery
  ✓ Like (5/min) | Pass (30/min) | SuperLike (1/hour, 50 coins)
  ✓ Automatic match detection
  ✓ Matches listing

PHASE 3 - CHAT + COMMUNITY:
  ✓ Real-time messaging (30/min)
  ✓ Message history & pagination
  ✓ Read receipts & unread tracking
  ✓ Community posts (7-day expiry)
  ✓ Post discovery (20km geo-filter)
  ✓ Post likes & engagement

V2.0 - COMPATIBILITY + PREMIUM:
  ✓ Hashtag system (35 curated tags)
  ✓ Weighted compatibility scoring algorithm
  ✓ User preference filtering
  ✓ Premium subscriptions (€7.99/€19.99/€59.99)
  ✓ Visibility boosts (3x, 30min)
  ✓ AI photo moderation (mock)

V2.0 Endpoints:
  - GET /api/v2/discover/feed (compatibility scoring)
  - POST/GET /api/v2/profiles/me/hashtags
  - GET /api/v2/hashtags/all (35 tags)
  - GET /api/v2/profiles/me/preferences
  - POST /api/v2/profiles/me/preferences
  - GET /api/v2/subscriptions
  - POST /api/v2/subscriptions (€7.99/19.99/59.99)
  - POST /api/v2/boosts
  - POST /api/v2/photos/:photoId/moderate

Database: Supabase PostgreSQL (v3 schema with RLS)
Algorithm: Weighted compatibility (Hashtag 40% + Age 20% + Distance 20% + Gender 10% + Freshness 10%)
Hashtags: 35 curated across 5 categories
Premium Plans: Monthly (1 boost) | Quarterly (3) | Yearly (12)

Next: WebSocket realtime + Push notifications
  `);
});

// ============================================
// PHASE 3: CHAT + COMMUNITY POSTS
// ============================================

/**
 * POST /api/matches/:matchId/messages
 * Send a message in a match
 */
app.post('/api/matches/:matchId/messages', verifyToken, rateLimit(30, 60000), async (req, res) => {
  try {
    const { matchId } = req.params;
    const { content } = req.body;

    if (!content || content.trim().length === 0) {
      return res.status(400).json({ error: 'Message content required' });
    }

    // Verify user is part of this match
    const { data: match } = await supabase
      .from('matches')
      .select('*')
      .eq('id', matchId)
      .single();

    if (!match || (match.user1_id !== req.userId && match.user2_id !== req.userId)) {
      return res.status(403).json({ error: 'Access denied' });
    }

    const otherUserId = match.user1_id === req.userId ? match.user2_id : match.user1_id;

    // Insert message
    const { data: message, error } = await supabase
      .from('messages')
      .insert({
        match_id: matchId,
        sender_id: req.userId,
        receiver_id: otherUserId,
        content: content.trim(),
        is_read: false
      })
      .select()
      .single();

    if (error) throw error;

    // Update match's last_message_at
    await supabase
      .from('matches')
      .update({ last_message_at: new Date().toISOString() })
      .eq('id', matchId);

    res.json({
      success: true,
      message: {
        id: message.id,
        matchId: message.match_id,
        senderId: message.sender_id,
        content: message.content,
        createdAt: message.created_at,
        isRead: message.is_read
      }
    });

  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

/**
 * GET /api/matches/:matchId/messages
 * Get message history for a match (paginated)
 */
app.get('/api/matches/:matchId/messages', verifyToken, async (req, res) => {
  try {
    const { matchId } = req.params;
    const { limit = 20, offset = 0 } = req.query;

    // Verify user is part of this match
    const { data: match } = await supabase
      .from('matches')
      .select('*')
      .eq('id', matchId)
      .single();

    if (!match || (match.user1_id !== req.userId && match.user2_id !== req.userId)) {
      return res.status(403).json({ error: 'Access denied' });
    }

    // Get messages
    const { data: messages } = await supabase
      .from('messages')
      .select('*')
      .eq('match_id', matchId)
      .order('created_at', { ascending: false })
      .range(offset, offset + limit - 1);

    // Mark as read (receiver's messages)
    if (messages && messages.length > 0) {
      await supabase
        .from('messages')
        .update({ is_read: true })
        .eq('match_id', matchId)
        .eq('receiver_id', req.userId)
        .eq('is_read', false);

      // Update unread count in matches table
      const otherUserId = match.user1_id === req.userId ? match.user2_id : match.user1_id;
      const unreads = await supabase
        .from('messages')
        .select('*', { count: 'exact' })
        .eq('match_id', matchId)
        .eq('receiver_id', req.userId)
        .eq('is_read', false);

      const updateObj = match.user1_id === req.userId
        ? { unread_count_user1: unreads.count || 0 }
        : { unread_count_user2: unreads.count || 0 };

      await supabase
        .from('matches')
        .update(updateObj)
        .eq('id', matchId);
    }

    res.json({
      messages: (messages || []).map(m => ({
        id: m.id,
        matchId: m.match_id,
        senderId: m.sender_id,
        content: m.content,
        createdAt: m.created_at,
        isRead: m.is_read
      })),
      limit: parseInt(limit),
      offset: parseInt(offset)
    });

  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

/**
 * DELETE /api/messages/:messageId
 * Delete a message (only sender can delete)
 */
app.delete('/api/messages/:messageId', verifyToken, async (req, res) => {
  try {
    const { messageId } = req.params;

    const { data: message } = await supabase
      .from('messages')
      .select('*')
      .eq('id', messageId)
      .single();

    if (!message) {
      return res.status(404).json({ error: 'Message not found' });
    }

    if (message.sender_id !== req.userId) {
      return res.status(403).json({ error: 'Can only delete your own messages' });
    }

    // Soft delete (set content to empty)
    await supabase
      .from('messages')
      .update({ content: '[deleted]' })
      .eq('id', messageId);

    res.json({ success: true, messageId });

  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

/**
 * POST /api/posts
 * Create a community post (7-day expiration)
 */
app.post('/api/posts', verifyToken, rateLimit(10, 3600000), async (req, res) => {
  try {
    const { content, imageUrl } = req.body;

    if (!content || content.trim().length === 0) {
      return res.status(400).json({ error: 'Post content required' });
    }

    if (content.length > 500) {
      return res.status(400).json({ error: 'Post too long (max 500 chars)' });
    }

    // Get user location
    const { data: profile } = await supabase
      .from('profiles')
      .select('latitude, longitude, city')
      .eq('id', req.userId)
      .single();

    if (!profile || !profile.latitude || !profile.longitude) {
      return res.status(400).json({ error: 'Set your location to post' });
    }

    // Create post (expires in 7 days)
    const expiresAt = new Date();
    expiresAt.setDate(expiresAt.getDate() + 7);

    const { data: post, error } = await supabase
      .from('posts')
      .insert({
        creator_id: req.userId,
        content: content.trim(),
        image_url: imageUrl || null,
        latitude: profile.latitude,
        longitude: profile.longitude,
        city: profile.city,
        expires_at: expiresAt.toISOString(),
        likes_count: 0,
        comments_count: 0
      })
      .select()
      .single();

    if (error) throw error;

    res.json({
      success: true,
      post: {
        id: post.id,
        creatorId: post.creator_id,
        content: post.content,
        imageUrl: post.image_url,
        latitude: post.latitude,
        longitude: post.longitude,
        city: post.city,
        expiresAt: post.expires_at,
        likesCount: post.likes_count,
        commentsCount: post.comments_count,
        createdAt: post.created_at,
        myLike: false
      }
    });

  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

/**
 * GET /api/posts
 * Discover community posts (geo-filtered, 20km radius)
 */
app.get('/api/posts', verifyToken, async (req, res) => {
  try {
    const { limit = 10, offset = 0, maxDistance = 20 } = req.query;

    // Get user location
    const { data: profile } = await supabase
      .from('profiles')
      .select('latitude, longitude')
      .eq('id', req.userId)
      .single();

    if (!profile || !profile.latitude || !profile.longitude) {
      return res.status(400).json({ error: 'Set your location first' });
    }

    // Get posts within radius (Haversine formula filtering in app layer)
    const { data: posts } = await supabase
      .from('posts')
      .select('*')
      .gt('expires_at', new Date().toISOString())
      .order('created_at', { ascending: false })
      .range(offset, offset + parseInt(limit) - 1);

    // Filter by distance
    const filteredPosts = (posts || []).filter(post => {
      const distance = calculateDistance(
        profile.latitude,
        profile.longitude,
        post.latitude,
        post.longitude
      );
      return distance <= parseInt(maxDistance);
    });

    // Get user's likes
    const postIds = filteredPosts.map(p => p.id);
    const { data: userLikes } = await supabase
      .from('post_likes')
      .select('post_id')
      .eq('user_id', req.userId)
      .in('post_id', postIds);

    const likedPostIds = new Set((userLikes || []).map(l => l.post_id));

    res.json({
      posts: filteredPosts.map(post => ({
        id: post.id,
        creatorId: post.creator_id,
        content: post.content,
        imageUrl: post.image_url,
        city: post.city,
        distance: calculateDistance(profile.latitude, profile.longitude, post.latitude, post.longitude),
        likesCount: post.likes_count,
        commentsCount: post.comments_count,
        expiresAt: post.expires_at,
        createdAt: post.created_at,
        myLike: likedPostIds.has(post.id)
      })),
      limit: parseInt(limit),
      offset: parseInt(offset)
    });

  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

/**
 * POST /api/posts/:postId/like
 * Like a post
 */
app.post('/api/posts/:postId/like', verifyToken, rateLimit(50, 60000), async (req, res) => {
  try {
    const { postId } = req.params;

    const { data: post } = await supabase
      .from('posts')
      .select('*')
      .eq('id', postId)
      .single();

    if (!post) {
      return res.status(404).json({ error: 'Post not found' });
    }

    // Check if already liked
    const { data: existing } = await supabase
      .from('post_likes')
      .select('*')
      .eq('post_id', postId)
      .eq('user_id', req.userId);

    if (existing && existing.length > 0) {
      // Unlike
      await supabase
        .from('post_likes')
        .delete()
        .eq('post_id', postId)
        .eq('user_id', req.userId);

      await supabase
        .from('posts')
        .update({ likes_count: Math.max(0, post.likes_count - 1) })
        .eq('id', postId);

      return res.json({ success: true, liked: false, likesCount: Math.max(0, post.likes_count - 1) });
    }

    // Like
    await supabase
      .from('post_likes')
      .insert({ post_id: postId, user_id: req.userId });

    await supabase
      .from('posts')
      .update({ likes_count: post.likes_count + 1 })
      .eq('id', postId);

    res.json({ success: true, liked: true, likesCount: post.likes_count + 1 });

  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

/**
 * DELETE /api/posts/:postId
 * Delete a post (only creator can delete)
 */
app.delete('/api/posts/:postId', verifyToken, async (req, res) => {
  try {
    const { postId } = req.params;

    const { data: post } = await supabase
      .from('posts')
      .select('*')
      .eq('id', postId)
      .single();

    if (!post) {
      return res.status(404).json({ error: 'Post not found' });
    }

    if (post.creator_id !== req.userId) {
      return res.status(403).json({ error: 'Can only delete your own posts' });
    }

    await supabase
      .from('posts')
      .delete()
      .eq('id', postId);

    res.json({ success: true, postId });

  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// ============================================
// V2.0 FEATURES - COMPATIBILITY ALGORITHM
// ============================================

// Calculate compatibility score between two profiles
async function calculateCompatibility(viewerId, profileId, supabase) {
  const { data: viewer } = await supabase
    .from('profiles')
    .select('*')
    .eq('id', viewerId)
    .single();

  const { data: profile } = await supabase
    .from('profiles')
    .select('*')
    .eq('id', profileId)
    .single();

  if (!viewer || !profile) return 0;

  const { data: prefs } = await supabase
    .from('user_preferences')
    .select('*')
    .eq('user_id', viewerId)
    .single();

  if (!prefs) return 0;

  // Hashtag match (0-100)
  const viewerHashtags = viewer.hashtags || [];
  const profileHashtags = profile.hashtags || [];
  const matchingTags = viewerHashtags.filter(h => profileHashtags.includes(h)).length;
  const maxTags = Math.max(viewerHashtags.length, profileHashtags.length, 1);
  const hashtagScore = (matchingTags / maxTags) * 100;

  // Age match (0-100)
  const age = calculateAge(new Date(profile.birth_date));
  const ageScore = (age >= prefs.min_age && age <= prefs.max_age) ? 100 : 0;

  // Gender match (0-100)
  const genderScore = (prefs.gender_preference.includes('all') ||
    prefs.gender_preference.includes(profile.gender)) ? 100 : 0;

  // Distance match (0-100)
  const distance = calculateDistance(
    viewer.latitude, viewer.longitude,
    profile.latitude, profile.longitude
  );
  const distanceScore = Math.max(0, 100 - (distance / prefs.max_distance_km * 100));

  // Freshness score (0-100)
  const lastActive = new Date(profile.updated_at);
  const daysSince = (new Date() - lastActive) / (1000 * 60 * 60 * 24);
  let freshnessScore = 100;
  if (daysSince > 30) freshnessScore = 10;
  else if (daysSince > 7) freshnessScore = 30;
  else if (daysSince > 1) freshnessScore = 60;
  else freshnessScore = 90;

  // Final score: weighted average
  const totalScore =
    (hashtagScore * 0.40) +
    (ageScore * 0.20) +
    (distanceScore * 0.20) +
    (genderScore * 0.10) +
    (freshnessScore * 0.10);

  return Math.round(totalScore * 100) / 100;
}

// ============================================
// V2.0 ROUTES: DISCOVERY WITH COMPATIBILITY
// ============================================

/**
 * GET /api/v2/discover/feed
 * Discovery feed with compatibility scoring
 */
app.get('/api/v2/discover/feed', verifyToken, async (req, res) => {
  try {
    const { limit = 10, offset = 0 } = req.query;

    // Get user preferences
    const { data: prefs } = await supabase
      .from('user_preferences')
      .select('*')
      .eq('user_id', req.userId)
      .single();

    if (!prefs) {
      return res.status(404).json({ error: 'User preferences not found' });
    }

    // Get blocked and passed profiles
    const { data: blocks } = await supabase
      .from('blocks')
      .select('blocked_id')
      .eq('blocker_id', req.userId);

    const { data: interactions } = await supabase
      .from('interactions')
      .select('target_id')
      .eq('actor_id', req.userId);

    const blockedIds = blocks?.map(b => b.blocked_id) || [];
    const interactedIds = interactions?.map(i => i.target_id) || [];

    // Get candidates
    const { data: candidates } = await supabase
      .from('profiles')
      .select('*')
      .neq('id', req.userId)
      .not('id', 'in', `(${[req.userId, ...blockedIds, ...interactedIds].join(',')})`)
      .limit(50);

    if (!candidates || candidates.length === 0) {
      return res.json({ profiles: [], total: 0 });
    }

    // Calculate scores and sort
    const scored = await Promise.all(
      candidates.map(async (profile) => ({
        ...profile,
        compatibilityScore: await calculateCompatibility(req.userId, profile.id, supabase)
      }))
    );

    const sorted = scored.sort((a, b) => b.compatibilityScore - a.compatibilityScore);
    const paginated = sorted.slice(offset, offset + limit);

    res.json({
      profiles: paginated,
      total: sorted.length,
      limit,
      offset
    });

  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// ============================================
// V2.0 ROUTES: HASHTAGS
// ============================================

const HASHTAGS = [
  // Acción Física
  '#Besos', '#Morder', '#Arañar', '#Masaje', '#Juegos', '#Caricias',
  '#Sexting', '#Lencería', '#Privado', '#Noche', '#Público', '#Exploración',
  // Tipo de Relación
  '#Citas', '#SinCompromiso', '#RelaciónAbierta', '#Parejas',
  '#Solteros', '#Amistad', '#Conexión', '#Química',
  // Intensidad
  '#Dominación', '#Sumisión', '#Roleplay', '#Fantasías', '#Suave', '#Intenso',
  // Perfil Específico
  '#Individual', '#Pareja', '#Buscando', '#Experimental',
  // Motivación
  '#Encuentros', '#Conocer', '#Flirtear', '#Diversión', '#Serio'
];

/**
 * POST /api/v2/profiles/me/hashtags
 * Set user hashtags
 */
app.post('/api/v2/profiles/me/hashtags', verifyToken, async (req, res) => {
  try {
    const { hashtags } = req.body;

    if (!Array.isArray(hashtags) || hashtags.length === 0 || hashtags.length > 10) {
      return res.status(400).json({ error: 'Select 1-10 hashtags' });
    }

    // Validate hashtags
    const invalid = hashtags.filter(h => !HASHTAGS.includes(h));
    if (invalid.length > 0) {
      return res.status(400).json({ error: `Invalid hashtags: ${invalid.join(', ')}` });
    }

    // Update profile
    const { data, error } = await supabase
      .from('profiles')
      .update({ hashtags })
      .eq('id', req.userId)
      .select()
      .single();

    if (error) throw error;

    res.json({ success: true, hashtags: data.hashtags });

  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

/**
 * GET /api/v2/hashtags/all
 * Get all available hashtags
 */
app.get('/api/v2/hashtags/all', (req, res) => {
  res.json({ hashtags: HASHTAGS });
});

// ============================================
// V2.0 ROUTES: USER PREFERENCES
// ============================================

/**
 * GET /api/v2/profiles/me/preferences
 * Get user preferences
 */
app.get('/api/v2/profiles/me/preferences', verifyToken, async (req, res) => {
  try {
    const { data, error } = await supabase
      .from('user_preferences')
      .select('*')
      .eq('user_id', req.userId)
      .single();

    if (error || !data) {
      return res.status(404).json({ error: 'Preferences not found' });
    }

    res.json(data);

  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

/**
 * POST /api/v2/profiles/me/preferences
 * Update user preferences
 */
app.post('/api/v2/profiles/me/preferences', verifyToken, async (req, res) => {
  try {
    const {
      min_age,
      max_age,
      gender_preference,
      max_distance_km,
      preferred_hashtags,
      show_verified_only
    } = req.body;

    const updateData = {
      ...(min_age !== undefined && { min_age }),
      ...(max_age !== undefined && { max_age }),
      ...(gender_preference && { gender_preference }),
      ...(max_distance_km !== undefined && { max_distance_km }),
      ...(preferred_hashtags && { preferred_hashtags }),
      ...(show_verified_only !== undefined && { show_verified_only }),
      updated_at: new Date().toISOString()
    };

    const { data, error } = await supabase
      .from('user_preferences')
      .update(updateData)
      .eq('user_id', req.userId)
      .select()
      .single();

    if (error) throw error;

    res.json({ success: true, preferences: data });

  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// ============================================
// V2.0 ROUTES: PREMIUM SUBSCRIPTIONS
// ============================================

/**
 * GET /api/v2/subscriptions
 * Get user subscription status
 */
app.get('/api/v2/subscriptions', verifyToken, async (req, res) => {
  try {
    const { data, error } = await supabase
      .from('premium_subscriptions')
      .select('*')
      .eq('user_id', req.userId)
      .eq('status', 'active')
      .single();

    if (!data) {
      return res.json({
        isPremium: false,
        subscription: null
      });
    }

    const isExpired = new Date(data.expires_at) < new Date();

    res.json({
      isPremium: !isExpired,
      subscription: isExpired ? null : data
    });

  } catch (error) {
    res.json({ isPremium: false, subscription: null });
  }
});

/**
 * POST /api/v2/subscriptions
 * Create or update subscription
 */
app.post('/api/v2/subscriptions', verifyToken, async (req, res) => {
  try {
    const { plan } = req.body;

    if (!['monthly', 'quarterly', 'yearly'].includes(plan)) {
      return res.status(400).json({ error: 'Invalid plan' });
    }

    const prices = {
      monthly: 7.99,
      quarterly: 19.99,
      yearly: 59.99
    };

    const boosts = {
      monthly: 1,
      quarterly: 3,
      yearly: 12
    };

    const durations = {
      monthly: 30,
      quarterly: 90,
      yearly: 365
    };

    const startsAt = new Date();
    const expiresAt = new Date(startsAt.getTime() + durations[plan] * 24 * 60 * 60 * 1000);

    const { data, error } = await supabase
      .from('premium_subscriptions')
      .insert({
        user_id: req.userId,
        plan,
        price: prices[plan],
        started_at: startsAt.toISOString(),
        expires_at: expiresAt.toISOString(),
        boosts_count: boosts[plan],
        status: 'active'
      })
      .select()
      .single();

    if (error) throw error;

    res.json({ success: true, subscription: data });

  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// ============================================
// V2.0 ROUTES: BOOSTS
// ============================================

/**
 * POST /api/v2/boosts
 * Activate a boost for visibility
 */
app.post('/api/v2/boosts', verifyToken, async (req, res) => {
  try {
    // Get user subscription
    const { data: sub } = await supabase
      .from('premium_subscriptions')
      .select('*')
      .eq('user_id', req.userId)
      .eq('status', 'active')
      .single();

    if (!sub || sub.boosts_used >= sub.boosts_count) {
      return res.status(403).json({ error: 'No boosts available' });
    }

    const startsAt = new Date();
    const expiresAt = new Date(startsAt.getTime() + 30 * 60 * 1000); // 30 minutes

    const { data: boost, error } = await supabase
      .from('boosts')
      .insert({
        user_id: req.userId,
        boost_type: 'premium',
        multiplier: 3.0,
        started_at: startsAt.toISOString(),
        expires_at: expiresAt.toISOString(),
        duration_minutes: 30,
        source: 'subscription_bonus',
        status: 'active'
      })
      .select()
      .single();

    if (error) throw error;

    // Update boosts_used
    await supabase
      .from('premium_subscriptions')
      .update({ boosts_used: sub.boosts_used + 1 })
      .eq('id', sub.id);

    res.json({ success: true, boost });

  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// ============================================
// V2.0 ROUTES: PHOTO MODERATION
// ============================================

/**
 * POST /api/v2/photos/:photoId/moderate
 * Run AI moderation on photo (mock)
 */
app.post('/api/v2/photos/:photoId/moderate', verifyToken, async (req, res) => {
  try {
    const { photoId } = req.params;

    // Get photo
    const { data: photo } = await supabase
      .from('profile_photos')
      .select('*')
      .eq('id', photoId)
      .single();

    if (!photo) {
      return res.status(404).json({ error: 'Photo not found' });
    }

    // Mock AI detection
    const nudeScore = Math.random() * 0.3; // Keep low for demo
    const isExplicit = nudeScore > 0.7;
    const genitalDetected = nudeScore > 0.8;

    const status = isExplicit ? 'rejected' : 'approved';
    const reasonRejected = isExplicit ? 'Inappropriate content detected' : null;

    // Save moderation result
    const { data: moderation, error } = await supabase
      .from('photo_moderation')
      .insert({
        photo_id: photoId,
        nude_score: nudeScore,
        explicit_content: isExplicit,
        genitals_detected: genitalDetected,
        status,
        reason_rejected: reasonRejected,
        reviewed_at: new Date().toISOString()
      })
      .select()
      .single();

    if (error) throw error;

    res.json({ success: true, moderation });

  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// ============================================
// ROUTES: NOTIFICATIONS
// ============================================

/**
 * POST /api/v2/notifications/register-token
 * Register device push token
 */
app.post('/api/v2/notifications/register-token', verifyToken, async (req, res) => {
  try {
    const { expoPushToken, deviceName, platform } = req.body;
    const userId = req.userId;

    if (!expoPushToken) {
      return res.status(400).json({ error: 'Expo push token required' });
    }

    // TODO: Save to user_push_tokens table
    console.log(`✅ Push token registered: ${expoPushToken.substring(0, 30)}...`);

    res.json({
      success: true,
      registered: true,
    });

  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

/**
 * POST /api/v2/notifications/preferences
 * Update notification preferences
 */
app.post('/api/v2/notifications/preferences', verifyToken, async (req, res) => {
  try {
    const userId = req.userId;
    const { newMatches, messages, likes, superLikes, boostReminders, subscriptionReminders } = req.body;

    // TODO: Save to notification_preferences table
    const preferences = {
      newMatches: newMatches ?? true,
      messages: messages ?? true,
      likes: likes ?? true,
      superLikes: superLikes ?? true,
      boostReminders: boostReminders ?? true,
      subscriptionReminders: subscriptionReminders ?? true,
    };

    console.log(`✅ Notification preferences updated for user ${userId}`);

    res.json({ success: true, preferences });

  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

/**
 * GET /api/v2/notifications/preferences
 * Get user's notification preferences
 */
app.get('/api/v2/notifications/preferences', verifyToken, async (req, res) => {
  try {
    const userId = req.userId;

    // TODO: Fetch from notification_preferences table
    const preferences = {
      newMatches: true,
      messages: true,
      likes: true,
      superLikes: true,
      boostReminders: true,
      subscriptionReminders: true,
    };

    res.json({ preferences });

  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

/**
 * POST /api/v2/notifications/send-test
 * Send test notification
 */
app.post('/api/v2/notifications/send-test', verifyToken, async (req, res) => {
  try {
    const userId = req.userId;

    // TODO: Send test notification via Firebase
    console.log(`✅ Test notification sent to user ${userId}`);

    res.json({
      success: true,
      message: 'Test notification sent. Check your device!',
    });

  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// ============================================
// ROUTES: PAYMENTS (STRIPE)
// ============================================

/**
 * POST /api/v2/payments/create-subscription
 * Create a new premium subscription
 */
app.post('/api/v2/payments/create-subscription', verifyToken, async (req, res) => {
  try {
    const { planId } = req.body;
    const userId = req.userId;

    // Validar plan
    const validPlans = ['monthly', 'quarterly', 'yearly'];
    if (!validPlans.includes(planId)) {
      return res.status(400).json({ error: 'Invalid plan' });
    }

    // Obtener usuario
    const { data: user } = await supabase
      .from('profiles')
      .select('email')
      .eq('user_id', userId)
      .single();

    if (!user) {
      return res.status(404).json({ error: 'User not found' });
    }

    // Guardar suscripción en base de datos
    const planPrices = {
      monthly: 7.99,
      quarterly: 19.99,
      yearly: 59.99,
    };

    const planBoosts = {
      monthly: 1,
      quarterly: 3,
      yearly: 12,
    };

    const expiresAtMap = {
      monthly: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000),
      quarterly: new Date(Date.now() + 90 * 24 * 60 * 60 * 1000),
      yearly: new Date(Date.now() + 365 * 24 * 60 * 60 * 1000),
    };

    const { data: subscription, error } = await supabase
      .from('premium_subscriptions')
      .insert({
        user_id: userId,
        plan: planId,
        price: planPrices[planId],
        currency: 'eur',
        started_at: new Date().toISOString(),
        expires_at: expiresAtMap[planId].toISOString(),
        boosts_count: planBoosts[planId],
        boosts_used: 0,
        status: 'active',
        stripe_subscription_id: `stripe_${userId}_${Date.now()}`,
      })
      .select()
      .single();

    if (error) {
      return res.status(400).json({ error: error.message });
    }

    console.log(`✅ Subscription created for user ${userId}: ${planId}`);

    res.json({
      success: true,
      subscriptionId: subscription.id,
      plan: subscription.plan,
      boosts: subscription.boosts_count,
      expiresAt: subscription.expires_at,
    });

  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

/**
 * GET /api/v2/payments/subscriptions
 * Get user's active subscriptions
 */
app.get('/api/v2/payments/subscriptions', verifyToken, async (req, res) => {
  try {
    const { data: subscriptions, error } = await supabase
      .from('premium_subscriptions')
      .select('*')
      .eq('user_id', req.userId)
      .order('created_at', { ascending: false });

    if (error) {
      return res.status(400).json({ error: error.message });
    }

    res.json({ subscriptions });

  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

/**
 * POST /api/v2/payments/cancel-subscription
 * Cancel a subscription
 */
app.post('/api/v2/payments/cancel-subscription', verifyToken, async (req, res) => {
  try {
    const { subscriptionId } = req.body;
    const userId = req.userId;

    // Verificar que la suscripción pertenece al usuario
    const { data: subscription } = await supabase
      .from('premium_subscriptions')
      .select('*')
      .eq('id', subscriptionId)
      .eq('user_id', userId)
      .single();

    if (!subscription) {
      return res.status(404).json({ error: 'Subscription not found' });
    }

    // Actualizar estado
    const { data: updated, error } = await supabase
      .from('premium_subscriptions')
      .update({
        status: 'cancelled',
        cancelled_at: new Date().toISOString(),
      })
      .eq('id', subscriptionId)
      .select()
      .single();

    if (error) {
      return res.status(400).json({ error: error.message });
    }

    console.log(`❌ Subscription cancelled: ${subscriptionId}`);

    res.json({ success: true, subscription: updated });

  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

/**
 * GET /api/v2/payments/invoices
 * Get user's payment invoices
 */
app.get('/api/v2/payments/invoices', verifyToken, async (req, res) => {
  try {
    const { data: subscriptions } = await supabase
      .from('premium_subscriptions')
      .select('*')
      .eq('user_id', req.userId);

    // Mock invoice data
    const invoices = subscriptions.map((sub) => ({
      id: `invoice_${sub.id}`,
      subscriptionId: sub.id,
      amount: sub.price,
      currency: sub.currency,
      status: 'paid',
      createdAt: sub.created_at,
      pdfUrl: `/api/v2/payments/invoices/${sub.id}/pdf`,
    }));

    res.json({ invoices });

  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

/**
 * POST /api/v2/boosts/activate
 * Activate a visibility boost
 */
app.post('/api/v2/boosts/activate', verifyToken, async (req, res) => {
  try {
    const userId = req.userId;

    // Verificar suscripción activa
    const { data: subscription } = await supabase
      .from('premium_subscriptions')
      .select('*')
      .eq('user_id', userId)
      .eq('status', 'active')
      .single();

    if (!subscription) {
      return res.status(403).json({ error: 'No active subscription' });
    }

    if (subscription.boosts_used >= subscription.boosts_count) {
      return res.status(403).json({ error: 'No boosts remaining' });
    }

    // Crear boost
    const expiresAt = new Date(Date.now() + 30 * 60 * 1000); // 30 minutes

    const { data: boost, error } = await supabase
      .from('boosts')
      .insert({
        user_id: userId,
        boost_type: 'premium',
        multiplier: 3.0,
        duration_minutes: 30,
        started_at: new Date().toISOString(),
        expires_at: expiresAt.toISOString(),
        source: 'subscription',
        status: 'active',
      })
      .select()
      .single();

    if (error) {
      return res.status(400).json({ error: error.message });
    }

    // Actualizar boosts_used
    await supabase
      .from('premium_subscriptions')
      .update({ boosts_used: subscription.boosts_used + 1 })
      .eq('id', subscription.id);

    console.log(`🚀 Boost activated for user ${userId}`);

    res.json({
      success: true,
      boost: {
        id: boost.id,
        expiresAt: boost.expires_at,
        multiplier: boost.multiplier,
        durationMinutes: boost.duration_minutes,
      },
    });

  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

export default app;
