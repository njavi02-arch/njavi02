import React from 'react';
import { Pressable, Text } from 'react-native';
import { useTheme } from '../theme/ThemeProvider';

interface ChipProps {
  label: string;
  selected?: boolean;
  onPress?: () => void;
}

export function Chip({ label, selected, onPress }: ChipProps) {
  const theme = useTheme();
  return (
    <Pressable
      onPress={onPress}
      style={{
        paddingVertical: 8,
        paddingHorizontal: 14,
        borderRadius: theme.radius.pill,
        backgroundColor: selected ? theme.colors.primary : theme.colors.surface,
        borderWidth: 1,
        borderColor: selected ? theme.colors.primary : theme.colors.border,
        marginRight: 8,
        marginBottom: 8,
      }}
    >
      <Text
        style={{
          color: selected ? theme.colors.onPrimary : theme.colors.textPrimary,
          fontFamily: theme.typography.fontFamilyBodyMedium,
          fontSize: theme.typography.sizes.bodySmall,
        }}
      >
        {label}
      </Text>
    </Pressable>
  );
}
