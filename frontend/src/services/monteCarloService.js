/**
 * Monte Carlo Simulation Service
 * API calls for portfolio Monte Carlo simulation
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

const monteCarloService = {
  /**
   * Run Monte Carlo simulation
   * @param {Object} params - Simulation parameters
   * @param {boolean} save - Whether to save simulation to database
   * @returns {Promise} Simulation results
   */
  runSimulation: async (params, save = true) => {
    const response = await api.post('/monte-carlo/simulate', params, {
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
    const response = await api.get('/monte-carlo/simulations', {
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
    const response = await api.get(`/monte-carlo/simulations/${simulationId}`);
    return response.data;
  },

  /**
   * Get latest simulation
   * @returns {Promise} Latest simulation
   */
  getLatestSimulation: async () => {
    const response = await api.get('/monte-carlo/latest');
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
    const response = await api.put(`/monte-carlo/simulations/${simulationId}`, null, {
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
    await api.delete(`/monte-carlo/simulations/${simulationId}`);
  },

  /**
   * Get AI explanation for Monte Carlo simulation
   * @returns {Promise} AI explanation with metrics
   */
  explainSimulation: async () => {
    const response = await api.get('/monte-carlo/explain');
    return response.data;
  },
};

export default monteCarloService;
