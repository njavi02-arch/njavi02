import React, { useState } from 'react';
import { Alert, ScrollView, Switch, Text, View } from 'react-native';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import type { NativeStackScreenProps } from '@react-navigation/native-stack';
import { useTheme } from '../../theme/ThemeProvider';
import { ScreenContainer } from '../../components/ScreenContainer';
import { LoadingState } from '../../components/LoadingState';
import { Button } from '../../components/Button';
import { useAuthStore } from '../../store/authStore';
import { supabase } from '../../lib/supabase';
import { deleteMyAccount } from '../../services/safety';
import { signOut } from '../../services/auth';
import type { NotificationPreferencesRow } from '../../types/database';
import type { ProfileStackParamList } from '../../navigation/types';

type Props = NativeStackScreenProps<ProfileStackParamList, 'Settings'>;

const PREFERENCE_LABELS: { key: keyof Omit<NotificationPreferencesRow, 'profile_id'>; label: string }[] = [
  { key: 'new_message', label: 'Nuevos mensajes' },
  { key: 'new_request', label: 'Nuevas solicitudes de conversación' },
  { key: 'super_like_received', label: 'Super Likes recibidos' },
  { key: 'profile_viewed', label: 'Alguien ha visto tu perfil' },
  { key: 'daily_reward_ready', label: 'Recompensa diaria disponible' },
  { key: 'secret_admirer', label: 'Nuevos admiradores secretos' },
  { key: 'promotions', label: 'Promociones' },
];

export function SettingsScreen({ navigation }: Props) {
  const theme = useTheme();
  const session = useAuthStore((s) => s.session);
  const queryClient = useQueryClient();
  const [deleting, setDeleting] = useState(false);

  const { data: prefs, isLoading } = useQuery({
    queryKey: ['notification-preferences', session?.user.id],
    queryFn: async () => {
      const { data, error } = await supabase
        .from('notification_preferences')
        .select('*')
        .eq('profile_id', session!.user.id)
        .single();
      if (error) throw error;
      return data as NotificationPreferencesRow;
    },
    enabled: Boolean(session),
  });

  async function togglePreference(key: keyof Omit<NotificationPreferencesRow, 'profile_id'>, value: boolean) {
    if (!session) return;
    await supabase.from('notification_preferences').update({ [key]: value }).eq('profile_id', session.user.id);
    queryClient.invalidateQueries({ queryKey: ['notification-preferences', session.user.id] });
  }

  function handleDeleteAccount() {
    Alert.alert(
      'Eliminar cuenta',
      'Esta acción es irreversible: tu perfil, fotos y conversaciones dejarán de estar visibles para otras personas. ¿Seguro que quieres continuar?',
      [
        { text: 'Cancelar', style: 'cancel' },
        {
          text: 'Eliminar',
          style: 'destructive',
          onPress: async () => {
            if (!session) return;
            setDeleting(true);
            try {
              await deleteMyAccount(session.user.id);
              await signOut();
            } catch (e) {
              Alert.alert('Error', e instanceof Error ? e.message : 'No se pudo eliminar la cuenta');
            } finally {
              setDeleting(false);
            }
          },
        },
      ],
    );
  }

  if (isLoading || !prefs) {
    return (
      <ScreenContainer>
        <LoadingState />
      </ScreenContainer>
    );
  }

  return (
    <ScreenContainer>
      <ScrollView contentContainerStyle={{ paddingTop: theme.spacing.md, paddingBottom: theme.spacing.xl }}>
        <Text style={{ fontFamily: theme.typography.fontFamilyHeading, fontSize: theme.typography.sizes.h1, color: theme.colors.textPrimary, marginBottom: theme.spacing.md }}>
          Ajustes
        </Text>

        <Text style={{ fontFamily: theme.typography.fontFamilyHeadingSemibold, fontSize: theme.typography.sizes.h3, color: theme.colors.textPrimary, marginBottom: theme.spacing.sm }}>
          Notificaciones
        </Text>
        {PREFERENCE_LABELS.map(({ key, label }) => (
          <View key={key} style={{ flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', paddingVertical: 10 }}>
            <Text style={{ color: theme.colors.textPrimary, flex: 1 }}>{label}</Text>
            <Switch
              value={Boolean(prefs[key])}
              onValueChange={(v) => togglePreference(key, v)}
              trackColor={{ true: theme.colors.primary, false: theme.colors.border }}
            />
          </View>
        ))}

        <View style={{ marginTop: theme.spacing.xl }}>
          <Button label="Términos de Servicio" variant="ghost" onPress={() => navigation.navigate('Terms')} style={{ marginBottom: 4 }} />
          <Button label="Política de Privacidad" variant="ghost" onPress={() => navigation.navigate('Privacy')} style={{ marginBottom: 10 }} />
          <Button label="Cerrar sesión" variant="outline" onPress={() => signOut()} style={{ marginBottom: 10 }} />
          <Button label="Eliminar cuenta" variant="danger" onPress={handleDeleteAccount} loading={deleting} />
        </View>
      </ScrollView>
    </ScreenContainer>
  );
}
