/**
 * Main Application Component
 * Sets up routing and global state
 */

import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';

// Layout
import Layout from './components/Layout/Layout';

// Pages
import Home from './pages/Home';
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import FinancialProfile from './pages/FinancialProfile';
import RiskAssessment from './pages/RiskAssessment';
import PortfolioRecommendation from './pages/PortfolioRecommendation';
import Portfolio from './pages/Portfolio';
import PortfolioAnalytics from './pages/PortfolioAnalytics';
import DiversificationAnalysis from './pages/DiversificationAnalysis';
import MonteCarloSimulation from './pages/MonteCarloSimulation';
import SIPPlanner from './pages/SIPPlanner';
import StockExplorer from './pages/StockExplorer';
import NotFound from './pages/NotFound';

function App() {
  return (
    <Router>
      <AuthProvider>
        <Routes>
          {/* Public Routes */}
          <Route path="/" element={<Layout />}>
            <Route index element={<Home />} />
            <Route path="login" element={<Login />} />
            <Route path="register" element={<Register />} />
            
            {/* Protected Routes */}
            <Route path="dashboard" element={<Dashboard />} />
            <Route path="profile" element={<FinancialProfile />} />
            <Route path="risk-assessment" element={<RiskAssessment />} />
            <Route path="portfolio-recommendation" element={<PortfolioRecommendation />} />
            <Route path="portfolio" element={<Portfolio />} />
            <Route path="portfolio-analytics" element={<PortfolioAnalytics />} />
            <Route path="diversification" element={<DiversificationAnalysis />} />
            <Route path="monte-carlo" element={<MonteCarloSimulation />} />
            <Route path="sip-planner" element={<SIPPlanner />} />
            <Route path="stocks" element={<StockExplorer />} />
            
            {/* 404 */}
            <Route path="*" element={<NotFound />} />
          </Route>
        </Routes>
      </AuthProvider>
    </Router>
  );
}

export default App;
