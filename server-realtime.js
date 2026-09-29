// ============================================
// YUIZZ V2.0 - WEBSOCKET REALTIME (Socket.io)
// ============================================

import express from 'express';
import { createServer } from 'http';
import { Server as SocketServer } from 'socket.io';
import cors from 'cors';
import dotenv from 'dotenv';

dotenv.config();

const app = express();
const httpServer = createServer(app);
const io = new SocketServer(httpServer, {
  cors: {
    origin: ['http://localhost:8081', 'http://localhost:3000'],
    credentials: true,
  },
  transports: ['websocket', 'polling'],
  pingInterval: 30000,
  pingTimeout: 10000,
});

app.use(cors());
app.use(express.json());

const PORT = process.env.REALTIME_PORT || 3002;

// ============================================
// DATA STRUCTURES
// ============================================

// Track active users and their status
const activeUsers = new Map();

// Track typing status per match
const typingStatus = new Map();

// Track discovery feed updates
const discoverySubscribers = new Set();

// ============================================
// SOCKET.IO EVENTS
// ============================================

io.on('connection', (socket) => {
  console.log(`🔌 User connected: ${socket.id}`);

  // ============================================
  // AUTHENTICATION
  // ============================================

  socket.on('auth', (data) => {
    const { userId, token } = data;

    if (!userId || !token) {
      socket.emit('auth_error', { message: 'Invalid credentials' });
      socket.disconnect();
      return;
    }

    // Store user info in socket
    socket.userId = userId;
    socket.token = token;

    // Add to active users
    activeUsers.set(userId, {
      socketId: socket.id,
      status: 'online',
      lastSeen: Date.now(),
      location: null,
    });

    // Join user's personal room
    socket.join(`user_${userId}`);
    socket.join('all_users');

    console.log(`✅ User authenticated: ${userId}`);
    socket.emit('auth_success', { userId, message: 'Connected' });

    // Notify others that user came online
    io.emit('user_online', {
      userId,
      timestamp: Date.now(),
      activeUsers: Array.from(activeUsers.keys()),
    });
  });

  // ============================================
  // MESSAGING
  // ============================================

  socket.on('message:send', (data) => {
    const { matchId, message, messageId } = data;
    const userId = socket.userId;

    if (!userId || !matchId || !message) {
      socket.emit('message:error', { message: 'Invalid data' });
      return;
    }

    const messageData = {
      id: messageId,
      matchId,
      senderId: userId,
      content: message,
      timestamp: Date.now(),
      status: 'sent',
    };

    // Send to specific match room
    io.to(`match_${matchId}`).emit('message:received', messageData);

    // Acknowledge to sender
    socket.emit('message:ack', { messageId, status: 'delivered' });

    console.log(`💬 Message sent in match ${matchId}`);
  });

  socket.on('message:read', (data) => {
    const { matchId, messageId } = data;
    const userId = socket.userId;

    if (!matchId || !messageId) return;

    io.to(`match_${matchId}`).emit('message:read_receipt', {
      messageId,
      readBy: userId,
      timestamp: Date.now(),
    });

    console.log(`👁️ Message ${messageId} marked as read`);
  });

  // ============================================
  // TYPING INDICATORS
  // ============================================

  socket.on('typing:start', (data) => {
    const { matchId } = data;
    const userId = socket.userId;

    if (!matchId) return;

    // Store typing status
    if (!typingStatus.has(matchId)) {
      typingStatus.set(matchId, new Set());
    }
    typingStatus.get(matchId).add(userId);

    // Broadcast to match
    io.to(`match_${matchId}`).emit('typing:active', {
      matchId,
      typingUsers: Array.from(typingStatus.get(matchId)),
    });
  });

  socket.on('typing:stop', (data) => {
    const { matchId } = data;
    const userId = socket.userId;

    if (!matchId) return;

    // Remove typing status
    if (typingStatus.has(matchId)) {
      typingStatus.get(matchId).delete(userId);

      if (typingStatus.get(matchId).size === 0) {
        typingStatus.delete(matchId);
      }

      // Broadcast update
      io.to(`match_${matchId}`).emit('typing:inactive', {
        matchId,
        typingUsers: Array.from(typingStatus.get(matchId) || []),
      });
    }
  });

  // ============================================
  // MATCH OPERATIONS
  // ============================================

  socket.on('match:subscribe', (data) => {
    const { matchId } = data;
    const userId = socket.userId;

    if (!matchId) return;

    // Join match room
    socket.join(`match_${matchId}`);

    // Notify others in match that user is online
    io.to(`match_${matchId}`).emit('match:user_online', {
      matchId,
      userId,
      timestamp: Date.now(),
    });

    socket.emit('match:subscribed', { matchId });
    console.log(`📱 User ${userId} subscribed to match ${matchId}`);
  });

  socket.on('match:unsubscribe', (data) => {
    const { matchId } = data;
    const userId = socket.userId;

    if (!matchId) return;

    // Leave match room
    socket.leave(`match_${matchId}`);

    // Notify others
    io.to(`match_${matchId}`).emit('match:user_offline', {
      matchId,
      userId,
      timestamp: Date.now(),
    });

    console.log(`📵 User ${userId} unsubscribed from match ${matchId}`);
  });

  // ============================================
  // DISCOVERY FEED UPDATES (Real-time)
  // ============================================

  socket.on('discovery:subscribe', () => {
    const userId = socket.userId;
    discoverySubscribers.add(userId);
    socket.emit('discovery:subscribed', {
      message: 'Receiving discovery feed updates',
    });
    console.log(`🔍 User ${userId} subscribed to discovery feed`);
  });

  socket.on('discovery:unsubscribe', () => {
    const userId = socket.userId;
    discoverySubscribers.delete(userId);
    console.log(`🔍 User ${userId} unsubscribed from discovery feed`);
  });

  // ============================================
  // PRESENCE & STATUS
  // ============================================

  socket.on('presence:update', (data) => {
    const { status, location } = data;
    const userId = socket.userId;

    if (!userId) return;

    const user = activeUsers.get(userId);
    if (user) {
      user.status = status; // 'online', 'away', 'dnd'
      user.location = location;
      user.lastSeen = Date.now();

      // Broadcast presence update
      io.emit('presence:changed', {
        userId,
        status,
        lastSeen: Date.now(),
      });

      console.log(`🟢 User ${userId} status: ${status}`);
    }
  });

  socket.on('presence:request', () => {
    const userId = socket.userId;

    // Send current active users to requester
    socket.emit('presence:users', {
      users: Array.from(activeUsers.entries()).map(([id, data]) => ({
        userId: id,
        status: data.status,
        lastSeen: data.lastSeen,
      })),
    });
  });

  // ============================================
  // DISCOVERY FEED EVENTS
  // ============================================

  socket.on('discovery:like', (data) => {
    const { profileId } = data;
    const userId = socket.userId;

    if (!profileId) return;

    // Broadcast like event to discovery subscribers
    io.emit('discovery:interaction', {
      type: 'like',
      userId,
      profileId,
      timestamp: Date.now(),
    });

    // Check for match and notify both users
    // (In production, this would check the database)
    socket.emit('interaction:recorded', {
      profileId,
      type: 'like',
      timestamp: Date.now(),
    });

    console.log(`❤️ User ${userId} liked profile ${profileId}`);
  });

  socket.on('discovery:pass', (data) => {
    const { profileId } = data;
    const userId = socket.userId;

    if (!profileId) return;

    socket.emit('interaction:recorded', {
      profileId,
      type: 'pass',
      timestamp: Date.now(),
    });

    console.log(`👋 User ${userId} passed profile ${profileId}`);
  });

  socket.on('discovery:superlike', (data) => {
    const { profileId } = data;
    const userId = socket.userId;

    if (!profileId) return;

    // SuperLike is special - notify the liked user
    io.emit('discovery:superlike_received', {
      receiverId: profileId,
      senderId: userId,
      timestamp: Date.now(),
    });

    socket.emit('interaction:recorded', {
      profileId,
      type: 'superlike',
      cost: 50,
      timestamp: Date.now(),
    });

    console.log(`⭐ User ${userId} super-liked profile ${profileId}`);
  });

  // ============================================
  // PRIVACY & SECURITY EVENTS
  // ============================================

  socket.on('privacy:screenshot_attempt', (data) => {
    const { conversationId, otherUserId, attemptNumber } = data;
    const userId = socket.userId;

    if (!otherUserId) return;

    // Notify the other user that their conversation partner attempted screenshot
    io.to(`user_${otherUserId}`).emit('privacy:screenshot_detected', {
      userId,
      conversationId,
      attemptNumber,
      timestamp: Date.now(),
    });

    console.log(`⚠️ Screenshot attempt detected: User ${userId} in conversation ${conversationId}`);
  });

  socket.on('privacy:conversation_deleted', (data) => {
    const { conversationId, otherUserId } = data;
    const userId = socket.userId;

    if (!otherUserId) return;

    // Notify the other user that their conversation was deleted
    io.to(`user_${otherUserId}`).emit('privacy:conversation_deleted_notice', {
      userId,
      conversationId,
      timestamp: Date.now(),
    });

    console.log(`🗑️ Conversation ${conversationId} deleted by user ${userId}`);
  });

  socket.on('privacy:anonymous_mode_changed', (data) => {
    const { anonymousMode } = data;
    const userId = socket.userId;

    // Broadcast anonymous mode change to conversation participants
    io.emit('privacy:mode_updated', {
      userId,
      anonymousMode,
      timestamp: Date.now(),
    });

    console.log(`👤 User ${userId} anonymous mode: ${anonymousMode}`);
  });

  // ============================================
  // REAL-TIME NOTIFICATIONS
  // ============================================

  socket.on('notification:subscribe', () => {
    const userId = socket.userId;
    socket.join(`notifications_${userId}`);
    console.log(`🔔 User ${userId} subscribed to notifications`);
  });

  // Server method to send notification
  const sendNotification = (userId, notification) => {
    io.to(`notifications_${userId}`).emit('notification:new', {
      id: Date.now(),
      ...notification,
      timestamp: Date.now(),
    });
  };

  socket.on('notification:mark_read', (data) => {
    const { notificationId } = data;
    // Would mark in database
    socket.emit('notification:marked_read', { notificationId });
  });

  // ============================================
  // DISCONNECT
  // ============================================

  socket.on('disconnect', () => {
    const userId = socket.userId;

    if (userId) {
      activeUsers.delete(userId);
      discoverySubscribers.delete(userId);

      // Notify others
      io.emit('user_offline', {
        userId,
        timestamp: Date.now(),
        activeUsers: Array.from(activeUsers.keys()),
      });

      console.log(`🔌 User disconnected: ${userId}`);
    }
  });

  socket.on('error', (error) => {
    console.error(`❌ Socket error for ${socket.userId}:`, error);
  });
});

