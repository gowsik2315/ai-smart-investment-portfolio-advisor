/**
 * Stock Predictor Page
 *
 * A 21-trading-day outlook for one stock: where it is trending now, the
 * probability it closes higher, and how far it may plausibly move.
 *
 * Honesty rules the page is built around:
 *  - A probability is only called a prediction when `probability_source`
 *    is 'ml_predicted'. Otherwise it is the stock's own historical
 *    frequency of rising, and the page says so.
 *  - The probability is always shown beside that base rate. Most large
 *    caps rise more often than they fall over a month, so 55% means
 *    little until it is compared with what the stock does anyway.
 *  - The range is centred on today's price. It says how far, not which way.
 */

import React, { useState, useEffect, useMemo, useRef } from 'react';
import { useSearchParams } from 'react-router-dom';
import ReactMarkdown from 'react-markdown';
import {
  ComposedChart, Area, Line, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, ReferenceLine,
} from 'recharts';
import Card from '../components/common/Card';
import Input from '../components/common/Input';
import Button from '../components/common/Button';
import Loading from '../components/common/Loading';
import mlService from '../services/mlService';
import marketService from '../services/marketService';

// Chart colours: one accent hue; the bands are washes of the same hue.
const LINE = '#0284c7';        // primary-600
const BAND = '#0ea5e9';        // primary-500
const GRID = '#e2e8f0';        // secondary-200
const AXIS_TEXT = '#64748b';   // secondary-500

const QUICK_PICKS = [
  { ticker: 'RELIANCE.NS', name: 'Reliance' },
  { ticker: 'TCS.NS', name: 'TCS' },
  { ticker: 'HDFCBANK.NS', name: 'HDFC Bank' },
  { ticker: 'INFY.NS', name: 'Infosys' },
  { ticker: 'ICICIBANK.NS', name: 'ICICI Bank' },
  { ticker: 'ITC.NS', name: 'ITC' },
  { ticker: 'MARUTI.NS', name: 'Maruti' },
  { ticker: 'SUNPHARMA.NS', name: 'Sun Pharma' },
];

const currencyFor = (ticker) => (/\.(NS|BO)$/i.test(ticker) ? 'INR' : 'USD');

const money = (value, ticker) =>
  new Intl.NumberFormat(currencyFor(ticker) === 'INR' ? 'en-IN' : 'en-US', {
    style: 'currency',
    currency: currencyFor(ticker),
    maximumFractionDigits: 2,
  }).format(value);

const pct = (value, digits = 1) => `${(value * 100).toFixed(digits)}%`;

const shortDate = (iso) =>
  new Date(`${iso}T00:00:00`).toLocaleDateString('en-GB', { day: '2-digit', month: 'short' });

/**
 * Flatten the response into one array for the chart. Day 0 of the range is
 * merged into the last close so the cone grows out of the final price.
 */
const buildSeries = (outlook) => {
  const points = outlook.recent_prices.map((p, i) => ({
    i, kind: 'history', date: p.date, label: shortDate(p.date), close: p.close,
  }));
  const lastIndex = points.length - 1;

  outlook.expected_range.forEach((r) => {
    const bands = { band68: [r.lower_68, r.upper_68], band95: [r.lower_95, r.upper_95] };
    if (r.day === 0) {
      Object.assign(points[lastIndex], bands);
    } else {
      points.push({ i: lastIndex + r.day, kind: 'forecast', day: r.day, label: `+${r.day}d`, ...bands });
    }
  });

  return { points, lastIndex };
};

/**
 * Round the price axis outwards to clean ticks (a 1, 2 or 5 times a power
 * of ten), so the axis reads 1,000 / 1,100 / 1,200 rather than whatever
 * the data's min and max happen to be.
 */
