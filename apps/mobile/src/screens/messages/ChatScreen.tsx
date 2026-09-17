import React, { useEffect, useRef, useState } from 'react';
import { Alert, FlatList, Image, KeyboardAvoidingView, Platform, Pressable, Text, View } from 'react-native';
import dayjs from 'dayjs';
import * as ImagePicker from 'expo-image-picker';
import type { NativeStackScreenProps } from '@react-navigation/native-stack';
import { useTheme } from '../../theme/ThemeProvider';
import { ScreenContainer } from '../../components/ScreenContainer';
import { LoadingState } from '../../components/LoadingState';
import { TextField } from '../../components/TextField';
import { Button } from '../../components/Button';
import { useAuthStore } from '../../store/authStore';
import {
  getConversation,
  listMessages,
  listReactions,
  markMessagesAsRead,
  reactToMessage,
  removeReaction,
  sendImageMessage,
  sendMessage,
  subscribeToConversationMessages,
  subscribeToReactions,
  subscribeToTypingPresence,
  archiveConversation,
  muteConversation,
  uploadChatImage,
} from '../../services/conversations';
import { blockUser, reportUser } from '../../services/safety';
import { REACTION_EMOJIS, type MessageReactionRow, type MessageRow } from '../../types/database';
import type { MessagesStackParamList } from '../../navigation/types';

type Props = NativeStackScreenProps<MessagesStackParamList, 'Chat'>;

