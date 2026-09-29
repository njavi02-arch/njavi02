// ============================================
// YUIZZ V2.0 - STRIPE PAYMENT INTEGRATION
// ============================================

import Stripe from 'stripe';
import dotenv from 'dotenv';

dotenv.config();

const stripe = new Stripe(process.env.STRIPE_SECRET_KEY, {
  apiVersion: '2024-04-10',
});

// ============================================
// SUBSCRIPTION PLANS
// ============================================

const SUBSCRIPTION_PLANS = {
  monthly: {
    stripePriceId: process.env.STRIPE_PRICE_MONTHLY,
    name: 'YUIZZ Premium Monthly',
    price: 7.99,
    currency: 'eur',
    interval: 'month',
    boosts: 1,
  },
  quarterly: {
    stripePriceId: process.env.STRIPE_PRICE_QUARTERLY,
    name: 'YUIZZ Premium Quarterly',
    price: 19.99,
    currency: 'eur',
    interval: 'quarter',
    boosts: 3,
  },
  yearly: {
    stripePriceId: process.env.STRIPE_PRICE_YEARLY,
    name: 'YUIZZ Premium Yearly',
    price: 59.99,
    currency: 'eur',
    interval: 'year',
    boosts: 12,
  },
};

// ============================================
// PAYMENT PROCESSING
// ============================================

// Create Stripe customer
export async function createOrGetStripeCustomer(userId, userEmail) {
  try {
    const customers = await stripe.customers.list({
      email: userEmail,
      limit: 1,
    });

    if (customers.data.length > 0) {
      return customers.data[0];
    }

    const customer = await stripe.customers.create({
      email: userEmail,
      metadata: {
        userId,
      },
    });

    return customer;
  } catch (error) {
    console.error('❌ Error creating/getting Stripe customer:', error);
    throw error;
  }
}

// Create subscription
export async function createSubscription(customerId, planKey, userId) {
  try {
    const plan = SUBSCRIPTION_PLANS[planKey];

    if (!plan) {
      throw new Error(`Invalid plan: ${planKey}`);
    }

    if (!plan.stripePriceId) {
      throw new Error(`Stripe price not configured for plan: ${planKey}`);
    }

    const subscription = await stripe.subscriptions.create({
      customer: customerId,
      items: [
        {
          price: plan.stripePriceId,
        },
      ],
      metadata: {
        userId,
        plan: planKey,
        boosts: plan.boosts,
      },
      payment_settings: {
        payment_method_types: ['card'],
      },
      expand: ['latest_invoice.payment_intent'],
    });

    console.log(`✅ Subscription created: ${subscription.id}`);

    return {
      subscriptionId: subscription.id,
      clientSecret: subscription.latest_invoice?.payment_intent?.client_secret,
      status: subscription.status,
      currentPeriodEnd: subscription.current_period_end,
    };
  } catch (error) {
    console.error('❌ Error creating subscription:', error);
    throw error;
  }
}

// Cancel subscription
export async function cancelSubscription(subscriptionId, immediate = false) {
  try {
    const subscription = await stripe.subscriptions.update(subscriptionId, {
      cancel_at_period_end: !immediate,
    });

    console.log(`✅ Subscription ${immediate ? 'cancelled immediately' : 'scheduled for cancellation'}: ${subscriptionId}`);

    return {
      subscriptionId: subscription.id,
      status: subscription.status,
      canceledAt: subscription.canceled_at,
      cancelAtPeriodEnd: subscription.cancel_at_period_end,
    };
  } catch (error) {
    console.error('❌ Error cancelling subscription:', error);
    throw error;
  }
}

// Get subscription details
export async function getSubscriptionDetails(subscriptionId) {
  try {
    const subscription = await stripe.subscriptions.retrieve(subscriptionId);

    return {
      id: subscription.id,
      customerId: subscription.customer,
      status: subscription.status,
      currentPeriodStart: subscription.current_period_start,
      currentPeriodEnd: subscription.current_period_end,
      canceledAt: subscription.canceled_at,
      cancelAtPeriodEnd: subscription.cancel_at_period_end,
      plan: subscription.metadata.plan,
      boosts: subscription.metadata.boosts,
    };
  } catch (error) {
    console.error('❌ Error retrieving subscription:', error);
    throw error;
  }
}

// List invoices for customer
export async function getCustomerInvoices(customerId) {
  try {
    const invoices = await stripe.invoices.list({
      customer: customerId,
      limit: 10,
    });

    return invoices.data.map((invoice) => ({
      id: invoice.id,
      number: invoice.number,
      status: invoice.status,
      amount: invoice.total,
      currency: invoice.currency,
      pdfUrl: invoice.pdf,
      createdAt: invoice.created,
      paidAt: invoice.paid_date,
    }));
  } catch (error) {
    console.error('❌ Error retrieving invoices:', error);
    throw error;
  }
}

// ============================================
// REFUND PROCESSING
// ============================================

export async function processRefund(paymentIntentId, amount = null) {
  try {
    const refund = await stripe.refunds.create({
      payment_intent: paymentIntentId,
      amount: amount ? Math.round(amount * 100) : undefined,
    });

    console.log(`✅ Refund processed: ${refund.id}`);

    return {
      refundId: refund.id,
      amount: refund.amount / 100,
      currency: refund.currency,
      status: refund.status,
    };
  } catch (error) {
    console.error('❌ Error processing refund:', error);
    throw error;
  }
}

// ============================================
// WEBHOOK HANDLERS
// ============================================

export async function handleStripeWebhook(event) {
  try {
    switch (event.type) {
      case 'customer.subscription.updated':
        return handleSubscriptionUpdated(event.data.object);

      case 'customer.subscription.deleted':
        return handleSubscriptionCancelled(event.data.object);

      case 'invoice.payment_succeeded':
        return handleInvoicePaid(event.data.object);

      case 'invoice.payment_failed':
        return handleInvoiceFailed(event.data.object);

      case 'charge.refunded':
        return handleRefund(event.data.object);

      default:
        console.log(`📝 Unhandled webhook event: ${event.type}`);
    }
  } catch (error) {
    console.error('❌ Error handling webhook:', error);
    throw error;
  }
}

async function handleSubscriptionUpdated(subscription) {
  console.log(`📋 Subscription updated: ${subscription.id}`);
  console.log(`   Status: ${subscription.status}`);
  console.log(`   Current period ends: ${new Date(subscription.current_period_end * 1000)}`);
  // TODO: Update database with subscription status
}

async function handleSubscriptionCancelled(subscription) {
  console.log(`❌ Subscription cancelled: ${subscription.id}`);
  // TODO: Update database, notify user
}

async function handleInvoicePaid(invoice) {
  console.log(`✅ Invoice paid: ${invoice.id}`);
  console.log(`   Amount: ${invoice.total / 100} ${invoice.currency.toUpperCase()}`);
  // TODO: Log payment, update subscription status
}

async function handleInvoiceFailed(invoice) {
  console.log(`❌ Invoice payment failed: ${invoice.id}`);
  console.log(`   Reason: ${invoice.last_finalization_error?.message}`);
  // TODO: Notify user, log payment failure
}

async function handleRefund(charge) {
  console.log(`💰 Refund processed for charge: ${charge.id}`);
  console.log(`   Amount: ${charge.amount / 100} ${charge.currency.toUpperCase()}`);
  // TODO: Log refund in database
}

// ============================================
// EXPORTS
// ============================================

export { SUBSCRIPTION_PLANS, stripe };
