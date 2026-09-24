export type AuthStackParamList = {
  Welcome: undefined;
  SignUp: undefined;
  Login: undefined;
  Terms: undefined;
  Privacy: undefined;
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
  Community: undefined;
  CreatePost: undefined;
  HashtagFeed: { hashtagId: string; hashtagName: string };
  PostDetail: { postId: string };
};

export type ProfileStackParamList = {
  MyProfile: undefined;
  EditProfile: undefined;
  Wallet: undefined;
  Streak: undefined;
  Premium: undefined;
  Settings: undefined;
  BlockedUsers: undefined;
  VerifyProfile: undefined;
  Terms: undefined;
  Privacy: undefined;
};

export type RootStackParamList = {
  Auth: undefined;
  Onboarding: undefined;
  Main: undefined;
};
