import { supabase } from '../lib/supabase';
import { getActiveBoostedProfileIds } from './economy';
import type { ProfilePromptRow, ProfileRow } from '../types/database';

export interface DiscoverProfile extends ProfileRow {
  photos: { url: string; position: number }[];
  interests: string[];
  prompts: Pick<ProfilePromptRow, 'question' | 'answer' | 'position'>[];
  isBoosted: boolean;
}

/**
 * Feed de descubrimiento: perfiles activos, distintos del propio usuario, que no hayan
 * recibido ya una solicitud pendiente/aceptada del usuario actual. Orden: primero quien
 * tenga un Boost activo (ver PRODUCT_BRAIN.md — pagado con monedas, no con dinero real),
 * y dentro de cada grupo, quien haya estado activo más recientemente. El filtrado por
 * bloqueos lo aplica la propia RLS de `profiles` (is_blocked_between).
 */
export async function fetchDiscoverProfiles(currentUserId: string, limit = 20): Promise<DiscoverProfile[]> {
  const [{ data: alreadyContacted, error: contactedError }, boostedIds] = await Promise.all([
    supabase.from('conversation_requests').select('receiver_id').eq('sender_id', currentUserId).in('status', ['pending', 'accepted']),
    getActiveBoostedProfileIds(),
  ]);
  if (contactedError) throw contactedError;

  const excludeIds = new Set((alreadyContacted ?? []).map((r) => r.receiver_id as string));
  excludeIds.add(currentUserId);

  const { data, error } = await supabase
    .from('profiles')
    .select('*, photos(url, position), profile_interests(interests(name)), profile_prompts(question, answer, position)')
    .eq('status', 'active')
    .order('last_active_at', { ascending: false })
    .limit(limit + excludeIds.size);

  if (error) throw error;

  const rows = (data ?? []) as Array<
    ProfileRow & {
      photos: { url: string; position: number }[];
      profile_interests: { interests: { name: string } | null }[];
      profile_prompts: Pick<ProfilePromptRow, 'question' | 'answer' | 'position'>[];
    }
  >;

  return rows
    .filter((row) => !excludeIds.has(row.id))
    .map((row) => ({
      ...row,
      photos: [...row.photos].sort((a, b) => a.position - b.position),
      interests: row.profile_interests.map((pi) => pi.interests?.name).filter((n): n is string => Boolean(n)),
      prompts: [...row.profile_prompts].sort((a, b) => a.position - b.position),
      isBoosted: boostedIds.has(row.id),
    }))
    .sort((a, b) => (a.isBoosted === b.isBoosted ? 0 : a.isBoosted ? -1 : 1))
    .slice(0, limit);
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
