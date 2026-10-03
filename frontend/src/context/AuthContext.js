/**
 * Authentication Context
 * Provides global authentication state management
 */

import React, { createContext, useState, useContext, useEffect } from 'react';
import authService from '../services/authService';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check if user is authenticated on mount
    const initAuth = async () => {
      try {
        if (authService.isAuthenticated()) {
          const userData = await authService.getCurrentUser();
          setUser(userData);
        }
      } catch (error) {
        console.error('Auth initialization error:', error);
        // Clear invalid auth data
        authService.logout();
      } finally {
        setLoading(false);
      }
    };

    initAuth();
  }, []);

  /**
   * Extract a human-readable message from a FastAPI error response.
   * FastAPI validation errors (422) return detail as an array of objects;
   * application errors (400, 401, etc.) return detail as a plain string.
   */
  const extractErrorMessage = (error, fallback) => {
    const detail = error.response?.data?.detail;
    if (!detail) return fallback;
    if (Array.isArray(detail)) {
      // 422 Unprocessable Entity — array of { loc, msg, type }
      return detail.map((e) => e.msg).join(', ');
    }
    return detail;
  };

  const login = async (credentials) => {
    try {
      const response = await authService.login(credentials);
      setUser(response.user);
      return { success: true };
    } catch (error) {
      return {
        success: false,
        error: extractErrorMessage(error, 'Login failed'),
      };
    }
  };

  const register = async (userData) => {
    try {
      await authService.register(userData);
      return { success: true };
    } catch (error) {
      return {
        success: false,
        error: extractErrorMessage(error, 'Registration failed'),
      };
    }
  };

  const logout = () => {
    authService.logout();
    setUser(null);
  };

  const value = {
    user,
    loading,
    login,
    register,
    logout,
    isAuthenticated: !!user,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};
