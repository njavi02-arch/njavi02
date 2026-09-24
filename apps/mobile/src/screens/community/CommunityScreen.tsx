import React, { useState } from 'react';
import { ActivityIndicator, FlatList, Image, Pressable, RefreshControl, ScrollView, Text, View } from 'react-native';
import { useQuery, useInfiniteQuery } from '@tanstack/react-query';
import { useTheme } from '../../theme/ThemeProvider';
import { ScreenContainer } from '../../components/ScreenContainer';
import { Button } from '../../components/Button';
import { LoadingState } from '../../components/LoadingState';
import { EmptyState } from '../../components/EmptyState';
import { listHashtags, getPostsForFeed } from '../../services/community';
import type { HashtagRow, PostWithAuthor } from '../../types/database';
import type { NativeStackScreenProps } from '@react-navigation/native-stack';
import type { CommunityStackParamList } from '../../navigation/types';

type Props = NativeStackScreenProps<CommunityStackParamList, 'CommunityFeed'>;

export function CommunityScreen({ navigation }: Props) {
  const theme = useTheme();
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);

  const { data: hashtags = [], isLoading: hashtagsLoading } = useQuery({
    queryKey: ['hashtags'],
    queryFn: listHashtags,
  });

  const { data: postsData, isLoading: postsLoading, refetch: refetchPosts, hasNextPage, fetchNextPage } = useInfiniteQuery({
    queryKey: ['posts-feed'],
    queryFn: ({ pageParam = 0 }) => getPostsForFeed(20, pageParam),
    getNextPageParam: (lastPage, pages) => {
      return lastPage.length === 20 ? pages.length * 20 : undefined;
    },
    initialPageParam: 0,
  });

  const posts = postsData?.pages.flatMap((page) => page) || [];
  const categories = [...new Set(hashtags.map((h) => h.category))];

  const handleRefresh = async () => {
    await refetchPosts();
  };

  return (
    <ScreenContainer>
      <FlatList
        ListHeaderComponent={
          <View>
            {/* Header */}
            <View
              style={{
                flexDirection: 'row',
                justifyContent: 'space-between',
                alignItems: 'center',
                marginBottom: theme.spacing.lg,
              }}
            >
              <Text
                style={{
                  fontSize: theme.typography.sizes.h1,
                  fontFamily: theme.typography.fontFamilyHeading,
                  color: theme.colors.textPrimary,
                }}
              >
                🌎 Comunidad
              </Text>
              <Pressable
                onPress={() => navigation.navigate('CreatePost')}
                style={{
                  backgroundColor: theme.colors.primary,
                  borderRadius: theme.radius.pill,
                  width: 44,
                  height: 44,
                  justifyContent: 'center',
                  alignItems: 'center',
                }}
              >
                <Text style={{ fontSize: 20 }}>+</Text>
              </Pressable>
            </View>

            {/* Categories */}
            <Text
              style={{
                fontSize: 12,
                color: theme.colors.textSecondary,
                marginBottom: theme.spacing.sm,
                textTransform: 'uppercase',
              }}
            >
              Categorías
            </Text>
            <ScrollView
              horizontal
              showsHorizontalScrollIndicator={false}
              contentContainerStyle={{ gap: theme.spacing.sm, marginBottom: theme.spacing.lg }}
            >
              <Pressable
                onPress={() => setSelectedCategory(null)}
                style={{
                  paddingHorizontal: theme.spacing.md,
                  paddingVertical: theme.spacing.sm,
                  borderRadius: theme.radius.pill,
                  backgroundColor: selectedCategory === null ? theme.colors.primary : theme.colors.surface,
                  borderWidth: 1,
                  borderColor: selectedCategory === null ? 'transparent' : theme.colors.border,
                }}
              >
                <Text
                  style={{
                    color: selectedCategory === null ? theme.colors.onPrimary : theme.colors.textPrimary,
                    fontSize: 14,
                    fontFamily: theme.typography.fontFamilyBodySemibold,
                  }}
                >
                  Todos
                </Text>
              </Pressable>
              {categories.map((category) => (
                <Pressable
                  key={category}
                  onPress={() => setSelectedCategory(category)}
                  style={{
                    paddingHorizontal: theme.spacing.md,
                    paddingVertical: theme.spacing.sm,
                    borderRadius: theme.radius.pill,
                    backgroundColor: selectedCategory === category ? theme.colors.primary : theme.colors.surface,
                    borderWidth: 1,
                    borderColor: selectedCategory === category ? 'transparent' : theme.colors.border,
                  }}
                >
                  <Text
                    style={{
                      color: selectedCategory === category ? theme.colors.onPrimary : theme.colors.textPrimary,
                      fontSize: 14,
                      fontFamily: theme.typography.fontFamilyBodySemibold,
                    }}
                  >
                    {category}
                  </Text>
                </Pressable>
              ))}
            </ScrollView>

            {/* Featured Hashtags */}
            <Text
              style={{
                fontSize: 12,
                color: theme.colors.textSecondary,
                marginBottom: theme.spacing.sm,
                textTransform: 'uppercase',
              }}
            >
              Tendencias
            </Text>
            <View style={{ flexDirection: 'row', flexWrap: 'wrap', gap: theme.spacing.sm, marginBottom: theme.spacing.lg }}>
              {hashtags.slice(0, 6).map((tag) => (
                <Pressable
                  key={tag.id}
                  onPress={() => navigation.navigate('HashtagFeed', { hashtagId: tag.id, hashtagName: tag.name })}
                  style={{
                    backgroundColor: theme.colors.surfaceElevated,
                    paddingHorizontal: theme.spacing.md,
                    paddingVertical: theme.spacing.xs,
                    borderRadius: theme.radius.pill,
                    borderWidth: 1,
                    borderColor: theme.colors.primary,
                  }}
                >
                  <Text
                    style={{
                      color: theme.colors.primary,
                      fontSize: 13,
                      fontFamily: theme.typography.fontFamilyBodySemibold,
                    }}
                  >
                    #{tag.name}
                  </Text>
                </Pressable>
              ))}
            </View>

            {/* Posts Header */}
            <Text
              style={{
                fontSize: 14,
                color: theme.colors.textSecondary,
                marginBottom: theme.spacing.md,
                textTransform: 'uppercase',
              }}
            >
              Feed
            </Text>
          </View>
        }
        data={posts}
        renderItem={({ item: post }) => <PostCard post={post} navigation={navigation} />}
        keyExtractor={(item) => item.id}
        onEndReached={() => {
          if (hasNextPage) {
            fetchNextPage();
          }
        }}
        onEndReachedThreshold={0.3}
        ListEmptyComponent={postsLoading ? <LoadingState /> : <EmptyState emoji="📝" title="Sin publicaciones" description="Sé el primero en compartir algo" actionLabel="Crear publicación" onAction={() => navigation.navigate('CreatePost')} />}
        refreshControl={<RefreshControl refreshing={postsLoading} onRefresh={handleRefresh} />}
        contentContainerStyle={{ paddingBottom: theme.spacing.xl }}
      />
    </ScreenContainer>
  );
}

