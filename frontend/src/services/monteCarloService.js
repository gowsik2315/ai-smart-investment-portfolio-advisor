/**
 * Monte Carlo Simulation Service
 * API calls for portfolio Monte Carlo simulation
 *
 * Uses the shared `api` instance rather than its own axios client.
 * The previous local client read `localStorage.getItem('token')`, but
 * authService stores the JWT under `access_token`, so no Authorization
 * header was ever attached. That was invisible while these endpoints
 * were hardcoded to user 1; now that they require authentication, every
 * call would have returned 401.
 */

import api from './api';

const monteCarloService = {
  /**
   * Run Monte Carlo simulation
   * @param {Object} params - Simulation parameters. Set
   *   `use_predicted_volatility: true` with a `ticker` to source sigma
   *   from the volatility forecasting model instead of `volatility`.
   * @param {boolean} save - Whether to save simulation to database
   * @returns {Promise} Simulation results, including
   *   `volatility_provenance`, `risk_metrics` and `simulation_id`
   */
  runSimulation: async (params, save = true) => {
    const response = await api.post('/api/monte-carlo/simulate', params, {
      params: { save },
    });
    return response.data;
  },

  /**
   * Get simulation history
   * @param {number} limit - Number of simulations to fetch
   * @returns {Promise} Simulation list
   */
  getSimulations: async (limit = 20) => {
    const response = await api.get('/api/monte-carlo/simulations', {
      params: { limit },
    });
    return response.data;
  },

  /**
   * Get specific simulation by ID
   * @param {number} simulationId - Simulation ID
   * @returns {Promise} Simulation details
   */
  getSimulation: async (simulationId) => {
    const response = await api.get(`/api/monte-carlo/simulations/${simulationId}`);
    return response.data;
  },

  /**
   * Get latest simulation
   * @returns {Promise} Latest simulation
   */
  getLatestSimulation: async () => {
    const response = await api.get('/api/monte-carlo/latest');
    return response.data;
  },

  /**
   * Update simulation name and notes
   * @param {number} simulationId - Simulation ID
   * @param {string} simulation_name - New name
   * @param {string} notes - New notes
   * @returns {Promise} Updated simulation
   */
  updateSimulation: async (simulationId, simulation_name, notes) => {
    const response = await api.put(`/api/monte-carlo/simulations/${simulationId}`, null, {
      params: { simulation_name, notes },
    });
    return response.data;
  },

  /**
   * Delete a simulation
   * @param {number} simulationId - Simulation ID
   * @returns {Promise}
   */
  deleteSimulation: async (simulationId) => {
    await api.delete(`/api/monte-carlo/simulations/${simulationId}`);
  },

  /**
   * Get AI explanation for a Monte Carlo simulation.
   *
   * Pass the `simulation_id` from runSimulation whenever available.
   * Without it the backend explains the most recent SAVED run, which is
   * a different simulation than the one just executed if that run used
   * `save=false`.
   *
   * @param {number} [simulationId] - Simulation to explain
   * @returns {Promise} AI explanation with metrics
   */
  explainSimulation: async (simulationId) => {
    const response = await api.get('/api/monte-carlo/explain', {
      params: simulationId ? { simulation_id: simulationId } : {},
      timeout: 240000, // Ollama on CPU can need ~100s per explanation;
                       // backend retries once, so allow headroom
    });
    return response.data;
  },
};

export default monteCarloService;
