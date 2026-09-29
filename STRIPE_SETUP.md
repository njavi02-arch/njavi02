# YUIZZ V2.0 - Stripe Integration Guide

**Date:** 2026-09-29  
**Status:** Ready to integrate  
**Phase:** 3 (Payment Processing)

---

## 📋 What This Integration Does

### 1. Subscription Management
- ✅ Create premium subscriptions (Monthly, Quarterly, Yearly)
- ✅ Cancel subscriptions at end of period or immediately
- ✅ Track subscription status and expiry
- ✅ Manage boosts per subscription tier

### 2. Payment Processing
- ✅ Accept card payments via Stripe
- ✅ Create payment intents for secure transactions
- ✅ Handle 3D Secure authentication
- ✅ Store subscription IDs and customer IDs

### 3. Webhook Handling
- ✅ Subscription created/updated/deleted events
- ✅ Invoice payment succeeded/failed events
- ✅ Refund processed events
- ✅ Automatic status updates

### 4. Invoice & Receipt Management
- ✅ List customer invoices
- ✅ Generate PDF receipts
- ✅ Track payment history

### 5. Refund Processing
- ✅ Full and partial refunds
- ✅ Refund status tracking
- ✅ Automatic expiry handling

---

## 🚀 How to Set Up Stripe

### Step 1: Create Stripe Account

1. Go to https://stripe.com
2. Click "Sign up"
3. Create account with business email
4. Verify email and complete setup

### Step 2: Get API Keys

1. Go to Stripe Dashboard
2. Click "Developers" → "API keys"
3. Copy these keys:
   - **Public Key** (starts with `pk_`)
   - **Secret Key** (starts with `sk_`)

### Step 3: Create Product & Prices

1. Go to "Products" in Stripe Dashboard
2. Create new product: "YUIZZ Premium"
3. Add three prices:

```
Price 1: Monthly
- Amount: €7.99
- Billing Period: Monthly
- Price ID: price_xxx_monthly

Price 2: Quarterly
- Amount: €19.99
- Billing Period: Quarterly
- Price ID: price_xxx_quarterly

Price 3: Yearly
- Amount: €59.99
- Billing Period: Yearly
- Price ID: price_xxx_yearly
```

### Step 4: Configure Environment

1. Create/update `.env` in project root:

```bash
# Stripe Configuration
STRIPE_PUBLIC_KEY=pk_your_public_key_here
STRIPE_SECRET_KEY=sk_your_secret_key_here
STRIPE_PRICE_MONTHLY=price_xxx_monthly
STRIPE_PRICE_QUARTERLY=price_xxx_quarterly
STRIPE_PRICE_YEARLY=price_xxx_yearly
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret

# Existing config
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your_anon_key
REACT_APP_API_URL=http://localhost:3001
REACT_APP_REALTIME_URL=http://localhost:3002
```

### Step 5: Set Up Webhooks

1. Go to Stripe Dashboard → Developers → Webhooks
2. Click "Add endpoint"
3. Configure webhook:
   - **URL:** `http://your-domain/api/v2/webhooks/stripe`
   - **Version:** Latest API version
   - **Events to listen to:**
     - `customer.subscription.updated`
     - `customer.subscription.deleted`
     - `invoice.payment_succeeded`
     - `invoice.payment_failed`
     - `charge.refunded`

4. Copy Webhook Signing Secret to `.env` as `STRIPE_WEBHOOK_SECRET`

### Step 6: Enable Stripe in Backend

Install Stripe package:

```bash
npm install stripe
```

### Step 7: Frontend Configuration

Update mobile app environment:

```bash
# apps/mobile/.env
STRIPE_PUBLIC_KEY=pk_your_public_key_here
REACT_APP_API_URL=http://localhost:3001
```

---

## 💳 Payment Flow

