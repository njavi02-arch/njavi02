import React from 'react';
import { Alert, ScrollView, Text, View } from 'react-native';
import { useTheme } from '../../theme/ThemeProvider';
import { ScreenContainer } from '../../components/ScreenContainer';
import { LoadingState } from '../../components/LoadingState';
import { Button } from '../../components/Button';
import { useAuthStore } from '../../store/authStore';
import { useAppConfig } from '../../hooks/useEconomy';

const BENEFITS = [
  '👀 Ver quién te ha visto, sin límite y con la hora exacta',
  '❤️ Descubrir todos tus admiradores secretos',
  '🔓 Ver las fotos bloqueadas de cualquier perfil',
  '✨ Más Super Likes gratis cada día',
  '✉️ Más créditos de mensaje para iniciar conversaciones',
  '🚀 Mayor visibilidad en Descubrir',
];

function formatPrice(cents: number, currency: string): string {
  return new Intl.NumberFormat('es-ES', { style: 'currency', currency }).format(cents / 100);
}

export function PremiumScreen() {
  const theme = useTheme();
  const profile = useAuthStore((s) => s.profile);
  const { data: config, isLoading } = useAppConfig();

  function handleSubscribe() {
    // Igual que en WalletScreen: sin pasarela de pago real conectada todavía — ver
    // premium_subscriptions en el esquema, ya lista para recibir el webhook de
    // Stripe/App Store/Play Store cuando se dé de alta ese servicio.
    Alert.alert(
      'Próximamente',
      'La suscripción Premium necesita una pasarela de pago real conectada. La base de datos (premium_subscriptions) ya está lista para activarla en cuanto se conecte.',
    );
  }

  if (isLoading || !config) {
    return (
      <ScreenContainer>
        <LoadingState />
      </ScreenContainer>
    );
  }

  return (
    <ScreenContainer>
      <ScrollView contentContainerStyle={{ paddingTop: theme.spacing.md, paddingBottom: theme.spacing.xl }}>
        <Text style={{ fontSize: 40, textAlign: 'center', marginBottom: theme.spacing.sm }}>⭐</Text>
        <Text style={{ fontFamily: theme.typography.fontFamilyHeading, fontSize: theme.typography.sizes.h1, color: theme.colors.textPrimary, textAlign: 'center', marginBottom: theme.spacing.md }}>
          Orbita Premium
        </Text>

        {profile?.is_premium ? (
          <Text style={{ textAlign: 'center', color: theme.colors.success, fontFamily: theme.typography.fontFamilyBodySemibold, marginBottom: theme.spacing.md }}>
            Ya eres Premium ✨
          </Text>
        ) : null}

        <View style={{ backgroundColor: theme.colors.surface, borderRadius: theme.radius.md, padding: theme.spacing.md, marginBottom: theme.spacing.lg }}>
          {BENEFITS.map((b) => (
            <Text key={b} style={{ color: theme.colors.textPrimary, marginBottom: theme.spacing.xs }}>
              {b}
            </Text>
          ))}
        </View>

        {!profile?.is_premium ? (
          <>
            <Button
              label={`Mensual · ${formatPrice(config.premium_price_monthly_cents, config.premium_currency)}`}
              onPress={handleSubscribe}
              style={{ marginBottom: 10 }}
            />
            <Button
              label={`Anual · ${formatPrice(config.premium_price_yearly_cents, config.premium_currency)} (ahorra más)`}
              variant="secondary"
              onPress={handleSubscribe}
            />
          </>
        ) : null}
      </ScrollView>
    </ScreenContainer>
  );
}
