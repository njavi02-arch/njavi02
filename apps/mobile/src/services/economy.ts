import { supabase } from '../lib/supabase';
import { DEFAULT_APP_CONFIG } from '@orbita/shared';
import type { AppConfig } from '@orbita/shared';
import type {
  CoinWalletRow,
  DailyStreakRow,
  MessageCreditWalletRow,
  ProfileRow,
  ProfileViewRow,
  SuperLikeCreditWalletRow,
} from '../types/database';

/** Lee app_config y la funde con los defaults locales (por si falta alguna clave nueva
 * que el panel admin todavía no ha sembrado en este entorno). Nunca hardcodear cifras de
 * negocio fuera de config-defaults.ts / esta función. */
export async function fetchAppConfig(): Promise<AppConfig> {
  const { data, error } = await supabase.from('app_config').select('key, value');
  if (error) throw error;

  const overrides = Object.fromEntries((data ?? []).map((row) => [row.key as string, row.value]));
  return { ...DEFAULT_APP_CONFIG, ...overrides } as AppConfig;
}

export interface Wallets {
  coins: number;
  messageCredits: number;
  superLikeCredits: number;
}

export async function fetchWallets(profileId: string): Promise<Wallets> {
  const [coinRes, creditRes, superLikeRes] = await Promise.all([
    supabase.from('coin_wallets').select('balance').eq('profile_id', profileId).maybeSingle(),
    supabase.from('message_credit_wallets').select('balance').eq('profile_id', profileId).maybeSingle(),
    supabase.from('super_like_credit_wallets').select('balance').eq('profile_id', profileId).maybeSingle(),
  ]);
  if (coinRes.error) throw coinRes.error;
  if (creditRes.error) throw creditRes.error;
  if (superLikeRes.error) throw superLikeRes.error;

  return {
    coins: (coinRes.data as CoinWalletRow | null)?.balance ?? 0,
    messageCredits: (creditRes.data as MessageCreditWalletRow | null)?.balance ?? 0,
    superLikeCredits: (superLikeRes.data as SuperLikeCreditWalletRow | null)?.balance ?? 0,
  };
}

export async function fetchDailyStreak(profileId: string): Promise<DailyStreakRow | null> {
  const { data, error } = await supabase.from('daily_streaks').select('*').eq('profile_id', profileId).maybeSingle();
  if (error) throw error;
  return data as DailyStreakRow | null;
}

export interface StreakClaimResult {
  day: number;
  coins: number;
  superLikes: number;
  messageCredits: number;
  currentStreak: number;
}

export async function claimDailyStreak(): Promise<StreakClaimResult> {
  const { data, error } = await supabase.rpc('claim_daily_streak');
  if (error) throw error;
  return data as StreakClaimResult;
}

function todayIso(): string {
  return new Date().toISOString().slice(0, 10);
}

export async function countSuperLikesSentToday(senderId: string): Promise<number> {
  const { count, error } = await supabase
    .from('super_likes')
    .select('id', { count: 'exact', head: true })
    .eq('sender_id', senderId)
    .gte('created_at', `${todayIso()}T00:00:00.000Z`);
  if (error) throw error;
  return count ?? 0;
}

/** Envía un Super Like. Si no quedan gratis hoy, gasta 1 de super_like_credit_wallets
 * (recompensa de racha) o, si tampoco hay, monedas al precio de app_config. */
export async function sendSuperLike(
  senderId: string,
  receiverId: string,
  message: string | undefined,
  config: Pick<AppConfig, 'super_like_daily_free' | 'super_like_coin_cost'>,
): Promise<void> {
  const sentToday = await countSuperLikesSentToday(senderId);
  const isFree = sentToday < config.super_like_daily_free;

  if (!isFree) {
    const wallets = await fetchWallets(senderId);
    if (wallets.superLikeCredits > 0) {
      const { error } = await supabase.rpc('spend_super_like_credit', {
        p_profile_id: senderId,
        p_reason: 'super_like_sent',
      });
      if (error) throw error;
    } else {
      const { error } = await supabase.rpc('spend_coins', {
        p_profile_id: senderId,
        p_amount: config.super_like_coin_cost,
        p_reason: 'super_like_sent',
      });
      if (error) throw error;
    }
  }

  const { error: insertError } = await supabase
    .from('super_likes')
    .insert({ sender_id: senderId, receiver_id: receiverId, message: message ?? null });
  if (insertError) throw insertError;
}

export interface ProfileViewerEntry {
  view: ProfileViewRow;
  viewer: Pick<ProfileRow, 'id' | 'display_name'> & { photo_url: string | null };
}

