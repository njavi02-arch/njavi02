import React, { useState } from 'react';
import { FlatList, Image, KeyboardAvoidingView, Platform, Pressable, Text, TextInput, View } from 'react-native';
import { useQuery } from '@tanstack/react-query';
import { useTheme } from '../../theme/ThemeProvider';
import { ScreenContainer } from '../../components/ScreenContainer';
import { LoadingState } from '../../components/LoadingState';
import { getPostsForFeed, getCommentsForPost, addComment } from '../../services/community';
import type { PostWithAuthor, CommentWithAuthor } from '../../types/database';
import type { NativeStackScreenProps } from '@react-navigation/native-stack';
import type { DiscoverStackParamList } from '../../navigation/types';

type Props = NativeStackScreenProps<DiscoverStackParamList, 'PostDetail'>;

export function PostDetailScreen({ route, navigation }: Props) {
  const theme = useTheme();
  const { postId } = route.params;
  const [commentText, setCommentText] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const { data: posts = [] } = useQuery({
    queryKey: ['posts-detail', postId],
    queryFn: async () => {
      const allPosts = await getPostsForFeed(100, 0);
      return allPosts.filter((p) => p.id === postId);
    },
  });

  const { data: comments = [], refetch: refetchComments } = useQuery({
    queryKey: ['comments', postId],
    queryFn: () => getCommentsForPost(postId),
  });

  const post = posts[0];

  const handleAddComment = async () => {
    if (!commentText.trim()) return;

    setIsSubmitting(true);
    try {
      await addComment(postId, commentText);
      setCommentText('');
      await refetchComments();
    } catch (error) {
      console.error('Error adding comment:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  if (!post) {
    return (
      <ScreenContainer>
        <LoadingState />
      </ScreenContainer>
    );
  }

  return (
    <KeyboardAvoidingView behavior={Platform.OS === 'ios' ? 'padding' : 'height'} style={{ flex: 1 }}>
      <ScreenContainer>
        <FlatList
          ListHeaderComponent={<PostView post={post} />}
          data={comments}
          renderItem={({ item: comment }) => <CommentCard comment={comment} />}
          keyExtractor={(item) => item.id}
          contentContainerStyle={{ paddingBottom: theme.spacing.xl }}
          ListEmptyComponent={<Text style={{ color: theme.colors.textSecondary, textAlign: 'center', marginTop: theme.spacing.lg }}>Sin comentarios aún</Text>}
        />
        <View
          style={{
            flexDirection: 'row',
            gap: theme.spacing.sm,
            padding: theme.spacing.md,
            borderTopWidth: 1,
            borderTopColor: theme.colors.border,
          }}
        >
          <TextInput
            placeholder="Añade un comentario..."
            placeholderTextColor={theme.colors.textSecondary}
            value={commentText}
            onChangeText={setCommentText}
            style={{
              flex: 1,
              backgroundColor: theme.colors.surface,
              borderRadius: theme.radius.pill,
              paddingHorizontal: theme.spacing.md,
              paddingVertical: theme.spacing.sm,
              color: theme.colors.textPrimary,
            }}
          />
          <Pressable
            onPress={handleAddComment}
            disabled={!commentText.trim() || isSubmitting}
            style={{
              backgroundColor: theme.colors.primary,
              borderRadius: theme.radius.pill,
              paddingHorizontal: theme.spacing.md,
              paddingVertical: theme.spacing.sm,
              justifyContent: 'center',
              opacity: !commentText.trim() || isSubmitting ? 0.5 : 1,
            }}
          >
            <Text style={{ color: theme.colors.onPrimary, fontSize: 16 }}>→</Text>
          </Pressable>
        </View>
      </ScreenContainer>
    </KeyboardAvoidingView>
  );
}

function PostView({ post }: { post: PostWithAuthor }) {
  const theme = useTheme();

  return (
    <View style={{ marginBottom: theme.spacing.lg }}>
      <View style={{ backgroundColor: theme.colors.surface, borderRadius: theme.radius.lg, padding: theme.spacing.md }}>
        {/* Author info */}
        {post.author && (
          <View style={{ flexDirection: 'row', alignItems: 'center', marginBottom: theme.spacing.md }}>
            <View style={{ flex: 1 }}>
              <Text style={{ color: theme.colors.textPrimary, fontFamily: theme.typography.fontFamilyBodySemibold }}>
                {post.author.display_name}
              </Text>
              <Text style={{ color: theme.colors.textSecondary, fontSize: 12 }}>
                {new Date(post.created_at).toLocaleDateString()}
              </Text>
            </View>
          </View>
        )}

        {/* Content */}
        <Text style={{ color: theme.colors.textPrimary, fontSize: 15, lineHeight: 22, marginBottom: theme.spacing.md }}>
          {post.content}
        </Text>

        {/* Media */}
        {post.media_urls && post.media_urls.length > 0 && (
          <Image
            source={{ uri: post.media_urls[0] }}
            style={{ width: '100%', height: 200, borderRadius: theme.radius.lg, marginBottom: theme.spacing.md }}
          />
        )}

        {/* Hashtags */}
        {post.hashtags && post.hashtags.length > 0 && (
          <View style={{ flexDirection: 'row', flexWrap: 'wrap', gap: 6, marginBottom: theme.spacing.md }}>
            {post.hashtags.map((tag) => (
              <Text key={tag.id} style={{ color: theme.colors.primary, fontSize: 13 }}>
                #{tag.name}
              </Text>
            ))}
          </View>
        )}

        {/* Stats */}
        <View
          style={{
            flexDirection: 'row',
            justifyContent: 'space-between',
            paddingTop: theme.spacing.md,
            borderTopWidth: 1,
            borderTopColor: theme.colors.border,
          }}
        >
          <Text style={{ color: theme.colors.textSecondary, fontSize: 12 }}>
            ❤️ {post.likes_count}
          </Text>
          <Text style={{ color: theme.colors.textSecondary, fontSize: 12 }}>
            💬 {post.comments_count}
          </Text>
        </View>
      </View>
    </View>
  );
}

function CommentCard({ comment }: { comment: CommentWithAuthor }) {
  const theme = useTheme();

  return (
    <View style={{ paddingHorizontal: theme.spacing.md, paddingVertical: theme.spacing.sm, borderBottomWidth: 1, borderBottomColor: theme.colors.border }}>
      {comment.author && (
        <Text style={{ color: theme.colors.textPrimary, fontFamily: theme.typography.fontFamilyBodySemibold, fontSize: 13 }}>
          {comment.author.display_name}
        </Text>
      )}
      <Text style={{ color: theme.colors.textPrimary, fontSize: 13, marginTop: theme.spacing.xs }}>
        {comment.content}
      </Text>
      <Text style={{ color: theme.colors.textSecondary, fontSize: 11, marginTop: theme.spacing.xs }}>
        {new Date(comment.created_at).toLocaleDateString()}
      </Text>
    </View>
  );
}
