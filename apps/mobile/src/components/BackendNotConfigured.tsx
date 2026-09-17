import React from 'react';
import { ScreenContainer } from './ScreenContainer';
import { EmptyState } from './EmptyState';

/**
 * Se muestra en vez de la app real cuando no hay credenciales de Supabase (.env vacío).
 * A propósito NO se sustituye por datos de mentira: el brief pide explícitamente no
 * simular funcionalidades conectadas a base de datos. Ver apps/mobile/.env.example.
 */
export function BackendNotConfigured() {
  return (
    <ScreenContainer>
      <EmptyState
        emoji="🛠️"
        title="Backend no configurado"
        description={
          'Orbita necesita un proyecto Supabase real para funcionar (autenticación, base de ' +
          'datos, chat en tiempo real). Copia apps/mobile/.env.example a .env, añade tu ' +
          'EXPO_PUBLIC_SUPABASE_URL y EXPO_PUBLIC_SUPABASE_ANON_KEY, y aplica las migraciones ' +
          'de supabase/migrations/ con `supabase db push`.'
        }
      />
    </ScreenContainer>
  );
}
