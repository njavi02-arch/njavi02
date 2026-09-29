import React from 'react';
import { Alert, ScrollView, Text, View, Pressable } from 'react-native';
import { useTheme } from '../../theme/ThemeProvider';
import { ScreenContainer } from '../../components/ScreenContainer';
import { LoadingState } from '../../components/LoadingState';
import { Button } from '../../components/Button';
import { useAuthStore } from '../../store/authStore';
import { useAppConfig } from '../../hooks/useEconomy';
import { usePremiumSubscription } from '../../hooks/useV2DiscoverFeed';

const BENEFITS_V2 = [
  '❤️ Likes ilimitados',
  '✨ SuperLikes: 5/día',
  '🔍 Filtros avanzados de discovery',
  '👀 Ver quién te ha visto',
  '🎯 Algoritmo de compatibilidad ponderado',
  '🚀 Boosts de visibilidad (3x, 30 min)',
];

const PLANS = [
  {
    name: 'Mensual',
    price: '€7.99',
    period: '/mes',
    boosts: '1 boost/mes',
    popular: false,
  },
  {
    name: 'Trimestral',
    price: '€19.99',
    period: '/3 meses',
    boosts: '3 boosts',
    popular: true,
    savings: 'Ahorra 17%',
  },
  {
    name: 'Anual',
    price: '€59.99',
    period: '/año',
    boosts: '12 boosts',
    popular: false,
    savings: 'Ahorra 38%',
  },
];

function formatPrice(cents: number, currency: string): string {
  return new Intl.NumberFormat('es-ES', { style: 'currency', currency }).format(cents / 100);
}

export function PremiumScreen() {
  const theme = useTheme();
  const profile = useAuthStore((s) => s.profile);
  const { data: config, isLoading } = useAppConfig();
  const { data: subscription, isLoading: isLoadingSubscription } = usePremiumSubscription();

  function handleSubscribe(plan: string) {
    Alert.alert(
      'V2.0 Premium',
      `Plan ${plan} - Stripe integration próximamente. La base de datos ya está lista para procesar pagos.`,
    );
  }

  const isLoaded = !isLoading && config && !isLoadingSubscription;

  if (!isLoaded) {
    return (
      <ScreenContainer>
        <LoadingState />
      </ScreenContainer>
    );
  }

  return (
    <ScreenContainer>
      <ScrollView contentContainerStyle={{ paddingTop: theme.spacing.md, paddingBottom: theme.spacing.xl }}>
        <Text style={{ fontSize: 40, textAlign: 'center', marginBottom: theme.spacing.sm }}>✨</Text>
        <Text style={{ fontFamily: theme.typography.fontFamilyHeading, fontSize: theme.typography.sizes.h1, color: theme.colors.textPrimary, textAlign: 'center', marginBottom: theme.spacing.sm }}>
          YUIZZ Premium
        </Text>
        <Text style={{ textAlign: 'center', color: theme.colors.textSecondary, fontFamily: theme.typography.fontFamilyBody, marginBottom: theme.spacing.lg }}>
          Acceso a features V2.0 exclusivos
        </Text>

        {subscription?.isPremium ? (
          <View style={{ backgroundColor: theme.colors.success + '20', borderRadius: theme.radius.md, padding: theme.spacing.md, marginBottom: theme.spacing.lg, borderLeftWidth: 4, borderLeftColor: theme.colors.success }}>
            <Text style={{ color: theme.colors.success, fontFamily: theme.typography.fontFamilyBodySemibold, marginBottom: theme.spacing.xs }}>
              ✅ Ya eres Premium
            </Text>
            <Text style={{ color: theme.colors.textSecondary, fontFamily: theme.typography.fontFamilyBody, fontSize: 12 }}>
              Expires: {subscription.subscription?.expires_at}
            </Text>
            <Text style={{ color: theme.colors.textSecondary, fontFamily: theme.typography.fontFamilyBody, fontSize: 12 }}>
              Boosts: {subscription.subscription?.boosts_used}/{subscription.subscription?.boosts_count}
            </Text>
          </View>
        ) : null}

        <View style={{ backgroundColor: theme.colors.surface, borderRadius: theme.radius.md, padding: theme.spacing.md, marginBottom: theme.spacing.lg }}>
          {BENEFITS_V2.map((b) => (
            <Text key={b} style={{ color: theme.colors.textPrimary, marginBottom: theme.spacing.xs, fontFamily: theme.typography.fontFamilyBody, fontSize: 14 }}>
              {b}
            </Text>
          ))}
        </View>

        {!subscription?.isPremium ? (
          <>
            <Text style={{ fontFamily: theme.typography.fontFamilyBodySemibold, fontSize: 14, color: theme.colors.textSecondary, marginBottom: theme.spacing.md, textTransform: 'uppercase' }}>
              Elige tu plan
            </Text>

            {PLANS.map((plan) => (
              <Pressable
                key={plan.name}
                onPress={() => handleSubscribe(plan.name)}
                style={{
                  backgroundColor: plan.popular ? theme.colors.primary + '20' : theme.colors.surface,
                  borderRadius: theme.radius.md,
                  padding: theme.spacing.md,
                  marginBottom: theme.spacing.md,
                  borderWidth: plan.popular ? 2 : 1,
                  borderColor: plan.popular ? theme.colors.primary : theme.colors.border,
                }}
              >
                {plan.popular && (
                  <View style={{ backgroundColor: theme.colors.primary, paddingHorizontal: theme.spacing.sm, paddingVertical: 4, borderRadius: theme.radius.sm, alignSelf: 'flex-start', marginBottom: theme.spacing.sm }}>
                    <Text style={{ color: '#fff', fontFamily: theme.typography.fontFamilyBodySemibold, fontSize: 10, textTransform: 'uppercase' }}>
                      Popular
                    </Text>
                  </View>
                )}

                <Text style={{ fontFamily: theme.typography.fontFamilyHeading, fontSize: theme.typography.sizes.h3, color: theme.colors.textPrimary, marginBottom: theme.spacing.xs }}>
                  {plan.name}
                </Text>

                <View style={{ flexDirection: 'row', alignItems: 'baseline', marginBottom: theme.spacing.sm }}>
                  <Text style={{ fontFamily: theme.typography.fontFamilyHeading, fontSize: 28, color: theme.colors.textPrimary }}>
                    {plan.price}
                  </Text>
                  <Text style={{ fontFamily: theme.typography.fontFamilyBody, fontSize: 12, color: theme.colors.textSecondary, marginLeft: theme.spacing.xs }}>
                    {plan.period}
                  </Text>
                </View>

                {plan.savings && (
                  <Text style={{ color: theme.colors.success, fontFamily: theme.typography.fontFamilyBodySemibold, fontSize: 12, marginBottom: theme.spacing.sm }}>
                    {plan.savings}
                  </Text>
                )}

                <Text style={{ color: theme.colors.textSecondary, fontFamily: theme.typography.fontFamilyBody, fontSize: 12 }}>
                  {plan.boosts}
                </Text>
              </Pressable>
            ))}

            <Button
              label="Comenzar con plan recomendado"
              onPress={() => handleSubscribe('Trimestral')}
              style={{ marginTop: theme.spacing.md }}
            />
          </>
        ) : null}
      </ScrollView>
    </ScreenContainer>
  );
}
