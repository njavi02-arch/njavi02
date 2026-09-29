# YUIZZ V2.0 - Database Migration Guide

**Date:** 2026-09-29  
**Status:** Ready to apply  
**File:** `SCHEMA_V2_MIGRATION.sql`

---

## 📋 What This Migration Does

### 1. Alters Existing Tables
- ✅ Adds V2.0 columns to `profiles`:
  - `hashtags TEXT[]` - User hashtag selection (1-10)
  - `profile_type VARCHAR(20)` - 'individual' or 'couple'
  - `couple_partner_id UUID` - Link to partner profile

- ✅ Adds V2.0 columns to `profile_photos`:
  - `photo_type VARCHAR(20)` - Type of photo (regular, private, locked)
  - `position INTEGER` - Photo position (1-3)

### 2. Creates 8 New V2.0 Tables

| Table | Purpose | Rows |
|-------|---------|------|
| `user_preferences` | User discovery filters | Per user |
| `premium_subscriptions` | Subscription tracking | Per user |
| `boosts` | Visibility boost log | Per activation |
| `photo_moderation` | AI moderation results | Per photo |
| `discovery_cache` | Performance optimization | Per user |
| `reports` | User reports & moderation | On demand |
| `blocks` | User blocking | On demand |
| `activity_log` | Audit trail | All actions |

### 3. Enables Security
- ✅ Row Level Security (RLS) on all tables
- ✅ User isolation policies
- ✅ Admin/system access controls
- ✅ Automatic timestamp management

### 4. Adds Performance Indexes
- ✅ B-tree indexes on foreign keys
- ✅ GIN indexes on array columns
- ✅ Partial indexes on frequently queried fields

---

## 🚀 How to Apply the Migration

### Option 1: Via Supabase Dashboard (Recommended)

1. **Log in to Supabase Dashboard**
   - Go to: https://supabase.com/dashboard
   - Select your project

2. **Open SQL Editor**
   - Navigate to: `SQL Editor` → `New Query`

3. **Copy & Paste the Migration**
   - Open: `SCHEMA_V2_MIGRATION.sql`
   - Copy entire content
   - Paste into SQL Editor
   - Click `Run`

4. **Verify Success**
   - Check for error messages (should see "Query OK")
   - Navigate to `Database` → `Tables`
   - Verify new tables appear:
     - `user_preferences`
     - `premium_subscriptions`
     - `boosts`
     - `photo_moderation`
     - `discovery_cache`
     - `reports`
     - `blocks`
     - `activity_log`

### Option 2: Via CLI (if installed)

```bash
# Install Supabase CLI
npm install -g supabase

# Link to your project
supabase link --project-ref YOUR_PROJECT_ID

# Apply migration
supabase db push SCHEMA_V2_MIGRATION.sql

# Verify
supabase db pull
```

### Option 3: Via psql/PostgreSQL Client

```bash
# Connect to your Supabase database
psql postgresql://[USER]:[PASSWORD]@[HOST]/postgres

# Run the migration
\i SCHEMA_V2_MIGRATION.sql

# Verify
\dt+  -- List all tables
```

---

## ✅ Verification Checklist

After applying the migration, run these queries to verify:

### Check New Tables
```sql
SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name IN (
  'user_preferences',
  'premium_subscriptions',
  'boosts',
  'photo_moderation',
  'discovery_cache',
  'reports',
  'blocks',
  'activity_log'
);
```

Expected: 8 rows returned

### Check RLS Policies
```sql
SELECT tablename, policyname 
FROM pg_policies 
WHERE tablename IN (
  'user_preferences',
  'premium_subscriptions',
  'boosts',
  'photo_moderation',
  'discovery_cache',
  'reports',
  'blocks',
  'activity_log'
)
ORDER BY tablename;
```

Expected: Multiple policies per table

### Check Indexes
```sql
SELECT schemaname, tablename, indexname 
FROM pg_indexes 
WHERE schemaname = 'public' 
AND tablename IN (
  'user_preferences',
  'premium_subscriptions',
  'boosts',
  'photo_moderation',
  'discovery_cache',
  'reports',
  'blocks',
  'activity_log'
);
```

Expected: Multiple indexes

### Check Columns Added
```sql
-- Check profiles table
\d profiles

-- Check profile_photos table
\d profile_photos
```

Expected columns:
- profiles: `hashtags`, `profile_type`, `couple_partner_id`
- profile_photos: `photo_type`, `position`

---

## 🔄 Rollback Plan

If something goes wrong, you can rollback using this SQL:

```sql
-- WARNING: This will DELETE all V2.0 data!
-- Only use if migration failed completely

-- Drop new tables
DROP TABLE IF EXISTS activity_log CASCADE;
DROP TABLE IF EXISTS blocks CASCADE;
DROP TABLE IF EXISTS reports CASCADE;
DROP TABLE IF EXISTS discovery_cache CASCADE;
DROP TABLE IF EXISTS photo_moderation CASCADE;
DROP TABLE IF EXISTS boosts CASCADE;
DROP TABLE IF EXISTS premium_subscriptions CASCADE;
DROP TABLE IF EXISTS user_preferences CASCADE;

-- Remove columns from existing tables
ALTER TABLE profiles 
DROP COLUMN IF EXISTS hashtags,
DROP COLUMN IF EXISTS profile_type,
DROP COLUMN IF EXISTS couple_partner_id;

ALTER TABLE profile_photos
DROP COLUMN IF EXISTS photo_type,
DROP COLUMN IF EXISTS position;

-- Done - database back to pre-V2.0 state
```

