# YUIZZ V2.0 - Privacy & Security Features

**Date:** 2026-09-29  
**Phase:** 4 (Push Notifications / Privacy Features)  
**Status:** Implemented ✅

---

## 📋 Overview

Privacy and security features have been added to YUIZZ V2.0 to protect user anonymity, prevent content capture, and enable conversation/media deletion controls.

---

## 🔐 Features Implemented

### 1. Anonymous Mode
**Description:** Hide user identity in conversations

**Settings:**
- `anonymousMode` - Don't show name or profile photo in chats
- `showLastSeen` - Hide "last seen" timestamp
- `showTypingIndicator` - Hide typing indicator while composing

**Frontend:** PrivacySettingsScreen.tsx (Lines 40-85)

**Database:** `privacy_settings` table (columns: `anonymous_mode`, `show_last_seen`, `show_typing_indicator`)

---

### 2. Screenshot Protection
**Description:** Detect and prevent screenshots, alert other user

**Functionality:**
- Monitor screenshot attempts using `expo-screen-capture`
- Alert user when screenshot is attempted
- Notify other user via POST to `/api/v2/privacy/screenshot-attempt`
- Count screenshot attempts

**Frontend:** 
- `usePrivacyMode.ts` hook (Lines 33-43: screenshot listener)
- `usePrivacyMode.ts` hook (Lines 46-65: handleScreenshotAttempt)
- `PrivacySettingsScreen.tsx` (Lines 87-110: UI)

**Backend Endpoint:**
```
POST /api/v2/privacy/screenshot-attempt
Request: { attemptCount, conversationId }
Response: { success, attempt: { id, attemptNumber, detectedAt } }
```

**Database:** 
- `privacy_settings` table (column: `prevent_screenshots`)
- `screenshot_attempts` table - Logs all attempts with timestamp

---

### 3. Message Auto-Deletion
**Description:** Messages auto-delete after 24 hours for both users

**Settings:**
- `autoDeleteMessages` - Enable/disable auto-deletion

**Frontend:** PrivacySettingsScreen.tsx (Lines 112-135)

**Database:** `privacy_settings` table (column: `auto_delete_messages`)

**Implementation Note:** Scheduled job needed to delete messages 24 hours after creation (can be implemented in `server-realtime.js` or as Postgres trigger)

---

### 4. Photo Auto-Destruction
**Description:** Photos auto-destroy after configurable time period

**Settings:**
- `autoDeletePhotos` - Enable/disable auto-destruction
- `deletePhotosAfterMinutes` - Time in minutes (5, 30, 60, 1440)

**Options:**
- 5 minutes
- 30 minutes
- 1 hour
- 24 hours

**Frontend:** 
- `usePrivacyMode.ts` (Line 11: deletePhotosAfterMinutes)
- `PrivacySettingsScreen.tsx` (Lines 137-193: UI with time selector)

**Database:**
- `privacy_settings` table (columns: `auto_delete_photos`, `delete_photos_after_minutes`)
- `auto_destroy_photos` table - Tracks photos and destruction schedule

**Implementation Note:** Scheduled cleanup job needed (use `auto_destroy_expired_photos()` function)

---

### 5. Photo Pinning
**Description:** Photos can be kept permanent in chat (not auto-destroyed)

**Functionality:**
- Toggle `autoDeletePhotos` off = photos stay in chat permanently
- Toggle `autoDeletePhotos` on = photos auto-destroy per timer

**Frontend:** PrivacySettingsScreen.tsx (Lines 155-193)

---

### 6. Conversation Deletion
**Description:** Delete entire conversation with confirmation

**Functionality:**
- Soft delete (mark as deleted for user, other user still sees it)
- Optional: Permanently delete if both users delete
- Notification sent to other user

**Frontend:** PrivacySettingsScreen.tsx (Lines 236-259)

**Backend Endpoint:**
```
POST /api/v2/privacy/delete-conversation
Request: { conversationId }
Response: { success, message: "Conversation deleted" }
```

**Database:**
- `conversations` table (columns: `deleted_by_users`, `deleted_at`)
- `privacy_events` table - Logs deletion event

---

### 7. Photo Forwarding Control
**Description:** Allow/disable forwarding of photos to other users

**Settings:**
- `allowForwarding` - Allow sharing photos with other users

**Frontend:** PrivacySettingsScreen.tsx (Lines 195-207)

**Database:** `privacy_settings` table (column: `allow_forwarding`)

---

## 🗄️ Database Schema

