/**
 * Dashboard Page
 * Main dashboard with portfolio overview (Placeholder for Phase 2)
 */

import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import Card from '../components/common/Card';
import Button from '../components/common/Button';
import profileService from '../services/profileService';
import riskService from '../services/riskService';
import recommendationService from '../services/recommendationService';
import portfolioAnalysisService from '../services/portfolioAnalysisService';

const Dashboard = () => {
  const [profile, setProfile] = useState(null);
  const [riskProfile, setRiskProfile] = useState(null);
  const [recommendation, setRecommendation] = useState(null);
  const [portfolioAnalysis, setPortfolioAnalysis] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const profileData = await profileService.getProfile();
      setProfile(profileData);
      
      // Try to fetch risk profile
      try {
        const riskData = await riskService.getRiskProfile();
        setRiskProfile(riskData);
      } catch (err) {
        // Risk profile doesn't exist yet
        console.log('No risk profile found');
      }
      
      // Try to fetch portfolio recommendation
      try {
        const recData = await recommendationService.getRecommendation();
        setRecommendation(recData);
      } catch (err) {
        // Recommendation doesn't exist yet
        console.log('No portfolio recommendation found');
      }
      
      // Try to fetch portfolio analysis
      try {
        const analysisData = await portfolioAnalysisService.getLatestAnalysis();
        setPortfolioAnalysis(analysisData);
      } catch (err) {
        // Analysis doesn't exist yet
        console.log('No portfolio analysis found');
      }
    } catch (err) {
      // Profile doesn't exist yet, that's okay
      console.log('No profile found');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <h1>Investment Dashboard</h1>
        <p className="text-secondary-600">Overview of your investment portfolio</p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <Card>
          <p className="text-secondary-600 text-sm mb-1">Total Portfolio Value</p>
          <h2 className="text-3xl font-bold text-primary-600">₹0</h2>
          <p className="text-sm text-green-600 mt-2">+0% this month</p>
        </Card>

        <Card>
          <p className="text-secondary-600 text-sm mb-1">Total Invested</p>
          <h2 className="text-3xl font-bold">₹0</h2>
          <p className="text-sm text-secondary-600 mt-2">Across all assets</p>
        </Card>

        <Card>
          <p className="text-secondary-600 text-sm mb-1">Current Returns</p>
          <h2 className="text-3xl font-bold text-green-600">₹0</h2>
          <p className="text-sm text-secondary-600 mt-2">0% gain</p>
        </Card>

        <Card>
          <p className="text-secondary-600 text-sm mb-1">Active SIPs</p>
          <h2 className="text-3xl font-bold">0</h2>
          <p className="text-sm text-secondary-600 mt-2">Monthly investment: ₹0</p>
        </Card>
      </div>

      {/* Quick Actions */}
      <div className="mb-8">
        <h2 className="text-xl font-bold mb-4">Quick Actions</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <Link to="/profile">
            <Card className="hover:shadow-lg transition-shadow cursor-pointer h-full">
              <div className="text-center py-4">
                <div className="w-12 h-12 bg-primary-100 rounded-full flex items-center justify-center mx-auto mb-3">
                  <span className="text-2xl">👤</span>
                </div>
                <h3 className="font-semibold text-secondary-900 mb-1">Financial Profile</h3>
                <p className="text-sm text-secondary-600">
                  {profile ? 'Update' : 'Create'} your financial information
                </p>
                {profile && (
                  <div className="mt-2">
                    <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                      ✓ Completed
                    </span>
                  </div>
                )}
              </div>
            </Card>
          </Link>

          <Link to="/risk-assessment">
            <Card className="hover:shadow-lg transition-shadow cursor-pointer h-full">
              <div className="text-center py-4">
                <div className="w-12 h-12 bg-secondary-100 rounded-full flex items-center justify-center mx-auto mb-3">
                  <span className="text-2xl">📊</span>
                </div>
                <h3 className="font-semibold text-secondary-900 mb-1">Risk Assessment</h3>
                <p className="text-sm text-secondary-600">
                  {riskProfile ? 'View' : 'Evaluate'} your risk tolerance
                </p>
                {riskProfile && (
                  <div className="mt-2">
                    <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                      ✓ {riskProfile.investor_type}
                    </span>
                  </div>
                )}
              </div>
            </Card>
          </Link>

          <Link to="/portfolio-recommendation">
            <Card className="hover:shadow-lg transition-shadow cursor-pointer h-full">
              <div className="text-center py-4">
                <div className="w-12 h-12 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-3">
                  <span className="text-2xl">💼</span>
                </div>
                <h3 className="font-semibold text-secondary-900 mb-1">Portfolio Advice</h3>
                <p className="text-sm text-secondary-600">
                  {recommendation ? 'View' : 'Get'} allocation recommendations
                </p>
                {recommendation && (
                  <div className="mt-2">
                    <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                      ✓ Generated
                    </span>
                  </div>
                )}
              </div>
            </Card>
          </Link>

          <Link to="/portfolio">
            <Card className="hover:shadow-lg transition-shadow cursor-pointer h-full">
              <div className="text-center py-4">
                <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-3">
                  <span className="text-2xl">💼</span>
                </div>
                <h3 className="font-semibold text-secondary-900 mb-1">My Portfolio</h3>
                <p className="text-sm text-secondary-600">View and manage investments</p>
              </div>
            </Card>
          </Link>

          <Link to="/sip-planner">
            <Card className="hover:shadow-lg transition-shadow cursor-pointer h-full">
              <div className="text-center py-4">
                <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-3">
                  <span className="text-2xl">📈</span>
                </div>
                <h3 className="font-semibold text-secondary-900 mb-1">SIP Planner</h3>
                <p className="text-sm text-secondary-600">Plan systematic investments</p>
              </div>
            </Card>
          </Link>

          <Link to="/portfolio-analytics">
            <Card className="hover:shadow-lg transition-shadow cursor-pointer h-full">
              <div className="text-center py-4">
                <div className="w-12 h-12 bg-indigo-100 rounded-full flex items-center justify-center mx-auto mb-3">
                  <span className="text-2xl">📊</span>
                </div>
                <h3 className="font-semibold text-secondary-900 mb-1">Risk Analysis</h3>
                <p className="text-sm text-secondary-600">Portfolio risk metrics</p>
                {portfolioAnalysis && (
                  <div className="mt-2">
                    <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                      ✓ {portfolioAnalysis.risk_level}
                    </span>
                  </div>
                )}
              </div>
            </Card>
          </Link>

          <Link to="/stocks">
            <Card className="hover:shadow-lg transition-shadow cursor-pointer h-full">
              <div className="text-center py-4">
                <div className="w-12 h-12 bg-yellow-100 rounded-full flex items-center justify-center mx-auto mb-3">
                  <span className="text-2xl">📈</span>
                </div>
                <h3 className="font-semibold text-secondary-900 mb-1">Stock Explorer</h3>
                <p className="text-sm text-secondary-600">Market data & analysis</p>
              </div>
            </Card>
          </Link>

          <Link to="/diversification">
            <Card className="hover:shadow-lg transition-shadow cursor-pointer h-full">
              <div className="text-center py-4">
                <div className="w-12 h-12 bg-teal-100 rounded-full flex items-center justify-center mx-auto mb-3">
                  <span className="text-2xl">🎯</span>
                </div>
                <h3 className="font-semibold text-secondary-900 mb-1">Diversification</h3>
                <p className="text-sm text-secondary-600">Analyze concentration risk</p>
              </div>
            </Card>
          </Link>

          <Link to="/monte-carlo">
            <Card className="hover:shadow-lg transition-shadow cursor-pointer h-full">
              <div className="text-center py-4">
                <div className="w-12 h-12 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-3">
                  <span className="text-2xl">🎲</span>
                </div>
                <h3 className="font-semibold text-secondary-900 mb-1">Monte Carlo</h3>
                <p className="text-sm text-secondary-600">Portfolio simulation</p>
              </div>
            </Card>
          </Link>
        </div>
      </div>

      {/* Financial Profile Summary - Show if profile exists */}
      {profile && (
        <div className="mb-8">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl font-bold">Your Financial Profile</h2>
            <Link to="/profile">
              <Button variant="outline">Edit Profile</Button>
            </Link>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            <Card>
              <h3 className="text-sm font-semibold text-secondary-700 mb-3">Basic Information</h3>
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span className="text-secondary-600 text-sm">Age:</span>
                  <span className="font-semibold">{profile.age} years</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-secondary-600 text-sm">Monthly Income:</span>
                  <span className="font-semibold">₹{profile.monthly_income?.toLocaleString()}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-secondary-600 text-sm">Monthly Savings:</span>
                  <span className="font-semibold">₹{profile.monthly_savings?.toLocaleString()}</span>
                </div>
                <div className="flex justify-between pt-2 border-t">
                  <span className="text-secondary-600 text-sm">Savings Rate:</span>
                  <span className="font-semibold text-primary-600">
                    {((profile.monthly_savings / profile.monthly_income) * 100).toFixed(1)}%
                  </span>
                </div>
              </div>
            </Card>

            <Card>
              <h3 className="text-sm font-semibold text-secondary-700 mb-3">Investment Profile</h3>
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span className="text-secondary-600 text-sm">Time Horizon:</span>
                  <span className="font-semibold">{profile.investment_horizon}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-secondary-600 text-sm">Risk Tolerance:</span>
                  <span className={`font-semibold ${
                    profile.risk_tolerance === 'High' ? 'text-red-600' :
                    profile.risk_tolerance === 'Medium' ? 'text-yellow-600' :
                    'text-green-600'
                  }`}>
                    {profile.risk_tolerance}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-secondary-600 text-sm">Financial Goal:</span>
                  <span className="font-semibold">{profile.financial_goal}</span>
                </div>
              </div>
            </Card>

            <Card>
              <h3 className="text-sm font-semibold text-secondary-700 mb-3">Projections</h3>
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span className="text-secondary-600 text-sm">Annual Savings:</span>
                  <span className="font-semibold">₹{(profile.monthly_savings * 12).toLocaleString()}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-secondary-600 text-sm">Monthly Expenses:</span>
                  <span className="font-semibold">
                    ₹{(profile.monthly_income - profile.monthly_savings).toLocaleString()}
                  </span>
                </div>
                <div className="flex justify-between pt-2 border-t">
                  <span className="text-secondary-600 text-sm">Profile Status:</span>
                  <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                    ✓ Complete
                  </span>
                </div>
              </div>
            </Card>
          </div>
        </div>
      )}

      {/* Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Portfolio Allocation */}
        <Card title="Portfolio Allocation">
          {profile ? (
            <div className="py-6">
              <div className="text-center mb-4">
                <p className="text-secondary-600 mb-2">
                  Based on your <span className="font-semibold">{profile.risk_tolerance}</span> risk tolerance
                </p>
              </div>
              <div className="space-y-3">
                <div>
                  <div className="flex justify-between mb-1">
                    <span className="text-sm font-medium">Equity</span>
                    <span className="text-sm font-medium">
                      {profile.risk_tolerance === 'High' ? '70%' : 
                       profile.risk_tolerance === 'Medium' ? '50%' : '30%'}
                    </span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div 
                      className="bg-blue-600 h-2 rounded-full" 
                      style={{width: profile.risk_tolerance === 'High' ? '70%' : 
                                     profile.risk_tolerance === 'Medium' ? '50%' : '30%'}}
                    ></div>
                  </div>
                </div>
                <div>
                  <div className="flex justify-between mb-1">
                    <span className="text-sm font-medium">Debt</span>
                    <span className="text-sm font-medium">
                      {profile.risk_tolerance === 'High' ? '20%' : 
                       profile.risk_tolerance === 'Medium' ? '40%' : '60%'}
                    </span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div 
                      className="bg-green-600 h-2 rounded-full" 
                      style={{width: profile.risk_tolerance === 'High' ? '20%' : 
                                     profile.risk_tolerance === 'Medium' ? '40%' : '60%'}}
                    ></div>
                  </div>
                </div>
                <div>
                  <div className="flex justify-between mb-1">
                    <span className="text-sm font-medium">Gold</span>
                    <span className="text-sm font-medium">10%</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div className="bg-yellow-500 h-2 rounded-full" style={{width: '10%'}}></div>
                  </div>
                </div>
              </div>
              <p className="text-xs text-secondary-500 mt-4 text-center">
                Recommended allocation based on your profile
              </p>
            </div>
          ) : (
            <div className="text-center py-12 text-secondary-500">
              <p>No portfolio data available</p>
              <p className="text-sm mt-2 mb-4">Complete your financial profile to get started</p>
              <Link to="/profile">
                <Button variant="primary">Create Financial Profile</Button>
              </Link>
            </div>
          )}
        </Card>

        {/* Recent Transactions */}
        <Card title="Recent Transactions">
          <div className="text-center py-12 text-secondary-500">
            <p>No transactions yet</p>
            <p className="text-sm mt-2">Your investment history will appear here</p>
          </div>
        </Card>

        {/* Portfolio Risk Analysis */}
        <Card title="Portfolio Risk Analysis">
          {portfolioAnalysis ? (
            <div className="py-4">
              <div className="text-center mb-4">
                <div className="inline-flex items-center justify-center w-20 h-20 rounded-full mb-3"
                  style={{
                    backgroundColor: portfolioAnalysis.risk_score < 30 ? '#10b98120' : 
                                     portfolioAnalysis.risk_score < 50 ? '#f59e0b20' :
                                     portfolioAnalysis.risk_score < 70 ? '#f9731620' : '#ef444420',
                    color: portfolioAnalysis.risk_score < 30 ? '#10b981' : 
                           portfolioAnalysis.risk_score < 50 ? '#f59e0b' :
                           portfolioAnalysis.risk_score < 70 ? '#f97316' : '#ef4444'
                  }}
                >
                  <div>
                    <div className="text-2xl font-bold">{portfolioAnalysis.risk_score.toFixed(1)}</div>
                    <div className="text-xs">/ 100</div>
                  </div>
                </div>
                <div>
                  <span className="inline-block px-4 py-1 rounded-full text-sm font-semibold"
                    style={{
                      backgroundColor: portfolioAnalysis.risk_score < 30 ? '#10b98120' : 
                                       portfolioAnalysis.risk_score < 50 ? '#f59e0b20' :
                                       portfolioAnalysis.risk_score < 70 ? '#f9731620' : '#ef444420',
                      color: portfolioAnalysis.risk_score < 30 ? '#10b981' : 
                             portfolioAnalysis.risk_score < 50 ? '#f59e0b' :
                             portfolioAnalysis.risk_score < 70 ? '#f97316' : '#ef4444'
                    }}
                  >
                    {portfolioAnalysis.risk_level}
                  </span>
                </div>
              </div>
              
              <div className="space-y-2 mb-4">
                <div className="flex justify-between text-sm">
                  <span className="text-secondary-600">Volatility:</span>
                  <span className="font-semibold">{portfolioAnalysis.volatility_percent.toFixed(2)}%</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-secondary-600">Sharpe Ratio:</span>
                  <span className="font-semibold">{portfolioAnalysis.sharpe_ratio.toFixed(2)}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-secondary-600">Max Drawdown:</span>
                  <span className="font-semibold text-red-600">{portfolioAnalysis.max_drawdown_percent.toFixed(2)}%</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-secondary-600">Total Return:</span>
                  <span className={`font-semibold ${portfolioAnalysis.total_return >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                    {portfolioAnalysis.total_return > 0 ? '+' : ''}{portfolioAnalysis.total_return.toFixed(2)}%
                  </span>
                </div>
              </div>

              <Link to="/portfolio-analytics" className="block">
                <Button variant="outline" className="w-full">View Detailed Analysis</Button>
              </Link>
            </div>
          ) : (
            <div className="text-center py-12 text-secondary-500">
              <p>No risk analysis available</p>
              <p className="text-sm mt-2 mb-4">Generate portfolio risk metrics</p>
              <Link to="/portfolio-analytics">
                <Button variant="secondary">Analyze Portfolio</Button>
              </Link>
            </div>
          )}
        </Card>

        {/* Risk Profile */}
        <Card title="Risk Profile">
          {riskProfile ? (
            <div className="py-4">
              <div className="text-center mb-4">
                <div className="inline-flex items-center justify-center w-20 h-20 rounded-full mb-3"
                  style={{
                    backgroundColor: riskProfile.risk_score < 40 ? '#10b98120' : 
                                     riskProfile.risk_score < 70 ? '#f59e0b20' : '#ef444420',
                    color: riskProfile.risk_score < 40 ? '#10b981' : 
                           riskProfile.risk_score < 70 ? '#f59e0b' : '#ef4444'
                  }}
                >
                  <div>
                    <div className="text-2xl font-bold">{riskProfile.risk_score.toFixed(1)}</div>
                    <div className="text-xs">/ 100</div>
                  </div>
                </div>
                <div>
                  <span className="inline-block px-4 py-1 rounded-full text-sm font-semibold"
                    style={{
                      backgroundColor: riskProfile.risk_score < 40 ? '#10b98120' : 
                                       riskProfile.risk_score < 70 ? '#f59e0b20' : '#ef444420',
                      color: riskProfile.risk_score < 40 ? '#10b981' : 
                             riskProfile.risk_score < 70 ? '#f59e0b' : '#ef4444'
                    }}
                  >
                    {riskProfile.investor_type}
                  </span>
                </div>
              </div>
              
              <div className="space-y-2 mb-4">
                <div className="flex justify-between text-sm">
                  <span className="text-secondary-600">Recommended Equity:</span>
                  <span className="font-semibold">
                    {riskProfile.investor_type === 'Conservative' ? '30%' :
                     riskProfile.investor_type === 'Moderate' ? '50%' : '70%'}
                  </span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-secondary-600">Recommended Debt:</span>
                  <span className="font-semibold">
                    {riskProfile.investor_type === 'Conservative' ? '60%' :
                     riskProfile.investor_type === 'Moderate' ? '40%' : '20%'}
                  </span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-secondary-600">Gold Allocation:</span>
                  <span className="font-semibold">10%</span>
                </div>
              </div>

              <Link to="/risk-assessment" className="block">
                <Button variant="outline" className="w-full">View Detailed Analysis</Button>
              </Link>
            </div>
          ) : (
            <div className="text-center py-12 text-secondary-500">
              <p>Risk profile not assessed</p>
              <p className="text-sm mt-2 mb-4">Take the risk assessment to get personalized recommendations</p>
              <Link to="/risk-assessment">
                <Button variant="secondary">Take Risk Assessment</Button>
              </Link>
            </div>
          )}
        </Card>

        {/* Investment Recommendations */}
        <Card title="Investment Recommendations">
          {profile ? (
            <div className="py-4">
              <p className="text-sm text-secondary-600 mb-4">
                Based on your goal: <span className="font-semibold">{profile.financial_goal}</span>
              </p>
              <div className="space-y-3">
                <div className="p-3 bg-primary-50 rounded-lg border border-primary-200">
                  <div className="flex items-start">
                    <span className="text-2xl mr-3">💰</span>
                    <div>
                      <h4 className="font-semibold text-sm mb-1">Systematic Investment Plan (SIP)</h4>
                      <p className="text-xs text-secondary-600">
                        Invest ₹{profile.monthly_savings?.toLocaleString()} monthly for steady growth
                      </p>
                    </div>
                  </div>
                </div>
                
                <div className="p-3 bg-blue-50 rounded-lg border border-blue-200">
                  <div className="flex items-start">
                    <span className="text-2xl mr-3">📊</span>
                    <div>
                      <h4 className="font-semibold text-sm mb-1">Diversified Mutual Funds</h4>
                      <p className="text-xs text-secondary-600">
                        {profile.risk_tolerance === 'High' ? 'Aggressive growth funds' : 
                         profile.risk_tolerance === 'Medium' ? 'Balanced funds' : 
                         'Conservative hybrid funds'} aligned with your risk profile
                      </p>
                    </div>
                  </div>
                </div>

                <div className="p-3 bg-green-50 rounded-lg border border-green-200">
                  <div className="flex items-start">
                    <span className="text-2xl mr-3">🎯</span>
                    <div>
                      <h4 className="font-semibold text-sm mb-1">Goal-based Planning</h4>
                      <p className="text-xs text-secondary-600">
                        Time horizon: {profile.investment_horizon} - Focus on {profile.financial_goal.toLowerCase()}
                      </p>
                    </div>
                  </div>
                </div>
              </div>
              <Link to="/portfolio" className="block mt-4">
                <Button variant="primary" className="w-full">Explore Investment Options</Button>
              </Link>
            </div>
          ) : (
            <div className="text-center py-12 text-secondary-500">
              <p>No recommendations available</p>
              <p className="text-sm mt-2">Complete your profile to receive AI-powered recommendations</p>
            </div>
          )}
        </Card>
      </div>
    </div>
  );
};

export default Dashboard;
