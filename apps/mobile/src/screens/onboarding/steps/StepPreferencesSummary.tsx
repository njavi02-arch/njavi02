import React from 'react';
import { Pressable, Text, View } from 'react-native';
import { useTheme } from '../../../theme/ThemeProvider';
import { useOnboardingStore } from '../../../store/onboardingStore';
import { computeProfileCompletionPct } from '@orbita/shared';

function Stepper({
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
