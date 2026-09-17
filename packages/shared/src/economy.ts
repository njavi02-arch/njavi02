// Lógica de negocio pura (sin I/O) para la economía de Orbita: monedas, créditos de
// mensaje, racha de 7 días, Super Likes, fotos bloqueadas y edad mínima.
//
// Estas funciones son el "contrato" que replican tanto el cliente (para UI optimista)
// como las funciones de Postgres/Edge Functions (para la validación real, que es la que
// manda). Mantenerlas puras permite testearlas sin base de datos — ver economy.test.ts.

import type { AppConfig, DailyStreakState, StreakReward } from './types';

export class InsufficientBalanceError extends Error {
  constructor(what: string, available: number, needed: number) {
    super(`Saldo insuficiente de ${what}: disponible ${available}, necesario ${needed}`);
    this.name = 'InsufficientBalanceError';
  }
}

/** Aplica un delta a un saldo de monedas/créditos, lanzando si el resultado sería negativo. */
export function applyBalanceDelta(
  balance: number,
  delta: number,
  label: string,
): number {
  const next = balance + delta;
  if (next < 0) {
    throw new InsufficientBalanceError(label, balance, -delta);
  }
  return next;
}

/** Coste en monedas de enviar un Super Like extra (fuera del gratuito diario). Premium no
 * cambia el coste del Super Like en sí (solo su cupo gratuito se gestiona aparte). */
export function superLikeCoinCost(config: Pick<AppConfig, 'super_like_coin_cost'>): number {
  return config.super_like_coin_cost;
}

/** ¿Puede el usuario enviar un Super Like gratis hoy? */
export function canSendFreeSuperLike(
  superLikesSentToday: number,
  config: Pick<AppConfig, 'super_like_daily_free'>,
): boolean {
  return superLikesSentToday < config.super_like_daily_free;
}

/** Coste de desbloquear el paquete de fotos ocultas de un perfil. Premium = gratis. */
export function photoUnlockCoinCost(
  config: Pick<AppConfig, 'photo_unlock_coin_cost'>,
  viewerIsPremium: boolean,
): number {
  return viewerIsPremium ? 0 : config.photo_unlock_coin_cost;
}

/** Coste de revelar la identidad de UN admirador secreto. Premium = gratis. */
export function secretAdmirerRevealCoinCost(
  config: Pick<AppConfig, 'secret_admirer_reveal_coin_cost'>,
  viewerIsPremium: boolean,
): number {
  return viewerIsPremium ? 0 : config.secret_admirer_reveal_coin_cost;
}

export interface PhotoVisibility {
  publicCount: number;
  lockedCount: number;
  /** true si el visor ya pagó/es premium y por tanto ve todas */
  allUnlocked: boolean;
  /** Texto tipo "+7 fotos 🔒" para el badge de galería (brief sección 5) */
  lockedBadgeLabel: string | null;
}

/** Calcula qué fotos son públicas y cuántas quedan bloqueadas, para el badge "+N 🔒". */
export function computePhotoVisibility(
  totalPhotos: number,
  config: Pick<AppConfig, 'public_photos_count'>,
  isUnlockedByViewer: boolean,
): PhotoVisibility {
  const publicCount = Math.min(totalPhotos, config.public_photos_count);
  const lockedCount = Math.max(0, totalPhotos - config.public_photos_count);
  return {
    publicCount,
    lockedCount,
    allUnlocked: isUnlockedByViewer || lockedCount === 0,
    lockedBadgeLabel: lockedCount > 0 && !isUnlockedByViewer ? `+${lockedCount} fotos 🔒` : null,
  };
}

/** Recompensa de racha para un día concreto (1-7). Lanza si el día está fuera de rango. */
export function streakRewardForDay(day: number, config: Pick<AppConfig, 'streak_rewards'>): StreakReward {
  const reward = config.streak_rewards.find((r) => r.day === day);
  if (!reward) {
    throw new RangeError(`No hay recompensa configurada para el día ${day} de la racha`);
  }
  return reward;
}

export interface StreakCheckinResult {
  streak: DailyStreakState;
  reward: StreakReward | null; // null si ya se reclamó hoy
  streakWasReset: boolean;
}