### privacy_settings Table
```sql
CREATE TABLE privacy_settings (
  id UUID PRIMARY KEY,
  user_id UUID UNIQUE NOT NULL,
  anonymous_mode BOOLEAN DEFAULT false,
  prevent_screenshots BOOLEAN DEFAULT true,
  auto_delete_messages BOOLEAN DEFAULT false,
  auto_delete_photos BOOLEAN DEFAULT false,
  delete_photos_after_minutes INTEGER DEFAULT 1440,
  show_last_seen BOOLEAN DEFAULT false,
  show_typing_indicator BOOLEAN DEFAULT false,
  allow_forwarding BOOLEAN DEFAULT false,
  created_at TIMESTAMP,
  updated_at TIMESTAMP
);
```

### screenshot_attempts Table
```sql
CREATE TABLE screenshot_attempts (
  id UUID PRIMARY KEY,
  user_id UUID NOT NULL,
  attempt_number INTEGER DEFAULT 1,
  conversation_id UUID,
  detected_at TIMESTAMP,
  created_at TIMESTAMP
);
```

### privacy_events Table (Audit Trail)
```sql
CREATE TABLE privacy_events (
  id UUID PRIMARY KEY,
  user_id UUID NOT NULL,
  event_type VARCHAR(50), -- screenshot_attempt, conversation_deleted, etc.
  conversation_id UUID,
  other_user_id UUID,
  metadata JSONB DEFAULT '{}',
  logged_at TIMESTAMP,
  created_at TIMESTAMP
);
```

### auto_destroy_photos Table
```sql
CREATE TABLE auto_destroy_photos (
  id UUID PRIMARY KEY,
  photo_id UUID NOT NULL,
  conversation_id UUID,
  sender_user_id UUID NOT NULL,
  destroy_at TIMESTAMP NOT NULL,
  is_destroyed BOOLEAN DEFAULT false,
  destroyed_at TIMESTAMP,
  created_at TIMESTAMP
);
```

---

## 📡 API Endpoints

### POST /api/v2/privacy/settings
**Save user privacy settings**

Request:
```json
{
  "anonymousMode": boolean,
  "preventScreenshots": boolean,
  "autoDeleteMessages": boolean,
  "autoDeletePhotos": boolean,
  "deletePhotosAfterMinutes": number,
  "showLastSeen": boolean,
  "showTypingIndicator": boolean,
  "allowForwarding": boolean
}
```

Response:
```json
{
  "success": true,
  "settings": { ... }
}
```

---

### GET /api/v2/privacy/settings
**Get user privacy settings**

Response:
```json
{
  "success": true,
  "settings": {
    "anonymousMode": false,
    "preventScreenshots": true,
    "autoDeleteMessages": false,
    "autoDeletePhotos": false,
    "deletePhotosAfterMinutes": 1440,
    "showLastSeen": false,
    "showTypingIndicator": false,
    "allowForwarding": false
  }
}
```

---

### POST /api/v2/privacy/screenshot-attempt
**Log screenshot attempt and notify other user**

Request:
```json
{
  "attemptCount": number,
  "conversationId": "uuid (optional)"
}
```

Response:
```json
{
  "success": true,
  "attempt": {
    "id": "uuid",
    "attemptNumber": number,
    "detectedAt": "timestamp"
  }
}
```

---

### POST /api/v2/privacy/delete-conversation
**Delete conversation and notify other user**

Request:
```json
{
  "conversationId": "uuid"
}
```

Response:
```json
{
  "success": true,
  "message": "Conversation deleted"
}
```

---

### POST /api/v2/privacy/log-event
**Log privacy event for audit trail**

Request:
```json
{
  "eventType": "screenshot_attempt|conversation_deleted|photo_viewed|etc",
  "conversationId": "uuid (optional)",
  "metadata": {} // Optional additional data
}
```

Response:
```json
{
  "success": true,
  "event": {
    "id": "uuid",
    "eventType": "string",
    "loggedAt": "timestamp"
  }
}
```

---

## 📱 Frontend Components

### usePrivacyMode Hook
**File:** `apps/mobile/src/hooks/usePrivacyMode.ts` (150 lines)

**Exports:**
```typescript
{
  privacySettings: PrivacySettings,
  updatePrivacySettings: (newSettings: Partial<PrivacySettings>) => Promise<void>,
  screenshotAttempts: number,
  logPrivacyEvent: (eventType: string) => Promise<void>
}
```

**Key Methods:**
- `handleScreenshotAttempt()` - Screenshot detection handler
- `notifyScreenshotAttempt()` - POST to backend
- `updatePrivacySettings()` - Persist settings to database
- `logPrivacyEvent()` - Audit trail logging

