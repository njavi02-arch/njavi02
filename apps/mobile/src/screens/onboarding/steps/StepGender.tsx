import React from 'react';
import { Text, View } from 'react-native';
import { useTheme } from '../../../theme/ThemeProvider';
import { Chip } from '../../../components/Chip';
import { useOnboardingStore } from '../../../store/onboardingStore';
import type { Gender } from '@orbita/shared';

const GENDER_OPTIONS: { value: Gender; label: string }[] = [
  { value: 'female', label: 'Mujer' },
  { value: 'male', label: 'Hombre' },
  { value: 'non_binary', label: 'No binario' },
  { value: 'unspecified', label: 'Prefiero no decirlo' },
];

const SHOW_ME_OPTIONS: { value: Gender; label: string }[] = [
  { value: 'female', label: 'Mujeres' },
  { value: 'male', label: 'Hombres' },
  { value: 'non_binary', label: 'No binarias' },
];

export function StepGender() {
  const theme = useTheme();
  const { draft, setPartial } = useOnboardingStore();

  function toggleShowMe(value: Gender) {
    const has = draft.showMeGender.includes(value);
    const next = has ? draft.showMeGender.filter((g) => g !== value) : [...draft.showMeGender, value];
    setPartial({ showMeGender: next });
  }

  return (
    <View>
      <Text
        style={{
          fontFamily: theme.typography.fontFamilyHeading,
          fontSize: theme.typography.sizes.h2,
          color: theme.colors.textPrimary,
          marginBottom: theme.spacing.md,
        }}
      >
        ¿Cómo te identificas?
      </Text>
      <View style={{ flexDirection: 'row', flexWrap: 'wrap', marginBottom: theme.spacing.lg }}>
        {GENDER_OPTIONS.map((opt) => (
          <Chip
            key={opt.value}
            label={opt.label}
            selected={draft.gender === opt.value}
            onPress={() => setPartial({ gender: opt.value })}
          />
        ))}
      </View>

      <Text
        style={{
          fontFamily: theme.typography.fontFamilyHeadingSemibold,
          fontSize: theme.typography.sizes.h3,
          color: theme.colors.textPrimary,
          marginBottom: theme.spacing.sm,
        }}
      >
        ¿A quién quieres conocer?
      </Text>
      <View style={{ flexDirection: 'row', flexWrap: 'wrap' }}>
        {SHOW_ME_OPTIONS.map((opt) => (
          <Chip
            key={opt.value}
            label={opt.label}
            selected={draft.showMeGender.includes(opt.value)}
            onPress={() => toggleShowMe(opt.value)}
          />
        ))}
      </View>
    </View>
  );
}

export function isStepGenderValid(draft: ReturnType<typeof useOnboardingStore.getState>['draft']): boolean {
  return Boolean(draft.gender) && draft.showMeGender.length > 0;
}
