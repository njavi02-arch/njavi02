import { useQuery, useMutation } from '@tanstack/react-query';
import { useAuthStore } from '../store/authStore';

const API_BASE = 'http://localhost:3001/api/v2';

export interface V2Profile {
  id: string;
  name: string;
  age: number;
  hashtags: string[];
  compatibilityScore: number;
  distance: number;
  photos: string[];
  bio?: string;
}

export interface V2DiscoverResponse {
  profiles: V2Profile[];
  total: number;
  limit: number;
  offset: number;
}

export interface UserPreferences {
  min_age: number;
  max_age: number;
  gender_preference: string[];
  max_distance_km: number;
  preferred_hashtags: string[];
  show_verified_only: boolean;
}

export function useV2DiscoverFeed(limit = 10, offset = 0) {
  const session = useAuthStore((s) => s.session);

  return useQuery<V2DiscoverResponse>({
    queryKey: ['v2-discover-feed', limit, offset],
    queryFn: async () => {
      if (!session) throw new Error('Not authenticated');

      const response = await fetch(`${API_BASE}/discover/feed?limit=${limit}&offset=${offset}`, {
        headers: {
          Authorization: `Bearer ${session.access_token}`,
        },
      });

      if (!response.ok) throw new Error('Failed to fetch discovery feed');
      return response.json();
    },
    enabled: !!session,
  });
}

export function useUserPreferences() {
  const session = useAuthStore((s) => s.session);

  return useQuery<UserPreferences>({
    queryKey: ['user-preferences'],
    queryFn: async () => {
      if (!session) throw new Error('Not authenticated');

      const response = await fetch(`${API_BASE}/profiles/me/preferences`, {
        headers: {
          Authorization: `Bearer ${session.access_token}`,
        },
      });

      if (!response.ok) throw new Error('Failed to fetch preferences');
      return response.json();
    },
    enabled: !!session,
  });
}

export function useUpdateUserPreferences() {
  const session = useAuthStore((s) => s.session);

  return useMutation({
    mutationFn: async (preferences: UserPreferences) => {
      if (!session) throw new Error('Not authenticated');

      const response = await fetch(`${API_BASE}/profiles/me/preferences`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${session.access_token}`,
        },
        body: JSON.stringify(preferences),
      });

      if (!response.ok) throw new Error('Failed to update preferences');
      return response.json();
    },
  });
}

export function useUserHashtags() {
  const session = useAuthStore((s) => s.session);

  return useQuery<{ hashtags: string[] }>({
    queryKey: ['user-hashtags'],
    queryFn: async () => {
      if (!session) throw new Error('Not authenticated');

      // For now, try to get from preferences; in real app would be separate endpoint
      const response = await fetch(`${API_BASE}/profiles/me/preferences`, {
        headers: {
          Authorization: `Bearer ${session.access_token}`,
        },
      });

      if (!response.ok) throw new Error('Failed to fetch hashtags');
      const data = await response.json();
      return { hashtags: data.preferred_hashtags || [] };
    },
    enabled: !!session,
  });
}

export function useUpdateUserHashtags() {
  const session = useAuthStore((s) => s.session);

  return useMutation({
    mutationFn: async (hashtags: string[]) => {
      if (!session) throw new Error('Not authenticated');

      const response = await fetch(`${API_BASE}/profiles/me/hashtags`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${session.access_token}`,
        },
        body: JSON.stringify({ hashtags }),
      });

      if (!response.ok) throw new Error('Failed to update hashtags');
      return response.json();
    },
  });
}

export function useAvailableHashtags() {
  return useQuery<{ hashtags: string[] }>({
    queryKey: ['available-hashtags'],
    queryFn: async () => {
      const response = await fetch(`${API_BASE}/hashtags/all`);
      if (!response.ok) throw new Error('Failed to fetch hashtags');
      return response.json();
    },
  });
}

export function usePremiumSubscription() {
  const session = useAuthStore((s) => s.session);

  return useQuery<{ isPremium: boolean; subscription?: any }>({
    queryKey: ['premium-subscription'],
    queryFn: async () => {
      if (!session) throw new Error('Not authenticated');

      const response = await fetch(`${API_BASE}/subscriptions`, {
        headers: {
          Authorization: `Bearer ${session.access_token}`,
        },
      });

      if (!response.ok) throw new Error('Failed to fetch subscription');
      return response.json();
    },
    enabled: !!session,
  });
}

export function useActivateBoost() {
  const session = useAuthStore((s) => s.session);

  return useMutation({
    mutationFn: async () => {
      if (!session) throw new Error('Not authenticated');

      const response = await fetch(`${API_BASE}/boosts`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${session.access_token}`,
        },
      });

      if (!response.ok) throw new Error('Failed to activate boost');
      return response.json();
    },
  });
}
