import React from 'react';
import { FlatList, RefreshControl, Text, View } from 'react-native';
import { useInfiniteQuery } from '@tanstack/react-query';
import { useTheme } from '../../theme/ThemeProvider';
import { ScreenContainer } from '../../components/ScreenContainer';
import { LoadingState } from '../../components/LoadingState';
import { EmptyState } from '../../components/EmptyState';
import { getPostsByHashtag } from '../../services/community';
import type { PostWithAuthor } from '../../types/database';
import type { NativeStackScreenProps } from '@react-navigation/native-stack';
import type { DiscoverStackParamList } from '../../navigation/types';

type Props = NativeStackScreenProps<DiscoverStackParamList, 'HashtagFeed'>;

export function HashtagFeedScreen({ route, navigation }: Props) {
  const theme = useTheme();
  const { hashtagId, hashtagName } = route.params;

  const { data: postsData, isLoading: postsLoading, refetch: refetchPosts, hasNextPage, fetchNextPage } = useInfiniteQuery({
    queryKey: ['hashtag-feed', hashtagId],
    queryFn: ({ pageParam = 0 }) => getPostsByHashtag(hashtagId, 20, pageParam),
    getNextPageParam: (lastPage, pages) => {
      return lastPage.length === 20 ? pages.length * 20 : undefined;
    },
    initialPageParam: 0,
  });

  const posts = postsData?.pages.flatMap((page) => page) || [];

  const handleRefresh = async () => {
    await refetchPosts();
  };

  return (
    <ScreenContainer>
      <FlatList
        ListHeaderComponent={
          <View style={{ marginBottom: theme.spacing.lg }}>
            <Text
              style={{
                fontSize: theme.typography.sizes.h2,
                fontFamily: theme.typography.fontFamilyHeading,
                color: theme.colors.textPrimary,
              }}
            >
              #{hashtagName}
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
        ListEmptyComponent={postsLoading ? <LoadingState /> : <EmptyState emoji="📝" title="Sin publicaciones" description="Sé el primero en compartir en este hashtag" actionLabel="Crear publicación" onAction={() => navigation.navigate('CreatePost')} />}
        refreshControl={<RefreshControl refreshing={postsLoading} onRefresh={handleRefresh} />}
        contentContainerStyle={{ paddingBottom: theme.spacing.xl }}
      />
    </ScreenContainer>
  );
}

function PostCard({ post, navigation }: { post: PostWithAuthor; navigation: any }) {
  const theme = useTheme();

  return (
    <View
      onTouchEnd={() => navigation.navigate('PostDetail', { postId: post.id })}
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
          <View style={{ flex: 1 }}>
            <Text style={{ color: theme.colors.textPrimary, fontFamily: theme.typography.fontFamilyBodySemibold }}>
              {post.author.display_name}
            </Text>
            <Text style={{ color: theme.colors.textSecondary, fontSize: 12 }}>
              {new Date(post.created_at).toLocaleDateString()}
            </Text>
          </View>
        )}
      </View>

      {/* Content */}
      <View style={{ paddingHorizontal: theme.spacing.md, marginBottom: theme.spacing.sm }}>
        <Text style={{ color: theme.colors.textPrimary, fontSize: 15, lineHeight: 22 }}>
          {post.content}
        </Text>
      </View>

      {/* Stats */}
      <View
        style={{
          flexDirection: 'row',
          justifyContent: 'space-between',
          paddingHorizontal: theme.spacing.md,
          paddingVertical: theme.spacing.md,
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
  );
}
