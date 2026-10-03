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
};

export default mlService;
