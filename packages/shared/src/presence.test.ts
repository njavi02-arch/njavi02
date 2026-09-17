import { describe, expect, it } from 'vitest';
import { getActivityStatus } from './presence';

describe('getActivityStatus', () => {
  const now = new Date('2026-06-15T12:00:00Z');

  it('hace 5 minutos -> Activo ahora', () => {
    expect(getActivityStatus('2026-06-15T11:55:00Z', now)).toEqual({ level: 'online', label: 'Activo ahora' });
  });

  it('justo en el límite de 2 horas menos 1 segundo -> Activo ahora', () => {
    expect(getActivityStatus('2026-06-15T10:00:01Z', now).level).toBe('online');
  });

  it('justo en el límite de 2 horas exactas -> ya no es "Activo ahora"', () => {
    expect(getActivityStatus('2026-06-15T10:00:00Z', now).level).toBe('today');
  });

  it('hace 10 horas -> Activo hoy', () => {
    expect(getActivityStatus('2026-06-15T02:00:00Z', now)).toEqual({ level: 'today', label: 'Activo hoy' });
  });

  it('hace 25 horas -> sin indicador (privacidad, como Bumble a partir de cierto punto)', () => {
    expect(getActivityStatus('2026-06-14T11:00:00Z', now)).toEqual({ level: null, label: null });
  });

  it('hace varios días -> sin indicador', () => {
    expect(getActivityStatus('2026-06-01T12:00:00Z', now).level).toBeNull();
  });

  it('reloj del dispositivo adelantado (última actividad "en el futuro") -> Activo ahora, nunca crashea', () => {
    expect(getActivityStatus('2026-06-15T13:00:00Z', now)).toEqual({ level: 'online', label: 'Activo ahora' });
  });
});
