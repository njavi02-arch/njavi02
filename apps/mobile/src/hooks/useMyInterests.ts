import { useQuery } from '@tanstack/react-query';
import { getProfileInterestNames } from '../services/profiles';
import { useAuthStore } from '../store/authStore';

export function useMyInterests() {
  const profileId = useAuthStore((s) => s.profile?.id);
  return useQuery({
    queryKey: ['my-interest-names', profileId],
    queryFn: () => getProfileInterestNames(profileId!),
    enabled: Boolean(profileId),
  });
}