const niceAxis = (lo, hi) => {
  const span = Math.max(hi - lo, Math.abs(hi) * 0.02, 1e-6);
  const rawStep = span / 4;
  const magnitude = 10 ** Math.floor(Math.log10(rawStep));
  const norm = rawStep / magnitude;
  const step = (norm <= 1 ? 1 : norm <= 2 ? 2 : norm <= 5 ? 5 : 10) * magnitude;

  const min = Math.floor(lo / step) * step;
  const max = Math.ceil(hi / step) * step;
  const ticks = [];
  for (let v = min; v <= max + step / 2; v += step) {
    ticks.push(Math.round(v * 1e6) / 1e6);
  }
  return { domain: [min, max], ticks };
};

const chartTicks = (lastIndex, horizon) => {
  const ticks = [];
  for (let i = lastIndex; i >= 0; i -= 21) ticks.unshift(i);
  return [...ticks, lastIndex + Math.round(horizon / 2), lastIndex + horizon];
};

const ChartTooltip = ({ active, payload, ticker }) => {
  if (!active || !payload || !payload.length) return null;
  const p = payload[0].payload;

  const row = (color, label, lo, hi) => (
    <div className="flex items-center justify-between gap-6 text-xs">
      <span className="flex items-center gap-2 text-secondary-600">
        <span className="inline-block w-3 h-0.5" style={{ background: color }} />
        {label}
      </span>
      <span className="font-semibold text-secondary-900">
        {money(lo, ticker)} – {money(hi, ticker)}
      </span>
    </div>
  );

  return (
    <div className="bg-white shadow-lg rounded-md px-3 py-2 border border-secondary-200 min-w-[220px]">
      <p className="text-xs text-secondary-500 mb-1">
        {p.kind === 'history' ? p.date : `Trading day +${p.day}`}
      </p>
      {p.close !== undefined && (
        <div className="flex items-center justify-between gap-6 text-xs">
          <span className="flex items-center gap-2 text-secondary-600">
            <span className="inline-block w-3 h-0.5" style={{ background: LINE }} />
            Close
          </span>
          <span className="font-semibold text-secondary-900">{money(p.close, ticker)}</span>
        </div>
      )}
      {p.band68 && p.kind === 'forecast' && (
        <>
          {row(BAND, '68% range', p.band68[0], p.band68[1])}
          {row(BAND, '95% range', p.band95[0], p.band95[1])}
        </>
      )}
    </div>
  );
};

const TREND_STYLE = {
  Bullish: { badge: 'bg-green-50 text-green-800', icon: '▲' },
  Bearish: { badge: 'bg-red-50 text-red-800', icon: '▼' },
  Neutral: { badge: 'bg-secondary-100 text-secondary-700', icon: '◆' },
};

