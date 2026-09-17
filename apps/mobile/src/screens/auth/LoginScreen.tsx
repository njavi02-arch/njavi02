import React, { useState } from 'react';
import { ScrollView, Text } from 'react-native';
import type { NativeStackScreenProps } from '@react-navigation/native-stack';
import { useTheme } from '../../theme/ThemeProvider';
import { ScreenContainer } from '../../components/ScreenContainer';
import { TextField } from '../../components/TextField';
import { Button } from '../../components/Button';
import { signInWithEmail } from '../../services/auth';
import type { AuthStackParamList } from '../../navigation/types';

type Props = NativeStackScreenProps<AuthStackParamList, 'Login'>;

export function LoginScreen({ navigation }: Props) {
  const theme = useTheme();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit() {
    setError(null);
    setLoading(true);
    try {
      await signInWithEmail(email.trim(), password);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'No se pudo iniciar sesión');
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
          Bienvenido de vuelta
        </Text>

        <TextField
          label="Email"
          value={email}
          onChangeText={setEmail}
          autoCapitalize="none"
          keyboardType="email-address"
        />
        <TextField label="Contraseña" value={password} onChangeText={setPassword} secureTextEntry />

        {error ? (
          <Text style={{ color: theme.colors.danger, marginBottom: theme.spacing.md }}>{error}</Text>
        ) : null}

        <Button label="Iniciar sesión" onPress={handleSubmit} disabled={loading} loading={loading} />
        <Button label="Volver" onPress={() => navigation.goBack()} variant="ghost" style={{ marginTop: 8 }} />
      </ScrollView>
    </ScreenContainer>
  );
}
