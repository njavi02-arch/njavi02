import React, { useMemo } from 'react';
import { ScrollView, Text, View } from 'react-native';
import { useQuery } from '@tanstack/react-query';
import dayjs from 'dayjs';
import type { NativeStackScreenProps } from '@react-navigation/native-stack';
import { useTheme } from '../../theme/ThemeProvider';
import { ScreenContainer } from '../../components/ScreenContainer';
import { LoadingState } from '../../components/LoadingState';
import { Button } from '../../components/Button';
import { PhotoGallery } from '../../components/PhotoGallery';
import { ProfileStrengthIndicator } from '../../components/ProfileStrengthIndicator';
import { useAuthStore } from '../../store/authStore';
import { getPhotosForProfile } from '../../services/profiles';
import { useAppConfig, useWallets, useDailyStreak } from '../../hooks/useEconomy';
import { useProfileViewsCount } from '../../hooks/useProfileViews';
import { signOut } from '../../services/auth';
import type { ProfileStackParamList } from '../../navigation/types';

type Props = NativeStackScreenProps<ProfileStackParamList, 'MyProfile'>;

function StatPill({ label, value }: { label: string; value: string | number }) {
  const theme = useTheme();
  return (
    <View style={{ alignItems: 'center', flex: 1 }}>
      <Text style={{ color: theme.colors.textPrimary, fontFamily: theme.typography.fontFamilyHeadingSemibold, fontSize: theme.typography.sizes.h3 }}>
        {value}
      </Text>
      <Text style={{ color: theme.colors.textSecondary, fontSize: theme.typography.sizes.caption }}>{label}</Text>
    </View>
  );
}

export function MyProfileScreen({ navigation }: Props) {
  const theme = useTheme();
  const profile = useAuthStore((s) => s.profile);
  const { data: config } = useAppConfig();
  const { data: wallets } = useWallets();
  const { data: streak } = useDailyStreak();
  const { data: viewsCount = 0 } = useProfileViewsCount();
  const photosQuery = useQuery({
    queryKey: ['photos', profile?.id],
    queryFn: () => getPhotosForProfile(profile!.id),
    enabled: Boolean(profile),
  });

  const claimedToday = useMemo(
    () => streak?.last_checkin_date === dayjs().format('YYYY-MM-DD'),
    [streak?.last_checkin_date],
  );

  const nextRewardDay = useMemo(() => {
    if (!config || !streak) return null;
    const reward = config.streak_rewards.find((r) => r.day === streak.next_reward_day);
    return reward;
  }, [config, streak]);

  if (!profile) {
    return (
      <ScreenContainer>
        <LoadingState />
      </ScreenContainer>
    );
  }

  return (
    <ScreenContainer>
      <ScrollView contentContainerStyle={{ paddingTop: theme.spacing.sm, paddingBottom: theme.spacing.xl }}>
        <View style={{ flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: theme.spacing.md }}>
          <Text style={{ fontFamily: theme.typography.fontFamilyHeading, fontSize: theme.typography.sizes.h1, color: theme.colors.textPrimary }}>
            {profile.display_name} {profile.is_verified ? '✅' : ''}
          </Text>
          <Button label="Editar" variant="outline" fullWidth={false} onPress={() => navigation.navigate('EditProfile')} />
        </View>

        <View
          style={{
            flexDirection: 'row',
            backgroundColor: theme.colors.surface,
            borderRadius: theme.radius.md,
            padding: theme.spacing.md,
            marginBottom: theme.spacing.md,
          }}
        >
          <StatPill label="Perfil completo" value={`${profile.profile_completion_pct}%`} />
          <StatPill label="Monedas" value={wallets?.coins ?? '—'} />
          <StatPill label="Créditos msj." value={wallets?.messageCredits ?? '—'} />
        </View>

        <ProfileStrengthIndicator
          completionPct={profile.profile_completion_pct}
          onPressAction={() => navigation.navigate('EditProfile')}
        />

        {viewsCount > 0 && (
          <View
            style={{
              backgroundColor: theme.colors.surfaceElevated,
              borderRadius: theme.radius.md,
              padding: theme.spacing.md,
              marginBottom: theme.spacing.md,
              borderLeftWidth: 4,
              borderLeftColor: '#FF6B9D',
              flexDirection: 'row',
              alignItems: 'center',
              justifyContent: 'space-between',
            }}
          >
            <View style={{ flex: 1 }}>
              <Text style={{ color: theme.colors.textPrimary, fontFamily: theme.typography.fontFamilyHeadingSemibold, fontSize: 16, marginBottom: 4 }}>
                👀 {viewsCount} personas te vieron
              </Text>
              <Text style={{ color: theme.colors.textSecondary, fontSize: 12 }}>
                Alguien está interesado en ti
              </Text>
            </View>
            {viewsCount > 5 && (
              <Text style={{ fontSize: 20, marginLeft: 8 }}>🔥</Text>
            )}
          </View>
        )}

        {!claimedToday && nextRewardDay && (
          <View
            style={{
              backgroundColor: theme.colors.primary,
              borderRadius: theme.radius.md,
              padding: theme.spacing.md,
              marginBottom: theme.spacing.md,
              borderLeftWidth: 4,
              borderLeftColor: theme.colors.secondary,
            }}
          >
            <Text style={{ color: theme.colors.onPrimary, fontFamily: theme.typography.fontFamilyHeadingSemibold, fontSize: 16, marginBottom: 8 }}>
              🎉 Racha: Día {streak?.next_reward_day} listo
            </Text>
            <Text style={{ color: theme.colors.onPrimary, opacity: 0.9, marginBottom: 12 }}>
              {nextRewardDay.coins > 0 && `${nextRewardDay.coins} 🪙`}
              {nextRewardDay.superLikes > 0 && (nextRewardDay.coins > 0 ? ' + ' : '') + `${nextRewardDay.superLikes} ✨`}
              {nextRewardDay.messageCredits > 0 && (nextRewardDay.coins > 0 || nextRewardDay.superLikes > 0 ? ' + ' : '') + `${nextRewardDay.messageCredits} 💬`}
            </Text>
            <Button label="Reclamar ahora" onPress={() => navigation.navigate('Streak')} />
          </View>
        )}

        <PhotoGallery
          photos={photosQuery.data?.map((p) => ({ url: p.url, position: p.position })) ?? []}
          config={config ?? { public_photos_count: 3 }}
          isUnlocked
        />

        {profile.bio ? (
          <Text style={{ color: theme.colors.textPrimary, marginTop: theme.spacing.md }}>{profile.bio}</Text>
        ) : null}

        <View style={{ marginTop: theme.spacing.lg }}>
          {!profile.is_verified ? (
            <Button label="✅ Verificar mi perfil" variant="outline" onPress={() => navigation.navigate('VerifyProfile')} style={{ marginBottom: 10 }} />
          ) : null}
          <Button label="🪙 Monedas y tienda" variant="outline" onPress={() => navigation.navigate('Wallet')} style={{ marginBottom: 10 }} />
          <Button label="🔥 Racha diaria" variant="outline" onPress={() => navigation.navigate('Streak')} style={{ marginBottom: 10 }} />
          <Button label="⭐ Orbita Premium" variant="secondary" onPress={() => navigation.navigate('Premium')} style={{ marginBottom: 10 }} />
          <Button label="Ajustes" variant="ghost" onPress={() => navigation.navigate('Settings')} style={{ marginBottom: 10 }} />
          <Button label="Cerrar sesión" variant="ghost" onPress={() => signOut()} />
        </View>
      </ScrollView>
    </ScreenContainer>
  );
}
