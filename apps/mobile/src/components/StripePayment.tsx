import React, { useState } from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  ActivityIndicator,
  Alert,
  StyleSheet,
} from 'react-native';
import { useStripePayment } from '../hooks/useStripePayment';

interface StripePaymentProps {
  planId: string;
  planName: string;
  price: number;
  currency: string;
  duration: string;
  onSuccess: (subscriptionId: string) => void;
  onError: (error: string) => void;
}

export function StripePayment({
  planId,
  planName,
  price,
  currency,
  duration,
  onSuccess,
  onError,
}: StripePaymentProps) {
  const [isProcessing, setIsProcessing] = useState(false);
  const { processPayment } = useStripePayment();

  const handlePayment = async () => {
    try {
      setIsProcessing(true);

      const response = await processPayment({
        planId,
        planName,
        amount: Math.round(price * 100), // Convert to cents
        currency,
        duration,
      });

      if (response.success) {
        Alert.alert('✅ Success', `Subscription activated: ${planName}`);
        onSuccess(response.subscriptionId);
      } else {
        Alert.alert('❌ Payment failed', response.error || 'Unknown error');
        onError(response.error || 'Payment processing failed');
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Payment failed';
      Alert.alert('❌ Error', errorMessage);
      onError(errorMessage);
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <View style={styles.container}>
      <TouchableOpacity
        style={[styles.button, isProcessing && styles.buttonDisabled]}
        onPress={handlePayment}
        disabled={isProcessing}
      >
        {isProcessing ? (
          <ActivityIndicator color="#fff" />
        ) : (
          <>
            <Text style={styles.buttonText}>Pay €{price.toFixed(2)}</Text>
            <Text style={styles.buttonSubtext}>{duration}</Text>
          </>
        )}
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    marginVertical: 12,
  },
  button: {
    backgroundColor: '#667eea',
    paddingVertical: 14,
    paddingHorizontal: 16,
    borderRadius: 8,
    alignItems: 'center',
  },
  buttonDisabled: {
    opacity: 0.6,
  },
  buttonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
  buttonSubtext: {
    color: '#ddd',
    fontSize: 12,
    marginTop: 4,
  },
});
