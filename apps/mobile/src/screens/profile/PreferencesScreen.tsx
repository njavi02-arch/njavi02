import React, { useState, useEffect } from 'react';
import { Alert, ScrollView } from 'react-native';
import type { NativeStackScreenProps } from '@react-navigation/native-stack';
import { useTheme } from '../../theme/ThemeProvider';
import { ScreenContainer } from '../../components/ScreenContainer';
import { LoadingState } from '../../components/LoadingState';
import { ErrorState } from '../../components/ErrorState';
import { Button } from '../../components/Button';
import { PreferencesForm } from '../../components/PreferencesForm';
import { useUserPreferences, useUpdateUserPreferences } from '../../hooks/useV2DiscoverFeed';
import type { ProfileStackParamList } from '../../navigation/types';

type Props = NativeStackScreenProps<ProfileStackParamList, 'Settings'>;

interface UserPreferences {
  min_age: number;
  max_age: number;
  gender_preference: string[];
  max_distance_km: number;
  preferred_hashtags: string[];
  show_verified_only: boolean;
}

export function PreferencesScreen({ navigation }: Props) {
  const theme = useTheme();
  const { data: preferences, isLoading, error } = useUserPreferences();
  const updateMutation = useUpdateUserPreferences();
  const [formData, setFormData] = useState<UserPreferences>({
    min_age: 18,
    max_age: 65,
    gender_preference: [],
    max_distance_km: 50,
    preferred_hashtags: [],
    show_verified_only: false,
  });

  useEffect(() => {
    if (preferences) {
      setFormData(preferences);
    }
  }, [preferences]);

  const handleSave = async () => {
    try {
      await updateMutation.mutateAsync(formData);
      Alert.alert('✅ Éxito', 'Tus preferencias han sido actualizadas');
    } catch (err) {
      Alert.alert('❌ Error', 'No pudimos guardar tus preferencias. Intenta de nuevo.');
    }
  };

  if (isLoading) {
    return (
      <ScreenContainer>
        <LoadingState />
      </ScreenContainer>
    );
  }

  if (error) {
    return (
      <ScreenContainer>
        <ErrorState message="Error al cargar preferencias" />
      </ScreenContainer>
    );
  }

  return (
    <ScreenContainer>
      <ScrollView contentContainerStyle={{ paddingBottom: theme.spacing.xl }}>
        <PreferencesForm
          preferences={formData}
          onChange={setFormData}
          isLoading={updateMutation.isPending}
        />

        <Button
          label={updateMutation.isPending ? 'Guardando...' : 'Guardar preferencias'}
          onPress={handleSave}
          isLoading={updateMutation.isPending}
          style={{ marginHorizontal: theme.spacing.md, marginTop: theme.spacing.lg }}
        />
      </ScrollView>
    </ScreenContainer>
  );
}
