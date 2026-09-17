'use server';

import { revalidatePath } from 'next/cache';
import { supabaseAdmin } from '@/lib/supabaseAdmin';
import { requireAdmin } from '@/lib/requireAdmin';

export async function reviewVerification(
  requestId: string,
  status: 'approved' | 'rejected',
  rejectionReason?: string,
) {
  const admin = await requireAdmin();
  const { error } = await supabaseAdmin
    .from('verification_requests')
    .update({
      status,
      reviewed_by: admin.id,
      reviewed_at: new Date().toISOString(),
      rejection_reason: status === 'rejected' ? (rejectionReason ?? 'No coincide con las fotos del perfil') : null,
    })
    .eq('id', requestId);
  if (error) throw new Error(error.message);
  revalidatePath('/verifications');
  revalidatePath('/users');
}
