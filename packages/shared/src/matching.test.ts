import { describe, expect, it } from 'vitest';
import { calculateMatchScore, getMatchLabel } from './matching';

describe('matching', () => {
  describe('calculateMatchScore', () => {
    it('100% cuando intereses y verificación perfectos', () => {
      const score = calculateMatchScore(
        ['música', 'deportes', 'viajes'],
        ['música', 'deportes', 'viajes'],
        true,
        100,
        new Date().toISOString(),
        ['dating'],
        ['dating'],
      );
      expect(score.percentage).toBe(100);
      expect(score.breakdown.sharedInterests).toBe(100);
      expect(score.breakdown.verification).toBe(100);
    });

    it('0% cuando no hay intereses compartidos', () => {
      const score = calculateMatchScore(
        ['música', 'deportes'],
        ['libros', 'arte'],
        false,
        0,
        new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString(),
        ['dating'],
        ['friendship'],
      );
      expect(score.percentage).toBeLessThan(30);
      expect(score.breakdown.sharedInterests).toBe(0);
    });

    it('calcula intereses parcialmente compartidos', () => {
      const score = calculateMatchScore(
        ['música', 'deportes', 'viajes'],
        ['música', 'cine', 'comida'],
        true,
        80,
        new Date().toISOString(),
        ['dating'],
        ['dating'],
      );
      // 1 de 5 únicos = 20% de intereses
      // + 100 * 0.15 (verificación) + 80 * 0.15 (completitud) + 100 * 0.15 (actividad) + 100 * 0.15 (intención)
      // = 20*0.4 + 15 + 12 + 15 + 15 = 8 + 57 = 65
      expect(score.percentage).toBeGreaterThan(60);
      expect(score.percentage).toBeLessThan(70);
    });

    it('actividad impacta el score', () => {
      const hoursAgo = (hours: number) => new Date(Date.now() - hours * 60 * 60 * 1000).toISOString();

      const scoreActive = calculateMatchScore(
        ['música'],
        ['música'],
        false,
        0,
        hoursAgo(6),
        ['social'],
        ['social'],
      );
      const scoreInactive = calculateMatchScore(
        ['música'],
        ['música'],
        false,
        0,
        hoursAgo(500),
        ['social'],
        ['social'],
      );
      expect(scoreActive.percentage).toBeGreaterThan(scoreInactive.percentage);
      expect(scoreActive.breakdown.activityLevel).toBe(100);
      expect(scoreInactive.breakdown.activityLevel).toBeLessThan(100);
    });

    it('social intent es compatible con todo', () => {
      const score1 = calculateMatchScore(['a'], ['a'], false, 0, new Date().toISOString(), ['social'], ['dating']);
      const score2 = calculateMatchScore(['a'], ['a'], false, 0, new Date().toISOString(), ['dating'], ['social']);
      const score3 = calculateMatchScore(['a'], ['a'], false, 0, new Date().toISOString(), ['friendship'], ['social']);
      expect(score1.breakdown.intentAlignment).toBe(100);
      expect(score2.breakdown.intentAlignment).toBe(100);
      expect(score3.breakdown.intentAlignment).toBe(100);
    });

    it('dating + friendship no son compatibles', () => {
      const score = calculateMatchScore(
        ['música'],
        ['música'],
        true,
        100,
        new Date().toISOString(),
        ['dating'],
        ['friendship'],
      );
      expect(score.breakdown.intentAlignment).toBe(0);
    });
  });

  describe('getMatchLabel', () => {
    it('etiqueta para excelente match (80+)', () => {
      const label = getMatchLabel(85);
      expect(label.emoji).toBe('🔥');
      expect(label.label).toBe('Excelente match');
    });

    it('etiqueta para buen match (60-79)', () => {
      const label = getMatchLabel(70);
      expect(label.emoji).toBe('💚');
      expect(label.label).toBe('Buen match');
    });

    it('etiqueta para potencial (40-59)', () => {
      const label = getMatchLabel(50);
      expect(label.emoji).toBe('👍');
      expect(label.label).toBe('Potencial');
    });

    it('etiqueta para poco probable (<40)', () => {
      const label = getMatchLabel(30);
      expect(label.emoji).toBe('🤔');
      expect(label.label).toBe('Poco probable');
    });
  });
});
