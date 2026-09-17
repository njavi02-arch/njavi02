import { useEffect } from 'react';
import { useAuthStore } from '../store/authStore';
import { registerPushToken } from '../services/notifications';

/** Registra el token de push del dispositivo en cuanto hay un perfil cargado. Falla en
 * silencio (permiso denegado, web, simulador) — nunca debe bloquear el uso de la app. */
export function useRegisterPushNotifications() {
  const profileId = useAuthStore((s) => s.profile?.id);

  useEffect(() => {
    if (!profileId) return;
    registerPushToken(profileId).catch(() => {});
  }, [profileId]);
}
