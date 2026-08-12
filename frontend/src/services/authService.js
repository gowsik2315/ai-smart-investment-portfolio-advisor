/**
 * Authentication Service
 * Handles authentication-related API calls
 */

import api from './api';

const authService = {
  /**
   * Register a new user
   * @param {Object} userData - User registration data
   * @returns {Promise} API response
   */
  register: async (userData) => {
    const response = await api.post('/api/auth/register', userData);
    return response.data;
  },

  /**
   * Login user
   * @param {Object} credentials - User login credentials
   * @returns {Promise} API response with tokens
   */
  login: async (credentials) => {
    const response = await api.post('/api/auth/login', credentials);
    const { access_token, refresh_token, user } = response.data;
    
    // Store tokens and user info in localStorage
    localStorage.setItem('access_token', access_token);
    localStorage.setItem('refresh_token', refresh_token);
    if (user) {
      localStorage.setItem('user', JSON.stringify(user));
    }
    
    return response.data;
  },

  /**
   * Logout user
   */
  logout: () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user');
  },

  /**
   * Get current user
   * @returns {Promise} Current user data
   */
  getCurrentUser: async () => {
    // First check localStorage
    const userStr = localStorage.getItem('user');
    if (userStr) {
      return JSON.parse(userStr);
    }
    
    // If not in localStorage, fetch from API (for future implementation)
    const response = await api.get('/api/auth/me');
    return response.data;
  },

  /**
   * Check if user is authenticated
   * @returns {boolean} Authentication status
   */
  isAuthenticated: () => {
    return !!localStorage.getItem('access_token');
  },
};

export default authService;
