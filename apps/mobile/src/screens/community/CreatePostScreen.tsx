import React, { useState } from 'react';
import { Alert, Pressable, ScrollView, Text, TextInput, View } from 'react-native';
import { useQuery } from '@tanstack/react-query';
import { useTheme } from '../../theme/ThemeProvider';
import { ScreenContainer } from '../../components/ScreenContainer';
import { Button } from '../../components/Button';
import { listHashtags, createPost } from '../../services/community';
import { useAuthStore } from '../../store/authStore';
import type { NativeStackScreenProps } from '@react-navigation/native-stack';
import type { CommunityStackParamList } from '../../navigation/types';

type Props = NativeStackScreenProps<CommunityStackParamList, 'CreatePost'>;

export function CreatePostScreen({ navigation }: Props) {
  const theme = useTheme();
  const [content, setContent] = useState('');
  const [selectedHashtags, setSelectedHashtags] = useState<string[]>([]);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const { data: hashtags = [] } = useQuery({
    queryKey: ['hashtags'],
    queryFn: listHashtags,
  });

  const categories = [...new Set(hashtags.map((h) => h.category))];

  const handleCreatePost = async () => {
    if (!content.trim()) {
      Alert.alert('Error', 'Escribe algo para compartir');
      return;
    }

    setIsSubmitting(true);
    try {
      await createPost(content, undefined, selectedHashtags);
      Alert.alert('✅ Publicado', 'Tu publicación se ha compartido');
      navigation.goBack();
    } catch (error) {
      Alert.alert('Error', 'No se pudo crear la publicación');
    } finally {
      setIsSubmitting(false);
    }
  };

  const toggleHashtag = (hashtagId: string) => {
    setSelectedHashtags((prev) =>
      prev.includes(hashtagId)
        ? prev.filter((id) => id !== hashtagId)
        : [...prev, hashtagId]
    );
  };

  return (
    <ScreenContainer>
      <ScrollView contentContainerStyle={{ paddingBottom: theme.spacing.xl }}>
        {/* Header */}
        <View style={{ flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: theme.spacing.lg }}>
          <Text
            style={{
              fontSize: theme.typography.sizes.h2,
              fontFamily: theme.typography.fontFamilyHeading,
              color: theme.colors.textPrimary,
            }}
          >
            Crear Publicación
          </Text>
          <Pressable onPress={() => navigation.goBack()}>
            <Text style={{ fontSize: 20 }}>✕</Text>
          </Pressable>
        </View>

        {/* Content Input */}
        <View
          style={{
            backgroundColor: theme.colors.surface,
            borderRadius: theme.radius.lg,
            padding: theme.spacing.md,
            marginBottom: theme.spacing.lg,
            borderWidth: 1,
            borderColor: theme.colors.border,
            minHeight: 120,
          }}
        >
          <TextInput
            placeholder="¿Qué quieres compartir?"
            placeholderTextColor={theme.colors.textSecondary}
            value={content}
            onChangeText={setContent}
            multiline
            numberOfLines={4}
            style={{
              color: theme.colors.textPrimary,
              fontSize: 15,
              fontFamily: theme.typography.fontFamilyBody,
              textAlignVertical: 'top',
            }}
          />
        </View>

        {/* Character count */}
        <Text
          style={{
            color: theme.colors.textSecondary,
            fontSize: 12,
            marginBottom: theme.spacing.lg,
            alignSelf: 'flex-end',
          }}
        >
          {content.length}/500
        </Text>

        {/* Hashtags Section */}
        <Text
          style={{
            fontSize: 14,
            fontFamily: theme.typography.fontFamilyBodySemibold,
            color: theme.colors.textPrimary,
            marginBottom: theme.spacing.md,
          }}
        >
          Añade Hashtags
        </Text>

        {categories.map((category) => (
          <View key={category} style={{ marginBottom: theme.spacing.lg }}>
            <Text
              style={{
                fontSize: 12,
                color: theme.colors.textSecondary,
                textTransform: 'uppercase',
                marginBottom: theme.spacing.sm,
              }}
            >
              {category}
            </Text>
            <View style={{ flexDirection: 'row', flexWrap: 'wrap', gap: theme.spacing.sm }}>
              {hashtags
                .filter((h) => h.category === category)
                .map((hashtag) => (
                  <Pressable
                    key={hashtag.id}
                    onPress={() => toggleHashtag(hashtag.id)}
                    style={{
                      paddingHorizontal: theme.spacing.md,
                      paddingVertical: theme.spacing.sm,
                      borderRadius: theme.radius.pill,
                      backgroundColor: selectedHashtags.includes(hashtag.id)
                        ? theme.colors.primary
                        : theme.colors.surface,
                      borderWidth: 1,
                      borderColor: selectedHashtags.includes(hashtag.id)
                        ? 'transparent'
                        : theme.colors.border,
                    }}
                  >
                    <Text
                      style={{
                        color: selectedHashtags.includes(hashtag.id)
                          ? theme.colors.onPrimary
                          : theme.colors.textPrimary,
                        fontSize: 13,
                      }}
                    >
                      #{hashtag.name}
                    </Text>
                  </Pressable>
                ))}
            </View>
          </View>
        ))}

        {/* Selected hashtags preview */}
        {selectedHashtags.length > 0 && (
          <View
            style={{
              backgroundColor: theme.colors.primary,
              borderRadius: theme.radius.lg,
              padding: theme.spacing.md,
              marginTop: theme.spacing.lg,
              marginBottom: theme.spacing.lg,
            }}
          >
            <Text
              style={{
                color: theme.colors.onPrimary,
                fontSize: 12,
                marginBottom: theme.spacing.sm,
              }}
            >
              {selectedHashtags.length} hashtag{selectedHashtags.length !== 1 ? 's' : ''} seleccionado{selectedHashtags.length !== 1 ? 's' : ''}
            </Text>
            <View style={{ flexDirection: 'row', flexWrap: 'wrap', gap: theme.spacing.sm }}>
              {hashtags
                .filter((h) => selectedHashtags.includes(h.id))
                .map((tag) => (
                  <Text key={tag.id} style={{ color: theme.colors.onPrimary, fontSize: 13 }}>
                    #{tag.name}
                  </Text>
                ))}
            </View>
          </View>
        )}

        {/* Action Buttons */}
        <View style={{ gap: theme.spacing.sm }}>
          <Button
            label={isSubmitting ? 'Publicando...' : 'Publicar'}
            onPress={handleCreatePost}
            loading={isSubmitting}
            disabled={!content.trim() || isSubmitting}
            fullWidth
          />
          <Button
            label="Cancelar"
            onPress={() => navigation.goBack()}
            variant="outline"
            fullWidth
          />
        </View>
      </ScrollView>
    </ScreenContainer>
  );
}
