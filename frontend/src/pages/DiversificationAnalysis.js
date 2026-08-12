/**
 * Diversification Analysis Page
 * Displays portfolio diversification analysis with sector and asset concentration
 */

import React, { useState, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import { PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import Card from '../components/common/Card';
import Button from '../components/common/Button';
import Loading from '../components/common/Loading';
import diversificationService from '../services/diversificationService';

const COLORS = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6', '#EC4899', '#14B8A6', '#F97316'];

const DiversificationAnalysis = () => {
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);
  const [error, setError] = useState(null);
  const [sampleParams, setSampleParams] = useState({
    portfolio_value: 1000000,
    diversified: true,
  });

  // AI explanation state
  const [aiExplanation, setAiExplanation] = useState('');
  const [aiLoading, setAiLoading] = useState(false);
  const [aiError, setAiError] = useState('');

  useEffect(() => {
    fetchLatestAnalysis();
  }, []);

  const fetchLatestAnalysis = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await diversificationService.getLatestAnalysis();
      setAnalysis(data);
      
      // Use cached AI explanation from response if available
      if (data && data.ai_explanation) {
        setAiExplanation(data.ai_explanation);
      } else if (data) {
        // If no cached AI, fetch it (will be generated and cached by backend)
        fetchAIExplanation();
      }
    } catch (err) {
      if (err.response?.status === 404) {
        setError('No analysis found. Generate sample data or analyze your portfolio.');
      } else {
        setError(err.response?.data?.detail || 'Failed to fetch analysis');
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
      const data = await diversificationService.explainAnalysis();
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

  const handleGenerateAndAnalyze = async () => {
    setAnalyzing(true);
    setError(null);
    try {
      // Generate sample holdings
      const sampleData = await diversificationService.generateSampleHoldings(sampleParams);
      
      // Analyze the generated holdings
      const analysisResult = await diversificationService.analyzeDiversification(
        sampleData.holdings
      );
      
      setAnalysis(analysisResult);
      
      // Automatically fetch AI explanation after analysis
      fetchAIExplanation();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to generate and analyze data');
    } finally {
      setAnalyzing(false);
    }
  };

  const getScoreColor = (score) => {
    if (score >= 80) return '#10b981'; // Green
    if (score >= 60) return '#3b82f6'; // Blue
    if (score >= 40) return '#f59e0b'; // Yellow
    return '#ef4444'; // Red
  };

  const getScoreLabel = (score) => {
    if (score >= 80) return 'Excellent';
    if (score >= 60) return 'Good';
    if (score >= 40) return 'Fair';
    return 'Poor';
  };

  // Prepare data for charts
  const prepareSectorData = () => {
    if (!analysis) return [];
    return Object.entries(analysis.sector_concentration.sectors).map(([name, value]) => ({
      name,
      value: parseFloat(value)
    }));
  };

  const prepareAssetData = () => {
    if (!analysis) return [];
    return Object.entries(analysis.asset_concentration.assets).map(([name, value]) => ({
      name,
      value: parseFloat(value)
    }));
  };

  if (loading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="flex justify-center items-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <h1>Diversification Analysis</h1>
        <p className="text-secondary-600">
          Analyze sector and asset concentration in your portfolio
        </p>
      </div>

      {/* Error Message */}
      {error && (
        <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-red-800">{error}</p>
        </div>
      )}

      {/* Sample Data Generator */}
      <Card title="Generate Sample Portfolio Holdings" className="mb-6">
        <div className="space-y-4">
          <p className="text-sm text-secondary-600">
            Generate sample portfolio holdings to test diversification analysis.
          </p>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-secondary-700 mb-1">
                Portfolio Value (₹)
              </label>
              <input
                type="number"
                value={sampleParams.portfolio_value}
                onChange={(e) => setSampleParams({
                  ...sampleParams,
                  portfolio_value: parseFloat(e.target.value)
                })}
                className="w-full px-3 py-2 border border-secondary-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-secondary-700 mb-1">
                Portfolio Type
              </label>
              <select
                value={sampleParams.diversified}
                onChange={(e) => setSampleParams({
                  ...sampleParams,
                  diversified: e.target.value === 'true'
                })}
                className="w-full px-3 py-2 border border-secondary-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              >
                <option value="true">Well Diversified</option>
                <option value="false">Concentrated (Poor)</option>
              </select>
            </div>
          </div>
          
          <Button
            onClick={handleGenerateAndAnalyze}
            disabled={analyzing}
            className="w-full"
          >
            {analyzing ? 'Generating & Analyzing...' : 'Generate & Analyze Sample Data'}
          </Button>
        </div>
      </Card>

      {/* Analysis Results */}
      {analysis && (
        <>
          {/* Diversification Score Overview */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
            <Card className="lg:col-span-1">
              <h3 className="text-lg font-semibold mb-4">Diversification Score</h3>
              <div className="flex flex-col items-center">
                <div className="relative w-40 h-40 mb-4">
                  <svg className="w-full h-full transform -rotate-90">
                    <circle
                      cx="80"
                      cy="80"
                      r="70"
                      stroke="#e5e7eb"
                      strokeWidth="12"
                      fill="none"
                    />
                    <circle
                      cx="80"
                      cy="80"
                      r="70"
                      stroke={getScoreColor(analysis.diversification_score)}
                      strokeWidth="12"
                      fill="none"
                      strokeDasharray={`${(analysis.diversification_score / 100) * 439.8} 439.8`}
                      strokeLinecap="round"
                    />
                  </svg>
                  <div className="absolute inset-0 flex flex-col items-center justify-center">
                    <div className="text-4xl font-bold" style={{ color: getScoreColor(analysis.diversification_score) }}>
                      {analysis.diversification_score.toFixed(1)}
                    </div>
                    <div className="text-sm text-secondary-600">/ 100</div>
                  </div>
                </div>
                <div className="px-6 py-2 rounded-full border-2 font-semibold" style={{
                  color: getScoreColor(analysis.diversification_score),
                  backgroundColor: `${getScoreColor(analysis.diversification_score)}15`,
                  borderColor: getScoreColor(analysis.diversification_score)
                }}>
                  {getScoreLabel(analysis.diversification_score)} Diversification
                </div>
              </div>
            </Card>

            <Card className="lg:col-span-2">
              <h3 className="text-lg font-semibold mb-4">Portfolio Summary</h3>
              <div className="grid grid-cols-2 gap-4">
                <div className="p-4 bg-primary-50 rounded-lg">
                  <div className="text-sm text-secondary-600 mb-1">Total Holdings</div>
                  <div className="text-3xl font-bold text-primary-600">{analysis.num_holdings}</div>
                </div>
                <div className="p-4 bg-green-50 rounded-lg">
                  <div className="text-sm text-secondary-600 mb-1">Portfolio Value</div>
                  <div className="text-3xl font-bold text-green-600">
                    ₹{(analysis.total_value / 100000).toFixed(1)}L
                  </div>
                </div>
                <div className="p-4 bg-blue-50 rounded-lg">
                  <div className="text-sm text-secondary-600 mb-1">Sectors</div>
                  <div className="text-3xl font-bold text-blue-600">
                    {analysis.sector_concentration.num_sectors}
                  </div>
                </div>
                <div className="p-4 bg-purple-50 rounded-lg">
                  <div className="text-sm text-secondary-600 mb-1">Asset Types</div>
                  <div className="text-3xl font-bold text-purple-600">
                    {analysis.asset_concentration.num_asset_types}
                  </div>
                </div>
              </div>
            </Card>
          </div>

          {/* Warnings */}
          {analysis.warnings && analysis.warnings.length > 0 && (
            <Card title="⚠️ Concentration Warnings" className="mb-6">
              <div className="space-y-2">
                {analysis.warnings.map((warning, idx) => (
                  <div 
                    key={idx} 
                    className={`p-3 rounded-lg ${
                      warning.includes('✅') ? 'bg-green-50 text-green-800' : 'bg-yellow-50 text-yellow-800'
                    }`}
                  >
                    {warning}
                  </div>
                ))}
              </div>
            </Card>
          )}

          {/* Charts */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
            {/* Sector Concentration Chart */}
            <Card title="Sector Concentration">
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={prepareSectorData()}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, value }) => `${name}: ${value.toFixed(1)}%`}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {prepareSectorData().map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip formatter={(value) => `${value.toFixed(2)}%`} />
                </PieChart>
              </ResponsiveContainer>
              
              <div className="mt-4 p-3 bg-secondary-50 rounded-lg">
                <div className="text-sm font-medium text-secondary-700">Top Sector</div>
                <div className="text-xl font-bold text-primary-600">
                  {analysis.sector_concentration.top_sector}
                </div>
                <div className="text-sm text-secondary-600">
                  {analysis.sector_concentration.top_sector_percentage.toFixed(1)}% of portfolio
                </div>
              </div>
            </Card>

            {/* Asset Concentration Chart */}
            <Card title="Asset Type Concentration">
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={prepareAssetData()}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis />
                  <Tooltip formatter={(value) => `${value.toFixed(2)}%`} />
                  <Legend />
                  <Bar dataKey="value" fill="#3B82F6" name="Percentage" />
                </BarChart>
              </ResponsiveContainer>
              
              <div className="mt-4 p-3 bg-secondary-50 rounded-lg">
                <div className="text-sm font-medium text-secondary-700">Top Asset Type</div>
                <div className="text-xl font-bold text-primary-600">
                  {analysis.asset_concentration.top_asset}
                </div>
                <div className="text-sm text-secondary-600">
                  {analysis.asset_concentration.top_asset_percentage.toFixed(1)}% of portfolio
                </div>
              </div>
            </Card>
          </div>

          {/* Metrics Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
            <Card title="Concentration Metrics">
              <div className="space-y-3">
                <div className="flex justify-between items-center pb-2 border-b">
                  <span className="text-sm font-medium text-secondary-700">HHI Score</span>
                  <span className="font-semibold text-secondary-900">
                    {analysis.hhi_score.toFixed(2)}
                  </span>
                </div>
                <div className="flex justify-between items-center pb-2 border-b">
                  <span className="text-sm font-medium text-secondary-700">Sector Diversity</span>
                  <span className="font-semibold text-secondary-900">
                    {analysis.sector_concentration.num_sectors} sectors
                  </span>
                </div>
                <div className="flex justify-between items-center pb-2 border-b">
                  <span className="text-sm font-medium text-secondary-700">Asset Diversity</span>
                  <span className="font-semibold text-secondary-900">
                    {analysis.asset_concentration.num_asset_types} types
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm font-medium text-secondary-700">Total Holdings</span>
                  <span className="font-semibold text-secondary-900">
                    {analysis.num_holdings} positions
                  </span>
                </div>
              </div>
            </Card>

            <Card title="📋 Recommendations">
              <div className="space-y-2">
                {analysis.recommendations.map((rec, idx) => (
                  <div 
                    key={idx} 
                    className={`p-3 rounded-lg ${
                      rec.includes('✅') || rec.includes('👍') 
                        ? 'bg-green-50 text-green-800' 
                        : rec.includes('⚡')
                        ? 'bg-blue-50 text-blue-800'
                        : 'bg-orange-50 text-orange-800'
                    }`}
                  >
                    {rec}
                  </div>
                ))}
              </div>
            </Card>
          </div>

          {/* AI Insights Card */}
          <Card title="AI Diversification Insights" className="mb-6">
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
                <div className="bg-gradient-to-r from-green-50 to-teal-50 border-l-4 border-green-500 px-4 py-3 mb-4 rounded">
                  <div className="flex items-center gap-2 mb-2">
                    <span className="text-xl">🤖</span>
                    <span className="font-semibold text-green-900">AI-Powered Diversification Analysis</span>
                  </div>
                </div>
                <div className="text-secondary-700 leading-relaxed">
                  <ReactMarkdown>
                    {aiExplanation}
                  </ReactMarkdown>
                </div>
              </div>
            ) : null}
          </Card>

          {/* Action Buttons */}
          <div className="flex gap-4">
            <Button onClick={handleGenerateAndAnalyze} disabled={analyzing}>
              {analyzing ? 'Analyzing...' : 'Generate New Analysis'}
            </Button>
            <Button variant="outline" onClick={fetchLatestAnalysis}>
              Refresh
            </Button>
          </div>
        </>
      )}
    </div>
  );
};

export default DiversificationAnalysis;
