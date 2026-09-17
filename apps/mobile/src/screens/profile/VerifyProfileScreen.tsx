import React, { useState } from 'react';
import { Alert, Image, Pressable, ScrollView, Text, View } from 'react-native';
import * as ImagePicker from 'expo-image-picker';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { useTheme } from '../../theme/ThemeProvider';
import { ScreenContainer } from '../../components/ScreenContainer';
import { LoadingState } from '../../components/LoadingState';
import { Button } from '../../components/Button';
import { useAuthStore } from '../../store/authStore';
import { getMyVerificationRequest, requestVerification } from '../../services/verification';

const STATUS_COPY: Record<string, { emoji: string; label: string; color: 'success' | 'warning' | 'danger' }> = {
  pending: { emoji: '⏳', label: 'En revisión — normalmente tarda menos de 24h', color: 'warning' },
  approved: { emoji: '✅', label: 'Perfil verificado', color: 'success' },
  rejected: { emoji: '❌', label: 'No se pudo verificar con esa foto — inténtalo de nuevo', color: 'danger' },
};

export function VerifyProfileScreen() {
  const theme = useTheme();
  const profile = useAuthStore((s) => s.profile);
  const refreshProfile = useAuthStore((s) => s.refreshProfile);
  const queryClient = useQueryClient();
  const [selfieUri, setSelfieUri] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  const { data: request, isLoading } = useQuery({
    queryKey: ['verification-request', profile?.id],
    queryFn: () => getMyVerificationRequest(profile!.id),
    enabled: Boolean(profile),
  });

  async function handleTakeSelfie() {
    const permission = await ImagePicker.requestCameraPermissionsAsync();
    if (!permission.granted) {
      Alert.alert('Necesitamos la cámara', 'Actívala en los ajustes del sistema para verificar tu perfil.');
      return;
    }
    const result = await ImagePicker.launchCameraAsync({ cameraType: ImagePicker.CameraType.front, quality: 0.7 });
    if (!result.canceled && result.assets[0]) setSelfieUri(result.assets[0].uri);
  }

  async function handleSubmit() {
    if (!profile || !selfieUri) return;
    setSubmitting(true);
    try {
      await requestVerification(profile.id, selfieUri);
      queryClient.invalidateQueries({ queryKey: ['verification-request', profile.id] });
      setSelfieUri(null);
      Alert.alert('¡Enviado!', 'Revisaremos tu selfie y te avisaremos. Normalmente tarda menos de 24h.');
    } catch (e) {
      Alert.alert('No se pudo enviar', e instanceof Error ? e.message : 'Inténtalo de nuevo');
    } finally {
      setSubmitting(false);
    }
  }

  if (!profile || isLoading) {
    return (
      <ScreenContainer>
        <LoadingState />
      </ScreenContainer>
    );
  }

  if (profile.is_verified) {
    return (
      <ScreenContainer>
        <View style={{ flex: 1, alignItems: 'center', justifyContent: 'center', padding: theme.spacing.lg }}>
          <Text style={{ fontSize: 48, marginBottom: theme.spacing.sm }}>✅</Text>
          <Text style={{ color: theme.colors.textPrimary, fontFamily: theme.typography.fontFamilyHeadingSemibold, fontSize: theme.typography.sizes.h2, textAlign: 'center' }}>
            Tu perfil ya está verificado
          </Text>
        </View>
      </ScreenContainer>
    );
  }

  const status = request && request.status !== 'rejected' ? STATUS_COPY[request.status] : null;
  const canSubmitNew = !request || request.status === 'rejected';

  return (
    <ScreenContainer>
      <ScrollView contentContainerStyle={{ paddingTop: theme.spacing.md, paddingBottom: theme.spacing.xl }}>
        <Text style={{ fontFamily: theme.typography.fontFamilyHeading, fontSize: theme.typography.sizes.h1, color: theme.colors.textPrimary, marginBottom: theme.spacing.xxs }}>
          Verifica tu perfil
        </Text>
        <Text style={{ color: theme.colors.textSecondary, marginBottom: theme.spacing.lg }}>
          Hazte una selfie ahora mismo (no una foto de galería) para confirmar que eres tú.
          Un moderador la revisa a mano — nunca se comparte ni se usa para nada más que esto.
        </Text>

        {request ? (
          <View
            style={{
              flexDirection: 'row',
              alignItems: 'center',
              backgroundColor: theme.colors.surface,
              borderRadius: theme.radius.md,
              padding: theme.spacing.md,
              marginBottom: theme.spacing.lg,
            }}
          >
            <Text style={{ fontSize: 24, marginRight: theme.spacing.sm }}>{STATUS_COPY[request.status].emoji}</Text>
            <Text style={{ color: theme.colors[STATUS_COPY[request.status].color], flex: 1, fontFamily: theme.typography.fontFamilyBodyMedium }}>
              {STATUS_COPY[request.status].label}
            </Text>
          </View>
        ) : null}

        {canSubmitNew ? (
          <>
            <Pressable
              onPress={handleTakeSelfie}
              style={{
                width: 200,
                height: 260,
                alignSelf: 'center',
                borderRadius: theme.radius.md,
                backgroundColor: theme.colors.surface,
                borderWidth: 1.5,
                borderColor: theme.colors.border,
                borderStyle: 'dashed',
                alignItems: 'center',
                justifyContent: 'center',
                overflow: 'hidden',
                marginBottom: theme.spacing.lg,
              }}
            >
              {selfieUri ? (
                <Image source={{ uri: selfieUri }} style={{ width: '100%', height: '100%' }} />
              ) : (
                <>
                  <Text style={{ fontSize: 32, marginBottom: 8 }}>🤳</Text>
                  <Text style={{ color: theme.colors.textSecondary }}>Hacerme una selfie</Text>
                </>
              )}
            </Pressable>

            <Button label="Enviar a revisión" onPress={handleSubmit} disabled={!selfieUri} loading={submitting} />
          </>
        ) : null}
      </ScrollView>
    </ScreenContainer>
  );
}
