import React from 'react';
import { Image, Pressable, Text, View } from 'react-native';
import * as ImagePicker from 'expo-image-picker';
import { useTheme } from '../../../theme/ThemeProvider';
import { useOnboardingStore } from '../../../store/onboardingStore';

export function StepPhoto() {
  const theme = useTheme();
  const { draft, setPartial } = useOnboardingStore();

  async function pickPhoto() {
    const permission = await ImagePicker.requestMediaLibraryPermissionsAsync();
    if (!permission.granted) return;

    const result = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ['images'],
      allowsEditing: true,
      aspect: [3, 4],
      quality: 0.8,
    });
    if (!result.canceled && result.assets[0]) {
      setPartial({ mainPhotoUri: result.assets[0].uri });
    }
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
        Tu foto principal
      </Text>
      <Text
        style={{
          fontFamily: theme.typography.fontFamilyBody,
          fontSize: theme.typography.sizes.body,
          color: theme.colors.textSecondary,
          marginBottom: theme.spacing.lg,
        }}
      >
        Los perfiles con foto reciben muchas más respuestas. Podrás añadir hasta 10 fotos
        después — las 3 primeras serán públicas, el resto quedará oculto hasta que alguien
        lo desbloquee.
      </Text>
      <Pressable
        onPress={pickPhoto}
        style={{
          width: 180,
          height: 240,
          borderRadius: theme.radius.md,
          backgroundColor: theme.colors.surface,
          borderWidth: 1.5,
          borderColor: theme.colors.border,
          borderStyle: 'dashed',
          alignSelf: 'center',
          alignItems: 'center',
          justifyContent: 'center',
          overflow: 'hidden',
        }}
      >
        {draft.mainPhotoUri ? (
          <Image source={{ uri: draft.mainPhotoUri }} style={{ width: '100%', height: '100%' }} />
        ) : (
          <>
            <Text style={{ fontSize: 32, marginBottom: 8 }}>📷</Text>
            <Text style={{ color: theme.colors.textSecondary, fontFamily: theme.typography.fontFamilyBodyMedium }}>
              Añadir foto
            </Text>
          </>
        )}
      </Pressable>
    </View>
  );
}

export function isStepPhotoValid(draft: ReturnType<typeof useOnboardingStore.getState>['draft']): boolean {
  return Boolean(draft.mainPhotoUri);
}
