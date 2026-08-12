/**
 * Risk Service
 * Handles risk profiling API calls
 */

import api from './api';

const riskService = {
  /**
   * Calculate risk profile for authenticated user
   * Automatically generated from financial profile
   * @returns {Promise} API response with risk profile
   */
  calculateRiskProfile: async () => {
    const response = await api.post('/api/risk/calculate');
    return response.data;
  },

  /**
   * Get risk profile for authenticated user
   * @returns {Promise} Risk profile data
   */
  getRiskProfile: async () => {
    const response = await api.get('/api/risk/');
    return response.data;
  },

  /**
   * Delete risk profile for authenticated user
   * @returns {Promise} API response
   */
  deleteRiskProfile: async () => {
    const response = await api.delete('/api/risk/');
    return response.data;
  },

  /**
   * Get AI-generated explanation for risk profile
   * @returns {Promise} AI explanation data
   */
  explainRiskProfile: async () => {
    const response = await api.get('/api/risk/explain');
    return response.data;
  },
};

export default riskService;
