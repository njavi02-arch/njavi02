import React, { useState } from 'react';
import { ScrollView, Text } from 'react-native';
import type { NativeStackScreenProps } from '@react-navigation/native-stack';
import { useTheme } from '../../theme/ThemeProvider';
import { ScreenContainer } from '../../components/ScreenContainer';
import { TextField } from '../../components/TextField';
import { Button } from '../../components/Button';
import { signUpWithEmail } from '../../services/auth';
import type { AuthStackParamList } from '../../navigation/types';

type Props = NativeStackScreenProps<AuthStackParamList, 'SignUp'>;

export function SignUpScreen({ navigation }: Props) {
  const theme = useTheme();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const emailValid = /\S+@\S+\.\S+/.test(email);
  const passwordValid = password.length >= 8;
  const canSubmit = emailValid && passwordValid && !loading;

  async function handleSubmit() {
    setError(null);
    setLoading(true);
    try {
      await signUpWithEmail(email.trim(), password);
      // El listener de authStore recoge la sesión y RootNavigator pasa a Onboarding
      // automáticamente al no encontrar perfil todavía.
    } catch (e) {
      setError(e instanceof Error ? e.message : 'No se pudo crear la cuenta');
    } finally {
      setLoading(false);
    }
  }

  return (
    <ScreenContainer>
      <ScrollView keyboardShouldPersistTaps="handled" contentContainerStyle={{ paddingTop: theme.spacing.xl }}>
        <Text
          style={{
            fontFamily: theme.typography.fontFamilyHeading,
            fontSize: theme.typography.sizes.h1,
            color: theme.colors.textPrimary,
            marginBottom: theme.spacing.lg,
          }}
        >
          Crea tu cuenta
        </Text>

        <TextField
          label="Email"
          value={email}
          onChangeText={setEmail}
          autoCapitalize="none"
          keyboardType="email-address"
          placeholder="tu@email.com"
        />
        <TextField
          label="Contraseña (mínimo 8 caracteres)"
          value={password}
          onChangeText={setPassword}
          secureTextEntry
          placeholder="••••••••"
        />

        {error ? (
          <Text style={{ color: theme.colors.danger, marginBottom: theme.spacing.md }}>{error}</Text>
        ) : null}

        <Button label="Continuar" onPress={handleSubmit} disabled={!canSubmit} loading={loading} />
        <Button label="Volver" onPress={() => navigation.goBack()} variant="ghost" style={{ marginTop: 8 }} />

        <Text
          style={{
            color: theme.colors.textSecondary,
            fontSize: theme.typography.sizes.caption,
            marginTop: theme.spacing.lg,
            textAlign: 'center',
          }}
        >
          Debes ser mayor de 18 años para usar Orbita. Al continuar aceptas los{' '}
          <Text style={{ color: theme.colors.primary }} onPress={() => navigation.navigate('Terms')}>
            Términos
          </Text>{' '}
          y la{' '}
          <Text style={{ color: theme.colors.primary }} onPress={() => navigation.navigate('Privacy')}>
            Política de Privacidad
          </Text>
          .
        </Text>
      </ScrollView>
    </ScreenContainer>
  );
}
