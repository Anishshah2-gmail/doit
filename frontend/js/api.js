// API Client for Authentication Backend
const API_BASE_URL = 'http://localhost:8000/v1/auth';

class AuthAPI {
  /**
   * Register a new user
   */
  static async register(email, password) {
    const response = await fetch(`${API_BASE_URL}/register`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ email, password }),
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.detail || 'Registration failed');
    }

    return data;
  }

  /**
   * Verify email with token
   */
  static async verifyEmail(token) {
    const response = await fetch(`${API_BASE_URL}/verify-email?token=${token}`);

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.detail || 'Email verification failed');
    }

    return data;
  }

  /**
   * Login user
   */
  static async login(email, password) {
    const response = await fetch(`${API_BASE_URL}/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ email, password }),
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.detail || 'Login failed');
    }

    // Store session token
    localStorage.setItem('session_token', data.session_token);
    localStorage.setItem('user', JSON.stringify(data.user));

    return data;
  }

  /**
   * Logout user
   */
  static async logout() {
    const token = localStorage.getItem('session_token');

    if (!token) {
      throw new Error('No active session');
    }

    const response = await fetch(`${API_BASE_URL}/logout`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });

    const data = await response.json();

    // Clear local storage
    localStorage.removeItem('session_token');
    localStorage.removeItem('user');

    if (!response.ok) {
      throw new Error(data.detail || 'Logout failed');
    }

    return data;
  }

  /**
   * Request password reset
   */
  static async requestPasswordReset(email) {
    const response = await fetch(`${API_BASE_URL}/password/reset-request`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ email }),
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.detail || 'Password reset request failed');
    }

    return data;
  }

  /**
   * Reset password with token
   */
  static async resetPassword(token, newPassword) {
    const response = await fetch(`${API_BASE_URL}/password/reset`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ token, new_password: newPassword }),
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.detail || 'Password reset failed');
    }

    return data;
  }

  /**
   * Resend verification email
   */
  static async resendVerification(email) {
    const response = await fetch(`${API_BASE_URL}/resend-verification`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ email }),
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.detail || 'Resend verification failed');
    }

    return data;
  }

  /**
   * Check if user is authenticated
   */
  static isAuthenticated() {
    return !!localStorage.getItem('session_token');
  }

  /**
   * Get current user
   */
  static getCurrentUser() {
    const userStr = localStorage.getItem('user');
    return userStr ? JSON.parse(userStr) : null;
  }
}
