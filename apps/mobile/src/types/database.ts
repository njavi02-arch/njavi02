// Tipos generados a mano a partir de supabase/migrations/0001_init.sql — si el esquema
// cambia, actualizar este archivo en el mismo commit (en un proyecto Supabase real esto
// se generaría automáticamente con `supabase gen types typescript`).

export interface ProfileRow {
  id: string;
  display_name: string;
  birth_date: string;
  gender: 'male' | 'female' | 'non_binary' | 'unspecified';
  seeking: string[];
  city: string | null;
  latitude: number | null;
  longitude: number | null;
  bio: string;
  status: 'active' | 'under_review' | 'suspended' | 'deleted';
  is_premium: boolean;
  is_verified: boolean;
  premium_until: string | null;
  profile_completion_pct: number;
  onboarding_completed_at: string | null;
  created_at: string;
  updated_at: string;
  last_active_at: string;
}

export interface PhotoRow {
  id: string;
  profile_id: string;
  storage_path: string;
  url: string;
  position: number;
  moderation_status: 'pending' | 'approved' | 'rejected';
  created_at: string;
}

export interface InterestRow {
  id: string;
  name: string;
  category: string | null;
}

export interface ConversationRequestRow {
  id: string;
  sender_id: string;
  receiver_id: string;
  first_message: string;
  status: 'pending' | 'accepted' | 'declined' | 'expired';
  created_at: string;
  responded_at: string | null;
}

export interface ConversationRow {
  id: string;
  user_a_id: string;
  user_b_id: string;
  source_request_id: string | null;
  created_at: string;
  last_message_at: string;
  archived_by_a: boolean;
  archived_by_b: boolean;
  muted_by_a: boolean;
  muted_by_b: boolean;
}

export interface MessageRow {
  id: string;
  conversation_id: string;
  sender_id: string;
  content: string | null;
  message_type: 'text' | 'image' | 'system';
  image_url: string | null;
  status: 'sent' | 'delivered' | 'read';
  created_at: string;
  read_at: string | null;
}

export interface SuperLikeRow {
  id: string;
  sender_id: string;
  receiver_id: string;
  message: string | null;
  is_seen: boolean;
  created_at: string;
}

export interface ProfileViewRow {
  id: string;
  viewer_id: string;
  viewed_id: string;
  created_at: string;
}

export interface AdmirerRevealRow {
  id: string;
  profile_id: string;
  revealed_viewer_id: string;
  method: 'coins' | 'premium' | 'admin_grant';
  created_at: string;
}

export interface CoinWalletRow {
  profile_id: string;
  balance: number;
}

export interface MessageCreditWalletRow {
  profile_id: string;
  balance: number;
}

export interface SuperLikeCreditWalletRow {
  profile_id: string;
  balance: number;
}

export interface DailyStreakRow {
  profile_id: string;
  current_streak: number;
  longest_streak: number;
  last_checkin_date: string | null;
  next_reward_day: number;
}

export interface NotificationRow {
  id: string;
  profile_id: string;
  type:
    | 'new_message'
    | 'new_request'
    | 'request_accepted'
    | 'super_like_received'
    | 'profile_viewed'
    | 'daily_reward_ready'
    | 'streak_at_risk'
    | 'secret_admirer'
    | 'promotion';
  payload: Record<string, unknown>;
  is_read: boolean;
  created_at: string;
}

export interface NotificationPreferencesRow {
  profile_id: string;
  new_message: boolean;
  new_request: boolean;
  super_like_received: boolean;
  profile_viewed: boolean;
  daily_reward_ready: boolean;
  secret_admirer: boolean;
  promotions: boolean;
}

export interface UserPreferencesRow {
  profile_id: string;
  min_age: number;
  max_age: number;
  max_distance_km: number;
  show_me_gender: string[];
}

export interface BlockRow {
  id: string;
  blocker_id: string;
  blocked_id: string;
  created_at: string;
}

export interface ReportRow {
  id: string;
  reporter_id: string;
  reported_id: string;
  reason: 'spam' | 'fake_profile' | 'inappropriate_content' | 'harassment' | 'underage' | 'other';
  details: string | null;
  related_message_id: string | null;
  status: 'pending' | 'reviewed' | 'actioned' | 'dismissed';
  created_at: string;
}

export interface AppConfigRow {
  key: string;
  value: unknown;
  description: string | null;
}

export interface VerificationRequestRow {
  id: string;
  profile_id: string;
  selfie_url: string;
  status: 'pending' | 'approved' | 'rejected';
  reviewed_by: string | null;
  reviewed_at: string | null;
  rejection_reason: string | null;
  created_at: string;
}

export interface ProfilePromptRow {
  id: string;
  profile_id: string;
  question: string;
  answer: string;
  position: number;
  created_at: string;
}

export interface ProfileBoostRow {
  id: string;
  profile_id: string;
  starts_at: string;
  ends_at: string;
  coin_cost: number;
}

export interface PushTokenRow {
  id: string;
  profile_id: string;
  expo_push_token: string;
  platform: 'ios' | 'android' | 'web';
}
