/**
 * Portfolio Recommendation Service
 * Handles portfolio recommendation API calls
 */

import api from './api';

const recommendationService = {
  /**
   * Generate portfolio recommendation for authenticated user
   * Automatically generated from risk profile
   * @returns {Promise} API response with portfolio recommendation
   */
  generateRecommendation: async () => {
    const response = await api.post('/api/recommendation/generate');
    return response.data;
  },

  /**
   * Get portfolio recommendation for authenticated user
   * @returns {Promise} Portfolio recommendation data
   */
  getRecommendation: async () => {
    const response = await api.get('/api/recommendation/');
    return response.data;
  },

  /**
   * Delete portfolio recommendation for authenticated user
   * @returns {Promise} API response
   */
  deleteRecommendation: async () => {
    const response = await api.delete('/api/recommendation/');
    return response.data;
  },

  /**
   * Get AI-generated explanation for portfolio recommendation
   * @returns {Promise} AI explanation data
   */
  explainRecommendation: async () => {
    const response = await api.get('/api/recommendation/explain');
    return response.data;
  },
};

export default recommendationService;
