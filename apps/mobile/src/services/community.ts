import { supabase } from '../lib/supabase';
import type { PostWithAuthor, CommentWithAuthor, HashtagRow, IcebreakerPackRow, InteractionTrackingRow } from '../types/database';

// ===== HASHTAGS =====
export async function listHashtags(): Promise<HashtagRow[]> {
  const { data, error } = await supabase
    .from('hashtags')
    .select('*')
    .order('name');

  if (error) throw error;
  return data || [];
}

export async function getHashtagsByCategory(category: string): Promise<HashtagRow[]> {
  const { data, error } = await supabase
    .from('hashtags')
    .select('*')
    .eq('category', category)
    .order('name');

  if (error) throw error;
  return data || [];
}

export async function followHashtag(hashtagId: string): Promise<void> {
  const { error } = await supabase
    .from('hashtag_followers')
    .insert({ hashtag_id: hashtagId });

  if (error) throw error;
}

export async function unfollowHashtag(hashtagId: string): Promise<void> {
  const { error } = await supabase
    .from('hashtag_followers')
    .delete()
    .eq('hashtag_id', hashtagId);

  if (error) throw error;
}

export async function getUserFollowedHashtags(userId: string): Promise<HashtagRow[]> {
  const { data, error } = await supabase
    .from('hashtag_followers')
    .select('hashtag_id, hashtags(*)')
    .eq('user_id', userId);

  if (error) throw error;
  return data?.map((row: any) => row.hashtags) || [];
}

// ===== POSTS =====
export async function createPost(content: string, mediaUrls?: string[], hashtagIds?: string[]): Promise<string> {
  const { data, error } = await supabase
    .from('posts')
    .insert({
      content,
      media_urls: mediaUrls || null,
    })
    .select('id')
    .single();

  if (error) throw error;

  const postId = data.id;

  // Add hashtags if provided
  if (hashtagIds && hashtagIds.length > 0) {
    const { error: tagError } = await supabase
      .from('post_hashtags')
      .insert(hashtagIds.map((hid) => ({ post_id: postId, hashtag_id: hid })));

    if (tagError) throw tagError;
  }

  return postId;
}

export async function getPostsForFeed(limit = 20, offset = 0): Promise<PostWithAuthor[]> {
  const { data, error } = await supabase
    .from('posts')
    .select(`
      *,
      author:profiles(*),
      post_hashtags(hashtag_id, hashtags(*)),
      post_likes(liker_id)
    `)
    .eq('is_archived', false)
    .order('created_at', { ascending: false })
    .range(offset, offset + limit - 1);

  if (error) throw error;

  // Transform to PostWithAuthor
  const currentUserId = (await supabase.auth.getUser()).data.user?.id;
  return (data || []).map((post: any) => ({
    ...post,
    hashtags: post.post_hashtags.map((ph: any) => ph.hashtags).filter(Boolean),
    liked_by_me: post.post_likes.some((l: any) => l.liker_id === currentUserId),
  }));
}

export async function getPostsByHashtag(hashtagId: string, limit = 20, offset = 0): Promise<PostWithAuthor[]> {
  const { data, error } = await supabase
    .from('post_hashtags')
    .select(`
      posts(
        *,
        author:profiles(*),
        post_hashtags(hashtag_id, hashtags(*))
      )
    `)
    .eq('hashtag_id', hashtagId)
    .order('posts(created_at)', { ascending: false })
    .range(offset, offset + limit - 1);

  if (error) throw error;

  const currentUserId = (await supabase.auth.getUser()).data.user?.id;
  return (data || [])
    .map((row: any) => row.posts)
    .filter(Boolean)
    .map((post: any) => ({
      ...post,
      hashtags: post.post_hashtags.map((ph: any) => ph.hashtags).filter(Boolean),
      liked_by_me: false, // Will be updated if needed
    }));
}

export async function getPostsByAuthor(authorId: string, limit = 20, offset = 0): Promise<PostWithAuthor[]> {
  const { data, error } = await supabase
    .from('posts')
    .select(`
      *,
      author:profiles(*),
      post_hashtags(hashtag_id, hashtags(*))
    `)
    .eq('author_id', authorId)
    .eq('is_archived', false)
    .order('created_at', { ascending: false })
    .range(offset, offset + limit - 1);

  if (error) throw error;

  const currentUserId = (await supabase.auth.getUser()).data.user?.id;
  return (data || []).map((post: any) => ({
    ...post,
    hashtags: post.post_hashtags.map((ph: any) => ph.hashtags).filter(Boolean),
    liked_by_me: post.post_likes?.some((l: any) => l.liker_id === currentUserId) || false,
  }));
}

export async function deletePost(postId: string): Promise<void> {
  const { error } = await supabase
    .from('posts')
    .update({ is_archived: true })
    .eq('id', postId);

  if (error) throw error;
}

// ===== POST LIKES =====
export async function likePost(postId: string): Promise<void> {
  const { error } = await supabase
    .from('post_likes')
    .insert({ post_id: postId });

  if (error) throw error;

  // Increment likes_count
  await supabase.rpc('increment_post_likes', { post_id: postId });
}

