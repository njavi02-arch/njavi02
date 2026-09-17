import React from 'react';
import { Alert, FlatList, Text, View } from 'react-native';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { useTheme } from '../../theme/ThemeProvider';
import { ScreenContainer } from '../../components/ScreenContainer';
import { LoadingState } from '../../components/LoadingState';
import { EmptyState } from '../../components/EmptyState';
import { Button } from '../../components/Button';
import { useAuthStore } from '../../store/authStore';
import { listMyBlocks, unblockUser } from '../../services/safety';

export function BlockedUsersScreen() {
  const theme = useTheme();
  const session = useAuthStore((s) => s.session);
  const queryClient = useQueryClient();

  const { data, isLoading, refetch } = useQuery({
    queryKey: ['my-blocks', session?.user.id],
    queryFn: () => listMyBlocks(session!.user.id),
    enabled: Boolean(session),
  });

  async function handleUnblock(blockedId: string) {
    if (!session) return;
    try {
      await unblockUser(session.user.id, blockedId);
      queryClient.invalidateQueries({ queryKey: ['my-blocks', session.user.id] });
    } catch (e) {
      Alert.alert('No se pudo desbloquear', e instanceof Error ? e.message : 'Inténtalo de nuevo');
    }
  }

  if (isLoading) {
    return (
      <ScreenContainer>
        <LoadingState />
      </ScreenContainer>
    );
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
        Usuarios bloqueados
      </Text>

      <FlatList
        data={data ?? []}
        keyExtractor={(item) => item.id}
        refreshing={isLoading}
        onRefresh={refetch}
        contentContainerStyle={{ paddingHorizontal: theme.spacing.md, paddingBottom: theme.spacing.xl }}
        ListEmptyComponent={
          <EmptyState emoji="🚫" title="No has bloqueado a nadie" description="Cuando bloqueas a alguien, aparecerá aquí y podrás desbloquearlo cuando quieras." />
        }
        renderItem={({ item }) => (
          <View
            style={{
              flexDirection: 'row',
              alignItems: 'center',
              justifyContent: 'space-between',
              paddingVertical: theme.spacing.sm,
            }}
          >
            <Text style={{ color: theme.colors.textPrimary, fontFamily: theme.typography.fontFamilyBodyMedium }}>
              {item.blocked?.display_name ?? 'Usuario'}
            </Text>
            <Button label="Desbloquear" variant="outline" fullWidth={false} onPress={() => handleUnblock(item.blocked_id)} />
          </View>
        )}
      />
    </ScreenContainer>
  );
}
