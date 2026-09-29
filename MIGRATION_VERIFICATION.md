# Migration Verification Checklist

**Purpose:** Verify all database migrations were applied successfully  
**Date:** 2026-09-29  
**Status:** Ready to use  

---

## ✅ Verification Procedure

### Step 1: Check Phase 1 Migration (Database)

**Verify tables created:**
```sql
-- Run this in Supabase SQL Editor
SELECT tablename FROM pg_tables 
WHERE schemaname = 'public'
ORDER BY tablename;
```

**Expected tables:**
- ✅ auth.users (from Supabase Auth)
- ✅ profiles
- ✅ profile_photos
- ✅ user_preferences
- ✅ premium_subscriptions
- ✅ boosts
- ✅ photo_moderation
- ✅ discovery_cache
- ✅ reports
- ✅ blocks
- ✅ activity_log
- ✅ conversations
- ✅ messages
- ✅ user_coins
- ✅ coin_transactions

---

### Step 2: Check Privacy Migration

**Verify privacy tables:**
```sql
SELECT tablename FROM pg_tables 
WHERE tablename LIKE 'privacy_%' 
OR tablename LIKE 'auto_destroy_%'
OR tablename LIKE 'screenshot_%';
```

**Expected tables:**
- ✅ privacy_settings
- ✅ screenshot_attempts
- ✅ privacy_events
- ✅ auto_destroy_photos

---

### Step 3: Verify RLS is Enabled

**Check privacy_settings RLS:**
```sql
SELECT 
  schemaname, 
  tablename, 
  rowsecurity 
FROM pg_tables 
WHERE tablename = 'privacy_settings';
```

**Expected result:** `rowsecurity = true`

**Check all privacy tables:**
```sql
SELECT * FROM pg_tables 
WHERE tablename LIKE 'privacy_%' 
OR tablename LIKE 'auto_destroy_%'
OR tablename LIKE 'screenshot_%'
ORDER BY tablename;
```

**Expected result:** All show `rowsecurity = true`

---

### Step 4: Verify Indexes

**Check indexes created:**
```sql
SELECT 
  schemaname, 
  tablename, 
  indexname 
FROM pg_indexes 
WHERE tablename LIKE 'privacy_%'
OR tablename LIKE 'auto_destroy_%'
OR tablename LIKE 'screenshot_%'
ORDER BY tablename;
```

**Expected indexes:**
- `idx_privacy_settings_user_id`
- `idx_screenshot_attempts_user_id`
- `idx_screenshot_attempts_conversation_id`
- `idx_screenshot_attempts_detected_at`
- `idx_privacy_events_user_id`
- `idx_privacy_events_event_type`
- `idx_privacy_events_logged_at`
- `idx_auto_destroy_photos_photo_id`
- `idx_auto_destroy_photos_destroy_at`
- `idx_auto_destroy_photos_is_destroyed`

---

### Step 5: Verify RLS Policies

**Check privacy_settings policies:**
```sql
SELECT policyname, cmd FROM pg_policies 
WHERE tablename = 'privacy_settings'
ORDER BY policyname;
```

**Expected policies:**
- ✅ "Users can view own privacy settings" (SELECT)
- ✅ "Users can update own privacy settings" (UPDATE)
- ✅ "Users can insert own privacy settings" (INSERT)

**Check screenshot_attempts policies:**
```sql
SELECT policyname, cmd FROM pg_policies 
WHERE tablename = 'screenshot_attempts'
ORDER BY policyname;
```

**Expected policies:**
- ✅ "Users can view own screenshot attempts" (SELECT)
- ✅ "Users can insert own screenshot attempts" (INSERT)

**Check privacy_events policies:**
```sql
SELECT policyname, cmd FROM pg_policies 
WHERE tablename = 'privacy_events'
ORDER BY policyname;
```

**Expected policies:**
- ✅ "Users can view own privacy events" (SELECT)
- ✅ "System can insert privacy events" (INSERT)

---

### Step 6: Verify Data Integrity

**Test insert into privacy_settings:**
```sql
-- Assuming you have a test user UUID
INSERT INTO privacy_settings (
  user_id,
  anonymous_mode,
  prevent_screenshots,
  auto_delete_messages,
  auto_delete_photos,
  delete_photos_after_minutes,
  show_last_seen,
  show_typing_indicator,
  allow_forwarding
) VALUES (
  'YOUR_USER_UUID_HERE',
  false,
  true,
  false,
  false,
  1440,
  false,
  false,
  false
);

-- Verify insert
SELECT * FROM privacy_settings 
WHERE user_id = 'YOUR_USER_UUID_HERE';
```

**Test query permissions:**
```sql
-- This query should work (SELECT)
SELECT * FROM privacy_settings LIMIT 1;

-- This query should show your own data only
-- (Due to RLS policies)
SELECT * FROM privacy_settings;
```

---

### Step 7: Verify Triggers

**Check updated_at trigger:**
```sql
SELECT trigger_name, event_object_table
FROM information_schema.triggers
WHERE trigger_name LIKE 'privacy_%'
OR trigger_name LIKE 'auto_destroy_%';
```

