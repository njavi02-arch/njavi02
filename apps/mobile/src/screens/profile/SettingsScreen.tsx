import React, { useState } from 'react';
import { Alert, ScrollView, Switch, Text, View } from 'react-native';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import type { NativeStackScreenProps } from '@react-navigation/native-stack';
import type { Gender } from '@orbita/shared';
import { useTheme } from '../../theme/ThemeProvider';
import { ScreenContainer } from '../../components/ScreenContainer';
import { LoadingState } from '../../components/LoadingState';
import { Button } from '../../components/Button';
import { Chip } from '../../components/Chip';
import { Stepper } from '../../components/Stepper';
import { useAuthStore } from '../../store/authStore';
import { supabase } from '../../lib/supabase';
import { deleteMyAccount } from '../../services/safety';
import { signOut } from '../../services/auth';
import type { NotificationPreferencesRow, UserPreferencesRow } from '../../types/database';
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

const SHOW_ME_OPTIONS: { value: Gender; label: string }[] = [
  { value: 'female', label: 'Mujeres' },
  { value: 'male', label: 'Hombres' },
  { value: 'non_binary', label: 'No binarias' },
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

  const { data: discoveryPrefs, isLoading: discoveryPrefsLoading } = useQuery({
    queryKey: ['discovery-preferences', session?.user.id],
    queryFn: async () => {
      const { data, error } = await supabase
        .from('user_preferences')
        .select('*')
        .eq('profile_id', session!.user.id)
        .single();
      if (error) throw error;
      return data as UserPreferencesRow;
    },
    enabled: Boolean(session),
  });

  async function togglePreference(key: keyof Omit<NotificationPreferencesRow, 'profile_id'>, value: boolean) {
    if (!session) return;
    await supabase.from('notification_preferences').update({ [key]: value }).eq('profile_id', session.user.id);
    queryClient.invalidateQueries({ queryKey: ['notification-preferences', session.user.id] });
  }

  async function updateDiscoveryPreference(patch: Partial<Omit<UserPreferencesRow, 'profile_id'>>) {
    if (!session) return;
    await supabase.from('user_preferences').update(patch).eq('profile_id', session.user.id);
    queryClient.invalidateQueries({ queryKey: ['discovery-preferences', session.user.id] });
  }

  function toggleShowMeGender(value: Gender) {
    if (!discoveryPrefs) return;
    const has = discoveryPrefs.show_me_gender.includes(value);
    const next = has ? discoveryPrefs.show_me_gender.filter((g) => g !== value) : [...discoveryPrefs.show_me_gender, value];
    if (next.length === 0) return; // siempre debe quedar al menos una opción, o el feed se vaciaría sin explicación
    updateDiscoveryPreference({ show_me_gender: next });
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

        <Text
          style={{
            fontFamily: theme.typography.fontFamilyHeadingSemibold,
            fontSize: theme.typography.sizes.h3,
            color: theme.colors.textPrimary,
            marginTop: theme.spacing.xl,
            marginBottom: theme.spacing.sm,
          }}
        >
          Preferencias de descubrimiento
        </Text>
        {discoveryPrefsLoading || !discoveryPrefs ? (
          <LoadingState />
        ) : (
          <>
            <Stepper
              label="Edad mínima que quieres ver"
              value={discoveryPrefs.min_age}
              min={18}
              max={discoveryPrefs.max_age}
              onChange={(v) => updateDiscoveryPreference({ min_age: v })}
            />
            <Stepper
              label="Edad máxima que quieres ver"
              value={discoveryPrefs.max_age}
              min={discoveryPrefs.min_age}
              max={80}
              onChange={(v) => updateDiscoveryPreference({ max_age: v })}
            />
            <Text
              style={{
                color: theme.colors.textSecondary,
                fontFamily: theme.typography.fontFamilyBodyMedium,
                fontSize: theme.typography.sizes.bodySmall,
                marginBottom: theme.spacing.xs,
              }}
            >
              A quién quieres conocer
            </Text>
            <View style={{ flexDirection: 'row', flexWrap: 'wrap', marginBottom: theme.spacing.sm }}>
              {SHOW_ME_OPTIONS.map((opt) => (
                <Chip
                  key={opt.value}
                  label={opt.label}
                  selected={discoveryPrefs.show_me_gender.includes(opt.value)}
                  onPress={() => toggleShowMeGender(opt.value)}
                />
              ))}
            </View>
            <View style={{ flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', paddingVertical: 10 }}>
              <Text style={{ color: theme.colors.textPrimary, flex: 1 }}>Mostrar solo perfiles verificados ✅</Text>
              <Switch
                value={discoveryPrefs.verified_only}
                onValueChange={(v) => updateDiscoveryPreference({ verified_only: v })}
                trackColor={{ true: theme.colors.primary, false: theme.colors.border }}
              />
            </View>
          </>
        )}

        <View style={{ marginTop: theme.spacing.xl }}>
          <Button label="Usuarios bloqueados" variant="ghost" onPress={() => navigation.navigate('BlockedUsers')} style={{ marginBottom: 4 }} />
          <Button label="Términos de Servicio" variant="ghost" onPress={() => navigation.navigate('Terms')} style={{ marginBottom: 4 }} />
          <Button label="Política de Privacidad" variant="ghost" onPress={() => navigation.navigate('Privacy')} style={{ marginBottom: 10 }} />
          <Button label="Cerrar sesión" variant="outline" onPress={() => signOut()} style={{ marginBottom: 10 }} />
          <Button label="Eliminar cuenta" variant="danger" onPress={handleDeleteAccount} loading={deleting} />
        </View>
      </ScrollView>
    </ScreenContainer>
  );
}
