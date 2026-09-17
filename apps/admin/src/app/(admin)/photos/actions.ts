'use server';

import { revalidatePath } from 'next/cache';
import { supabaseAdmin } from '@/lib/supabaseAdmin';

export async function moderatePhoto(photoId: string, status: 'approved' | 'rejected') {
  const { error } = await supabaseAdmin.from('photos').update({ moderation_status: status }).eq('id', photoId);
  if (error) throw new Error(error.message);
  revalidatePath('/photos');
}