function PostCard({ post, navigation }: { post: PostWithAuthor; navigation: any }) {
  const theme = useTheme();

  return (
    <Pressable
      onPress={() => navigation.navigate('PostDetail', { postId: post.id })}
      style={{
        backgroundColor: theme.colors.surface,
        borderRadius: theme.radius.lg,
        overflow: 'hidden',
        marginBottom: theme.spacing.md,
      }}
    >
      {/* Author info */}
      <View style={{ flexDirection: 'row', alignItems: 'center', padding: theme.spacing.md }}>
        {post.author && (
          <>
            <Image
              source={{ uri: 'https://via.placeholder.com/40' }}
              style={{ width: 40, height: 40, borderRadius: 20, marginRight: theme.spacing.sm }}
            />
            <View style={{ flex: 1 }}>
              <Text style={{ color: theme.colors.textPrimary, fontFamily: theme.typography.fontFamilyBodySemibold }}>
                {post.author.display_name}
              </Text>
              <Text style={{ color: theme.colors.textSecondary, fontSize: 12 }}>
                {new Date(post.created_at).toLocaleDateString()}
              </Text>
            </View>
          </>
        )}
      </View>

      {/* Content */}
      <View style={{ paddingHorizontal: theme.spacing.md, marginBottom: theme.spacing.sm }}>
        <Text style={{ color: theme.colors.textPrimary, fontSize: 15, lineHeight: 22 }}>
          {post.content}
        </Text>
      </View>

      {/* Media */}
      {post.media_urls && post.media_urls.length > 0 && (
        <Image
          source={{ uri: post.media_urls[0] }}
          style={{ width: '100%', height: 200, backgroundColor: theme.colors.skeleton }}
        />
      )}

      {/* Hashtags */}
      {post.hashtags && post.hashtags.length > 0 && (
        <View style={{ flexDirection: 'row', flexWrap: 'wrap', gap: 6, paddingHorizontal: theme.spacing.md, marginTop: theme.spacing.sm, marginBottom: theme.spacing.md }}>
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
          paddingHorizontal: theme.spacing.md,
          paddingBottom: theme.spacing.md,
          borderTopWidth: 1,
          borderTopColor: theme.colors.border,
          paddingTop: theme.spacing.sm,
        }}
      >
        <Text style={{ color: theme.colors.textSecondary, fontSize: 12 }}>
          ❤️ {post.likes_count}
        </Text>
        <Text style={{ color: theme.colors.textSecondary, fontSize: 12 }}>
          💬 {post.comments_count}
        </Text>
      </View>
    </Pressable>
  );
}
