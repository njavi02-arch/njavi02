// Identidad visual propia de Orbita — ver docs/04-ux-ui-flows.md §1.
// Ningún color/tipografía se hardcodea en pantallas: todo pasa por aquí.

export const palette = {
  coralAurora: '#FF5D73',
  coralAuroraDark: '#E3475C',
  violetNebula: '#8B7CFF',
  violetNebulaDark: '#6E5CE0',
  successGreen: '#3DDC97',
  warningAmber: '#FFB648',
  dangerRed: '#FF4D4D',
  white: '#FFFFFF',
  black: '#000000',
  ink900: '#0B0B12',
  ink800: '#15151F',
  ink700: '#1E1E2B',
  ink600: '#2A2A3A',
  ink500: '#3D3D52',
  grey400: '#6B6B7D',
  grey300: '#9494A6',
  grey200: '#C7C7D4',
  grey100: '#E5E5EC',
  grey50: '#F4F4F8',
} as const;

export interface ThemeColors {
  background: string;
  surface: string;
  surfaceElevated: string;
  border: string;
  textPrimary: string;
  textSecondary: string;
  textInverse: string;
  primary: string;
  primaryPressed: string;
  onPrimary: string;
  secondary: string;
  secondaryPressed: string;
  onSecondary: string;
  success: string;
  warning: string;
  danger: string;
  overlay: string;
  skeleton: string;
}

export const darkColors: ThemeColors = {
  background: palette.ink900,
  surface: palette.ink800,
  surfaceElevated: palette.ink700,
  border: palette.ink600,
  textPrimary: palette.white,
  textSecondary: palette.grey300,
  textInverse: palette.ink900,
  primary: palette.coralAurora,
  primaryPressed: palette.coralAuroraDark,
  onPrimary: palette.white,
  secondary: palette.violetNebula,
  secondaryPressed: palette.violetNebulaDark,
  onSecondary: palette.white,
  success: palette.successGreen,
  warning: palette.warningAmber,
  danger: palette.dangerRed,
  overlay: 'rgba(11, 11, 18, 0.72)',
  skeleton: palette.ink600,
};

export const lightColors: ThemeColors = {
  background: palette.white,
  surface: palette.grey50,
  surfaceElevated: palette.white,
  border: palette.grey100,
  textPrimary: palette.ink900,
  textSecondary: palette.grey400,
  textInverse: palette.white,
  primary: palette.coralAurora,
  primaryPressed: palette.coralAuroraDark,
  onPrimary: palette.white,
  secondary: palette.violetNebula,
  secondaryPressed: palette.violetNebulaDark,
  onSecondary: palette.white,
  success: '#1FA976',
  warning: '#C97E00',
  danger: '#D93131',
  overlay: 'rgba(11, 11, 18, 0.55)',
  skeleton: palette.grey100,
};

export const spacing = {
  xxs: 4,
  xs: 8,
  sm: 12,
  md: 16,
  lg: 24,
  xl: 32,
  xxl: 48,
} as const;

export const radius = {
  sm: 12,
  md: 20,
  lg: 28,
  pill: 999,
} as const;

export const typography = {
  fontFamilyHeading: 'Sora_700Bold',
  fontFamilyHeadingSemibold: 'Sora_600SemiBold',
  fontFamilyBody: 'Inter_400Regular',
  fontFamilyBodyMedium: 'Inter_500Medium',
  fontFamilyBodySemibold: 'Inter_600SemiBold',
  sizes: {
    display: 32,
    h1: 26,
    h2: 22,
    h3: 18,
    body: 15,
    bodySmall: 13,
    caption: 12,
  },
} as const;

export const shadow = {
  card: {
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 8 },
    shadowOpacity: 0.18,
    shadowRadius: 16,
    elevation: 6,
  },
} as const;
