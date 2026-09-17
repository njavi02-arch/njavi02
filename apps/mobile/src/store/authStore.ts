import { create } from 'zustand';
import type { Session } from '@supabase/supabase-js';
import { supabase } from '../lib/supabase';
import { getMyProfile } from '../services/profiles';
import type { ProfileRow } from '../types/database';

interface AuthState {
  session: Session | null;
  profile: ProfileRow | null;
  isBootstrapping: boolean;
  setSession: (session: Session | null) => void;
  refreshProfile: () => Promise<void>;
  bootstrap: () => Promise<void>;
}

export const useAuthStore = create<AuthState>((set, get) => ({
  session: null,
  profile: null,
  isBootstrapping: true,

  setSession: (session) => set({ session }),

  refreshProfile: async () => {
    const { session } = get();
    if (!session) {
      set({ profile: null });
      return;
    }
    const profile = await getMyProfile(session.user.id);
    set({ profile });
  },

  bootstrap: async () => {
    const { data } = await supabase.auth.getSession();
    set({ session: data.session });
    if (data.session) {
      const profile = await getMyProfile(data.session.user.id);
      set({ profile });
    }
    set({ isBootstrapping: false });

    supabase.auth.onAuthStateChange(async (_event, session) => {
      set({ session });
      if (session) {
        const profile = await getMyProfile(session.user.id);
        set({ profile });
      } else {
        set({ profile: null });
      }
    });
  },
}));
