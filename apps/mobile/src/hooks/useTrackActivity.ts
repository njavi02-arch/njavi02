import { useEffect, useRef } from 'react';
import { AppState } from 'react-native';
import { useAuthStore } from '../store/authStore';
import { touchLastActive } from '../services/profiles';
import { notifyStreakAtRiskIfNeeded } from '../services/economy';

const HEARTBEAT_MS = 3 * 60 * 1000; // cada 3 minutos en primer plano

function onAppOpened(profileId: string) {
  touchLastActive(profileId).catch(() => {});
  notifyStreakAtRiskIfNeeded().catch(() => {});
}

/** Mantiene profiles.last_active_at al día mientras la app está en primer plano — es lo
 * que hace real el indicador "Activo ahora"/"Activo hoy" y el orden del feed de
 * descubrimiento por actividad reciente. También dispara (con deduplicación en el
 * servidor) la notificación de racha en riesgo cada vez que se abre la app. */
export function useTrackActivity() {
  const profileId = useAuthStore((s) => s.profile?.id);
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

  useEffect(() => {
    if (!profileId) return;

    onAppOpened(profileId);
    intervalRef.current = setInterval(() => {
      touchLastActive(profileId).catch(() => {});
    }, HEARTBEAT_MS);

    const subscription = AppState.addEventListener('change', (state) => {
      if (state === 'active') {
        onAppOpened(profileId);
      }
    });

    return () => {
      if (intervalRef.current) clearInterval(intervalRef.current);
      subscription.remove();
    };
  }, [profileId]);
}
