/**
 * Market Service
 * Handles stock market data API calls
 */

import api from './api';

const marketService = {
  /**
   * Search for stocks by ticker or company name
   * @param {string} query - Search query
   * @param {number} limit - Maximum number of results
   * @returns {Promise} Search results
   */
  searchStocks: async (query, limit = 10) => {
    const response = await api.get('/api/market/search', {
      params: { query, limit }
    });
    return response.data;
  },

  /**
   * Get detailed stock information
   * @param {string} ticker - Stock ticker symbol
   * @returns {Promise} Stock information
   */
  getStockInfo: async (ticker) => {
    const response = await api.get(`/api/market/stock/${ticker}`);
    return response.data;
  },

  /**
   * Get historical price data
   * @param {string} ticker - Stock ticker symbol
   * @param {string} period - Data period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
   * @param {string} interval - Data interval (1d, 5d, 1wk, 1mo)
   * @returns {Promise} Historical price data
   */
  getStockHistory: async (ticker, period = '1y', interval = '1d') => {
    const response = await api.get(`/api/market/stock/${ticker}/history`, {
      params: { period, interval }
    });
    return response.data;
  },

  /**
   * Get AI-generated trend explanation for a stock
   * @param {string} ticker - Stock ticker symbol
   * @returns {Promise} AI trend explanation
   */
  explainTrend: async (ticker) => {
    const response = await api.get(`/api/market/stock/${ticker}/explain`);
    return response.data;
  },

  /**
   * Get an AI-generated (Ollama) explanation of the Stock Predictor outlook
   * for a stock. This is generated prose, not a model output.
   *
   * Slow on CPU (the 3B model needs ~40-100s) but cached server-side, so a
   * repeat request for the same outlook returns immediately.
   *
   * @param {string} ticker - Stock ticker symbol
   * @returns {Promise} { ai_explanation, ai_available, cached, disclaimer, ... }
   */
  explainOutlook: async (ticker) => {
    const response = await api.get(
      `/api/market/stock/${encodeURIComponent(ticker)}/outlook/explain`,
      { timeout: 240000 }
    );
    return response.data;
  },
};

export default marketService;
