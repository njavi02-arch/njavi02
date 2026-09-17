import { useQuery } from '@tanstack/react-query';
import { listConversations, listIncomingRequests } from '../services/conversations';
import { useAuthStore } from '../store/authStore';

export function useConversations() {
  const session = useAuthStore((s) => s.session);
  return useQuery({
    queryKey: ['conversations', session?.user.id],
    queryFn: () => listConversations(session!.user.id),
    enabled: Boolean(session),
    refetchInterval: 15000,
  });
}

export function useIncomingRequests() {
  const session = useAuthStore((s) => s.session);
  return useQuery({
    queryKey: ['incoming-requests', session?.user.id],
    queryFn: () => listIncomingRequests(session!.user.id),
    enabled: Boolean(session),
    refetchInterval: 15000,
  });
}
