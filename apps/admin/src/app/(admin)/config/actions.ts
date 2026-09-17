'use server';

import { revalidatePath } from 'next/cache';
import { supabaseAdmin } from '@/lib/supabaseAdmin';
import { requireAdmin } from '@/lib/requireAdmin';

export interface UpdateConfigState {
  error: string | null;
  success: boolean;
}

export async function updateConfigValue(
  key: string,
  _prevState: UpdateConfigState,
  formData: FormData,
): Promise<UpdateConfigState> {
  const admin = await requireAdmin();
  const rawValue = String(formData.get('value') ?? '');

  let parsed: unknown;
  try {
    parsed = JSON.parse(rawValue);
  } catch {
    return { error: 'JSON inválido — revisa la sintaxis (comillas, comas, corchetes).', success: false };
  }

  const { error } = await supabaseAdmin
    .from('app_config')
    .update({ value: parsed, updated_by: admin.id, updated_at: new Date().toISOString() })
    .eq('key', key);

  if (error) {
    return { error: error.message, success: false };
  }

  revalidatePath('/config');
  return { error: null, success: true };
}
