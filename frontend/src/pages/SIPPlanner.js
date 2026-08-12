/**
 * SIP Planner Page
 * SIP calculator with yearly growth chart and plan saving
 */

import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import ReactMarkdown from 'react-markdown';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import Card from '../components/common/Card';
import Input from '../components/common/Input';
import Button from '../components/common/Button';
import Loading from '../components/common/Loading';
import sipService from '../services/sipService';

const SIPPlanner = () => {
  // Calculator state
  const [monthlyInvestment, setMonthlyInvestment] = useState('5000');
  const [annualReturn, setAnnualReturn] = useState('12');
  const [duration, setDuration] = useState('10');
  
  // Results state
  const [results, setResults] = useState(null);
  const [calculating, setCalculating] = useState(false);
  const [error, setError] = useState('');
  
  // AI explanation state
  const [aiExplanation, setAiExplanation] = useState('');
  const [aiAvailable, setAiAvailable] = useState(false);
  const [aiLoading, setAiLoading] = useState(false);
  
  // Save plan state
  const [showSaveForm, setShowSaveForm] = useState(false);
  const [planName, setPlanName] = useState('');
  const [startDate, setStartDate] = useState(new Date().toISOString().split('T')[0]);
  const [saving, setSaving] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState(false);
  
  // Saved plans state
  const [savedPlans, setSavedPlans] = useState([]);
  const [loadingPlans, setLoadingPlans] = useState(true);

  useEffect(() => {
    fetchSavedPlans();
    loadLastCalculation(); // Load last calculation from localStorage
  }, []);

  const loadLastCalculation = () => {
    try {
      const lastCalc = localStorage.getItem('sipLastCalculation');
      if (lastCalc) {
        const calc = JSON.parse(lastCalc);
        setResults(calc.results);
        setMonthlyInvestment(calc.params.monthly_investment.toString());
        setAnnualReturn(calc.params.annual_return_rate.toString());
        setDuration(calc.params.investment_duration_years.toString());
        
        // Load AI explanation if available
        if (calc.aiExplanation) {
          setAiExplanation(calc.aiExplanation);
          setAiAvailable(true);
        }
      }
    } catch (err) {
      console.log('No previous calculation found');
    }
  };

  const saveCalculationToStorage = (results, params, aiExplanation = '') => {
    try {
      localStorage.setItem('sipLastCalculation', JSON.stringify({
        results,
        params,
        aiExplanation,
        timestamp: new Date().toISOString()
      }));
    } catch (err) {
      console.error('Failed to save calculation:', err);
    }
  };

  const fetchSavedPlans = async () => {
    try {
      const plans = await sipService.getPlans();
      setSavedPlans(plans);
    } catch (err) {
      console.log('No saved plans found');
    } finally {
      setLoadingPlans(false);
    }
  };

  const handleCalculate = async (e) => {
    e.preventDefault();
    setCalculating(true);
    setError('');
    setSaveSuccess(false);
    setAiExplanation('');
    setAiAvailable(false);
    setAiLoading(false);

    try {
      const data = {
        monthly_investment: parseFloat(monthlyInvestment),
        annual_return_rate: parseFloat(annualReturn),
        investment_duration_years: parseInt(duration)
      };

      // First, get instant calculation results (no AI)
      const result = await sipService.calculateSIP(data);
      setResults(result);
      setCalculating(false);
      
      // Save calculation to localStorage for persistence
      saveCalculationToStorage(result, data);
      
      // Then, fetch AI explanation in the background
      setAiLoading(true);
      fetchAIExplanation(data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to calculate SIP');
      setCalculating(false);
    }
  };

  const fetchAIExplanation = async (data) => {
    try {
      const result = await sipService.calculateSIPWithExplanation(data);
      
      // Set AI explanation if available
      if (result.ai_explanation) {
        setAiExplanation(result.ai_explanation);
        setAiAvailable(true);
        
        // Update localStorage with AI explanation
        try {
          const lastCalc = localStorage.getItem('sipLastCalculation');
          if (lastCalc) {
            const calc = JSON.parse(lastCalc);
            calc.aiExplanation = result.ai_explanation;
            localStorage.setItem('sipLastCalculation', JSON.stringify(calc));
          }
        } catch (err) {
          console.error('Failed to update AI in storage:', err);
        }
      }
    } catch (err) {
      console.log('AI explanation unavailable:', err);
      setAiAvailable(false);
    } finally {
      setAiLoading(false);
    }
  };

  const handleSavePlan = async (e) => {
    e.preventDefault();
    setSaving(true);
    setError('');

    try {
      const planData = {
        plan_name: planName,
        investment_amount: parseFloat(monthlyInvestment),
        frequency: 'Monthly',
        start_date: startDate,
        duration_months: parseInt(duration) * 12,
        equity_percentage: 70,
        debt_percentage: 25,
        gold_percentage: 5,
        expected_return_rate: parseFloat(annualReturn)
      };

      await sipService.createPlan(planData);
      setSaveSuccess(true);
      setShowSaveForm(false);
      setPlanName('');
      fetchSavedPlans();
      
      setTimeout(() => setSaveSuccess(false), 3000);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to save plan');
    } finally {
      setSaving(false);
    }
  };

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 0
    }).format(value);
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-7xl mx-auto">
        <div className="mb-8">
          <h1>SIP Planner</h1>
          <p className="text-secondary-600">
            Calculate your SIP returns and plan your investments
          </p>
        </div>

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-6">
            {error}
          </div>
        )}

        {saveSuccess && (
          <div className="bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded-lg mb-6">
            SIP plan saved successfully!
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Calculator Form */}
          <div className="lg:col-span-1">
            <Card title="SIP Calculator">
              <form onSubmit={handleCalculate}>
                <Input
                  label="Monthly Investment (₹)"
                  type="number"
                  value={monthlyInvestment}
                  onChange={(e) => setMonthlyInvestment(e.target.value)}
                  required
                  min="500"
                  step="500"
                  placeholder="5000"
                />

                <Input
                  label="Expected Annual Return (%)"
                  type="number"
                  value={annualReturn}
                  onChange={(e) => setAnnualReturn(e.target.value)}
                  required
                  min="1"
                  max="30"
                  step="0.5"
                  placeholder="12"
                  helpText="Typical range: 10-15% for equity funds"
                />

                <Input
                  label="Investment Duration (Years)"
                  type="number"
                  value={duration}
                  onChange={(e) => setDuration(e.target.value)}
                  required
                  min="1"
                  max="40"
                  placeholder="10"
                />

                <Button
                  type="submit"
                  variant="primary"
                  className="w-full"
                  disabled={calculating}
                >
                  {calculating ? 'Calculating...' : 'Calculate Returns'}
                </Button>
              </form>

              {/* Quick Presets */}
              <div className="mt-6 pt-6 border-t border-secondary-200">
                <h4 className="text-sm font-semibold mb-3 text-secondary-700">Quick Presets</h4>
                <div className="grid grid-cols-2 gap-2">
                  <button
                    onClick={() => { setMonthlyInvestment('5000'); setAnnualReturn('12'); setDuration('10'); }}
                    className="text-xs px-3 py-2 bg-secondary-100 hover:bg-secondary-200 rounded transition-colors"
                  >
                    Beginner
                  </button>
                  <button
                    onClick={() => { setMonthlyInvestment('10000'); setAnnualReturn('12'); setDuration('15'); }}
                    className="text-xs px-3 py-2 bg-secondary-100 hover:bg-secondary-200 rounded transition-colors"
                  >
                    Moderate
                  </button>
                  <button
                    onClick={() => { setMonthlyInvestment('20000'); setAnnualReturn('14'); setDuration('20'); }}
                    className="text-xs px-3 py-2 bg-secondary-100 hover:bg-secondary-200 rounded transition-colors"
                  >
                    Aggressive
                  </button>
                  <button
                    onClick={() => { setMonthlyInvestment('50000'); setAnnualReturn('15'); setDuration('25'); }}
                    className="text-xs px-3 py-2 bg-secondary-100 hover:bg-secondary-200 rounded transition-colors"
                  >
                    High Net Worth
                  </button>
                </div>
              </div>
            </Card>
          </div>

          {/* Results Section */}
          <div className="lg:col-span-2">
            {!results ? (
              <Card>
                <div className="text-center py-12 text-secondary-500">
                  <div className="w-16 h-16 bg-primary-100 rounded-full flex items-center justify-center mx-auto mb-4">
                    <span className="text-3xl">📊</span>
                  </div>
                  <p className="text-lg font-semibold mb-2">Calculate Your SIP Returns</p>
                  <p className="text-sm">Enter your investment details and click calculate to see projections</p>
                </div>
              </Card>
            ) : (
              <>
                {/* Results Cards */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                  <Card>
                    <div className="text-center">
                      <p className="text-sm text-secondary-600 mb-1">Total Invested</p>
                      <p className="text-2xl font-bold text-primary-600">
                        {formatCurrency(results.total_invested)}
                      </p>
                      <p className="text-xs text-secondary-500 mt-1">
                        {results.monthly_investment.toLocaleString('en-IN')} × {results.investment_duration_years * 12} months
                      </p>
                    </div>
                  </Card>

                  <Card>
                    <div className="text-center">
                      <p className="text-sm text-secondary-600 mb-1">Wealth Generated</p>
                      <p className="text-2xl font-bold text-green-600">
                        {formatCurrency(results.wealth_generated)}
                      </p>
                      <p className="text-xs text-secondary-500 mt-1">
                        Returns @ {results.annual_return_rate}% p.a.
                      </p>
                    </div>
                  </Card>

                  <Card>
                    <div className="text-center">
                      <p className="text-sm text-secondary-600 mb-1">Future Value</p>
                      <p className="text-2xl font-bold text-blue-600">
                        {formatCurrency(results.future_value)}
                      </p>
                      <p className="text-xs text-secondary-500 mt-1">
                        After {results.investment_duration_years} years
                      </p>
                    </div>
                  </Card>
                </div>

                {/* Growth Chart */}
                <Card title="Yearly Growth Projection">
                  <div className="h-80">
                    <ResponsiveContainer width="100%" height="100%">
                      <LineChart data={results.yearly_breakdown}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis 
                          dataKey="year" 
                          label={{ value: 'Years', position: 'insideBottom', offset: -5 }}
                        />
                        <YAxis 
                          label={{ value: 'Amount (₹)', angle: -90, position: 'insideLeft' }}
                          tickFormatter={(value) => `₹${(value / 100000).toFixed(1)}L`}
                        />
                        <Tooltip 
                          formatter={(value) => formatCurrency(value)}
                          labelFormatter={(label) => `Year ${label}`}
                        />
                        <Legend />
                        <Line 
                          type="monotone" 
                          dataKey="invested" 
                          stroke="#3b82f6" 
                          strokeWidth={2}
                          name="Total Invested"
                          dot={{ r: 4 }}
                        />
                        <Line 
                          type="monotone" 
                          dataKey="value" 
                          stroke="#10b981" 
                          strokeWidth={2}
                          name="Portfolio Value"
                          dot={{ r: 4 }}
                        />
                      </LineChart>
                    </ResponsiveContainer>
                  </div>
                </Card>

                {/* AI Explanation */}
                {aiLoading && (
                  <Card title="AI Investment Insights" className="mt-6">
                    <div className="flex items-center justify-center py-8">
                      <div className="text-center">
                        <div className="w-12 h-12 border-4 border-primary-200 border-t-primary-600 rounded-full animate-spin mx-auto mb-4"></div>
                        <p className="text-secondary-600">🤖 Generating AI insights...</p>
                        <p className="text-xs text-secondary-500 mt-2">This may take 10-15 seconds</p>
                      </div>
                    </div>
                  </Card>
                )}
                
                {aiAvailable && aiExplanation && !aiLoading && (
                  <Card title="AI Investment Insights" className="mt-6">
                    <div className="prose max-w-none">
                      <div className="bg-gradient-to-r from-purple-50 to-indigo-50 border-l-4 border-purple-500 px-4 py-3 mb-4 rounded">
                        <div className="flex items-center gap-2 mb-2">
                          <span className="text-xl">🤖</span>
                          <span className="font-semibold text-purple-900">AI-Powered SIP Analysis</span>
                        </div>
                      </div>
                      <div className="text-secondary-700 leading-relaxed">
                        <ReactMarkdown>
                          {aiExplanation}
                        </ReactMarkdown>
                      </div>
                    </div>
                  </Card>
                )}

                {/* Save Plan Card */}
                <Card className="mt-6">
                  {/* Save Plan Button */}
                  <div className="text-center">
                    {!showSaveForm ? (
                      <Button
                        variant="primary"
                        onClick={() => setShowSaveForm(true)}
                      >
                        💾 Save This Plan
                      </Button>
                    ) : (
                      <form onSubmit={handleSavePlan} className="max-w-md mx-auto">
                        <Input
                          label="Plan Name"
                          type="text"
                          value={planName}
                          onChange={(e) => setPlanName(e.target.value)}
                          required
                          placeholder="e.g., Retirement Fund, Education Goal"
                        />
                        <Input
                          label="Start Date"
                          type="date"
                          value={startDate}
                          onChange={(e) => setStartDate(e.target.value)}
                          required
                        />
                        <div className="flex gap-2">
                          <Button
                            type="submit"
                            variant="primary"
                            className="flex-1"
                            disabled={saving}
                          >
                            {saving ? 'Saving...' : 'Save Plan'}
                          </Button>
                          <Button
                            type="button"
                            variant="outline"
                            onClick={() => setShowSaveForm(false)}
                          >
                            Cancel
                          </Button>
                        </div>
                      </form>
                    )}
                  </div>
                </Card>
              </>
            )}
          </div>
        </div>

        {/* Saved Plans */}
        {!loadingPlans && savedPlans.length > 0 && (
          <div className="mt-8">
            <h2 className="text-xl font-bold mb-4">Your Saved Plans</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {savedPlans.map((plan) => (
                <Card key={plan.id}>
                  <div className="flex justify-between items-start mb-3">
                    <div>
                      <h3 className="font-semibold text-lg">{plan.plan_name}</h3>
                      <span className={`text-xs px-2 py-1 rounded-full ${
                        plan.status === 'Active' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                      }`}>
                        {plan.status}
                      </span>
                    </div>
                  </div>
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span className="text-secondary-600">Monthly SIP:</span>
                      <span className="font-semibold">{formatCurrency(plan.investment_amount)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-secondary-600">Duration:</span>
                      <span className="font-semibold">{plan.duration_months / 12} years</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-secondary-600">Expected Returns:</span>
                      <span className="font-semibold">{plan.expected_return_rate}% p.a.</span>
                    </div>
                    <div className="flex justify-between pt-2 border-t">
                      <span className="text-secondary-600">Target Corpus:</span>
                      <span className="font-semibold text-primary-600">{formatCurrency(plan.projected_corpus)}</span>
                    </div>
                  </div>
                </Card>
              ))}
            </div>
          </div>
        )}

        {/* Information Section */}
        <Card className="mt-8">
          <h3 className="text-lg font-semibold mb-4">About SIP</h3>
          <div className="prose max-w-none text-sm">
            <p className="text-secondary-700">
              <strong>Systematic Investment Plan (SIP)</strong> is a disciplined way of investing where you invest a fixed amount regularly (monthly, quarterly, etc.) in mutual funds.
            </p>
            <div className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <h4 className="font-semibold text-secondary-900 mb-2">Benefits:</h4>
                <ul className="list-disc list-inside space-y-1 text-secondary-600">
                  <li>Rupee cost averaging</li>
                  <li>Power of compounding</li>
                  <li>Disciplined investing</li>
                  <li>Flexibility to start small</li>
                </ul>
              </div>
              <div>
                <h4 className="font-semibold text-secondary-900 mb-2">Important Notes:</h4>
                <ul className="list-disc list-inside space-y-1 text-secondary-600">
                  <li>Past performance doesn't guarantee future returns</li>
                  <li>Market-linked investments carry risk</li>
                  <li>Stay invested for long term</li>
                  <li>Review periodically</li>
                </ul>
              </div>
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
};

export default SIPPlanner;