/** "Quién te ha visto" — brief sección 7. */
export async function listWhoViewedMe(profileId: string): Promise<ProfileViewerEntry[]> {
  const { data, error } = await supabase
    .from('profile_views')
    .select('*, viewer:profiles!profile_views_viewer_id_fkey(id, display_name, photos(url, position))')
    .eq('viewed_id', profileId)
    .order('created_at', { ascending: false });
  if (error) throw error;

  return (data ?? []).map((row: any) => ({
    view: row,
    viewer: {
      id: row.viewer.id,
      display_name: row.viewer.display_name,
      photo_url: [...(row.viewer.photos ?? [])].sort((a: any, b: any) => a.position - b.position)[0]?.url ?? null,
    },
  }));
}

export interface SecretAdmirerEntry {
  viewerId: string;
  timesViewed: number;
  superLiked: boolean;
  revealed: boolean;
  displayName: string | null; // solo presente si `revealed`
  photoUrl: string | null;
}

/** Admiradores secretos (brief sección 8): gente que vio 2+ veces o super-likeó, sin
 * conversación abierta todavía. La identidad solo se incluye si ya hay un
 * admirer_reveals para ese viewer. */
export async function listSecretAdmirers(profileId: string): Promise<SecretAdmirerEntry[]> {
  const [{ data: views, error: viewsError }, { data: superLikes, error: slError }, { data: reveals, error: revealsError }, { data: conversations, error: convError }] =
    await Promise.all([
      supabase.from('profile_views').select('viewer_id').eq('viewed_id', profileId),
      supabase.from('super_likes').select('sender_id').eq('receiver_id', profileId),
      supabase.from('admirer_reveals').select('revealed_viewer_id').eq('profile_id', profileId),
      supabase.from('conversations').select('user_a_id, user_b_id').or(`user_a_id.eq.${profileId},user_b_id.eq.${profileId}`),
    ]);
  if (viewsError) throw viewsError;
  if (slError) throw slError;
  if (revealsError) throw revealsError;
  if (convError) throw convError;

  const conversationPartnerIds = new Set(
    (conversations ?? []).map((c: any) => (c.user_a_id === profileId ? c.user_b_id : c.user_a_id)),
  );
  const revealedIds = new Set((reveals ?? []).map((r: any) => r.revealed_viewer_id as string));
  const superLikedIds = new Set((superLikes ?? []).map((s: any) => s.sender_id as string));

  const viewCounts = new Map<string, number>();
  for (const v of views ?? []) {
    viewCounts.set(v.viewer_id, (viewCounts.get(v.viewer_id) ?? 0) + 1);
  }

  const candidateIds = new Set<string>([...viewCounts.keys(), ...superLikedIds]);
  const admirerIds = [...candidateIds].filter((id) => {
    if (conversationPartnerIds.has(id)) return false;
    const views2 = viewCounts.get(id) ?? 0;
    return views2 >= 2 || superLikedIds.has(id);
  });

  if (admirerIds.length === 0) return [];

  const revealedNeeded = admirerIds.filter((id) => revealedIds.has(id));
  let profilesById = new Map<string, { display_name: string; photo_url: string | null }>();
  if (revealedNeeded.length > 0) {
    const { data: profiles, error: profilesError } = await supabase
      .from('profiles')
      .select('id, display_name, photos(url, position)')
      .in('id', revealedNeeded);
    if (profilesError) throw profilesError;
    profilesById = new Map(
      (profiles ?? []).map((p: any) => [
        p.id,
        {
          display_name: p.display_name,
          photo_url: [...(p.photos ?? [])].sort((a: any, b: any) => a.position - b.position)[0]?.url ?? null,
        },
      ]),
    );
  }

  return admirerIds.map((id) => ({
    viewerId: id,
    timesViewed: viewCounts.get(id) ?? 0,
    superLiked: superLikedIds.has(id),
    revealed: revealedIds.has(id),
    displayName: profilesById.get(id)?.display_name ?? null,
    photoUrl: profilesById.get(id)?.photo_url ?? null,
  }));
}

export async function revealSecretAdmirer(admirerProfileId: string): Promise<void> {
  const { error } = await supabase.rpc('reveal_secret_admirer', { p_admirer_profile_id: admirerProfileId });
  if (error) throw error;
}

export async function unlockPhotos(targetProfileId: string, method: 'coins' | 'premium'): Promise<void> {
  const { error } = await supabase.rpc('unlock_photos', { p_target_profile_id: targetProfileId, p_method: method });
  if (error) throw error;
}

export async function hasUnlockedPhotos(viewerId: string, targetProfileId: string): Promise<boolean> {
  const { data, error } = await supabase
    .from('photo_unlocks')
    .select('id')
    .eq('viewer_id', viewerId)
    .eq('target_profile_id', targetProfileId)
    .maybeSingle();
  if (error) throw error;
  return Boolean(data);
}
