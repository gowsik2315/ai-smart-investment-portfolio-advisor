/**
 * Portfolio Analysis Service
 * API calls for portfolio risk analysis
 */

import api from './api';

const portfolioAnalysisService = {
  /**
   * Analyze portfolio risk metrics
   * @param {Array} portfolioData - Array of {date, value} objects
   * @param {number} riskFreeRate - Annual risk-free rate (optional)
   * @returns {Promise} Analysis results
   */
  analyzePortfolio: async (portfolioData, riskFreeRate = null) => {
    const response = await api.post('/api/portfolio-analysis/analyze', {
      portfolio_data: portfolioData,
      risk_free_rate: riskFreeRate,
    });
    return response.data;
  },

  /**
   * Get latest portfolio analysis (includes cached ai_explanation if present)
   * @returns {Promise} Latest analysis
   */
  getLatestAnalysis: async () => {
    const response = await api.get('/api/portfolio-analysis/latest');
    return response.data;
  },

  /**
   * Get analysis history
   * @param {number} limit - Number of analyses to fetch
   * @returns {Promise} Analysis history
   */
  getAnalysisHistory: async (limit = 10) => {
    const response = await api.get('/api/portfolio-analysis/history', {
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

    const response = await api.post('/api/portfolio-analysis/generate-sample-data', {
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
    await api.delete(`/api/portfolio-analysis/${analysisId}`);
  },

  /**
   * Get AI-powered explanation for latest portfolio analysis.
   * Returns cached explanation instantly if already generated,
   * otherwise calls Ollama LLM (may take up to 90s).
   * @returns {Promise} AI explanation with metrics
   */
  explainAnalysis: async () => {
    const response = await api.get('/api/portfolio-analysis/explain', {
      timeout: 120000, // 120s — LLM inference can take up to 90s
    });
    return response.data;
  },
};

export default portfolioAnalysisService;
