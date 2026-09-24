import React, { useEffect, useMemo, useState, useCallback } from 'react';
import { Image, Pressable, ScrollView, Text, View, Animated, Easing } from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { useQueryClient } from '@tanstack/react-query';
import type { NativeStackScreenProps } from '@react-navigation/native-stack';
import { useTheme } from '../../theme/ThemeProvider';
import { ScreenContainer } from '../../components/ScreenContainer';
import { LoadingState } from '../../components/LoadingState';
import { ErrorState } from '../../components/ErrorState';
import { EmptyState } from '../../components/EmptyState';
import { Button } from '../../components/Button';
import { TextField } from '../../components/TextField';
import { ActivityBadge } from '../../components/ActivityBadge';
import { StreakAtRiskBanner } from '../../components/StreakAtRiskBanner';
import { IcebreakerChips } from '../../components/IcebreakerChips';
import { useDiscoverProfiles } from '../../hooks/useDiscoverProfiles';
import { useMyInterests } from '../../hooks/useMyInterests';
import { useAuthStore } from '../../store/authStore';
import { recordProfileView } from '../../services/discover';
import { sendConversationRequest } from '../../services/conversations';
import { sendSuperLike } from '../../services/economy';
import { useSuperLikeQuota } from '../../hooks/useSuperLikeQuota';
import type { DiscoverStackParamList } from '../../navigation/types';

type Props = NativeStackScreenProps<DiscoverStackParamList, 'DiscoverFeed'>;

function ageFromBirthDate(birthDate: string): number {
  const birth = new Date(birthDate);
  const now = new Date();
  let age = now.getFullYear() - birth.getFullYear();
  if (
    now.getMonth() < birth.getMonth() ||
    (now.getMonth() === birth.getMonth() && now.getDate() < birth.getDate())
  ) {
    age -= 1;
  }
  return age;
}

