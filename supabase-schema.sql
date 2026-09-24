-- ============================================
-- YUIZZ DATABASE SCHEMA
-- ============================================

-- ============================================
-- 1. USERS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS auth.users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email VARCHAR(255) UNIQUE NOT NULL,
  encrypted_password VARCHAR(255) NOT NULL,
  email_verified BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP DEFAULT NOW(),
  last_login TIMESTAMP
);

-- ============================================
-- 2. USER PROFILES
-- ============================================
CREATE TABLE IF NOT EXISTS public.profiles (
  id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  username VARCHAR(50) UNIQUE NOT NULL,
  first_name VARCHAR(100),
  last_name VARCHAR(100),
  bio TEXT,
  birth_date DATE,
  gender VARCHAR(50),
  looking_for VARCHAR(50),
  age INT GENERATED ALWAYS AS (EXTRACT(YEAR FROM AGE(birth_date))) STORED,
  
  -- Location
  latitude DECIMAL(10, 8),
  longitude DECIMAL(11, 8),
  city VARCHAR(100),
  country VARCHAR(100),
  
  -- Verification
  verified BOOLEAN DEFAULT FALSE,
  id_verified BOOLEAN DEFAULT FALSE,
  verification_selfie_url TEXT,
  
  -- Profile completion
  profile_complete BOOLEAN DEFAULT FALSE,
  registration_date TIMESTAMP DEFAULT NOW(),
  
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  
  CONSTRAINT age_valid CHECK (age >= 18 AND age <= 120)
);

-- ============================================
-- 3. PROFILE PHOTOS
-- ============================================
CREATE TABLE IF NOT EXISTS public.profile_photos (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
  photo_url TEXT NOT NULL,
  order_index INT DEFAULT 0,
  uploaded_at TIMESTAMP DEFAULT NOW()
);

-- ============================================
-- 4. USER PREFERENCES
-- ============================================
CREATE TABLE IF NOT EXISTS public.preferences (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL UNIQUE REFERENCES profiles(id) ON DELETE CASCADE,
  
  -- Age range
  min_age INT DEFAULT 18,
  max_age INT DEFAULT 65,
  
  -- Distance (km)
  max_distance_km INT DEFAULT 50,
  
  -- Looking for
  interested_in VARCHAR(50)[],
  
  -- Interests/hobbies
  interests VARCHAR(100)[],
  
  -- Language
  preferred_language VARCHAR(10) DEFAULT 'es',
  
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- ============================================
-- 5. LIKES & PASSES
-- ============================================
CREATE TABLE IF NOT EXISTS public.interactions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
  target_user_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
  
  action VARCHAR(20) NOT NULL CHECK (action IN ('like', 'pass', 'super_like')),
  created_at TIMESTAMP DEFAULT NOW(),
  
  -- Prevent duplicate interactions
  UNIQUE(user_id, target_user_id, action),
  CONSTRAINT no_self_like CHECK (user_id != target_user_id)
);

-- ============================================
-- 6. MATCHES
-- ============================================
CREATE TABLE IF NOT EXISTS public.matches (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id_1 UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
  user_id_2 UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
  
  matched_at TIMESTAMP DEFAULT NOW(),
  
  -- Ensure order doesn't matter
  UNIQUE(LEAST(user_id_1, user_id_2), GREATEST(user_id_1, user_id_2)),
  CONSTRAINT no_self_match CHECK (user_id_1 != user_id_2)
);

-- ============================================
-- 7. MESSAGES
-- ============================================
CREATE TABLE IF NOT EXISTS public.messages (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  sender_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
  receiver_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
  
  content TEXT NOT NULL,
  read BOOLEAN DEFAULT FALSE,
  read_at TIMESTAMP,
  
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  
  CONSTRAINT message_order CHECK (sender_id != receiver_id)
);

