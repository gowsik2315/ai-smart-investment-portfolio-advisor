/**
 * Risk Assessment Page
 * Displays automated risk profile based on financial profile
 */

import React, { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import ReactMarkdown from 'react-markdown';
import Card from '../components/common/Card';
import Button from '../components/common/Button';
import Loading from '../components/common/Loading';
import RiskGauge from '../components/common/RiskGauge';
import riskService from '../services/riskService';
import profileService from '../services/profileService';
import recommendationService from '../services/recommendationService';

const RiskAssessment = () => {
  const navigate = useNavigate();
  const [riskProfile, setRiskProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [calculating, setCalculating] = useState(false);
  const [error, setError] = useState('');
  const [hasFinancialProfile, setHasFinancialProfile] = useState(false);
  
  // AI explanation state
  const [aiExplanation, setAiExplanation] = useState('');
  const [aiLoading, setAiLoading] = useState(false);
  const [aiError, setAiError] = useState('');

  useEffect(() => {
    fetchRiskProfile();
  }, []);

  const fetchRiskProfile = async () => {
    try {
      // First check if financial profile exists
      try {
        await profileService.getProfile();
        setHasFinancialProfile(true);
      } catch (err) {
        setHasFinancialProfile(false);
        setLoading(false);
        return;
      }

      // Then try to get risk profile
      const data = await riskService.getRiskProfile();
      setRiskProfile(data);
      
      // Use cached AI explanation from response if available
      if (data && data.ai_explanation) {
        setAiExplanation(data.ai_explanation);
      }
    } catch (err) {
      if (err.response?.status === 404) {
        // Risk profile doesn't exist yet, that's okay
        console.log('No risk profile found');
      } else {
        setError('Error loading risk profile');
      }
    } finally {
      setLoading(false);
    }
  };

  const fetchAIExplanation = async () => {
    setAiLoading(true);
    setAiError('');
    setAiExplanation('');

    try {
      const data = await riskService.explainRiskProfile();
      if (data.ai_available && data.ai_explanation) {
        setAiExplanation(data.ai_explanation);
      } else {
        setAiError('AI insights are currently unavailable.');
      }
    } catch (err) {
      console.error('AI explanation error:', err);
      setAiError('AI insights are currently unavailable.');
    } finally {
      setAiLoading(false);
    }
  };

  const handleCalculateRisk = async () => {
    setCalculating(true);
    setError('');

    try {
      const data = await riskService.calculateRiskProfile();
      setRiskProfile(data);
      
      // Fetch AI explanation after calculation (will be generated and cached by backend)
      fetchAIExplanation();
      
      // Automatically generate portfolio recommendation after risk calculation
      try {
        await recommendationService.generateRecommendation();
        console.log('Portfolio recommendation generated successfully');
      } catch (recErr) {
        console.error('Failed to generate portfolio recommendation:', recErr);
        // Don't show error to user, just log it
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to calculate risk profile');
    } finally {
      setCalculating(false);
    }
  };

  if (loading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <Loading message="Loading risk profile..." />
      </div>
    );
  }

  // If no financial profile exists
  if (!hasFinancialProfile) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-3xl mx-auto">
          <div className="mb-8">
            <h1>Risk Assessment</h1>
            <p className="text-secondary-600">
              Automated risk profiling based on your financial profile
            </p>
          </div>

          <Card>
            <div className="text-center py-12">
              <div className="w-16 h-16 bg-yellow-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-3xl">⚠️</span>
              </div>
              <h3 className="text-xl font-semibold mb-2">Financial Profile Required</h3>
              <p className="text-secondary-600 mb-6">
                You need to create your financial profile before we can calculate your risk profile
              </p>
              <Link to="/profile">
                <Button variant="primary">Create Financial Profile</Button>
              </Link>
            </div>
          </Card>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-5xl mx-auto">
        <div className="mb-8">
          <h1>Risk Assessment</h1>
          <p className="text-secondary-600">
            Automated risk profiling based on your financial profile
          </p>
        </div>

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-6">
            {error}
          </div>
        )}

        {/* If no risk profile exists yet */}
        {!riskProfile && (
          <Card>
            <div className="text-center py-12">
              <div className="w-16 h-16 bg-primary-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-3xl">📊</span>
              </div>
              <h3 className="text-xl font-semibold mb-2">Calculate Your Risk Profile</h3>
              <p className="text-secondary-600 mb-6">
                We'll automatically analyze your financial profile to determine your investment risk capacity
              </p>
              <Button 
                variant="primary" 
                onClick={handleCalculateRisk}
                disabled={calculating}
              >
                {calculating ? 'Calculating...' : 'Calculate Risk Profile'}
              </Button>
            </div>
          </Card>
        )}

        {/* If risk profile exists */}
        {riskProfile && (
          <>
            {/* Risk Score Gauge */}
            <Card className="mb-6">
              <div className="text-center py-8">
                <h2 className="text-2xl font-bold mb-6">Your Risk Profile</h2>
                <RiskGauge score={riskProfile.risk_score} size={280} />
                <div className="mt-6">
                  <Button 
                    variant="outline" 
                    onClick={handleCalculateRisk}
                    disabled={calculating}
                  >
                    {calculating ? 'Recalculating...' : 'Recalculate Risk Profile'}
                  </Button>
                </div>
              </div>
            </Card>

            {/* Explanation */}
            <Card title="Risk Profile Analysis">
              {aiLoading ? (
                <div className="flex items-center justify-center py-8">
                  <Loading message="Generating AI insights..." />
                </div>
              ) : aiError ? (
                <div className="text-center py-6">
                  <p className="text-secondary-600 mb-4">{aiError}</p>
                  <Button variant="outline" onClick={fetchAIExplanation} size="sm">
                    Retry AI Explanation
                  </Button>
                </div>
              ) : aiExplanation ? (
                <div className="prose max-w-none">
                  <div className="bg-gradient-to-r from-blue-50 to-purple-50 border-l-4 border-blue-500 px-4 py-3 mb-4 rounded">
                    <div className="flex items-center gap-2 mb-2">
                      <span className="text-xl">🤖</span>
                      <span className="font-semibold text-blue-900">AI-Powered Analysis</span>
                    </div>
                  </div>
                  <div className="text-secondary-700 leading-relaxed">
                    <ReactMarkdown>
                      {aiExplanation}
                    </ReactMarkdown>
                  </div>
                </div>
              ) : (
                <p className="text-secondary-700 whitespace-pre-line">
                  {riskProfile.explanation}
                </p>
              )}
            </Card>

            {/* Investment Recommendations */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-6">
              <Card>
                <div className="text-center">
                  <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-3">
                    <span className="text-2xl">📈</span>
                  </div>
                  <h3 className="font-semibold mb-2">Equity Allocation</h3>
                  <p className="text-3xl font-bold text-blue-600">
                    {riskProfile.investor_type === 'Conservative' ? '30%' :
                     riskProfile.investor_type === 'Moderate' ? '50%' : '70%'}
                  </p>
                  <p className="text-sm text-secondary-600 mt-2">
                    High growth potential with volatility
                  </p>
                </div>
              </Card>

              <Card>
                <div className="text-center">
                  <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-3">
                    <span className="text-2xl">🏦</span>
                  </div>
                  <h3 className="font-semibold mb-2">Debt Allocation</h3>
                  <p className="text-3xl font-bold text-green-600">
                    {riskProfile.investor_type === 'Conservative' ? '60%' :
                     riskProfile.investor_type === 'Moderate' ? '40%' : '20%'}
                  </p>
                  <p className="text-sm text-secondary-600 mt-2">
                    Stable returns with lower risk
                  </p>
                </div>
              </Card>

              <Card>
                <div className="text-center">
                  <div className="w-12 h-12 bg-yellow-100 rounded-full flex items-center justify-center mx-auto mb-3">
                    <span className="text-2xl">🥇</span>
                  </div>
                  <h3 className="font-semibold mb-2">Gold Allocation</h3>
                  <p className="text-3xl font-bold text-yellow-600">10%</p>
                  <p className="text-sm text-secondary-600 mt-2">
                    Hedge against inflation
                  </p>
                </div>
              </Card>
            </div>

            {/* Next Steps */}
            <Card className="mt-6">
              <h3 className="text-lg font-semibold mb-4">Next Steps</h3>
              <div className="space-y-3">
                <div className="flex items-start gap-3 p-3 bg-primary-50 rounded-lg">
                  <span className="text-2xl">💼</span>
                  <div>
                    <h4 className="font-semibold">View Portfolio Recommendation</h4>
                    <p className="text-sm text-secondary-600">
                      Get personalized asset allocation strategy based on your risk profile
                    </p>
                    <Link to="/portfolio-recommendation" className="text-primary-600 text-sm font-medium hover:underline">
                      View Recommendations →
                    </Link>
                  </div>
                </div>

                <div className="flex items-start gap-3 p-3 bg-green-50 rounded-lg">
                  <span className="text-2xl">💰</span>
                  <div>
                    <h4 className="font-semibold">Build Your Portfolio</h4>
                    <p className="text-sm text-secondary-600">
                      Use this risk profile to create a balanced investment portfolio
                    </p>
                    <Link to="/portfolio" className="text-green-600 text-sm font-medium hover:underline">
                      Go to Portfolio →
                    </Link>
                  </div>
                </div>

                <div className="flex items-start gap-3 p-3 bg-blue-50 rounded-lg">
                  <span className="text-2xl">📊</span>
                  <div>
                    <h4 className="font-semibold">Start SIP</h4>
                    <p className="text-sm text-secondary-600">
                      Plan systematic investments aligned with your risk profile
                    </p>
                    <Link to="/sip-planner" className="text-blue-600 text-sm font-medium hover:underline">
                      Plan SIP →
                    </Link>
                  </div>
                </div>

                <div className="flex items-start gap-3 p-3 bg-secondary-50 rounded-lg">
                  <span className="text-2xl">👤</span>
                  <div>
                    <h4 className="font-semibold">Update Financial Profile</h4>
                    <p className="text-sm text-secondary-600">
                      Your risk profile will automatically update when you change your financial details
                    </p>
                    <Link to="/profile" className="text-secondary-600 text-sm font-medium hover:underline">
                      Edit Profile →
                    </Link>
                  </div>
                </div>
              </div>
            </Card>
          </>
        )}
      </div>
    </div>
  );
};

export default RiskAssessment;
