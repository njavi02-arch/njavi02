import React from 'react';
import { Text, View } from 'react-native';
import { useQuery } from '@tanstack/react-query';
import { useTheme } from '../../../theme/ThemeProvider';
import { TextField } from '../../../components/TextField';
import { Chip } from '../../../components/Chip';
import { LoadingState } from '../../../components/LoadingState';
import { useOnboardingStore } from '../../../store/onboardingStore';
import { listInterests } from '../../../services/profiles';

export function StepBioAndInterests() {
  const theme = useTheme();
  const { draft, setPartial } = useOnboardingStore();
  const { data: interests, isLoading } = useQuery({ queryKey: ['interests'], queryFn: listInterests });

  function toggleInterest(id: string) {
    const has = draft.interestIds.includes(id);
    setPartial({
      interestIds: has ? draft.interestIds.filter((i) => i !== id) : [...draft.interestIds, id],
    });
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
        Cuéntanos algo de ti
      </Text>
      <TextField
        label="Bio"
        value={draft.bio}
        onChangeText={(bio) => setPartial({ bio })}
        placeholder="Algo breve y auténtico sobre ti..."
        multiline
        maxLength={500}
      />

      <Text
        style={{
          fontFamily: theme.typography.fontFamilyHeadingSemibold,
          fontSize: theme.typography.sizes.h3,
          color: theme.colors.textPrimary,
          marginBottom: theme.spacing.sm,
        }}
      >
        Tus intereses
      </Text>
      {isLoading ? (
        <LoadingState />
      ) : (
        <View style={{ flexDirection: 'row', flexWrap: 'wrap' }}>
          {(interests ?? []).map((interest) => (
            <Chip
              key={interest.id}
              label={interest.name}
              selected={draft.interestIds.includes(interest.id)}
              onPress={() => toggleInterest(interest.id)}
            />
          ))}
        </View>
      )}
    </View>
  );
}

export function isStepBioValid(draft: ReturnType<typeof useOnboardingStore.getState>['draft']): boolean {
  return draft.bio.trim().length >= 10;
}
