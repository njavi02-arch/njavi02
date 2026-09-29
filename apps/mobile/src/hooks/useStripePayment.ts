import { useMutation } from 'react-query';
import { useAuthStore } from '../store/authStore';

interface PaymentRequest {
  planId: string;
  planName: string;
  amount: number;
  currency: string;
  duration: string;
}

interface PaymentResponse {
  success: boolean;
  subscriptionId?: string;
  clientSecret?: string;
  error?: string;
}

export function useStripePayment() {
  const session = useAuthStore((s) => s.session);

  const processPaymentMutation = useMutation(
    async (data: PaymentRequest): Promise<PaymentResponse> => {
      if (!session?.access_token) {
        throw new Error('Not authenticated');
      }

      const response = await fetch(`${process.env.REACT_APP_API_URL || 'http://localhost:3001'}/api/v2/payments/create-subscription`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${session.access_token}`,
        },
        body: JSON.stringify(data),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.message || 'Payment failed');
      }

      return response.json();
    }
  );

  const processPayment = async (data: PaymentRequest) => {
    return processPaymentMutation.mutateAsync(data);
  };

  return {
    processPayment,
    isLoading: processPaymentMutation.isLoading,
    error: processPaymentMutation.error,
  };
}
