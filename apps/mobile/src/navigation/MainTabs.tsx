import React from 'react';
import { Text } from 'react-native';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { useTheme } from '../theme/ThemeProvider';
import type { MainTabParamList, CommunityStackParamList } from './types';
import { DiscoverNavigator } from './DiscoverNavigator';
import { MessagesNavigator } from './MessagesNavigator';
import { ProfileNavigator } from './ProfileNavigator';
import { CommunityScreen } from '../screens/community/CommunityScreen';
import { CreatePostScreen } from '../screens/community/CreatePostScreen';
import { HashtagFeedScreen } from '../screens/community/HashtagFeedScreen';
import { PostDetailScreen } from '../screens/community/PostDetailScreen';
import { ActivityScreen } from '../screens/activity/ActivityScreen';
import { useIncomingRequests } from '../hooks/useConversations';
import { useRegisterPushNotifications } from '../hooks/useRegisterPushNotifications';
import { useNotifications } from '../hooks/useNotifications';
import { useTrackActivity } from '../hooks/useTrackActivity';

const Tab = createBottomTabNavigator<MainTabParamList>();
const CommunityStackNav = createNativeStackNavigator<CommunityStackParamList>();

function CommunityNavigator() {
  const theme = useTheme();
  return (
    <CommunityStackNav.Navigator
      screenOptions={{
        headerStyle: { backgroundColor: theme.colors.background },
        headerTintColor: theme.colors.textPrimary,
        headerShadowVisible: false,
      }}
    >
      <CommunityStackNav.Screen name="CommunityFeed" component={CommunityScreen} options={{ headerShown: false }} />
      <CommunityStackNav.Screen name="CreatePost" component={CreatePostScreen} options={{ headerShown: false }} />
      <CommunityStackNav.Screen name="HashtagFeed" component={HashtagFeedScreen} options={{ title: '', headerShown: false }} />
      <CommunityStackNav.Screen name="PostDetail" component={PostDetailScreen} options={{ title: '', headerShown: false }} />
    </CommunityStackNav.Navigator>
  );
}

const ICONS: Record<keyof MainTabParamList, string> = {
  Discover: '🧭',
  Community: '🌎',
  Messages: '💬',
  Activity: '⚡',
  Profile: '👤',
};

export function MainTabs() {
  const theme = useTheme();
  const { data: requests } = useIncomingRequests();
  const pendingCount = requests?.length ?? 0;
  const { data: notifications } = useNotifications();
  const unreadNotifications = notifications?.filter((n) => !n.is_read).length ?? 0;
  useRegisterPushNotifications();
  useTrackActivity();

  return (
    <Tab.Navigator
      screenOptions={({ route }) => ({
        headerShown: false,
        tabBarActiveTintColor: theme.colors.primary,
        tabBarInactiveTintColor: theme.colors.textSecondary,
        tabBarStyle: { backgroundColor: theme.colors.background, borderTopColor: theme.colors.border },
        tabBarIcon: () => <Text style={{ fontSize: 20 }}>{ICONS[route.name as keyof MainTabParamList]}</Text>,
        tabBarBadge:
          route.name === 'Messages' && pendingCount > 0
            ? pendingCount
            : route.name === 'Activity' && unreadNotifications > 0
              ? unreadNotifications
              : undefined,
      })}
    >
      <Tab.Screen name="Discover" component={DiscoverNavigator} options={{ title: 'Descubrir' }} />
      <Tab.Screen name="Community" component={CommunityNavigator} options={{ title: 'Comunidad' }} />
      <Tab.Screen name="Messages" component={MessagesNavigator} options={{ title: 'Mensajes' }} />
      <Tab.Screen name="Activity" component={ActivityScreen} options={{ title: 'Actividad' }} />
      <Tab.Screen name="Profile" component={ProfileNavigator} options={{ title: 'Perfil' }} />
    </Tab.Navigator>
  );
}
