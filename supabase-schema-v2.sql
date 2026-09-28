-- ============================================
-- YUIZZ V2 - ADULT DATING PLATFORM SCHEMA
-- ============================================
-- Complete database schema for adult dating app
-- Includes: profiles, couples, photos, interactions, chat, coins, etc.
-- Last updated: 28 September 2026

-- ============================================
-- 1. USERS (Authentication)
-- ============================================
-- Note: Supabase Auth handles auth.users
-- We extend with our profiles table

-- ============================================
-- 2. PROFILES (Individual Profiles)
-- ============================================
CREATE TABLE IF NOT EXISTS public.profiles (
  id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,

  -- Identity
  username VARCHAR(50) UNIQUE NOT NULL,
  first_name VARCHAR(100),
  last_name VARCHAR(100),
  bio TEXT,

  -- Personal data (private)
  birth_date DATE NOT NULL,
  age INT GENERATED ALWAYS AS (EXTRACT(YEAR FROM AGE(birth_date))) STORED,
  gender VARCHAR(50), -- 'm', 'f', 'nb', 'other'
  pronoun VARCHAR(50),

  -- Location
  latitude DECIMAL(10, 8),
  longitude DECIMAL(11, 8),
  city VARCHAR(100),
  country VARCHAR(100),

  -- Privacy
  show_location BOOLEAN DEFAULT TRUE,
  location_accuracy VARCHAR(50) DEFAULT 'city', -- 'city', 'neighbourhood', 'exact'
  show_age BOOLEAN DEFAULT TRUE,
  show_distance BOOLEAN DEFAULT TRUE,

  -- Verification
  age_verified BOOLEAN DEFAULT FALSE,
  document_verified BOOLEAN DEFAULT FALSE,
  selfie_verified BOOLEAN DEFAULT FALSE,
  verification_doc_url TEXT,
  verification_selfie_url TEXT,

  -- Interests and preferences
  interests VARCHAR(50)[],
  orientations VARCHAR(50)[],
  languages VARCHAR(50)[],

  -- What are they looking for? (CRITICAL FIELD)
  seeking VARCHAR(50)[],  -- 'dating', 'casual', 'sexting', 'relationship', 'meeting', 'friends', 'explore'

  -- Profile type
  profile_type VARCHAR(50) DEFAULT 'individual', -- 'individual' or 'couple'
  couple_id UUID,

  -- Status
  profile_complete BOOLEAN DEFAULT FALSE,
  is_active BOOLEAN DEFAULT TRUE,
  last_active TIMESTAMP DEFAULT NOW(),

  -- Timestamps
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),

  CONSTRAINT age_valid CHECK (age >= 18 AND age <= 120),
  CONSTRAINT valid_profile_type CHECK (profile_type IN ('individual', 'couple'))
);

CREATE INDEX idx_profiles_city ON profiles(city);
CREATE INDEX idx_profiles_seeking ON profiles USING GIN(seeking);
CREATE INDEX idx_profiles_active ON profiles(is_active, last_active DESC);
CREATE INDEX idx_profiles_location ON profiles(latitude, longitude) WHERE is_active = TRUE;

-- ============================================
-- 3. COUPLES (Couple Profiles)
-- ============================================
CREATE TABLE IF NOT EXISTS public.couples (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

  name VARCHAR(200),
  bio TEXT,
  couple_photo_url TEXT,

  -- Members
  primary_user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  secondary_user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,

  -- Member info
  person1_name VARCHAR(100),
  person1_gender VARCHAR(50),
  person2_name VARCHAR(100),
  person2_gender VARCHAR(50),

  -- What they seek
  seeking VARCHAR(50)[],  -- 'women', 'men', 'couples', 'groups'

  -- Location (couple)
  latitude DECIMAL(10, 8),
  longitude DECIMAL(11, 8),
  city VARCHAR(100),
  country VARCHAR(100),

  -- Interests
  interests VARCHAR(50)[],

  -- Status
  is_active BOOLEAN DEFAULT TRUE,
  profile_complete BOOLEAN DEFAULT FALSE,

  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),

  CONSTRAINT both_users_different CHECK (primary_user_id != secondary_user_id)
);

CREATE INDEX idx_couples_location ON couples(latitude, longitude) WHERE is_active = TRUE;
CREATE INDEX idx_couples_seeking ON couples USING GIN(seeking);

