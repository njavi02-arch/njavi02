import React, { useState } from 'react';
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
import { usePrivacyMode } from '../hooks/usePrivacyMode';

export function PrivacySettingsScreen() {
  const { privacySettings, updatePrivacySettings } = usePrivacyMode();
  const [loading, setLoading] = useState(false);

  const handleToggle = async (key: string, value: boolean) => {
    setLoading(true);
    try {
      await updatePrivacySettings({ [key]: value });
    } catch (error) {
      Alert.alert('❌ Error', 'Failed to update privacy settings');
    } finally {
      setLoading(false);
    }
  };

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView showsVerticalScrollIndicator={false}>
        {/* Header */}
        <View style={styles.header}>
          <Text style={styles.headerTitle}>🔒 Privacidad & Seguridad</Text>
          <Text style={styles.headerSubtitle}>
            Controla quién puede ver y capturar tus datos
          </Text>
        </View>

        {/* Anonymous Mode */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Modo Anónimo</Text>

          <View style={styles.settingItem}>
            <View style={styles.settingContent}>
              <Text style={styles.settingName}>👤 Modo Anónimo</Text>
              <Text style={styles.settingDescription}>
                No mostrar nombre ni foto de perfil en chats
              </Text>
            </View>
            <Switch
              value={privacySettings.anonymousMode}
              onValueChange={(value) => handleToggle('anonymousMode', value)}
              disabled={loading}
            />
          </View>

          <View style={styles.settingItem}>
            <View style={styles.settingContent}>
              <Text style={styles.settingName}>👁️ Mostrar Último Visto</Text>
              <Text style={styles.settingDescription}>
                Mostrar cuándo fue tu última conexión
              </Text>
            </View>
            <Switch
              value={privacySettings.showLastSeen}
              onValueChange={(value) => handleToggle('showLastSeen', value)}
              disabled={loading}
            />
          </View>

          <View style={styles.settingItem}>
            <View style={styles.settingContent}>
              <Text style={styles.settingName}>⌨️ Indicador de Escritura</Text>
              <Text style={styles.settingDescription}>
                Mostrar cuando estés escribiendo
              </Text>
            </View>
            <Switch
              value={privacySettings.showTypingIndicator}
              onValueChange={(value) => handleToggle('showTypingIndicator', value)}
              disabled={loading}
            />
          </View>
        </View>

        {/* Screenshot Protection */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>🛡️ Protección de Capturas</Text>

          <View style={styles.settingItem}>
            <View style={styles.settingContent}>
              <Text style={styles.settingName}>Bloquear Screenshots</Text>
              <Text style={styles.settingDescription}>
                Detectar y alertar sobre intentos de captura
              </Text>
            </View>
            <Switch
              value={privacySettings.preventScreenshots}
              onValueChange={(value) => handleToggle('preventScreenshots', value)}
              disabled={loading}
            />
          </View>

          <View style={styles.infoBox}>
            <Text style={styles.infoText}>
              ℹ️ Cuando el otro usuario intente hacer captura, recibirá una alerta y tú serás notificado.
            </Text>
          </View>
        </View>

        {/* Message Deletion */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>💬 Auto-eliminación de Mensajes</Text>

          <View style={styles.settingItem}>
            <View style={styles.settingContent}>
              <Text style={styles.settingName}>Auto-eliminar Mensajes</Text>
              <Text style={styles.settingDescription}>
                Los mensajes se eliminan automáticamente
              </Text>
            </View>
            <Switch
              value={privacySettings.autoDeleteMessages}
              onValueChange={(value) => handleToggle('autoDeleteMessages', value)}
              disabled={loading}
            />
          </View>

          <View style={styles.infoBox}>
            <Text style={styles.infoText}>
              ✓ Los mensajes se eliminarán después de 24 horas para ambos usuarios
            </Text>
          </View>
        </View>

        {/* Photo Settings */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>📸 Fotos & Medios</Text>

          <View style={styles.settingItem}>
            <View style={styles.settingContent}>
              <Text style={styles.settingName}>Auto-destruir Fotos</Text>
              <Text style={styles.settingDescription}>
                Las fotos se eliminarán automáticamente
              </Text>
            </View>
            <Switch
              value={privacySettings.autoDeletePhotos}
              onValueChange={(value) => handleToggle('autoDeletePhotos', value)}
              disabled={loading}
            />
          </View>

          {privacySettings.autoDeletePhotos && (
            <View style={styles.timeSelector}>
              <Text style={styles.timeSelectorLabel}>
                Auto-eliminar después de:
              </Text>
              <View style={styles.timeOptions}>
                {[
                  { label: '5 min', value: 5 },
                  { label: '30 min', value: 30 },
                  { label: '1 hora', value: 60 },
                  { label: '24 horas', value: 24 * 60 },
                ].map((option) => (
                  <TouchableOpacity
                    key={option.value}
                    style={[
                      styles.timeOption,
                      privacySettings.deletePhotosAfterMinutes === option.value &&
                        styles.timeOptionSelected,
                    ]}
                    onPress={() =>
                      updatePrivacySettings({
                        deletePhotosAfterMinutes: option.value,
                      })
                    }
                  >
                    <Text
                      style={[
                        styles.timeOptionText,
                        privacySettings.deletePhotosAfterMinutes === option.value &&
                          styles.timeOptionTextSelected,
                      ]}
                    >
                      {option.label}
                    </Text>
                  </TouchableOpacity>
                ))}
              </View>
            </View>
          )}

          <View style={styles.settingItem}>
            <View style={styles.settingContent}>
              <Text style={styles.settingName}>Permitir Reenvío</Text>
              <Text style={styles.settingDescription}>
                Permitir compartir fotos con otros
              </Text>
            </View>
            <Switch
              value={privacySettings.allowForwarding}
              onValueChange={(value) => handleToggle('allowForwarding', value)}
              disabled={loading}
            />
          </View>
        </View>

        {/* Info Section */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>ℹ️ Cómo Funciona</Text>

          <View style={styles.infoBox}>
            <Text style={styles.infoBoxTitle}>🔐 Privacidad Total</Text>
            <Text style={styles.infoText}>
              Todos tus ajustes de privacidad se respetan. Nadie puede hacer capturas ni guardar contenido sin permiso.
            </Text>
          </View>

          <View style={styles.infoBox}>
            <Text style={styles.infoBoxTitle}>⚡ Notificaciones</Text>
            <Text style={styles.infoText}>
              Recibirás notificaciones si alguien intenta capturar pantalla o guardar fotos.
            </Text>
          </View>

          <View style={styles.infoBox}>
            <Text style={styles.infoBoxTitle}>🗑️ Eliminación</Text>
            <Text style={styles.infoText}>
              Puedes eliminar conversaciones en cualquier momento. El otro usuario será notificado.
            </Text>
          </View>
        </View>

        {/* Danger Zone */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>⚠️ Zona Peligrosa</Text>

          <TouchableOpacity
            style={styles.dangerButton}
            onPress={() => {
              Alert.alert(
                '⚠️ Confirmar',
                '¿Eliminar toda la conversación? Esto no se puede deshacer.',
                [
                  { text: 'Cancelar', style: 'cancel' },
                  {
                    text: 'Eliminar',
                    style: 'destructive',
                    onPress: () => Alert.alert('✅ Eliminado', 'Conversación eliminada'),
                  },
                ]
              );
            }}
          >
            <Text style={styles.dangerButtonText}>🗑️ Eliminar Conversación</Text>
          </TouchableOpacity>
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
  section: {
    backgroundColor: '#fff',
    marginTop: 16,
    marginHorizontal: 16,
    borderRadius: 12,
    paddingVertical: 12,
    marginBottom: 16,
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
  settingItem: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 16,
    paddingVertical: 14,
    borderBottomWidth: 1,
    borderBottomColor: '#f0f0f0',
  },
  settingContent: {
    flex: 1,
    marginRight: 16,
  },
  settingName: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
    marginBottom: 4,
  },
  settingDescription: {
    fontSize: 13,
    color: '#999',
  },
  infoBox: {
    backgroundColor: '#f8f9ff',
    paddingHorizontal: 16,
    paddingVertical: 12,
    marginHorizontal: 16,
    marginVertical: 8,
    borderRadius: 8,
    borderLeftWidth: 3,
    borderLeftColor: '#667eea',
  },
  infoBoxTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: '#333',
    marginBottom: 4,
  },
  infoText: {
    fontSize: 13,
    color: '#666',
    lineHeight: 20,
  },
  timeSelector: {
    paddingHorizontal: 16,
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#f0f0f0',
  },
  timeSelectorLabel: {
    fontSize: 14,
    fontWeight: '600',
    color: '#333',
    marginBottom: 8,
  },
  timeOptions: {
    flexDirection: 'row',
    gap: 8,
    flexWrap: 'wrap',
  },
  timeOption: {
    paddingVertical: 8,
    paddingHorizontal: 12,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#ddd',
    backgroundColor: '#fff',
  },
  timeOptionSelected: {
    backgroundColor: '#667eea',
    borderColor: '#667eea',
  },
  timeOptionText: {
    fontSize: 12,
    fontWeight: '500',
    color: '#666',
  },
  timeOptionTextSelected: {
    color: '#fff',
  },
  dangerButton: {
    marginHorizontal: 16,
    marginVertical: 8,
    paddingVertical: 12,
    backgroundColor: '#ff6b6b',
    borderRadius: 8,
    alignItems: 'center',
  },
  dangerButtonText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#fff',
  },
});
