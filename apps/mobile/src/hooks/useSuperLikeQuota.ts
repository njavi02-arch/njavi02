import { useQuery } from '@tanstack/react-query';
import { countSuperLikesSentToday } from '../services/economy';
import { useAuthStore } from '../store/authStore';
import { useAppConfig, useWallets } from './useEconomy';

/** Cuántos Super Likes gratis quedan hoy, y si hay saldo de racha/monedas para uno extra.
 * Puramente informativo para la UI — la validación real y autoritativa ocurre en
 * send_super_like() (supabase/migrations/0002_atomic_actions.sql). */
export function useSuperLikeQuota() {
  const session = useAuthStore((s) => s.session);
  const { data: config } = useAppConfig();
  const { data: wallets } = useWallets();

  const sentTodayQuery = useQuery({
    queryKey: ['super-likes-sent-today', session?.user.id],
    queryFn: () => countSuperLikesSentToday(session!.user.id),
    enabled: Boolean(session),
  });

  const freeLimit = config?.super_like_daily_free ?? 1;
  const sentToday = sentTodayQuery.data ?? 0;
  const freeRemaining = Math.max(0, freeLimit - sentToday);

  return {
    freeRemaining,
    isFree: freeRemaining > 0,
    coinCost: config?.super_like_coin_cost ?? 20,
    superLikeCredits: wallets?.superLikeCredits ?? 0,
  };
}
