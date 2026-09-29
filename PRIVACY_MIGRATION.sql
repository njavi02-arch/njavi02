/**
 * YUIZZ V2.0 - Privacy & Security Migration
 * Phase 4: Privacy Features
 * Date: 2026-09-29
 */

-- ============================================
-- 1. PRIVACY SETTINGS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS privacy_settings (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL UNIQUE REFERENCES auth.users(id) ON DELETE CASCADE,
  anonymous_mode BOOLEAN DEFAULT false,
  prevent_screenshots BOOLEAN DEFAULT true,
  auto_delete_messages BOOLEAN DEFAULT false,
  auto_delete_photos BOOLEAN DEFAULT false,
  delete_photos_after_minutes INTEGER DEFAULT 1440, -- 24 hours
  show_last_seen BOOLEAN DEFAULT false,
  show_typing_indicator BOOLEAN DEFAULT false,
  allow_forwarding BOOLEAN DEFAULT false,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_privacy_settings_user_id
  ON privacy_settings(user_id);

-- Enable RLS
ALTER TABLE privacy_settings ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own privacy settings"
  ON privacy_settings FOR SELECT
  USING (auth.uid() = user_id);

CREATE POLICY "Users can update own privacy settings"
  ON privacy_settings FOR UPDATE
  USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own privacy settings"
  ON privacy_settings FOR INSERT
  WITH CHECK (auth.uid() = user_id);

-- ============================================
-- 2. SCREENSHOT ATTEMPTS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS screenshot_attempts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  attempt_number INTEGER DEFAULT 1,
  conversation_id UUID REFERENCES conversations(id) ON DELETE SET NULL,
  detected_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_screenshot_attempts_user_id
  ON screenshot_attempts(user_id);
CREATE INDEX IF NOT EXISTS idx_screenshot_attempts_conversation_id
  ON screenshot_attempts(conversation_id);
CREATE INDEX IF NOT EXISTS idx_screenshot_attempts_detected_at
  ON screenshot_attempts(detected_at DESC);

-- Enable RLS
ALTER TABLE screenshot_attempts ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own screenshot attempts"
  ON screenshot_attempts FOR SELECT
  USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own screenshot attempts"
  ON screenshot_attempts FOR INSERT
  WITH CHECK (auth.uid() = user_id);

-- ============================================
-- 3. PRIVACY EVENTS TABLE (Audit Trail)
-- ============================================
CREATE TABLE IF NOT EXISTS privacy_events (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  event_type VARCHAR(50) NOT NULL, -- screenshot_attempt, conversation_deleted, photo_viewed, etc.
  conversation_id UUID REFERENCES conversations(id) ON DELETE SET NULL,
  other_user_id UUID REFERENCES auth.users(id) ON DELETE SET NULL,
  metadata JSONB DEFAULT '{}',
  logged_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_privacy_events_user_id
  ON privacy_events(user_id);
CREATE INDEX IF NOT EXISTS idx_privacy_events_event_type
  ON privacy_events(event_type);
CREATE INDEX IF NOT EXISTS idx_privacy_events_conversation_id
  ON privacy_events(conversation_id);
CREATE INDEX IF NOT EXISTS idx_privacy_events_logged_at
  ON privacy_events(logged_at DESC);

-- Enable RLS
ALTER TABLE privacy_events ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own privacy events"
  ON privacy_events FOR SELECT
  USING (auth.uid() = user_id);

CREATE POLICY "System can insert privacy events"
  ON privacy_events FOR INSERT
  WITH CHECK (true);

-- ============================================
-- 4. AUTO-DESTROYING PHOTOS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS auto_destroy_photos (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  photo_id UUID NOT NULL REFERENCES profile_photos(id) ON DELETE CASCADE,
  conversation_id UUID REFERENCES conversations(id) ON DELETE CASCADE,
  sender_user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  destroy_at TIMESTAMP WITH TIME ZONE NOT NULL,
  is_destroyed BOOLEAN DEFAULT false,
  destroyed_at TIMESTAMP WITH TIME ZONE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_auto_destroy_photos_photo_id
  ON auto_destroy_photos(photo_id);
CREATE INDEX IF NOT EXISTS idx_auto_destroy_photos_conversation_id
  ON auto_destroy_photos(conversation_id);
CREATE INDEX IF NOT EXISTS idx_auto_destroy_photos_destroy_at
  ON auto_destroy_photos(destroy_at);
CREATE INDEX IF NOT EXISTS idx_auto_destroy_photos_is_destroyed
  ON auto_destroy_photos(is_destroyed);

-- Enable RLS
ALTER TABLE auto_destroy_photos ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view photos in their conversations"
  ON auto_destroy_photos FOR SELECT
  USING (
    sender_user_id = auth.uid() OR
    conversation_id IN (
      SELECT id FROM conversations
      WHERE user1_id = auth.uid() OR user2_id = auth.uid()
    )
  );

-- ============================================
-- 5. UPDATE CONVERSATIONS TABLE (if needed)
-- ============================================
-- Add deleted tracking if not already present
ALTER TABLE conversations
ADD COLUMN IF NOT EXISTS deleted_by_users UUID[] DEFAULT '{}';

ALTER TABLE conversations
ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMP WITH TIME ZONE;

-- ============================================
-- 6. TRIGGER: Auto-update privacy_settings updated_at
-- ============================================
CREATE OR REPLACE FUNCTION update_privacy_settings_timestamp()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS privacy_settings_updated_at_trigger ON privacy_settings;

CREATE TRIGGER privacy_settings_updated_at_trigger
BEFORE UPDATE ON privacy_settings
FOR EACH ROW
EXECUTE FUNCTION update_privacy_settings_timestamp();

-- ============================================
-- 7. FUNCTION: Auto-destroy expired photos
-- ============================================
CREATE OR REPLACE FUNCTION auto_destroy_expired_photos()
RETURNS void AS $$
BEGIN
  UPDATE auto_destroy_photos
  SET
    is_destroyed = true,
    destroyed_at = NOW()
  WHERE
    is_destroyed = false
    AND destroy_at <= NOW();

  RAISE NOTICE 'Auto-destroyed % photos', ROW_COUNT;
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- 8. CLEANUP: Remove old privacy events (30 days)
-- ============================================
CREATE OR REPLACE FUNCTION cleanup_old_privacy_events()
RETURNS void AS $$
BEGIN
  DELETE FROM privacy_events
  WHERE logged_at < NOW() - INTERVAL '30 days';

  RAISE NOTICE 'Cleaned up old privacy events, deleted % rows', ROW_COUNT;
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- Verification Queries
-- ============================================
-- Run after migration to verify tables exist:
-- SELECT * FROM information_schema.tables
-- WHERE table_name IN (
--   'privacy_settings',
--   'screenshot_attempts',
--   'privacy_events',
--   'auto_destroy_photos'
-- );

-- Check RLS policies:
-- SELECT * FROM pg_policies
-- WHERE tablename IN (
--   'privacy_settings',
--   'screenshot_attempts',
--   'privacy_events',
--   'auto_destroy_photos'
-- );
