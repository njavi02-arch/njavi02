import React from 'react';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { useTheme } from '../theme/ThemeProvider';
import type { DiscoverStackParamList } from './types';
import { DiscoverScreen } from '../screens/discover/DiscoverScreen';
import { ProfileDetailScreen } from '../screens/discover/ProfileDetailScreen';

const Stack = createNativeStackNavigator<DiscoverStackParamList>();

export function DiscoverNavigator() {
  const theme = useTheme();
  return (
    <Stack.Navigator
      screenOptions={{
        headerStyle: { backgroundColor: theme.colors.background },
        headerTintColor: theme.colors.textPrimary,
        headerShadowVisible: false,
      }}
    >
      <Stack.Screen name="DiscoverFeed" component={DiscoverScreen} options={{ headerShown: false }} />
      <Stack.Screen name="ProfileDetail" component={ProfileDetailScreen} options={{ title: '' }} />
    </Stack.Navigator>
  );
}
