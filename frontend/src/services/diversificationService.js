/**
 * Diversification Analysis Service
 * API calls for portfolio diversification analysis
 */

import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api';

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
});

// Add token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

const diversificationService = {
  /**
   * Analyze portfolio diversification
   * @param {Array} holdings - Array of holdings objects
   * @returns {Promise} Analysis results
   */
  analyzeDiversification: async (holdings) => {
    const response = await api.post('/diversification-analysis/analyze', {
      holdings,
    });
    return response.data;
  },

  /**
   * Get latest diversification analysis
   * @returns {Promise} Latest analysis
   */
  getLatestAnalysis: async () => {
    const response = await api.get('/diversification-analysis/latest');
    return response.data;
  },

  /**
   * Get analysis history
   * @param {number} limit - Number of analyses to fetch
   * @returns {Promise} Analysis history
   */
  getAnalysisHistory: async (limit = 10) => {
    const response = await api.get('/diversification-analysis/history', {
      params: { limit },
    });
    return response.data;
  },

  /**
   * Generate sample holdings for testing
   * @param {Object} params - Generation parameters
   * @returns {Promise} Sample holdings
   */
  generateSampleHoldings: async (params = {}) => {
    const {
      portfolio_value = 1000000,
      diversified = true,
    } = params;

    const response = await api.post('/diversification-analysis/generate-sample-holdings', {
      portfolio_value,
      diversified,
    });
    return response.data;
  },

  /**
   * Delete an analysis
   * @param {number} analysisId - Analysis ID
   * @returns {Promise}
   */
  deleteAnalysis: async (analysisId) => {
    await api.delete(`/diversification-analysis/${analysisId}`);
  },

  /**
   * Get AI explanation for diversification analysis
   * @returns {Promise} AI explanation with metrics
   */
  explainAnalysis: async () => {
    const response = await api.get('/diversification-analysis/explain');
    return response.data;
  },
};

export default diversificationService;
