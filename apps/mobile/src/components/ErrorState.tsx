import React from 'react';
import { EmptyState } from './EmptyState';

export function ErrorState({ message, onRetry }: { message?: string; onRetry?: () => void }) {
  return (
    <EmptyState
      emoji="⚠️"
      title="Algo ha fallado"
      description={message ?? 'No hemos podido cargar esto. Inténtalo de nuevo.'}
      actionLabel={onRetry ? 'Reintentar' : undefined}
      onAction={onRetry}
    />
  );
}
