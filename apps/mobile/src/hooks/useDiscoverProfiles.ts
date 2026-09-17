import { useQuery } from '@tanstack/react-query';
import { fetchDiscoverProfiles } from '../services/discover';
import { useAuthStore } from '../store/authStore';

export function useDiscoverProfiles() {
  const session = useAuthStore((s) => s.session);
  return useQuery({
    queryKey: ['discover', session?.user.id],
    queryFn: () => fetchDiscoverProfiles(session!.user.id),
    enabled: Boolean(session),
  });
}
