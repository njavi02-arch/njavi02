import React from 'react';
import { Text } from 'react-native';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { useTheme } from '../theme/ThemeProvider';
import type { MainTabParamList } from './types';
import { DiscoverNavigator } from './DiscoverNavigator';
import { MessagesNavigator } from './MessagesNavigator';
import { ProfileNavigator } from './ProfileNavigator';
import { ActivityScreen } from '../screens/activity/ActivityScreen';
import { useIncomingRequests } from '../hooks/useConversations';

const Tab = createBottomTabNavigator<MainTabParamList>();

const ICONS: Record<keyof MainTabParamList, string> = {
  Discover: '🧭',
  Messages: '💬',
  Activity: '⚡',
  Profile: '👤',
};

export function MainTabs() {
  const theme = useTheme();
  const { data: requests } = useIncomingRequests();
  const pendingCount = requests?.length ?? 0;

  return (
    <Tab.Navigator
      screenOptions={({ route }) => ({
        headerShown: false,
        tabBarActiveTintColor: theme.colors.primary,
        tabBarInactiveTintColor: theme.colors.textSecondary,
        tabBarStyle: { backgroundColor: theme.colors.background, borderTopColor: theme.colors.border },
        tabBarIcon: () => <Text style={{ fontSize: 20 }}>{ICONS[route.name as keyof MainTabParamList]}</Text>,
        tabBarBadge: route.name === 'Messages' && pendingCount > 0 ? pendingCount : undefined,
      })}
    >
      <Tab.Screen name="Discover" component={DiscoverNavigator} options={{ title: 'Descubrir' }} />
      <Tab.Screen name="Messages" component={MessagesNavigator} options={{ title: 'Mensajes' }} />
      <Tab.Screen name="Activity" component={ActivityScreen} options={{ title: 'Actividad' }} />
      <Tab.Screen name="Profile" component={ProfileNavigator} options={{ title: 'Perfil' }} />
    </Tab.Navigator>
  );
}
