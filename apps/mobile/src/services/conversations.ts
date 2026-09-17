import { supabase } from '../lib/supabase';
import type { ConversationRequestRow, ConversationRow, MessageRow, ProfileRow } from '../types/database';

/**
 * Envía una solicitud de conversación ("Hablar"). Llama a create_conversation_request()
 * (supabase/migrations/0002_atomic_actions.sql), una función SECURITY DEFINER que hace
 * en una sola transacción atómica del lado del servidor: comprobar bloqueo, filtrar
 * palabras prohibidas, aplicar el cooldown de 30 días tras un rechazo, comprobar el rate
 * limit anti-spam, gastar el crédito de mensaje y crear la solicitud + su notificación.
 * Sin esto, un fallo de red a mitad de las dos llamadas de red que hacía antes esta
 * función podía crear una solicitud sin cobrar el crédito; ahora es todo o nada.
 */
export async function sendConversationRequest(
  receiverId: string,
  firstMessage: string,
): Promise<ConversationRequestRow> {
  const { data, error } = await supabase.rpc('create_conversation_request', {
    p_receiver_id: receiverId,
    p_first_message: firstMessage,
  });
  if (error) throw error;
  return data as ConversationRequestRow;
}

export interface IncomingRequest extends ConversationRequestRow {
  sender: Pick<ProfileRow, 'id' | 'display_name'> & { photo_url: string | null };
}

export async function listIncomingRequests(receiverId: string): Promise<IncomingRequest[]> {
  const { data, error } = await supabase
    .from('conversation_requests')
    .select('*, sender:profiles!conversation_requests_sender_id_fkey(id, display_name, photos(url, position))')
    .eq('receiver_id', receiverId)
    .eq('status', 'pending')
    .order('created_at', { ascending: false });
  if (error) throw error;

  return (data ?? []).map((row: any) => ({
    ...row,
    sender: {
      id: row.sender.id,
      display_name: row.sender.display_name,
      photo_url:
        [...(row.sender.photos ?? [])].sort((a: any, b: any) => a.position - b.position)[0]?.url ?? null,
    },
  }));
}

export async function acceptConversationRequest(requestId: string): Promise<string> {
  const { data, error } = await supabase.rpc('accept_conversation_request', { p_request_id: requestId });
  if (error) throw error;
  return data as string;
}

export async function declineConversationRequest(requestId: string): Promise<void> {
  const { error } = await supabase.rpc('decline_conversation_request', { p_request_id: requestId });
  if (error) throw error;
}

export interface ConversationSummary extends ConversationRow {
  otherProfile: Pick<ProfileRow, 'id' | 'display_name'> & { photo_url: string | null };
  lastMessage: Pick<MessageRow, 'content' | 'message_type' | 'sender_id' | 'created_at'> | null;
  unreadCount: number;
}

