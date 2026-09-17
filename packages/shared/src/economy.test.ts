import { describe, expect, it } from 'vitest';
import { DEFAULT_APP_CONFIG } from './config-defaults';
import {
  InsufficientBalanceError,
  applyBalanceDelta,
  canSendFreeSuperLike,
  computePhotoVisibility,
  computeProfileCompletionPct,
  computeStreakCheckin,
  effectiveRateLimit,
  isOldEnough,
  photoUnlockCoinCost,
  secretAdmirerRevealCoinCost,
  streakRewardForDay,
  superLikeCoinCost,
} from './economy';
import type { DailyStreakState } from './types';

describe('applyBalanceDelta', () => {
  it('suma correctamente un ingreso', () => {
    expect(applyBalanceDelta(100, 20, 'monedas')).toBe(120);
  });

  it('resta correctamente un gasto válido', () => {
    expect(applyBalanceDelta(100, -20, 'monedas')).toBe(80);
  });

  it('lanza InsufficientBalanceError si el saldo quedaría negativo', () => {
    expect(() => applyBalanceDelta(10, -20, 'monedas')).toThrow(InsufficientBalanceError);
  });

  it('permite dejar el saldo exactamente en 0', () => {
    expect(applyBalanceDelta(20, -20, 'monedas')).toBe(0);
  });
});

describe('super likes', () => {
  it('coste en monedas viene de la config', () => {
    expect(superLikeCoinCost(DEFAULT_APP_CONFIG)).toBe(20);
  });

  it('permite super like gratis si no se ha usado el cupo diario', () => {
    expect(canSendFreeSuperLike(0, DEFAULT_APP_CONFIG)).toBe(true);
  });

  it('no permite super like gratis si ya se agotó el cupo diario', () => {
    expect(canSendFreeSuperLike(1, DEFAULT_APP_CONFIG)).toBe(false);
  });
});

describe('fotos bloqueadas (brief sección 5)', () => {
  it('perfil con 3 fotos: todas públicas, sin badge de bloqueadas', () => {
    const v = computePhotoVisibility(3, DEFAULT_APP_CONFIG, false);
    expect(v).toEqual({
      publicCount: 3,
      lockedCount: 0,
      allUnlocked: true,
      lockedBadgeLabel: null,
    });
  });

  it('perfil con 10 fotos sin desbloquear: 3 públicas + badge "+7 fotos 🔒"', () => {
    const v = computePhotoVisibility(10, DEFAULT_APP_CONFIG, false);
    expect(v.publicCount).toBe(3);
    expect(v.lockedCount).toBe(7);
    expect(v.allUnlocked).toBe(false);
    expect(v.lockedBadgeLabel).toBe('+7 fotos 🔒');
  });

  it('perfil con 10 fotos y viewer que ya desbloqueó: sin badge', () => {
    const v = computePhotoVisibility(10, DEFAULT_APP_CONFIG, true);
    expect(v.allUnlocked).toBe(true);
    expect(v.lockedBadgeLabel).toBeNull();
  });

  it('premium desbloquea gratis (coste 0), usuario normal paga la config', () => {
    expect(photoUnlockCoinCost(DEFAULT_APP_CONFIG, true)).toBe(0);
    expect(photoUnlockCoinCost(DEFAULT_APP_CONFIG, false)).toBe(50);
  });
});

describe('admiradores secretos', () => {
  it('coste de revelar identidad: gratis premium, config si no', () => {
    expect(secretAdmirerRevealCoinCost(DEFAULT_APP_CONFIG, true)).toBe(0);
    expect(secretAdmirerRevealCoinCost(DEFAULT_APP_CONFIG, false)).toBe(30);
  });
});

