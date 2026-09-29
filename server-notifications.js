// ============================================
// YUIZZ V2.0 - PUSH NOTIFICATIONS
// Firebase Cloud Messaging Integration
// ============================================

import admin from 'firebase-admin';
import dotenv from 'dotenv';

dotenv.config();

// Initialize Firebase Admin
const serviceAccount = JSON.parse(process.env.FIREBASE_SERVICE_ACCOUNT || '{}');

if (!serviceAccount.project_id) {
  console.warn('⚠️  FIREBASE_SERVICE_ACCOUNT not configured');
}

admin.initializeApp({
  credential: admin.credential.cert(serviceAccount),
  projectId: process.env.FIREBASE_PROJECT_ID,
});

// ============================================
// NOTIFICATION TYPES & TEMPLATES
// ============================================

const NOTIFICATION_TEMPLATES = {
  newMatch: {
    title: '🎉 ¡Nuevo Match!',
    body: '{name} te ha gustado. ¡Empieza a chatear!',
    icon: 'match',
  },
  newMessage: {
    title: '💬 Nuevo mensaje',
    body: '{name}: {preview}',
    icon: 'message',
  },
  likeReceived: {
    title: '❤️ Te ha gustado',
    body: '{name} te ha dado like',
    icon: 'like',
  },
  superlikeReceived: {
    title: '⭐ ¡SuperLike!',
    body: '{name} te ha dado un SuperLike',
    icon: 'superlike',
  },
  boostExpiring: {
    title: '🚀 Boost expirando',
    body: 'Tu boost expira en 5 minutos',
    icon: 'boost',
  },
  subscriptionReminder: {
    title: '✨ Premium activo',
    body: 'Tu suscripción vence en {days} días',
    icon: 'premium',
  },
  subscriptionExpiring: {
    title: '⏰ Suscripción vence pronto',
    body: 'Tu Premium vence mañana. ¿Renovar?',
    icon: 'premium',
  },
  verificationRequest: {
    title: '🎯 Verifica tu perfil',
    body: 'Completa la verificación para más visibilidad',
    icon: 'verify',
  },
};

// ============================================
// SEND NOTIFICATION FUNCTIONS
// ============================================

export async function sendNotification(userId, template, data = {}) {
  try {
    const templateData = NOTIFICATION_TEMPLATES[template];
    if (!templateData) {
      throw new Error(`Unknown template: ${template}`);
    }

    // Replace placeholders in title and body
    let title = templateData.title;
    let body = templateData.body;

    Object.entries(data).forEach(([key, value]) => {
      title = title.replace(`{${key}}`, value);
      body = body.replace(`{${key}}`, value);
    });

    // Get user's push tokens from database
    // TODO: Query from user_push_tokens table
    const tokens = await getUserPushTokens(userId);

    if (tokens.length === 0) {
      console.log(`⚠️  No push tokens for user ${userId}`);
      return;
    }

    // Send to all tokens
    const response = await admin.messaging().sendMulticast({
      tokens,
      notification: {
        title,
        body,
      },
      data: {
        type: template,
        userId,
        ...data,
      },
      android: {
        priority: 'high',
        notification: {
          sound: 'default',
          clickAction: 'FLUTTER_NOTIFICATION_CLICK',
        },
      },
      apns: {
        headers: {
          'apns-priority': '10',
        },
      },
    });

    console.log(`✅ Notification sent to ${userId}: ${template}`);
    console.log(`   Successful: ${response.successCount}, Failed: ${response.failureCount}`);

    // Handle failures
    if (response.failureCount > 0) {
      response.responses.forEach((resp, idx) => {
        if (!resp.success) {
          console.error(`   ❌ Failed to send to token ${idx}: ${resp.error.message}`);
          // TODO: Remove invalid token from database
        }
      });
    }

    return response;
  } catch (error) {
    console.error('❌ Error sending notification:', error);
    throw error;
  }
}

export async function sendBatchNotifications(userIds, template, data = {}) {
  try {
    const results = await Promise.all(
      userIds.map((userId) => sendNotification(userId, template, data))
    );

    console.log(`✅ Batch notifications sent to ${userIds.length} users`);
    return results;
  } catch (error) {
    console.error('❌ Error sending batch notifications:', error);
    throw error;
  }
}

