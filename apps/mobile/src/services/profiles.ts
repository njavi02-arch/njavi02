import { supabase } from '../lib/supabase';
import { computeProfileCompletionPct } from '@orbita/shared';
import type { Gender, SeekingIntent } from '@orbita/shared';
import type { InterestRow, PhotoRow, ProfileRow } from '../types/database';

export interface OnboardingProfileInput {
  id: string;
  displayName: string;
  birthDate: string; // YYYY-MM-DD
  gender: Gender;
  seeking: SeekingIntent[];
  city: string;
  bio: string;
  interestIds: string[];
}

/** Crea el perfil (paso final del onboarding) — dispara handle_new_profile() en la BD,
 * que crea wallets, preferencias y concede los créditos de mensaje iniciales. */
export async function createProfile(input: OnboardingProfileInput): Promise<ProfileRow> {
  const { data, error } = await supabase
    .from('profiles')
    .insert({
      id: input.id,
      display_name: input.displayName,
      birth_date: input.birthDate,
      gender: input.gender,
      seeking: input.seeking,
      city: input.city,
      bio: input.bio,
      onboarding_completed_at: new Date().toISOString(),
    })
    .select()
    .single();

  if (error) throw error;

  if (input.interestIds.length > 0) {
    const rows = input.interestIds.map((interest_id) => ({ profile_id: input.id, interest_id }));
    const { error: interestsError } = await supabase.from('profile_interests').insert(rows);
    if (interestsError) throw interestsError;
  }

  return data as ProfileRow;
}

export async function getMyProfile(userId: string): Promise<ProfileRow | null> {
  const { data, error } = await supabase.from('profiles').select('*').eq('id', userId).maybeSingle();
  if (error) throw error;
  return data as ProfileRow | null;
}

export async function getProfileById(profileId: string): Promise<ProfileRow | null> {
  const { data, error } = await supabase.from('profiles').select('*').eq('id', profileId).maybeSingle();
  if (error) throw error;
  return data as ProfileRow | null;
}

export async function updateMyProfile(userId: string, patch: Partial<ProfileRow>): Promise<void> {
  const { error } = await supabase.from('profiles').update(patch).eq('id', userId);
  if (error) throw error;
}

export async function listInterests(): Promise<InterestRow[]> {
  const { data, error } = await supabase.from('interests').select('*').order('category');
  if (error) throw error;
  return (data ?? []) as InterestRow[];
}

export async function getProfileInterestIds(profileId: string): Promise<string[]> {
  const { data, error } = await supabase.from('profile_interests').select('interest_id').eq('profile_id', profileId);
  if (error) throw error;
  return (data ?? []).map((row) => row.interest_id as string);
}

export async function setProfileInterestSelected(
  profileId: string,
  interestId: string,
  selected: boolean,
): Promise<void> {
  if (selected) {
    const { error } = await supabase.from('profile_interests').insert({ profile_id: profileId, interest_id: interestId });
    if (error && error.code !== '23505') throw error;
  } else {
    const { error } = await supabase
      .from('profile_interests')
      .delete()
      .eq('profile_id', profileId)
      .eq('interest_id', interestId);
    if (error) throw error;
  }
}

export async function getPhotosForProfile(profileId: string): Promise<PhotoRow[]> {
  const { data, error } = await supabase
    .from('photos')
    .select('*')
    .eq('profile_id', profileId)
    .order('position');
  if (error) throw error;
  return (data ?? []) as PhotoRow[];
}

export interface UploadPhotoInput {
  profileId: string;
  position: number;
  fileUri: string;
  contentType: string;
}

/** Sube una foto al bucket `photos` de Supabase Storage y registra la fila en `photos`.
 * Queda en moderation_status='pending' hasta que el panel admin la apruebe. */
export async function uploadProfilePhoto(input: UploadPhotoInput): Promise<PhotoRow> {
  const ext = input.contentType.split('/')[1] ?? 'jpg';
  const storagePath = `${input.profileId}/${input.position}-${Date.now()}.${ext}`;

  const response = await fetch(input.fileUri);
  const blob = await response.blob();

  const { error: uploadError } = await supabase.storage.from('photos').upload(storagePath, blob, {
    contentType: input.contentType,
    upsert: true,
  });
  if (uploadError) throw uploadError;

  const { data: publicUrlData } = supabase.storage.from('photos').getPublicUrl(storagePath);

  const { data, error } = await supabase
    .from('photos')
    .upsert(
      {
        profile_id: input.profileId,
        position: input.position,
        storage_path: storagePath,
        url: publicUrlData.publicUrl,
        moderation_status: 'pending',
      },
      { onConflict: 'profile_id,position' },
    )
    .select()
    .single();

  if (error) throw error;
  return data as PhotoRow;
}

export async function deleteProfilePhoto(photoId: string): Promise<void> {
  const { error } = await supabase.from('photos').delete().eq('id', photoId);
  if (error) throw error;
}

export function computeCompletionFromProfile(
  profile: ProfileRow,
  photoCount: number,
  interestCount: number,
): number {
  return computeProfileCompletionPct({
    hasName: Boolean(profile.display_name),
    hasBirthDate: Boolean(profile.birth_date),
    hasGender: profile.gender !== 'unspecified',
    hasSeeking: profile.seeking.length > 0,
    hasCity: Boolean(profile.city),
    photoCount,
    hasBio: profile.bio.trim().length > 0,
    interestCount,
  });
}
