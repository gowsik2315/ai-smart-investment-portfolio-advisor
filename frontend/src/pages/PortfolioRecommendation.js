/**
 * Portfolio Recommendation Page
 * Displays automated portfolio allocation recommendations
 */

import React, { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import ReactMarkdown from 'react-markdown';
import Card from '../components/common/Card';
import Button from '../components/common/Button';
import Loading from '../components/common/Loading';
import PieChart from '../components/common/PieChart';
import recommendationService from '../services/recommendationService';
import riskService from '../services/riskService';

const PortfolioRecommendation = () => {
  const navigate = useNavigate();
  const [recommendation, setRecommendation] = useState(null);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState('');
  const [hasRiskProfile, setHasRiskProfile] = useState(false);

  // AI explanation state
  const [aiExplanation, setAiExplanation] = useState('');
  const [aiLoading, setAiLoading] = useState(false);
  const [aiError, setAiError] = useState('');

  useEffect(() => {
    fetchRecommendation();
  }, []);

  const fetchRecommendation = async () => {
    try {
      // First check if risk profile exists
      try {
        await riskService.getRiskProfile();
        setHasRiskProfile(true);
      } catch (err) {
        setHasRiskProfile(false);
        setLoading(false);
        return;
      }

      // Then try to get recommendation
      const data = await recommendationService.getRecommendation();
      setRecommendation(data);
      
      // Use cached AI explanation from response if available
      if (data && data.ai_explanation) {
        setAiExplanation(data.ai_explanation);
      } else if (data) {
        // If no cached AI, fetch it (will be generated and cached by backend)
        fetchAIExplanation();
      }
    } catch (err) {
      if (err.response?.status === 404) {
        // Recommendation doesn't exist yet, that's okay
        console.log('No recommendation found');
      } else {
        setError('Error loading portfolio recommendation');
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
      const data = await recommendationService.explainRecommendation();
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

  const handleGenerateRecommendation = async () => {
    setGenerating(true);
    setError('');

    try {
      const data = await recommendationService.generateRecommendation();
      setRecommendation(data);
      
      // Automatically fetch AI explanation after generation
      fetchAIExplanation();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to generate recommendation');
    } finally {
      setGenerating(false);
    }
  };

  if (loading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <Loading message="Loading portfolio recommendation..." />
      </div>
    );
  }

  // If no risk profile exists
  if (!hasRiskProfile) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-3xl mx-auto">
          <div className="mb-8">
            <h1>Portfolio Recommendation</h1>
            <p className="text-secondary-600">
              Automated asset allocation based on your risk profile
            </p>
          </div>

          <Card>
            <div className="text-center py-12">
              <div className="w-16 h-16 bg-yellow-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-3xl">⚠️</span>
              </div>
              <h3 className="text-xl font-semibold mb-2">Risk Profile Required</h3>
              <p className="text-secondary-600 mb-6">
                You need to complete your risk assessment before we can generate portfolio recommendations
              </p>
              <Link to="/risk-assessment">
                <Button variant="primary">Take Risk Assessment</Button>
              </Link>
            </div>
          </Card>
        </div>
      </div>
    );
  }

  // Prepare pie chart data
  const pieChartData = recommendation ? [
    { label: 'Stocks', value: recommendation.stocks_percent, color: '#3b82f6' },
    { label: 'Mutual Funds', value: recommendation.mutual_funds_percent, color: '#10b981' },
    { label: 'Gold', value: recommendation.gold_percent, color: '#f59e0b' },
    { label: 'Emergency Fund', value: recommendation.emergency_percent, color: '#ef4444' },
  ] : [];

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-6xl mx-auto">
        <div className="mb-8">
          <h1>Portfolio Recommendation</h1>
          <p className="text-secondary-600">
            Personalized asset allocation strategy based on your risk profile
          </p>
        </div>

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-6">
            {error}
          </div>
        )}

        {/* If no recommendation exists yet */}
        {!recommendation && (
          <Card>
            <div className="text-center py-12">
              <div className="w-16 h-16 bg-primary-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-3xl">💼</span>
              </div>
              <h3 className="text-xl font-semibold mb-2">Generate Your Portfolio Recommendation</h3>
              <p className="text-secondary-600 mb-6">
                We'll create a personalized asset allocation strategy based on your risk profile
              </p>
              <Button 
                variant="primary" 
                onClick={handleGenerateRecommendation}
                disabled={generating}
              >
                {generating ? 'Generating...' : 'Generate Recommendation'}
              </Button>
            </div>
          </Card>
        )}

        {/* If recommendation exists */}
        {recommendation && (
          <>
            {/* Pie Chart */}
            <Card className="mb-6">
              <div className="text-center py-8">
                <h2 className="text-2xl font-bold mb-6">Your Asset Allocation</h2>
                <PieChart data={pieChartData} size={320} />
                <div className="mt-6">
                  <Button 
                    variant="outline" 
                    onClick={handleGenerateRecommendation}
                    disabled={generating}
                  >
                    {generating ? 'Regenerating...' : 'Regenerate Recommendation'}
                  </Button>
                </div>
              </div>
            </Card>

            {/* Allocation Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
              <Card>
                <div className="text-center">
                  <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-3">
                    <span className="text-2xl">📈</span>
                  </div>
                  <h3 className="font-semibold mb-2">Stocks</h3>
                  <p className="text-3xl font-bold text-blue-600">
                    {recommendation.stocks_percent}%
                  </p>
                  <p className="text-sm text-secondary-600 mt-2">
                    Direct equity investments
                  </p>
                </div>
              </Card>

              <Card>
                <div className="text-center">
                  <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-3">
                    <span className="text-2xl">📊</span>
                  </div>
                  <h3 className="font-semibold mb-2">Mutual Funds</h3>
                  <p className="text-3xl font-bold text-green-600">
                    {recommendation.mutual_funds_percent}%
                  </p>
                  <p className="text-sm text-secondary-600 mt-2">
                    Diversified fund investments
                  </p>
                </div>
              </Card>

              <Card>
                <div className="text-center">
                  <div className="w-12 h-12 bg-yellow-100 rounded-full flex items-center justify-center mx-auto mb-3">
                    <span className="text-2xl">🥇</span>
                  </div>
                  <h3 className="font-semibold mb-2">Gold</h3>
                  <p className="text-3xl font-bold text-yellow-600">
                    {recommendation.gold_percent}%
                  </p>
                  <p className="text-sm text-secondary-600 mt-2">
                    Precious metal allocation
                  </p>
                </div>
              </Card>

              <Card>
                <div className="text-center">
                  <div className="w-12 h-12 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-3">
                    <span className="text-2xl">🛡️</span>
                  </div>
                  <h3 className="font-semibold mb-2">Emergency Fund</h3>
                  <p className="text-3xl font-bold text-red-600">
                    {recommendation.emergency_percent}%
                  </p>
                  <p className="text-sm text-secondary-600 mt-2">
                    Liquid safety net
                  </p>
                </div>
              </Card>
            </div>

            {/* Recommendation Summary */}
            <Card title="AI-Powered Portfolio Analysis">
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
                  <div className="bg-gradient-to-r from-green-50 to-blue-50 border-l-4 border-green-500 px-4 py-3 mb-4 rounded">
                    <div className="flex items-center gap-2 mb-2">
                      <span className="text-xl">🤖</span>
                      <span className="font-semibold text-green-900">AI-Powered Recommendation</span>
                    </div>
                  </div>
                  <div className="text-secondary-700 leading-relaxed">
                    <ReactMarkdown>
                      {aiExplanation}
                    </ReactMarkdown>
                  </div>
                </div>
              ) : (
                <div className="prose max-w-none">
                  <pre className="text-secondary-700 whitespace-pre-wrap font-sans text-sm leading-relaxed">
                    {recommendation.recommendation_summary}
                  </pre>
                </div>
              )}
            </Card>

            {/* Next Steps */}
            <Card className="mt-6">
              <h3 className="text-lg font-semibold mb-4">Ready to Invest?</h3>
              <div className="space-y-3">
                <div className="flex items-start gap-3 p-3 bg-blue-50 rounded-lg">
                  <span className="text-2xl">🎯</span>
                  <div>
                    <h4 className="font-semibold">Start SIP</h4>
                    <p className="text-sm text-secondary-600">
                      Set up systematic investment plans aligned with your allocation
                    </p>
                    <Link to="/sip-planner" className="text-blue-600 text-sm font-medium hover:underline">
                      Plan Your SIP →
                    </Link>
                  </div>
                </div>

                <div className="flex items-start gap-3 p-3 bg-green-50 rounded-lg">
                  <span className="text-2xl">💼</span>
                  <div>
                    <h4 className="font-semibold">Build Portfolio</h4>
                    <p className="text-sm text-secondary-600">
                      Add specific investments to your portfolio
                    </p>
                    <Link to="/portfolio" className="text-green-600 text-sm font-medium hover:underline">
                      Manage Portfolio →
                    </Link>
                  </div>
                </div>

                <div className="flex items-start gap-3 p-3 bg-secondary-50 rounded-lg">
                  <span className="text-2xl">📊</span>
                  <div>
                    <h4 className="font-semibold">Review Risk Profile</h4>
                    <p className="text-sm text-secondary-600">
                      Your recommendation updates automatically when risk profile changes
                    </p>
                    <Link to="/risk-assessment" className="text-secondary-600 text-sm font-medium hover:underline">
                      View Risk Profile →
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

export default PortfolioRecommendation;
