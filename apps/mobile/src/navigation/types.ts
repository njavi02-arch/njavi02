export type AuthStackParamList = {
  Welcome: undefined;
  SignUp: undefined;
  Login: undefined;
};

export type OnboardingStackParamList = {
  Onboarding: undefined;
};

export type MainTabParamList = {
  Discover: undefined;
  Messages: undefined;
  Activity: undefined;
  Profile: undefined;
};

export type MessagesStackParamList = {
  MessagesList: undefined;
  Requests: undefined;
  Chat: { conversationId: string; otherProfileId: string; otherDisplayName: string };
};

export type DiscoverStackParamList = {
  DiscoverFeed: undefined;
  ProfileDetail: { profileId: string };
};

export type ProfileStackParamList = {
  MyProfile: undefined;
  EditProfile: undefined;
  Wallet: undefined;
  Streak: undefined;
  Premium: undefined;
  Settings: undefined;
};

export type RootStackParamList = {
  Auth: undefined;
  Onboarding: undefined;
  Main: undefined;
};
