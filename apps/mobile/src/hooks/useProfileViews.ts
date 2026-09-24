import { useQuery } from '@tanstack/react-query';
import { getProfileViewsCount } from '../services/profileViews';
import { useAuthStore } from '../store/authStore';

export function useProfileViewsCount() {
  const session = useAuthStore((s) => s.session);
  return useQuery({
    queryKey: ['profile-views-count', session?.user.id],
    queryFn: () => getProfileViewsCount(session!.user.id),
    enabled: Boolean(session),
    staleTime: 1000 * 60 * 5, // 5 minutes
  });
}
