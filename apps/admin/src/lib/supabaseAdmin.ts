import 'server-only';
import { createClient } from '@supabase/supabase-js';

// Cliente con la service_role key: ignora RLS por completo. SOLO se importa desde código
// de servidor (Server Components, Server Actions, Route Handlers) — el paquete
// `server-only` hace que el build falle si algo intenta importarlo desde un Client
// Component, para que la clave nunca pueda acabar en el bundle del navegador.
const supabaseUrl = process.env.SUPABASE_URL ?? '';
const serviceRoleKey = process.env.SUPABASE_SERVICE_ROLE_KEY ?? '';

export const isAdminBackendConfigured = Boolean(supabaseUrl && serviceRoleKey);

export const supabaseAdmin = createClient(
  supabaseUrl || 'https://placeholder.supabase.co',
  serviceRoleKey || 'placeholder-service-role-key',
  { auth: { autoRefreshToken: false, persistSession: false } },
);

// Cliente con la anon key, usado únicamente para verificar email/password en el login
// del panel (signInWithPassword) — nunca para leer/escribir datos de negocio.
export function createAnonClientForLogin() {
  const anonKey = process.env.SUPABASE_ANON_KEY ?? '';
  return createClient(supabaseUrl || 'https://placeholder.supabase.co', anonKey || 'placeholder-anon-key', {
    auth: { autoRefreshToken: false, persistSession: false },
  });
}
