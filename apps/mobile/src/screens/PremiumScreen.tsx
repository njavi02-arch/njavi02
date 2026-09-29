import React, { useState } from 'react';
import {
  View,
  Text,
  ScrollView,
  StyleSheet,
  SafeAreaView,
  Alert,
} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { StripePayment } from '../components/StripePayment';
import { usePremiumSubscription } from '../hooks/useV2DiscoverFeed';

export function PremiumScreen() {
  const [selectedPlan, setSelectedPlan] = useState('quarterly');
  const [showPayment, setShowPayment] = useState(false);
  const { data: subscription } = usePremiumSubscription();

  const plans = [
    {
      id: 'monthly',
      name: 'Mensual',
      price: 7.99,
      period: '/mes',
      boosts: 1,
      savings: null,
      popular: false,
    },
    {
      id: 'quarterly',
      name: 'Trimestral',
      price: 19.99,
      period: '/3 meses (€6.66/mes)',
      boosts: 3,
      savings: '17%',
      popular: true,
    },
    {
      id: 'yearly',
      name: 'Anual',
      price: 59.99,
      period: '/año (€5.00/mes)',
      boosts: 12,
      savings: '38%',
      popular: false,
    },
  ];

  const handlePaymentSuccess = (subscriptionId) => {
    setShowPayment(false);
    Alert.alert(
      '✅ ¡Éxito!',
      'Tu suscripción Premium está activada. ¡Disfruta de todas las funciones!'
    );
  };

  const handlePaymentError = (error) => {
    Alert.alert('❌ Error', error);
  };

  const currentPlan = plans.find((p) => p.id === selectedPlan);

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView showsVerticalScrollIndicator={false}>
        {/* Header */}
        <LinearGradient
          colors={['#667eea', '#764ba2']}
          style={styles.header}
        >
          <Text style={styles.headerEmoji}>✨</Text>
          <Text style={styles.headerTitle}>YUIZZ Premium</Text>
          <Text style={styles.headerSubtitle}>
            Desbloquea todas las funciones V2.0
          </Text>
        </LinearGradient>

        {/* Current Subscription Status */}
        {subscription?.status === 'active' && (
          <View style={styles.activeSubscription}>
            <Text style={styles.activeText}>
              ✅ Suscripción activa hasta {new Date(subscription.expires_at).toLocaleDateString()}
            </Text>
            <Text style={styles.boostsText}>
              Boosts disponibles: {subscription.boosts_count - subscription.boosts_used}/{subscription.boosts_count}
            </Text>
          </View>
        )}

        {/* Plans */}
        <View style={styles.plansContainer}>
          {plans.map((plan) => (
            <View
              key={plan.id}
              style={[
                styles.planCard,
                selectedPlan === plan.id && styles.planCardSelected,
                plan.popular && styles.planCardPopular,
              ]}
            >
              {plan.popular && (
                <Text style={styles.popularBadge}>⭐ POPULAR</Text>
              )}

              <Text style={styles.planName}>📅 {plan.name}</Text>
              <Text style={styles.planPrice}>€{plan.price.toFixed(2)}</Text>
              <Text style={styles.planPeriod}>{plan.period}</Text>
              <Text style={styles.planBoosts}>🚀 {plan.boosts} boosts</Text>

              {plan.savings && (
                <Text style={styles.planSavings}>Ahorras {plan.savings}</Text>
              )}
            </View>
          ))}
        </View>

        {/* Payment Section */}
        {showPayment && currentPlan && (
          <View style={styles.paymentSection}>
            <Text style={styles.paymentTitle}>Confirmar pago</Text>
            <StripePayment
              planId={currentPlan.id}
              planName={currentPlan.name}
              price={currentPlan.price}
              currency="eur"
              duration={currentPlan.period}
              onSuccess={handlePaymentSuccess}
              onError={handlePaymentError}
            />
          </View>
        )}

        {/* Features List */}
        <View style={styles.featuresContainer}>
          <Text style={styles.featuresTitle}>Incluye en tu plan</Text>

          <View style={styles.featureItem}>
            <Text style={styles.featureIcon}>❤️</Text>
            <Text style={styles.featureText}>Likes ilimitados</Text>
          </View>

          <View style={styles.featureItem}>
            <Text style={styles.featureIcon}>⭐</Text>
            <Text style={styles.featureText}>5 SuperLikes diarios</Text>
          </View>

          <View style={styles.featureItem}>
            <Text style={styles.featureIcon}>🔍</Text>
            <Text style={styles.featureText}>Filtros avanzados</Text>
          </View>

          <View style={styles.featureItem}>
            <Text style={styles.featureIcon}>👁️</Text>
            <Text style={styles.featureText}>Ver quién te vio</Text>
          </View>

          <View style={styles.featureItem}>
            <Text style={styles.featureIcon}>🚀</Text>
            <Text style={styles.featureText}>Boosts de visibilidad 3x</Text>
          </View>

          <View style={styles.featureItem}>
            <Text style={styles.featureIcon}>💬</Text>
            <Text style={styles.featureText}>Mensajes prioritarios</Text>
          </View>

          <View style={styles.featureItem}>
            <Text style={styles.featureIcon}>🏷️</Text>
            <Text style={styles.featureText}>Filtros por hashtags</Text>
          </View>

          <View style={styles.featureItem}>
            <Text style={styles.featureIcon}>📊</Text>
            <Text style={styles.featureText}>Compatibilidad en tiempo real</Text>
          </View>
        </View>

        {/* Action Button */}
        {!showPayment && (
          <View style={styles.actionButtonContainer}>
            <LinearGradient
              colors={['#667eea', '#764ba2']}
              style={styles.actionButton}
            >
              <Text
                style={styles.actionButtonText}
                onPress={() => setShowPayment(true)}
              >
                Comenzar suscripción
              </Text>
            </LinearGradient>
          </View>
        )}

        {/* Footer */}
        <Text style={styles.footerText}>
          Cancela en cualquier momento. Sin compromisos.
        </Text>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  header: {
    paddingVertical: 30,
    paddingHorizontal: 20,
    alignItems: 'center',
  },
  headerEmoji: {
    fontSize: 48,
    marginBottom: 12,
  },
  headerTitle: {
    fontSize: 28,
    fontWeight: '700',
    color: '#fff',
    marginBottom: 6,
  },
  headerSubtitle: {
    fontSize: 14,
    color: '#e0e0e0',
  },
  activeSubscription: {
    backgroundColor: '#e8f5e9',
    marginHorizontal: 16,
    marginTop: 16,
    padding: 12,
    borderRadius: 8,
    borderLeftWidth: 4,
    borderLeftColor: '#4caf50',
  },
  activeText: {
    fontSize: 14,
    fontWeight: '600',
    color: '#2e7d32',
  },
  boostsText: {
    fontSize: 12,
    color: '#558b2f',
    marginTop: 4,
  },
  plansContainer: {
    paddingHorizontal: 16,
    marginTop: 20,
  },
  planCard: {
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
    borderWidth: 2,
    borderColor: '#eee',
  },
  planCardSelected: {
    borderColor: '#667eea',
    backgroundColor: '#f8f9ff',
  },
  planCardPopular: {
    borderColor: '#667eea',
    backgroundColor: '#f8f9ff',
    position: 'relative',
  },
  popularBadge: {
    position: 'absolute',
    top: -12,
    left: 16,
    backgroundColor: '#667eea',
    color: '#fff',
    paddingHorizontal: 12,
    paddingVertical: 4,
    borderRadius: 12,
    fontSize: 11,
    fontWeight: '600',
  },
  planName: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
    marginBottom: 8,
  },
  planPrice: {
    fontSize: 28,
    fontWeight: '700',
    color: '#667eea',
    marginBottom: 4,
  },
  planPeriod: {
    fontSize: 12,
    color: '#999',
    marginBottom: 8,
  },
  planBoosts: {
    fontSize: 14,
    color: '#666',
    marginBottom: 8,
  },
  planSavings: {
    fontSize: 12,
    color: '#4caf50',
    fontWeight: '600',
  },
  paymentSection: {
    backgroundColor: '#fff',
    marginHorizontal: 16,
    marginTop: 16,
    padding: 16,
    borderRadius: 12,
  },
  paymentTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
    marginBottom: 12,
  },
  featuresContainer: {
    backgroundColor: '#fff',
    marginHorizontal: 16,
    marginTop: 20,
    padding: 16,
    borderRadius: 12,
    marginBottom: 20,
  },
  featuresTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
    marginBottom: 12,
  },
  featureItem: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 8,
    borderBottomWidth: 1,
    borderBottomColor: '#f0f0f0',
  },
  featureIcon: {
    fontSize: 18,
    marginRight: 12,
  },
  featureText: {
    fontSize: 14,
    color: '#666',
    flex: 1,
  },
  actionButtonContainer: {
    paddingHorizontal: 16,
    marginBottom: 16,
  },
  actionButton: {
    paddingVertical: 14,
    borderRadius: 8,
    alignItems: 'center',
  },
  actionButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
  footerText: {
    textAlign: 'center',
    fontSize: 12,
    color: '#999',
    marginBottom: 20,
  },
});