export async function listConversations(currentUserId: string): Promise<ConversationSummary[]> {
  const { data, error } = await supabase
    .from('conversations')
    .select(
      `*,
       user_a:profiles!conversations_user_a_id_fkey(id, display_name, photos(url, position)),
       user_b:profiles!conversations_user_b_id_fkey(id, display_name, photos(url, position)),
       messages(content, message_type, sender_id, created_at, status)`,
    )
    .or(`user_a_id.eq.${currentUserId},user_b_id.eq.${currentUserId}`)
    .order('last_message_at', { ascending: false });

  if (error) throw error;

  return (data ?? []).map((row: any) => {
    const other = row.user_a_id === currentUserId ? row.user_b : row.user_a;
    const messages = [...(row.messages ?? [])].sort(
      (a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime(),
    );
    return {
      ...row,
      otherProfile: {
        id: other.id,
        display_name: other.display_name,
        photo_url: [...(other.photos ?? [])].sort((a: any, b: any) => a.position - b.position)[0]?.url ?? null,
      },
      lastMessage: messages[0] ?? null,
      unreadCount: messages.filter((m) => m.sender_id !== currentUserId && m.status !== 'read').length,
    };
  });
}

export async function getConversation(conversationId: string): Promise<ConversationRow> {
  const { data, error } = await supabase.from('conversations').select('*').eq('id', conversationId).single();
  if (error) throw error;
  return data as ConversationRow;
}

export async function listMessages(conversationId: string): Promise<MessageRow[]> {
  const { data, error } = await supabase
    .from('messages')
    .select('*')
    .eq('conversation_id', conversationId)
    .order('created_at', { ascending: true });
  if (error) throw error;
  return (data ?? []) as MessageRow[];
}

export async function sendMessage(
  conversationId: string,
  senderId: string,
  content: string,
): Promise<MessageRow> {
  const { data, error } = await supabase
    .from('messages')
    .insert({ conversation_id: conversationId, sender_id: senderId, content, message_type: 'text' })
    .select()
    .single();
  if (error) throw error;
  return data as MessageRow;
}

/** Sube una foto de chat al bucket `photos` (mismo bucket que las fotos de perfil, bajo
 * el prefijo chat/ — ver docs/07-roadmap-and-scaling.md sobre la configuración de Storage
 * pendiente) y devuelve su URL pública para pasársela a sendImageMessage. */
export async function uploadChatImage(
  conversationId: string,
  senderId: string,
  fileUri: string,
  contentType: string,
): Promise<string> {
  const ext = contentType.split('/')[1] ?? 'jpg';
  const storagePath = `chat/${conversationId}/${senderId}-${Date.now()}.${ext}`;

  const response = await fetch(fileUri);
  const blob = await response.blob();

  const { error } = await supabase.storage.from('photos').upload(storagePath, blob, { contentType });
  if (error) throw error;

  const { data } = supabase.storage.from('photos').getPublicUrl(storagePath);
  return data.publicUrl;
}

export async function sendImageMessage(
  conversationId: string,
  senderId: string,
  imageUrl: string,
): Promise<MessageRow> {
  const { data, error } = await supabase
    .from('messages')
    .insert({ conversation_id: conversationId, sender_id: senderId, image_url: imageUrl, message_type: 'image' })
    .select()
    .single();
  if (error) throw error;
  return data as MessageRow;
}

export async function markMessagesAsRead(conversationId: string, readerId: string): Promise<void> {
  const { error } = await supabase
    .from('messages')
    .update({ status: 'read', read_at: new Date().toISOString() })
    .eq('conversation_id', conversationId)
    .neq('sender_id', readerId)
    .neq('status', 'read');
  if (error) throw error;
}

/** Suscripción Realtime a los mensajes nuevos de una conversación (ver docs/02-architecture.md §4). */
export function subscribeToConversationMessages(
  conversationId: string,
  onInsert: (message: MessageRow) => void,
) {
  const channel = supabase
    .channel(`conversation:${conversationId}`)
    .on(
      'postgres_changes',
      { event: 'INSERT', schema: 'public', table: 'messages', filter: `conversation_id=eq.${conversationId}` },
      (payload) => onInsert(payload.new as MessageRow),
    )
    .subscribe();

  return () => {
    supabase.removeChannel(channel);
  };
}

/** Canal de Presence para el indicador "escribiendo..." — no persiste en tabla. */
export function subscribeToTypingPresence(
  conversationId: string,
  selfId: string,
  onTypingChange: (typingUserIds: string[]) => void,
) {
  const channel = supabase.channel(`typing:${conversationId}`, { config: { presence: { key: selfId } } });

  channel
    .on('presence', { event: 'sync' }, () => {
      const state = channel.presenceState<{ typing: boolean }>();
      const typingIds = Object.entries(state)
        .filter(([, entries]) => entries.some((e) => e.typing))
        .map(([id]) => id)
        .filter((id) => id !== selfId);
      onTypingChange(typingIds);
    })
    .subscribe();

  return {
    setTyping: (typing: boolean) => channel.track({ typing }),
    unsubscribe: () => supabase.removeChannel(channel),
  };
}

export async function archiveConversation(conversationId: string, isUserA: boolean) {
  const { error } = await supabase
    .from('conversations')
    .update(isUserA ? { archived_by_a: true } : { archived_by_b: true })
    .eq('id', conversationId);
  if (error) throw error;
}

export async function muteConversation(conversationId: string, isUserA: boolean, muted: boolean) {
  const { error } = await supabase
    .from('conversations')
    .update(isUserA ? { muted_by_a: muted } : { muted_by_b: muted })
    .eq('id', conversationId);
  if (error) throw error;
}