export async function sendTopicNotification(topic, template, data = {}) {
  try {
    const templateData = NOTIFICATION_TEMPLATES[template];
    if (!templateData) {
      throw new Error(`Unknown template: ${template}`);
    }

    let title = templateData.title;
    let body = templateData.body;

    Object.entries(data).forEach(([key, value]) => {
      title = title.replace(`{${key}}`, value);
      body = body.replace(`{${key}}`, value);
    });

    const response = await admin.messaging().send({
      notification: {
        title,
        body,
      },
      topic,
      data: {
        type: template,
        ...data,
      },
    });

    console.log(`✅ Topic notification sent to ${topic}`);
    return response;
  } catch (error) {
    console.error('❌ Error sending topic notification:', error);
    throw error;
  }
}

// ============================================
// TOKEN MANAGEMENT
// ============================================

export async function registerPushToken(userId, expoPushToken) {
  try {
    // TODO: Save to database
    console.log(`✅ Push token registered for user ${userId}`);
  } catch (error) {
    console.error('❌ Error registering push token:', error);
    throw error;
  }
}

export async function unsubscribeToken(expoPushToken) {
  try {
    // TODO: Remove from database
    console.log(`✅ Push token unsubscribed`);
  } catch (error) {
    console.error('❌ Error unsubscribing token:', error);
    throw error;
  }
}

export async function getUserPushTokens(userId) {
  try {
    // TODO: Query from database
    // SELECT expo_push_token FROM user_push_tokens
    // WHERE user_id = userId AND is_active = true
    return [];
  } catch (error) {
    console.error('❌ Error getting push tokens:', error);
    throw error;
  }
}

// ============================================
// SCHEDULED NOTIFICATIONS
// ============================================

export async function scheduleBoostReminder(userId, boostExpiresAt) {
  try {
    const timeUntilExpiry = new Date(boostExpiresAt) - Date.now();

    if (timeUntilExpiry > 5 * 60 * 1000) {
      // Schedule 5 minutes before expiry
      setTimeout(() => {
        sendNotification(userId, 'boostExpiring');
      }, timeUntilExpiry - 5 * 60 * 1000);

      console.log(`📅 Boost reminder scheduled for user ${userId}`);
    }
  } catch (error) {
    console.error('❌ Error scheduling boost reminder:', error);
  }
}

export async function scheduleSubscriptionReminder(userId, subscriptionExpiresAt) {
  try {
    const expiryDate = new Date(subscriptionExpiresAt);
    const now = new Date();
    const daysUntilExpiry = Math.ceil((expiryDate - now) / (24 * 60 * 60 * 1000));

    // Send reminder 3 days before expiry
    if (daysUntilExpiry === 3) {
      await sendNotification(userId, 'subscriptionReminder', {
        days: 3,
      });
    }

    // Send reminder 1 day before expiry
    if (daysUntilExpiry === 1) {
      await sendNotification(userId, 'subscriptionExpiring');
    }

    console.log(`📅 Subscription reminder scheduled for user ${userId}`);
  } catch (error) {
    console.error('❌ Error scheduling subscription reminder:', error);
  }
}

// ============================================
// NOTIFICATION EVENTS
// ============================================

export async function notifyNewMatch(userId1, userId2, userName1, userName2) {
  try {
    await Promise.all([
      sendNotification(userId1, 'newMatch', { name: userName2 }),
      sendNotification(userId2, 'newMatch', { name: userName1 }),
    ]);
  } catch (error) {
    console.error('❌ Error notifying new match:', error);
  }
}

export async function notifyNewMessage(senderId, senderName, recipientId, messagePreview) {
  try {
    await sendNotification(recipientId, 'newMessage', {
      name: senderName,
      preview: messagePreview.substring(0, 50),
    });
  } catch (error) {
    console.error('❌ Error notifying new message:', error);
  }
}

export async function notifyLikeReceived(likerId, likerName, likedUserId) {
  try {
    await sendNotification(likedUserId, 'likeReceived', { name: likerName });
  } catch (error) {
    console.error('❌ Error notifying like:', error);
  }
}

export async function notifySuperlikeReceived(superliker, superlikerName, superlikedId) {
  try {
    await sendNotification(superlikedId, 'superlikeReceived', { name: superlikerName });
  } catch (error) {
    console.error('❌ Error notifying superlike:', error);
  }
}

export async function notifyVerificationRequest(userId) {
  try {
    await sendNotification(userId, 'verificationRequest');
  } catch (error) {
    console.error('❌ Error notifying verification request:', error);
  }
}

// ============================================
// EXPORTS
// ============================================

export { admin };
