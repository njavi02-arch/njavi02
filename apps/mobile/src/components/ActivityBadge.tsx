import React from 'react';
import { Text, View } from 'react-native';
import { getActivityStatus } from '@orbita/shared';
import { useTheme } from '../theme/ThemeProvider';

/** "Activo ahora" / "Activo hoy" — ver PRODUCT_BRAIN.md → INVESTIGACIÓN/DECISIONES.
 * No renderiza nada si la persona no ha estado activa en las últimas 24h (privacidad). */
export function ActivityBadge({ lastActiveAt, light, prominent }: { lastActiveAt: string; light?: boolean; prominent?: boolean }) {
  const theme = useTheme();
  const status = getActivityStatus(lastActiveAt);
  if (!status.level) return null;

  const textColor = light ? '#fff' : theme.colors.textPrimary;
  const isOnline = status.level === 'online';

  if (prominent) {
    return (
      <View
        style={{
          flexDirection: 'row',
          alignItems: 'center',
          backgroundColor: isOnline ? theme.colors.success : theme.colors.surfaceElevated,
          borderRadius: theme.radius.pill,
          paddingHorizontal: 8,
          paddingVertical: 4,
        }}
      >
        <View
          style={{
            width: 6,
            height: 6,
            borderRadius: 3,
            marginRight: 4,
            backgroundColor: isOnline ? '#fff' : theme.colors.textSecondary,
          }}
        />
        <Text
          style={{
            color: isOnline ? '#fff' : theme.colors.textSecondary,
            fontSize: theme.typography.sizes.caption,
            fontFamily: theme.typography.fontFamilyBodySemibold,
          }}
        >
          {status.label}
        </Text>
      </View>
    );
  }

  return (
    <View style={{ flexDirection: 'row', alignItems: 'center' }}>
      <View
        style={{
          width: 8,
          height: 8,
          borderRadius: 4,
          marginRight: 5,
          backgroundColor: isOnline ? theme.colors.success : theme.colors.textSecondary,
        }}
      />
      <Text style={{ color: textColor, fontSize: theme.typography.sizes.caption, opacity: light ? 0.95 : 1 }}>
        {status.label}
      </Text>
    </View>
  );
}
