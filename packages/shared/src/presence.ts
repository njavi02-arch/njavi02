// Lógica pura del indicador de actividad ("Activo ahora" / "Activo hoy") — brief
// implícito en la investigación de mercado (ver PRODUCT_BRAIN.md → INVESTIGACIÓN):
// Hinge usa dos niveles, Tinder uno (punto verde a 2h), Bumble ninguno por privacidad.
// Orbita adopta el punto medio: dos niveles, nunca la hora exacta de última conexión.

export type ActivityLevel = 'online' | 'today' | null;

export interface ActivityStatus {
  level: ActivityLevel;
  label: string | null;
}

const ONLINE_THRESHOLD_MS = 2 * 60 * 60 * 1000; // 2 horas, igual de umbral que Tinder
const TODAY_THRESHOLD_MS = 24 * 60 * 60 * 1000; // 24 horas, igual de umbral que Tinder

export function getActivityStatus(lastActiveAtIso: string, now: Date = new Date()): ActivityStatus {
  const lastActive = new Date(lastActiveAtIso).getTime();
  const diff = now.getTime() - lastActive;

  if (diff < 0) {
    // Reloj del dispositivo desincronizado u otro caso límite — nunca mostrar "en el futuro".
    return { level: 'online', label: 'Activo ahora' };
  }
  if (diff < ONLINE_THRESHOLD_MS) {
    return { level: 'online', label: 'Activo ahora' };
  }
  if (diff < TODAY_THRESHOLD_MS) {
    return { level: 'today', label: 'Activo hoy' };
  }
  return { level: null, label: null };
}
