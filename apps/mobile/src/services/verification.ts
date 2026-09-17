import { supabase } from '../lib/supabase';
import type { VerificationRequestRow } from '../types/database';

/** Sube la selfie de verificación y crea la solicitud (cola de moderación manual en el
 * panel admin — ver PRODUCT_BRAIN.md: decidimos no usar reconocimiento facial de terceros
 * porque implicaría contratar un servicio externo). */
export async function requestVerification(profileId: string, fileUri: string): Promise<VerificationRequestRow> {
  const storagePath = `verification/${profileId}/${Date.now()}.jpg`;

  const response = await fetch(fileUri);
  const blob = await response.blob();

  const { error: uploadError } = await supabase.storage.from('photos').upload(storagePath, blob, {
    contentType: 'image/jpeg',
  });
  if (uploadError) throw uploadError;

  const { data: publicUrlData } = supabase.storage.from('photos').getPublicUrl(storagePath);

  const { data, error } = await supabase
    .from('verification_requests')
    .insert({ profile_id: profileId, selfie_url: publicUrlData.publicUrl })
    .select()
    .single();
  if (error) throw error;
  return data as VerificationRequestRow;
}

export async function getMyVerificationRequest(profileId: string): Promise<VerificationRequestRow | null> {
  const { data, error } = await supabase
    .from('verification_requests')
    .select('*')
    .eq('profile_id', profileId)
    .order('created_at', { ascending: false })
    .limit(1)
    .maybeSingle();
  if (error) throw error;
  return data as VerificationRequestRow | null;
}
