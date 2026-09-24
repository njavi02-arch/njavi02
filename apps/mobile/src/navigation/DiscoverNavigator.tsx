import React from 'react';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { useTheme } from '../theme/ThemeProvider';
import type { DiscoverStackParamList } from './types';
import { DiscoverScreen } from '../screens/discover/DiscoverScreen';
import { ProfileDetailScreen } from '../screens/discover/ProfileDetailScreen';
import { CommunityScreen } from '../screens/community/CommunityScreen';
import { CreatePostScreen } from '../screens/community/CreatePostScreen';
import { HashtagFeedScreen } from '../screens/community/HashtagFeedScreen';
import { PostDetailScreen } from '../screens/community/PostDetailScreen';

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
      <Stack.Screen name="Community" component={CommunityScreen} options={{ headerShown: false }} />
      <Stack.Screen name="CreatePost" component={CreatePostScreen} options={{ headerShown: false }} />
      <Stack.Screen name="HashtagFeed" component={HashtagFeedScreen} options={{ title: '', headerShown: false }} />
      <Stack.Screen name="PostDetail" component={PostDetailScreen} options={{ title: '', headerShown: false }} />
    </Stack.Navigator>
  );
}
