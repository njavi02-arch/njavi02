/** Algoritmm de compatibilidad: calcula % de match entre dos perfiles basado en
 * intereses compartidos, verificación, completitud de perfil, actividad y intención de búsqueda. */

import type { SeekingIntent } from './types';

export interface MatchScore {
  percentage: number; // 0-100
  breakdown: {
    sharedInterests: number; // 0-100
    verification: number; // 0 or 100
    profileCompleteness: number; // 0-100
    activityLevel: number; // 0-100
    intentAlignment: number; // 0 or 100
  };
}

/**
 * Calcula compatibilidad entre currentUser e otherProfile.
 * Pesos: intereses compartidos (40%), verificación (15%), completitud (15%),
 * actividad (15%), alineación de intención (15%).
 */
export function calculateMatchScore(
  currentUserInterests: string[],
  otherProfileInterests: string[],
  otherProfileIsVerified: boolean,
  otherProfileCompletionPct: number,
  otherProfileLastActiveAt: string,
  currentUserSeekingIntents: SeekingIntent[],
  otherProfileSeekingIntents: SeekingIntent[],
): MatchScore {
  // Intereses compartidos (0-100)
  const currentSet = new Set(currentUserInterests.map((i) => i.toLowerCase()));
  const otherSet = new Set(otherProfileInterests.map((i) => i.toLowerCase()));
  const intersection = [...currentSet].filter((i) => otherSet.has(i)).length;
  const union = new Set([...currentSet, ...otherSet]).size;
  const sharedInterestsScore = union > 0 ? (intersection / union) * 100 : 0;

  // Verificación (0 o 100)
  const verificationScore = otherProfileIsVerified ? 100 : 0;

  // Completitud de perfil (0-100, ya viene en %)
  const completenessScore = otherProfileCompletionPct || 0;

  // Actividad (0-100: activo hoy = 100, activo esta semana = 75, hace más = 50)
  const now = new Date();
  const lastActive = new Date(otherProfileLastActiveAt);
  const hoursSinceActive = (now.getTime() - lastActive.getTime()) / (1000 * 60 * 60);
  let activityScore = 0;
  if (hoursSinceActive < 24) {
    activityScore = 100; // Activo hoy
  } else if (hoursSinceActive < 168) {
    activityScore = 75; // Activo esta semana
  } else if (hoursSinceActive < 720) {
    activityScore = 50; // Hace menos de un mes
  } else {
    activityScore = 25; // Hace más de un mes
  }

  // Alineación de intención (0 o 100)
  const intentAlignmentScore = areIntentsCompatible(currentUserSeekingIntents, otherProfileSeekingIntents) ? 100 : 0;

  // Promedio ponderado
  const percentage = Math.round(
    sharedInterestsScore * 0.4 + verificationScore * 0.15 + completenessScore * 0.15 + activityScore * 0.15 + intentAlignmentScore * 0.15,
  );

  return {
    percentage: Math.min(100, Math.max(0, percentage)),
    breakdown: {
      sharedInterests: Math.round(sharedInterestsScore),
      verification: verificationScore,
      profileCompleteness: completenessScore,
      activityLevel: activityScore,
      intentAlignment: intentAlignmentScore,
    },
  };
}

function areIntentsCompatible(intents1: SeekingIntent[], intents2: SeekingIntent[]): boolean {
  // 'social' es compatible con todo (significa usuario flexible)
  const set1 = new Set(intents1);
  const set2 = new Set(intents2);
  if (set1.has('social') || set2.has('social')) return true;
  // Si hay overlap en las intenciones, compatible
  return [...set1].some((intent) => set2.has(intent));
}

/** Retorna un emoji y label basado en el % de compatibilidad. */
export function getMatchLabel(percentage: number): { emoji: string; label: string } {
  if (percentage >= 80) return { emoji: '🔥', label: 'Excelente match' };
  if (percentage >= 60) return { emoji: '💚', label: 'Buen match' };
  if (percentage >= 40) return { emoji: '👍', label: 'Potencial' };
  return { emoji: '🤔', label: 'Poco probable' };
}