-- ============================================
-- 4. PROFILE_PHOTOS (Photo Galleries)
-- ============================================
CREATE TABLE IF NOT EXISTS public.profile_photos (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,

  photo_url TEXT NOT NULL,
  thumb_url TEXT,

  -- Privacy settings
  position INT DEFAULT 0,
  is_public BOOLEAN DEFAULT TRUE,
  is_private BOOLEAN DEFAULT FALSE,
  is_blur BOOLEAN DEFAULT FALSE,

  -- Unlock system
  requires_unlock BOOLEAN DEFAULT FALSE,
  unlock_price_coins INT DEFAULT 50,

  -- Moderation
  flagged BOOLEAN DEFAULT FALSE,
  flag_reason VARCHAR(255),
  approved_by_moderation BOOLEAN DEFAULT TRUE,

  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_profile_photos_user ON profile_photos(user_id);
CREATE INDEX idx_profile_photos_public ON profile_photos(user_id, is_public);

-- ============================================
-- 5. PROFILE_GALLERIES (Private Collections)
-- ============================================
CREATE TABLE IF NOT EXISTS public.profile_galleries (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,

  title VARCHAR(100),
  description TEXT,
  is_public BOOLEAN DEFAULT FALSE,

  -- Access control
  access_type VARCHAR(50) DEFAULT 'matches_only', -- 'matches_only', 'liked_me', 'request_based', 'coins'
  access_coins_required INT DEFAULT 0,

  created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.gallery_access_requests (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  gallery_id UUID NOT NULL REFERENCES profile_galleries(id) ON DELETE CASCADE,
  requester_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  owner_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,

  status VARCHAR(50) DEFAULT 'pending', -- 'pending', 'approved', 'denied'
  cost_coins INT DEFAULT 0,

  created_at TIMESTAMP DEFAULT NOW(),
  responded_at TIMESTAMP
);

-- ============================================
-- 6. INTERACTIONS (Likes, Passes, Superlikes)
-- ============================================
CREATE TABLE IF NOT EXISTS public.interactions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

  actor_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  target_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  action VARCHAR(50) NOT NULL, -- 'like', 'pass', 'superlike', 'view'

  -- Match detection
  match_found BOOLEAN DEFAULT FALSE,
  match_created_at TIMESTAMP,

  -- Metadata
  ip_hash VARCHAR(255),
  created_at TIMESTAMP DEFAULT NOW(),

  CONSTRAINT actor_not_target CHECK (actor_id != target_id)
);

CREATE INDEX idx_interactions_actor ON interactions(actor_id, action);
CREATE INDEX idx_interactions_target ON interactions(target_id, action);
CREATE INDEX idx_interactions_match ON interactions(match_found) WHERE match_found = TRUE;

-- ============================================
-- 7. MATCHES (Connections)
-- ============================================
CREATE TABLE IF NOT EXISTS public.matches (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

  user1_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  user2_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,

  match_type VARCHAR(50) DEFAULT 'mutual_like', -- 'mutual_like', 'superlike'
  status VARCHAR(50) DEFAULT 'active', -- 'active', 'blocked', 'reported'

  last_message_id UUID,
  last_message_at TIMESTAMP,

  unread_count_user1 INT DEFAULT 0,
  unread_count_user2 INT DEFAULT 0,

  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),

  CONSTRAINT user1_less_user2 CHECK (user1_id < user2_id)
);

CREATE INDEX idx_matches_users ON matches(user1_id, user2_id);
CREATE INDEX idx_matches_status ON matches(status);

-- ============================================
-- 8. MESSAGES (Chat)
-- ============================================
CREATE TABLE IF NOT EXISTS public.messages (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

  match_id UUID NOT NULL REFERENCES matches(id) ON DELETE CASCADE,
  sender_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  receiver_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,

  -- Content
  content TEXT,
  content_type VARCHAR(50) DEFAULT 'text', -- 'text', 'image', 'gif', 'emoji'

  -- Media
  image_url TEXT,
  image_thumb_url TEXT,

  -- Status
  is_read BOOLEAN DEFAULT FALSE,
  read_at TIMESTAMP,
  deleted_by_sender BOOLEAN DEFAULT FALSE,
  deleted_by_receiver BOOLEAN DEFAULT FALSE,

  -- Moderation
  flagged BOOLEAN DEFAULT FALSE,
  flag_reason VARCHAR(255),

  created_at TIMESTAMP DEFAULT NOW(),

  CONSTRAINT sender_receiver_diff CHECK (sender_id != receiver_id)
);

CREATE INDEX idx_messages_match ON messages(match_id, created_at DESC);
CREATE INDEX idx_messages_receiver ON messages(receiver_id, is_read);
CREATE INDEX idx_messages_created ON messages(created_at DESC);

