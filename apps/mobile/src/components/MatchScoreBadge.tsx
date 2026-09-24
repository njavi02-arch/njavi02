import React from 'react';
import { Text, View } from 'react-native';
import { getMatchLabel } from '@orbita/shared';
import { useTheme } from '../theme/ThemeProvider';

interface MatchScoreBadgeProps {
  percentage: number;
  size?: 'small' | 'medium' | 'large';
  prominent?: boolean;
}

export function MatchScoreBadge({ percentage, size = 'medium', prominent = false }: MatchScoreBadgeProps) {
  const theme = useTheme();
  const { emoji, label } = getMatchLabel(percentage);

  const sizeStyles = {
    small: { fontSize: 12, padding: 4, gap: 2 },
    medium: { fontSize: 14, padding: 6, gap: 3 },
    large: { fontSize: 16, padding: 8, gap: 4 },
  }[size];

  const backgroundColor = (() => {
    if (percentage >= 80) return 'rgba(255, 71, 87, 0.1)';
    if (percentage >= 60) return 'rgba(0, 200, 83, 0.1)';
    if (percentage >= 40) return 'rgba(41, 128, 185, 0.1)';
    return 'rgba(149, 165, 166, 0.1)';
  })();

  const textColor = (() => {
    if (percentage >= 80) return '#FF4757';
    if (percentage >= 60) return '#00C853';
    if (percentage >= 40) return '#2980B9';
    return '#95A5A6';
  })();

  if (prominent) {
    return (
      <View
        style={{
          backgroundColor,
          borderRadius: theme.radius.pill,
          paddingHorizontal: sizeStyles.padding * 2,
          paddingVertical: sizeStyles.padding,
          alignSelf: 'flex-start',
          borderWidth: 1,
          borderColor: textColor,
          marginVertical: sizeStyles.gap,
        }}
      >
        <Text
          style={{
            fontSize: sizeStyles.fontSize,
            fontFamily: theme.typography.fontFamilyBodySemibold,
            color: textColor,
          }}
        >
          {emoji} {percentage}% - {label}
        </Text>
      </View>
    );
  }

  return (
    <View
      style={{
        flexDirection: 'row',
        alignItems: 'center',
        backgroundColor,
        borderRadius: theme.radius.pill,
        paddingHorizontal: sizeStyles.padding * 1.5,
        paddingVertical: sizeStyles.padding,
        gap: sizeStyles.gap,
      }}
    >
      <Text style={{ fontSize: sizeStyles.fontSize + 2 }}>{emoji}</Text>
      <Text
        style={{
          fontSize: sizeStyles.fontSize,
          fontFamily: theme.typography.fontFamilyBodySemibold,
          color: textColor,
        }}
      >
        {percentage}%
      </Text>
    </View>
  );
}