**Expected trigger:**
- ✅ `privacy_settings_updated_at_trigger`

---

### Step 8: Verify Functions

**Check privacy functions:**
```sql
SELECT routine_name, routine_type
FROM information_schema.routines
WHERE routine_schema = 'public'
AND (routine_name LIKE 'auto_destroy%'
     OR routine_name LIKE 'cleanup%'
     OR routine_name LIKE 'update_privacy%');
```

**Expected functions:**
- ✅ `auto_destroy_expired_photos()`
- ✅ `cleanup_old_privacy_events()`
- ✅ `update_privacy_settings_timestamp()`

---

## 🔍 Quick Verification Summary

Run this all-in-one query to verify everything:

```sql
-- All checks at once
WITH table_check AS (
  SELECT 
    COUNT(*) as total_tables,
    COUNT(CASE WHEN tablename LIKE 'privacy_%' THEN 1 END) as privacy_tables,
    COUNT(CASE WHEN rowsecurity = true THEN 1 END) as rls_enabled
  FROM pg_tables 
  WHERE schemaname = 'public'
),
policy_check AS (
  SELECT COUNT(*) as total_policies
  FROM pg_policies
  WHERE tablename LIKE 'privacy_%'
),
index_check AS (
  SELECT COUNT(*) as total_indexes
  FROM pg_indexes
  WHERE tablename LIKE 'privacy_%'
)
SELECT 
  'Tables Created' as check_item,
  CASE WHEN (SELECT total_tables FROM table_check) >= 14 
    THEN '✅ PASS' ELSE '❌ FAIL' END as status,
  (SELECT total_tables FROM table_check)::text as details
UNION ALL
SELECT 
  'Privacy Tables',
  CASE WHEN (SELECT privacy_tables FROM table_check) >= 4 
    THEN '✅ PASS' ELSE '❌ FAIL' END,
  (SELECT privacy_tables FROM table_check)::text
UNION ALL
SELECT 
  'RLS Enabled',
  CASE WHEN (SELECT rls_enabled FROM table_check) >= 4 
    THEN '✅ PASS' ELSE '❌ FAIL' END,
  (SELECT rls_enabled FROM table_check)::text
UNION ALL
SELECT 
  'RLS Policies',
  CASE WHEN (SELECT total_policies FROM policy_check) >= 6 
    THEN '✅ PASS' ELSE '❌ FAIL' END,
  (SELECT total_policies FROM policy_check)::text
UNION ALL
SELECT 
  'Indexes Created',
  CASE WHEN (SELECT total_indexes FROM index_check) >= 8 
    THEN '✅ PASS' ELSE '❌ FAIL' END,
  (SELECT total_indexes FROM index_check)::text;
```

---

## 🎯 Expected Results

If all migrations passed, you should see:

```
✅ Tables Created
✅ Privacy Tables
✅ RLS Enabled
✅ RLS Policies
✅ Indexes Created
```

---

## ❌ Troubleshooting

### Issue: "privacy_settings table not found"

**Solution:**
```sql
-- Re-run migration
-- Copy PRIVACY_MIGRATION.sql content
-- Run in SQL Editor
```

### Issue: "RLS not enabled"

**Solution:**
```sql
ALTER TABLE privacy_settings ENABLE ROW LEVEL SECURITY;
ALTER TABLE screenshot_attempts ENABLE ROW LEVEL SECURITY;
ALTER TABLE privacy_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE auto_destroy_photos ENABLE ROW LEVEL SECURITY;
```

### Issue: "Policies missing"

**Solution:**
```sql
-- Re-apply policies from PRIVACY_MIGRATION.sql
-- Scroll to RLS Policies section
-- Copy and run each CREATE POLICY statement
```

### Issue: "Indexes not found"

**Solution:**
```sql
-- Re-create indexes from PRIVACY_MIGRATION.sql
-- Look for "CREATE INDEX IF NOT EXISTS" statements
```

---

## ✅ Post-Verification Steps

After all checks pass:

1. ✅ Database migration complete
2. ✅ Start backend servers:
   ```bash
   npm run server      # server-v2.js
   npm run realtime    # server-realtime.js
   npm run jobs        # privacy-jobs.js
   ```

3. ✅ Start mobile app:
   ```bash
   npm run mobile
   ```

4. ✅ Run E2E tests:
   ```bash
   node E2E_TESTING_SUITE.js --run-all
   ```

5. ✅ Deploy to production

---

## 📋 Verification Checklist

- [ ] All Phase 1 tables exist
- [ ] All Phase 2+ tables exist
- [ ] Privacy tables created (4 tables)
- [ ] RLS enabled on all privacy tables
- [ ] RLS policies created (6+ policies)
- [ ] Indexes created (8+ indexes)
- [ ] Triggers working (updated_at)
- [ ] Functions created (3+ functions)
- [ ] Data can be inserted successfully
- [ ] Data integrity maintained
- [ ] User isolation enforced

**Status when all checked:** ✅ PRODUCTION READY

---

**Last Updated:** 2026-09-29  
**Revision:** 1.0

