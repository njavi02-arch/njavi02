import React, { useState } from 'react';
import { Alert, ScrollView, Text, View } from 'react-native';
import dayjs from 'dayjs';
import { useQueryClient } from '@tanstack/react-query';
import { useTheme } from '../../theme/ThemeProvider';
import { ScreenContainer } from '../../components/ScreenContainer';
import { LoadingState } from '../../components/LoadingState';
import { Button } from '../../components/Button';
import { useAppConfig, useDailyStreak } from '../../hooks/useEconomy';
import { claimDailyStreak } from '../../services/economy';

export function StreakScreen() {
  const theme = useTheme();
  const { data: streak, isLoading } = useDailyStreak();
  const { data: config } = useAppConfig();
  const queryClient = useQueryClient();
  const [claiming, setClaiming] = useState(false);

  const claimedToday = streak?.last_checkin_date === dayjs().format('YYYY-MM-DD');

  async function handleClaim() {
    setClaiming(true);
    try {
      const result = await claimDailyStreak();
      queryClient.invalidateQueries({ queryKey: ['streak'] });
      queryClient.invalidateQueries({ queryKey: ['wallets'] });
      const parts = [
        result.coins > 0 ? `${result.coins} 🪙` : null,
        result.superLikes > 0 ? `${result.superLikes} ✨ Super Likes` : null,
        result.messageCredits > 0 ? `${result.messageCredits} créditos de mensaje` : null,
      ].filter(Boolean);
      Alert.alert('¡Recompensa reclamada!', `Día ${result.day}: ${parts.join(', ')}`);
    } catch (e) {
      Alert.alert('No se pudo reclamar', e instanceof Error ? e.message : 'Inténtalo de nuevo');
    } finally {
      setClaiming(false);
    }
  }

  if (isLoading || !config) {
    return (
      <ScreenContainer>
        <LoadingState />
      </ScreenContainer>
    );
  }

  const currentCycleDay = streak?.next_reward_day ?? 1;

  return (
    <ScreenContainer>
      <ScrollView contentContainerStyle={{ paddingTop: theme.spacing.md, paddingBottom: theme.spacing.xl }}>
        <Text style={{ fontFamily: theme.typography.fontFamilyHeading, fontSize: theme.typography.sizes.h1, color: theme.colors.textPrimary }}>
          🔥 Racha diaria
        </Text>
        <Text style={{ color: theme.colors.textSecondary, marginTop: theme.spacing.xxs, marginBottom: theme.spacing.lg }}>
          Llevas {streak?.current_streak ?? 0} días seguidos. Racha máxima: {streak?.longest_streak ?? 0}.
        </Text>

        <View style={{ flexDirection: 'row', flexWrap: 'wrap', marginBottom: theme.spacing.lg }}>
          {config.streak_rewards.map((reward) => {
            const isToday = reward.day === currentCycleDay && !claimedToday;
            const isPast = reward.day < currentCycleDay || (reward.day === currentCycleDay && claimedToday);
            return (
              <View
                key={reward.day}
                style={{
                  width: '30%',
                  marginRight: '3%',
                  marginBottom: 10,
                  aspectRatio: 0.85,
                  borderRadius: theme.radius.md,
                  alignItems: 'center',
                  justifyContent: 'center',
                  backgroundColor: isToday ? theme.colors.primary : theme.colors.surface,
                  borderWidth: reward.isSpecial ? 2 : 0,
                  borderColor: theme.colors.secondary,
                  opacity: isPast ? 0.5 : 1,
                }}
              >
                <Text style={{ color: isToday ? theme.colors.onPrimary : theme.colors.textSecondary, fontSize: theme.typography.sizes.caption }}>
                  Día {reward.day}
                </Text>
                <Text style={{ fontSize: 20, marginVertical: 4 }}>{reward.isSpecial ? (reward.day === 7 ? '🎁' : '✨') : '🪙'}</Text>
                <Text style={{ color: isToday ? theme.colors.onPrimary : theme.colors.textPrimary, fontFamily: theme.typography.fontFamilyBodySemibold, fontSize: theme.typography.sizes.caption, textAlign: 'center' }}>
                  {reward.coins > 0 ? `${reward.coins} monedas` : reward.superLikes > 0 ? `${reward.superLikes} Super Likes` : `${reward.messageCredits} mensajes`}
                </Text>
              </View>
            );
          })}
        </View>

        <Button
          label={claimedToday ? 'Ya reclamado hoy — vuelve mañana' : `Reclamar recompensa del día ${currentCycleDay}`}
          onPress={handleClaim}
          disabled={claimedToday || claiming}
          loading={claiming}
        />
      </ScrollView>
    </ScreenContainer>
  );
}