---

## 📊 Schema Diagram

```
┌─────────────────────┐
│ auth.users          │
│ (Supabase Auth)     │
└──────────┬──────────┘
           │
    ┌──────┴────────────────────────┐
    │                               │
┌───▼──────────────────┐   ┌───────▼─────────────────┐
│ profiles (updated)   │   │ user_preferences (NEW)  │
│ + hashtags           │   │ - min/max age           │
│ + profile_type       │   │ - gender preference     │
│ + couple_partner_id  │   │ - max distance          │
└───┬──────────────────┘   │ - preferred_hashtags    │
    │                      └─────────────────────────┘
    │
┌───▼────────────────────────┐
│ profile_photos (updated)   │
│ + photo_type               │
│ + position (1-3)           │
└───┬────────────────────────┘
    │
┌───▼──────────────────────┐
│ photo_moderation (NEW)   │
│ - nude_score             │
│ - explicit_content       │
│ - genitals_detected      │
│ - status                 │
└──────────────────────────┘

┌──────────────────────────────┐
│ premium_subscriptions (NEW)  │
│ - plan (monthly/quarterly..) │
│ - price & currency           │
│ - boosts_count/used          │
│ - stripe_ids                 │
│ - status                     │
└───┬─────────────────────────┘
    │
    ├─▶ ┌──────────────────┐
    │   │ boosts (NEW)     │
    │   │ - multiplier (3x)│
    │   │ - duration (30m) │
    │   │ - status         │
    │   └──────────────────┘
    │
    └─▶ ┌──────────────────────────┐
        │ discovery_cache (NEW)    │
        │ - cached_profile_ids     │
        │ - compatibility_scores   │
        │ - expires_at             │
        └──────────────────────────┘

┌──────────────────┐
│ reports (NEW)    │
│ - reporter_id    │
│ - reported_id    │
│ - reason         │
│ - status         │
└──────────────────┘

┌──────────────────┐
│ blocks (NEW)     │
│ - blocker_id     │
│ - blocked_id     │
│ - reason         │
└──────────────────┘

┌──────────────────┐
│ activity_log     │
│ (NEW)            │
│ - user_id        │
│ - action         │
│ - details        │
│ - ip_address     │
└──────────────────┘
```

---

## 📝 Post-Migration Tasks

After successful migration:

1. **Update Backend Environment**
   ```bash
   # Restart Node server to connect to new schema
   pkill -f "node server-v2.js"
   node server-v2.js
   ```

2. **Test V2.0 Endpoints**
   ```bash
   # Test preferences endpoint
   curl http://localhost:3001/api/v2/profiles/me/preferences \
     -H "Authorization: Bearer YOUR_JWT_TOKEN"
   
   # Test hashtags endpoint
   curl http://localhost:3001/api/v2/hashtags/all
   
   # Test premium endpoint
   curl http://localhost:3001/api/v2/subscriptions \
     -H "Authorization: Bearer YOUR_JWT_TOKEN"
   ```

3. **Populate Sample Data (Optional)**
   ```sql
   -- Create test preferences for existing users
   INSERT INTO user_preferences (user_id, min_age, max_age, gender_preference)
   SELECT id, 18, 65, ARRAY['female', 'male']::text[]
   FROM auth.users
   WHERE id NOT IN (SELECT user_id FROM user_preferences)
   LIMIT 10;
   ```

4. **Monitor Performance**
   - Check index usage
   - Monitor query performance
   - Set up alerts in Supabase

---

## 🆘 Troubleshooting

### Error: "Permission denied for schema public"
**Solution:** Ensure your Supabase role has proper permissions
```sql
GRANT USAGE ON SCHEMA public TO authenticated;
GRANT ALL ON ALL TABLES IN SCHEMA public TO authenticated;
```

### Error: "Relation already exists"
**Solution:** Migration was already applied or partially applied
```sql
-- Check what exists
SELECT tablename FROM pg_tables WHERE schemaname = 'public';
```

### Error: "Foreign key constraint failed"
**Solution:** Referenced table doesn't exist - run migration in order

### Slow queries after migration
**Solution:** Analyze and refresh indexes
```sql
ANALYZE; -- Recalculate table statistics
REINDEX DATABASE postgres; -- Rebuild all indexes
```

---

## 📈 Next Steps

After migration completes:

1. ✅ **Migrate Database** (You are here)
2. → **WebSocket Realtime** (2-3 hours)
   - Socket.io integration
   - Typing indicators
   - Online/offline status
   
3. → **Stripe Integration** (3-4 hours)
   - Payment processing
   - Subscription webhooks
   - Receipt management

4. → **Push Notifications** (2-3 hours)
   - Firebase Cloud Messaging
   - Expo Push integration
   - Notification routing

---

**Status:** Ready to deploy ✅  
**Duration:** ~15-30 minutes  
**Risk Level:** Low (RLS protects data, migration is additive)  
**Rollback Time:** ~5 minutes  

Questions? Check the V2_IMPLEMENTATION_STATUS.md file for more details.