// ============================================
// HTTP ENDPOINTS
// ============================================

app.get('/health', (req, res) => {
  res.json({
    status: 'YUIZZ Realtime API v2 running ✅',
    activeUsers: activeUsers.size,
    socketConnections: io.engine.clientsCount,
  });
});

app.get('/api/v2/realtime/status', (req, res) => {
  res.json({
    status: 'operational',
    activeUsers: Array.from(activeUsers.entries()).map(([id, data]) => ({
      userId: id,
      status: data.status,
      lastSeen: data.lastSeen,
    })),
    discoverySubscribers: discoverySubscribers.size,
    totalConnections: io.engine.clientsCount,
  });
});

// Broadcast new profile match to subscribers
app.post('/api/v2/realtime/broadcast-match', (req, res) => {
  const { userId1, userId2 } = req.body;

  if (!userId1 || !userId2) {
    return res.status(400).json({ error: 'Missing user IDs' });
  }

  // Notify both users of match
  io.to(`user_${userId1}`).emit('match:created', {
    matchWith: userId2,
    timestamp: Date.now(),
  });

  io.to(`user_${userId2}`).emit('match:created', {
    matchWith: userId1,
    timestamp: Date.now(),
  });

  res.json({ success: true, message: 'Match broadcasted' });
});

// Broadcast discovery feed update
app.post('/api/v2/realtime/broadcast-profile', (req, res) => {
  const { profileId, profile } = req.body;

  if (!profileId || !profile) {
    return res.status(400).json({ error: 'Invalid data' });
  }

  io.emit('discovery:profile_updated', {
    profileId,
    profile,
    timestamp: Date.now(),
  });

  res.json({ success: true, message: 'Profile broadcasted' });
});

