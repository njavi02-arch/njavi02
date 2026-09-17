import React, { useEffect, useState } from 'react';
import { Alert, ScrollView, Text, View } from 'react-native';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import type { NativeStackScreenProps } from '@react-navigation/native-stack';
import { useTheme } from '../../theme/ThemeProvider';
import { ScreenContainer } from '../../components/ScreenContainer';
import { LoadingState } from '../../components/LoadingState';
import { ErrorState } from '../../components/ErrorState';
import { Button } from '../../components/Button';
import { TextField } from '../../components/TextField';
import { PhotoGallery } from '../../components/PhotoGallery';
import { getPhotosForProfile, getProfileById } from '../../services/profiles';
import { hasUnlockedPhotos, unlockPhotos, sendSuperLike } from '../../services/economy';
import { recordProfileView } from '../../services/discover';
import { sendConversationRequest } from '../../services/conversations';
import { blockUser, reportUser } from '../../services/safety';
import { useAuthStore } from '../../store/authStore';
import { DEFAULT_APP_CONFIG } from '@orbita/shared';
import type { DiscoverStackParamList } from '../../navigation/types';

type Props = NativeStackScreenProps<DiscoverStackParamList, 'ProfileDetail'>;

export function ProfileDetailScreen({ route, navigation }: Props) {
  const theme = useTheme();
  const { profileId } = route.params;
  const session = useAuthStore((s) => s.session);
  const queryClient = useQueryClient();
  const [unlocking, setUnlocking] = useState(false);
  const [composerOpen, setComposerOpen] = useState(false);
  const [message, setMessage] = useState('');
  const [sendingMessage, setSendingMessage] = useState(false);

  const profileQuery = useQuery({ queryKey: ['profile', profileId], queryFn: () => getProfileById(profileId) });
  const photosQuery = useQuery({ queryKey: ['photos', profileId], queryFn: () => getPhotosForProfile(profileId) });
  const unlockedQuery = useQuery({
    queryKey: ['photo-unlock', session?.user.id, profileId],
    queryFn: () => hasUnlockedPhotos(session!.user.id, profileId),
    enabled: Boolean(session),
  });

  useEffect(() => {
    if (session) recordProfileView(session.user.id, profileId).catch(() => {});
  }, [session?.user.id, profileId]);

  async function handleUnlock() {
    if (!session) return;
    setUnlocking(true);
    try {
      const viewerIsPremium = useAuthStore.getState().profile?.is_premium ?? false;
      await unlockPhotos(profileId, viewerIsPremium ? 'premium' : 'coins');
      queryClient.invalidateQueries({ queryKey: ['photo-unlock', session.user.id, profileId] });
      queryClient.invalidateQueries({ queryKey: ['wallets'] });
    } catch (e) {
      Alert.alert('No se pudo desbloquear', e instanceof Error ? e.message : 'Inténtalo de nuevo');
    } finally {
      setUnlocking(false);
    }
  }

  async function handleSuperLike() {
    if (!session) return;
    try {
      await sendSuperLike(profileId);
      Alert.alert('✨ Super Like enviado');
      queryClient.invalidateQueries({ queryKey: ['wallets'] });
    } catch (e) {
      Alert.alert('No se pudo enviar', e instanceof Error ? e.message : 'Inténtalo de nuevo');
    }
  }

  async function handleSendMessage() {
    if (!session || message.trim().length === 0) return;
    setSendingMessage(true);
    try {
      await sendConversationRequest(profileId, message.trim());
      queryClient.invalidateQueries({ queryKey: ['wallets'] });
      Alert.alert('¡Mensaje enviado!', 'Te avisaremos si responde.');
      navigation.goBack();
    } catch (e) {
      Alert.alert('No se pudo enviar', e instanceof Error ? e.message : 'Inténtalo de nuevo');
    } finally {
      setSendingMessage(false);
    }
  }

  function handleReportOrBlock() {
    if (!session) return;
    Alert.alert('Opciones', undefined, [
      {
        text: 'Bloquear',
        style: 'destructive',
        onPress: () =>
          blockUser(session.user.id, profileId)
            .then(() => navigation.goBack())
            .catch((e) => Alert.alert('Error', e.message)),
      },
      {
        text: 'Reportar',
        onPress: () =>
          reportUser({ reporterId: session.user.id, reportedId: profileId, reason: 'other' })
            .then(() => Alert.alert('Gracias', 'Hemos recibido tu reporte y lo revisaremos.'))
            .catch((e) => Alert.alert('Error', e.message)),
      },
      { text: 'Cancelar', style: 'cancel' },
    ]);
  }

  if (profileQuery.isLoading || photosQuery.isLoading) {
    return (
      <ScreenContainer>
        <LoadingState />
      </ScreenContainer>
    );
  }

  if (profileQuery.isError || !profileQuery.data) {
    return (
      <ScreenContainer>
        <ErrorState onRetry={() => profileQuery.refetch()} />
      </ScreenContainer>
    );
  }

  const profile = profileQuery.data;

  return (
    <ScreenContainer>
      <ScrollView contentContainerStyle={{ paddingBottom: theme.spacing.xl, paddingTop: theme.spacing.sm }}>
        <View style={{ flexDirection: 'row', justifyContent: 'space-between', marginBottom: theme.spacing.md }}>
          <Text style={{ color: theme.colors.textPrimary, fontFamily: theme.typography.fontFamilyHeading, fontSize: theme.typography.sizes.h1 }}>
            {profile.display_name}
          </Text>
          <Button label="⋯" variant="ghost" fullWidth={false} onPress={handleReportOrBlock} />
        </View>

        {profile.city ? (
          <Text style={{ color: theme.colors.textSecondary, marginBottom: theme.spacing.md }}>📍 {profile.city}</Text>
        ) : null}

        <PhotoGallery
          photos={photosQuery.data ?? []}
          config={DEFAULT_APP_CONFIG}
          isUnlocked={Boolean(unlockedQuery.data)}
          onPressLocked={handleUnlock}
        />

        {!unlockedQuery.data && (photosQuery.data?.length ?? 0) > DEFAULT_APP_CONFIG.public_photos_count ? (
          <Button
            label={unlocking ? 'Desbloqueando…' : `Desbloquear fotos (${DEFAULT_APP_CONFIG.photo_unlock_coin_cost} 🪙)`}
            variant="outline"
            onPress={handleUnlock}
            loading={unlocking}
            style={{ marginTop: theme.spacing.sm, marginBottom: theme.spacing.md }}
          />
        ) : null}

        {profile.bio ? (
          <Text style={{ color: theme.colors.textPrimary, fontFamily: theme.typography.fontFamilyBody, fontSize: theme.typography.sizes.body, marginTop: theme.spacing.md }}>
            {profile.bio}
          </Text>
        ) : null}
      </ScrollView>

      {composerOpen ? (
        <View style={{ paddingBottom: theme.spacing.sm }}>
          <TextField
            placeholder={`Hola ${profile.display_name}, ¿qué tal?`}
            value={message}
            onChangeText={setMessage}
            autoFocus
            multiline
          />
          <View style={{ flexDirection: 'row' }}>
            <Button label="Cancelar" variant="ghost" onPress={() => setComposerOpen(false)} fullWidth={false} style={{ marginRight: 8 }} />
            <View style={{ flex: 1 }}>
              <Button label="Enviar" onPress={handleSendMessage} disabled={message.trim().length === 0} loading={sendingMessage} />
            </View>
          </View>
        </View>
      ) : (
        <View style={{ flexDirection: 'row', paddingVertical: theme.spacing.md }}>
          <Button label="✨ Super Like" variant="secondary" onPress={handleSuperLike} fullWidth={false} style={{ marginRight: 8, flex: 1 }} />
          <View style={{ flex: 1 }}>
            <Button label="Hablar" onPress={() => setComposerOpen(true)} />
          </View>
        </View>
      )}
    </ScreenContainer>
  );
}
