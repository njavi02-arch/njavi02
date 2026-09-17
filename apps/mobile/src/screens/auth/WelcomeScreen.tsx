import React from 'react';
import { StyleSheet, Text, View } from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { useTheme } from '../../theme/ThemeProvider';
import { Button } from '../../components/Button';
import type { NativeStackScreenProps } from '@react-navigation/native-stack';
import type { AuthStackParamList } from '../../navigation/types';

type Props = NativeStackScreenProps<AuthStackParamList, 'Welcome'>;

export function WelcomeScreen({ navigation }: Props) {
  const theme = useTheme();

  return (
    <LinearGradient
      colors={[theme.colors.background, theme.colors.surface]}
      style={[styles.container, { paddingHorizontal: theme.spacing.lg }]}
    >
      <View style={styles.logoBlock}>
        <View
          style={[
            styles.logoCircle,
            { backgroundColor: theme.colors.primary, shadowColor: theme.colors.primary },
          ]}
        >
          <Text style={styles.logoEmoji}>🪐</Text>
        </View>
        <Text
          style={{
            fontFamily: theme.typography.fontFamilyHeading,
            fontSize: theme.typography.sizes.display,
            color: theme.colors.textPrimary,
            marginTop: theme.spacing.md,
          }}
        >
          Orbita
        </Text>
        <Text
          style={{
            fontFamily: theme.typography.fontFamilyBody,
            fontSize: theme.typography.sizes.body,
            color: theme.colors.textSecondary,
            textAlign: 'center',
            marginTop: theme.spacing.xs,
            paddingHorizontal: theme.spacing.lg,
          }}
        >
          Descubre personas cerca de ti y empieza a hablar de verdad. Amistad, conocer gente
          o algo más — tú decides.
        </Text>
      </View>

      <View style={{ marginBottom: theme.spacing.lg }}>
        <Button label="Crear cuenta" onPress={() => navigation.navigate('SignUp')} style={{ marginBottom: 12 }} />
        <Button label="Ya tengo cuenta" onPress={() => navigation.navigate('Login')} variant="outline" />
      </View>
    </LinearGradient>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, alignItems: 'center', justifyContent: 'space-between', paddingVertical: 64 },
  logoBlock: { alignItems: 'center', marginTop: 96 },
  logoCircle: {
    width: 88,
    height: 88,
    borderRadius: 44,
    alignItems: 'center',
    justifyContent: 'center',
    shadowOpacity: 0.5,
    shadowRadius: 24,
    shadowOffset: { width: 0, height: 8 },
  },
  logoEmoji: { fontSize: 40 },
});