-- ============================================
-- 9. POSTS (Announcements/Status)
-- ============================================
CREATE TABLE IF NOT EXISTS public.posts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  couple_id UUID REFERENCES couples(id) ON DELETE CASCADE,

  -- Content
  content TEXT NOT NULL,
  post_type VARCHAR(50) DEFAULT 'status', -- 'status', 'announcement', 'question', 'event'

  -- Intent tags
  seeking VARCHAR(50)[],

  -- Location
  latitude DECIMAL(10, 8),
  longitude DECIMAL(11, 8),
  city VARCHAR(100),
  show_location BOOLEAN DEFAULT TRUE,

  -- Filters
  min_age INT,
  max_age INT,
  gender_preference VARCHAR(50)[],

  -- Media
  photos_urls TEXT[],  -- max 4

  -- Engagement
  views INT DEFAULT 0,
  likes INT DEFAULT 0,
  comments INT DEFAULT 0,
  shares INT DEFAULT 0,

  -- Status
  is_active BOOLEAN DEFAULT TRUE,
  flagged BOOLEAN DEFAULT FALSE,

  -- Expiration (posts expire in 7 days)
  expires_at TIMESTAMP DEFAULT (NOW() + INTERVAL '7 days'),

  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_posts_user ON posts(user_id, created_at DESC);
CREATE INDEX idx_posts_location ON posts(latitude, longitude) WHERE is_active = TRUE;
CREATE INDEX idx_posts_seeking ON posts USING GIN(seeking);
CREATE INDEX idx_posts_active ON posts(is_active, expires_at);

