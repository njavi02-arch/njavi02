-- ============================================
-- YUIZZ V2.0 DATABASE MIGRATION
-- Date: 2026-09-29
-- Status: Ready to apply to Supabase
-- ============================================

-- ============================================
-- STEP 1: ALTER EXISTING TABLES FOR V2.0
-- ============================================

-- Add V2.0 columns to profiles table
ALTER TABLE profiles
ADD COLUMN IF NOT EXISTS hashtags TEXT[] DEFAULT ARRAY[],
ADD COLUMN IF NOT EXISTS profile_type VARCHAR(20) DEFAULT 'individual',
ADD COLUMN IF NOT EXISTS couple_partner_id UUID;

-- Add V2.0 columns to profile_photos table
ALTER TABLE profile_photos
ADD COLUMN IF NOT EXISTS photo_type VARCHAR(20) DEFAULT 'regular',
ADD COLUMN IF NOT EXISTS position INTEGER CHECK (position >= 1 AND position <= 3);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_profiles_hashtags ON profiles USING GIN (hashtags);
CREATE INDEX IF NOT EXISTS idx_profiles_profile_type ON profiles(profile_type);

-- ============================================
-- STEP 2: CREATE NEW V2.0 TABLES
-- ============================================

-- User Preferences Table
CREATE TABLE IF NOT EXISTS user_preferences (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL UNIQUE REFERENCES auth.users(id) ON DELETE CASCADE,
  min_age INTEGER NOT NULL DEFAULT 18 CHECK (min_age >= 18),
  max_age INTEGER NOT NULL DEFAULT 65 CHECK (max_age <= 120 AND max_age >= min_age),
  gender_preference TEXT[] NOT NULL DEFAULT ARRAY['female', 'male'],
  max_distance_km INTEGER NOT NULL DEFAULT 50 CHECK (max_distance_km > 0),
  preferred_hashtags TEXT[] DEFAULT ARRAY[],
  show_verified_only BOOLEAN DEFAULT FALSE,
  show_couple_profiles BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_user_preferences_user_id ON user_preferences(user_id);

-- Premium Subscriptions Table
CREATE TABLE IF NOT EXISTS premium_subscriptions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL UNIQUE REFERENCES auth.users(id) ON DELETE CASCADE,
  plan VARCHAR(20) NOT NULL CHECK (plan IN ('monthly', 'quarterly', 'yearly')),
  price DECIMAL(10, 2) NOT NULL,
  currency VARCHAR(3) DEFAULT 'EUR',
  started_at TIMESTAMP WITH TIME ZONE NOT NULL,
  expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
  cancelled_at TIMESTAMP WITH TIME ZONE,
  stripe_subscription_id VARCHAR(255),
  stripe_customer_id VARCHAR(255),
  boosts_count INTEGER NOT NULL DEFAULT 0,
  boosts_used INTEGER NOT NULL DEFAULT 0,
  status VARCHAR(20) NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'cancelled', 'expired')),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_premium_subscriptions_user_id ON premium_subscriptions(user_id);
CREATE INDEX IF NOT EXISTS idx_premium_subscriptions_status ON premium_subscriptions(status);
CREATE INDEX IF NOT EXISTS idx_premium_subscriptions_expires_at ON premium_subscriptions(expires_at);

-- Boosts Table
CREATE TABLE IF NOT EXISTS boosts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  boost_type VARCHAR(20) NOT NULL DEFAULT 'premium',
  multiplier DECIMAL(3, 1) NOT NULL DEFAULT 3.0,
  duration_minutes INTEGER NOT NULL DEFAULT 30,
  started_at TIMESTAMP WITH TIME ZONE NOT NULL,
  expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
  source VARCHAR(20) NOT NULL DEFAULT 'subscription' CHECK (source IN ('subscription', 'manual', 'promotion')),
  status VARCHAR(20) NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'expired')),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_boosts_user_id ON boosts(user_id);
CREATE INDEX IF NOT EXISTS idx_boosts_status ON boosts(status);
CREATE INDEX IF NOT EXISTS idx_boosts_expires_at ON boosts(expires_at);