export async function unlikePost(postId: string): Promise<void> {
  const { error } = await supabase
    .from('post_likes')
    .delete()
    .match({ post_id: postId });

  if (error) throw error;

  // Decrement likes_count
  await supabase.rpc('decrement_post_likes', { post_id: postId });
}

export async function getPostLikesCount(postId: string): Promise<number> {
  const { count, error } = await supabase
    .from('post_likes')
    .select('*', { count: 'exact', head: true })
    .eq('post_id', postId);

  if (error) throw error;
  return count || 0;
}

// ===== COMMENTS =====
export async function addComment(postId: string, content: string): Promise<string> {
  const { data, error } = await supabase
    .from('comments')
    .insert({
      post_id: postId,
      content,
    })
    .select('id')
    .single();

  if (error) throw error;

  // Increment comments_count on post
  await supabase.rpc('increment_post_comments', { post_id: postId });

  return data.id;
}

export async function getCommentsForPost(postId: string, limit = 50): Promise<CommentWithAuthor[]> {
  const { data, error } = await supabase
    .from('comments')
    .select(`
      *,
      author:profiles(*)
    `)
    .eq('post_id', postId)
    .order('created_at', { ascending: true })
    .limit(limit);

  if (error) throw error;

  const currentUserId = (await supabase.auth.getUser()).data.user?.id;
  return (data || []).map((comment: any) => ({
    ...comment,
    liked_by_me: false, // Will be updated if needed
  }));
}

export async function deleteComment(commentId: string): Promise<void> {
  const { error } = await supabase
    .from('comments')
    .delete()
    .eq('id', commentId);

  if (error) throw error;
}

// ===== COMMENT LIKES =====
export async function likeComment(commentId: string): Promise<void> {
  const { error } = await supabase
    .from('comment_likes')
    .insert({ comment_id: commentId });

  if (error) throw error;

  await supabase.rpc('increment_comment_likes', { comment_id: commentId });
}

export async function unlikeComment(commentId: string): Promise<void> {
  const { error } = await supabase
    .from('comment_likes')
    .delete()
    .eq('comment_id', commentId);

  if (error) throw error;

  await supabase.rpc('decrement_comment_likes', { comment_id: commentId });
}

// ===== ICEBREAKER PACKS =====
export async function getAllIcebreakerPacks(): Promise<IcebreakerPackRow[]> {
  const { data, error } = await supabase
    .from('icebreaker_packs')
    .select('*')
    .order('pack_number');

  if (error) throw error;
  return data || [];
}

export async function getIcebreakerPackForUser(userId: string): Promise<IcebreakerPackRow | null> {
  // Get interaction tracking
  const tracking = await getInteractionTracking(userId);
  if (!tracking) {
    // Initialize tracking
    await initializeInteractionTracking(userId);
    const allPacks = await getAllIcebreakerPacks();
    return allPacks[0] || null;
  }

  // Get current pack
  const allPacks = await getAllIcebreakerPacks();
  const currentPack = allPacks.find((p) => p.pack_number === tracking.current_pack);

  if (!currentPack && allPacks.length > 0) {
    // If pack doesn't exist, wrap around
    return allPacks[0];
  }

  return currentPack || null;
}

export async function getRandomPhrasesFromPack(packId: string, count = 4): Promise<string[]> {
  const { data, error } = await supabase
    .from('icebreaker_packs')
    .select('phrases')
    .eq('id', packId)
    .single();

  if (error) throw error;

  const phrases = data?.phrases || [];
  // Return random phrases
  const shuffled = [...phrases].sort(() => Math.random() - 0.5);
  return shuffled.slice(0, Math.min(count, shuffled.length));
}

// ===== INTERACTION TRACKING =====
export async function getInteractionTracking(userId: string): Promise<InteractionTrackingRow | null> {
  const { data, error } = await supabase
    .from('interaction_tracking')
    .select('*')
    .eq('user_id', userId)
    .single();

  if (error && error.code !== 'PGRST116') throw error;
  return data || null;
}

export async function initializeInteractionTracking(userId: string): Promise<void> {
  const { error } = await supabase
    .from('interaction_tracking')
    .insert({
      user_id: userId,
      total_interactions: 0,
      current_pack: 1,
    });

  if (error && error.code !== '23505') throw error; // 23505 = unique constraint
}

export async function recordInteraction(userId: string): Promise<void> {
  const tracking = await getInteractionTracking(userId);

  if (!tracking) {
    await initializeInteractionTracking(userId);
    return;
  }

  const newCount = tracking.total_interactions + 1;
  const allPacks = await getAllIcebreakerPacks();
  const packSize = 40; // Rotate every 40 interactions
  const newPackNumber = Math.floor(newCount / packSize) % allPacks.length;
  const nextPackNumber = newPackNumber + 1 > allPacks.length ? 1 : newPackNumber + 1;

  const { error } = await supabase
    .from('interaction_tracking')
    .update({
      total_interactions: newCount,
      current_pack: nextPackNumber,
      last_pack_rotation: newCount % packSize === 0 ? new Date().toISOString() : tracking.last_pack_rotation,
    })
    .eq('user_id', userId);

  if (error) throw error;
}
