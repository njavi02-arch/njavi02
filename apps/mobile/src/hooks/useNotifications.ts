import { useQuery } from '@tanstack/react-query';
import { listNotifications } from '../services/notifications';
import { useAuthStore } from '../store/authStore';

export function useNotifications() {
  const session = useAuthStore((s) => s.session);
  return useQuery({
    queryKey: ['notifications', session?.user.id],
    queryFn: () => listNotifications(session!.user.id),
    enabled: Boolean(session),
    refetchInterval: 20000,
  });
}
