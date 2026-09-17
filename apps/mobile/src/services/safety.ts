import { supabase } from '../lib/supabase';
import { unregisterAllPushTokens } from './notifications';
import type { ReportRow } from '../types/database';

export async function blockUser(blockerId: string, blockedId: string): Promise<void> {
  const { error } = await supabase.from('blocks').insert({ blocker_id: blockerId, blocked_id: blockedId });
  if (error) throw error;
}

export async function unblockUser(blockerId: string, blockedId: string): Promise<void> {
  const { error } = await supabase.from('blocks').delete().eq('blocker_id', blockerId).eq('blocked_id', blockedId);
  if (error) throw error;
}

export interface BlockedUserEntry {
  id: string;
  blocked_id: string;
  created_at: string;
  blocked: { display_name: string } | null;
}

export async function listMyBlocks(blockerId: string): Promise<BlockedUserEntry[]> {
  const { data, error } = await supabase
    .from('blocks')
    .select('id, blocked_id, created_at, blocked:profiles!blocks_blocked_id_fkey(display_name)')
    .eq('blocker_id', blockerId)
    .order('created_at', { ascending: false });
  if (error) throw error;
  return (data ?? []) as unknown as BlockedUserEntry[];
}

export interface ReportInput {
  reporterId: string;
  reportedId: string;
  reason: ReportRow['reason'];
  details?: string;
  relatedMessageId?: string;
}

export async function reportUser(input: ReportInput): Promise<void> {
  const { data: allowed, error: rateLimitError } = await supabase.rpc('check_and_record_rate_limit', {
    p_profile_id: input.reporterId,
    p_action_type: 'report',
    p_base_limit: 10, // app_config.report_rate_limit_per_day
    p_window: '1 day',
  });
  if (rateLimitError) throw rateLimitError;
  if (!allowed) {
    throw new Error('Has enviado demasiados reportes hoy. Inténtalo de nuevo mañana.');
  }

  const { error } = await supabase.from('reports').insert({
    reporter_id: input.reporterId,
    reported_id: input.reportedId,
    reason: input.reason,
    details: input.details ?? null,
    related_message_id: input.relatedMessageId ?? null,
  });
  if (error) throw error;
}

export async function deleteMyAccount(userId: string): Promise<void> {
  // Soft delete + anonimización — ver docs/03-database.md §2 y docs/06-security-and-privacy.md.
  const { error } = await supabase
    .from('profiles')
    .update({
      status: 'deleted',
      display_name: 'Usuario eliminado',
      bio: '',
      city: null,
      latitude: null,
      longitude: null,
      deleted_at: new Date().toISOString(),
    })
    .eq('id', userId);
  if (error) throw error;

  // Una cuenta eliminada no debe poder recibir push a partir de ahora.
  await unregisterAllPushTokens(userId).catch(() => {});
}
