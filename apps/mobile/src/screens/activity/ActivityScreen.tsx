import React, { useState } from 'react';
import { FlatList, Image, Pressable, Text, View } from 'react-native';
import dayjs from 'dayjs';
import 'dayjs/locale/es';
import relativeTime from 'dayjs/plugin/relativeTime';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { useTheme } from '../../theme/ThemeProvider';
import { ScreenContainer } from '../../components/ScreenContainer';
import { LoadingState } from '../../components/LoadingState';
import { EmptyState } from '../../components/EmptyState';
import { Button } from '../../components/Button';
import { useAuthStore } from '../../store/authStore';
import { listSecretAdmirers, listWhoViewedMe, revealSecretAdmirer } from '../../services/economy';
import { useAppConfig } from '../../hooks/useEconomy';
import { useNotifications } from '../../hooks/useNotifications';
import { markAllNotificationsRead, markNotificationRead } from '../../services/notifications';
import type { NotificationRow } from '../../types/database';

dayjs.extend(relativeTime);
dayjs.locale('es');

type Tab = 'notifications' | 'views' | 'admirers';

const NOTIFICATION_COPY: Record<NotificationRow['type'], { emoji: string; label: string }> = {
  new_message: { emoji: '💬', label: 'Tienes un mensaje nuevo' },
  new_request: { emoji: '📸', label: 'Alguien quiere hablar contigo' },
  request_accepted: { emoji: '✅', label: 'Aceptaron tu solicitud de conversación' },
  super_like_received: { emoji: '✨', label: 'Has recibido un Super Like' },
  profile_viewed: { emoji: '👀', label: 'Alguien ha visto tu perfil' },
  daily_reward_ready: { emoji: '🔥', label: 'Tu recompensa diaria te espera' },
  streak_at_risk: { emoji: '⏳', label: 'Tu racha está a punto de romperse' },
  secret_admirer: { emoji: '❤️', label: 'Tienes un nuevo admirador secreto' },
  promotion: { emoji: '🎁', label: 'Nueva promoción disponible' },
};

export function ActivityScreen() {
  const theme = useTheme();
  const session = useAuthStore((s) => s.session);
  const profile = useAuthStore((s) => s.profile);
  const [tab, setTab] = useState<Tab>('notifications');
  const queryClient = useQueryClient();
  const { data: config } = useAppConfig();
  const notificationsQuery = useNotifications();

  async function handleMarkAllRead() {
    if (!session) return;
    await markAllNotificationsRead(session.user.id);
    queryClient.invalidateQueries({ queryKey: ['notifications', session.user.id] });
  }

  async function handleOpenNotification(notification: NotificationRow) {
    if (!notification.is_read) {
      await markNotificationRead(notification.id);
      queryClient.invalidateQueries({ queryKey: ['notifications', session?.user.id] });
    }
  }

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
            { key: 'notifications', label: 'Notificaciones' },
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

      {tab === 'notifications' ? (
        notificationsQuery.isLoading ? (
          <LoadingState />
        ) : (
          <FlatList
            data={notificationsQuery.data ?? []}
            keyExtractor={(item) => item.id}
            contentContainerStyle={{ paddingHorizontal: theme.spacing.md, paddingBottom: theme.spacing.xl }}
            ListHeaderComponent={
              (notificationsQuery.data ?? []).some((n) => !n.is_read) ? (
                <Button
                  label="Marcar todo como leído"
                  variant="ghost"
                  fullWidth={false}
                  onPress={handleMarkAllRead}
                  style={{ marginBottom: theme.spacing.sm, alignSelf: 'flex-end' }}
                />
              ) : null
            }
            ListEmptyComponent={
              <EmptyState emoji="🔔" title="Sin novedades por ahora" description="Aquí verás mensajes, solicitudes, Super Likes y recompensas en cuanto ocurran." />
            }
            renderItem={({ item }) => {
              const copy = NOTIFICATION_COPY[item.type] ?? { emoji: '🔔', label: item.type };
              return (
                <Pressable
                  onPress={() => handleOpenNotification(item)}
                  style={{
                    flexDirection: 'row',
                    alignItems: 'center',
                    paddingVertical: theme.spacing.sm,
                    opacity: item.is_read ? 0.55 : 1,
                  }}
                >
                  <Text style={{ fontSize: 22, marginRight: theme.spacing.sm }}>{copy.emoji}</Text>
                  <View style={{ flex: 1 }}>
                    <Text style={{ color: theme.colors.textPrimary, fontFamily: theme.typography.fontFamilyBodyMedium }}>
                      {copy.label}
                    </Text>
                    <Text style={{ color: theme.colors.textSecondary, fontSize: theme.typography.sizes.caption }}>
                      {dayjs(item.created_at).fromNow()}
                    </Text>
                  </View>
                  {!item.is_read ? (
                    <View style={{ width: 8, height: 8, borderRadius: 4, backgroundColor: theme.colors.primary }} />
                  ) : null}
                </Pressable>
              );
            }}
          />
        )
      ) : tab === 'views' ? (
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
