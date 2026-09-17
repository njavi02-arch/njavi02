import { supabase } from '../lib/supabase';
import type { ProfileRow } from '../types/database';

export interface DiscoverProfile extends ProfileRow {
  photos: { url: string; position: number }[];
  interests: string[];
}

/**
 * Feed de descubrimiento: perfiles activos, distintos del propio usuario, que no hayan
 * recibido ya una solicitud pendiente/aceptada del usuario actual, respetando el orden
 * "más recientemente activos primero". El filtrado por bloqueos lo aplica la propia RLS
 * de `profiles` (is_blocked_between), así que no hace falta repetirlo aquí.
 */
export async function fetchDiscoverProfiles(currentUserId: string, limit = 20): Promise<DiscoverProfile[]> {
  const { data: alreadyContacted, error: contactedError } = await supabase
    .from('conversation_requests')
    .select('receiver_id')
    .eq('sender_id', currentUserId)
    .in('status', ['pending', 'accepted']);
  if (contactedError) throw contactedError;

  const excludeIds = new Set((alreadyContacted ?? []).map((r) => r.receiver_id as string));
  excludeIds.add(currentUserId);

  const { data, error } = await supabase
    .from('profiles')
    .select('*, photos(url, position), profile_interests(interests(name))')
    .eq('status', 'active')
    .order('last_active_at', { ascending: false })
    .limit(limit + excludeIds.size);

  if (error) throw error;

  const rows = (data ?? []) as Array<
    ProfileRow & {
      photos: { url: string; position: number }[];
      profile_interests: { interests: { name: string } | null }[];
    }
  >;

  return rows
    .filter((row) => !excludeIds.has(row.id))
    .slice(0, limit)
    .map((row) => ({
      ...row,
      photos: [...row.photos].sort((a, b) => a.position - b.position),
      interests: row.profile_interests.map((pi) => pi.interests?.name).filter((n): n is string => Boolean(n)),
    }));
}

/** Registra que currentUserId ha visto viewedProfileId (para "Quién te ha visto"). */
export async function recordProfileView(currentUserId: string, viewedProfileId: string): Promise<void> {
  if (currentUserId === viewedProfileId) return;
  const { error } = await supabase.from('profile_views').insert({
    viewer_id: currentUserId,
    viewed_id: viewedProfileId,
  });
  // No relanzamos si ya existe una vista reciente duplicada por doble tap; cualquier
  // otro error sí se propaga.
  if (error && error.code !== '23505') throw error;
}
