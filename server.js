import express from 'express';
import cors from 'cors';
import dotenv from 'dotenv';
import { createClient } from '@supabase/supabase-js';
import jwt from 'jsonwebtoken';
import bcrypt from 'bcryptjs';

// ============================================
// CONFIG
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
  console.warn('   Primero configura las variables de entorno:');
  console.warn('   export SUPABASE_URL="https://xxxxx.supabase.co"');
  console.warn('   export SUPABASE_ANON_KEY="eyJhbGc..."');
}

// ============================================
// JWT MIDDLEWARE
// ============================================
const verifyToken = (req, res, next) => {
  const token = req.headers.authorization?.split(' ')[1];
  if (!token) return res.status(401).json({ error: 'No token' });
  
  try {
    const decoded = jwt.verify(token, process.env.JWT_SECRET || 'dev-secret');
    req.userId = decoded.id;
    next();
  } catch {
    res.status(403).json({ error: 'Invalid token' });
  }
};

// ============================================
// ROUTES: AUTH
// ============================================

// REGISTER
app.post('/api/auth/register', async (req, res) => {
  try {
    const { email, password, username, firstName, lastName } = req.body;

    // Validate
    if (!email || !password || !username) {
      return res.status(400).json({ error: 'Missing required fields' });
    }

    // Check if user exists
    const { data: existing } = await supabase
      .from('profiles')
      .select('id')
      .eq('username', username)
      .single();

    if (existing) {
      return res.status(409).json({ error: 'Username already taken' });
    }

    // Hash password
    const hashedPassword = await bcrypt.hash(password, 10);

    // Create user in auth.users (Supabase Auth)
    const { data: authData, error: authError } = await supabase.auth.signUpWithPassword({
      email,
      password
    });

    if (authError) return res.status(400).json({ error: authError.message });

    const userId = authData.user.id;

    // Create profile
    const { error: profileError } = await supabase
      .from('profiles')
      .insert({
        id: userId,
        username,
        first_name: firstName || '',
        last_name: lastName || '',
        email: email
      });

    if (profileError) return res.status(400).json({ error: profileError.message });

    // Create coins & streak records
    await supabase.from('user_coins').insert({ user_id: userId, coins: 50 });
    await supabase.from('daily_streaks').insert({ user_id: userId });
    await supabase.from('preferences').insert({ user_id: userId });

    // Generate JWT
    const token = jwt.sign({ id: userId, email }, process.env.JWT_SECRET || 'dev-secret');

    res.status(201).json({
      message: 'User created successfully',
      userId,
      token,
      user: {
        id: userId,
        email,
        username
      }
    });
  } catch (error) {
    console.error('Register error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// LOGIN
app.post('/api/auth/login', async (req, res) => {
  try {
    const { email, password } = req.body;

    if (!email || !password) {
      return res.status(400).json({ error: 'Email and password required' });
    }

    // Authenticate with Supabase
    const { data, error } = await supabase.auth.signInWithPassword({
      email,
      password
    });

    if (error) return res.status(401).json({ error: 'Invalid credentials' });

    const userId = data.user.id;
    const token = jwt.sign({ id: userId, email }, process.env.JWT_SECRET || 'dev-secret');

    res.json({ token, userId, email });
  } catch (error) {
    console.error('Login error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// ============================================
// ROUTES: PROFILES
// ============================================

// GET OWN PROFILE
app.get('/api/users/profile', verifyToken, async (req, res) => {
  try {
    const { data, error } = await supabase
      .from('profiles')
      .select(`
        *,
        user_coins(coins),
        daily_streaks(current_streak, last_streak_date),
        profile_photos(*)
      `)
      .eq('id', req.userId)
      .single();

    if (error) return res.status(404).json({ error: 'Profile not found' });

    res.json(data);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// UPDATE PROFILE
app.put('/api/users/profile', verifyToken, async (req, res) => {
  try {
    const { firstName, lastName, bio, birthDate, gender, lookingFor, latitude, longitude, city } = req.body;

    const { data, error } = await supabase
      .from('profiles')
      .update({
        first_name: firstName,
        last_name: lastName,
        bio,
        birth_date: birthDate,
        gender,
        looking_for: lookingFor,
        latitude,
        longitude,
        city,
        profile_complete: true,
        updated_at: new Date()
      })
      .eq('id', req.userId)
      .select()
      .single();

    if (error) return res.status(400).json({ error: error.message });

    res.json(data);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// GET DISCOVER (Profiles para swipe)
app.get('/api/discover', verifyToken, async (req, res) => {
  try {
    const { data: userProfile } = await supabase
      .from('profiles')
      .select('*')
      .eq('id', req.userId)
      .single();

    if (!userProfile) return res.status(404).json({ error: 'User profile not found' });

    // Get preferences
    const { data: prefs } = await supabase
      .from('preferences')
      .select('*')
      .eq('user_id', req.userId)
      .single();

    // Get users already interacted with
    const { data: interactions } = await supabase
      .from('interactions')
      .select('target_user_id')
      .eq('user_id', req.userId);

    const interactedIds = interactions?.map(i => i.target_user_id) || [];

    // Query: nearby users matching preferences
    let query = supabase
      .from('profiles')
      .select(`
        *,
        profile_photos(photo_url, order_index)
      `)
      .neq('id', req.userId)
      .not('id', 'in', `(${interactedIds.join(',') || 'null'})`)
      .filter('profile_complete', 'eq', true);

    // Apply filters
    if (prefs?.min_age) query = query.gte('age', prefs.min_age);
    if (prefs?.max_age) query = query.lte('age', prefs.max_age);

    const { data: profiles } = await query.limit(50);

    res.json(profiles || []);
  } catch (error) {
    console.error('Discover error:', error);
    res.status(500).json({ error: error.message });
  }
});

// ============================================
// ROUTES: INTERACTIONS
// ============================================

// LIKE
app.post('/api/interactions/like', verifyToken, async (req, res) => {
  try {
    const { targetUserId } = req.body;

    if (!targetUserId) return res.status(400).json({ error: 'targetUserId required' });

    // Insert interaction
    const { error } = await supabase
      .from('interactions')
      .insert({
        user_id: req.userId,
        target_user_id: targetUserId,
        action: 'like'
      });

    if (error && !error.message.includes('duplicate')) {
      return res.status(400).json({ error: error.message });
    }

    // Log activity
    await supabase.from('activity_log').insert({
      user_id: req.userId,
      action_type: 'like',
      target_user_id: targetUserId
    });

    // Check for mutual like (match)
    const { data: mutualLike } = await supabase
      .from('interactions')
      .select('id')
      .eq('user_id', targetUserId)
      .eq('target_user_id', req.userId)
      .eq('action', 'like')
      .single();

    if (mutualLike) {
      // Create match
      const { error: matchError } = await supabase
        .from('matches')
        .insert({
          user_id_1: req.userId,
          user_id_2: targetUserId
        });

      if (!matchError) {
        // Create notification
        await supabase.from('notifications').insert({
          user_id: targetUserId,
          type: 'match',
          title: '¡Tienes un match! 🎉',
          related_user_id: req.userId
        });
      }
    }

    res.json({ success: true, matched: !!mutualLike });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// PASS
app.post('/api/interactions/pass', verifyToken, async (req, res) => {
  try {
    const { targetUserId } = req.body;

    await supabase
      .from('interactions')
      .insert({
        user_id: req.userId,
        target_user_id: targetUserId,
        action: 'pass'
      })
      .on('*', (payload) => { /* handle realtime */ });

    await supabase.from('activity_log').insert({
      user_id: req.userId,
      action_type: 'pass',
      target_user_id: targetUserId
    });

    res.json({ success: true });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// SUPER LIKE (costs coins)
app.post('/api/interactions/super-like', verifyToken, async (req, res) => {
  try {
    const { targetUserId } = req.body;

    // Check coins
    const { data: coins } = await supabase
      .from('user_coins')
      .select('coins')
      .eq('user_id', req.userId)
      .single();

    if (coins.coins < 10) {
      return res.status(400).json({ error: 'Not enough coins' });
    }

    // Deduct coins
    const newCoins = coins.coins - 10;
    await supabase
      .from('user_coins')
      .update({ coins: newCoins })
      .eq('user_id', req.userId);

    // Record interaction
    await supabase
      .from('interactions')
      .insert({
        user_id: req.userId,
        target_user_id: targetUserId,
        action: 'super_like'
      });

    await supabase.from('activity_log').insert({
      user_id: req.userId,
      action_type: 'super_like',
      target_user_id: targetUserId,
      coins_involved: 10
    });

    // Notify
    await supabase.from('notifications').insert({
      user_id: targetUserId,
      type: 'super_like',
      title: '¡Alguien te ha dado Super Like! ⭐',
      related_user_id: req.userId
    });

    res.json({ success: true, coinsRemaining: newCoins });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// ============================================
// ROUTES: MESSAGES
// ============================================

// GET CHATS
app.get('/api/messages/chats', verifyToken, async (req, res) => {
  try {
    const { data } = await supabase
      .from('matches')
      .select(`
        id,
        user_id_1,
        user_id_2,
        matched_at
      `)
      .or(`user_id_1.eq.${req.userId},user_id_2.eq.${req.userId}`);

    res.json(data || []);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// SEND MESSAGE
app.post('/api/messages/send', verifyToken, async (req, res) => {
  try {
    const { receiverId, content } = req.body;

    const { data, error } = await supabase
      .from('messages')
      .insert({
        sender_id: req.userId,
        receiver_id: receiverId,
        content
      })
      .select()
      .single();

    if (error) return res.status(400).json({ error: error.message });

    // Notify receiver
    await supabase.from('notifications').insert({
      user_id: receiverId,
      type: 'message',
      title: 'Nuevo mensaje 💬',
      related_user_id: req.userId
    });

    res.json(data);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// ============================================
// ROUTES: COINS & ECONOMY
// ============================================

// GET COINS
app.get('/api/coins', verifyToken, async (req, res) => {
  try {
    const { data } = await supabase
      .from('user_coins')
      .select('*')
      .eq('user_id', req.userId)
      .single();

    res.json(data);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// BUY COINS
app.post('/api/coins/purchase', verifyToken, async (req, res) => {
  try {
    const { amount, paymentMethodId } = req.body;

    // TODO: Integrate Stripe
    // For now, just add coins (demo mode)
    const { data } = await supabase
      .from('user_coins')
      .select('coins')
      .eq('user_id', req.userId)
      .single();

    const newCoins = data.coins + amount;

    await supabase
      .from('user_coins')
      .update({ coins: newCoins })
      .eq('user_id', req.userId);

    await supabase.from('coin_transactions').insert({
      user_id: req.userId,
      amount,
      type: 'spend',
      reason: 'Purchased coins',
      balance_after: newCoins
    });

    res.json({ success: true, coins: newCoins });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// ============================================
// ROUTES: DAILY STREAKS
// ============================================

// CLAIM DAILY REWARD
app.post('/api/streaks/claim', verifyToken, async (req, res) => {
  try {
    const { data: streak } = await supabase
      .from('daily_streaks')
      .select('*')
      .eq('user_id', req.userId)
      .single();

    const today = new Date().toISOString().split('T')[0];
    const lastClaimedDate = streak.last_claimed_date;

    if (lastClaimedDate === today) {
      return res.status(400).json({ error: 'Already claimed today' });
    }

    // Rewards progression
    const rewards = [50, 75, 100, 150, 200, 300, 500];
    const newStreak = (streak.current_streak % 7) + 1;
    const reward = rewards[newStreak - 1];

    // Update streak
    await supabase
      .from('daily_streaks')
      .update({
        current_streak: newStreak,
        longest_streak: Math.max(streak.longest_streak || 0, newStreak),
        last_claimed_date: today,
        total_rewards_earned: (streak.total_rewards_earned || 0) + reward
      })
      .eq('user_id', req.userId);

    // Add coins
    const { data: coins } = await supabase
      .from('user_coins')
      .select('coins')
      .eq('user_id', req.userId)
      .single();

    const newCoins = coins.coins + reward;
    await supabase
      .from('user_coins')
      .update({ coins: newCoins })
      .eq('user_id', req.userId);

    res.json({ 
      success: true, 
      streakDay: newStreak, 
      reward, 
      coinsTotal: newCoins 
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// ============================================
// HEALTH CHECK
// ============================================

app.get('/health', (req, res) => {
  res.json({ status: 'API running ✅' });
});

app.get('/', (req, res) => {
  res.json({
    name: 'YUIZZ API',
    version: '1.0.0',
    docs: 'Coming soon...'
  });
});

// ============================================
// START SERVER
// ============================================

app.listen(PORT, () => {
  console.log(`\n╔═══════════════════════════════════════╗`);
  console.log(`║   🚀 YUIZZ API BACKEND RUNNING      ║`);
  console.log(`╚═══════════════════════════════════════╝\n`);
  console.log(`📍 Server: http://localhost:${PORT}`);
  console.log(`📚 Health: http://localhost:${PORT}/health\n`);
  
  if (!supabaseUrl || !supabaseKey) {
    console.log(`⚠️  Configure environment variables:`);
    console.log(`   export SUPABASE_URL="https://xxxxx.supabase.co"`);
    console.log(`   export SUPABASE_ANON_KEY="eyJhbGc..."\n`);
  }
});
