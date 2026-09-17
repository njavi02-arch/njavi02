import React from 'react';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { useTheme } from '../theme/ThemeProvider';
import type { MessagesStackParamList } from './types';
import { MessagesListScreen } from '../screens/messages/MessagesListScreen';
import { RequestsScreen } from '../screens/messages/RequestsScreen';
import { ChatScreen } from '../screens/messages/ChatScreen';

const Stack = createNativeStackNavigator<MessagesStackParamList>();

export function MessagesNavigator() {
  const theme = useTheme();
  return (
    <Stack.Navigator
      screenOptions={{
        headerStyle: { backgroundColor: theme.colors.background },
        headerTintColor: theme.colors.textPrimary,
        headerShadowVisible: false,
      }}
    >
      <Stack.Screen name="MessagesList" component={MessagesListScreen} options={{ headerShown: false }} />
      <Stack.Screen name="Requests" component={RequestsScreen} options={{ headerShown: false }} />
      <Stack.Screen name="Chat" component={ChatScreen} options={{ title: '' }} />
    </Stack.Navigator>
  );
}