-- Photo Moderation Table
CREATE TABLE IF NOT EXISTS photo_moderation (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  photo_id UUID NOT NULL REFERENCES profile_photos(id) ON DELETE CASCADE,
  nude_score DECIMAL(3, 2) NOT NULL DEFAULT 0.0 CHECK (nude_score >= 0 AND nude_score <= 1),
  explicit_content BOOLEAN DEFAULT FALSE,
  genitals_detected BOOLEAN DEFAULT FALSE,
  status VARCHAR(20) NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'approved', 'rejected', 'flagged')),
  reason_rejected TEXT,
  reviewed_by VARCHAR(255),
  reviewed_at TIMESTAMP WITH TIME ZONE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_photo_moderation_photo_id ON photo_moderation(photo_id);
CREATE INDEX IF NOT EXISTS idx_photo_moderation_status ON photo_moderation(status);

-- Discovery Cache Table (Performance optimization)
CREATE TABLE IF NOT EXISTS discovery_cache (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  cached_profile_ids UUID[] NOT NULL,
  compatibility_scores DECIMAL(5, 2)[] NOT NULL,
  cached_at TIMESTAMP WITH TIME ZONE NOT NULL,
  expires_at TIMESTAMP WITH TIME ZONE NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_discovery_cache_user_id ON discovery_cache(user_id);
CREATE INDEX IF NOT EXISTS idx_discovery_cache_expires_at ON discovery_cache(expires_at);

-- Reports Table (Moderation)
CREATE TABLE IF NOT EXISTS reports (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  reporter_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  reported_user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  reason VARCHAR(255) NOT NULL,
  description TEXT,
  status VARCHAR(20) NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'investigating', 'resolved', 'dismissed')),
  action_taken VARCHAR(255),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_reports_reporter_id ON reports(reporter_id);
CREATE INDEX IF NOT EXISTS idx_reports_reported_user_id ON reports(reported_user_id);
CREATE INDEX IF NOT EXISTS idx_reports_status ON reports(status);

-- Blocks Table (User blocking)
CREATE TABLE IF NOT EXISTS blocks (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  blocker_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  blocked_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  reason VARCHAR(255),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  UNIQUE(blocker_id, blocked_id)
);

CREATE INDEX IF NOT EXISTS idx_blocks_blocker_id ON blocks(blocker_id);
CREATE INDEX IF NOT EXISTS idx_blocks_blocked_id ON blocks(blocked_id);

