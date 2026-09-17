import React, { useState } from 'react';
import { FlatList, Image, Text, View } from 'react-native';
import dayjs from 'dayjs';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { useTheme } from '../../theme/ThemeProvider';
import { ScreenContainer } from '../../components/ScreenContainer';
import { LoadingState } from '../../components/LoadingState';
import { EmptyState } from '../../components/EmptyState';
import { Button } from '../../components/Button';
import { useAuthStore } from '../../store/authStore';
import { listSecretAdmirers, listWhoViewedMe, revealSecretAdmirer } from '../../services/economy';
import { useAppConfig } from '../../hooks/useEconomy';

type Tab = 'views' | 'admirers';

export function ActivityScreen() {
  const theme = useTheme();
  const session = useAuthStore((s) => s.session);
  const profile = useAuthStore((s) => s.profile);
  const [tab, setTab] = useState<Tab>('views');
  const queryClient = useQueryClient();
  const { data: config } = useAppConfig();

  const viewsQuery = useQuery({
    queryKey: ['who-viewed-me', session?.user.id],
    queryFn: () => listWhoViewedMe(session!.user.id),
    enabled: Boolean(session),
  });

  const admirersQuery = useQuery({
    queryKey: ['secret-admirers', session?.user.id],
    queryFn: () => listSecretAdmirers(session!.user.id),
    enabled: Boolean(session),
  });

  async function handleReveal(viewerId: string) {
    await revealSecretAdmirer(viewerId);
    queryClient.invalidateQueries({ queryKey: ['secret-admirers', session?.user.id] });
    queryClient.invalidateQueries({ queryKey: ['wallets'] });
  }

  return (
    <ScreenContainer padded={false}>
      <Text
        style={{
          fontFamily: theme.typography.fontFamilyHeading,
          fontSize: theme.typography.sizes.h1,
          color: theme.colors.textPrimary,
          paddingHorizontal: theme.spacing.md,
          marginBottom: theme.spacing.sm,
        }}
      >
        Actividad
      </Text>

      <View style={{ flexDirection: 'row', paddingHorizontal: theme.spacing.md, marginBottom: theme.spacing.md }}>
        {(
          [
            { key: 'views', label: 'Quién te ha visto' },
            { key: 'admirers', label: 'Admiradores secretos' },
          ] as const
        ).map((t) => (
          <Button
            key={t.key}
            label={t.label}
            onPress={() => setTab(t.key)}
            variant={tab === t.key ? 'primary' : 'outline'}
            fullWidth={false}
            style={{ marginRight: 8, paddingHorizontal: 14 }}
          />
        ))}
      </View>

      {tab === 'views' ? (
        viewsQuery.isLoading ? (
          <LoadingState />
        ) : (
          <FlatList
            data={viewsQuery.data ?? []}
            keyExtractor={(item) => item.view.id}
            contentContainerStyle={{ paddingHorizontal: theme.spacing.md, paddingBottom: theme.spacing.xl }}
            ListEmptyComponent={
              <EmptyState emoji="👀" title="Todavía nadie te ha visto" description="Completa tu perfil para aparecer más en el descubrimiento de otras personas." />
            }
            renderItem={({ item }) => (
              <View style={{ flexDirection: 'row', alignItems: 'center', paddingVertical: theme.spacing.sm }}>
                <View
                  style={{
                    width: 48,
                    height: 48,
                    borderRadius: 24,
                    backgroundColor: theme.colors.surface,
                    marginRight: theme.spacing.sm,
                    overflow: 'hidden',
                    alignItems: 'center',
                    justifyContent: 'center',
                  }}
                >
                  {item.viewer.photo_url ? (
                    <Image source={{ uri: item.viewer.photo_url }} style={{ width: '100%', height: '100%' }} />
                  ) : (
                    <Text style={{ fontSize: 18 }}>👤</Text>
                  )}
                </View>
                <View style={{ flex: 1 }}>
                  <Text style={{ color: theme.colors.textPrimary, fontFamily: theme.typography.fontFamilyBodySemibold }}>
                    {item.viewer.display_name}
                  </Text>
                  <Text style={{ color: theme.colors.textSecondary, fontSize: theme.typography.sizes.caption }}>
                    {profile?.is_premium ? dayjs(item.view.created_at).fromNow() : 'Visitó tu perfil recientemente'}
                  </Text>
                </View>
              </View>
            )}
          />
        )
      ) : admirersQuery.isLoading ? (
        <LoadingState />
      ) : (
        <FlatList
          data={admirersQuery.data ?? []}
          keyExtractor={(item) => item.viewerId}
          contentContainerStyle={{ paddingHorizontal: theme.spacing.md, paddingBottom: theme.spacing.xl }}
          ListEmptyComponent={
            <EmptyState emoji="❤️" title="Sin admiradores secretos por ahora" description="Cuando alguien te vea varias veces o te envíe un Super Like sin hablar contigo, aparecerá aquí." />
          }
          renderItem={({ item }) => (
            <View
              style={{
                flexDirection: 'row',
                alignItems: 'center',
                backgroundColor: theme.colors.surface,
                borderRadius: theme.radius.md,
                padding: theme.spacing.sm,
                marginBottom: theme.spacing.sm,
              }}
            >
              <View
                style={{
                  width: 48,
                  height: 48,
                  borderRadius: 24,
                  backgroundColor: theme.colors.surfaceElevated,
                  marginRight: theme.spacing.sm,
                  overflow: 'hidden',
                  alignItems: 'center',
                  justifyContent: 'center',
                }}
              >
                {item.revealed && item.photoUrl ? (
                  <Image source={{ uri: item.photoUrl }} style={{ width: '100%', height: '100%' }} />
                ) : (
                  <Text style={{ fontSize: 18 }}>❤️</Text>
                )}
              </View>
              <View style={{ flex: 1 }}>
                <Text style={{ color: theme.colors.textPrimary, fontFamily: theme.typography.fontFamilyBodySemibold }}>
                  {item.revealed ? item.displayName : 'Admirador secreto'}
                </Text>
                <Text style={{ color: theme.colors.textSecondary, fontSize: theme.typography.sizes.caption }}>
                  {item.superLiked ? '✨ Te envió un Super Like' : `Vio tu perfil ${item.timesViewed} veces`}
                </Text>
              </View>
              {!item.revealed ? (
                <Button
                  label={profile?.is_premium ? 'Ver gratis' : `${config?.secret_admirer_reveal_coin_cost ?? 30} 🪙`}
                  onPress={() => handleReveal(item.viewerId)}
                  fullWidth={false}
                  variant="secondary"
                />
              ) : null}
            </View>
          )}
        />
      )}
    </ScreenContainer>
  );
}
