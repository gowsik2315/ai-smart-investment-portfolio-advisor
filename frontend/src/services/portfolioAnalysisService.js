/**
 * Portfolio Analysis Service
 * API calls for portfolio risk analysis
 */

import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api';

// Create axios instance with auth token
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

const portfolioAnalysisService = {
  /**
   * Analyze portfolio risk metrics
   * @param {Array} portfolioData - Array of {date, value} objects
   * @param {number} riskFreeRate - Annual risk-free rate (optional)
   * @returns {Promise} Analysis results
   */
  analyzePortfolio: async (portfolioData, riskFreeRate = null) => {
    const token = localStorage.getItem('token');
    const response = await api.post('/portfolio-analysis/analyze', {
      portfolio_data: portfolioData,
      risk_free_rate: riskFreeRate,
    }, {
      headers: token ? { Authorization: `Bearer ${token}` } : {}
    });
    return response.data;
  },

  /**
   * Get latest portfolio analysis
   * @returns {Promise} Latest analysis
   */
  getLatestAnalysis: async () => {
    const response = await api.get('/portfolio-analysis/latest');
    return response.data;
  },

  /**
   * Get analysis history
   * @param {number} limit - Number of analyses to fetch
   * @returns {Promise} Analysis history
   */
  getAnalysisHistory: async (limit = 10) => {
    const response = await api.get('/portfolio-analysis/history', {
      params: { limit },
    });
    return response.data;
  },

  /**
   * Generate sample portfolio data for testing
   * @param {Object} params - Generation parameters
   * @returns {Promise} Sample data
   */
  generateSampleData: async (params = {}) => {
    const {
      initial_value = 100000,
      days = 252,
      volatility = 0.15,
      drift = 0.10,
    } = params;

    const response = await api.post('/portfolio-analysis/generate-sample-data', {
      initial_value,
      days,
      volatility,
      drift,
    });
    return response.data;
  },

  /**
   * Delete an analysis
   * @param {number} analysisId - Analysis ID
   * @returns {Promise}
   */
  deleteAnalysis: async (analysisId) => {
    await api.delete(`/portfolio-analysis/${analysisId}`);
  },

  /**
   * Get AI explanation for portfolio analysis
   * @returns {Promise} AI explanation with metrics
   */
  explainAnalysis: async () => {
    const response = await api.get('/portfolio-analysis/explain');
    return response.data;
  },
};

export default portfolioAnalysisService;
