import 'react-native-url-polyfill/auto';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { createClient } from '@supabase/supabase-js';

// Variables EXPO_PUBLIC_* se inlinean en build por Expo — no son secretas (la anon key
// de Supabase está protegida por RLS, no por ocultarla). Ver .env.example.
const supabaseUrl = process.env.EXPO_PUBLIC_SUPABASE_URL ?? '';
const supabaseAnonKey = process.env.EXPO_PUBLIC_SUPABASE_ANON_KEY ?? '';

export const isSupabaseConfigured = Boolean(supabaseUrl && supabaseAnonKey);

if (!isSupabaseConfigured && typeof console !== 'undefined') {
  // eslint-disable-next-line no-console
  console.warn(
    '[Orbita] EXPO_PUBLIC_SUPABASE_URL / EXPO_PUBLIC_SUPABASE_ANON_KEY no configuradas. ' +
      'Copia .env.example a .env y añade las credenciales de tu proyecto Supabase.',
  );
}

// Con placeholders válidos-en-forma para que createClient no lance si aún no hay .env
// (la app muestra su propio estado de "backend no configurado" — ver useBackendStatus).
export const supabase = createClient(
  supabaseUrl || 'https://placeholder.supabase.co',
  supabaseAnonKey || 'placeholder-anon-key',
  {
    auth: {
      storage: AsyncStorage,
      autoRefreshToken: true,
      persistSession: true,
      detectSessionInUrl: false,
    },
  },
);