-- Activity Log Table (Audit trail)
CREATE TABLE IF NOT EXISTS activity_log (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  action VARCHAR(255) NOT NULL,
  details JSONB,
  ip_address INET,
  user_agent TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_activity_log_user_id ON activity_log(user_id);
CREATE INDEX IF NOT EXISTS idx_activity_log_created_at ON activity_log(created_at);

-- ============================================
-- STEP 3: ENABLE ROW LEVEL SECURITY (RLS)
-- ============================================

-- Enable RLS on all new V2.0 tables
ALTER TABLE user_preferences ENABLE ROW LEVEL SECURITY;
ALTER TABLE premium_subscriptions ENABLE ROW LEVEL SECURITY;
ALTER TABLE boosts ENABLE ROW LEVEL SECURITY;
ALTER TABLE photo_moderation ENABLE ROW LEVEL SECURITY;
ALTER TABLE discovery_cache ENABLE ROW LEVEL SECURITY;
ALTER TABLE reports ENABLE ROW LEVEL SECURITY;
ALTER TABLE blocks ENABLE ROW LEVEL SECURITY;
ALTER TABLE activity_log ENABLE ROW LEVEL SECURITY;

-- User Preferences RLS Policies
CREATE POLICY "Users can view own preferences"
  ON user_preferences FOR SELECT
  USING (auth.uid() = user_id);

CREATE POLICY "Users can update own preferences"
  ON user_preferences FOR UPDATE
  USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own preferences"
  ON user_preferences FOR INSERT
  WITH CHECK (auth.uid() = user_id);

-- Premium Subscriptions RLS Policies
CREATE POLICY "Users can view own subscription"
  ON premium_subscriptions FOR SELECT
  USING (auth.uid() = user_id);

-- Boosts RLS Policies
CREATE POLICY "Users can view own boosts"
  ON boosts FOR SELECT
  USING (auth.uid() = user_id);

CREATE POLICY "Users can create own boosts"
  ON boosts FOR INSERT
  WITH CHECK (auth.uid() = user_id);

-- Photo Moderation RLS Policies
CREATE POLICY "Users can view moderation of own photos"
  ON photo_moderation FOR SELECT
  USING (photo_id IN (
    SELECT id FROM profile_photos
    WHERE profile_id IN (
      SELECT id FROM profiles WHERE user_id = auth.uid()
    )
  ));

-- Reports RLS Policies
CREATE POLICY "Users can view own reports"
  ON reports FOR SELECT
  USING (auth.uid() = reporter_id OR auth.uid() = reported_user_id);

CREATE POLICY "Users can create reports"
  ON reports FOR INSERT
  WITH CHECK (auth.uid() = reporter_id);

-- Blocks RLS Policies
CREATE POLICY "Users can view own blocks"
  ON blocks FOR SELECT
  USING (auth.uid() = blocker_id OR auth.uid() = blocked_id);

CREATE POLICY "Users can create blocks"
  ON blocks FOR INSERT
  WITH CHECK (auth.uid() = blocker_id);

-- Activity Log RLS Policies
CREATE POLICY "Users can view own activity"
  ON activity_log FOR SELECT
  USING (auth.uid() = user_id);

CREATE POLICY "System can insert activity logs"
  ON activity_log FOR INSERT
  WITH CHECK (true);

-- ============================================
-- STEP 4: CREATE FUNCTIONS & TRIGGERS
-- ============================================

-- Function to update timestamp on update
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Triggers for updated_at columns
CREATE TRIGGER update_user_preferences_updated_at
  BEFORE UPDATE ON user_preferences
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_premium_subscriptions_updated_at
  BEFORE UPDATE ON premium_subscriptions
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_photo_moderation_updated_at
  BEFORE UPDATE ON photo_moderation
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_reports_updated_at
  BEFORE UPDATE ON reports
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Function to check subscription expiry and update status
CREATE OR REPLACE FUNCTION check_subscription_expiry()
RETURNS VOID AS $$
BEGIN
  UPDATE premium_subscriptions
  SET status = 'expired'
  WHERE status = 'active' AND expires_at < NOW();
END;
$$ LANGUAGE plpgsql;

-- Function to check boost expiry and update status
CREATE OR REPLACE FUNCTION check_boost_expiry()
RETURNS VOID AS $$
BEGIN
  UPDATE boosts
  SET status = 'expired'
  WHERE status = 'active' AND expires_at < NOW();
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- STEP 5: SAMPLE DATA (for testing)
-- ============================================

-- Note: Uncomment these if you want sample data
-- INSERT INTO user_preferences (user_id, min_age, max_age, gender_preference, max_distance_km)
-- SELECT id, 18, 65, ARRAY['female', 'male'], 50
-- FROM auth.users LIMIT 5;

-- ============================================
-- STEP 6: VERIFICATION & GRANTS
-- ============================================

-- Grant permissions to anon role (for public endpoints)
GRANT USAGE ON SCHEMA public TO anon, authenticated;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO anon, authenticated;
GRANT INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO authenticated;

-- ============================================
-- END OF MIGRATION
-- ============================================

-- Execute these checks to verify migration:
-- SELECT * FROM information_schema.tables WHERE table_schema = 'public' AND table_name LIKE '%preference%';
-- SELECT * FROM information_schema.tables WHERE table_schema = 'public' AND table_name LIKE '%subscription%';
-- SELECT * FROM information_schema.tables WHERE table_schema = 'public' AND table_name LIKE '%boost%';
-- SELECT * FROM information_schema.tables WHERE table_schema = 'public' AND table_name LIKE '%moderation%';
