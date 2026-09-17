import React from 'react';
import { Text, View } from 'react-native';
import { useTheme } from '../../../theme/ThemeProvider';
import { Chip } from '../../../components/Chip';
import { useOnboardingStore } from '../../../store/onboardingStore';
import type { SeekingIntent } from '@orbita/shared';

const OPTIONS: { value: SeekingIntent; label: string; emoji: string }[] = [
  { value: 'friendship', label: 'Amistad', emoji: '🤝' },
  { value: 'social', label: 'Conocer gente', emoji: '🎉' },
  { value: 'dating', label: 'Citas', emoji: '💫' },
];

export function StepSeeking() {
  const theme = useTheme();
  const { draft, setPartial } = useOnboardingStore();

  function toggle(value: SeekingIntent) {
    const has = draft.seeking.includes(value);
    setPartial({ seeking: has ? draft.seeking.filter((s) => s !== value) : [...draft.seeking, value] });
  }

  return (
    <View>
      <Text
        style={{
          fontFamily: theme.typography.fontFamilyHeading,
          fontSize: theme.typography.sizes.h2,
          color: theme.colors.textPrimary,
          marginBottom: theme.spacing.xxs,
        }}
      >
        ¿Qué buscas en Orbita?
      </Text>
      <Text
        style={{
          fontFamily: theme.typography.fontFamilyBody,
          fontSize: theme.typography.sizes.body,
          color: theme.colors.textSecondary,
          marginBottom: theme.spacing.lg,
        }}
      >
        Puedes elegir más de una — no son excluyentes.
      </Text>
      <View style={{ flexDirection: 'row', flexWrap: 'wrap' }}>
        {OPTIONS.map((opt) => (
          <Chip
            key={opt.value}
            label={`${opt.emoji} ${opt.label}`}
            selected={draft.seeking.includes(opt.value)}
            onPress={() => toggle(opt.value)}
          />
        ))}
      </View>
    </View>
  );
}

export function isStepSeekingValid(draft: ReturnType<typeof useOnboardingStore.getState>['draft']): boolean {
  return draft.seeking.length > 0;
}
