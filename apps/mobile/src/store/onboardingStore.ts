import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import AsyncStorage from '@react-native-async-storage/async-storage';
import type { Gender, SeekingIntent } from '@orbita/shared';

// Borrador de onboarding persistido en AsyncStorage — ver docs/04-ux-ui-flows.md §3:
// "cerrar la app a mitad de onboarding no pierde el avance". Solo se escribe de verdad
// en `profiles` (Supabase) al completar el último paso, porque display_name/birth_date
// son NOT NULL en el esquema (ver ASSUMPTIONS.md): no tiene sentido crear una fila de
// perfil a medias en la base de datos compartida.
export interface OnboardingDraft {
  step: number;
  displayName: string;
  birthDate: string | null; // YYYY-MM-DD
  gender: Gender | null;
  showMeGender: Gender[];
  seeking: SeekingIntent[];
  city: string;
  mainPhotoUri: string | null;
  bio: string;
  interestIds: string[];
  minAgePref: number;
  maxAgePref: number;
  maxDistanceKm: number;
}

const initialDraft: OnboardingDraft = {
  step: 0,
  displayName: '',
  birthDate: null,
  gender: null,
  showMeGender: ['male', 'female', 'non_binary'],
  seeking: [],
  city: '',
  mainPhotoUri: null,
  bio: '',
  interestIds: [],
  minAgePref: 18,
  maxAgePref: 55,
  maxDistanceKm: 50,
};

interface OnboardingState {
  draft: OnboardingDraft;
  setPartial: (patch: Partial<OnboardingDraft>) => void;
  nextStep: () => void;
  prevStep: () => void;
  reset: () => void;
}

export const useOnboardingStore = create<OnboardingState>()(
  persist(
    (set) => ({
      draft: initialDraft,
      setPartial: (patch) => set((s) => ({ draft: { ...s.draft, ...patch } })),
      nextStep: () => set((s) => ({ draft: { ...s.draft, step: s.draft.step + 1 } })),
      prevStep: () => set((s) => ({ draft: { ...s.draft, step: Math.max(0, s.draft.step - 1) } })),
      reset: () => set({ draft: initialDraft }),
    }),
    { name: 'orbita-onboarding-draft', storage: createJSONStorage(() => AsyncStorage) },
  ),
);
