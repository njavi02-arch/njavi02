// Lógica pura para traducir las preferencias de descubrimiento (edad mínima/máxima,
// captadas en el onboarding en `user_preferences` pero nunca aplicadas al feed — bug real
// encontrado en esta ronda, ver PRODUCT_BRAIN.md) en el rango de `birth_date` que hay que
// pedirle a la base de datos, ya que Postgres no puede indexar "edad calculada" de forma
// eficiente pero sí un rango de fechas.

function toIsoDate(d: Date): string {
  return d.toISOString().slice(0, 10);
}

function subtractYearsUtc(iso: string, years: number): Date {
  const [y, m, d] = iso.split('-').map(Number);
  return new Date(Date.UTC(y - years, m - 1, d));
}

function addDaysUtc(d: Date, days: number): Date {
  return new Date(d.getTime() + days * 24 * 60 * 60 * 1000);
}

export interface BirthDateRange {
  /** `birth_date >= minBirthDate` — la persona no supera maxAge. */
  minBirthDate: string;
  /** `birth_date <= maxBirthDate` — la persona ya cumplió minAge. */
  maxBirthDate: string;
}

/**
 * Convierte [minAge, maxAge] en el rango de fecha de nacimiento equivalente a día de hoy
 * (`todayIso` en formato YYYY-MM-DD, por defecto hoy en UTC). Alguien tiene exactamente
 * `edad` años si su `birth_date` está en (hoy − (edad+1) años, hoy − edad años].
 */
export function ageRangeToBirthDateRange(minAge: number, maxAge: number, todayIso?: string): BirthDateRange {
  const today = todayIso ?? toIsoDate(new Date());
  const maxBirthDate = toIsoDate(subtractYearsUtc(today, minAge));
  const minBirthDate = toIsoDate(addDaysUtc(subtractYearsUtc(today, maxAge + 1), 1));
  return { minBirthDate, maxBirthDate };
}
