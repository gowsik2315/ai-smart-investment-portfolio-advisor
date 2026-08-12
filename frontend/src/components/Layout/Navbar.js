/**
 * Navbar Component
 * Main navigation bar with authentication controls
 */

import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';

const Navbar = () => {
  const { isAuthenticated, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  return (
    <nav className="bg-white shadow-md">
      <div className="container mx-auto px-4">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <Link to="/" className="flex items-center space-x-2">
            <div className="w-10 h-10 bg-primary-600 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-xl">SI</span>
            </div>
            <span className="text-xl font-bold text-secondary-900 hidden sm:block">
              Smart Advisor
            </span>
          </Link>

          {/* Navigation Links */}
          <div className="flex items-center space-x-4">
            {isAuthenticated ? (
              <>
                <Link 
                  to="/dashboard" 
                  className="text-secondary-700 hover:text-primary-600 transition-colors"
                >
                  Dashboard
                </Link>
                <Link 
                  to="/profile" 
                  className="text-secondary-700 hover:text-primary-600 transition-colors"
                >
                  Profile
                </Link>
                <Link 
                  to="/risk-assessment" 
                  className="text-secondary-700 hover:text-primary-600 transition-colors"
                >
                  Risk
                </Link>
                <Link 
                  to="/portfolio-recommendation" 
                  className="text-secondary-700 hover:text-primary-600 transition-colors"
                >
                  Recommendations
                </Link>
                <Link 
                  to="/portfolio" 
                  className="text-secondary-700 hover:text-primary-600 transition-colors"
                >
                  Portfolio
                </Link>
                <Link 
                  to="/portfolio-analytics" 
                  className="text-secondary-700 hover:text-primary-600 transition-colors"
                >
                  Analytics
                </Link>
                <Link 
                  to="/diversification" 
                  className="text-secondary-700 hover:text-primary-600 transition-colors"
                >
                  Diversification
                </Link>
                <Link 
                  to="/monte-carlo" 
                  className="text-secondary-700 hover:text-primary-600 transition-colors"
                >
                  Monte Carlo
                </Link>
                <Link 
                  to="/stocks" 
                  className="text-secondary-700 hover:text-primary-600 transition-colors"
                >
                  Stocks
                </Link>
                <Link 
                  to="/sip-planner" 
                  className="text-secondary-700 hover:text-primary-600 transition-colors"
                >
                  SIP Planner
                </Link>
                <button 
                  onClick={handleLogout}
                  className="btn btn-outline"
                >
                  Logout
                </button>
              </>
            ) : (
              <>
                <Link 
                  to="/login" 
                  className="text-secondary-700 hover:text-primary-600 transition-colors"
                >
                  Login
                </Link>
                <Link 
                  to="/register" 
                  className="btn btn-primary"
                >
                  Get Started
                </Link>
              </>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