-- ============================================
-- 8. COINS & ECONOMY
-- ============================================
CREATE TABLE IF NOT EXISTS public.user_coins (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL UNIQUE REFERENCES profiles(id) ON DELETE CASCADE,
  
  coins INT DEFAULT 50,
  total_spent INT DEFAULT 0,
  total_earned INT DEFAULT 0,
  
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- ============================================
-- 9. DAILY STREAKS
-- ============================================
CREATE TABLE IF NOT EXISTS public.daily_streaks (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL UNIQUE REFERENCES profiles(id) ON DELETE CASCADE,
  
  current_streak INT DEFAULT 0,
  longest_streak INT DEFAULT 0,
  last_streak_date DATE,
  
  last_claimed_date DATE,
  total_rewards_earned INT DEFAULT 0,
  
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- ============================================
-- 10. ACTIVITY TRACKING
-- ============================================
CREATE TABLE IF NOT EXISTS public.activity_log (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
  
  action_type VARCHAR(50) NOT NULL CHECK (action_type IN ('like', 'pass', 'super_like', 'message', 'view')),
  target_user_id UUID REFERENCES profiles(id) ON DELETE SET NULL,
  
  coins_involved INT DEFAULT 0,
  created_at TIMESTAMP DEFAULT NOW()
);

-- ============================================
-- 11. PREMIUM SUBSCRIPTIONS
-- ============================================
CREATE TABLE IF NOT EXISTS public.subscriptions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL UNIQUE REFERENCES profiles(id) ON DELETE CASCADE,
  
  active BOOLEAN DEFAULT FALSE,
  plan_type VARCHAR(50) DEFAULT 'premium',
  price_eur DECIMAL(10, 2) DEFAULT 2.99,
  
  started_at TIMESTAMP,
  renews_at TIMESTAMP,
  cancelled_at TIMESTAMP,
  
  stripe_subscription_id VARCHAR(255),
  
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- ============================================
-- 12. COIN TRANSACTIONS
-- ============================================
CREATE TABLE IF NOT EXISTS public.coin_transactions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
  
  amount INT NOT NULL,
  type VARCHAR(50) NOT NULL CHECK (type IN ('earn', 'spend', 'gift', 'refund')),
  reason TEXT,
  
  balance_after INT,
  
  created_at TIMESTAMP DEFAULT NOW()
);

-- ============================================
-- 13. NOTIFICATIONS
-- ============================================
CREATE TABLE IF NOT EXISTS public.notifications (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
  
  type VARCHAR(50) NOT NULL CHECK (type IN ('match', 'message', 'super_like', 'streak', 'promotion')),
  title TEXT NOT NULL,
  body TEXT,
  related_user_id UUID REFERENCES profiles(id) ON DELETE SET NULL,
  
  read BOOLEAN DEFAULT FALSE,
  
  created_at TIMESTAMP DEFAULT NOW()
);

-- ============================================
-- INDEXES (Performance)
-- ============================================

CREATE INDEX idx_profiles_location ON profiles (latitude, longitude);
CREATE INDEX idx_interactions_user ON interactions (user_id, created_at DESC);
CREATE INDEX idx_interactions_target ON interactions (target_user_id);
CREATE INDEX idx_messages_sender ON messages (sender_id, created_at DESC);
CREATE INDEX idx_messages_receiver ON messages (receiver_id, read, created_at DESC);
CREATE INDEX idx_matches_user ON matches (user_id_1) WHERE user_id_1 IS NOT NULL;
CREATE INDEX idx_activity_user ON activity_log (user_id, created_at DESC);
CREATE INDEX idx_notifications_user ON notifications (user_id, read, created_at DESC);

-- ============================================
-- ROW LEVEL SECURITY (Privacy)
-- ============================================

-- Perfiles: Usuarios pueden ver todos, editar solo el suyo
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Profiles are viewable by everyone" ON public.profiles
  FOR SELECT USING (true);
CREATE POLICY "Users can edit own profile" ON public.profiles
  FOR UPDATE USING (auth.uid() = id);

-- Mensajes: Solo sender/receiver pueden verlos
ALTER TABLE public.messages ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can view own messages" ON public.messages
  FOR SELECT USING (auth.uid() = sender_id OR auth.uid() = receiver_id);
CREATE POLICY "Users can send messages" ON public.messages
  FOR INSERT WITH CHECK (auth.uid() = sender_id);

-- Coins: Solo el dueño puede verlas
ALTER TABLE public.user_coins ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can view own coins" ON public.user_coins
  FOR SELECT USING (auth.uid() = user_id);

-- Preferences: Solo el dueño puede verlas/editarlas
ALTER TABLE public.preferences ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can view own preferences" ON public.preferences
  FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can edit own preferences" ON public.preferences
  FOR UPDATE USING (auth.uid() = user_id);

