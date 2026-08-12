/**
 * SIP Service
 * Handles SIP calculator and plan management API calls
 */

import api from './api';

const sipService = {
  /**
   * Calculate SIP returns
   * @param {Object} data - Calculation parameters
   * @param {number} data.monthly_investment - Monthly investment amount
   * @param {number} data.annual_return_rate - Expected annual return percentage
   * @param {number} data.investment_duration_years - Investment duration in years
   * @returns {Promise} SIP calculation results
   */
  calculateSIP: async (data) => {
    const response = await api.post('/api/sip/calculate', data);
    return response.data;
  },

  /**
   * Calculate SIP returns with AI explanation
   * @param {Object} data - Calculation parameters
   * @returns {Promise} SIP calculation results with AI explanation
   */
  calculateSIPWithExplanation: async (data) => {
    const response = await api.post('/api/sip/explain', data);
    return response.data;
  },

  /**
   * Create a new SIP plan
   * @param {Object} planData - SIP plan details
   * @returns {Promise} Created SIP plan
   */
  createPlan: async (planData) => {
    const response = await api.post('/api/sip/plans', planData);
    return response.data;
  },

  /**
   * Get all SIP plans for authenticated user
   * @param {string} statusFilter - Optional status filter
   * @returns {Promise} List of SIP plans
   */
  getPlans: async (statusFilter = null) => {
    const params = statusFilter ? { status_filter: statusFilter } : {};
    const response = await api.get('/api/sip/plans', { params });
    return response.data;
  },

  /**
   * Get specific SIP plan by ID
   * @param {number} planId - Plan ID
   * @returns {Promise} SIP plan details
   */
  getPlan: async (planId) => {
    const response = await api.get(`/api/sip/plans/${planId}`);
    return response.data;
  },

  /**
   * Update SIP plan
   * @param {number} planId - Plan ID
   * @param {Object} updateData - Updated plan data
   * @returns {Promise} Updated SIP plan
   */
  updatePlan: async (planId, updateData) => {
    const response = await api.put(`/api/sip/plans/${planId}`, updateData);
    return response.data;
  },

  /**
   * Delete SIP plan
   * @param {number} planId - Plan ID
   * @returns {Promise} API response
   */
  deletePlan: async (planId) => {
    const response = await api.delete(`/api/sip/plans/${planId}`);
    return response.data;
  },
};

export default sipService;
