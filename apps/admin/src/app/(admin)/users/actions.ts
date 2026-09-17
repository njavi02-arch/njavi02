'use server';

import { revalidatePath } from 'next/cache';
import { supabaseAdmin } from '@/lib/supabaseAdmin';
import type { ProfileStatus } from '@orbita/shared';

export async function setUserStatus(profileId: string, status: ProfileStatus) {
  const { error } = await supabaseAdmin.from('profiles').update({ status }).eq('id', profileId);
  if (error) throw new Error(error.message);
  revalidatePath('/users');
}

export async function grantCoinsToUser(profileId: string, amount: number) {
  const { error } = await supabaseAdmin.rpc('grant_coins', {
    p_profile_id: profileId,
    p_amount: amount,
    p_reason: 'admin_grant',
  });
  if (error) throw new Error(error.message);
  revalidatePath('/users');
}
