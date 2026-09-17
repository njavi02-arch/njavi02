import { describe, expect, it } from 'vitest';
import { ageRangeToBirthDateRange } from './discoveryFilters';

describe('ageRangeToBirthDateRange', () => {
  const today = '2026-09-17';

  it('para minAge=maxAge=18, el límite superior es exactamente hace 18 años hoy', () => {
    const { maxBirthDate } = ageRangeToBirthDateRange(18, 18, today);
    expect(maxBirthDate).toBe('2008-09-17');
  });

  it('alguien que cumple 18 justo hoy queda incluido (birth_date == maxBirthDate)', () => {
    const { maxBirthDate } = ageRangeToBirthDateRange(18, 99, today);
    expect(maxBirthDate).toBe('2008-09-17');
  });

  it('alguien que cumple 18 mañana queda excluido de min_age=18 (nacido un día después del límite)', () => {
    const { maxBirthDate } = ageRangeToBirthDateRange(18, 99, today);
    expect('2008-09-18' > maxBirthDate).toBe(true);
  });

  it('el límite inferior corresponde a quien cumple maxAge+1 mañana (el día después del límite ya no vale)', () => {
    const { minBirthDate } = ageRangeToBirthDateRange(18, 30, today);
    // Alguien nacido el 2026-09-17 menos 31 años cumpliría 31 hoy → debe quedar excluido;
    // el primer día válido es un día después de esa fecha.
    expect(minBirthDate).toBe('1995-09-18');
  });

  it('rango típico min=25 max=35 produce un rango de fechas coherente (min < max)', () => {
    const { minBirthDate, maxBirthDate } = ageRangeToBirthDateRange(25, 35, today);
    expect(minBirthDate < maxBirthDate).toBe(true);
  });

  it('con min=max=18 el rango cubre exactamente un año de nacimientos', () => {
    const { minBirthDate, maxBirthDate } = ageRangeToBirthDateRange(18, 18, today);
    expect(minBirthDate).toBe('2007-09-18');
    expect(maxBirthDate).toBe('2008-09-17');
  });
});
