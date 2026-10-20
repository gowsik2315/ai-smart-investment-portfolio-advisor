/**
 * Portfolio Analytics Page
 * Displays portfolio risk analysis with metrics and visualizations
 */

import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import ReactMarkdown from 'react-markdown';
import { XAxis, YAxis, CartesianGrid, Tooltip, ReferenceLine, ResponsiveContainer, Area, AreaChart } from 'recharts';
import Card from '../components/common/Card';
import Button from '../components/common/Button';
import Loading from '../components/common/Loading';
import portfolioAnalysisService from '../services/portfolioAnalysisService';
import portfolioService from '../services/portfolioService';

const PortfolioAnalytics = () => {
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);
  const [error, setError] = useState(null);
  const [sampleParams, setSampleParams] = useState({
    initial_value: 100000,
    days: 252,
    volatility: 0.15,
    drift: 0.10,
  });

  // The user's real value series, and which source the analysis came from.
  const [valueSeries, setValueSeries] = useState(null);
  const [seriesMeta, setSeriesMeta] = useState(null);
  const [source, setSource] = useState(null);   // 'portfolio' | 'sample' | null

  // Which portfolio the series is scoped to. '' means all combined,
  // which is the default; scoping to one lets two strategies be compared.
  const [portfolios, setPortfolios] = useState([]);
  const [scopeId, setScopeId] = useState('');
  const [analysedScope, setAnalysedScope] = useState('');

  // AI explanation state
  const [aiExplanation, setAiExplanation] = useState('');
  const [aiLoading, setAiLoading] = useState(false);
  const [aiError, setAiError] = useState('');

  // Run once on mount. The fetchers are stable for the page's lifetime.
  useEffect(() => {
    fetchPortfolios();
    fetchValueSeries('');
    fetchLatestAnalysis();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const fetchPortfolios = async () => {
    try {
      setPortfolios(await portfolioService.listPortfolios());
    } catch (err) {
      setPortfolios([]);
    }
  };

  const handleScopeChange = async (event) => {
    const value = event.target.value;
    setScopeId(value);
    setValueSeries(null);
    await fetchValueSeries(value);
  };

  // Rebuild the user's real value series. Failing here is not a page
  // error: it only means the "my portfolio" option stays unavailable.
  const fetchValueSeries = async (portfolioId) => {
    try {
      const data = await portfolioService.getValueSeries('1y', portfolioId || null);
      setValueSeries(data.series || []);
      setSeriesMeta(data);
    } catch (err) {
      setValueSeries([]);
      setSeriesMeta(null);
    }
  };

  const handleAnalyzePortfolio = async () => {
    // The analyzer needs at least two points; never send fewer.
    if (!valueSeries || valueSeries.length < 2) return;

    setAnalyzing(true);
    setError(null);
    try {
      const result = await portfolioAnalysisService.analyzePortfolio(valueSeries);
      setAnalysis(result);
      setSource('portfolio');
      setAnalysedScope(scopeId);
      fetchAIExplanation();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to analyze your portfolio');
    } finally {
      setAnalyzing(false);
    }
  };

  const fetchLatestAnalysis = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await portfolioAnalysisService.getLatestAnalysis();
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
      const data = await portfolioAnalysisService.explainAnalysis();
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
      // Generate sample data
      const sampleData = await portfolioAnalysisService.generateSampleData(sampleParams);
      
      // Analyze the generated data
      const analysisResult = await portfolioAnalysisService.analyzePortfolio(
        sampleData.portfolio_data
      );
      
      setAnalysis(analysisResult);
      setSource('sample');

      // Automatically fetch AI explanation after analysis
      fetchAIExplanation();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to generate and analyze data');
    } finally {
      setAnalyzing(false);
    }
  };

  const getRiskColor = (riskLevel) => {
    const colors = {
      'Low': 'text-green-600 bg-green-50 border-green-200',
      'Moderate': 'text-yellow-600 bg-yellow-50 border-yellow-200',
      'High': 'text-orange-600 bg-orange-50 border-orange-200',
      'Very High': 'text-red-600 bg-red-50 border-red-200',
    };
    return colors[riskLevel] || colors['Moderate'];
  };

  const getRiskScoreColor = (score) => {
    if (score < 30) return '#10b981'; // Green
    if (score < 50) return '#f59e0b'; // Yellow
    if (score < 70) return '#f97316'; // Orange
    return '#ef4444'; // Red
  };

  const getMetricColor = (value, isPositive) => {
    if (isPositive) {
      return value >= 0 ? 'text-green-600' : 'text-red-600';
    }
    return value <= 0 ? 'text-green-600' : 'text-red-600';
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
        <h1>Portfolio Risk Analysis</h1>
        <p className="text-secondary-600">
          Comprehensive risk metrics and performance analysis
        </p>
      </div>

      {/* Error Message */}
      {error && (
        <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-red-800">{error}</p>
        </div>
      )}

      {/* Analyse the user's real portfolio */}
      <Card title="Analyse My Portfolio" className="mb-6">
        {portfolios.length > 1 && (
          <div className="mb-4">
            <label className="block text-sm font-medium text-secondary-700 mb-1">
              Which holdings?
            </label>
            <select
              value={scopeId}
              onChange={handleScopeChange}
              className="w-full px-3 py-2 border border-secondary-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            >
              <option value="">All portfolios combined ({portfolios.length})</option>
              {portfolios.map((p) => (
                <option key={p.id} value={p.id}>
                  {p.portfolio_name} only
                </option>
              ))}
            </select>
            <p className="mt-1 text-xs text-secondary-500">
              Scope to one portfolio to compare strategies; each is measured over its own
              history, so the periods may differ.
            </p>
          </div>
        )}

        {valueSeries === null ? (
          <p className="text-sm text-secondary-600">Rebuilding your portfolio history...</p>
        ) : valueSeries.length < 2 ? (
          <div className="text-sm text-secondary-600">
            <p className="mb-2">
              {seriesMeta?.note ||
                'Not enough history to measure risk from your portfolio yet.'}
            </p>
            <Link to="/portfolio" className="text-primary-600 hover:underline">
              Record transactions in My Portfolio →
            </Link>
            <p className="mt-2 text-secondary-500">
              Risk metrics need at least two days of price history for a holding with a
              ticker symbol. You can explore the analysis with sample data below.
            </p>
          </div>
        ) : (
          <div className="space-y-4">
            <p className="text-sm text-secondary-600">
              Measure volatility, Sharpe ratio and drawdown from your actual holdings,
              rebuilt over {valueSeries.length} trading days from{' '}
              {valueSeries[0].date} to {valueSeries[valueSeries.length - 1].date}.
            </p>

            <div className="p-3 bg-blue-50 border border-blue-200 rounded-lg text-blue-800 text-sm">
              <strong>Deposits and withdrawals are excluded.</strong> Each day's return is
              computed from price movement only, so buying more does not register as a
              gain. This is the time-weighted convention funds use, and it keeps the risk
              metrics about the investments rather than your saving pattern. It also means
              the chart below tracks <em>performance</em>, not the size of your portfolio.
            </div>

            {seriesMeta?.coverage &&
              seriesMeta.coverage.priced_value_percent < 100 && (
                <div className="p-3 bg-amber-50 border border-amber-200 rounded-lg text-amber-800 text-sm">
                  This covers{' '}
                  <strong>{seriesMeta.coverage.priced_value_percent}%</strong> of your
                  invested value.{' '}
                  {seriesMeta.excluded_holdings?.length > 0 && (
                    <>
                      {seriesMeta.excluded_holdings.join(', ')} ha
                      {seriesMeta.excluded_holdings.length === 1 ? 's' : 've'} no price
                      history and {seriesMeta.excluded_holdings.length === 1 ? 'is' : 'are'}{' '}
                      excluded — holding them at a flat value would make the portfolio look
                      less volatile than it is.
                    </>
                  )}
                </div>
              )}

            <div>
              <div className="flex items-baseline justify-between mb-1">
                <h4 className="text-sm font-semibold">
                  Performance index — not your balance
                </h4>
                <span className="text-xs text-secondary-500">
                  100 = {valueSeries[0].date}
                </span>
              </div>
              <p className="text-xs text-secondary-500 mb-2">
                How these holdings moved, as if the money had been invested on day one
                and never topped up. Your actual balance is on the{' '}
                <Link to="/portfolio" className="text-primary-600 hover:underline">
                  Portfolio page
                </Link>
                .
              </p>
              <ResponsiveContainer width="100%" height={200}>
                <AreaChart data={valueSeries}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" tick={{ fontSize: 11 }} minTickGap={40} />
                  <YAxis
                    tick={{ fontSize: 11 }}
                    domain={['auto', 'auto']}
                    tickFormatter={(v) => Number(v).toFixed(0)}
                  />
                  <Tooltip
                    formatter={(v) => [
                      `${Number(v).toFixed(2)}  (${v >= 100 ? '+' : ''}${(Number(v) - 100).toFixed(2)}%)`,
                      'Index',
                    ]}
                  />
                  <ReferenceLine
                    y={100}
                    stroke="#94a3b8"
                    strokeDasharray="4 4"
                    label={{ value: 'start', position: 'insideLeft', fontSize: 10, fill: '#64748b' }}
                  />
                  <Area type="monotone" dataKey="value" stroke="#3b82f6" fill="#bfdbfe" />
                </AreaChart>
              </ResponsiveContainer>
              <p className="text-xs text-secondary-500 mt-1">
                Latest: <strong>{valueSeries[valueSeries.length - 1].value.toFixed(2)}</strong>
                {' '}({(valueSeries[valueSeries.length - 1].value - 100) >= 0 ? '+' : ''}
                {(valueSeries[valueSeries.length - 1].value - 100).toFixed(2)}% since{' '}
                {valueSeries[0].date})
                {seriesMeta?.opening_value > 0 && (
                  <>
                    {' '}· 100 was worth ₹
                    {seriesMeta.opening_value.toLocaleString('en-IN', { maximumFractionDigits: 0 })}
                    {' '}that day
                  </>
                )}
              </p>
            </div>

            <Button onClick={handleAnalyzePortfolio} disabled={analyzing} className="w-full">
              {analyzing ? 'Analyzing...' : 'Analyse My Portfolio'}
            </Button>
          </div>
        )}
      </Card>

      {/* Sample Data Generator */}
      <Card title="Generate Sample Portfolio Data" className="mb-6">
        <div className="space-y-4">
          <p className="text-sm text-secondary-600">
            Not your portfolio — a synthetic price series for exploring the analysis.
          </p>
            
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <div>
                <label className="block text-sm font-medium text-secondary-700 mb-1">
                  Initial Value (₹)
                </label>
                <input
                  type="number"
                  value={sampleParams.initial_value}
                  onChange={(e) => setSampleParams({
                    ...sampleParams,
                    initial_value: parseFloat(e.target.value)
                  })}
                  className="w-full px-3 py-2 border border-secondary-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-secondary-700 mb-1">
                  Days (30-1260)
                </label>
                <input
                  type="number"
                  min="30"
                  max="1260"
                  value={sampleParams.days}
                  onChange={(e) => setSampleParams({
                    ...sampleParams,
                    days: parseInt(e.target.value)
                  })}
                  className="w-full px-3 py-2 border border-secondary-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-secondary-700 mb-1">
                  Volatility (0-1)
                </label>
                <input
                  type="number"
                  step="0.01"
                  min="0"
                  max="1"
                  value={sampleParams.volatility}
                  onChange={(e) => setSampleParams({
                    ...sampleParams,
                    volatility: parseFloat(e.target.value)
                  })}
                  className="w-full px-3 py-2 border border-secondary-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-secondary-700 mb-1">
                  Expected Return (0-1)
                </label>
                <input
                  type="number"
                  step="0.01"
                  min="-1"
                  max="1"
                  value={sampleParams.drift}
                  onChange={(e) => setSampleParams({
                    ...sampleParams,
                    drift: parseFloat(e.target.value)
                  })}
                  className="w-full px-3 py-2 border border-secondary-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                />
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
          {/* Which data produced the numbers below. Without this a
              sample-data risk score is indistinguishable from a real one. */}
          <div
            className={`mb-6 p-3 rounded-lg text-sm border ${
              source === 'portfolio'
                ? 'bg-green-50 border-green-200 text-green-800'
                : 'bg-blue-50 border-blue-200 text-blue-800'
            }`}
          >
            {source === 'portfolio' ? (
              <>
                <strong>
                  {analysedScope
                    ? portfolios.find((p) => String(p.id) === String(analysedScope))
                        ?.portfolio_name || 'Your portfolio'
                    : 'All portfolios combined'}
                  .
                </strong>{' '}
                Time-weighted from your real holdings, excluding deposits and withdrawals.
              </>
            ) : source === 'sample' ? (
              <>
                <strong>Sample data.</strong> A synthetic price series, not your
                portfolio.{' '}
                {valueSeries && valueSeries.length >= 2 && (
                  <button onClick={handleAnalyzePortfolio} className="underline">
                    Analyse my portfolio instead
                  </button>
                )}
              </>
            ) : (
              <>
                <strong>Saved analysis.</strong> Loaded from your last saved run; re-run
                either source above for current numbers.
              </>
            )}
          </div>

          {/* Risk Score Overview */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
            <Card className="lg:col-span-1">
              <h3 className="text-lg font-semibold mb-4">Risk Score</h3>
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
                      stroke={getRiskScoreColor(analysis.risk_score)}
                      strokeWidth="12"
                      fill="none"
                      strokeDasharray={`${(analysis.risk_score / 100) * 439.8} 439.8`}
                      strokeLinecap="round"
                    />
                  </svg>
                  <div className="absolute inset-0 flex flex-col items-center justify-center">
                    <div className="text-4xl font-bold" style={{ color: getRiskScoreColor(analysis.risk_score) }}>
                      {analysis.risk_score.toFixed(1)}
                    </div>
                    <div className="text-sm text-secondary-600">/ 100</div>
                  </div>
                </div>
                <div className={`px-6 py-2 rounded-full border-2 font-semibold ${getRiskColor(analysis.risk_level)}`}>
                  {analysis.risk_level} Risk
                </div>
              </div>
            </Card>

            <Card className="lg:col-span-2">
              <h3 className="text-lg font-semibold mb-4">Risk Interpretation</h3>
              <p className="text-secondary-700 mb-4">{analysis.interpretation.description}</p>
              
              <div className="mb-4">
                <h4 className="text-sm font-semibold text-secondary-700 mb-2">Characteristics:</h4>
                <ul className="list-disc list-inside space-y-1">
                  {analysis.interpretation.characteristics.map((char, idx) => (
                    <li key={idx} className="text-sm text-secondary-600">{char}</li>
                  ))}
                </ul>
              </div>
              
              <div>
                <h4 className="text-sm font-semibold text-secondary-700 mb-2">Recommendations:</h4>
                <ul className="list-disc list-inside space-y-1">
                  {analysis.interpretation.recommendations.map((rec, idx) => (
                    <li key={idx} className="text-sm text-secondary-600">{rec}</li>
                  ))}
                </ul>
              </div>
            </Card>
          </div>

          {/* Risk Metrics Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
            <Card>
              <div className="flex items-start justify-between mb-2">
                <h3 className="text-sm font-semibold text-secondary-700">Volatility</h3>
                <span className="text-2xl">📊</span>
              </div>
              <div className="text-3xl font-bold text-primary-600 mb-1">
                {analysis.volatility_percent.toFixed(2)}%
              </div>
              <p className="text-xs text-secondary-600">
                Annualized standard deviation of returns
              </p>
              <div className="mt-2 pt-2 border-t">
                <p className="text-xs text-secondary-500">
                  {analysis.volatility_percent < 10 ? 'Low volatility' :
                   analysis.volatility_percent < 20 ? 'Moderate volatility' :
                   analysis.volatility_percent < 30 ? 'High volatility' :
                   'Very high volatility'}
                </p>
              </div>
            </Card>

            <Card>
              <div className="flex items-start justify-between mb-2">
                <h3 className="text-sm font-semibold text-secondary-700">Sharpe Ratio</h3>
                <span className="text-2xl">📈</span>
              </div>
              <div className={`text-3xl font-bold mb-1 ${
                analysis.sharpe_ratio > 2 ? 'text-green-600' :
                analysis.sharpe_ratio > 1 ? 'text-yellow-600' :
                analysis.sharpe_ratio > 0 ? 'text-orange-600' :
                'text-red-600'
              }`}>
                {analysis.sharpe_ratio.toFixed(2)}
              </div>
              <p className="text-xs text-secondary-600">
                Risk-adjusted return metric
              </p>
              <div className="mt-2 pt-2 border-t">
                <p className="text-xs text-secondary-500">
                  {analysis.sharpe_ratio > 2 ? 'Excellent' :
                   analysis.sharpe_ratio > 1 ? 'Good' :
                   analysis.sharpe_ratio > 0 ? 'Fair' :
                   'Poor'} risk-adjusted returns
                </p>
              </div>
            </Card>

            <Card>
              <div className="flex items-start justify-between mb-2">
                <h3 className="text-sm font-semibold text-secondary-700">Max Drawdown</h3>
                <span className="text-2xl">📉</span>
              </div>
              <div className={`text-3xl font-bold mb-1 ${getMetricColor(analysis.max_drawdown_percent, false)}`}>
                {analysis.max_drawdown_percent.toFixed(2)}%
              </div>
              <p className="text-xs text-secondary-600">
                Largest peak-to-trough decline
              </p>
              <div className="mt-2 pt-2 border-t">
                <p className="text-xs text-secondary-500">
                  {Math.abs(analysis.max_drawdown_percent) < 10 ? 'Low drawdown' :
                   Math.abs(analysis.max_drawdown_percent) < 20 ? 'Moderate drawdown' :
                   Math.abs(analysis.max_drawdown_percent) < 30 ? 'High drawdown' :
                   'Severe drawdown'}
                </p>
              </div>
            </Card>

            <Card>
              <div className="flex items-start justify-between mb-2">
                <h3 className="text-sm font-semibold text-secondary-700">Total Return</h3>
                <span className="text-2xl">💰</span>
              </div>
              <div className={`text-3xl font-bold mb-1 ${getMetricColor(analysis.total_return, true)}`}>
                {analysis.total_return > 0 ? '+' : ''}{analysis.total_return.toFixed(2)}%
              </div>
              <p className="text-xs text-secondary-600">
                Overall portfolio return
              </p>
              <div className="mt-2 pt-2 border-t">
                <p className="text-xs text-secondary-500">
                  Avg: {analysis.average_return_percent.toFixed(2)}% annually
                </p>
              </div>
            </Card>
          </div>

          {/* Additional Metrics */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
            <Card title="Performance Metrics">
              <div className="space-y-3">
                <div className="flex justify-between items-center pb-2 border-b">
                  <span className="text-sm font-medium text-secondary-700">Average Return (Annual)</span>
                  <span className={`font-semibold ${getMetricColor(analysis.average_return_percent, true)}`}>
                    {analysis.average_return_percent > 0 ? '+' : ''}{analysis.average_return_percent.toFixed(2)}%
                  </span>
                </div>
                <div className="flex justify-between items-center pb-2 border-b">
                  <span className="text-sm font-medium text-secondary-700">Risk-Free Rate</span>
                  <span className="font-semibold text-secondary-900">
                    {(analysis.risk_free_rate * 100).toFixed(2)}%
                  </span>
                </div>
                <div className="flex justify-between items-center pb-2 border-b">
                  <span className="text-sm font-medium text-secondary-700">Excess Return</span>
                  <span className={`font-semibold ${getMetricColor(analysis.average_return_percent - (analysis.risk_free_rate * 100), true)}`}>
                    {(analysis.average_return_percent - (analysis.risk_free_rate * 100)).toFixed(2)}%
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm font-medium text-secondary-700">Return per Unit Risk</span>
                  <span className="font-semibold text-secondary-900">
                    {(analysis.average_return_percent / analysis.volatility_percent).toFixed(2)}
                  </span>
                </div>
              </div>
            </Card>

            <Card title="Analysis Details">
              <div className="space-y-3">
                <div className="flex justify-between items-center pb-2 border-b">
                  <span className="text-sm font-medium text-secondary-700">Data Points</span>
                  <span className="font-semibold text-secondary-900">{analysis.data_points}</span>
                </div>
                <div className="flex justify-between items-center pb-2 border-b">
                  <span className="text-sm font-medium text-secondary-700">Analysis Period</span>
                  <span className="font-semibold text-secondary-900">
                    {analysis.analysis_period_days} days
                  </span>
                </div>
                <div className="flex justify-between items-center pb-2 border-b">
                  <span className="text-sm font-medium text-secondary-700">Trading Days</span>
                  <span className="font-semibold text-secondary-900">
                    ~{Math.floor(analysis.analysis_period_days * 252 / 365)} days
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm font-medium text-secondary-700">Annualization Factor</span>
                  <span className="font-semibold text-secondary-900">√252</span>
                </div>
              </div>
            </Card>
          </div>

          {/* AI Insights Card */}
          <Card title="AI Risk Analysis" className="mb-6">
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
                <div className="bg-gradient-to-r from-blue-50 to-indigo-50 border-l-4 border-blue-500 px-4 py-3 mb-4 rounded">
                  <div className="flex items-center gap-2 mb-2">
                    <span className="text-xl">🤖</span>
                    <span className="font-semibold text-blue-900">AI-Powered Risk Insights</span>
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

export default PortfolioAnalytics;
