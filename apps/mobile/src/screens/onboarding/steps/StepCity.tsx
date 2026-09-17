import React from 'react';
import { Text, View } from 'react-native';
import { useTheme } from '../../../theme/ThemeProvider';
import { TextField } from '../../../components/TextField';
import { useOnboardingStore } from '../../../store/onboardingStore';

export function StepCity() {
  const theme = useTheme();
  const { draft, setPartial } = useOnboardingStore();

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
        ¿Dónde estás?
      </Text>
      <Text
        style={{
          fontFamily: theme.typography.fontFamilyBody,
          fontSize: theme.typography.sizes.body,
          color: theme.colors.textSecondary,
          marginBottom: theme.spacing.lg,
        }}
      >
        Usamos tu ciudad para mostrarte personas cerca de ti. Nunca compartimos tu ubicación
        exacta — ver docs/06-security-and-privacy.md.
      </Text>
      <TextField
        label="Ciudad"
        value={draft.city}
        onChangeText={(city) => setPartial({ city })}
        placeholder="Madrid"
      />
    </View>
  );
}

export function isStepCityValid(draft: ReturnType<typeof useOnboardingStore.getState>['draft']): boolean {
  return draft.city.trim().length >= 2;
}
