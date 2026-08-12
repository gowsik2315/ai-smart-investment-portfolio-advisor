/**
 * Home Page
 * Landing page with feature overview
 */

import React from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const Home = () => {
  const { isAuthenticated } = useAuth();

  return (
    <div className="bg-gradient-to-b from-primary-50 to-white">
      {/* Hero Section */}
      <section className="container mx-auto px-4 py-20">
        <div className="text-center max-w-4xl mx-auto">
          <h1 className="text-5xl font-bold text-secondary-900 mb-6">
            AI-Powered Smart Investment Portfolio Advisor
          </h1>
          <p className="text-xl text-secondary-600 mb-8">
            Make informed investment decisions with personalized portfolio recommendations,
            risk assessment, and SIP planning powered by AI.
          </p>
          <div className="flex justify-center gap-4">
            {isAuthenticated ? (
              <Link to="/dashboard" className="btn btn-primary text-lg px-8 py-3">
                Go to Dashboard
              </Link>
            ) : (
              <>
                <Link to="/register" className="btn btn-primary text-lg px-8 py-3">
                  Get Started Free
                </Link>
                <Link to="/login" className="btn btn-outline text-lg px-8 py-3">
                  Sign In
                </Link>
              </>
            )}
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="container mx-auto px-4 py-16">
        <h2 className="text-center mb-12">Core Features</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {/* Feature 1 */}
          <div className="card">
            <div className="w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center mb-4">
              <span className="text-2xl">📊</span>
            </div>
            <h3 className="mb-2">Risk Profiling</h3>
            <p className="text-secondary-600">
              Assess your risk tolerance with our intelligent questionnaire and get personalized recommendations.
            </p>
          </div>

          {/* Feature 2 */}
          <div className="card">
            <div className="w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center mb-4">
              <span className="text-2xl">💼</span>
            </div>
            <h3 className="mb-2">Portfolio Recommendations</h3>
            <p className="text-secondary-600">
              Get AI-powered portfolio allocation recommendations tailored to your financial goals.
            </p>
          </div>

          {/* Feature 3 */}
          <div className="card">
            <div className="w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center mb-4">
              <span className="text-2xl">📈</span>
            </div>
            <h3 className="mb-2">SIP Planner</h3>
            <p className="text-secondary-600">
              Plan your systematic investment plans with projected returns and growth simulation.
            </p>
          </div>

          {/* Feature 4 */}
          <div className="card">
            <div className="w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center mb-4">
              <span className="text-2xl">🎯</span>
            </div>
            <h3 className="mb-2">Goal Planning</h3>
            <p className="text-secondary-600">
              Set and track your financial goals with intelligent investment strategies.
            </p>
          </div>

          {/* Feature 5 */}
          <div className="card">
            <div className="w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center mb-4">
              <span className="text-2xl">📉</span>
            </div>
            <h3 className="mb-2">Risk Analysis</h3>
            <p className="text-secondary-600">
              Understand portfolio risk metrics and diversification strategies for better decisions.
            </p>
          </div>

          {/* Feature 6 */}
          <div className="card">
            <div className="w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center mb-4">
              <span className="text-2xl">🔮</span>
            </div>
            <h3 className="mb-2">Growth Simulation</h3>
            <p className="text-secondary-600">
              Simulate future portfolio growth based on historical data and market trends.
            </p>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="container mx-auto px-4 py-16">
        <div className="card bg-primary-600 text-white text-center">
          <h2 className="mb-4">Ready to Start Your Investment Journey?</h2>
          <p className="text-lg mb-6">
            Join thousands of investors making smarter decisions with AI-powered insights.
          </p>
          {!isAuthenticated && (
            <Link to="/register" className="btn bg-white text-primary-600 hover:bg-gray-100">
              Create Free Account
            </Link>
          )}
        </div>
      </section>
    </div>
  );
};

export default Home;