const StockPredictor = () => {
  // Stock Explorer links here with ?ticker=..., so honour it on arrival
  const [searchParams] = useSearchParams();
  const initialTicker = (searchParams.get('ticker') || 'RELIANCE.NS').trim().toUpperCase();

  const [input, setInput] = useState(initialTicker);
  const [outlook, setOutlook] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [showTable, setShowTable] = useState(false);
  const [explanation, setExplanation] = useState(null);
  const [explaining, setExplaining] = useState(false);
  const [explainError, setExplainError] = useState('');
  const requestId = useRef(0);
  const explainId = useRef(0);

  const analyse = async (raw) => {
    const ticker = raw.trim().toUpperCase();
    if (!ticker) return;

    const myRequest = ++requestId.current;
    explainId.current += 1;   // an explanation still in flight belongs to the old stock
    setLoading(true);
    setError('');
    setExplanation(null);
    setExplainError('');
    setExplaining(false);

    try {
      const data = await mlService.getTrendOutlook(ticker);
      if (myRequest === requestId.current) setOutlook(data);
    } catch (err) {
      if (myRequest !== requestId.current) return;
      const detail = err.response?.data?.detail;
      setError(typeof detail === 'string' ? detail : 'Could not load the outlook for that symbol.');
    } finally {
      if (myRequest === requestId.current) setLoading(false);
    }
  };

  useEffect(() => {
    analyse(initialTicker);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const explain = async () => {
    if (!outlook) return;
    const myRequest = ++explainId.current;
    setExplaining(true);
    setExplainError('');

    try {
      const data = await marketService.explainOutlook(outlook.ticker);
      if (myRequest !== explainId.current) return;
      if (data.ai_available) {
        setExplanation(data);
      } else {
        setExplainError('AI explanation is unavailable right now. Is Ollama running? The numbers above stand on their own.');
      }
    } catch (err) {
      if (myRequest !== explainId.current) return;
      setExplainError('AI explanation is unavailable right now. Is Ollama running? The numbers above stand on their own.');
    } finally {
      if (myRequest === explainId.current) setExplaining(false);
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    analyse(input);
  };

  const handlePick = (ticker) => {
    setInput(ticker);
    analyse(ticker);
  };

  const series = useMemo(() => (outlook ? buildSeries(outlook) : null), [outlook]);

  const yAxis = useMemo(() => {
    if (!outlook) return { domain: ['auto', 'auto'], ticks: undefined };
    const last = outlook.expected_range[outlook.expected_range.length - 1];
    const closes = outlook.recent_prices.map((p) => p.close);
    return niceAxis(Math.min(...closes, last.lower_95), Math.max(...closes, last.upper_95));
  }, [outlook]);

  const isModel = outlook?.probability_source === 'ml_predicted';
  const horizonRow = outlook?.expected_range[outlook.expected_range.length - 1];
  const trendStyle = outlook ? TREND_STYLE[outlook.trend.label] || TREND_STYLE.Neutral : null;
  const metrics = outlook?.model_metrics;
  const skill = metrics?.brier_skill_score;

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-7xl mx-auto">
        <div className="mb-8">
          <h1>Stock Predictor</h1>
          <p className="text-secondary-600">
            A 21-trading-day outlook: current trend, the probability of a rise, and the
            range the price may move within.
          </p>
        </div>

        {/* One filter row above everything it scopes */}
        <Card className="mb-6">
          <form onSubmit={handleSubmit} className="flex gap-2 items-start">
            <div className="flex-1">
              <Input
                type="text"
                name="ticker"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="Yahoo Finance symbol, e.g. RELIANCE.NS"
                className="mb-0"
                aria-label="Stock symbol"
              />
            </div>
            <Button type="submit" variant="primary" disabled={loading}>
              {loading ? 'Analysing…' : 'Analyse'}
            </Button>
          </form>

          <div className="mt-4 flex flex-wrap gap-2">
            {QUICK_PICKS.map((s) => (
              <button
                key={s.ticker}
                type="button"
                onClick={() => handlePick(s.ticker)}
                className={`px-3 py-1 text-sm rounded transition-colors ${
                  outlook?.ticker === s.ticker
                    ? 'bg-primary-600 text-white'
                    : 'bg-secondary-100 hover:bg-secondary-200'
                }`}
              >
                {s.name}
              </button>
            ))}
          </div>
          <p className="mt-3 text-xs text-secondary-500">
            The model is trained on large NSE stocks. Other markets use the Nifty 50 as
            their market context, so treat those outlooks as less reliable.
          </p>
        </Card>

        {error && (
          <div role="alert" className="mb-6 p-4 rounded bg-red-50 text-red-800 text-sm">
            {error}
          </div>
        )}

        {!outlook && loading && <Loading message="Fetching price history and building the outlook…" />}

        {outlook && (
          <div className={`transition-opacity ${loading ? 'opacity-50' : 'opacity-100'}`}>
            {/* Provenance: is the probability a prediction or a statistic? */}
            {isModel ? (
              <div className="mb-6 p-4 rounded bg-green-50 text-green-900 text-sm">
                <strong>Model prediction</strong> — probability from trained model{' '}
                <code>{outlook.model_version}</code>.
                {skill !== undefined && skill !== null && (
                  <>
                    {' '}On held-out data its Brier skill score was{' '}
                    <strong>{skill >= 0 ? '+' : ''}{skill.toFixed(3)}</strong>
                    {skill > 0
                      ? ' (positive: it beat the historical base rate).'
                      : ' (zero or negative: it did not beat the historical base rate, so treat the probability with caution).'}
                  </>
                )}
              </div>
            ) : (
              <div role="status" className="mb-6 p-4 rounded bg-amber-50 text-amber-900 text-sm">
                <strong>Not a prediction.</strong> No trained trend model is loaded, so the
                probability below is this stock’s own historical frequency of rising over 21
                trading days ({pct(outlook.base_rate_up)} of recent windows). It describes the
                past, and says nothing about the next month.
              </div>
            )}

            {/* Summary tiles */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
              <Card>
                <p className="text-sm text-secondary-600 mb-2">Current trend</p>
                <span className={`inline-flex items-center gap-2 px-3 py-1 rounded-full font-semibold ${trendStyle.badge}`}>
                  <span aria-hidden="true">{trendStyle.icon}</span>
                  {outlook.trend.label}
                </span>
                <p className="mt-2 text-xs text-secondary-500">
                  Describes the past, not a forecast.
                  {outlook.trend.rsi_14 !== null && (
                    <> RSI {outlook.trend.rsi_14} ({outlook.trend.rsi_state}).</>
                  )}
                </p>
                <ul className="mt-3 space-y-1">
                  {outlook.trend.signals.map((s) => (
                    <li key={s.name} className="text-xs text-secondary-700 flex gap-2">
                      <span aria-hidden="true">{s.bullish ? '▲' : '▼'}</span>
                      <span>
                        <span className="sr-only">{s.bullish ? 'Bullish: ' : 'Bearish: '}</span>
                        {s.detail}
                      </span>
                    </li>
                  ))}
                </ul>
              </Card>

              <Card>
                <p className="text-sm text-secondary-600 mb-1">
                  Chance of closing higher in {outlook.horizon_days} trading days
                </p>
                <p className="text-5xl font-semibold text-secondary-900 mb-4">
                  {pct(outlook.probability_up)}
                </p>

                <div
                  className="relative h-3 rounded-full bg-primary-100"
                  role="meter"
                  aria-valuemin={0}
                  aria-valuemax={100}
                  aria-valuenow={Math.round(outlook.probability_up * 100)}
                  aria-label="Probability of a rise"
                >
                  <div
                    className="absolute inset-y-0 left-0 rounded-full bg-primary-600"
                    style={{ width: pct(outlook.probability_up, 0) }}
                  />
                  <div
                    className="absolute w-0.5 bg-secondary-900"
                    style={{ left: pct(outlook.base_rate_up, 0), top: '-4px', bottom: '-4px' }}
                  />
                </div>
                <div className="relative h-5 mt-1 text-xs text-secondary-600">
                  <span
                    className="absolute -translate-x-1/2 whitespace-nowrap"
                    style={{ left: pct(Math.min(Math.max(outlook.base_rate_up, 0.15), 0.85), 0) }}
                  >
                    ▲ historical base rate {pct(outlook.base_rate_up)}
                  </span>
                </div>
                <p className="mt-2 text-xs text-secondary-500">
                  Compare against the base rate, not against 50%: most large stocks rise more
                  often than they fall over a month.
                </p>
              </Card>

              <Card>
                <p className="text-sm text-secondary-600 mb-2">
                  Expected range in {outlook.horizon_days} trading days
                </p>
                <p className="text-sm text-secondary-500">Last close {money(outlook.last_close, outlook.ticker)} · {outlook.as_of}</p>
                <dl className="mt-3 space-y-2">
                  <div>
                    <dt className="text-xs text-secondary-500">Likely (68%)</dt>
                    <dd className="text-lg font-semibold text-secondary-900">
                      {money(horizonRow.lower_68, outlook.ticker)} – {money(horizonRow.upper_68, outlook.ticker)}
                    </dd>
                  </div>
                  <div>
                    <dt className="text-xs text-secondary-500">Wide (95%)</dt>
                    <dd className="text-lg font-semibold text-secondary-900">
                      {money(horizonRow.lower_95, outlook.ticker)} – {money(horizonRow.upper_95, outlook.ticker)}
                    </dd>
                  </div>
                </dl>
                <p className="mt-3 text-xs text-secondary-500">
                  Based on {pct(outlook.volatility)} annualised volatility (
                  {outlook.volatility_source === 'ml_predicted'
                    ? 'ML forecast'
                    : 'trailing 21-day realised, not an ML forecast'}
                  ). Centred on today’s price: it shows how far, not which way.
                </p>
              </Card>
            </div>

            {/* Chart / table twin */}
            <Card className="mb-6">
              <div className="flex items-center justify-between mb-2">
                <h3 className="mb-0">Price and expected range — {outlook.ticker}</h3>
                <button
                  type="button"
                  onClick={() => setShowTable((v) => !v)}
                  className="text-sm text-primary-700 hover:underline"
                >
                  {showTable ? 'Show chart' : 'Show as table'}
                </button>
              </div>

              <div className="flex flex-wrap items-center gap-x-6 gap-y-1 mb-3 text-xs text-secondary-600">
                <span className="flex items-center gap-2">
                  <span className="inline-block w-4 h-0.5" style={{ background: LINE }} />
                  Close, last 6 months
                </span>
                <span className="flex items-center gap-2">
                  <span className="inline-block w-4 h-3 rounded-sm" style={{ background: BAND, opacity: 0.35 }} />
                  68% range
                </span>
                <span className="flex items-center gap-2">
                  <span className="inline-block w-4 h-3 rounded-sm" style={{ background: BAND, opacity: 0.15 }} />
                  95% range
                </span>
              </div>

              {!showTable ? (
                <ResponsiveContainer width="100%" height={360}>
                  <ComposedChart data={series.points} margin={{ top: 8, right: 16, bottom: 8, left: 8 }}>
                    <CartesianGrid stroke={GRID} vertical={false} />
                    <XAxis
                      type="number"
                      dataKey="i"
                      domain={[0, series.lastIndex + outlook.horizon_days]}
                      ticks={chartTicks(series.lastIndex, outlook.horizon_days)}
                      tickFormatter={(i) => series.points[i]?.label ?? ''}
                      tick={{ fill: AXIS_TEXT, fontSize: 12 }}
                      axisLine={{ stroke: GRID }}
                      tickLine={false}
                    />
                    <YAxis
                      domain={yAxis.domain}
                      ticks={yAxis.ticks}
                      tickFormatter={(v) => v.toLocaleString('en-IN')}
                      tick={{ fill: AXIS_TEXT, fontSize: 12 }}
                      axisLine={false}
                      tickLine={false}
                      width={64}
                    />
                    <Tooltip
                      content={<ChartTooltip ticker={outlook.ticker} />}
                      cursor={{ stroke: AXIS_TEXT, strokeWidth: 1 }}
                    />
                    <ReferenceLine
                      x={series.lastIndex}
                      stroke={GRID}
                      label={{ value: 'Today', position: 'insideTopLeft', fill: AXIS_TEXT, fontSize: 11 }}
                    />
                    <Area dataKey="band95" stroke="none" fill={BAND} fillOpacity={0.15} isAnimationActive={false} activeDot={false} />
                    <Area dataKey="band68" stroke="none" fill={BAND} fillOpacity={0.3} isAnimationActive={false} activeDot={false} />
                    <Line
                      dataKey="close"
                      stroke={LINE}
                      strokeWidth={2}
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      dot={false}
                      activeDot={{ r: 4, fill: LINE, stroke: '#ffffff', strokeWidth: 2 }}
                      isAnimationActive={false}
                    />
                  </ComposedChart>
                </ResponsiveContainer>
              ) : (
                <div className="max-h-80 overflow-auto">
                  <table className="w-full text-sm">
                    <thead className="sticky top-0 bg-white text-left text-secondary-600">
                      <tr>
                        <th className="py-2 pr-4 font-medium">Trading day</th>
                        <th className="py-2 pr-4 font-medium">68% range</th>
                        <th className="py-2 font-medium">95% range</th>
                      </tr>
                    </thead>
                    <tbody className="text-secondary-900">
                      {outlook.expected_range.map((r) => (
                        <tr key={r.day} className="border-t border-secondary-100">
                          <td className="py-1 pr-4">{r.day === 0 ? 'Last close' : `+${r.day}`}</td>
                          <td className="py-1 pr-4 tabular-nums">
                            {money(r.lower_68, outlook.ticker)} – {money(r.upper_68, outlook.ticker)}
                          </td>
                          <td className="py-1 tabular-nums">
                            {money(r.lower_95, outlook.ticker)} – {money(r.upper_95, outlook.ticker)}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </Card>

            {/* AI-written explanation: generated prose, kept visibly separate from the model output */}
            <Card className="mb-6">
              <div className="flex items-start justify-between gap-4">
                <div>
                  <h3 className="mb-1">Explain this outlook</h3>
                  <p className="text-xs text-secondary-500">
                    Written by a local language model from the numbers above. It is an
                    explanation, not a prediction, and it can be wrong.
                  </p>
                </div>
                <Button
                  variant="outline"
                  onClick={explain}
                  disabled={explaining || loading}
                  className="shrink-0"
                >
                  {explaining ? 'Writing…' : explanation ? 'Regenerate' : 'Explain'}
                </Button>
              </div>

              {explaining && (
                <p role="status" className="mt-4 text-sm text-secondary-600">
                  Generating the explanation. On a CPU this can take up to two minutes.
                </p>
              )}

              {explainError && (
                <p role="alert" className="mt-4 text-sm text-amber-800 bg-amber-50 rounded p-3">
                  {explainError}
                </p>
              )}

              {explanation && !explaining && (
                <div className="mt-4 text-sm text-secondary-800 space-y-2">
                  <ReactMarkdown>{explanation.ai_explanation}</ReactMarkdown>
                  <p className="text-xs text-secondary-500">
                    AI-generated{explanation.cached ? ' (saved from an earlier request)' : ''}.
                  </p>
                </div>
              )}
            </Card>

            {/* Model evidence, only when a model exists */}
            {isModel && metrics && (
              <Card className="mb-6" title="How the model did on held-out data">
                <dl className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                  {[
                    ['Accuracy', metrics.accuracy, metrics.baseline_accuracy, 'baseline'],
                    ['Brier score', metrics.brier, metrics.baseline_brier, 'baseline'],
                    ['Log loss', metrics.log_loss, metrics.baseline_log_loss, 'baseline'],
                  ]
                    .filter(([, v]) => v !== undefined && v !== null)
                    .map(([label, value, base, tag]) => (
                      <div key={label}>
                        <dt className="text-secondary-500">{label}</dt>
                        <dd className="text-lg font-semibold text-secondary-900">{value}</dd>
                        {base !== undefined && base !== null && (
                          <dd className="text-xs text-secondary-500">{tag} {base}</dd>
                        )}
                      </div>
                    ))}
                  {metrics.roc_auc !== undefined && metrics.roc_auc !== null && (
                    <div>
                      <dt className="text-secondary-500">ROC AUC</dt>
                      <dd className="text-lg font-semibold text-secondary-900">{metrics.roc_auc}</dd>
                      <dd className="text-xs text-secondary-500">0.5 = no skill</dd>
                    </div>
                  )}
                </dl>
              </Card>
            )}

            <p className="text-xs text-secondary-500">{outlook.disclaimer}</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default StockPredictor;
