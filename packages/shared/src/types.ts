// Tipos de dominio compartidos entre apps/mobile y apps/admin.
// Reflejan 1:1 el esquema de supabase/migrations/0001_init.sql — si cambia una columna,
// este archivo debe cambiar en el mismo commit.

export type Gender = 'male' | 'female' | 'non_binary' | 'unspecified';

export type SeekingIntent = 'friendship' | 'social' | 'dating';

export type ProfileStatus = 'active' | 'under_review' | 'suspended' | 'deleted';

export type ConversationRequestStatus =
  | 'pending'
  | 'accepted'
  | 'declined'
  | 'expired';

export type MessageStatus = 'sent' | 'delivered' | 'read';

export type MessageType = 'text' | 'image' | 'system';

export type ReportReason =
  | 'spam'
  | 'fake_profile'
  | 'inappropriate_content'
  | 'harassment'
  | 'underage'
  | 'other';

export type ReportStatus = 'pending' | 'reviewed' | 'actioned' | 'dismissed';

export type CoinTransactionReason =
  | 'daily_login'
  | 'streak_bonus'
  | 'purchase'
  | 'super_like_sent'
  | 'super_like_purchase'
  | 'photo_unlock'
  | 'secret_admirer_reveal'
  | 'admin_grant'
  | 'boost_purchase'
  | 'refund';

export type MessageCreditTransactionReason =
  | 'signup_grant'
  | 'conversation_started'
  | 'streak_bonus'
  | 'purchase'
  | 'admin_grant'
  | 'refund';

export type PremiumPlan = 'monthly' | 'yearly';

export type PremiumStatus = 'active' | 'canceled' | 'expired' | 'in_grace_period';

export type NotificationType =
  | 'new_message'
  | 'new_request'
  | 'request_accepted'
  | 'super_like_received'
  | 'profile_viewed'
  | 'daily_reward_ready'
  | 'streak_at_risk'
  | 'secret_admirer'
  | 'promotion';

export type AdminRole = 'superadmin' | 'moderator' | 'support';

/** Recompensa asociada a un día de la racha de 7 días (brief sección 12). */
export interface StreakReward {
  day: number; // 1-7
  coins: number;
  superLikes: number;
  messageCredits: number;
  isSpecial: boolean;
  label: string;
}

/** Configuración económica y de negocio editable desde el panel de administración. */
export interface AppConfig {
  public_photos_count: number;
  max_photos_count: number;
  starting_message_credits: number;
  super_like_daily_free: number;
  super_like_coin_cost: number;
  photo_unlock_coin_cost: number;
  secret_admirer_reveal_coin_cost: number;
  daily_login_coins: number;
  streak_rewards: StreakReward[];
  new_conversation_rate_limit_per_hour: number;
  new_conversation_rate_limit_per_day: number;
  new_account_rate_limit_factor: number;
  new_account_grace_hours: number;
  report_rate_limit_per_day: number;
  photo_upload_rate_limit_per_day: number;
  min_age: number;
  conversation_request_expiry_days: number;
  banned_words: string[];
  premium_price_monthly_cents: number;
  premium_price_yearly_cents: number;
  premium_currency: string;
}

export interface Profile {
  id: string;
  displayName: string;
  birthDate: string; // ISO date
  gender: Gender;
  seeking: SeekingIntent[];
  city: string | null;
  latitude: number | null;
  longitude: number | null;
  bio: string;
  status: ProfileStatus;
  isPremium: boolean;
  premiumUntil: string | null;
  profileCompletionPct: number;
  createdAt: string;
  lastActiveAt: string;
}

export interface Photo {
  id: string;
  profileId: string;
  url: string;
  position: number; // 0-based; position < publicPhotosCount => pública
  moderationStatus: 'pending' | 'approved' | 'rejected';
}

export interface CoinWallet {
  profileId: string;
  balance: number;
}

export interface MessageCreditWallet {
  profileId: string;
  balance: number;
}

export interface DailyStreakState {
  profileId: string;
  currentStreak: number;
  longestStreak: number;
  lastCheckinDate: string | null; // ISO date (YYYY-MM-DD)
  nextRewardDay: number; // 1-7
}
