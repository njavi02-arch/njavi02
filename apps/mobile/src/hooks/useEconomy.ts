import { useQuery, useQueryClient } from '@tanstack/react-query';
import { fetchAppConfig, fetchDailyStreak, fetchWallets } from '../services/economy';
import { useAuthStore } from '../store/authStore';

export function useAppConfig() {
  return useQuery({ queryKey: ['app-config'], queryFn: fetchAppConfig, staleTime: 5 * 60 * 1000 });
}

export function useWallets() {
  const session = useAuthStore((s) => s.session);
  return useQuery({
    queryKey: ['wallets', session?.user.id],
    queryFn: () => fetchWallets(session!.user.id),
    enabled: Boolean(session),
  });
}

export function useDailyStreak() {
  const session = useAuthStore((s) => s.session);
  return useQuery({
    queryKey: ['streak', session?.user.id],
    queryFn: () => fetchDailyStreak(session!.user.id),
    enabled: Boolean(session),
  });
}

export function useInvalidateEconomy() {
  const queryClient = useQueryClient();
  return () => {
    queryClient.invalidateQueries({ queryKey: ['wallets'] });
    queryClient.invalidateQueries({ queryKey: ['streak'] });
  };
}
