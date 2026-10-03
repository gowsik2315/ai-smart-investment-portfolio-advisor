/**
 * Diversification Analysis Service
 * API calls for portfolio diversification analysis
 *
 * Uses the shared `api` instance rather than its own axios client.
 * The previous local client read `localStorage.getItem('token')`, but
 * authService stores the JWT under `access_token`, so it attached no
 * Authorization header at all. That went unnoticed only because these
 * endpoints were hardcoded to user 1; now that they require
 * authentication, every call would have returned 401.
 */

import api from './api';

const diversificationService = {
  /**
   * Analyze portfolio diversification
   * @param {Array} holdings - Array of holdings objects
   * @returns {Promise} Analysis results
   */
  analyzeDiversification: async (holdings) => {
    const response = await api.post('/api/diversification-analysis/analyze', {
      holdings,
    });
    return response.data;
  },

  /**
   * Get latest diversification analysis
   * @returns {Promise} Latest analysis
   */
  getLatestAnalysis: async () => {
    const response = await api.get('/api/diversification-analysis/latest');
    return response.data;
  },

  /**
   * Get analysis history
   * @param {number} limit - Number of analyses to fetch
   * @returns {Promise} Analysis history
   */
  getAnalysisHistory: async (limit = 10) => {
    const response = await api.get('/api/diversification-analysis/history', {
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

    const response = await api.post('/api/diversification-analysis/generate-sample-holdings', {
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
    await api.delete(`/api/diversification-analysis/${analysisId}`);
  },

  /**
   * Get AI explanation for diversification analysis
   * @returns {Promise} AI explanation with metrics
   */
  explainAnalysis: async () => {
    const response = await api.get('/api/diversification-analysis/explain', {
      timeout: 240000, // Ollama on CPU can need ~100s per explanation;
                       // backend retries once, so allow headroom
    });
    return response.data;
  },
};

export default diversificationService;