// ============================================
// MIDDLEWARE
// ============================================

// Cleanup inactive users every 5 minutes
setInterval(() => {
  const now = Date.now();
  const inactiveThreshold = 5 * 60 * 1000; // 5 minutes

  for (const [userId, userData] of activeUsers.entries()) {
    if (now - userData.lastSeen > inactiveThreshold && userData.status === 'online') {
      userData.status = 'away';
      io.emit('presence:changed', {
        userId,
        status: 'away',
        lastSeen: userData.lastSeen,
      });
    }
  }
}, 5 * 60 * 1000);

// ============================================
// SERVER START
// ============================================

httpServer.listen(PORT, () => {
  console.log(`
╔════════════════════════════════════════╗
║  🔥 YUIZZ V2 REALTIME - RUNNING      ║
╚════════════════════════════════════════╝

📍 Realtime API: http://localhost:${PORT}
🔌 WebSocket: ws://localhost:${PORT}

Features:
  ✓ Real-time messaging
  ✓ Typing indicators
  ✓ Online/offline status
  ✓ Presence tracking
  ✓ Discovery feed updates
  ✓ Match notifications
  ✓ User interactions (like/pass/superlike)

Active Users: 0
Socket Connections: 0

Next: Connect frontend + Stripe integration
  `);
});

// Export for use in main server
export { io, sendNotification, activeUsers };
