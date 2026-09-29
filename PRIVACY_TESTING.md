# Privacy Features Testing Guide

**Date:** 2026-09-29  
**Status:** Ready for QA  

---

## 🧪 Test Cases

### Test 1: Screenshot Detection
**Objective:** Verify screenshot detection and notification

**Steps:**
1. User A enables `preventScreenshots` in PrivacySettingsScreen
2. User A starts conversation with User B
3. User B attempts screenshot on device
4. Verify:
   - ✓ User A receives alert: "⚠️ Screenshot Detectado"
   - ✓ `expo-screen-capture` listener triggered
   - ✓ Screenshot attempt logged to database
   - ✓ Event sent to backend `/api/v2/privacy/screenshot-attempt`
   - ✓ User B receives notification via socket.io: `privacy:screenshot_detected`

**Expected Result:** Both users notified, event logged ✅

---

### Test 2: Anonymous Mode
**Objective:** Verify user appears anonymous in conversations

**Steps:**
1. User A enables `anonymousMode` in PrivacySettingsScreen
2. User B opens conversation with User A
3. Verify:
   - ✓ User A's name NOT visible (shows "👤 Anónimo")
   - ✓ User A's profile photo NOT visible
   - ✓ In Discovery: User A shows "👤 Anónimo" badge
   - ✓ `showLastSeen` hides last seen timestamp
   - ✓ `showTypingIndicator` hides typing status

**Expected Result:** User A appears completely anonymous ✅

---

### Test 3: Photo Auto-Destruction
**Objective:** Verify photos auto-destroy after timer

**Steps:**
1. User A enables `autoDeletePhotos` with `deletePhotosAfterMinutes: 5`
2. User A sends photo to User B
3. Verify:
   - ✓ Photo stored with `destroy_at` timestamp
   - ✓ Entry created in `auto_destroy_photos` table
   - ✓ Photo visible for 5 minutes
   - ✓ After 5 minutes, `auto_destroy_expired_photos()` runs
   - ✓ Photo marked as `is_destroyed: true`
   - ✓ Event logged in `privacy_events`

**Wait Time:** 5 minutes (can test with shorter interval in dev)

**Expected Result:** Photo auto-destroyed after timer ✅

---

### Test 4: Photo Pinning (Fixed in Chat)
**Objective:** Verify photos stay when auto-destroy disabled

**Steps:**
1. User A disables `autoDeletePhotos`
2. User A sends photo to User B
3. Verify:
   - ✓ Photo NOT stored in `auto_destroy_photos` table
   - ✓ Photo stays in conversation permanently
   - ✓ Can be viewed/shared indefinitely

**Expected Result:** Photo stays in chat ✅

---

### Test 5: Message Auto-Deletion
**Objective:** Verify messages auto-delete after 24 hours

**Steps:**
1. User A enables `autoDeleteMessages`
2. User A sends message
3. Verify:
   - ✓ Message stored in `messages` table
   - ✓ Privacy job runs (scheduled daily or triggered)
   - ✓ Message older than 24 hours is deleted
   - ✓ Event logged

**Wait Time:** 24 hours (can simulate in dev)

**Expected Result:** Message auto-deleted ✅

---

### Test 6: Conversation Deletion
**Objective:** Verify conversation delete and notification

**Steps:**
1. User A opens conversation
2. Opens PrivacySettingsScreen
3. Clicks "🗑️ Eliminar Conversación"
4. Confirms deletion
5. Verify:
   - ✓ Confirmation alert shown
   - ✓ Conversation marked as deleted for User A
   - ✓ User B receives notification via socket.io: `privacy:conversation_deleted_notice`
   - ✓ Event logged in `privacy_events`
   - ✓ Conversation removed from User A's list

**Expected Result:** Conversation deleted, User B notified ✅

---

### Test 7: Photo Forwarding Control
**Objective:** Verify photo sharing can be disabled

