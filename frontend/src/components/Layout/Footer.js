/**
 * Footer Component
 * Application footer with links and copyright
 */

import React from 'react';
import { Link } from 'react-router-dom';

const Footer = () => {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="bg-secondary-900 text-secondary-300">
      <div className="container mx-auto px-4 py-8">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {/* About */}
          <div>
            <h3 className="text-white font-semibold mb-4">Smart Investment Advisor</h3>
            <p className="text-sm">
              AI-powered investment portfolio advisor helping you make informed financial decisions.
            </p>
          </div>

          {/* Quick Links */}
          <div>
            <h4 className="text-white font-semibold mb-4">Quick Links</h4>
            <ul className="space-y-2 text-sm">
              <li>
                <Link to="/dashboard" className="hover:text-white transition-colors">
                  Dashboard
                </Link>
              </li>
              <li>
                <Link to="/portfolio" className="hover:text-white transition-colors">
                  Portfolio
                </Link>
              </li>
              <li>
                <Link to="/sip-planner" className="hover:text-white transition-colors">
                  SIP Planner
                </Link>
              </li>
            </ul>
          </div>

          {/* Contact */}
          <div>
            <h4 className="text-white font-semibold mb-4">Contact</h4>
            <p className="text-sm">
              Final Year Project<br />
              AI-Powered Investment Advisor<br />
              © {currentYear} All rights reserved.
            </p>
          </div>
        </div>

        <div className="border-t border-secondary-800 mt-8 pt-6 text-center text-sm">
          <p>Built with React, FastAPI, and TailwindCSS</p>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