### 1. User Selects Plan
```
┌─────────────────┐
│ Premium Screen  │
│  - Monthly      │
│  - Quarterly    │ ← User selects
│  - Yearly       │
└────────┬────────┘
         │
         ▼
┌─────────────────────────┐
│ Stripe Payment Modal    │
│  - Card details        │
│  - Confirmation        │
└────────┬────────────────┘
```

### 2. Create Payment Intent
```
Frontend              Backend              Stripe
   │                    │                    │
   ├─POST /create-sub──>│                    │
   │                    ├─Create Intent─────>│
   │                    │<─client_secret────┤
   │<─client_secret─────┤                    │
   │                    │                    │
```

### 3. Confirm Payment
```
Frontend              Backend              Stripe
   │                    │                    │
   ├─POST /confirm─────>│                    │
   │  (card token)      ├─Confirm Intent───>│
   │                    │<─Success/Fail─────┤
   │<─Subscription ID───┤                    │
   │                    │                    │
```

### 4. Save to Database
```
Backend              Supabase
   │                   │
   ├─INSERT sub───────>│
   │  - user_id        │
   │  - plan           │
   │  - stripe_id      │
   │  - status: active │
   │<─Subscription────┤
```

---

## 🔐 Security Measures

### 1. PCI Compliance
- ✅ Never store card details
- ✅ Use Stripe.js for tokenization
- ✅ Client secret verification
- ✅ 3D Secure fallback

### 2. Database Security
- ✅ Stripe IDs stored (never card details)
- ✅ Row Level Security (RLS) on premium_subscriptions
- ✅ User isolation policies
- ✅ Encrypted payment history

### 3. API Security
- ✅ JWT token verification on all endpoints
- ✅ HTTPS only in production
- ✅ Webhook signature verification
- ✅ Rate limiting on payment endpoints

### 4. Error Handling
- ✅ Never expose Stripe errors to frontend
- ✅ Log all payment failures
- ✅ Automatic retry logic
- ✅ User-friendly error messages

---

## 🧪 Testing

### Test Card Numbers

Use these in Stripe Test mode:

```
Visa Success:           4242 4242 4242 4242
Visa 3D Secure:         4000 0025 0000 3155
Card Declined:          4000 0000 0000 0002
Insufficient Funds:     4000 0000 0000 9995
Lost Card:              4000 0000 0000 9979
Stolen Card:            4000 0000 0000 9995
Expired Card:           4000 0000 0000 0069
Incorrect CVC:          4000 0000 0000 0010
```

All test cards use:
- **Expiry:** Any future date
- **CVC:** Any 3-4 digits

### Test Webhooks Locally

```bash
# Install Stripe CLI
brew install stripe/stripe-cli/stripe

# Login to Stripe account
stripe login

# Forward webhooks to local endpoint
stripe listen --forward-to localhost:3001/api/v2/webhooks/stripe

# Copy webhook signing secret to .env
# STRIPE_WEBHOOK_SECRET=whsec_xxxxx
```

### Test Payment Flow

1. Start backend: `node server-v2.js`
2. Start mobile app: `npm run ios` or `npm run android`
3. Navigate to Premium screen
4. Select plan
5. Enter test card number
6. Verify subscription created in database

```bash
# Check subscription in Supabase
SELECT * FROM premium_subscriptions 
WHERE user_id = 'your_test_user_id'
ORDER BY created_at DESC;
```

---

## 📊 Subscription States

```
┌─────────────────────────────────────────┐
│        Subscription Lifecycle            │
└──────────────────────┬──────────────────┘
                       │
                       ▼
                    active ────────┐
                       │           │
        ┌──────────────┘│           │
        │               │ expires   │
        │               ▼           │
        │            expired ◄──────┘
        │               │
        │ cancel_at_    │
        │ period_end    │
        │               │
        ▼               ▼
     cancelled ◄──── cancelled_at
        │              │
        └──────┬───────┘
               │
               ▼
          Refund processed
          or Dispute filed
```

---

## 🛠️ API Endpoints

