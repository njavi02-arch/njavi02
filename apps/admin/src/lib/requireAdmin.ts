import 'server-only';
import { cookies } from 'next/headers';
import { redirect } from 'next/navigation';
import { ADMIN_SESSION_COOKIE, verifySessionCookieValue } from './adminSession';
import { supabaseAdmin } from './supabaseAdmin';

export interface AdminUser {
  id: string;
  email: string | null;
  role: 'superadmin' | 'moderator' | 'support';
}

/** Comprueba la cookie de sesión firmada y que el usuario siga en `admin_users`
 * (revocar acceso = borrar la fila, no hace falta gestionar tokens aparte).
 * Redirige a /login si no hay sesión válida — se llama al principio de cada página
 * admin y en el layout del grupo (admin). */
export async function requireAdmin(): Promise<AdminUser> {
  const cookieStore = await cookies();
  const raw = cookieStore.get(ADMIN_SESSION_COOKIE)?.value;
  const userId = verifySessionCookieValue(raw);

  if (!userId) {
    redirect('/login');
  }

  const { data: adminRow, error } = await supabaseAdmin
    .from('admin_users')
    .select('id, role')
    .eq('id', userId)
    .maybeSingle();

  if (error || !adminRow) {
    redirect('/login');
  }

  const { data: authUser } = await supabaseAdmin.auth.admin.getUserById(userId);

  return { id: userId, email: authUser?.user?.email ?? null, role: adminRow.role };
}
