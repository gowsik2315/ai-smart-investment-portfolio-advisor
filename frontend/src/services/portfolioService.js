/**
 * Portfolio Service
 * Handles portfolio tracking: portfolios, transactions and derived holdings
 */

import api from './api';

const portfolioService = {
  /**
   * Aggregate holdings and totals across every portfolio (dashboard)
   * @param {number|null} portfolioId - one portfolio, or null for all
   * @returns {Promise} { summary, holdings, num_portfolios }
   */
  getOverview: async (portfolioId = null) => {
    const response = await api.get('/api/portfolio/overview', {
      params: portfolioId ? { portfolio_id: portfolioId } : {},
    });
    return response.data;
  },

  /**
   * Real holdings reshaped for the diversification analyzer
   * @param {number|null} portfolioId - one portfolio, or null for all
   * @returns {Promise} { holdings, coverage, note }
   */
  getHoldingsForDiversification: async (portfolioId = null) => {
    const response = await api.get('/api/portfolio/holdings/diversification', {
      params: portfolioId ? { portfolio_id: portfolioId } : {},
    });
    return response.data;
  },

  /**
   * Daily portfolio value as a time-weighted index, for risk analytics.
   * The index moves only with prices, never with deposits or withdrawals.
   * @param {string} period - yfinance period, e.g. '1y'
   * @param {number|null} portfolioId - one portfolio, or null for all
   * @returns {Promise} { series, coverage, excluded_holdings, note }
   */
  getValueSeries: async (period = '1y', portfolioId = null) => {
    const response = await api.get('/api/portfolio/value-series', {
      params: portfolioId ? { period, portfolio_id: portfolioId } : { period },
    });
    return response.data;
  },

  /**
   * List the user's portfolios
   * @returns {Promise} Array of portfolios
   */
  listPortfolios: async () => {
    const response = await api.get('/api/portfolio/');
    return response.data;
  },

  /**
   * Create a portfolio
   * @param {Object} data - { portfolio_name, portfolio_type, notes }
   * @returns {Promise} Created portfolio
   */
  createPortfolio: async (data) => {
    const response = await api.post('/api/portfolio/', data);
    return response.data;
  },

  /**
   * Get one portfolio with its derived holdings and totals
   * @param {number} portfolioId
   * @returns {Promise} { portfolio, summary, holdings, transaction_count }
   */
  getPortfolio: async (portfolioId) => {
    const response = await api.get(`/api/portfolio/${portfolioId}`);
    return response.data;
  },

  /**
   * Rename a portfolio or change its notes
   * @param {number} portfolioId
   * @param {Object} data
   * @returns {Promise} Updated portfolio
   */
  updatePortfolio: async (portfolioId, data) => {
    const response = await api.put(`/api/portfolio/${portfolioId}`, data);
    return response.data;
  },

  /**
   * Delete a portfolio and its transactions
   * @param {number} portfolioId
   */
  deletePortfolio: async (portfolioId) => {
    await api.delete(`/api/portfolio/${portfolioId}`);
  },

  /**
   * Record a buy, sell, SIP instalment or dividend
   * @param {number} portfolioId
   * @param {Object} data - transaction details
   * @returns {Promise} Created transaction
   */
  addTransaction: async (portfolioId, data) => {
    const response = await api.post(`/api/portfolio/${portfolioId}/transactions`, data);
    return response.data;
  },

  /**
   * Transaction ledger for a portfolio
   * @param {number} portfolioId
   * @returns {Promise} Array of transactions
   */
  listTransactions: async (portfolioId) => {
    const response = await api.get(`/api/portfolio/${portfolioId}/transactions`);
    return response.data;
  },

  /**
   * Delete a transaction
   * @param {number} portfolioId
   * @param {number} transactionId
   */
  deleteTransaction: async (portfolioId, transactionId) => {
    await api.delete(`/api/portfolio/${portfolioId}/transactions/${transactionId}`);
  },
};

export default portfolioService;
