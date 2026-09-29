import React, { useState } from 'react';
import { Text, View, ScrollView } from 'react-native';
import { useTheme } from '../../../theme/ThemeProvider';
import { Button } from '../../../components/Button';
import { HashtagSelector } from '../../../components/HashtagSelector';

interface StepHashtagsProps {
  hashtags: string[];
  onChange: (hashtags: string[]) => void;
  onNext: () => void;
  isLoading?: boolean;
}

export function StepHashtags({ hashtags, onChange, onNext, isLoading }: StepHashtagsProps) {
  const theme = useTheme();

  return (
    <View style={{ flex: 1 }}>
      <ScrollView contentContainerStyle={{ paddingTop: theme.spacing.lg, paddingHorizontal: theme.spacing.md, paddingBottom: theme.spacing.xl }}>
        <Text style={{ fontFamily: theme.typography.fontFamilyHeading, fontSize: theme.typography.sizes.h2, color: theme.colors.textPrimary, marginBottom: theme.spacing.md }}>
          Tus intereses 🏷️
        </Text>

        <Text style={{ fontFamily: theme.typography.fontFamilyBody, fontSize: 14, color: theme.colors.textSecondary, marginBottom: theme.spacing.lg }}>
          Selecciona de 1 a 10 hashtags que mejor te describan. Esto ayuda a encontrar personas más compatibles.
        </Text>

        <View style={{ marginBottom: theme.spacing.xl }}>
          <HashtagSelector selected={hashtags} onChange={onChange} />
        </View>

        {hashtags.length > 0 && (
          <View style={{ backgroundColor: theme.colors.surface, borderRadius: theme.radius.md, padding: theme.spacing.md, marginBottom: theme.spacing.lg }}>
            <Text style={{ fontFamily: theme.typography.fontFamilyBodySemibold, fontSize: 12, color: theme.colors.textSecondary, textTransform: 'uppercase', marginBottom: theme.spacing.sm }}>
              Seleccionados
            </Text>
            <View style={{ flexDirection: 'row', flexWrap: 'wrap', gap: theme.spacing.xs }}>
              {hashtags.map((tag) => (
                <View key={tag} style={{ backgroundColor: theme.colors.primary, borderRadius: theme.radius.full, paddingHorizontal: theme.spacing.sm, paddingVertical: 4 }}>
                  <Text style={{ fontFamily: theme.typography.fontFamilyBody, fontSize: 12, color: '#fff' }}>
                    {tag}
                  </Text>
                </View>
              ))}
            </View>
          </View>
        )}
      </ScrollView>

      <View style={{ paddingHorizontal: theme.spacing.md, paddingBottom: theme.spacing.lg, gap: theme.spacing.sm }}>
        <Button
          label="Continuar"
          onPress={onNext}
          disabled={hashtags.length === 0}
          isLoading={isLoading}
        />
        <Button
          label="Omitir"
          variant="secondary"
          onPress={onNext}
        />
      </View>
    </View>
  );
}
