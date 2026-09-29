import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  ScrollView,
  StyleSheet,
  SafeAreaView,
  Switch,
  TouchableOpacity,
  Alert,
} from 'react-native';
import { usePushNotifications } from '../hooks/usePushNotifications';

export function NotificationPreferencesScreen() {
  const {
    isEnabled,
    preferences,
    updatePreferences,
    sendTestNotification,
  } = usePushNotifications();

  const [loading, setLoading] = useState(false);

  const handleToggle = async (key: string, value: boolean) => {
    setLoading(true);
    try {
      await updatePreferences({ [key]: value });
    } catch (error) {
      Alert.alert('❌ Error', 'Failed to update preferences');
    } finally {
      setLoading(false);
    }
  };

  const handleTestNotification = async () => {
    try {
      await sendTestNotification();
      Alert.alert('✅ Success', 'Test notification sent!');
    } catch (error) {
      Alert.alert('❌ Error', 'Failed to send test notification');
    }
  };

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView showsVerticalScrollIndicator={false}>
        {/* Header */}
        <View style={styles.header}>
          <Text style={styles.headerTitle}>🔔 Notificaciones</Text>
          <Text style={styles.headerSubtitle}>
            {isEnabled ? '✅ Activadas' : '❌ Desactivadas'}
          </Text>
        </View>

        {!isEnabled && (
          <View style={styles.disabledBanner}>
            <Text style={styles.disabledText}>
              Las notificaciones están desactivadas. Habilita en configuración del sistema.
            </Text>
          </View>
        )}

        {/* Notification Categories */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Notificaciones</Text>

          {/* New Matches */}
          <View style={styles.preferencesItem}>
            <View style={styles.preferenceContent}>
              <Text style={styles.preferenceName}>🎉 Nuevos Matches</Text>
              <Text style={styles.preferenceDescription}>
                Cuando alguien te da like
              </Text>
            </View>
            <Switch
              value={preferences.newMatches}
              onValueChange={(value) => handleToggle('newMatches', value)}
              disabled={!isEnabled || loading}
            />
          </View>

          {/* Messages */}
          <View style={styles.preferencesItem}>
            <View style={styles.preferenceContent}>
              <Text style={styles.preferenceName}>💬 Mensajes</Text>
              <Text style={styles.preferenceDescription}>
                Nuevos mensajes en chats
              </Text>
            </View>
            <Switch
              value={preferences.messages}
              onValueChange={(value) => handleToggle('messages', value)}
              disabled={!isEnabled || loading}
            />
          </View>

          {/* Likes */}
          <View style={styles.preferencesItem}>
            <View style={styles.preferenceContent}>
              <Text style={styles.preferenceName}>❤️ Likes</Text>
              <Text style={styles.preferenceDescription}>
                Cuando alguien te da like
              </Text>
            </View>
            <Switch
              value={preferences.likes}
              onValueChange={(value) => handleToggle('likes', value)}
              disabled={!isEnabled || loading}
            />
          </View>

          {/* SuperLikes */}
          <View style={styles.preferencesItem}>
            <View style={styles.preferenceContent}>
              <Text style={styles.preferenceName}>⭐ SuperLikes</Text>
              <Text style={styles.preferenceDescription}>
                Cuando alguien te da SuperLike
              </Text>
            </View>
            <Switch
              value={preferences.superLikes}
              onValueChange={(value) => handleToggle('superLikes', value)}
              disabled={!isEnabled || loading}
            />
          </View>

          {/* Boost Reminders */}
          <View style={styles.preferencesItem}>
            <View style={styles.preferenceContent}>
              <Text style={styles.preferenceName}>🚀 Recordatorios de Boost</Text>
              <Text style={styles.preferenceDescription}>
                Cuando un boost está por expirar
              </Text>
            </View>
            <Switch
              value={preferences.boostReminders}
              onValueChange={(value) => handleToggle('boostReminders', value)}
              disabled={!isEnabled || loading}
            />
          </View>

          {/* Subscription Reminders */}
          <View style={styles.preferencesItem}>
            <View style={styles.preferenceContent}>
              <Text style={styles.preferenceName}>✨ Recordatorios de Premium</Text>
              <Text style={styles.preferenceDescription}>
                Cuando tu suscripción está por vencer
              </Text>
            </View>
            <Switch
              value={preferences.subscriptionReminders}
              onValueChange={(value) => handleToggle('subscriptionReminders', value)}
              disabled={!isEnabled || loading}
            />
          </View>
        </View>

        {/* Testing Section */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Prueba</Text>

          <TouchableOpacity
            style={styles.testButton}
            onPress={handleTestNotification}
            disabled={!isEnabled || loading}
          >
            <Text style={styles.testButtonText}>Enviar notificación de prueba</Text>
          </TouchableOpacity>

          <Text style={styles.testDescription}>
            Deberías recibir una notificación de prueba en tu dispositivo.
          </Text>
        </View>

        {/* Info Section */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>ℹ️ Información</Text>

          <View style={styles.infoBox}>
            <Text style={styles.infoText}>
              • Las notificaciones se envían en tiempo real
            </Text>
            <Text style={styles.infoText}>
              • Puedes cambiar estas preferencias en cualquier momento
            </Text>
            <Text style={styles.infoText}>
              • Algunos eventos importantes siempre te notificarán
            </Text>
            <Text style={styles.infoText}>
              • Desactiva notificaciones en configuración del sistema para desuscribirse completamente
            </Text>
          </View>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  header: {
    backgroundColor: '#fff',
    paddingHorizontal: 16,
    paddingVertical: 20,
    borderBottomWidth: 1,
    borderBottomColor: '#eee',
  },
  headerTitle: {
    fontSize: 24,
    fontWeight: '700',
    color: '#333',
  },
  headerSubtitle: {
    fontSize: 13,
    color: '#999',
    marginTop: 4,
  },
  disabledBanner: {
    backgroundColor: '#fff3cd',
    paddingHorizontal: 16,
    paddingVertical: 12,
    marginHorizontal: 16,
    marginTop: 16,
    borderRadius: 8,
    borderLeftWidth: 4,
    borderLeftColor: '#ffc107',
  },
  disabledText: {
    fontSize: 13,
    color: '#856404',
    fontWeight: '500',
  },
  section: {
    backgroundColor: '#fff',
    marginTop: 16,
    marginHorizontal: 16,
    borderRadius: 12,
    paddingVertical: 12,
  },
  sectionTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: '#999',
    textTransform: 'uppercase',
    paddingHorizontal: 16,
    paddingTop: 8,
    paddingBottom: 12,
  },
  preferencesItem: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 16,
    paddingVertical: 14,
    borderBottomWidth: 1,
    borderBottomColor: '#f0f0f0',
  },
  preferenceContent: {
    flex: 1,
    marginRight: 16,
  },
  preferenceName: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
    marginBottom: 4,
  },
  preferenceDescription: {
    fontSize: 13,
    color: '#999',
  },
  testButton: {
    marginHorizontal: 16,
    marginVertical: 12,
    paddingVertical: 12,
    backgroundColor: '#667eea',
    borderRadius: 8,
    alignItems: 'center',
  },
  testButtonText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#fff',
  },
  testDescription: {
    fontSize: 12,
    color: '#999',
    paddingHorizontal: 16,
    marginBottom: 12,
  },
  infoBox: {
    backgroundColor: '#f8f9ff',
    paddingHorizontal: 16,
    paddingVertical: 12,
    marginHorizontal: 16,
    borderRadius: 8,
    borderLeftWidth: 3,
    borderLeftColor: '#667eea',
  },
  infoText: {
    fontSize: 13,
    color: '#666',
    lineHeight: 20,
    marginBottom: 8,
  },
});