-- ============================================
-- 10. COINS (Economy)
-- ============================================
CREATE TABLE IF NOT EXISTS public.user_coins (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL UNIQUE REFERENCES auth.users(id) ON DELETE CASCADE,

  coins INT DEFAULT 0,
  lifetime_coins_spent INT DEFAULT 0,
  lifetime_coins_earned INT DEFAULT 0,

  updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.coin_transactions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,

  transaction_type VARCHAR(50) NOT NULL, -- 'purchase', 'spent', 'bonus', 'refund'
  amount INT NOT NULL,
  reason VARCHAR(255),

  -- For purchases
  stripe_payment_id VARCHAR(255),
  price_eur DECIMAL(10, 2),

  created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_coin_trans_user ON coin_transactions(user_id, created_at DESC);

-- ============================================
-- 11. SUBSCRIPTIONS (Premium Plans)
-- ============================================
CREATE TABLE IF NOT EXISTS public.subscriptions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL UNIQUE REFERENCES auth.users(id) ON DELETE CASCADE,

  plan_id VARCHAR(50) DEFAULT 'free', -- 'free', 'premium'
  billing_period VARCHAR(20), -- 'monthly', 'annual'
  status VARCHAR(50) DEFAULT 'active', -- 'active', 'cancelled', 'expired'

  start_date TIMESTAMP DEFAULT NOW(),
  end_date TIMESTAMP,

  stripe_customer_id VARCHAR(255),
  stripe_subscription_id VARCHAR(255),
  payment_method VARCHAR(50),

  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_subscriptions_status ON subscriptions(status);

-- ============================================
-- 12. BLOCKS & REPORTS (Safety)
-- ============================================
CREATE TABLE IF NOT EXISTS public.blocks (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  blocker_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  blocked_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,

  reason VARCHAR(255),
  created_at TIMESTAMP DEFAULT NOW(),

  CONSTRAINT blocker_not_blocked CHECK (blocker_id != blocked_id)
);

CREATE INDEX idx_blocks_blocker ON blocks(blocker_id);
CREATE INDEX idx_blocks_blocked ON blocks(blocked_id);

CREATE TABLE IF NOT EXISTS public.reports (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  reporter_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  reported_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,

  report_type VARCHAR(50) NOT NULL, -- 'fake_profile', 'spam', 'harassment', 'inappropriate', 'scam'
  description TEXT,
  evidence_urls TEXT[],

  status VARCHAR(50) DEFAULT 'pending', -- 'pending', 'investigating', 'resolved', 'dismissed'
  moderation_notes TEXT,
  action_taken VARCHAR(50), -- 'warning', 'suspend', 'ban'

  created_at TIMESTAMP DEFAULT NOW(),
  resolved_at TIMESTAMP
);

CREATE INDEX idx_reports_reported ON reports(reported_id, status);

-- ============================================
-- 13. AGE_VERIFICATION (18+ Enforcement)
-- ============================================
CREATE TABLE IF NOT EXISTS public.age_verification (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL UNIQUE REFERENCES auth.users(id) ON DELETE CASCADE,

  birth_date DATE NOT NULL,
  document_type VARCHAR(50), -- 'passport', 'id_card', 'driving_license'
  document_country VARCHAR(2),

  verification_status VARCHAR(50) DEFAULT 'pending', -- 'pending', 'verified', 'rejected'
  verified_at TIMESTAMP,
  verified_by_admin_id UUID,

  rejection_reason VARCHAR(255),

  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- ============================================
-- 14. ACTIVITY_LOG (Analytics)
-- ============================================
CREATE TABLE IF NOT EXISTS public.activity_log (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES auth.users(id) ON DELETE SET NULL,

  action VARCHAR(100),
  entity_type VARCHAR(50), -- 'profile', 'message', 'like', 'post'
  entity_id UUID,
  metadata JSON,

  ip_address INET,
  user_agent TEXT,

  created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_activity_log_user ON activity_log(user_id, created_at DESC);

-- ============================================
-- 15. NOTIFICATIONS (Push Notifications)
-- ============================================
CREATE TABLE IF NOT EXISTS public.notifications (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,

  type VARCHAR(50) NOT NULL, -- 'match', 'message', 'like', 'superlike', 'viewed'
  title VARCHAR(200),
  body TEXT,
  actor_id UUID REFERENCES auth.users(id) ON DELETE SET NULL,

  data JSON,

  is_read BOOLEAN DEFAULT FALSE,
  read_at TIMESTAMP,

  created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_notifications_user ON notifications(user_id, created_at DESC);
CREATE INDEX idx_notifications_unread ON notifications(user_id, is_read) WHERE is_read = FALSE;

-- ============================================
-- INDEXES FOR PERFORMANCE
-- ============================================
CREATE INDEX idx_profiles_updated ON profiles(updated_at DESC);
CREATE INDEX idx_couples_updated ON couples(updated_at DESC);
CREATE INDEX idx_interactions_created ON interactions(created_at DESC);
CREATE INDEX idx_matches_created ON matches(created_at DESC);

-- ============================================
-- ROW LEVEL SECURITY (RLS)
-- ============================================

-- Enable RLS on all tables
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE couples ENABLE ROW LEVEL SECURITY;
ALTER TABLE profile_photos ENABLE ROW LEVEL SECURITY;
ALTER TABLE profile_galleries ENABLE ROW LEVEL SECURITY;
ALTER TABLE interactions ENABLE ROW LEVEL SECURITY;
ALTER TABLE matches ENABLE ROW LEVEL SECURITY;
ALTER TABLE messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE posts ENABLE ROW LEVEL SECURITY;
ALTER TABLE blocks ENABLE ROW LEVEL SECURITY;

-- Policies: Profiles
CREATE POLICY "Users can view own profile"
  ON profiles FOR SELECT
  USING (auth.uid() = id);

CREATE POLICY "Users can update own profile"
  ON profiles FOR UPDATE
  USING (auth.uid() = id);

-- Policies: Messages
CREATE POLICY "Users can only see own messages"
  ON messages FOR SELECT
  USING (auth.uid() IN (sender_id, receiver_id));

CREATE POLICY "Users can only insert own messages"
  ON messages FOR INSERT
  WITH CHECK (auth.uid() = sender_id);

-- Policies: Blocks
CREATE POLICY "Users can only see own blocks"
  ON blocks FOR SELECT
  USING (auth.uid() IN (blocker_id, blocked_id));

-- ============================================
-- COMMENTS (Documentation)
-- ============================================
COMMENT ON TABLE profiles IS 'User profiles - individual dating profiles';
COMMENT ON TABLE couples IS 'Couple profiles - joint dating profiles for couples';
COMMENT ON TABLE profile_photos IS 'Photo galleries - public and private photos';
COMMENT ON TABLE messages IS 'Chat messages - private messaging between matches';
COMMENT ON TABLE posts IS 'Public announcements - "what''s on your mind" style posts';
COMMENT ON TABLE user_coins IS 'Virtual currency for monetization';
COMMENT ON TABLE subscriptions IS 'Premium subscription data';
COMMENT ON TABLE blocks IS 'User blocking (privacy/safety)';
COMMENT ON TABLE reports IS 'Abuse reports and moderation';

-- ============================================
-- SCHEMA COMPLETE
-- ============================================
-- Version: 2.0
-- Tables: 15
-- Date: 28 September 2026
-- Status: Ready for development
