import React from 'react';
import { Alert, ScrollView, Text, View } from 'react-native';
import { useTheme } from '../../theme/ThemeProvider';
import { ScreenContainer } from '../../components/ScreenContainer';
import { LoadingState } from '../../components/LoadingState';
import { Button } from '../../components/Button';
import { useWallets } from '../../hooks/useEconomy';

const COIN_PACKS = [
  { coins: 100, priceLabel: '0,99 €' },
  { coins: 550, priceLabel: '4,99 €' },
  { coins: 1200, priceLabel: '9,99 €' },
];

function StatCard({ emoji, label, value }: { emoji: string; label: string; value: number | string }) {
  const theme = useTheme();
  return (
    <View
      style={{
        flex: 1,
        backgroundColor: theme.colors.surface,
        borderRadius: theme.radius.md,
        padding: theme.spacing.md,
        marginRight: theme.spacing.sm,
        alignItems: 'center',
      }}
    >
      <Text style={{ fontSize: 24 }}>{emoji}</Text>
      <Text style={{ color: theme.colors.textPrimary, fontFamily: theme.typography.fontFamilyHeadingSemibold, fontSize: theme.typography.sizes.h2, marginTop: 4 }}>
        {value}
      </Text>
      <Text style={{ color: theme.colors.textSecondary, fontSize: theme.typography.sizes.caption }}>{label}</Text>
    </View>
  );
}

export function WalletScreen() {
  const theme = useTheme();
  const { data: wallets, isLoading } = useWallets();

  function handleBuy(coins: number) {
    // La pasarela de pago real (Stripe/RevenueCat/IAP) no está conectada en este MVP —
    // implica dar de alta un servicio de cobro real, fuera del alcance autónomo de esta
    // build (ver docs/ASSUMPTIONS.md y docs/07-roadmap-and-scaling.md). La arquitectura
    // (coin_transactions, grant_coins) ya está lista para conectarla.
    Alert.alert(
      'Próximamente',
      `La compra de ${coins} monedas necesita una pasarela de pago real conectada (Stripe/Apple/Google). La base de datos y la lógica ya están preparadas — solo falta dar de alta el proveedor de pago.`,
    );
  }

  if (isLoading) {
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
          Monedas
        </Text>

        <View style={{ flexDirection: 'row', marginBottom: theme.spacing.lg }}>
          <StatCard emoji="🪙" label="Monedas" value={wallets?.coins ?? 0} />
          <StatCard emoji="✉️" label="Créditos mensaje" value={wallets?.messageCredits ?? 0} />
          <StatCard emoji="✨" label="Super Likes" value={wallets?.superLikeCredits ?? 0} />
        </View>

        <Text style={{ fontFamily: theme.typography.fontFamilyHeadingSemibold, fontSize: theme.typography.sizes.h3, color: theme.colors.textPrimary, marginBottom: theme.spacing.sm }}>
          Comprar monedas
        </Text>
        {COIN_PACKS.map((pack) => (
          <View
            key={pack.coins}
            style={{
              flexDirection: 'row',
              alignItems: 'center',
              justifyContent: 'space-between',
              backgroundColor: theme.colors.surface,
              borderRadius: theme.radius.md,
              padding: theme.spacing.md,
              marginBottom: theme.spacing.sm,
            }}
          >
            <Text style={{ color: theme.colors.textPrimary, fontFamily: theme.typography.fontFamilyBodySemibold }}>🪙 {pack.coins} monedas</Text>
            <Button label={pack.priceLabel} onPress={() => handleBuy(pack.coins)} fullWidth={false} variant="outline" />
          </View>
        ))}

        <Text style={{ color: theme.colors.textSecondary, fontSize: theme.typography.sizes.caption, marginTop: theme.spacing.md }}>
          Las monedas se usan para Super Likes extra, desbloquear fotos y revelar
          admiradores secretos. También puedes conseguirlas gratis con la racha diaria.
        </Text>
      </ScrollView>
    </ScreenContainer>
  );
}