describe('racha diaria de 7 días (brief sección 12)', () => {
  const base: DailyStreakState = {
    profileId: 'p1',
    currentStreak: 0,
    longestStreak: 0,
    lastCheckinDate: null,
    nextRewardDay: 1,
  };

  it('primer check-in nunca hecho antes: día 1, racha = 1', () => {
    const result = computeStreakCheckin(base, '2026-01-01', DEFAULT_APP_CONFIG);
    expect(result.reward?.day).toBe(1);
    expect(result.streak.currentStreak).toBe(1);
    expect(result.streak.nextRewardDay).toBe(2);
    expect(result.streakWasReset).toBe(false); // no hubo racha previa que romper
  });

  it('check-in en el mismo día no reclama recompensa dos veces', () => {
    const afterDay1 = computeStreakCheckin(base, '2026-01-01', DEFAULT_APP_CONFIG).streak;
    const again = computeStreakCheckin(afterDay1, '2026-01-01', DEFAULT_APP_CONFIG);
    expect(again.reward).toBeNull();
    expect(again.streak).toEqual(afterDay1);
  });

  it('check-in en día consecutivo avanza la racha y da la recompensa del día correcto', () => {
    let state = computeStreakCheckin(base, '2026-01-01', DEFAULT_APP_CONFIG).streak; // día 1
    const day2 = computeStreakCheckin(state, '2026-01-02', DEFAULT_APP_CONFIG);
    expect(day2.reward?.day).toBe(2);
    expect(day2.streak.currentStreak).toBe(2);
    state = day2.streak;
    const day3 = computeStreakCheckin(state, '2026-01-03', DEFAULT_APP_CONFIG);
    expect(day3.reward?.day).toBe(3);
    expect(day3.streak.currentStreak).toBe(3);
  });

  it('romper la racha (saltarse un día) reinicia en el día 1', () => {
    const afterDay1 = computeStreakCheckin(base, '2026-01-01', DEFAULT_APP_CONFIG).streak;
    // Se salta el 2 de enero, vuelve el 4.
    const result = computeStreakCheckin(afterDay1, '2026-01-04', DEFAULT_APP_CONFIG);
    expect(result.streakWasReset).toBe(true);
    expect(result.reward?.day).toBe(1);
    expect(result.streak.currentStreak).toBe(1);
  });

  it('el día 4 da 5 Super Likes (recompensa especial) y no monedas', () => {
    const reward = streakRewardForDay(4, DEFAULT_APP_CONFIG);
    expect(reward.superLikes).toBe(5);
    expect(reward.coins).toBe(0);
    expect(reward.isSpecial).toBe(true);
  });

  it('el día 7 da 50 créditos de mensaje (brief literal: "Enviar 50 mensajes")', () => {
    const reward = streakRewardForDay(7, DEFAULT_APP_CONFIG);
    expect(reward.messageCredits).toBe(50);
    expect(reward.isSpecial).toBe(true);
  });

  it('tras completar el día 7, el ciclo vuelve a empezar en el día 1', () => {
    let state = base;
    let lastResult;
    const days = ['2026-01-01', '2026-01-02', '2026-01-03', '2026-01-04', '2026-01-05', '2026-01-06', '2026-01-07'];
    for (const day of days) {
      lastResult = computeStreakCheckin(state, day, DEFAULT_APP_CONFIG);
      state = lastResult.streak;
    }
    expect(lastResult!.reward?.day).toBe(7);
    expect(state.nextRewardDay).toBe(1); // ciclo reinicia
    expect(state.currentStreak).toBe(7);

    const day8 = computeStreakCheckin(state, '2026-01-08', DEFAULT_APP_CONFIG);
    expect(day8.reward?.day).toBe(1);
    expect(day8.streak.currentStreak).toBe(8); // la racha total sigue creciendo
    expect(day8.streakWasReset).toBe(false); // fue consecutivo, no se rompió
  });

  it('longestStreak nunca decrece aunque la racha actual se reinicie', () => {
    let state = base;
    for (const day of ['2026-01-01', '2026-01-02', '2026-01-03']) {
      state = computeStreakCheckin(state, day, DEFAULT_APP_CONFIG).streak;
    }
    expect(state.longestStreak).toBe(3);
    const broken = computeStreakCheckin(state, '2026-01-10', DEFAULT_APP_CONFIG).streak;
    expect(broken.currentStreak).toBe(1);
    expect(broken.longestStreak).toBe(3);
  });
});

describe('perfil completado', () => {
  it('perfil vacío = 0%', () => {
    expect(
      computeProfileCompletionPct({
        hasName: false,
        hasBirthDate: false,
        hasGender: false,
        hasSeeking: false,
        hasCity: false,
        photoCount: 0,
        hasBio: false,
        interestCount: 0,
      }),
    ).toBe(0);
  });

  it('perfil completo (onboarding + 3 fotos + 3 intereses) = 100%', () => {
    expect(
      computeProfileCompletionPct({
        hasName: true,
        hasBirthDate: true,
        hasGender: true,
        hasSeeking: true,
        hasCity: true,
        photoCount: 3,
        hasBio: true,
        interestCount: 3,
      }),
    ).toBe(100);
  });

  it('perfil mínimo de onboarding (1 foto, sin intereses) queda incompleto', () => {
    const pct = computeProfileCompletionPct({
      hasName: true,
      hasBirthDate: true,
      hasGender: true,
      hasSeeking: true,
      hasCity: true,
      photoCount: 1,
      hasBio: true,
      interestCount: 0,
    });
    expect(pct).toBeGreaterThan(0);
    expect(pct).toBeLessThan(100);
  });
});

describe('edad mínima (brief sección 16/24 — 18 años duros)', () => {
  const today = new Date('2026-06-15T00:00:00Z');

  it('cumple exactamente 18 hoy: es mayor de edad', () => {
    expect(isOldEnough('2008-06-15', today, DEFAULT_APP_CONFIG)).toBe(true);
  });

  it('cumple 18 mañana: todavía NO es mayor de edad', () => {
    expect(isOldEnough('2008-06-16', today, DEFAULT_APP_CONFIG)).toBe(false);
  });

  it('17 años: no es mayor de edad', () => {
    expect(isOldEnough('2009-01-01', today, DEFAULT_APP_CONFIG)).toBe(false);
  });

  it('30 años: es mayor de edad', () => {
    expect(isOldEnough('1996-01-01', today, DEFAULT_APP_CONFIG)).toBe(true);
  });
});

describe('rate limiting por antigüedad de cuenta (antispam)', () => {
  it('cuenta nueva (< 48h) tiene el límite reducido por el factor configurado', () => {
    expect(effectiveRateLimit(20, 5, DEFAULT_APP_CONFIG)).toBe(6); // floor(20 * 0.3) = 6
  });

  it('cuenta madura (>= 48h) usa el límite base completo', () => {
    expect(effectiveRateLimit(20, 72, DEFAULT_APP_CONFIG)).toBe(20);
  });

  it('el límite reducido nunca baja de 1', () => {
    expect(effectiveRateLimit(1, 0, DEFAULT_APP_CONFIG)).toBe(1);
  });
});
