/**
 * Portfolio Page
 * Portfolio management and recommendations (Placeholder for Phase 2)
 */

import React from 'react';
import Card from '../components/common/Card';

const Portfolio = () => {
  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <h1>My Portfolio</h1>
        <p className="text-secondary-600">Manage and track your investment portfolio</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Portfolio Overview */}
        <Card className="lg:col-span-2" title="Portfolio Overview">
          <div className="text-center py-12 text-secondary-500">
            <div className="w-16 h-16 bg-primary-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <span className="text-3xl">💼</span>
            </div>
            <h3 className="mb-2">Portfolio Management</h3>
            <p>This feature will be implemented in Phase 2</p>
            <p className="text-sm mt-2">
              View your portfolio allocation, performance, and get AI-powered recommendations
            </p>
          </div>
        </Card>

        {/* Asset Allocation */}
        <Card title="Asset Allocation">
          <div className="text-center py-12 text-secondary-500">
            <p className="text-sm">No assets allocated</p>
          </div>
        </Card>
      </div>
    </div>
  );
};

export default Portfolio;
