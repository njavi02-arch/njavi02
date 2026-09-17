'use server';

import { cookies } from 'next/headers';
import { redirect } from 'next/navigation';
import { createAnonClientForLogin, supabaseAdmin } from '@/lib/supabaseAdmin';
import { ADMIN_SESSION_COOKIE, createSessionCookieValue } from '@/lib/adminSession';

export interface LoginState {
  error: string | null;
}

export async function loginAction(_prevState: LoginState, formData: FormData): Promise<LoginState> {
  const email = String(formData.get('email') ?? '').trim();
  const password = String(formData.get('password') ?? '');

  if (!email || !password) {
    return { error: 'Introduce email y contraseña' };
  }

  const anonClient = createAnonClientForLogin();
  const { data, error } = await anonClient.auth.signInWithPassword({ email, password });

  if (error || !data.user) {
    return { error: 'Credenciales incorrectas' };
  }

  const { data: adminRow } = await supabaseAdmin
    .from('admin_users')
    .select('id')
    .eq('id', data.user.id)
    .maybeSingle();

  if (!adminRow) {
    return { error: 'Esta cuenta no tiene acceso al panel de administración' };
  }

  const cookieStore = await cookies();
  cookieStore.set(ADMIN_SESSION_COOKIE, createSessionCookieValue(data.user.id), {
    httpOnly: true,
    secure: process.env.NODE_ENV === 'production',
    sameSite: 'lax',
    path: '/',
    maxAge: 12 * 60 * 60,
  });

  redirect('/dashboard');
}

export async function logoutAction() {
  const cookieStore = await cookies();
  cookieStore.delete(ADMIN_SESSION_COOKIE);
  redirect('/login');
}
