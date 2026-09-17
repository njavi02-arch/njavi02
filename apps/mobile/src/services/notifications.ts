import { Platform } from 'react-native';
import * as Notifications from 'expo-notifications';
import * as Device from 'expo-device';
import { supabase } from '../lib/supabase';
import type { NotificationRow } from '../types/database';

Notifications.setNotificationHandler({
  handleNotification: async () => ({
    shouldShowAlert: true,
    shouldPlaySound: true,
    shouldSetBadge: true,
    shouldShowBanner: true,
    shouldShowList: true,
  }),
});

/**
 * Pide permiso y registra el token de push del dispositivo en `push_tokens`. La entrega
 * real (Expo Push Service → APNs/FCM) necesita credenciales de Apple/Google dadas de alta
 * en el proyecto EAS (ver docs/07-roadmap-and-scaling.md) — eso sí está fuera del alcance
 * de esta build. Pero el registro del token en sí es real y funciona ya: cualquier backend
 * que envíe a través del Expo Push Service podría notificar a este dispositivo en cuanto
 * exista ese backend.
 */
export async function registerPushToken(profileId: string): Promise<void> {
  if (Platform.OS === 'web') return; // expo-notifications no soporta push en web
  if (!Device.isDevice) return; // los simuladores no tienen token de push real

  const { status: existingStatus } = await Notifications.getPermissionsAsync();
  let finalStatus = existingStatus;
  if (existingStatus !== 'granted') {
    const { status } = await Notifications.requestPermissionsAsync();
    finalStatus = status;
  }
  if (finalStatus !== 'granted') return;

  if (Platform.OS === 'android') {
    await Notifications.setNotificationChannelAsync('default', {
      name: 'default',
      importance: Notifications.AndroidImportance.DEFAULT,
    });
  }

  const { data: token } = await Notifications.getExpoPushTokenAsync();

  const { error } = await supabase.from('push_tokens').upsert(
    {
      profile_id: profileId,
      expo_push_token: token,
      platform: Platform.OS === 'ios' ? 'ios' : 'android',
      last_used_at: new Date().toISOString(),
    },
    { onConflict: 'profile_id,expo_push_token' },
  );
  if (error) throw error;
}

export async function unregisterAllPushTokens(profileId: string): Promise<void> {
  const { error } = await supabase.from('push_tokens').delete().eq('profile_id', profileId);
  if (error) throw error;
}

export async function listNotifications(profileId: string): Promise<NotificationRow[]> {
  const { data, error } = await supabase
    .from('notifications')
    .select('*')
    .eq('profile_id', profileId)
    .order('created_at', { ascending: false })
    .limit(50);
  if (error) throw error;
  return (data ?? []) as NotificationRow[];
}

export async function markNotificationRead(notificationId: string): Promise<void> {
  const { error } = await supabase.from('notifications').update({ is_read: true }).eq('id', notificationId);
  if (error) throw error;
}

export async function markAllNotificationsRead(profileId: string): Promise<void> {
  const { error } = await supabase
    .from('notifications')
    .update({ is_read: true })
    .eq('profile_id', profileId)
    .eq('is_read', false);
  if (error) throw error;
}
