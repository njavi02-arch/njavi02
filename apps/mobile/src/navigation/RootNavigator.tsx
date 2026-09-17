import React, { useEffect } from 'react';
import { NavigationContainer, DarkTheme, DefaultTheme } from '@react-navigation/native';
import { useTheme } from '../theme/ThemeProvider';
import { useAuthStore } from '../store/authStore';
import { LoadingState } from '../components/LoadingState';
import { AuthNavigator } from './AuthNavigator';
import { MainTabs } from './MainTabs';
import { OnboardingScreen } from '../screens/onboarding/OnboardingScreen';

export function RootNavigator() {
  const theme = useTheme();
  const { session, profile, isBootstrapping, bootstrap } = useAuthStore();

  useEffect(() => {
    bootstrap();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const navTheme = {
    ...(theme.scheme === 'dark' ? DarkTheme : DefaultTheme),
    colors: {
      ...(theme.scheme === 'dark' ? DarkTheme.colors : DefaultTheme.colors),
      background: theme.colors.background,
      card: theme.colors.background,
      text: theme.colors.textPrimary,
      border: theme.colors.border,
      primary: theme.colors.primary,
    },
  };

  if (isBootstrapping) {
    return <LoadingState />;
  }

  return (
    <NavigationContainer theme={navTheme}>
      {!session ? <AuthNavigator /> : !profile ? <OnboardingScreen /> : <MainTabs />}
    </NavigationContainer>
  );
}