**Steps:**
1. User A disables `allowForwarding`
2. User B tries to forward photo from User A
3. Verify:
   - ✓ Forwarding button disabled/hidden
   - ✓ Error message shown
   - ✓ Setting enforced on backend

**Expected Result:** Photo cannot be forwarded ✅

---

### Test 8: Privacy Settings Persistence
**Objective:** Verify settings saved to database

**Steps:**
1. User A changes multiple privacy settings
2. User A closes app
3. User A reopens app
4. Verify:
   - ✓ Settings restored from database
   - ✓ No settings reverted to default
   - ✓ Toggles show correct state

**Expected Result:** Settings persisted ✅

---

### Test 9: Audit Trail Logging
**Objective:** Verify privacy events logged

**Steps:**
1. User A performs privacy actions (screenshot, delete conversation, etc.)
2. Query `privacy_events` table
3. Verify:
   - ✓ All events logged with timestamp
   - ✓ Metadata stored correctly
   - ✓ Events older than 30 days cleaned up
   - ✓ User isolation in queries

**Expected Result:** Complete audit trail maintained ✅

---

### Test 10: Socket.io Events
**Objective:** Verify real-time notifications

**Steps:**
1. User A and B connected via socket.io
2. User A triggers privacy event (screenshot attempt)
3. Verify:
   - ✓ Socket.io event emitted: `privacy:screenshot_detected`
   - ✓ User B receives event in real-time
   - ✓ Event contains correct data (userId, attemptNumber, timestamp)
   - ✓ Conversation deletion emits: `privacy:conversation_deleted_notice`

**Expected Result:** All events received in real-time ✅

---

## 📋 Database Verification

### Query 1: Privacy Settings
```sql
SELECT * FROM privacy_settings WHERE user_id = 'test_user_id';
-- Should show all privacy settings
```

### Query 2: Screenshot Attempts
```sql
SELECT * FROM screenshot_attempts 
WHERE user_id = 'test_user_id' 
ORDER BY detected_at DESC;
-- Should show all screenshot attempts with timestamps
```

### Query 3: Privacy Events
```sql
SELECT * FROM privacy_events 
WHERE user_id = 'test_user_id'
ORDER BY logged_at DESC LIMIT 50;
-- Should show privacy audit trail
```

### Query 4: Auto-Destroy Photos
```sql
SELECT * FROM auto_destroy_photos 
WHERE is_destroyed = false;
-- Should show pending destruction
```

### Query 5: RLS Policies
```sql
SELECT * FROM pg_policies 
WHERE tablename IN (
  'privacy_settings', 
  'screenshot_attempts', 
  'privacy_events',
  'auto_destroy_photos'
);
-- Should show RLS policies enabled
```

---

## 🚀 Running Tests

### Manual Testing
1. Start backend: `npm run dev` (server-v2.js)
2. Start realtime: `node server-realtime.js`
3. Start jobs: `node privacy-jobs.js --start`
4. Start mobile app: `npm run mobile`
5. Run through test cases above

### Automated Testing (Future)
```bash
# Run privacy test suite
npm run test:privacy

# Run privacy E2E tests
npm run test:e2e:privacy
```

---

## ✅ Checklist Before Production

- [ ] All 10 test cases pass
- [ ] Database queries verified
- [ ] Socket.io events working
- [ ] Privacy jobs running
- [ ] Screenshot detection working
- [ ] Anonymous mode working
- [ ] Photo auto-destruction working
- [ ] Message auto-deletion working
- [ ] Conversation deletion working
- [ ] Audit trail complete
- [ ] RLS policies enforced
- [ ] No data leaks in logs
- [ ] Error handling complete
- [ ] Performance acceptable
- [ ] Load testing passed

---

## 🐛 Known Issues

**None at this time**

---

## 📝 Notes

- Screenshot detection uses `expo-screen-capture` which may not work on all Android devices
- Auto-destruction timing depends on privacy-jobs.js running continuously
- Message deletion happens daily at midnight
- Privacy events retained for 30 days for compliance

---

**Last Updated:** 2026-09-29  
**Status:** Ready for QA Testing

