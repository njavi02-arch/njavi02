/**
 * YUIZZ V2.0 - Privacy & Security Scheduled Jobs
 * Runs recurring maintenance tasks for privacy features
 */

import { createClient } from '@supabase/supabase-js';
import dotenv from 'dotenv';
import fs from 'fs';
import path from 'path';

dotenv.config();

const supabaseUrl = process.env.SUPABASE_URL;
const supabaseKey = process.env.SUPABASE_SERVICE_ROLE_KEY || process.env.SUPABASE_ANON_KEY;
const supabase = createClient(supabaseUrl, supabaseKey);

// ============================================
// JOB 1: AUTO-DESTROY EXPIRED PHOTOS
// ============================================

async function autoDestroyExpiredPhotos() {
  try {
    console.log('🕐 Starting photo destruction job...');

    // Get all photos that should be destroyed
    const { data: expiredPhotos, error: getError } = await supabase
      .from('auto_destroy_photos')
      .select('*')
      .eq('is_destroyed', false)
      .lte('destroy_at', new Date().toISOString());

    if (getError) {
      console.error('❌ Error fetching expired photos:', getError);
      return;
    }

    if (!expiredPhotos || expiredPhotos.length === 0) {
      console.log('✓ No photos to destroy');
      return;
    }

    console.log(`Found ${expiredPhotos.length} photos to destroy`);

    // Mark photos as destroyed
    for (const photo of expiredPhotos) {
      const { error: updateError } = await supabase
        .from('auto_destroy_photos')
        .update({
          is_destroyed: true,
          destroyed_at: new Date().toISOString(),
        })
        .eq('id', photo.id);

      if (updateError) {
        console.error(`Error marking photo ${photo.id} as destroyed:`, updateError);
        continue;
      }

      // Log privacy event
      await supabase
        .from('privacy_events')
        .insert({
          user_id: photo.sender_user_id,
          event_type: 'photo_auto_destroyed',
          conversation_id: photo.conversation_id,
          metadata: {
            photo_id: photo.photo_id,
            destroyed_at: new Date().toISOString(),
          },
          logged_at: new Date().toISOString(),
        });

      console.log(`✓ Photo ${photo.id} marked as destroyed`);
    }

    console.log(`✅ Destroyed ${expiredPhotos.length} photos`);

  } catch (error) {
    console.error('❌ Error in autoDestroyExpiredPhotos:', error);
  }
}

// ============================================
// JOB 2: AUTO-DELETE OLD MESSAGES
// ============================================

async function autoDeleteOldMessages() {
  try {
    console.log('🕐 Starting message deletion job...');

    // Get user preferences for auto-delete messages
    const { data: usersWithAutoDelete, error: getError } = await supabase
      .from('privacy_settings')
      .select('user_id')
      .eq('auto_delete_messages', true);

    if (getError) {
      console.error('❌ Error fetching users with auto-delete:', getError);
      return;
    }

    if (!usersWithAutoDelete || usersWithAutoDelete.length === 0) {
      console.log('✓ No users with auto-delete enabled');
      return;
    }

    const userIds = usersWithAutoDelete.map(u => u.user_id);
    console.log(`Found ${userIds.length} users with auto-delete enabled`);

    // Delete messages older than 24 hours for these users
    const twentyFourHoursAgo = new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString();

    const { data: deletedCount, error: deleteError } = await supabase
      .from('messages')
      .delete()
      .in('sender_id', userIds)
      .lt('created_at', twentyFourHoursAgo);

    if (deleteError) {
      console.error('❌ Error deleting old messages:', deleteError);
      return;
    }

    console.log(`✅ Auto-deleted messages older than 24 hours`);

  } catch (error) {
    console.error('❌ Error in autoDeleteOldMessages:', error);
  }
}

// ============================================
// JOB 3: CLEANUP OLD PRIVACY EVENTS
// ============================================

