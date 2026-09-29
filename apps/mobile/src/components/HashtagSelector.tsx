import React, { useState } from 'react';
import { Text, View, Pressable, ScrollView } from 'react-native';
import { useTheme } from '../theme/ThemeProvider';

const HASHTAGS = [
  // ACCIÓN FÍSICA
  '#Besos', '#Morder', '#Arañar', '#Masaje', '#Juegos', '#Caricias',
  '#Sexting', '#Lencería', '#Privado', '#Noche', '#Público', '#Exploración',
  // TIPO DE RELACIÓN
  '#Citas', '#SinCompromiso', '#RelaciónAbierta', '#Parejas',
  '#Solteros', '#Amistad', '#Conexión', '#Química',
  // INTENSIDAD
  '#Dominación', '#Sumisión', '#Roleplay', '#Fantasías', '#Suave', '#Intenso',
  // PERFIL ESPECÍFICO
  '#Individual', '#Pareja', '#Buscando', '#Experimental',
  // MOTIVACIÓN
  '#Encuentros', '#Conocer', '#Flirtear', '#Diversión', '#Serio',
];

interface HashtagSelectorProps {
  selected?: string[];
  onChange: (hashtags: string[]) => void;
  maxTags?: number;
}

export function HashtagSelector({ selected = [], onChange, maxTags = 10 }: HashtagSelectorProps) {
  const theme = useTheme();
  const isFull = selected.length >= maxTags;

  const toggleHashtag = (tag: string) => {
    if (selected.includes(tag)) {
      onChange(selected.filter((t) => t !== tag));
    } else if (!isFull) {
      onChange([...selected, tag]);
    }
  };

  const categories = [
    { name: 'Acción Física', tags: HASHTAGS.slice(0, 12) },
    { name: 'Tipo de Relación', tags: HASHTAGS.slice(12, 20) },
    { name: 'Intensidad', tags: HASHTAGS.slice(20, 26) },
    { name: 'Perfil', tags: HASHTAGS.slice(26, 30) },
    { name: 'Motivación', tags: HASHTAGS.slice(30, 35) },
  ];

  return (
    <View>
      <Text style={{ fontFamily: theme.typography.fontFamilyBodySemibold, fontSize: 14, color: theme.colors.textSecondary, marginBottom: theme.spacing.sm }}>
        Selecciona {selected.length}/{maxTags} hashtags
      </Text>

      <ScrollView showsVerticalScrollIndicator={false} scrollEventThrottle={16} style={{ maxHeight: 500 }}>
        {categories.map((category) => (
          <View key={category.name} style={{ marginBottom: theme.spacing.lg }}>
            <Text style={{ fontFamily: theme.typography.fontFamilyBodySemibold, fontSize: 12, color: theme.colors.textSecondary, marginBottom: theme.spacing.xs, textTransform: 'uppercase' }}>
              {category.name}
            </Text>
            <View style={{ flexDirection: 'row', flexWrap: 'wrap', gap: theme.spacing.xs }}>
              {category.tags.map((tag) => {
                const isSelected = selected.includes(tag);
                return (
                  <Pressable
                    key={tag}
                    onPress={() => toggleHashtag(tag)}
                    disabled={isFull && !isSelected}
                    style={{
                      paddingHorizontal: theme.spacing.sm,
                      paddingVertical: theme.spacing.xs,
                      borderRadius: theme.radius.full,
                      backgroundColor: isSelected ? theme.colors.primary : theme.colors.surface,
                      borderWidth: 1,
                      borderColor: isSelected ? theme.colors.primary : theme.colors.border,
                      opacity: isFull && !isSelected ? 0.5 : 1,
                    }}
                  >
                    <Text
                      style={{
                        fontFamily: theme.typography.fontFamilyBody,
                        fontSize: 12,
                        color: isSelected ? '#fff' : theme.colors.textPrimary,
                      }}
                    >
                      {tag}
                    </Text>
                  </Pressable>
                );
              })}
            </View>
          </View>
        ))}
      </ScrollView>
    </View>
  );
}
