import React from 'react';
import { Text, View } from 'react-native';
import { useTheme } from '../../../theme/ThemeProvider';
import { TextField } from '../../../components/TextField';
import { useOnboardingStore } from '../../../store/onboardingStore';
import { isOldEnough } from '@orbita/shared';
import { DEFAULT_APP_CONFIG } from '@orbita/shared';

export function StepBasics() {
  const theme = useTheme();
  const { draft, setPartial } = useOnboardingStore();

  const birthDateError = React.useMemo(() => {
    if (!draft.birthDate) return null;
    if (!/^\d{4}-\d{2}-\d{2}$/.test(draft.birthDate)) return 'Usa el formato AAAA-MM-DD';
    if (!isOldEnough(draft.birthDate, new Date(), DEFAULT_APP_CONFIG)) {
      return `Debes tener ${DEFAULT_APP_CONFIG.min_age} años o más para usar Orbita`;
    }
    return null;
  }, [draft.birthDate]);

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
        ¿Cómo te llamas?
      </Text>
      <TextField
        label="Nombre"
        value={draft.displayName}
        onChangeText={(displayName) => setPartial({ displayName })}
        placeholder="Tu nombre"
      />
      <TextField
        label="Fecha de nacimiento"
        value={draft.birthDate ?? ''}
        onChangeText={(text) => {
          const digitsOnly = text.replace(/\D/g, '');
          let formatted = '';

          if (digitsOnly.length >= 1) formatted = digitsOnly.substring(0, 4);
          if (digitsOnly.length >= 5) formatted += '-' + digitsOnly.substring(4, 6);
          if (digitsOnly.length >= 7) formatted += '-' + digitsOnly.substring(6, 8);

          setPartial({ birthDate: formatted });
        }}
        placeholder="AAAA-MM-DD"
        keyboardType="number-pad"
        error={birthDateError ?? undefined}
        maxLength={10}
      />
    </View>
  );
}

export function isStepBasicsValid(draft: ReturnType<typeof useOnboardingStore.getState>['draft']): boolean {
  return (
    draft.displayName.trim().length >= 2 &&
    Boolean(draft.birthDate) &&
    /^\d{4}-\d{2}-\d{2}$/.test(draft.birthDate ?? '') &&
    isOldEnough(draft.birthDate as string, new Date(), DEFAULT_APP_CONFIG)
  );
}
