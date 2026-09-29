import React from 'react';
import { Text, View } from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { useTheme } from '../theme/ThemeProvider';

interface CompatibilityScoreBadgeProps {
  score: number;
  showLabel?: boolean;
}

export function CompatibilityScoreBadge({ score, showLabel = true }: CompatibilityScoreBadgeProps) {
  const theme = useTheme();

  let colors: [string, string];
  let icon: string;

  if (score >= 85) {
    colors = ['#FF6B6B', '#FF8E8E'];
    icon = '🔥';
  } else if (score >= 70) {
    colors = ['#FFD93D', '#FFE66D'];
    icon = '✨';
  } else if (score >= 50) {
    colors = ['#6BCB77', '#9EFFA9'];
    icon = '👍';
  } else {
    colors = ['#4D96FF', '#7FB5FF'];
    icon = '💫';
  }

  return (
    <LinearGradient colors={colors} start={{ x: 0, y: 0 }} end={{ x: 1, y: 1 }} style={{ borderRadius: theme.radius.sm, padding: 8 }}>
      <View style={{ flexDirection: 'row', alignItems: 'center', gap: 4 }}>
        <Text style={{ fontSize: 14 }}>{icon}</Text>
        <Text style={{ fontFamily: theme.typography.fontFamilyBodySemibold, fontSize: 14, color: '#fff' }}>
          {Math.round(score)}%
        </Text>
        {showLabel && (
          <Text style={{ fontFamily: theme.typography.fontFamilyBody, fontSize: 12, color: 'rgba(255,255,255,0.8)', marginLeft: 4 }}>
            Compatibilidad
          </Text>
        )}
      </View>
    </LinearGradient>
  );
}
