import React from 'react';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { useTheme } from '../theme/ThemeProvider';
import type { ProfileStackParamList } from './types';
import { MyProfileScreen } from '../screens/profile/MyProfileScreen';
import { EditProfileScreen } from '../screens/profile/EditProfileScreen';
import { WalletScreen } from '../screens/profile/WalletScreen';
import { StreakScreen } from '../screens/profile/StreakScreen';
import { PremiumScreen } from '../screens/profile/PremiumScreen';
import { SettingsScreen } from '../screens/profile/SettingsScreen';

const Stack = createNativeStackNavigator<ProfileStackParamList>();

export function ProfileNavigator() {
  const theme = useTheme();
  return (
    <Stack.Navigator
      screenOptions={{
        headerStyle: { backgroundColor: theme.colors.background },
        headerTintColor: theme.colors.textPrimary,
        headerShadowVisible: false,
      }}
    >
      <Stack.Screen name="MyProfile" component={MyProfileScreen} options={{ headerShown: false }} />
      <Stack.Screen name="EditProfile" component={EditProfileScreen} options={{ title: '' }} />
      <Stack.Screen name="Wallet" component={WalletScreen} options={{ title: '' }} />
      <Stack.Screen name="Streak" component={StreakScreen} options={{ title: '' }} />
      <Stack.Screen name="Premium" component={PremiumScreen} options={{ title: '' }} />
      <Stack.Screen name="Settings" component={SettingsScreen} options={{ title: '' }} />
    </Stack.Navigator>
  );
}
