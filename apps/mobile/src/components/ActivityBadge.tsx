import React from 'react';
import { Text, View } from 'react-native';
import { getActivityStatus } from '@orbita/shared';
import { useTheme } from '../theme/ThemeProvider';

/** "Activo ahora" / "Activo hoy" — ver PRODUCT_BRAIN.md → INVESTIGACIÓN/DECISIONES.
 * No renderiza nada si la persona no ha estado activa en las últimas 24h (privacidad). */
export function ActivityBadge({ lastActiveAt, light }: { lastActiveAt: string; light?: boolean }) {
  const theme = useTheme();
  const status = getActivityStatus(lastActiveAt);
  if (!status.level) return null;

  const textColor = light ? '#fff' : theme.colors.textSecondary;

  return (
    <View style={{ flexDirection: 'row', alignItems: 'center' }}>
      <View
        style={{
          width: 8,
          height: 8,
          borderRadius: 4,
          marginRight: 5,
          backgroundColor: status.level === 'online' ? theme.colors.success : theme.colors.textSecondary,
        }}
      />
      <Text style={{ color: textColor, fontSize: theme.typography.sizes.caption, opacity: light ? 0.95 : 1 }}>
        {status.label}
      </Text>
    </View>
  );
}
