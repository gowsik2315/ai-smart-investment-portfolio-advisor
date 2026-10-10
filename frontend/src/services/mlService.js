/**
 * ML Volatility Forecasting Service
 * API calls for the ML-based volatility forecasting endpoints.
 *
 * Distinct from the Ollama-backed `/explain` endpoints used elsewhere:
 * this is a trained model returning a number, not an LLM returning
 * prose. Keep the two labelled separately in the UI.
 */

import api from './api';

const mlService = {
  /**
   * Forecast annualised volatility for a ticker.
   *
   * Always inspect `source` on the result before describing it:
   *   'ml_predicted'        -> a genuine model forecast
   *   'historical_fallback' -> trailing realised volatility, NOT a forecast
   *
   * @param {string} ticker - e.g. 'RELIANCE.NS'
   * @param {boolean} useCache - serve a recent forecast if available
   * @returns {Promise} Forecast with provenance
   */
  predictVolatility: async (ticker, useCache = true) => {
    const response = await api.post('/api/ml/predict-volatility', {
      ticker,
      use_cache: useCache,
    });
    return response.data;
  },

  /**
   * Whether a volatility model is currently loaded, and its metadata.
   * `model_loaded: false` before training is expected, not an error.
   * @returns {Promise} Model info
   */
  getModelInfo: async () => {
    const response = await api.get('/api/ml/model-info');
    return response.data;
  },

  /**
   * Re-read the model artifact from disk. Use after training.
   * @returns {Promise} Model info after reload
   */
  reloadModel: async () => {
    const response = await api.post('/api/ml/reload-model');
    return response.data;
  },

  /**
   * Feature values a prediction for `ticker` would be based on.
   * First place to look when a forecast looks wrong.
   * @param {string} ticker
   * @returns {Promise} Feature snapshot
   */
  getFeatureSnapshot: async (ticker) => {
    const response = await api.get(`/api/ml/features/${encodeURIComponent(ticker)}`);
    return response.data;
  },

  /**
   * Price cache contents and available model artifacts.
   * @returns {Promise} Cache status
   */
  getCacheStatus: async () => {
    const response = await api.get('/api/ml/cache-status');
    return response.data;
  },

  /**
   * 21-day outlook for a stock: current trend, probability of a rise, and
   * the expected price range.
   *
   * Inspect `probability_source` before describing the probability:
   *   'ml_predicted'         -> a trained model's output
   *   'historical_base_rate' -> the stock's own past frequency of rising,
   *                             NOT a prediction
   *
   * The first call for an uncached ticker downloads three years of daily
   * bars, so the timeout is generous.
   *
   * @param {string} ticker - e.g. 'RELIANCE.NS'
   * @returns {Promise} Outlook with provenance
   */
  getTrendOutlook: async (ticker) => {
    const response = await api.get(
      `/api/ml/trend-outlook/${encodeURIComponent(ticker)}`,
      { timeout: 120000 }
    );
    return response.data;
  },

  /**
   * Whether a trend classifier is loaded, and its held-out metrics.
   * `model_loaded: false` before training is expected, not an error.
   * @returns {Promise} Model info
   */
  getTrendModelInfo: async () => {
    const response = await api.get('/api/ml/trend-model-info');
    return response.data;
  },

  /**
   * Re-read the trend artifact from disk. Use after training.
   * @returns {Promise} Model info after reload
   */
  reloadTrendModel: async () => {
    const response = await api.post('/api/ml/reload-trend-model');
    return response.data;
  },
};

export default mlService;