export function DiscoverScreen({ navigation }: Props) {
  const theme = useTheme();
  const session = useAuthStore((s) => s.session);
  const { data: profiles, isLoading, isError, refetch } = useDiscoverProfiles();
  const { data: myInterests } = useMyInterests();
  const queryClient = useQueryClient();
  const superLikeQuota = useSuperLikeQuota();

  const [index, setIndex] = useState(0);
  const [composerOpen, setComposerOpen] = useState(false);
  const [message, setMessage] = useState('');
  const [sending, setSending] = useState(false);
  const [feedback, setFeedback] = useState<string | null>(null);
  const cardScaleAnim = useMemo(() => new Animated.Value(1), []);

  const current = profiles?.[index] ?? null;

  useEffect(() => {
    if (current && session) {
      recordProfileView(session.user.id, current.id).catch(() => {});
    }
    setComposerOpen(false);
    setMessage('');
  }, [current?.id, session?.user.id]);

  const interestsLabel = useMemo(() => current?.interests.slice(0, 5).join(' · ') ?? '', [current]);
  const sharedInterests = useMemo(() => {
    if (!current || !myInterests) return [];
    const mine = new Set(myInterests);
    return current.interests.filter((i) => mine.has(i));
  }, [current, myInterests]);

  const goNext = useCallback(() => {
    Animated.sequence([
      Animated.timing(cardScaleAnim, {
        toValue: 0.95,
        duration: 100,
        easing: Easing.out(Easing.cubic),
        useNativeDriver: true,
      }),
      Animated.timing(cardScaleAnim, {
        toValue: 1,
        duration: 150,
        easing: Easing.out(Easing.cubic),
        useNativeDriver: true,
      }),
    ]).start();
    setIndex((i) => i + 1);
    setFeedback(null);
  }, [cardScaleAnim]);

  const handleSendMessage = useCallback(async () => {
    if (!session || !current || message.trim().length === 0) return;
    setSending(true);
    try {
      await sendConversationRequest(current.id, message.trim());
      setFeedback('¡Mensaje enviado! Te avisaremos si responde.');
      queryClient.invalidateQueries({ queryKey: ['wallets'] });
      setTimeout(goNext, 600);
    } catch (e) {
      setFeedback(e instanceof Error ? e.message : 'No se pudo enviar el mensaje');
    } finally {
      setSending(false);
    }
  }, [session, current, message, queryClient, goNext]);

  const handleSuperLike = useCallback(async () => {
    if (!session || !current) return;
    setSending(true);
    try {
      await sendSuperLike(current.id);
      setFeedback('✨ Super Like enviado');
      queryClient.invalidateQueries({ queryKey: ['wallets'] });
      queryClient.invalidateQueries({ queryKey: ['super-likes-sent-today'] });
      setTimeout(goNext, 400);
    } catch (e) {
      setFeedback(e instanceof Error ? e.message : 'No se pudo enviar el Super Like');
    } finally {
      setSending(false);
    }
  }, [session, current, queryClient, goNext]);

  if (isLoading) {
    return (
      <ScreenContainer>
        <LoadingState />
      </ScreenContainer>
    );
  }

  if (isError) {
    return (
      <ScreenContainer>
        <ErrorState onRetry={() => refetch()} />
      </ScreenContainer>
    );
  }

  if (!current) {
    return (
      <ScreenContainer>
        <EmptyState
          emoji="🔭"
          title="No hay más personas por ahora"
          description="Prueba a ampliar tu rango de distancia o edad en preferencias, o vuelve más tarde — cada día se suman nuevas personas cerca de ti."
          actionLabel="Actualizar"
          onAction={() => {
            setIndex(0);
            refetch();
          }}
        />
      </ScreenContainer>
    );
  }

  const mainPhoto = current.photos[0]?.url;

  return (
    <ScreenContainer padded={false}>
      <ScrollView contentContainerStyle={{ paddingBottom: theme.spacing.xl }}>
        <StreakAtRiskBanner onPressGoToStreak={() => navigation.getParent()?.navigate('Profile', { screen: 'Streak' })} />
        <Pressable
          onPress={() => navigation.navigate('ProfileDetail', { profileId: current.id })}
          style={{ marginHorizontal: theme.spacing.md, borderRadius: theme.radius.lg, overflow: 'hidden' }}
        >
          <View style={{ width: '100%', height: 440, backgroundColor: theme.colors.surface }}>
            {mainPhoto ? (
              <Image source={{ uri: mainPhoto }} style={{ width: '100%', height: '100%' }} resizeMode="cover" />
            ) : (
              <View style={{ flex: 1, alignItems: 'center', justifyContent: 'center' }}>
                <Text style={{ fontSize: 48 }}>👤</Text>
              </View>
            )}
            {current.isBoosted ? (
              <View
                style={{
                  position: 'absolute',
                  top: theme.spacing.sm,
                  left: theme.spacing.sm,
                  backgroundColor: theme.colors.secondary,
                  borderRadius: theme.radius.pill,
                  paddingHorizontal: 10,
                  paddingVertical: 4,
                }}
              >
                <Text style={{ color: theme.colors.onSecondary, fontSize: theme.typography.sizes.caption, fontFamily: theme.typography.fontFamilyBodySemibold }}>
                  🚀 Destacado
                </Text>
              </View>
            ) : null}
            <LinearGradient
              colors={['transparent', 'rgba(0,0,0,0.75)']}
              style={{ position: 'absolute', bottom: 0, left: 0, right: 0, height: 140, justifyContent: 'flex-end', padding: theme.spacing.md }}
            >
              <Text style={{ color: '#fff', fontFamily: theme.typography.fontFamilyHeading, fontSize: theme.typography.sizes.h1 }}>
                {current.display_name}, {ageFromBirthDate(current.birth_date)} {current.is_verified ? '✅' : ''}
              </Text>
              {current.city ? (
                <Text style={{ color: '#fff', fontFamily: theme.typography.fontFamilyBody, opacity: 0.9 }}>
                  📍 {current.city}
                </Text>
              ) : null}
              <View style={{ marginTop: 4 }}>
                <ActivityBadge lastActiveAt={current.last_active_at} light />
              </View>
            </LinearGradient>
          </View>
        </Pressable>

        <View style={{ paddingHorizontal: theme.spacing.md, marginTop: theme.spacing.md }}>
          {current.bio ? (
            <Text style={{ color: theme.colors.textPrimary, fontFamily: theme.typography.fontFamilyBody, fontSize: theme.typography.sizes.body, marginBottom: theme.spacing.sm }}>
              {current.bio}
            </Text>
          ) : null}
          {interestsLabel ? (
            <Text style={{ color: theme.colors.textSecondary, fontFamily: theme.typography.fontFamilyBodyMedium, fontSize: theme.typography.sizes.bodySmall, marginBottom: theme.spacing.sm }}>
              {interestsLabel}
            </Text>
          ) : null}
          {current.prompts.map((p) => (
            <View key={p.position} style={{ backgroundColor: theme.colors.surface, borderRadius: theme.radius.md, padding: theme.spacing.sm, marginBottom: theme.spacing.xs }}>
              <Text style={{ color: theme.colors.textSecondary, fontSize: theme.typography.sizes.caption, marginBottom: 2 }}>{p.question}</Text>
              <Text style={{ color: theme.colors.textPrimary, fontFamily: theme.typography.fontFamilyBodyMedium }}>{p.answer}</Text>
            </View>
          ))}
        </View>

        {feedback ? (
          <Text style={{ textAlign: 'center', color: theme.colors.secondary, marginTop: theme.spacing.sm, fontFamily: theme.typography.fontFamilyBodyMedium }}>
            {feedback}
          </Text>
        ) : null}

        <View style={{ paddingHorizontal: theme.spacing.md, marginTop: theme.spacing.lg }}>
          {composerOpen ? (
            <View>
              <IcebreakerChips
                otherDisplayName={current.display_name}
                sharedInterests={sharedInterests}
                otherPrompts={current.prompts}
                onSelect={setMessage}
              />
              <TextField
                placeholder={`Hola ${current.display_name}, ¿qué tal?`}
                value={message}
                onChangeText={setMessage}
                autoFocus
                multiline
              />
              <View style={{ flexDirection: 'row' }}>
                <Button label="Cancelar" variant="ghost" onPress={() => setComposerOpen(false)} fullWidth={false} style={{ marginRight: 8 }} />
                <View style={{ flex: 1 }}>
                  <Button label="Enviar" onPress={handleSendMessage} disabled={message.trim().length === 0} loading={sending} />
                </View>
              </View>
            </View>
          ) : (
            <View style={{ flexDirection: 'row' }}>
              <Button label="Pasar" variant="outline" onPress={goNext} fullWidth={false} style={{ marginRight: 8, flex: 1 }} />
              <Button
                label={superLikeQuota.isFree ? '✨' : superLikeQuota.superLikeCredits > 0 ? '✨' : `✨${superLikeQuota.coinCost}`}
                variant="secondary"
                onPress={handleSuperLike}
                fullWidth={false}
                style={{ marginRight: 8, width: superLikeQuota.isFree ? 56 : 76 }}
                disabled={sending}
              />
              <View style={{ flex: 2 }}>
                <Button label="Hablar" onPress={() => setComposerOpen(true)} />
              </View>
            </View>
          )}
        </View>
      </ScrollView>
    </ScreenContainer>
  );
}
