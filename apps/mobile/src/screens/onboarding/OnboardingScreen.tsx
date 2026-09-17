import React, { useState } from 'react';
import { ScrollView, Text, View } from 'react-native';
import { useTheme } from '../../theme/ThemeProvider';
import { ScreenContainer } from '../../components/ScreenContainer';
import { Button } from '../../components/Button';
import { useOnboardingStore } from '../../store/onboardingStore';
import { useAuthStore } from '../../store/authStore';
import { createProfile, uploadProfilePhoto } from '../../services/profiles';
import { supabase } from '../../lib/supabase';

import { StepBasics, isStepBasicsValid } from './steps/StepBasics';
import { StepGender, isStepGenderValid } from './steps/StepGender';
import { StepSeeking, isStepSeekingValid } from './steps/StepSeeking';
import { StepCity, isStepCityValid } from './steps/StepCity';
import { StepPhoto, isStepPhotoValid } from './steps/StepPhoto';
import { StepBioAndInterests, isStepBioValid } from './steps/StepBioAndInterests';
import { StepPreferencesSummary } from './steps/StepPreferencesSummary';

const STEPS = [
  { key: 'basics', Component: StepBasics, isValid: isStepBasicsValid },
  { key: 'gender', Component: StepGender, isValid: isStepGenderValid },
  { key: 'seeking', Component: StepSeeking, isValid: isStepSeekingValid },
  { key: 'city', Component: StepCity, isValid: isStepCityValid },
  { key: 'photo', Component: StepPhoto, isValid: isStepPhotoValid },
  { key: 'bio', Component: StepBioAndInterests, isValid: isStepBioValid },
  { key: 'summary', Component: StepPreferencesSummary, isValid: () => true },
] as const;

export function OnboardingScreen() {
  const theme = useTheme();
  const { draft, nextStep, prevStep, reset } = useOnboardingStore();
  const { session, refreshProfile } = useAuthStore();
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const stepIndex = Math.min(draft.step, STEPS.length - 1);
  const { Component, isValid } = STEPS[stepIndex];
  const canAdvance = isValid(draft);
  const isLastStep = stepIndex === STEPS.length - 1;

  async function handleFinish() {
    if (!session) return;
    setSubmitting(true);
    setError(null);
    try {
      await createProfile({
        id: session.user.id,
        displayName: draft.displayName.trim(),
        birthDate: draft.birthDate as string,
        gender: draft.gender ?? 'unspecified',
        seeking: draft.seeking,
        city: draft.city.trim(),
        bio: draft.bio.trim(),
        interestIds: draft.interestIds,
      });

      await supabase
        .from('user_preferences')
        .update({
          min_age: draft.minAgePref,
          max_age: draft.maxAgePref,
          max_distance_km: draft.maxDistanceKm,
          show_me_gender: draft.showMeGender,
        })
        .eq('profile_id', session.user.id);

      if (draft.mainPhotoUri) {
        await uploadProfilePhoto({
          profileId: session.user.id,
          position: 0,
          fileUri: draft.mainPhotoUri,
          contentType: 'image/jpeg',
        });
      }

      await refreshProfile();
      reset();
    } catch (e) {
      setError(e instanceof Error ? e.message : 'No se pudo completar el registro');
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <ScreenContainer>
      <View style={{ flexDirection: 'row', marginTop: theme.spacing.sm, marginBottom: theme.spacing.lg }}>
        {STEPS.map((s, i) => (
          <View
            key={s.key}
            style={{
              flex: 1,
              height: 4,
              borderRadius: 2,
              marginRight: i < STEPS.length - 1 ? 4 : 0,
              backgroundColor: i <= stepIndex ? theme.colors.primary : theme.colors.border,
            }}
          />
        ))}
      </View>

      <ScrollView keyboardShouldPersistTaps="handled" contentContainerStyle={{ flexGrow: 1 }}>
        <Component />
      </ScrollView>

      {error ? <Text style={{ color: theme.colors.danger, marginBottom: theme.spacing.sm }}>{error}</Text> : null}

      <View style={{ flexDirection: 'row', paddingVertical: theme.spacing.md }}>
        {stepIndex > 0 ? (
          <Button label="Atrás" onPress={prevStep} variant="ghost" fullWidth={false} style={{ marginRight: 12 }} />
        ) : null}
        <View style={{ flex: 1 }}>
          <Button
            label={isLastStep ? 'Empezar a descubrir' : 'Continuar'}
            onPress={isLastStep ? handleFinish : nextStep}
            disabled={!canAdvance || submitting}
            loading={submitting}
          />
        </View>
      </View>
    </ScreenContainer>
  );
}
