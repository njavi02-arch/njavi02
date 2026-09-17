import React from 'react';
import { ScrollView, View } from 'react-native';
import { suggestIcebreakers, type ProfilePromptLike } from '@orbita/shared';
import { Chip } from './Chip';
import { useTheme } from '../theme/ThemeProvider';

interface IcebreakerChipsProps {
  otherDisplayName: string;
  sharedInterests: string[];
  otherPrompts: ProfilePromptLike[];
  onSelect: (text: string) => void;
}

/** Sugerencias de primer mensaje — ver PRODUCT_BRAIN.md (inspirado en el problema que
 * resuelven Icebreaker/Opening Move de Bumble y los Prompts de Hinge, sin copiarlos: aquí
 * son deterministas, sin IA generativa de terceros). Tocar una sugerencia la escribe en el
 * composer; el usuario puede editarla antes de enviar. */
export function IcebreakerChips({ otherDisplayName, sharedInterests, otherPrompts, onSelect }: IcebreakerChipsProps) {
  const theme = useTheme();
  const suggestions = suggestIcebreakers(otherDisplayName, sharedInterests, otherPrompts);

  if (suggestions.length === 0) return null;

  return (
    <ScrollView horizontal showsHorizontalScrollIndicator={false} style={{ marginBottom: theme.spacing.sm }}>
      <View style={{ flexDirection: 'row' }}>
        {suggestions.map((s) => (
          <Chip key={s.text} label={s.text.length > 40 ? `${s.text.slice(0, 40)}…` : s.text} onPress={() => onSelect(s.text)} />
        ))}
      </View>
    </ScrollView>
  );
}
