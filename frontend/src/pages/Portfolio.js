/**
 * Portfolio Page
 *
 * Portfolio tracking: record transactions, see the holdings they imply.
 *
 * Holdings are derived on the server from the transaction ledger, so
 * this page never stores a position of its own — it records a
 * transaction and re-reads the result.
 */

import React, { useCallback, useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import {
  Cell,
  Legend,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
} from 'recharts';

import Button from '../components/common/Button';
import Card from '../components/common/Card';
import Input from '../components/common/Input';
import Loading from '../components/common/Loading';
import Select from '../components/common/Select';
import portfolioService from '../services/portfolioService';

const TRANSACTION_TYPES = ['Buy', 'Sell', 'SIP', 'Dividend'];
const ASSET_TYPES = ['Stocks', 'Mutual Funds', 'Bonds', 'Gold', 'ETF', 'Other'];
const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#14b8a6', '#f472b6', '#64748b'];

const today = () => new Date().toISOString().split('T')[0];

const emptyTransaction = {
  transaction_type: 'Buy',
  asset_type: 'Stocks',
  asset_name: '',
  asset_symbol: '',
  quantity: '',
  price_per_unit: '',
  fees: '0',
  transaction_date: today(),
};

const Portfolio = () => {
  const [portfolios, setPortfolios] = useState([]);
  const [selectedId, setSelectedId] = useState(null);
  const [detail, setDetail] = useState(null);
  const [transactions, setTransactions] = useState([]);

  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState(null);

  const [newPortfolioName, setNewPortfolioName] = useState('');
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState(emptyTransaction);

  const formatCurrency = (value) =>
    new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 0,
    }).format(value || 0);

  const loadPortfolios = useCallback(async () => {
    const list = await portfolioService.listPortfolios();
    setPortfolios(list);
    return list;
  }, []);

  const loadDetail = useCallback(async (portfolioId) => {
    if (!portfolioId) {
      setDetail(null);
      setTransactions([]);
      return;
    }
    const [detailData, ledger] = await Promise.all([
      portfolioService.getPortfolio(portfolioId),
      portfolioService.listTransactions(portfolioId),
    ]);
    setDetail(detailData);
    setTransactions(ledger);
  }, []);

  // First load: fetch portfolios and open the most recent one.
  useEffect(() => {
    (async () => {
      try {
        const list = await loadPortfolios();
        if (list.length > 0) {
          setSelectedId(list[0].id);
          await loadDetail(list[0].id);
        }
      } catch (err) {
        setError(err.response?.data?.detail || 'Could not load portfolios');
      } finally {
        setLoading(false);
      }
    })();
  }, [loadPortfolios, loadDetail]);

  const selectPortfolio = async (portfolioId) => {
    setSelectedId(portfolioId);
    setError(null);
    setBusy(true);
    try {
      await loadDetail(portfolioId);
    } catch (err) {
      setError(err.response?.data?.detail || 'Could not load that portfolio');
    } finally {
      setBusy(false);
    }
  };

  const handleCreatePortfolio = async (event) => {
    event.preventDefault();
    if (!newPortfolioName.trim()) return;

    setBusy(true);
    setError(null);
    try {
      const created = await portfolioService.createPortfolio({
        portfolio_name: newPortfolioName.trim(),
        portfolio_type: 'Custom',
      });
      setNewPortfolioName('');
      await loadPortfolios();
      setSelectedId(created.id);
      await loadDetail(created.id);
    } catch (err) {
      setError(err.response?.data?.detail || 'Could not create the portfolio');
    } finally {
      setBusy(false);
    }
  };

  const handleDeletePortfolio = async (portfolioId) => {
    if (!window.confirm('Delete this portfolio and all of its transactions?')) return;

    setBusy(true);
    setError(null);
    try {
      await portfolioService.deletePortfolio(portfolioId);
      const list = await loadPortfolios();
      const next = list.length > 0 ? list[0].id : null;
      setSelectedId(next);
      await loadDetail(next);
    } catch (err) {
      setError(err.response?.data?.detail || 'Could not delete the portfolio');
    } finally {
      setBusy(false);
    }
  };

  const handleFormChange = (event) => {
    const { name, value } = event.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  };

  const handleAddTransaction = async (event) => {
    event.preventDefault();
    setBusy(true);
    setError(null);
    try {
      await portfolioService.addTransaction(selectedId, {
        ...form,
        asset_symbol: form.asset_symbol.trim() || null,
        quantity: parseFloat(form.quantity),
        price_per_unit: parseFloat(form.price_per_unit),
        fees: parseFloat(form.fees || 0),
      });
      setForm({ ...emptyTransaction, transaction_date: form.transaction_date });
      setShowForm(false);
      await loadDetail(selectedId);
      await loadPortfolios();
    } catch (err) {
      const detailMessage = err.response?.data?.detail;
      setError(
        Array.isArray(detailMessage)
          ? detailMessage.map((d) => d.msg).join('; ')
          : detailMessage || 'Could not record the transaction'
      );
    } finally {
      setBusy(false);
    }
  };

  const handleDeleteTransaction = async (transactionId) => {
    setBusy(true);
    setError(null);
    try {
      await portfolioService.deleteTransaction(selectedId, transactionId);
      await loadDetail(selectedId);
      await loadPortfolios();
    } catch (err) {
      setError(err.response?.data?.detail || 'Could not delete the transaction');
    } finally {
      setBusy(false);
    }
  };

  if (loading) return <Loading message="Loading your portfolios..." />;

  const summary = detail?.summary;
  const holdings = detail?.holdings || [];
  const gainClass = (value) => (value >= 0 ? 'text-green-600' : 'text-red-600');
  const pieData = holdings.map((h) => ({ name: h.asset_name, value: h.market_value }));
  const hasStalePrices = summary?.holdings_priced_from_last_trade > 0;

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <h1>My Portfolio</h1>
        <p className="text-secondary-600">
          Record what you bought and sold. Holdings, value and profit are worked out from
          that ledger.
        </p>
      </div>

      {error && (
        <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
          {error}
        </div>
      )}

      {/* Portfolio selector */}
      <Card className="mb-6" title="Portfolios">
        <div className="flex flex-wrap gap-2 mb-4">
          {portfolios.map((p) => (
            <button
              key={p.id}
              onClick={() => selectPortfolio(p.id)}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition ${
                p.id === selectedId
                  ? 'bg-primary-600 text-white'
                  : 'bg-secondary-100 text-secondary-700 hover:bg-secondary-200'
              }`}
            >
              {p.portfolio_name}
            </button>
          ))}
          {portfolios.length === 0 && (
            <p className="text-secondary-500 text-sm">
              No portfolios yet. Create one below to start tracking.
            </p>
          )}
        </div>

        <form onSubmit={handleCreatePortfolio} className="flex flex-wrap items-end gap-3">
          <Input
            label="New portfolio"
            name="newPortfolioName"
            value={newPortfolioName}
            onChange={(e) => setNewPortfolioName(e.target.value)}
            placeholder="e.g. Long Term Equity"
            className="mb-0 flex-1 min-w-[220px]"
          />
          <Button type="submit" disabled={busy || !newPortfolioName.trim()}>
            Create
          </Button>
          {selectedId && (
            <Button
              type="button"
              variant="outline"
              onClick={() => handleDeletePortfolio(selectedId)}
              disabled={busy}
            >
              Delete selected
            </Button>
          )}
        </form>
      </Card>

      {selectedId && summary && (
        <>
          {/* Summary tiles */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
            <Card>
              <p className="text-sm text-secondary-600">Invested</p>
              <h2 className="text-2xl font-bold">{formatCurrency(summary.invested_amount)}</h2>
              <p className="text-xs text-secondary-500 mt-1">
                {summary.num_holdings} holding{summary.num_holdings === 1 ? '' : 's'}
              </p>
            </Card>
            <Card>
              <p className="text-sm text-secondary-600">Current value</p>
              <h2 className="text-2xl font-bold text-primary-600">
                {formatCurrency(summary.current_value)}
              </h2>
              <p className="text-xs text-secondary-500 mt-1">
                {summary.holdings_priced_live} priced live
              </p>
            </Card>
            <Card>
              <p className="text-sm text-secondary-600">Unrealised P&amp;L</p>
              <h2 className={`text-2xl font-bold ${gainClass(summary.unrealised_pnl)}`}>
                {formatCurrency(summary.unrealised_pnl)}
              </h2>
              <p className={`text-xs mt-1 ${gainClass(summary.unrealised_pnl)}`}>
                {summary.unrealised_pnl_percent >= 0 ? '+' : ''}
                {summary.unrealised_pnl_percent}%
              </p>
            </Card>
            <Card>
              <p className="text-sm text-secondary-600">Total gain</p>
              <h2 className={`text-2xl font-bold ${gainClass(summary.total_gain)}`}>
                {formatCurrency(summary.total_gain)}
              </h2>
              <p className="text-xs text-secondary-500 mt-1">
                incl. {formatCurrency(summary.realised_pnl)} realised,{' '}
                {formatCurrency(summary.dividend_income)} dividends
              </p>
            </Card>
          </div>

          {hasStalePrices && (
            <div className="mb-6 p-4 bg-amber-50 border border-amber-200 rounded-lg text-amber-800 text-sm">
              <strong>{summary.holdings_priced_from_last_trade}</strong> holding
              {summary.holdings_priced_from_last_trade === 1 ? ' is' : 's are'} valued at
              their last transaction price, because no live quote was available. Those
              holdings show no gain or loss by construction — that is missing data, not a
              flat return. Add a ticker symbol (e.g. <code>RELIANCE.NS</code>) to price
              them live.
            </div>
          )}

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
            {/* Holdings table */}
            <Card className="lg:col-span-2" title="Holdings">
              {holdings.length === 0 ? (
                <div className="text-center py-10 text-secondary-500">
                  <p>No open holdings.</p>
                  <p className="text-sm mt-1">Record a transaction to see holdings here.</p>
                </div>
              ) : (
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="text-left text-secondary-600 border-b">
                        <th className="py-2 pr-3">Asset</th>
                        <th className="py-2 px-3 text-right">Qty</th>
                        <th className="py-2 px-3 text-right">Avg cost</th>
                        <th className="py-2 px-3 text-right">Price</th>
                        <th className="py-2 px-3 text-right">Value</th>
                        <th className="py-2 px-3 text-right">P&amp;L</th>
                        <th className="py-2 pl-3 text-right">Weight</th>
                      </tr>
                    </thead>
                    <tbody>
                      {holdings.map((h) => (
                        <tr key={`${h.asset_symbol || h.asset_name}-${h.asset_type}`} className="border-b last:border-0">
                          <td className="py-3 pr-3">
                            <div className="font-medium">{h.asset_name}</div>
                            <div className="text-xs text-secondary-500">
                              {h.asset_symbol || h.asset_type}
                              {h.price_source !== 'live' && (
                                <span className="ml-2 px-1.5 py-0.5 bg-amber-100 text-amber-700 rounded">
                                  last trade price
                                </span>
                              )}
                            </div>
                          </td>
                          <td className="py-3 px-3 text-right">{h.quantity}</td>
                          <td className="py-3 px-3 text-right">{formatCurrency(h.average_cost)}</td>
                          <td className="py-3 px-3 text-right">{formatCurrency(h.current_price)}</td>
                          <td className="py-3 px-3 text-right font-medium">
                            {formatCurrency(h.market_value)}
                          </td>
                          <td className={`py-3 px-3 text-right ${gainClass(h.unrealised_pnl)}`}>
                            {formatCurrency(h.unrealised_pnl)}
                            <div className="text-xs">
                              {h.unrealised_pnl_percent >= 0 ? '+' : ''}
                              {h.unrealised_pnl_percent}%
                            </div>
                          </td>
                          <td className="py-3 pl-3 text-right">{h.weight_percent}%</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </Card>

            {/* Allocation chart */}
            <Card title="Allocation">
              {pieData.length === 0 ? (
                <div className="text-center py-12 text-secondary-500">
                  <p className="text-sm">No assets allocated</p>
                </div>
              ) : (
                <>
                  <ResponsiveContainer width="100%" height={260}>
                    <PieChart>
                      <Pie
                        data={pieData}
                        dataKey="value"
                        nameKey="name"
                        cx="50%"
                        cy="50%"
                        outerRadius={90}
                        innerRadius={45}
                      >
                        {pieData.map((entry, index) => (
                          <Cell key={entry.name} fill={COLORS[index % COLORS.length]} />
                        ))}
                      </Pie>
                      <Tooltip formatter={(value) => formatCurrency(value)} />
                      <Legend />
                    </PieChart>
                  </ResponsiveContainer>
                  <Link
                    to="/diversification"
                    className="block mt-3 text-sm text-primary-600 hover:underline text-center"
                  >
                    Analyse diversification →
                  </Link>
                </>
              )}
            </Card>
          </div>

          {/* Transactions */}
          <Card
            title={`Transactions (${transactions.length})`}
            className="mb-6"
          >
            <div className="mb-4">
              <Button type="button" onClick={() => setShowForm((v) => !v)} disabled={busy}>
                {showForm ? 'Cancel' : '+ Record transaction'}
              </Button>
            </div>

            {showForm && (
              <form onSubmit={handleAddTransaction} className="mb-6 p-4 bg-secondary-50 rounded-lg">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <Select
                    label="Type"
                    name="transaction_type"
                    value={form.transaction_type}
                    onChange={handleFormChange}
                    options={TRANSACTION_TYPES}
                    placeholder=""
                    required
                  />
                  <Select
                    label="Asset type"
                    name="asset_type"
                    value={form.asset_type}
                    onChange={handleFormChange}
                    options={ASSET_TYPES}
                    placeholder=""
                    required
                  />
                  <Input
                    label="Asset name"
                    name="asset_name"
                    value={form.asset_name}
                    onChange={handleFormChange}
                    placeholder="Reliance Industries"
                    required
                  />
                  <Input
                    label="Ticker (optional)"
                    name="asset_symbol"
                    value={form.asset_symbol}
                    onChange={handleFormChange}
                    placeholder="RELIANCE.NS"
                  />
                  <Input
                    label="Quantity"
                    name="quantity"
                    type="number"
                    step="any"
                    min="0"
                    value={form.quantity}
                    onChange={handleFormChange}
                    required
                  />
                  <Input
                    label="Price per unit (₹)"
                    name="price_per_unit"
                    type="number"
                    step="any"
                    min="0"
                    value={form.price_per_unit}
                    onChange={handleFormChange}
                    required
                  />
                  <Input
                    label="Fees (₹)"
                    name="fees"
                    type="number"
                    step="any"
                    min="0"
                    value={form.fees}
                    onChange={handleFormChange}
                  />
                  <Input
                    label="Date"
                    name="transaction_date"
                    type="date"
                    max={today()}
                    value={form.transaction_date}
                    onChange={handleFormChange}
                    required
                  />
                </div>
                <p className="text-xs text-secondary-500 mb-3">
                  Add a ticker to value the holding at the live market price. A sale larger
                  than the quantity held on that date is rejected.
                </p>
                <Button type="submit" disabled={busy}>
                  {busy ? 'Saving...' : 'Save transaction'}
                </Button>
              </form>
            )}

            {transactions.length === 0 ? (
              <p className="text-secondary-500 text-sm py-4">
                No transactions recorded in this portfolio yet.
              </p>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="text-left text-secondary-600 border-b">
                      <th className="py-2 pr-3">Date</th>
                      <th className="py-2 px-3">Type</th>
                      <th className="py-2 px-3">Asset</th>
                      <th className="py-2 px-3 text-right">Qty</th>
                      <th className="py-2 px-3 text-right">Price</th>
                      <th className="py-2 px-3 text-right">Amount</th>
                      <th className="py-2 pl-3" />
                    </tr>
                  </thead>
                  <tbody>
                    {transactions.map((t) => (
                      <tr key={t.id} className="border-b last:border-0">
                        <td className="py-3 pr-3 whitespace-nowrap">{t.transaction_date}</td>
                        <td className="py-3 px-3">
                          <span
                            className={`px-2 py-0.5 rounded text-xs font-medium ${
                              t.transaction_type === 'Sell'
                                ? 'bg-red-100 text-red-700'
                                : t.transaction_type === 'Dividend'
                                ? 'bg-purple-100 text-purple-700'
                                : 'bg-green-100 text-green-700'
                            }`}
                          >
                            {t.transaction_type}
                          </span>
                        </td>
                        <td className="py-3 px-3">
                          {t.asset_name}
                          {t.asset_symbol && (
                            <span className="text-xs text-secondary-500 ml-1">
                              ({t.asset_symbol})
                            </span>
                          )}
                        </td>
                        <td className="py-3 px-3 text-right">{t.quantity}</td>
                        <td className="py-3 px-3 text-right">{formatCurrency(t.price_per_unit)}</td>
                        <td className="py-3 px-3 text-right">{formatCurrency(t.total_amount)}</td>
                        <td className="py-3 pl-3 text-right">
                          <button
                            onClick={() => handleDeleteTransaction(t.id)}
                            disabled={busy}
                            className="text-red-500 hover:text-red-700 text-xs"
                          >
                            Delete
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </Card>
        </>
      )}
    </div>
  );
};

export default Portfolio;
