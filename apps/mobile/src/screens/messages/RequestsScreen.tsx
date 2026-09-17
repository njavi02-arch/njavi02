import React, { useState } from 'react';
import { FlatList, Image, Text, View } from 'react-native';
import { useQueryClient } from '@tanstack/react-query';
import type { NativeStackScreenProps } from '@react-navigation/native-stack';
import { useTheme } from '../../theme/ThemeProvider';
import { ScreenContainer } from '../../components/ScreenContainer';
import { EmptyState } from '../../components/EmptyState';
import { Button } from '../../components/Button';
import { useIncomingRequests } from '../../hooks/useConversations';
import { acceptConversationRequest, declineConversationRequest } from '../../services/conversations';
import type { MessagesStackParamList } from '../../navigation/types';

type Props = NativeStackScreenProps<MessagesStackParamList, 'Requests'>;

export function RequestsScreen({ navigation }: Props) {
  const theme = useTheme();
  const { data, isLoading, refetch } = useIncomingRequests();
  const queryClient = useQueryClient();
  const [busyId, setBusyId] = useState<string | null>(null);

  async function handleAccept(requestId: string, senderId: string, senderName: string) {
    setBusyId(requestId);
    try {
      const conversationId = await acceptConversationRequest(requestId);
      await refetch();
      queryClient.invalidateQueries({ queryKey: ['conversations'] });
      navigation.replace('Chat', { conversationId, otherProfileId: senderId, otherDisplayName: senderName });
    } finally {
      setBusyId(null);
    }
  }

  async function handleDecline(requestId: string) {
    setBusyId(requestId);
    try {
      await declineConversationRequest(requestId);
      await refetch();
    } finally {
      setBusyId(null);
    }
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
        Te han hablado
      </Text>

      <FlatList
        data={data ?? []}
        keyExtractor={(item) => item.id}
        refreshing={isLoading}
        onRefresh={refetch}
        contentContainerStyle={{ paddingHorizontal: theme.spacing.md, paddingBottom: theme.spacing.xl }}
        ListEmptyComponent={
          <EmptyState emoji="📭" title="Sin solicitudes por ahora" description="Cuando alguien te escriba por primera vez, aparecerá aquí." />
        }
        renderItem={({ item }) => (
          <View
            style={{
              backgroundColor: theme.colors.surface,
              borderRadius: theme.radius.md,
              padding: theme.spacing.md,
              marginBottom: theme.spacing.sm,
            }}
          >
            <View style={{ flexDirection: 'row', alignItems: 'center', marginBottom: theme.spacing.sm }}>
              <View
                style={{
                  width: 44,
                  height: 44,
                  borderRadius: 22,
                  backgroundColor: theme.colors.surfaceElevated,
                  marginRight: theme.spacing.sm,
                  overflow: 'hidden',
                  alignItems: 'center',
                  justifyContent: 'center',
                }}
              >
                {item.sender.photo_url ? (
                  <Image source={{ uri: item.sender.photo_url }} style={{ width: '100%', height: '100%' }} />
                ) : (
                  <Text style={{ fontSize: 18 }}>👤</Text>
                )}
              </View>
              <Text style={{ color: theme.colors.textPrimary, fontFamily: theme.typography.fontFamilyBodySemibold }}>
                {item.sender.display_name}
              </Text>
            </View>
            <Text style={{ color: theme.colors.textSecondary, marginBottom: theme.spacing.sm }}>
              "{item.first_message}"
            </Text>
            <View style={{ flexDirection: 'row' }}>
              <Button
                label="Ignorar"
                variant="ghost"
                fullWidth={false}
                style={{ marginRight: 8 }}
                onPress={() => handleDecline(item.id)}
                disabled={busyId === item.id}
              />
              <View style={{ flex: 1 }}>
                <Button
                  label="Responder"
                  onPress={() => handleAccept(item.id, item.sender.id, item.sender.display_name)}
                  loading={busyId === item.id}
                />
              </View>
            </View>
          </View>
        )}
      />
    </ScreenContainer>
  );
}
