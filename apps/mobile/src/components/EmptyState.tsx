import React from 'react';
import { StyleSheet, Text, View } from 'react-native';
import { useTheme } from '../theme/ThemeProvider';
import { Button } from './Button';

interface EmptyStateProps {
  emoji?: string;
  title: string;
  description?: string;
  actionLabel?: string;
  onAction?: () => void;
}

export function EmptyState({ emoji = '✨', title, description, actionLabel, onAction }: EmptyStateProps) {
  const theme = useTheme();
  return (
    <View style={styles.container}>
      <Text style={{ fontSize: 40, marginBottom: theme.spacing.sm }}>{emoji}</Text>
      <Text
        style={{
          color: theme.colors.textPrimary,
          fontFamily: theme.typography.fontFamilyHeadingSemibold,
          fontSize: theme.typography.sizes.h3,
          textAlign: 'center',
          marginBottom: theme.spacing.xxs,
        }}
      >
        {title}
      </Text>
      {description ? (
        <Text
          style={{
            color: theme.colors.textSecondary,
            fontFamily: theme.typography.fontFamilyBody,
            fontSize: theme.typography.sizes.body,
            textAlign: 'center',
            marginBottom: theme.spacing.md,
          }}
        >
          {description}
        </Text>
      ) : null}
      {actionLabel && onAction ? (
        <Button label={actionLabel} onPress={onAction} variant="outline" fullWidth={false} />
      ) : null}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    padding: 32,
  },
});