async function cleanupOldPrivacyEvents() {
  try {
    console.log('🕐 Starting privacy events cleanup...');

    // Delete events older than 30 days
    const thirtyDaysAgo = new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString();

    const { data, error } = await supabase
      .from('privacy_events')
      .delete()
      .lt('logged_at', thirtyDaysAgo);

    if (error) {
      console.error('❌ Error cleaning privacy events:', error);
      return;
    }

    console.log(`✅ Cleaned up privacy events older than 30 days`);

  } catch (error) {
    console.error('❌ Error in cleanupOldPrivacyEvents:', error);
  }
}

// ============================================
// JOB 4: CLEANUP INVALID PUSH TOKENS
// ============================================

async function cleanupInvalidPushTokens() {
  try {
    console.log('🕐 Starting push token cleanup...');

    // Mark tokens older than 90 days as inactive
    const ninetyDaysAgo = new Date(Date.now() - 90 * 24 * 60 * 60 * 1000).toISOString();

    const { data, error } = await supabase
      .from('user_push_tokens')
      .update({ is_active: false })
      .lt('last_used_at', ninetyDaysAgo)
      .eq('is_active', true);

    if (error) {
      console.error('❌ Error cleaning push tokens:', error);
      return;
    }

    console.log(`✅ Marked inactive push tokens as inactive`);

  } catch (error) {
    console.error('❌ Error in cleanupInvalidPushTokens:', error);
  }
}

// ============================================
// JOB SCHEDULER
// ============================================

function startJobScheduler() {
  console.log(`
╔════════════════════════════════════════╗
║  🔒 PRIVACY JOBS - RUNNING            ║
╚════════════════════════════════════════╝

📋 Scheduled Tasks:
  ✓ Auto-destroy photos (every 1 minute)
  ✓ Auto-delete messages (every 1 hour)
  ✓ Cleanup privacy events (every 1 day)
  ✓ Cleanup push tokens (every 1 day)

  `);

  // Run photo destruction every minute
  setInterval(autoDestroyExpiredPhotos, 60 * 1000);

  // Run message deletion every hour
  setInterval(autoDeleteOldMessages, 60 * 60 * 1000);

  // Run cleanup at midnight
  const scheduleAtMidnight = (fn) => {
    const now = new Date();
    const midnight = new Date(now);
    midnight.setDate(midnight.getDate() + 1);
    midnight.setHours(0, 0, 0, 0);

    const timeUntilMidnight = midnight - now;
    setTimeout(() => {
      fn();
      setInterval(fn, 24 * 60 * 60 * 1000);
    }, timeUntilMidnight);
  };

  scheduleAtMidnight(cleanupOldPrivacyEvents);
  scheduleAtMidnight(cleanupInvalidPushTokens);

  // Run immediately on startup
  autoDestroyExpiredPhotos();
  autoDeleteOldMessages();
}

// ============================================
// EXPORTS
// ============================================

export {
  autoDestroyExpiredPhotos,
  autoDeleteOldMessages,
  cleanupOldPrivacyEvents,
  cleanupInvalidPushTokens,
  startJobScheduler,
};

// ============================================
// CLI ENTRY POINT
// ============================================

if (process.argv[2] === '--start') {
  startJobScheduler();
} else if (process.argv[2] === '--destroy-photos') {
  autoDestroyExpiredPhotos().then(() => process.exit(0));
} else if (process.argv[2] === '--delete-messages') {
  autoDeleteOldMessages().then(() => process.exit(0));
} else if (process.argv[2] === '--cleanup-events') {
  cleanupOldPrivacyEvents().then(() => process.exit(0));
} else if (process.argv[2] === '--cleanup-tokens') {
  cleanupInvalidPushTokens().then(() => process.exit(0));
} else {
  console.log(`
Privacy Jobs - Usage:
  node privacy-jobs.js --start              Start scheduler
  node privacy-jobs.js --destroy-photos     Run photo destruction
  node privacy-jobs.js --delete-messages    Run message deletion
  node privacy-jobs.js --cleanup-events     Cleanup old events
  node privacy-jobs.js --cleanup-tokens     Cleanup push tokens
  `);
  process.exit(0);
}
