/**
 * YUIZZ API Client
 * Conecta el frontend (volta-pro.html) con el backend (server.js)
 */

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:3001';

class YuizzAPIClient {
  constructor(apiUrl = API_URL) {
    this.apiUrl = apiUrl;
    this.token = localStorage.getItem('yuizz_token');
  }

  // ============================================
  // AUTH
  // ============================================

  async register(email, password, username, firstName, lastName) {
    const response = await fetch(`${this.apiUrl}/api/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password, username, firstName, lastName })
    });
    const data = await response.json();
    if (response.ok) {
      this.token = data.token;
      localStorage.setItem('yuizz_token', data.token);
      localStorage.setItem('yuizz_user_id', data.userId);
    }
    return data;
  }

  async login(email, password) {
    const response = await fetch(`${this.apiUrl}/api/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password })
    });
    const data = await response.json();
    if (response.ok) {
      this.token = data.token;
      localStorage.setItem('yuizz_token', data.token);
      localStorage.setItem('yuizz_user_id', data.userId);
    }
    return data;
  }

  logout() {
    this.token = null;
    localStorage.removeItem('yuizz_token');
    localStorage.removeItem('yuizz_user_id');
  }

  // ============================================
  // PROFILES
  // ============================================

  async getMyProfile() {
    return this._fetch('/api/users/profile');
  }

  async updateProfile(profileData) {
    return this._fetch('/api/users/profile', {
      method: 'PUT',
      body: JSON.stringify(profileData)
    });
  }

  async getDiscoverProfiles() {
    return this._fetch('/api/discover');
  }

  // ============================================
  // INTERACTIONS
  // ============================================

  async like(targetUserId) {
    return this._fetch('/api/interactions/like', {
      method: 'POST',
      body: JSON.stringify({ targetUserId })
    });
  }

  async pass(targetUserId) {
    return this._fetch('/api/interactions/pass', {
      method: 'POST',
      body: JSON.stringify({ targetUserId })
    });
  }

  async superLike(targetUserId) {
    return this._fetch('/api/interactions/super-like', {
      method: 'POST',
      body: JSON.stringify({ targetUserId })
    });
  }

  // ============================================
  // MESSAGES
  // ============================================

  async getChats() {
    return this._fetch('/api/messages/chats');
  }

  async sendMessage(receiverId, content) {
    return this._fetch('/api/messages/send', {
      method: 'POST',
      body: JSON.stringify({ receiverId, content })
    });
  }

  // ============================================
  // ECONOMY
  // ============================================

  async getCoins() {
    return this._fetch('/api/coins');
  }

  async purchaseCoins(amount) {
    return this._fetch('/api/coins/purchase', {
      method: 'POST',
      body: JSON.stringify({ amount })
    });
  }

  async claimDailyReward() {
    return this._fetch('/api/streaks/claim', {
      method: 'POST'
    });
  }

  // ============================================
  // UTILITY
  // ============================================

  async _fetch(endpoint, options = {}) {
    const headers = {
      'Content-Type': 'application/json',
      ...options.headers
    };

    if (this.token) {
      headers.Authorization = `Bearer ${this.token}`;
    }

    const response = await fetch(`${this.apiUrl}${endpoint}`, {
      ...options,
      headers
    });

    if (response.status === 401) {
      this.logout();
      window.location.href = '/login';
    }

    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.error || 'API Error');
    }
    return data;
  }

  // Health check
  async healthCheck() {
    try {
      const response = await fetch(`${this.apiUrl}/health`);
      return response.ok;
    } catch {
      return false;
    }
  }
}

// Exportar para usar en volta-pro.html
if (typeof window !== 'undefined') {
  window.yuizzAPI = new YuizzAPIClient();
}

export default YuizzAPIClient;
