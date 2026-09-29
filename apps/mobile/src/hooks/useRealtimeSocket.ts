import { useEffect, useRef, useState } from 'react';
import { io, Socket } from 'socket.io-client';
import { useAuthStore } from '../store/authStore';

const SOCKET_URL = process.env.REACT_APP_REALTIME_URL || 'http://localhost:3002';

interface RealtimeMessage {
  id: string;
  matchId: string;
  senderId: string;
  content: string;
  timestamp: number;
  status: 'sent' | 'delivered' | 'read';
}

interface TypingUser {
  userId: string;
  matchId: string;
}

interface PresenceUser {
  userId: string;
  status: 'online' | 'away' | 'dnd';
  lastSeen: number;
}

export function useRealtimeSocket() {
  const socketRef = useRef<Socket | null>(null);
  const session = useAuthStore((s) => s.session);
  const [isConnected, setIsConnected] = useState(false);
  const [activeUsers, setActiveUsers] = useState<PresenceUser[]>([]);
  const [typingUsers, setTypingUsers] = useState<Set<string>>(new Set());

  // Initialize socket connection
  useEffect(() => {
    if (!session) return;

    const socket = io(SOCKET_URL, {
      auth: {
        userId: session.user.id,
        token: session.access_token,
      },
      reconnection: true,
      reconnectionDelay: 1000,
      reconnectionDelayMax: 5000,
      reconnectionAttempts: 5,
      transports: ['websocket', 'polling'],
    });

    socketRef.current = socket;

    // Connection events
    socket.on('connect', () => {
      console.log('🔌 Socket connected');
      setIsConnected(true);
    });

    socket.on('auth_success', (data) => {
      console.log('✅ Socket authenticated:', data);
    });

    socket.on('auth_error', (error) => {
      console.error('❌ Socket auth error:', error);
      socket.disconnect();
    });

    socket.on('disconnect', () => {
      console.log('🔌 Socket disconnected');
      setIsConnected(false);
    });

    socket.on('user_online', (data) => {
      console.log('🟢 User online:', data.userId);
    });

    socket.on('user_offline', (data) => {
      console.log('🔴 User offline:', data.userId);
    });

    // Presence updates
    socket.on('presence:changed', (data: PresenceUser) => {
      setActiveUsers((prev) => {
        const filtered = prev.filter((u) => u.userId !== data.userId);
        return [...filtered, data];
      });
    });

    socket.on('presence:users', (data: { users: PresenceUser[] }) => {
      setActiveUsers(data.users);
    });

    return () => {
      socket.disconnect();
    };
  }, [session]);

  // Send message
  const sendMessage = (matchId: string, message: string, messageId: string) => {
    if (socketRef.current && isConnected) {
      socketRef.current.emit('message:send', {
        matchId,
        message,
        messageId,
      });
    }
  };

  // Mark message as read
  const markMessageRead = (matchId: string, messageId: string) => {
    if (socketRef.current && isConnected) {
      socketRef.current.emit('message:read', {
        matchId,
        messageId,
      });
    }
  };

  // Start typing
  const startTyping = (matchId: string) => {
    if (socketRef.current && isConnected) {
      socketRef.current.emit('typing:start', { matchId });
    }
  };

  // Stop typing
  const stopTyping = (matchId: string) => {
    if (socketRef.current && isConnected) {
      socketRef.current.emit('typing:stop', { matchId });
    }
  };

  // Subscribe to match
  const subscribeToMatch = (matchId: string) => {
    if (socketRef.current && isConnected) {
      socketRef.current.emit('match:subscribe', { matchId });
    }
  };

  // Unsubscribe from match
  const unsubscribeFromMatch = (matchId: string) => {
    if (socketRef.current && isConnected) {
      socketRef.current.emit('match:unsubscribe', { matchId });
    }
  };

  // Subscribe to discovery feed updates
  const subscribeToDiscovery = () => {
    if (socketRef.current && isConnected) {
      socketRef.current.emit('discovery:subscribe');
    }
  };

  // Unsubscribe from discovery
  const unsubscribeFromDiscovery = () => {
    if (socketRef.current && isConnected) {
      socketRef.current.emit('discovery:unsubscribe');
    }
  };

  // Update presence/status
  const updatePresence = (status: 'online' | 'away' | 'dnd', location?: { lat: number; lng: number }) => {
    if (socketRef.current && isConnected) {
      socketRef.current.emit('presence:update', { status, location });
    }
  };

  // Like profile
  const likeProfile = (profileId: string) => {
    if (socketRef.current && isConnected) {
      socketRef.current.emit('discovery:like', { profileId });
    }
  };

  // Pass profile
  const passProfile = (profileId: string) => {
    if (socketRef.current && isConnected) {
      socketRef.current.emit('discovery:pass', { profileId });
    }
  };

  // SuperLike profile
  const superlikeProfile = (profileId: string) => {
    if (socketRef.current && isConnected) {
      socketRef.current.emit('discovery:superlike', { profileId });
    }
  };

  // Listen to message events
  const onMessageReceived = (callback: (message: RealtimeMessage) => void) => {
    if (socketRef.current) {
      socketRef.current.on('message:received', callback);
      return () => socketRef.current?.off('message:received', callback);
    }
  };

  // Listen to typing events
  const onTypingActive = (callback: (users: string[]) => void) => {
    if (socketRef.current) {
      socketRef.current.on('typing:active', (data) => callback(data.typingUsers));
      return () => socketRef.current?.off('typing:active');
    }
  };

  // Listen to typing stop events
  const onTypingInactive = (callback: (users: string[]) => void) => {
    if (socketRef.current) {
      socketRef.current.on('typing:inactive', (data) => callback(data.typingUsers));
      return () => socketRef.current?.off('typing:inactive');
    }
  };

  // Listen to match created
  const onMatchCreated = (callback: (matchData: { matchWith: string }) => void) => {
    if (socketRef.current) {
      socketRef.current.on('match:created', callback);
      return () => socketRef.current?.off('match:created');
    }
  };

  // Listen to discovery interactions
  const onDiscoveryInteraction = (callback: (data: any) => void) => {
    if (socketRef.current) {
      socketRef.current.on('discovery:interaction', callback);
      return () => socketRef.current?.off('discovery:interaction');
    }
  };

  return {
    isConnected,
    activeUsers,
    socket: socketRef.current,

    // Methods
    sendMessage,
    markMessageRead,
    startTyping,
    stopTyping,
    subscribeToMatch,
    unsubscribeFromMatch,
    subscribeToDiscovery,
    unsubscribeFromDiscovery,
    updatePresence,
    likeProfile,
    passProfile,
    superlikeProfile,

    // Event listeners
    onMessageReceived,
    onTypingActive,
    onTypingInactive,
    onMatchCreated,
    onDiscoveryInteraction,
  };
}
