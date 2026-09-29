import { useEffect, useState } from 'react';
import * as ScreenCapture from 'expo-screen-capture';
import { Alert } from 'react-native';
import { useAuthStore } from '../store/authStore';

interface PrivacySettings {
  anonymousMode: boolean;
  preventScreenshots: boolean;
  autoDeleteMessages: boolean;
  autoDeletePhotos: boolean;
  deletePhotosAfterMinutes: number;
  showLastSeen: boolean;
  showTypingIndicator: boolean;
  allowForwarding: boolean;
}

export function usePrivacyMode() {
  const [privacySettings, setPrivacySettings] = useState<PrivacySettings>({
    anonymousMode: false,
    preventScreenshots: true,
    autoDeleteMessages: false,
    autoDeletePhotos: false,
    deletePhotosAfterMinutes: 24 * 60, // 24 hours
    showLastSeen: false,
    showTypingIndicator: false,
    allowForwarding: false,
  });

  const [screenshotAttempts, setScreenshotAttempts] = useState(0);
  const session = useAuthStore((s) => s.session);

  // Monitor screenshot attempts
  useEffect(() => {
    if (!privacySettings.preventScreenshots) return;

    const subscription = ScreenCapture.addScreenshotListener(() => {
      handleScreenshotAttempt();
    });

    return () => {
      subscription.remove();
    };
  }, [privacySettings.preventScreenshots]);

  // Handle screenshot attempt
  const handleScreenshotAttempt = async () => {
    try {
      setScreenshotAttempts((prev) => prev + 1);

      // Alert user
      Alert.alert(
        '⚠️ Screenshot Detectado',
        'Las capturas no están permitidas en modo privado. El otro usuario ha sido notificado.',
        [{ text: 'Entendido' }]
      );

      // Notify other user
      await notifyScreenshotAttempt();

      // Log event
      logPrivacyEvent('screenshot_attempt');
    } catch (error) {
      console.error('❌ Error handling screenshot:', error);
    }
  };

  // Notify other user about screenshot attempt
  const notifyScreenshotAttempt = async () => {
    try {
      if (!session?.access_token) return;

      await fetch(`${process.env.REACT_APP_API_URL || 'http://localhost:3001'}/api/v2/privacy/screenshot-attempt`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${session.access_token}`,
        },
        body: JSON.stringify({
          attemptCount: screenshotAttempts + 1,
        }),
      });

      console.log('✅ Screenshot attempt reported');
    } catch (error) {
      console.error('❌ Error notifying screenshot:', error);
    }
  };

  // Update privacy settings
  const updatePrivacySettings = async (newSettings: Partial<PrivacySettings>) => {
    try {
      if (!session?.access_token) return;

      const updated = { ...privacySettings, ...newSettings };

      await fetch(`${process.env.REACT_APP_API_URL || 'http://localhost:3001'}/api/v2/privacy/settings`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${session.access_token}`,
        },
        body: JSON.stringify(updated),
      });

      setPrivacySettings(updated);
      console.log('✅ Privacy settings updated');
    } catch (error) {
      console.error('❌ Error updating privacy settings:', error);
    }
  };

  // Log privacy events
  const logPrivacyEvent = async (eventType: string) => {
    try {
      if (!session?.access_token) return;

      await fetch(`${process.env.REACT_APP_API_URL || 'http://localhost:3001'}/api/v2/privacy/log-event`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${session.access_token}`,
        },
        body: JSON.stringify({ eventType }),
      });
    } catch (error) {
      console.error('❌ Error logging privacy event:', error);
    }
  };

  return {
    privacySettings,
    updatePrivacySettings,
    screenshotAttempts,
    logPrivacyEvent,
  };
}