### POST /api/v2/payments/create-subscription
Create a new subscription

**Request:**
```json
{
  "planId": "monthly" | "quarterly" | "yearly"
}
```

**Response:**
```json
{
  "success": true,
  "subscriptionId": "sub_1234567890",
  "plan": "quarterly",
  "boosts": 3,
  "expiresAt": "2026-12-29T00:00:00Z"
}
```

### GET /api/v2/payments/subscriptions
Get user's active subscriptions

**Response:**
```json
{
  "subscriptions": [
    {
      "id": "sub_1234567890",
      "plan": "quarterly",
      "status": "active",
      "price": 19.99,
      "boosts_count": 3,
      "boosts_used": 1,
      "expires_at": "2026-12-29T00:00:00Z"
    }
  ]
}
```

### POST /api/v2/payments/cancel-subscription
Cancel a subscription

**Request:**
```json
{
  "subscriptionId": "sub_1234567890"
}
```

**Response:**
```json
{
  "success": true,
  "subscription": {
    "id": "sub_1234567890",
    "status": "cancelled",
    "cancelledAt": "2026-09-29T10:00:00Z"
  }
}
```

### GET /api/v2/payments/invoices
Get user's payment invoices

**Response:**
```json
{
  "invoices": [
    {
      "id": "invoice_1234567890",
      "amount": 19.99,
      "currency": "eur",
      "status": "paid",
      "createdAt": "2026-06-29T00:00:00Z",
      "pdfUrl": "/api/v2/payments/invoices/inv_xxx/pdf"
    }
  ]
}
```

### POST /api/v2/boosts/activate
Activate a visibility boost

**Response:**
```json
{
  "success": true,
  "boost": {
    "id": "boost_1234567890",
    "expiresAt": "2026-09-29T10:30:00Z",
    "multiplier": 3.0,
    "durationMinutes": 30
  }
}
```

---

## 🔄 Post-Setup Tasks

After Stripe integration:

1. **Test Payment Flow**
   - Create subscription with test card
   - Verify database record
   - Check invoice generation

2. **Configure Webhooks**
   - Test webhook delivery
   - Verify event processing
   - Monitor webhook logs

3. **Set Up Monitoring**
   - Create Stripe dashboard alerts
   - Log failed payments
   - Monitor refund rate

4. **User Communication**
   - Send welcome email after purchase
   - Send receipt/invoice
   - Notify on subscription renewal
   - Warn before expiry

5. **Next Phase: Push Notifications**
   - Firebase Cloud Messaging setup
   - Expo Push API integration
   - Notification templates
   - User preference management

---

## 🆘 Troubleshooting

### Error: "Missing Stripe API Key"
**Solution:** Ensure `STRIPE_SECRET_KEY` is set in `.env`

### Error: "Invalid price ID"
**Solution:** Verify price IDs match Stripe dashboard:
```bash
stripe prices list --product=prod_xxxxx
```

### Error: "Webhook signature verification failed"
**Solution:** Ensure webhook secret matches:
```bash
stripe listen --print-secret
# Copy output to STRIPE_WEBHOOK_SECRET
```

### Error: "Payment intent expired"
**Solution:** Payment intent valid for 24 hours, create new if needed

### Card Declined in Testing
**Solution:** Use correct test card number and future expiry date

### Subscription not creating in database
**Solution:** Check:
1. JWT token validity
2. Database RLS policies
3. Stripe API response
4. Backend logs

---

## 📈 Next Steps

✅ Phase 1: Database Migration (COMPLETE)
✅ Phase 2: WebSocket Realtime (COMPLETE)
✅ Phase 3: Stripe Integration (IN PROGRESS)
→ Phase 4: Push Notifications (2-3 hours)

---

**Status:** Ready to test  
**Duration:** 3-4 hours  
**Risk Level:** Medium (payment handling, PCI compliance)  

Questions? Check the README.md or contact support.
