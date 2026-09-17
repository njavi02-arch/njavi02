import React from 'react';
import { FlatList, Image, Pressable, Text, View } from 'react-native';
import dayjs from 'dayjs';
import 'dayjs/locale/es';
import relativeTime from 'dayjs/plugin/relativeTime';
import type { NativeStackScreenProps } from '@react-navigation/native-stack';
import { useTheme } from '../../theme/ThemeProvider';
import { ScreenContainer } from '../../components/ScreenContainer';
import { LoadingState } from '../../components/LoadingState';
import { ErrorState } from '../../components/ErrorState';
import { EmptyState } from '../../components/EmptyState';
import { useConversations, useIncomingRequests } from '../../hooks/useConversations';
import { useAuthStore } from '../../store/authStore';
import type { MessagesStackParamList } from '../../navigation/types';

dayjs.extend(relativeTime);
dayjs.locale('es');

type Props = NativeStackScreenProps<MessagesStackParamList, 'MessagesList'>;

export function MessagesListScreen({ navigation }: Props) {
  const theme = useTheme();
  const session = useAuthStore((s) => s.session);
  const conversations = useConversations();
  const requests = useIncomingRequests();

  if (conversations.isLoading) {
    return (
      <ScreenContainer>
        <LoadingState />
      </ScreenContainer>
    );
  }

  if (conversations.isError) {
    return (
      <ScreenContainer>
        <ErrorState onRetry={() => conversations.refetch()} />
      </ScreenContainer>
    );
  }

  const pendingCount = requests.data?.length ?? 0;

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
        Mensajes
      </Text>

      {pendingCount > 0 ? (
        <Pressable
          onPress={() => navigation.navigate('Requests')}
          style={{
            marginHorizontal: theme.spacing.md,
            marginBottom: theme.spacing.md,
            backgroundColor: theme.colors.primary,
            borderRadius: theme.radius.md,
            padding: theme.spacing.md,
            flexDirection: 'row',
            alignItems: 'center',
            justifyContent: 'space-between',
          }}
        >
          <View>
            <Text style={{ color: theme.colors.onPrimary, fontFamily: theme.typography.fontFamilyHeadingSemibold, fontSize: theme.typography.sizes.h3 }}>
              📸 Te han hablado
            </Text>
            <Text style={{ color: theme.colors.onPrimary, opacity: 0.9 }}>
              {pendingCount} {pendingCount === 1 ? 'persona quiere' : 'personas quieren'} hablar contigo
            </Text>
          </View>
          <Text style={{ color: theme.colors.onPrimary, fontSize: 20 }}>›</Text>
        </Pressable>
      ) : null}

      <FlatList
        data={conversations.data ?? []}
        keyExtractor={(item) => item.id}
        contentContainerStyle={{ paddingHorizontal: theme.spacing.md, paddingBottom: theme.spacing.xl }}
        ListEmptyComponent={
          <EmptyState
            emoji="💬"
            title="Todavía no tienes conversaciones"
            description="Ve a Descubrir y empieza a hablar con alguien — el primer paso siempre es el más fácil."
          />
        }
        renderItem={({ item }) => (
          <Pressable
            onPress={() =>
              navigation.navigate('Chat', {
                conversationId: item.id,
                otherProfileId: item.otherProfile.id,
                otherDisplayName: item.otherProfile.display_name,
              })
            }
            style={{ flexDirection: 'row', alignItems: 'center', paddingVertical: theme.spacing.sm }}
          >
            <View
              style={{
                width: 56,
                height: 56,
                borderRadius: 28,
                backgroundColor: theme.colors.surface,
                marginRight: theme.spacing.sm,
                overflow: 'hidden',
                alignItems: 'center',
                justifyContent: 'center',
              }}
            >
              {item.otherProfile.photo_url ? (
                <Image source={{ uri: item.otherProfile.photo_url }} style={{ width: '100%', height: '100%' }} />
              ) : (
                <Text style={{ fontSize: 22 }}>👤</Text>
              )}
            </View>
            <View style={{ flex: 1 }}>
              <Text style={{ color: theme.colors.textPrimary, fontFamily: theme.typography.fontFamilyBodySemibold }}>
                {item.otherProfile.display_name}
              </Text>
              <Text numberOfLines={1} style={{ color: theme.colors.textSecondary, fontSize: theme.typography.sizes.bodySmall }}>
                {item.lastMessage?.message_type === 'image'
                  ? '📷 Foto'
                  : item.lastMessage?.content ?? 'Conversación iniciada'}
              </Text>
            </View>
            <View style={{ alignItems: 'flex-end' }}>
              <Text style={{ color: theme.colors.textSecondary, fontSize: theme.typography.sizes.caption }}>
                {dayjs(item.last_message_at).fromNow()}
              </Text>
              {item.unreadCount > 0 ? (
                <View
                  style={{
                    marginTop: 4,
                    backgroundColor: theme.colors.primary,
                    borderRadius: theme.radius.pill,
                    minWidth: 20,
                    height: 20,
                    alignItems: 'center',
                    justifyContent: 'center',
                    paddingHorizontal: 6,
                  }}
                >
                  <Text style={{ color: theme.colors.onPrimary, fontSize: 11, fontFamily: theme.typography.fontFamilyBodySemibold }}>
                    {item.unreadCount}
                  </Text>
                </View>
              ) : null}
            </View>
          </Pressable>
        )}
      />
    </ScreenContainer>
  );
}
