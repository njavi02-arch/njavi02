import type { AppConfig, StreakReward } from './types';

// Recompensas de la racha de 7 días — brief sección 12.
// Día 4 = "recompensa especial" no especificada en el brief -> se interpreta como
// Super Likes (ver docs/ASSUMPTIONS.md). Día 7 = 50 créditos de mensaje (literal del brief).
export const DEFAULT_STREAK_REWARDS: StreakReward[] = [
  { day: 1, coins: 15, superLikes: 0, messageCredits: 0, isSpecial: false, label: 'Día 1' },
  { day: 2, coins: 20, superLikes: 0, messageCredits: 0, isSpecial: false, label: 'Día 2' },
  { day: 3, coins: 25, superLikes: 0, messageCredits: 0, isSpecial: false, label: 'Día 3' },
  { day: 4, coins: 0, superLikes: 7, messageCredits: 0, isSpecial: true, label: 'Día 4 · Especial' },
  { day: 5, coins: 30, superLikes: 0, messageCredits: 0, isSpecial: false, label: 'Día 5' },
  { day: 6, coins: 35, superLikes: 0, messageCredits: 0, isSpecial: false, label: 'Día 6' },
  {
    day: 7,
    coins: 100,
    superLikes: 10,
    messageCredits: 75,
    isSpecial: true,
    label: 'Día 7 · Gran recompensa 🎉',
  },
];

export const DEFAULT_APP_CONFIG: AppConfig = {
  public_photos_count: 3,
  max_photos_count: 10,
  starting_message_credits: 150,
  super_like_daily_free: 3,
  super_like_coin_cost: 10,
  photo_unlock_coin_cost: 25,
  secret_admirer_reveal_coin_cost: 15,
  daily_login_coins: 20,
  streak_rewards: DEFAULT_STREAK_REWARDS,
  new_conversation_rate_limit_per_hour: 30,
  new_conversation_rate_limit_per_day: 80,
  new_account_rate_limit_factor: 0.5,
  new_account_grace_hours: 24,
  report_rate_limit_per_day: 15,
  photo_upload_rate_limit_per_day: 10,
  min_age: 18,
  conversation_request_expiry_days: 30,
  banned_words: [],
  premium_price_monthly_cents: 999,
  premium_price_yearly_cents: 5999,
  premium_currency: 'EUR',
  boost_coin_cost: 50,
  boost_duration_minutes: 60,
};