**Features:**
- Screenshot listener with expo-screen-capture
- Alert.alert when screenshot detected
- Auto-notify other user
- Automatic cleanup on unmount

---

### PrivacySettingsScreen Component
**File:** `apps/mobile/src/screens/PrivacySettingsScreen.tsx` (250+ lines)

**Sections:**
1. **Anonymous Mode** - Toggle anonymousMode, showLastSeen, showTypingIndicator
2. **Screenshot Protection** - Toggle preventScreenshots with info box
3. **Message Auto-deletion** - Toggle autoDeleteMessages with info
4. **Photo Settings** - Toggle autoDeletePhotos, time selector, allowForwarding
5. **Info Section** - 3 info boxes explaining features
6. **Danger Zone** - Delete conversation button with confirmation

**Styling:**
- Custom StyleSheet with:
  - Header with subtitle
  - Section cards with rounded corners
  - Time selector buttons with active state
  - Info boxes with left border accent
  - Danger zone red button

---

## 🔄 Workflow Examples

### Example 1: Screenshot Protection
1. User A enables `preventScreenshots` via PrivacySettingsScreen
2. User A opens conversation with User B
3. User B attempts to take screenshot
4. `expo-screen-capture` listener triggers
5. User A sees: Alert "⚠️ Screenshot Detectado"
6. Backend logs attempt in `screenshot_attempts` table
7. User B receives notification via socket/FCM (TODO)

### Example 2: Photo Auto-Destruction
1. User A sends photo with `autoDeletePhotos` enabled
2. Photo is stored with destroy_at = now + deletePhotosAfterMinutes
3. Entry created in `auto_destroy_photos` table
4. Scheduled job runs every minute checking for expired photos
5. When destroy_at <= now, photo is deleted from storage
6. Entry marked as destroyed

### Example 3: Conversation Deletion
1. User A opens PrivacySettingsScreen
2. Clicks "Eliminar Conversación"
3. Confirmation alert appears
4. User A confirms deletion
5. Soft delete: conversation marked with deleted_by_users=[User A]
6. Event logged in `privacy_events` table
7. User B still sees conversation (TODO: notify User B)

---

## 🚀 Implementation Checklist

### ✅ Completed
- [x] Frontend hooks (usePrivacyMode)
- [x] Frontend screen (PrivacySettingsScreen)
- [x] Backend API endpoints
- [x] Database migration (PRIVACY_MIGRATION.sql)
- [x] RLS policies for all tables
- [x] Triggers for timestamp updates
- [x] Audit trail logging

### 📝 TODO (Next Steps)
- [ ] Run PRIVACY_MIGRATION.sql in Supabase
- [ ] Implement scheduled job for auto-destructing photos
- [ ] Implement scheduled job for auto-deleting messages
- [ ] Implement socket.io/FCM notifications for screenshot attempts
- [ ] Test privacy features end-to-end
- [ ] Add anonymous profile display logic in Discovery screen
- [ ] Add UI indicator when user is in anonymous mode
- [ ] Create privacy feature tutorial/onboarding

---

## 🔐 Security Considerations

### Row Level Security (RLS)
✅ All privacy tables have RLS enabled
✅ Users can only view/update their own settings
✅ System can insert privacy events
✅ Soft-deleted conversations are filtered by user

### Data Protection
✅ Screenshot attempts logged with timestamps
✅ Privacy events create complete audit trail
✅ Metadata can store additional context
✅ Old events automatically cleaned (30-day retention)

### Privacy by Default
- `preventScreenshots: true` (enabled by default)
- Screenshot attempts tracked even if user doesn't view them
- Metadata stored for investigation/reporting

---

## 📚 Related Files

- `PRIVACY_MIGRATION.sql` - Database schema
- `server-v2.js` - API endpoints (lines 2515-2850+)
- `apps/mobile/src/hooks/usePrivacyMode.ts` - Screenshot detection hook
- `apps/mobile/src/screens/PrivacySettingsScreen.tsx` - Settings UI
- `.github/PULL_REQUEST_TEMPLATE.md` - PR template (if exists)

---

## 🎯 Next Phase

**Phase 5 (Future):** Integration & Deployment
- Verify all privacy endpoints work with mobile app
- Test photo auto-destruction with scheduled jobs
- Test message auto-deletion after 24 hours
- Implement anonymous profile display
- Deploy to production with monitoring

---

**Status:** Privacy features ready for database migration and testing  
**Last Updated:** 2026-09-29  
**Committed:** Yes (branch: `claude/app-7n3n95`)

