import React from 'react';
import { Pressable, Text } from 'react-native';
import dayjs from 'dayjs';
import { useTheme } from '../theme/ThemeProvider';
import { useDailyStreak } from '../hooks/useEconomy';

interface StreakAtRiskBannerProps {
  /** Navega a Perfil > Racha diaria. Se pasa desde fuera para no acoplar este componente a
   * un tipo de navegación concreto (se usa desde el stack de Descubrir). */
  onPressGoToStreak: () => void;
}

/**
 * Aviso de racha en riesgo — inspirado en el mecanismo de aversión a la pérdida que hace
 * funcionar las rachas de Duolingo (ver PRODUCT_BRAIN.md → INVESTIGACIÓN: los usuarios con
 * racha de 7+ días vuelven ~2,3x más). Sin un job programado en el servidor (no hay
 * proyecto Supabase desplegado en este entorno, ver docs/07-roadmap-and-scaling.md) no
 * podemos enviar un push proactivo por la tarde — así que el recordatorio aparece en la
 * pantalla de mayor tráfico (Descubrir) nada más abrir la app, que es el momento en que sí
 * podemos actuar.
 */
export function StreakAtRiskBanner({ onPressGoToStreak }: StreakAtRiskBannerProps) {
  const theme = useTheme();
  const { data: streak } = useDailyStreak();

  if (!streak || streak.current_streak <= 0) return null;
  const today = dayjs().format('YYYY-MM-DD');
  const alreadyClaimedToday = streak.last_checkin_date === today;
  if (alreadyClaimedToday) return null;

  return (
    <Pressable
      onPress={onPressGoToStreak}
      style={{
        flexDirection: 'row',
        alignItems: 'center',
        justifyContent: 'space-between',
        backgroundColor: theme.colors.surface,
        borderRadius: theme.radius.md,
        borderWidth: 1,
        borderColor: theme.colors.warning,
        paddingVertical: theme.spacing.sm,
        paddingHorizontal: theme.spacing.md,
        marginHorizontal: theme.spacing.md,
        marginTop: theme.spacing.sm,
        marginBottom: theme.spacing.sm,
      }}
    >
      <Text style={{ color: theme.colors.textPrimary, fontFamily: theme.typography.fontFamilyBodyMedium, flex: 1 }}>
        🔥 No pierdas tu racha de {streak.current_streak} {streak.current_streak === 1 ? 'día' : 'días'} — reclama la recompensa de hoy
      </Text>
      <Text style={{ color: theme.colors.primary, fontFamily: theme.typography.fontFamilyBodySemibold }}>Ir ›</Text>
    </Pressable>
  );
}
