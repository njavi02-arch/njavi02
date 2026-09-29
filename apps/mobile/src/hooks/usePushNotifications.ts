import { useEffect, useState } from 'react';
import * as Notifications from 'expo-notifications';
import { useAuthStore } from '../store/authStore';

interface NotificationPreferences {
  newMatches: boolean;
  messages: boolean;
  likes: boolean;
  superLikes: boolean;
  boostReminders: boolean;
  subscriptionReminders: boolean;
}

export function usePushNotifications() {
  const [expoPushToken, setExpoPushToken] = useState<string | null>(null);
  const [isEnabled, setIsEnabled] = useState(true);
  const [preferences, setPreferences] = useState<NotificationPreferences>({
    newMatches: true,
    messages: true,
    likes: true,
    superLikes: true,
    boostReminders: true,
    subscriptionReminders: true,
  });

  const session = useAuthStore((s) => s.session);

  // Request permissions and get push token
  useEffect(() => {
    if (!session) return;

    (async () => {
      try {
        // Request permissions
        const { status: existingStatus } = await Notifications.getPermissionsAsync();
        let finalStatus = existingStatus;

        if (existingStatus !== 'granted') {
          const { status } = await Notifications.requestPermissionsAsync();
          finalStatus = status;
        }

        if (finalStatus !== 'granted') {
          setIsEnabled(false);
          console.log('❌ Notification permissions not granted');
          return;
        }

        // Get Expo push token
        const token = await Notifications.getExpoPushTokenAsync({
          projectId: process.env.EXPO_PUBLIC_PROJECT_ID,
        });

        setExpoPushToken(token.data);
        console.log(`✅ Expo push token: ${token.data}`);

        // Send token to backend
        await registerPushToken(token.data);

        // Configure notification handler
        Notifications.setNotificationHandler({
          handleNotification: async (notification) => {
            const { title, body } = notification.request.content;

            // Check preferences
            if (shouldShowNotification(notification.request.content.data)) {
              return {
                shouldShowAlert: true,
                shouldPlaySound: true,
                shouldSetBadge: true,
              };
            }

            return {
              shouldShowAlert: false,
              shouldPlaySound: false,
              shouldSetBadge: false,
            };
          },
        });

        setIsEnabled(true);
      } catch (error) {
        console.error('❌ Error setting up push notifications:', error);
      }
    })();
  }, [session]);

  // Register push token with backend
  const registerPushToken = async (token: string) => {
    try {
      if (!session?.access_token) return;

      await fetch(`${process.env.REACT_APP_API_URL || 'http://localhost:3001'}/api/v2/notifications/register-token`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${session.access_token}`,
        },
        body: JSON.stringify({ expoPushToken: token }),
      });

      console.log('✅ Push token registered with backend');
    } catch (error) {
      console.error('❌ Error registering push token:', error);
    }
  };

  // Check if notification should be shown based on preferences
  const shouldShowNotification = (data: any): boolean => {
    const type = data.type || 'general';

    switch (type) {
      case 'match':
        return preferences.newMatches;
      case 'message':
        return preferences.messages;
      case 'like':
        return preferences.likes;
      case 'superlike':
        return preferences.superLikes;
      case 'boost_reminder':
        return preferences.boostReminders;
      case 'subscription_reminder':
        return preferences.subscriptionReminders;
      default:
        return true;
    }
  };

  // Update notification preferences
  const updatePreferences = async (newPreferences: Partial<NotificationPreferences>) => {
    try {
      if (!session?.access_token) return;

      const updated = { ...preferences, ...newPreferences };

      await fetch(`${process.env.REACT_APP_API_URL || 'http://localhost:3001'}/api/v2/notifications/preferences`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${session.access_token}`,
        },
        body: JSON.stringify(updated),
      });

      setPreferences(updated);
      console.log('✅ Notification preferences updated');
    } catch (error) {
      console.error('❌ Error updating preferences:', error);
    }
  };

  // Send test notification
  const sendTestNotification = async () => {
    try {
      if (!session?.access_token) return;

      await fetch(`${process.env.REACT_APP_API_URL || 'http://localhost:3001'}/api/v2/notifications/send-test`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${session.access_token}`,
        },
      });

      console.log('✅ Test notification sent');
    } catch (error) {
      console.error('❌ Error sending test notification:', error);
    }
  };

  return {
    expoPushToken,
    isEnabled,
    preferences,
    updatePreferences,
    sendTestNotification,
  };
}
