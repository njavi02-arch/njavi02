import React from 'react';
import { Text, View } from 'react-native';
import { useTheme } from '../../../theme/ThemeProvider';
import { Stepper } from '../../../components/Stepper';
import { useOnboardingStore } from '../../../store/onboardingStore';
import { computeProfileCompletionPct } from '@orbita/shared';

export function StepPreferencesSummary() {
  const theme = useTheme();
  const { draft, setPartial } = useOnboardingStore();

  const completionPreview = computeProfileCompletionPct({
    hasName: draft.displayName.trim().length > 0,
    hasBirthDate: Boolean(draft.birthDate),
    hasGender: Boolean(draft.gender),
    hasSeeking: draft.seeking.length > 0,
    hasCity: draft.city.trim().length > 0,
    photoCount: draft.mainPhotoUri ? 1 : 0,
    hasBio: draft.bio.trim().length > 0,
    interestCount: draft.interestIds.length,
  });

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
        Últimos ajustes
      </Text>

      <Stepper
        label="Edad mínima que quieres ver"
        value={draft.minAgePref}
        min={18}
        max={draft.maxAgePref}
        onChange={(v) => setPartial({ minAgePref: v })}
      />
      <Stepper
        label="Edad máxima que quieres ver"
        value={draft.maxAgePref}
        min={draft.minAgePref}
        max={80}
        onChange={(v) => setPartial({ maxAgePref: v })}
      />
      <Stepper
        label="Distancia máxima"
        value={draft.maxDistanceKm}
        min={1}
        max={200}
        step={5}
        suffix=" km"
        onChange={(v) => setPartial({ maxDistanceKm: v })}
      />

      <View
        style={{
          backgroundColor: theme.colors.surface,
          borderRadius: theme.radius.md,
          padding: theme.spacing.md,
          marginTop: theme.spacing.md,
        }}
      >
        <Text style={{ color: theme.colors.textPrimary, fontFamily: theme.typography.fontFamilyBodySemibold }}>
          Tu perfil quedará al {completionPreview}% completo
        </Text>
        <View
          style={{
            height: 8,
            borderRadius: 4,
            backgroundColor: theme.colors.border,
            marginTop: theme.spacing.xs,
            overflow: 'hidden',
          }}
        >
          <View
            style={{
              width: `${completionPreview}%`,
              height: '100%',
              backgroundColor: theme.colors.secondary,
            }}
          />
        </View>
        <Text
          style={{
            color: theme.colors.textSecondary,
            fontSize: theme.typography.sizes.caption,
            marginTop: theme.spacing.xs,
          }}
        >
          Podrás completar el resto (más fotos, más intereses) después, sin que te bloquee
          la entrada a la app.
        </Text>
      </View>
    </View>
  );
}
