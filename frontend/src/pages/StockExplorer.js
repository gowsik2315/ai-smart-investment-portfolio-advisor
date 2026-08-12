/**
 * Stock Explorer Page
 * Search and view stock information with historical charts
 */

import React, { useState, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import Card from '../components/common/Card';
import Input from '../components/common/Input';
import Button from '../components/common/Button';
import Loading from '../components/common/Loading';
import marketService from '../services/marketService';

const StockExplorer = () => {
  // Search state
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [searching, setSearching] = useState(false);
  const [searchError, setSearchError] = useState('');

  // Selected stock state
  const [selectedTicker, setSelectedTicker] = useState('');
  const [stockInfo, setStockInfo] = useState(null);
  const [loadingInfo, setLoadingInfo] = useState(false);
  const [infoError, setInfoError] = useState('');

  // Historical data state
  const [historicalData, setHistoricalData] = useState([]);
  const [loadingHistory, setLoadingHistory] = useState(false);
  const [historyError, setHistoryError] = useState('');
  const [selectedPeriod, setSelectedPeriod] = useState('1y');

  // AI explanation state
  const [aiExplanation, setAiExplanation] = useState('');
  const [aiLoading, setAiLoading] = useState(false);
  const [aiError, setAiError] = useState('');

  // Quick search for popular stocks on mount
  useEffect(() => {
    handleQuickSearch('RELIANCE.NS');
  }, []);

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!searchQuery.trim()) return;

    setSearching(true);
    setSearchError('');

    try {
      const data = await marketService.searchStocks(searchQuery);
      setSearchResults(data.results);
      if (data.results.length === 0) {
        setSearchError('No stocks found. Try searching for ticker symbols like AAPL, RELIANCE.NS, or TCS.NS');
      }
    } catch (err) {
      setSearchError(err.response?.data?.detail || 'Failed to search stocks');
    } finally {
      setSearching(false);
    }
  };

  const handleQuickSearch = (ticker) => {
    setSelectedTicker(ticker);
    loadStockInfo(ticker);
    loadHistoricalData(ticker, selectedPeriod);
    fetchAIExplanation(ticker);
  };

  const handleSelectStock = (ticker) => {
    setSelectedTicker(ticker);
    setSearchResults([]);
    setSearchQuery('');
    loadStockInfo(ticker);
    loadHistoricalData(ticker, selectedPeriod);
    fetchAIExplanation(ticker);
  };

  const loadStockInfo = async (ticker) => {
    setLoadingInfo(true);
    setInfoError('');

    try {
      const data = await marketService.getStockInfo(ticker);
      setStockInfo(data);
    } catch (err) {
      setInfoError(err.response?.data?.detail || 'Failed to load stock information');
      setStockInfo(null);
    } finally {
      setLoadingInfo(false);
    }
  };

  const loadHistoricalData = async (ticker, period) => {
    setLoadingHistory(true);
    setHistoryError('');

    try {
      const data = await marketService.getStockHistory(ticker, period, '1d');
      setHistoricalData(data.data);
    } catch (err) {
      setHistoryError(err.response?.data?.detail || 'Failed to load historical data');
      setHistoricalData([]);
    } finally {
      setLoadingHistory(false);
    }
  };

  const fetchAIExplanation = async (ticker) => {
    setAiLoading(true);
    setAiError('');
    setAiExplanation('');

    try {
      const data = await marketService.explainTrend(ticker);
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

  const handlePeriodChange = (period) => {
    setSelectedPeriod(period);
    if (selectedTicker) {
      loadHistoricalData(selectedTicker, period);
    }
  };

  const formatCurrency = (value, currency = 'INR') => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: currency === 'INR' ? 'INR' : 'USD',
      maximumFractionDigits: 2
    }).format(value);
  };

  const formatNumber = (value) => {
    if (value >= 10000000) {
      return `₹${(value / 10000000).toFixed(2)}Cr`;
    } else if (value >= 100000) {
      return `₹${(value / 100000).toFixed(2)}L`;
    } else {
      return new Intl.NumberFormat('en-IN').format(value);
    }
  };

  const popularStocks = [
    { ticker: 'RELIANCE.NS', name: 'Reliance' },
    { ticker: 'TCS.NS', name: 'TCS' },
    { ticker: 'INFY.NS', name: 'Infosys' },
    { ticker: 'AAPL', name: 'Apple' },
    { ticker: 'MSFT', name: 'Microsoft' },
    { ticker: 'GOOGL', name: 'Google' },
  ];

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-7xl mx-auto">
        <div className="mb-8">
          <h1>Stock Explorer</h1>
          <p className="text-secondary-600">
            Search and explore stocks with real-time data from Yahoo Finance
          </p>
        </div>

        {/* Search Section */}
        <Card className="mb-6">
          <form onSubmit={handleSearch} className="flex gap-2">
            <div className="flex-1">
              <Input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search by ticker (e.g., AAPL, RELIANCE.NS, TCS.NS)"
                disabled={searching}
              />
            </div>
            <Button type="submit" variant="primary" disabled={searching}>
              {searching ? 'Searching...' : 'Search'}
            </Button>
          </form>

          {/* Quick Access */}
          <div className="mt-4">
            <p className="text-sm text-secondary-600 mb-2">Quick Access:</p>
            <div className="flex flex-wrap gap-2">
              {popularStocks.map((stock) => (
                <button
                  key={stock.ticker}
                  onClick={() => handleQuickSearch(stock.ticker)}
                  className="px-3 py-1 text-sm bg-secondary-100 hover:bg-secondary-200 rounded transition-colors"
                >
                  {stock.name}
                </button>
              ))}
            </div>
          </div>

          {/* Search Results */}
          {searchResults.length > 0 && (
            <div className="mt-4 border-t pt-4">
              <p className="text-sm font-semibold mb-2">Search Results:</p>
              <div className="space-y-2">
                {searchResults.map((result) => (
                  <button
                    key={result.ticker}
                    onClick={() => handleSelectStock(result.ticker)}
                    className="w-full text-left px-4 py-2 bg-secondary-50 hover:bg-secondary-100 rounded transition-colors"
                  >
                    <div className="flex justify-between items-center">
                      <div>
                        <span className="font-semibold">{result.ticker}</span>
                        <span className="text-secondary-600 ml-2">{result.name}</span>
                      </div>
                      <span className="text-xs text-secondary-500">{result.exchange}</span>
                    </div>
                  </button>
                ))}
              </div>
            </div>
          )}

          {searchError && (
            <div className="mt-4 text-sm text-red-600">
              {searchError}
            </div>
          )}
        </Card>

        {/* Stock Information */}
        {loadingInfo ? (
          <Card>
            <Loading message="Loading stock information..." />
          </Card>
        ) : infoError ? (
          <Card>
            <div className="text-center py-8 text-red-600">
              <p>{infoError}</p>
            </div>
          </Card>
        ) : stockInfo ? (
          <>
            {/* Stock Header */}
            <Card className="mb-6">
              <div className="flex justify-between items-start mb-4">
                <div>
                  <h2 className="text-2xl font-bold">{stockInfo.company_name}</h2>
                  <p className="text-secondary-600">
                    {stockInfo.ticker} · {stockInfo.exchange}
                  </p>
                </div>
                <div className="text-right">
                  <p className="text-3xl font-bold">
                    {formatCurrency(stockInfo.current_price, stockInfo.currency)}
                  </p>
                  <p className={`text-sm ${stockInfo.change >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                    {stockInfo.change >= 0 ? '▲' : '▼'} {formatCurrency(Math.abs(stockInfo.change), stockInfo.currency)} ({stockInfo.change_percent.toFixed(2)}%)
                  </p>
                </div>
              </div>

              {/* Key Metrics */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 pt-4 border-t">
                <div>
                  <p className="text-sm text-secondary-600">52W High</p>
                  <p className="text-lg font-semibold">{formatCurrency(stockInfo.fifty_two_week_high, stockInfo.currency)}</p>
                </div>
                <div>
                  <p className="text-sm text-secondary-600">52W Low</p>
                  <p className="text-lg font-semibold">{formatCurrency(stockInfo.fifty_two_week_low, stockInfo.currency)}</p>
                </div>
                <div>
                  <p className="text-sm text-secondary-600">Market Cap</p>
                  <p className="text-lg font-semibold">{formatNumber(stockInfo.market_cap)}</p>
                </div>
                <div>
                  <p className="text-sm text-secondary-600">Volume</p>
                  <p className="text-lg font-semibold">{new Intl.NumberFormat('en-IN').format(stockInfo.volume)}</p>
                </div>
              </div>

              {/* Additional Info */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-4 pt-4 border-t">
                <div>
                  <p className="text-sm text-secondary-600">Open</p>
                  <p className="font-semibold">{formatCurrency(stockInfo.open_price, stockInfo.currency)}</p>
                </div>
                <div>
                  <p className="text-sm text-secondary-600">Day High</p>
                  <p className="font-semibold">{formatCurrency(stockInfo.day_high, stockInfo.currency)}</p>
                </div>
                <div>
                  <p className="text-sm text-secondary-600">Day Low</p>
                  <p className="font-semibold">{formatCurrency(stockInfo.day_low, stockInfo.currency)}</p>
                </div>
                <div>
                  <p className="text-sm text-secondary-600">Prev Close</p>
                  <p className="font-semibold">{formatCurrency(stockInfo.previous_close, stockInfo.currency)}</p>
                </div>
              </div>

              {/* Sector & Industry */}
              {stockInfo.sector !== 'N/A' && (
                <div className="mt-4 pt-4 border-t">
                  <div className="flex gap-4 text-sm">
                    <div>
                      <span className="text-secondary-600">Sector:</span>
                      <span className="ml-2 font-semibold">{stockInfo.sector}</span>
                    </div>
                    <div>
                      <span className="text-secondary-600">Industry:</span>
                      <span className="ml-2 font-semibold">{stockInfo.industry}</span>
                    </div>
                  </div>
                </div>
              )}
            </Card>

            {/* Historical Chart */}
            <Card>
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-lg font-semibold">Price History</h3>
                <div className="flex gap-2">
                  {['1mo', '3mo', '6mo', '1y', '2y', '5y'].map((period) => (
                    <button
                      key={period}
                      onClick={() => handlePeriodChange(period)}
                      className={`px-3 py-1 text-sm rounded transition-colors ${
                        selectedPeriod === period
                          ? 'bg-primary-600 text-white'
                          : 'bg-secondary-100 hover:bg-secondary-200'
                      }`}
                    >
                      {period}
                    </button>
                  ))}
                </div>
              </div>

              {loadingHistory ? (
                <div className="h-80 flex items-center justify-center">
                  <Loading message="Loading chart..." />
                </div>
              ) : historyError ? (
                <div className="h-80 flex items-center justify-center text-red-600">
                  <p>{historyError}</p>
                </div>
              ) : historicalData.length > 0 ? (
                <div className="h-80">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={historicalData}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis
                        dataKey="date"
                        tick={{ fontSize: 12 }}
                        tickFormatter={(value) => {
                          const date = new Date(value);
                          return `${date.getMonth() + 1}/${date.getDate()}`;
                        }}
                      />
                      <YAxis
                        tick={{ fontSize: 12 }}
                        domain={['dataMin - 5', 'dataMax + 5']}
                      />
                      <Tooltip
                        formatter={(value) => formatCurrency(value, stockInfo.currency)}
                        labelFormatter={(label) => `Date: ${label}`}
                      />
                      <Line
                        type="monotone"
                        dataKey="close"
                        stroke="#3b82f6"
                        strokeWidth={2}
                        dot={false}
                        name="Close Price"
                      />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              ) : (
                <div className="h-80 flex items-center justify-center text-secondary-500">
                  <p>No historical data available</p>
                </div>
              )}
            </Card>

            {/* Company Description */}
            {stockInfo.description && (
              <Card className="mt-6">
                <h3 className="text-lg font-semibold mb-3">About</h3>
                <p className="text-secondary-700 text-sm leading-relaxed">
                  {stockInfo.description}
                </p>
                {stockInfo.website && (
                  <a
                    href={stockInfo.website}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-primary-600 text-sm hover:underline mt-2 inline-block"
                  >
                    Visit Website →
                  </a>
                )}
              </Card>
            )}

            {/* AI Trend Analysis */}
            {stockInfo && (
              <Card className="mt-6">
                <h3 className="text-lg font-semibold mb-4">AI Trend Analysis</h3>
                {aiLoading ? (
                  <div className="flex items-center justify-center py-8">
                    <Loading message="Generating AI trend analysis..." />
                  </div>
                ) : aiError ? (
                  <div className="text-center py-6">
                    <p className="text-secondary-600 mb-4">{aiError}</p>
                    <Button variant="outline" onClick={() => fetchAIExplanation(selectedTicker)} size="sm">
                      Retry AI Analysis
                    </Button>
                  </div>
                ) : aiExplanation ? (
                  <div className="prose max-w-none">
                    <div className="bg-gradient-to-r from-indigo-50 to-cyan-50 border-l-4 border-indigo-500 px-4 py-3 mb-4 rounded">
                      <div className="flex items-center gap-2 mb-2">
                        <span className="text-xl">🤖</span>
                        <span className="font-semibold text-indigo-900">AI-Powered Market Analysis</span>
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
            )}
          </>
        ) : (
          <Card>
            <div className="text-center py-12 text-secondary-500">
              <div className="w-16 h-16 bg-primary-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-3xl">📈</span>
              </div>
              <p className="text-lg font-semibold mb-2">Search for a Stock</p>
              <p className="text-sm">Enter a ticker symbol or company name to get started</p>
            </div>
          </Card>
        )}

        {/* Info Section */}
        <Card className="mt-6">
          <h3 className="text-lg font-semibold mb-3">How to Use</h3>
          <div className="text-sm text-secondary-700 space-y-2">
            <p><strong>Indian Stocks:</strong> Add .NS suffix (e.g., RELIANCE.NS, TCS.NS, INFY.NS)</p>
            <p><strong>US Stocks:</strong> Use ticker directly (e.g., AAPL, MSFT, GOOGL)</p>
            <p><strong>Quick Access:</strong> Click any button above to instantly load popular stocks</p>
            <p className="text-xs text-secondary-500 mt-4">
              Data provided by Yahoo Finance. Prices may be delayed. Not investment advice.
            </p>
          </div>
        </Card>
      </div>
    </div>
  );
};

export default StockExplorer;
