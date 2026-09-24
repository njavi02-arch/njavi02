import React from 'react';
import { View, Text, Pressable } from 'react-native';
import { useTheme } from '../theme/ThemeProvider';

interface ProfileStrengthIndicatorProps {
  completionPct: number;
  onPressAction?: () => void;
  fullWidth?: boolean;
}

export function ProfileStrengthIndicator({ completionPct, onPressAction, fullWidth = true }: ProfileStrengthIndicatorProps) {
  const theme = useTheme();

  const getStrengthLevel = (pct: number) => {
    if (pct >= 90) return { label: '💯 Perfecto', color: theme.colors.success, bgColor: 'rgba(0, 200, 83, 0.1)' };
    if (pct >= 70) return { label: '✨ Fuerte', color: '#FFB800', bgColor: 'rgba(255, 184, 0, 0.1)' };
    if (pct >= 50) return { label: '👍 Regular', color: '#2980B9', bgColor: 'rgba(41, 128, 185, 0.1)' };
    return { label: '⚠️ Incompleto', color: '#E74C3C', bgColor: 'rgba(231, 76, 60, 0.1)' };
  };

  const strength = getStrengthLevel(completionPct);
  const fillWidth = (completionPct / 100) * 100;

  return (
    <Pressable
      onPress={onPressAction}
      disabled={!onPressAction}
      style={[
        {
          backgroundColor: strength.bgColor,
          borderRadius: theme.radius.md,
          padding: theme.spacing.md,
          marginBottom: theme.spacing.md,
        },
        fullWidth && { width: '100%' },
      ]}
    >
      <View style={{ flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
        <Text style={{ color: strength.color, fontFamily: theme.typography.fontFamilyBodySemibold, fontSize: 14 }}>
          {strength.label}
        </Text>
        <Text style={{ color: theme.colors.textSecondary, fontSize: 12 }}>
          {completionPct}%
        </Text>
      </View>

      <View
        style={{
          height: 6,
          backgroundColor: 'rgba(0, 0, 0, 0.1)',
          borderRadius: 3,
          overflow: 'hidden',
          marginBottom: 8,
        }}
      >
        <View
          style={{
            height: '100%',
            width: `${fillWidth}%`,
            backgroundColor: strength.color,
          }}
        />
      </View>

      {completionPct < 90 && (
        <Text style={{ color: theme.colors.textSecondary, fontSize: 12, fontFamily: theme.typography.fontFamilyBody }}>
          {completionPct < 50
            ? '💭 Agrega fotos, bio e intereses para mejorar'
            : completionPct < 70
              ? '📝 Completa tu biografía y añade más detalles'
              : '✍️ Un poco más para perfeccionar tu perfil'}
        </Text>
      )}

      {completionPct >= 90 && onPressAction && (
        <Text style={{ color: theme.colors.textSecondary, fontSize: 12, fontFamily: theme.typography.fontFamilyBodySemibold }}>
          👉 Presiona para editar
        </Text>
      )}
    </Pressable>
  );
}
