import { supabase } from '../lib/supabase';

export async function getProfileViewsCount(profileId: string): Promise<number> {
  const { count, error } = await supabase
    .from('profile_views')
    .select('*', { count: 'exact', head: true })
    .eq('viewed_id', profileId);

  if (error) throw error;
  return count ?? 0;
}

export async function getRecentProfileViewers(profileId: string, limit = 5): Promise<
  Array<{
    viewerId: string;
    displayName: string;
    viewedAt: string;
  }>
> {
  const { data, error } = await supabase
    .from('profile_views')
    .select('viewer_id, profiles!profile_views_viewer_id_fkey(display_name), created_at')
    .eq('viewed_id', profileId)
    .order('created_at', { ascending: false })
    .limit(limit);

  if (error) throw error;

  return (data ?? [])
    .map((row: any) => ({
      viewerId: row.viewer_id,
      displayName: row.profiles?.display_name || 'Anónimo',
      viewedAt: row.created_at,
    }));
}
