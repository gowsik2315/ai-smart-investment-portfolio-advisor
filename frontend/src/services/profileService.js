/**
 * Profile Service
 * Handles financial profile-related API calls
 */

import api from './api';

const profileService = {
  /**
   * Create financial profile for authenticated user
   * @param {Object} profileData - Financial profile data
   * @returns {Promise} API response
   */
  createProfile: async (profileData) => {
    const response = await api.post('/api/profile/', profileData);
    return response.data;
  },

  /**
   * Get financial profile for authenticated user
   * @returns {Promise} Financial profile data
   */
  getProfile: async () => {
    const response = await api.get('/api/profile/');
    return response.data;
  },

  /**
   * Update financial profile for authenticated user
   * @param {Object} profileData - Updated profile data
   * @returns {Promise} API response
   */
  updateProfile: async (profileData) => {
    const response = await api.put('/api/profile/', profileData);
    return response.data;
  },

  /**
   * Delete financial profile for authenticated user
   * @returns {Promise} API response
   */
  deleteProfile: async () => {
    const response = await api.delete('/api/profile/');
    return response.data;
  },
};

export default profileService;
