'use server';

import { revalidatePath } from 'next/cache';
import { supabaseAdmin } from '@/lib/supabaseAdmin';
import type { ReportStatus } from '@orbita/shared';
import { requireAdmin } from '@/lib/requireAdmin';

export async function setReportStatus(reportId: string, status: ReportStatus) {
  const admin = await requireAdmin();
  const { error } = await supabaseAdmin
    .from('reports')
    .update({ status, reviewed_by: admin.id, reviewed_at: new Date().toISOString() })
    .eq('id', reportId);
  if (error) throw new Error(error.message);
  revalidatePath('/reports');
}

export async function resolveSuspiciousFlag(flagId: string) {
  await requireAdmin();
  const { error } = await supabaseAdmin.from('suspicious_activity_flags').update({ resolved: true }).eq('id', flagId);
  if (error) throw new Error(error.message);
  revalidatePath('/reports');
}

export async function suspendProfileFromFlag(flagId: string, profileId: string) {
  await requireAdmin();
  const { error: suspendError } = await supabaseAdmin.from('profiles').update({ status: 'suspended' }).eq('id', profileId);
  if (suspendError) throw new Error(suspendError.message);

  const { error } = await supabaseAdmin.from('suspicious_activity_flags').update({ resolved: true }).eq('id', flagId);
  if (error) throw new Error(error.message);

  revalidatePath('/reports');
  revalidatePath('/users');
}

export async function actionReportAndSuspend(reportId: string, reportedId: string) {
  const admin = await requireAdmin();
  const { error: suspendError } = await supabaseAdmin
    .from('profiles')
    .update({ status: 'suspended' })
    .eq('id', reportedId);
  if (suspendError) throw new Error(suspendError.message);

  const { error } = await supabaseAdmin
    .from('reports')
    .update({ status: 'actioned', reviewed_by: admin.id, reviewed_at: new Date().toISOString() })
    .eq('id', reportId);
  if (error) throw new Error(error.message);
  revalidatePath('/reports');
  revalidatePath('/users');
}