export function ChatScreen({ route, navigation }: Props) {
  const theme = useTheme();
  const { conversationId, otherProfileId, otherDisplayName } = route.params;
  const session = useAuthStore((s) => s.session);
  const selfId = session?.user.id ?? '';

  const [messages, setMessages] = useState<MessageRow[]>([]);
  const [reactions, setReactions] = useState<MessageReactionRow[]>([]);
  const [pickerForMessageId, setPickerForMessageId] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [isUserA, setIsUserA] = useState<boolean | null>(null);
  const [draft, setDraft] = useState('');
  const [sending, setSending] = useState(false);
  const [sendingImage, setSendingImage] = useState(false);
  const [typingUsers, setTypingUsers] = useState<string[]>([]);
  const typingRef = useRef<{ setTyping: (t: boolean) => void; unsubscribe: () => void } | null>(null);
  const listRef = useRef<FlatList<MessageRow>>(null);
  const messageIdsRef = useRef<Set<string>>(new Set());

  useEffect(() => {
    messageIdsRef.current = new Set(messages.map((m) => m.id));
  }, [messages]);

  useEffect(() => {
    navigation.setOptions({
      title: otherDisplayName,
      headerRight: () => (
        <Pressable onPress={openMenu} hitSlop={12}>
          <Text style={{ fontSize: 20, color: theme.colors.textPrimary }}>⋯</Text>
        </Pressable>
      ),
    });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [otherDisplayName]);

  useEffect(() => {
    let mounted = true;
    listMessages(conversationId).then((data) => {
      if (mounted) {
        setMessages(data);
        setLoading(false);
        markMessagesAsRead(conversationId, selfId).catch(() => {});
      }
    });
    getConversation(conversationId).then((conversation) => {
      if (mounted) setIsUserA(conversation.user_a_id === selfId);
    });
    listReactions(conversationId).then((data) => {
      if (mounted) setReactions(data);
    });

    const unsubscribeMessages = subscribeToConversationMessages(conversationId, (message) => {
      setMessages((prev) => (prev.some((m) => m.id === message.id) ? prev : [...prev, message]));
      if (message.sender_id !== selfId) {
        markMessagesAsRead(conversationId, selfId).catch(() => {});
      }
    });

    const unsubscribeReactions = subscribeToReactions(conversationId, (event, reaction) => {
      if (event === 'DELETE') {
        setReactions((prev) => prev.filter((r) => r.id !== reaction.id));
        return;
      }
      const full = reaction as MessageReactionRow;
      if (!messageIdsRef.current.has(full.message_id)) return;
      setReactions((prev) => [...prev.filter((r) => r.id !== full.id), full]);
    });

    const typing = subscribeToTypingPresence(conversationId, selfId, setTypingUsers);
    typingRef.current = typing;

    return () => {
      mounted = false;
      unsubscribeMessages();
      unsubscribeReactions();
      typing.unsubscribe();
    };
  }, [conversationId, selfId]);

  function handleChangeDraft(text: string) {
    setDraft(text);
    typingRef.current?.setTyping(text.length > 0);
  }

  async function handleSend() {
    if (draft.trim().length === 0) return;
    const content = draft.trim();
    setDraft('');
    typingRef.current?.setTyping(false);
    setSending(true);
    try {
      await sendMessage(conversationId, selfId, content);
    } catch (e) {
      Alert.alert('No se pudo enviar', e instanceof Error ? e.message : 'Inténtalo de nuevo');
      setDraft(content);
    } finally {
      setSending(false);
    }
  }

  async function handleSendImage() {
    const permission = await ImagePicker.requestMediaLibraryPermissionsAsync();
    if (!permission.granted) return;

    const result = await ImagePicker.launchImageLibraryAsync({ mediaTypes: ['images'], quality: 0.7 });
    if (result.canceled || !result.assets[0]) return;

    setSendingImage(true);
    try {
      const imageUrl = await uploadChatImage(conversationId, selfId, result.assets[0].uri, 'image/jpeg');
      await sendImageMessage(conversationId, selfId, imageUrl);
    } catch (e) {
      Alert.alert('No se pudo enviar la foto', e instanceof Error ? e.message : 'Inténtalo de nuevo');
    } finally {
      setSendingImage(false);
    }
  }

  async function handleReact(messageId: string, emoji: (typeof REACTION_EMOJIS)[number]) {
    setPickerForMessageId(null);
    const mine = reactions.find((r) => r.message_id === messageId && r.profile_id === selfId);
    try {
      if (mine && mine.emoji === emoji) {
        setReactions((prev) => prev.filter((r) => r.id !== mine.id));
        await removeReaction(messageId, selfId);
      } else {
        const saved = await reactToMessage(messageId, selfId, emoji);
        setReactions((prev) => [...prev.filter((r) => !(r.message_id === messageId && r.profile_id === selfId)), saved]);
      }
    } catch {
      // Si falla, la suscripción Realtime/recarga siguiente reconciliará el estado real.
    }
  }

  function openMenu() {
    if (isUserA === null) return; // todavía no sabemos si somos user_a o user_b — evita
    // silenciar/archivar la mitad equivocada de la conversación (bug real corregido).
    Alert.alert(otherDisplayName, undefined, [
      {
        text: 'Silenciar',
        onPress: () => muteConversation(conversationId, isUserA, true).catch(() => {}),
      },
      {
        text: 'Bloquear',
        style: 'destructive',
        onPress: () =>
          blockUser(selfId, otherProfileId)
            .then(() => navigation.goBack())
            .catch((e) => Alert.alert('Error', e.message)),
      },
      {
        text: 'Reportar',
        onPress: () =>
          reportUser({ reporterId: selfId, reportedId: otherProfileId, reason: 'other' })
            .then(() => Alert.alert('Gracias', 'Hemos recibido tu reporte.'))
            .catch((e) => Alert.alert('Error', e.message)),
      },
      {
        text: 'Eliminar conversación',
        style: 'destructive',
        onPress: () =>
          archiveConversation(conversationId, isUserA)
            .then(() => navigation.goBack())
            .catch((e) => Alert.alert('Error', e.message)),
      },
      { text: 'Cancelar', style: 'cancel' },
    ]);
  }

  if (loading) {
    return (
      <ScreenContainer>
        <LoadingState />
      </ScreenContainer>
    );
  }

  return (
    <ScreenContainer padded={false}>
      <KeyboardAvoidingView style={{ flex: 1 }} behavior={Platform.OS === 'ios' ? 'padding' : undefined} keyboardVerticalOffset={90}>
        <FlatList
          ref={listRef}
          data={messages}
          keyExtractor={(m) => m.id}
          contentContainerStyle={{ padding: theme.spacing.md }}
          onContentSizeChange={() => listRef.current?.scrollToEnd({ animated: true })}
          renderItem={({ item }) => {
            const isMine = item.sender_id === selfId;
            if (item.message_type === 'system') {
              return (
                <Text style={{ textAlign: 'center', color: theme.colors.textSecondary, fontSize: theme.typography.sizes.caption, marginVertical: theme.spacing.sm }}>
                  {item.content}
                </Text>
              );
            }
            const isImage = item.message_type === 'image';
            const messageReactions = reactions.filter((r) => r.message_id === item.id);
            const reactionCounts = messageReactions.reduce<Record<string, number>>((acc, r) => {
              acc[r.emoji] = (acc[r.emoji] ?? 0) + 1;
              return acc;
            }, {});
            const myReactionEmoji = messageReactions.find((r) => r.profile_id === selfId)?.emoji ?? null;
            const pickerOpen = pickerForMessageId === item.id;
            return (
              <View style={{ alignSelf: isMine ? 'flex-end' : 'flex-start', maxWidth: '78%', marginBottom: 8 }}>
                <Pressable
                  onLongPress={() => setPickerForMessageId(pickerOpen ? null : item.id)}
                  style={{
                    backgroundColor: isImage ? 'transparent' : isMine ? theme.colors.primary : theme.colors.surface,
                    borderRadius: theme.radius.md,
                    borderBottomRightRadius: isMine ? 4 : theme.radius.md,
                    borderBottomLeftRadius: isMine ? theme.radius.md : 4,
                    paddingVertical: isImage ? 0 : 10,
                    paddingHorizontal: isImage ? 0 : 14,
                    overflow: 'hidden',
                  }}
                >
                  {isImage && item.image_url ? (
                    <Image source={{ uri: item.image_url }} style={{ width: 220, height: 220, borderRadius: theme.radius.md }} resizeMode="cover" />
                  ) : (
                    <Text style={{ color: isMine ? theme.colors.onPrimary : theme.colors.textPrimary }}>{item.content}</Text>
                  )}
                  <View style={{ flexDirection: 'row', justifyContent: 'flex-end', alignItems: 'center', marginTop: isImage ? 2 : 4 }}>
                    <Text
                      style={{
                        fontSize: 10,
                        color: isImage ? theme.colors.textSecondary : isMine ? theme.colors.onPrimary : theme.colors.textSecondary,
                        opacity: 0.75,
                      }}
                    >
                      {dayjs(item.created_at).format('HH:mm')}
                    </Text>
                    {isMine ? (
                      <Text
                        style={{
                          fontSize: 10,
                          marginLeft: 4,
                          color: item.status === 'read' ? theme.colors.success : isImage ? theme.colors.textSecondary : theme.colors.onPrimary,
                          opacity: item.status === 'read' ? 1 : 0.75,
                        }}
                      >
                        {item.status === 'sent' ? '✓' : '✓✓'}
                      </Text>
                    ) : null}
                  </View>
                </Pressable>

                {Object.keys(reactionCounts).length > 0 ? (
                  <View
                    style={{
                      flexDirection: 'row',
                      alignSelf: isMine ? 'flex-end' : 'flex-start',
                      backgroundColor: theme.colors.surface,
                      borderRadius: 999,
                      paddingHorizontal: 6,
                      paddingVertical: 2,
                      marginTop: -8,
                      marginRight: isMine ? 6 : 0,
                      marginLeft: isMine ? 0 : 6,
                    }}
                  >
                    {Object.entries(reactionCounts).map(([emoji, count]) => (
                      <Text key={emoji} style={{ fontSize: 12, marginHorizontal: 1 }}>
                        {emoji}
                        {count > 1 ? count : ''}
                      </Text>
                    ))}
                  </View>
                ) : null}

                {pickerOpen ? (
                  <View
                    style={{
                      flexDirection: 'row',
                      alignSelf: isMine ? 'flex-end' : 'flex-start',
                      backgroundColor: theme.colors.surface,
                      borderRadius: theme.radius.md,
                      paddingHorizontal: 8,
                      paddingVertical: 6,
                      marginTop: 4,
                      gap: 6,
                    }}
                  >
                    {REACTION_EMOJIS.map((emoji) => (
                      <Pressable key={emoji} onPress={() => handleReact(item.id, emoji)} hitSlop={4}>
                        <Text style={{ fontSize: 20, opacity: myReactionEmoji === emoji ? 1 : 0.6 }}>{emoji}</Text>
                      </Pressable>
                    ))}
                  </View>
                ) : null}
              </View>
            );
          }}
        />

        {typingUsers.length > 0 ? (
          <Text style={{ paddingHorizontal: theme.spacing.md, color: theme.colors.textSecondary, fontSize: theme.typography.sizes.caption }}>
            {otherDisplayName} está escribiendo…
          </Text>
        ) : null}

        <View style={{ flexDirection: 'row', alignItems: 'flex-end', padding: theme.spacing.md }}>
          <Button
            label="📷"
            variant="outline"
            onPress={handleSendImage}
            fullWidth={false}
            loading={sendingImage}
            style={{ width: 48, height: 48, paddingHorizontal: 0, marginRight: 8 }}
          />
          <View style={{ flex: 1, marginRight: 8 }}>
            <TextField value={draft} onChangeText={handleChangeDraft} placeholder="Escribe un mensaje…" style={{ marginBottom: 0 }} />
          </View>
          <Button label="➤" onPress={handleSend} fullWidth={false} disabled={draft.trim().length === 0} loading={sending} style={{ width: 48, height: 48, paddingHorizontal: 0 }} />
        </View>
      </KeyboardAvoidingView>
    </ScreenContainer>
  );
}
