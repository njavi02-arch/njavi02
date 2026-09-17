import React, { useState } from 'react';
import { Alert, Image, Pressable, ScrollView, Text, View } from 'react-native';
import * as ImagePicker from 'expo-image-picker';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import type { NativeStackScreenProps } from '@react-navigation/native-stack';
import { useTheme } from '../../theme/ThemeProvider';
import { ScreenContainer } from '../../components/ScreenContainer';
import { TextField } from '../../components/TextField';
import { Chip } from '../../components/Chip';
import { Button } from '../../components/Button';
import { ProfilePromptEditor } from '../../components/ProfilePromptEditor';
import { useAuthStore } from '../../store/authStore';
import {
  deleteProfilePhoto,
  getPhotosForProfile,
  getProfileInterestIds,
  getProfilePrompts,
  listInterests,
  setProfileInterestSelected,
  updateMyProfile,
  uploadProfilePhoto,
} from '../../services/profiles';
import { DEFAULT_APP_CONFIG } from '@orbita/shared';
import type { ProfileStackParamList } from '../../navigation/types';

type Props = NativeStackScreenProps<ProfileStackParamList, 'EditProfile'>;

export function EditProfileScreen({ navigation }: Props) {
  const theme = useTheme();
  const profile = useAuthStore((s) => s.profile);
  const refreshProfile = useAuthStore((s) => s.refreshProfile);
  const queryClient = useQueryClient();

  const [bio, setBio] = useState(profile?.bio ?? '');
  const [city, setCity] = useState(profile?.city ?? '');
  const [saving, setSaving] = useState(false);
  const [uploadingSlot, setUploadingSlot] = useState<number | null>(null);

  const photosQuery = useQuery({
    queryKey: ['photos', profile?.id],
    queryFn: () => getPhotosForProfile(profile!.id),
    enabled: Boolean(profile),
  });
  const interestsQuery = useQuery({ queryKey: ['interests'], queryFn: listInterests });
  const myInterestsQuery = useQuery({
    queryKey: ['profile-interests', profile?.id],
    queryFn: () => getProfileInterestIds(profile!.id),
    enabled: Boolean(profile),
  });
  const promptsQuery = useQuery({
    queryKey: ['prompts', profile?.id],
    queryFn: () => getProfilePrompts(profile!.id),
    enabled: Boolean(profile),
  });
  const promptsByPosition = new Map((promptsQuery.data ?? []).map((p) => [p.position, p]));

  const photosBySlot = new Map((photosQuery.data ?? []).map((p) => [p.position, p]));
  const selectedInterestIds = new Set(myInterestsQuery.data ?? []);

  // profiles.profile_completion_pct se recalcula solo en la base de datos (trigger,
  // ver supabase/migrations/0003_profile_completion_trigger.sql) en cuanto cambian
  // fotos/intereses/bio/etc. — pero authStore.profile es una copia local, así que hay
  // que refrescarla después de cada cambio para que el % que se ve en MyProfileScreen
  // no se quede desactualizado.
  async function handleToggleInterest(interestId: string) {
    if (!profile) return;
    const nowSelected = !selectedInterestIds.has(interestId);
    await setProfileInterestSelected(profile.id, interestId, nowSelected);
    queryClient.invalidateQueries({ queryKey: ['profile-interests', profile.id] });
    await refreshProfile();
  }

  async function handlePickPhoto(position: number) {
    if (!profile) return;
    const permission = await ImagePicker.requestMediaLibraryPermissionsAsync();
    if (!permission.granted) return;
    const result = await ImagePicker.launchImageLibraryAsync({ mediaTypes: ['images'], quality: 0.8, allowsEditing: true, aspect: [3, 4] });
    if (result.canceled || !result.assets[0]) return;

    setUploadingSlot(position);
    try {
      await uploadProfilePhoto({ profileId: profile.id, position, fileUri: result.assets[0].uri, contentType: 'image/jpeg' });
      queryClient.invalidateQueries({ queryKey: ['photos', profile.id] });
      await refreshProfile();
    } catch (e) {
      Alert.alert('No se pudo subir la foto', e instanceof Error ? e.message : 'Inténtalo de nuevo');
    } finally {
      setUploadingSlot(null);
    }
  }

  async function handleRemovePhoto(photoId: string) {
    if (!profile) return;
    await deleteProfilePhoto(photoId);
    queryClient.invalidateQueries({ queryKey: ['photos', profile.id] });
    await refreshProfile();
  }

  async function handleSave() {
    if (!profile) return;
    setSaving(true);
    try {
      await updateMyProfile(profile.id, { bio: bio.trim(), city: city.trim() });
      await refreshProfile();
      navigation.goBack();
    } catch (e) {
      Alert.alert('No se pudo guardar', e instanceof Error ? e.message : 'Inténtalo de nuevo');
    } finally {
      setSaving(false);
    }
  }

  if (!profile) return null;

  return (
    <ScreenContainer>
      <ScrollView contentContainerStyle={{ paddingTop: theme.spacing.md, paddingBottom: theme.spacing.xl }}>
        <Text style={{ fontFamily: theme.typography.fontFamilyHeading, fontSize: theme.typography.sizes.h1, color: theme.colors.textPrimary, marginBottom: theme.spacing.md }}>
          Editar perfil
        </Text>

        <Text style={{ color: theme.colors.textSecondary, fontFamily: theme.typography.fontFamilyBodyMedium, marginBottom: theme.spacing.sm }}>
          Fotos ({photosQuery.data?.length ?? 0}/{DEFAULT_APP_CONFIG.max_photos_count}) — las 3 primeras son públicas
        </Text>
        <View style={{ flexDirection: 'row', flexWrap: 'wrap', marginBottom: theme.spacing.lg }}>
          {Array.from({ length: DEFAULT_APP_CONFIG.max_photos_count }).map((_, position) => {
            const photo = photosBySlot.get(position);
            return (
              <Pressable
                key={position}
                onPress={() => (photo ? handleRemovePhoto(photo.id) : handlePickPhoto(position))}
                style={{
                  width: '30%',
                  aspectRatio: 0.8,
                  marginRight: '3%',
                  marginBottom: 10,
                  borderRadius: theme.radius.sm,
                  backgroundColor: theme.colors.surface,
                  borderWidth: 1,
                  borderColor: theme.colors.border,
                  borderStyle: photo ? 'solid' : 'dashed',
                  alignItems: 'center',
                  justifyContent: 'center',
                  overflow: 'hidden',
                }}
              >
                {uploadingSlot === position ? (
                  <Text style={{ color: theme.colors.textSecondary }}>…</Text>
                ) : photo ? (
                  <Image source={{ uri: photo.url }} style={{ width: '100%', height: '100%' }} />
                ) : (
                  <Text style={{ fontSize: 22, color: theme.colors.textSecondary }}>+</Text>
                )}
                {photo && position < DEFAULT_APP_CONFIG.public_photos_count ? (
                  <View style={{ position: 'absolute', top: 4, left: 4, backgroundColor: theme.colors.success, borderRadius: 4, paddingHorizontal: 4 }}>
                    <Text style={{ fontSize: 9, color: '#fff' }}>Pública</Text>
                  </View>
                ) : null}
              </Pressable>
            );
          })}
        </View>

        <TextField label="Ciudad" value={city} onChangeText={setCity} />
        <TextField label="Bio" value={bio} onChangeText={setBio} multiline maxLength={500} />

        <Text style={{ color: theme.colors.textSecondary, fontFamily: theme.typography.fontFamilyBodyMedium, marginBottom: theme.spacing.sm }}>
          Intereses
        </Text>
        <View style={{ flexDirection: 'row', flexWrap: 'wrap', marginBottom: theme.spacing.lg }}>
          {(interestsQuery.data ?? []).map((i) => (
            <Chip
              key={i.id}
              label={i.name}
              selected={selectedInterestIds.has(i.id)}
              onPress={() => handleToggleInterest(i.id)}
            />
          ))}
        </View>

        <Text style={{ color: theme.colors.textSecondary, fontFamily: theme.typography.fontFamilyBodyMedium, marginBottom: theme.spacing.xxs }}>
          Prompts (hasta 3)
        </Text>
        <Text style={{ color: theme.colors.textSecondary, fontSize: theme.typography.sizes.caption, marginBottom: theme.spacing.sm }}>
          Ayudan a que alguien sepa de qué hablarte al abrir la conversación.
        </Text>
        {[0, 1, 2].map((position) => (
          <ProfilePromptEditor
            key={position}
            profileId={profile.id}
            position={position}
            existing={promptsByPosition.get(position) ?? null}
            onChanged={() => queryClient.invalidateQueries({ queryKey: ['prompts', profile.id] })}
          />
        ))}

        <Button label="Guardar cambios" onPress={handleSave} loading={saving} style={{ marginTop: theme.spacing.sm }} />
      </ScrollView>
    </ScreenContainer>
  );
}