/**
 * Calcula el nuevo estado de la racha al hacer check-in en `today`.
 * - Si ya hizo check-in hoy, no hay recompensa (idempotente, evita doble cobro).
 * - Si el check-in anterior fue ayer, la racha continúa y avanza al siguiente día (ciclo 1-7).
 * - Si el check-in anterior fue hace 2+ días (o nunca), la racha se reinicia en el día 1.
 */
export function computeStreakCheckin(
  state: DailyStreakState,
  today: string, // 'YYYY-MM-DD'
  config: Pick<AppConfig, 'streak_rewards'>,
): StreakCheckinResult {
  if (state.lastCheckinDate === today) {
    return { streak: state, reward: null, streakWasReset: false };
  }

  const daysSinceLast = state.lastCheckinDate
    ? diffInDays(state.lastCheckinDate, today)
    : null;

  const isConsecutive = daysSinceLast === 1;
  // Solo cuenta como "racha rota" si había una racha previa que perder; el primer
  // check-in de un usuario nuevo no rompe nada (no hay nada que romper todavía).
  const streakWasReset = state.lastCheckinDate !== null && !isConsecutive;

  const currentStreak = isConsecutive ? state.currentStreak + 1 : 1;
  const longestStreak = Math.max(state.longestStreak, currentStreak);

  const claimedDay = isConsecutive ? state.nextRewardDay : 1;
  const nextDayInCycle = wrapStreakDay(claimedDay + 1);
  const reward = streakRewardForDay(claimedDay, config);

  return {
    streak: {
      profileId: state.profileId,
      currentStreak,
      longestStreak,
      lastCheckinDate: today,
      nextRewardDay: nextDayInCycle,
    },
    reward,
    streakWasReset,
  };
}

function wrapStreakDay(day: number): number {
  // El ciclo es 1..7; tras el 7 vuelve a empezar en 1.
  return ((day - 1) % 7) + 1;
}

function diffInDays(isoA: string, isoB: string): number {
  const a = new Date(`${isoA}T00:00:00Z`).getTime();
  const b = new Date(`${isoB}T00:00:00Z`).getTime();
  return Math.round((b - a) / 86_400_000);
}

/** Porcentaje de perfil completado (brief sección 20/6) sobre los campos que cuentan. */
export interface ProfileCompletionInput {
  hasName: boolean;
  hasBirthDate: boolean;
  hasGender: boolean;
  hasSeeking: boolean;
  hasCity: boolean;
  photoCount: number;
  hasBio: boolean;
  interestCount: number;
}

export function computeProfileCompletionPct(input: ProfileCompletionInput): number {
  const checks = [
    input.hasName,
    input.hasBirthDate,
    input.hasGender,
    input.hasSeeking,
    input.hasCity,
    input.photoCount >= 1,
    input.hasBio,
    input.interestCount >= 3,
    input.photoCount >= 3, // incentivo a llenar las 3 fotos públicas
  ];
  const done = checks.filter(Boolean).length;
  return Math.round((done / checks.length) * 100);
}

/** Edad mínima (brief sección 16/24) — verificación real, no checkbox de autodeclaración. */
export function isOldEnough(
  birthDateIso: string,
  today: Date,
  config: Pick<AppConfig, 'min_age'>,
): boolean {
  const birth = new Date(birthDateIso);
  let age = today.getUTCFullYear() - birth.getUTCFullYear();
  const hasHadBirthdayThisYear =
    today.getUTCMonth() > birth.getUTCMonth() ||
    (today.getUTCMonth() === birth.getUTCMonth() && today.getUTCDate() >= birth.getUTCDate());
  if (!hasHadBirthdayThisYear) age -= 1;
  return age >= config.min_age;
}

/** Multiplicador de rate limit efectivo según antigüedad de la cuenta (antispam). */
export function effectiveRateLimit(
  baseLimit: number,
  accountAgeHours: number,
  config: Pick<AppConfig, 'new_account_rate_limit_factor' | 'new_account_grace_hours'>,
): number {
  if (accountAgeHours >= config.new_account_grace_hours) return baseLimit;
  return Math.max(1, Math.floor(baseLimit * config.new_account_rate_limit_factor));
}
