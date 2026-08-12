/**
 * Financial Profile Page
 * Form to collect user financial information
 */

import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Card from '../components/common/Card';
import Input from '../components/common/Input';
import Select from '../components/common/Select';
import Button from '../components/common/Button';
import Loading from '../components/common/Loading';
import profileService from '../services/profileService';
import riskService from '../services/riskService';

const FinancialProfile = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [fetchLoading, setFetchLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [isUpdate, setIsUpdate] = useState(false);
  
  const [formData, setFormData] = useState({
    age: '',
    monthly_income: '',
    monthly_savings: '',
    investment_horizon: '',
    risk_tolerance: '',
    financial_goal: '',
  });

  const [formErrors, setFormErrors] = useState({});

  // Investment horizon options
  const investmentHorizons = [
    '1-3 Years',
    '3-5 Years',
    '5-10 Years',
    '10+ Years'
  ];

  // Risk tolerance options with descriptions
  const riskTolerances = [
    { value: 'Low', label: 'Low - Prefer stable, predictable returns' },
    { value: 'Medium', label: 'Medium - Can accept moderate fluctuations' },
    { value: 'High', label: 'High - Can handle significant volatility' }
  ];

  // Financial goal options
  const financialGoals = [
    'Wealth Creation',
    'Retirement',
    'House Purchase',
    'Education',
    'Emergency Fund'
  ];

  // Fetch existing profile on mount
  useEffect(() => {
    fetchProfile();
  }, []);

  const fetchProfile = async () => {
    try {
      const profile = await profileService.getProfile();
      
      if (profile) {
        setFormData({
          age: profile.age || '',
          monthly_income: profile.monthly_income || '',
          monthly_savings: profile.monthly_savings || '',
          investment_horizon: profile.investment_horizon || '',
          risk_tolerance: profile.risk_tolerance || '',
          financial_goal: profile.financial_goal || '',
        });
        setIsUpdate(true);
      }
    } catch (err) {
      // Profile doesn't exist yet, that's okay
      if (err.response?.status !== 404) {
        console.error('Error fetching profile:', err);
      }
    } finally {
      setFetchLoading(false);
    }
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: value,
    });
    // Clear field error on change
    if (formErrors[name]) {
      setFormErrors({
        ...formErrors,
        [name]: null,
      });
    }
    setError('');
    setSuccess('');
  };

  const validateForm = () => {
    const errors = {};

    // Age validation
    const age = parseInt(formData.age);
    if (!formData.age || age < 18 || age > 100) {
      errors.age = 'Age must be between 18 and 100';
    }

    // Monthly income validation
    const income = parseFloat(formData.monthly_income);
    if (!formData.monthly_income || income <= 0) {
      errors.monthly_income = 'Monthly income must be greater than 0';
    }

    // Monthly savings validation
    const savings = parseFloat(formData.monthly_savings);
    if (formData.monthly_savings === '' || savings < 0) {
      errors.monthly_savings = 'Monthly savings cannot be negative';
    } else if (savings > income) {
      errors.monthly_savings = 'Monthly savings cannot exceed monthly income';
    }

    // Required field validation
    if (!formData.investment_horizon) {
      errors.investment_horizon = 'Please select an investment horizon';
    }
    if (!formData.risk_tolerance) {
      errors.risk_tolerance = 'Please select your risk tolerance';
    }
    if (!formData.financial_goal) {
      errors.financial_goal = 'Please select your financial goal';
    }

    setFormErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setSuccess('');

    // Validate form
    if (!validateForm()) {
      setLoading(false);
      setError('Please fix the errors in the form');
      return;
    }

    try {
      // Convert string values to numbers
      const profileData = {
        age: parseInt(formData.age),
        monthly_income: parseFloat(formData.monthly_income),
        monthly_savings: parseFloat(formData.monthly_savings),
        investment_horizon: formData.investment_horizon,
        risk_tolerance: formData.risk_tolerance,
        financial_goal: formData.financial_goal,
      };

      if (isUpdate) {
        await profileService.updateProfile(profileData);
        setSuccess('Financial profile updated successfully!');
      } else {
        await profileService.createProfile(profileData);
        setSuccess('Financial profile created successfully!');
        setIsUpdate(true);
      }
      
      // Automatically calculate risk profile after saving financial profile
      try {
        await riskService.calculateRiskProfile();
        console.log('Risk profile calculated successfully');
      } catch (riskErr) {
        console.error('Failed to calculate risk profile:', riskErr);
        // Don't show error to user, just log it
      }
      
      // Redirect to risk assessment page to show results after 2 seconds
      setTimeout(() => {
        navigate('/risk-assessment');
      }, 2000);
      
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to save profile');
    } finally {
      setLoading(false);
    }
  };

  if (fetchLoading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <Loading message="Loading profile..." />
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-3xl mx-auto">
        <div className="mb-8">
          <h1>{isUpdate ? 'Update' : 'Create'} Financial Profile</h1>
          <p className="text-secondary-600">
            Tell us about your financial situation to get personalized recommendations
          </p>
        </div>

        <Card>
          {success && (
            <div className="bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded-lg mb-6">
              {success}
            </div>
          )}

          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-6">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit}>
            {/* Age */}
            <Input
              label="Age"
              type="number"
              name="age"
              value={formData.age}
              onChange={handleChange}
              placeholder="Enter your age"
              required
              min="18"
              max="100"
              error={formErrors.age}
            />

            {/* Monthly Income */}
            <Input
              label="Monthly Income (₹)"
              type="number"
              name="monthly_income"
              value={formData.monthly_income}
              onChange={handleChange}
              placeholder="Enter your monthly income"
              required
              min="0"
              step="0.01"
              error={formErrors.monthly_income}
            />

            {/* Monthly Savings */}
            <Input
              label="Monthly Savings (₹)"
              type="number"
              name="monthly_savings"
              value={formData.monthly_savings}
              onChange={handleChange}
              placeholder="Enter your monthly savings"
              required
              min="0"
              step="0.01"
              error={formErrors.monthly_savings}
            />

            {/* Investment Horizon */}
            <Select
              label="Investment Horizon"
              name="investment_horizon"
              value={formData.investment_horizon}
              onChange={handleChange}
              options={investmentHorizons}
              required
              placeholder="Select investment horizon"
              helpText="How long do you plan to invest?"
              error={formErrors.investment_horizon}
            />

            {/* Risk Tolerance */}
            <Select
              label="Risk Tolerance"
              name="risk_tolerance"
              value={formData.risk_tolerance}
              onChange={handleChange}
              options={riskTolerances}
              required
              placeholder="Select risk tolerance"
              helpText="How comfortable are you with market fluctuations?"
              error={formErrors.risk_tolerance}
            />

            {/* Financial Goal */}
            <Select
              label="Financial Goal"
              name="financial_goal"
              value={formData.financial_goal}
              onChange={handleChange}
              options={financialGoals}
              required
              placeholder="Select financial goal"
              helpText="What is your primary investment objective?"
              error={formErrors.financial_goal}
            />

            {/* Financial Summary - Show if data is available */}
            {formData.monthly_income && formData.monthly_savings && (
              <div className="mb-6 p-4 bg-gradient-to-r from-primary-50 to-secondary-50 rounded-lg border border-primary-200">
                <h3 className="text-sm font-semibold text-secondary-700 mb-3">Financial Summary</h3>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <p className="text-xs text-secondary-600">Savings Rate</p>
                    <p className="text-lg font-bold text-primary-600">
                      {((parseFloat(formData.monthly_savings) / parseFloat(formData.monthly_income)) * 100).toFixed(1)}%
                    </p>
                  </div>
                  <div>
                    <p className="text-xs text-secondary-600">Annual Savings</p>
                    <p className="text-lg font-bold text-primary-600">
                      ₹{(parseFloat(formData.monthly_savings) * 12).toLocaleString()}
                    </p>
                  </div>
                  <div>
                    <p className="text-xs text-secondary-600">Monthly Expenses</p>
                    <p className="text-lg font-bold text-secondary-600">
                      ₹{(parseFloat(formData.monthly_income) - parseFloat(formData.monthly_savings)).toLocaleString()}
                    </p>
                  </div>
                  <div>
                    <p className="text-xs text-secondary-600">Expense Ratio</p>
                    <p className="text-lg font-bold text-secondary-600">
                      {(((parseFloat(formData.monthly_income) - parseFloat(formData.monthly_savings)) / parseFloat(formData.monthly_income)) * 100).toFixed(1)}%
                    </p>
                  </div>
                </div>
              </div>
            )}

            {/* Submit Button */}
            <div className="flex gap-4">
              <Button
                type="submit"
                variant="primary"
                className="flex-1"
                disabled={loading}
              >
                {loading ? 'Saving...' : isUpdate ? 'Update Profile' : 'Create Profile'}
              </Button>
              
              <Button
                type="button"
                variant="outline"
                onClick={() => navigate('/dashboard')}
                disabled={loading}
              >
                Cancel
              </Button>
            </div>
          </form>
        </Card>
      </div>
    </div>
  );
};

export default FinancialProfile;
