import React from 'react';
import { Pressable, Text, View } from 'react-native';
import { useTheme } from '../theme/ThemeProvider';

export function Stepper({
  label,
  value,
  onChange,
  min,
  max,
  step = 1,
  suffix = '',
}: {
  label: string;
  value: number;
  onChange: (v: number) => void;
  min: number;
  max: number;
  step?: number;
  suffix?: string;
}) {
  const theme = useTheme();
  return (
    <View style={{ marginBottom: theme.spacing.md }}>
      <Text
        style={{
          color: theme.colors.textSecondary,
          fontFamily: theme.typography.fontFamilyBodyMedium,
          fontSize: theme.typography.sizes.bodySmall,
          marginBottom: theme.spacing.xs,
        }}
      >
        {label}
      </Text>
      <View style={{ flexDirection: 'row', alignItems: 'center' }}>
        <Pressable
          onPress={() => onChange(Math.max(min, value - step))}
          style={{
            width: 40,
            height: 40,
            borderRadius: theme.radius.pill,
            backgroundColor: theme.colors.surface,
            alignItems: 'center',
            justifyContent: 'center',
            borderWidth: 1,
            borderColor: theme.colors.border,
          }}
        >
          <Text style={{ color: theme.colors.textPrimary, fontSize: 18 }}>−</Text>
        </Pressable>
        <Text
          style={{
            marginHorizontal: theme.spacing.md,
            color: theme.colors.textPrimary,
            fontFamily: theme.typography.fontFamilyHeadingSemibold,
            fontSize: theme.typography.sizes.h3,
            minWidth: 64,
            textAlign: 'center',
          }}
        >
          {value}
          {suffix}
        </Text>
        <Pressable
          onPress={() => onChange(Math.min(max, value + step))}
          style={{
            width: 40,
            height: 40,
            borderRadius: theme.radius.pill,
            backgroundColor: theme.colors.surface,
            alignItems: 'center',
            justifyContent: 'center',
            borderWidth: 1,
            borderColor: theme.colors.border,
          }}
        >
          <Text style={{ color: theme.colors.textPrimary, fontSize: 18 }}>+</Text>
        </Pressable>
      </View>
    </View>
  );
}
