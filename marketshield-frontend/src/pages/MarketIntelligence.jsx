/**
 * MarketIntelligence – main page for the brand intelligence engine.
 *
 * Route: /intel
 *
 * Flow:
 *   1. User enters company name + category
 *   2. POST /api/v1/company/full_intel
 *   3. ResultsView renders all 10 output sections
 */
import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Search, Loader2, Brain, Zap, AlertCircle, X } from 'lucide-react';
import { getFullIntel } from '../services/api';
import ResultsView from '../components/intel/ResultsView';

const EXAMPLES = [
  { company: 'Nike',       category: 'athletic footwear' },
  { company: 'Stripe',     category: 'online payment processing' },
  { company: 'Lululemon',  category: 'athletic apparel' },
];

export default function MarketIntelligence() {
  const [company,  setCompany]  = useState('');
  const [category, setCategory] = useState('');
  const [data,     setData]     = useState(null);
  const [loading,  setLoading]  = useState(false);
  const [error,    setError]    = useState('');
  const [elapsed,  setElapsed]  = useState(0);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!company.trim()) return;

    setLoading(true);
    setError('');
    setData(null);
    setElapsed(0);

    // Elapsed-time ticker
    const start = Date.now();
    const ticker = setInterval(() => setElapsed(Math.floor((Date.now() - start) / 1000)), 500);

    try {
      const res = await getFullIntel(company.trim(), category.trim());
      setData(res.data);
    } catch (err) {
      const msg = err.response?.data?.detail || err.message || 'Unknown error';
      setError(`Request failed: ${msg}`);
    } finally {
      clearInterval(ticker);
      setLoading(false);
    }
  };

  const handleExample = (ex) => {
    setCompany(ex.company);
    setCategory(ex.category);
  };

  return (
    <div className="max-w-[1200px] mx-auto px-4 sm:px-8 lg:px-12 py-8">

      {/* ── Header ─────────────────────────────────────────────────────── */}
      <motion.div
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        className="mb-8"
      >
        <div className="inline-flex items-center gap-2 px-3 py-1.5 bg-accent-500/10 border border-accent-500/20 rounded-full mb-4">
          <Brain className="w-3.5 h-3.5 text-accent-400" />
          <span className="text-xs font-semibold text-accent-400 tracking-wide">Brand Intelligence Engine</span>
        </div>
        <h1 className="text-3xl sm:text-4xl font-bold text-white tracking-tight mb-2">
          Market Intelligence
        </h1>
        <p className="text-navy-400 text-sm max-w-xl">
          Enter a brand name and category to generate a full intelligence report —
          company overview, competitor mapping, strategic watchouts, and personalised outreach.
        </p>
      </motion.div>

      {/* ── Search form ────────────────────────────────────────────────── */}
      <motion.form
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        onSubmit={handleSubmit}
        className="glass-card p-5 mb-4"
      >
        <div className="flex flex-col sm:flex-row gap-3">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-navy-500 pointer-events-none" />
            <input
              type="text"
              placeholder="Company name  (e.g. Nike)"
              value={company}
              onChange={e => setCompany(e.target.value)}
              required
              className="w-full pl-9 pr-4 py-2.5 bg-navy-800/60 border border-navy-700/50 rounded-xl text-sm text-white placeholder-navy-600 focus:outline-none focus:border-accent-500/50 transition-colors"
            />
          </div>
          <div className="flex-1 relative">
            <input
              type="text"
              placeholder="Category  (e.g. athletic footwear)"
              value={category}
              onChange={e => setCategory(e.target.value)}
              className="w-full px-4 py-2.5 bg-navy-800/60 border border-navy-700/50 rounded-xl text-sm text-white placeholder-navy-600 focus:outline-none focus:border-accent-500/50 transition-colors"
            />
          </div>
          <button
            type="submit"
            disabled={loading || !company.trim()}
            className="btn-primary flex items-center gap-2 whitespace-nowrap"
          >
            {loading
              ? <><Loader2 className="w-4 h-4 animate-spin" /> Researching… {elapsed}s</>
              : <><Zap className="w-4 h-4" /> Analyze Brand</>
            }
          </button>
        </div>

        {/* Example chips */}
        <div className="flex flex-wrap items-center gap-2 mt-3">
          <span className="text-xs text-navy-600">Try:</span>
          {EXAMPLES.map(ex => (
            <button
              key={ex.company}
              type="button"
              onClick={() => handleExample(ex)}
              className="text-xs px-2.5 py-1 rounded-full bg-navy-800/60 border border-navy-700/40 text-navy-400 hover:text-white hover:border-accent-500/30 transition-all"
            >
              {ex.company}
            </button>
          ))}
        </div>
      </motion.form>

      {/* ── Loading state ───────────────────────────────────────────────── */}
      <AnimatePresence>
        {loading && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="glass-card p-8 text-center mb-4"
          >
            <Loader2 className="w-8 h-8 text-accent-400 animate-spin mx-auto mb-3" />
            <p className="text-white font-medium">Collecting intelligence for <span className="text-accent-400">{company}</span>…</p>
            <p className="text-xs text-navy-500 mt-1">
              Scraping website, news, competitors, events, and decision-makers. This takes ~15–30s.
            </p>
            <div className="mt-4 flex justify-center gap-6 text-xs text-navy-600">
              {['Website', 'News', 'Competitors', 'Events', 'People', 'LLM enrichment'].map((step, i) => (
                <span key={step} className={elapsed > i * 3 ? 'text-accent-400' : ''}>
                  {elapsed > i * 3 ? '✓' : '○'} {step}
                </span>
              ))}
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* ── Error state ─────────────────────────────────────────────────── */}
      <AnimatePresence>
        {error && (
          <motion.div
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0 }}
            className="flex items-start gap-3 p-4 rounded-xl bg-danger/5 border border-danger/20 mb-4"
          >
            <AlertCircle className="w-4 h-4 text-danger mt-0.5 flex-shrink-0" />
            <p className="text-sm text-danger flex-1">{error}</p>
            <button onClick={() => setError('')} className="text-danger/60 hover:text-danger">
              <X className="w-4 h-4" />
            </button>
          </motion.div>
        )}
      </AnimatePresence>

      {/* ── Results ─────────────────────────────────────────────────────── */}
      <AnimatePresence>
        {data && !loading && (
          <motion.div
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4 }}
          >
            {/* Company header */}
            <div className="flex items-center justify-between mb-2">
              <div>
                <h2 className="text-xl font-bold text-white">{data.company_name}</h2>
                {data.category && (
                  <span className="text-xs text-navy-500">{data.category}</span>
                )}
              </div>
              <button
                onClick={() => setData(null)}
                className="btn-secondary text-xs flex items-center gap-1.5"
              >
                <X className="w-3.5 h-3.5" /> Clear
              </button>
            </div>

            <ResultsView data={data} />
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
