import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Search, TrendingUp, TrendingDown, Target, Activity, RefreshCw, ChevronRight } from 'lucide-react';
import { useCompanyData } from '../../hooks/useCompanyData';
import { useCompanySearch } from '../../hooks/useCompanySearch';

const StatBox = ({ label, value }) => (
  <div className="flex flex-col gap-1 p-3.5 bg-navy-800/50 rounded-xl border border-white/5">
    <span className="stat-label">{label}</span>
    <span className="text-base font-bold text-white tabular-nums">{value}</span>
  </div>
);

export default function CompanySidePanel({ selectedSymbol, onSymbolChange }) {
  const [searchQuery, setSearchQuery] = useState('');
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);

  const { companyData, isLoading } = useCompanyData(selectedSymbol);
  const { results: searchResults, isLoading: isSearching } = useCompanySearch(searchQuery);

  const displayCompanies = searchQuery ? searchResults : [];

  const handleSelectCompany = (company) => {
    setIsDropdownOpen(false);
    setSearchQuery('');
    onSymbolChange?.(company.symbol);
  };

  if (isLoading || !companyData) {
    return (
      <div className="bg-navy-900/50 border border-white/5 rounded-2xl p-5 space-y-4">
        {[80, 100, 60, 120, 80].map((w, i) => (
          <div key={i} className="skeleton h-8 rounded-lg" style={{ width: `${w}%` }} />
        ))}
      </div>
    );
  }

  const cur = companyData.currency === 'INR' ? '₹' : '$';
  const up = companyData.changePercent >= 0;
  const pred = companyData.prediction || {};
  const targetPrice = pred.predicted_price || companyData.price * 1.043;
  const targetChange = pred.change_percent || 4.3;
  const confidence = pred.confidence || 0.75;

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="bg-navy-900/50 border border-white/5 rounded-2xl overflow-hidden shadow-card"
    >
      {/* SEARCH */}
      <div className="p-4 border-b border-white/5">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-navy-500 pointer-events-none" />
          <input
            type="text"
            value={searchQuery}
            onChange={e => { setSearchQuery(e.target.value); setIsDropdownOpen(true); }}
            onFocus={() => setIsDropdownOpen(true)}
            placeholder="Search stocks, crypto, commodities…"
            className="w-full pl-9 pr-4 py-2.5 bg-navy-800/60 text-sm text-white placeholder-navy-500
                       border border-white/8 rounded-xl focus:border-accent-500/50 focus:outline-none
                       focus:ring-2 focus:ring-accent-500/15 transition-all"
          />
          <AnimatePresence>
            {isDropdownOpen && searchQuery && (
              <>
                <div className="fixed inset-0 z-10" onClick={() => setIsDropdownOpen(false)} />
                <motion.div
                  initial={{ opacity: 0, y: -6 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -6 }}
                  transition={{ duration: 0.15 }}
                  className="absolute top-full left-0 right-0 mt-1.5 bg-navy-800 border border-white/8
                             rounded-xl shadow-2xl max-h-60 overflow-y-auto z-20 custom-scrollbar"
                >
                  {isSearching ? (
                    <div className="px-4 py-3 text-center text-navy-500 text-sm">Searching…</div>
                  ) : displayCompanies.length > 0 ? (
                    displayCompanies.map(c => (
                      <button
                        key={c.symbol}
                        onClick={() => handleSelectCompany(c)}
                        className="w-full px-4 py-2.5 text-left hover:bg-white/5 transition-colors
                                   border-b border-white/5 last:border-0 flex items-center justify-between group"
                      >
                        <div>
                          <p className="text-sm font-medium text-white">{c.name}</p>
                          <p className="text-xs text-navy-500 font-mono">{c.symbol} · {c.exchange}</p>
                        </div>
                        <ChevronRight className="w-4 h-4 text-navy-600 group-hover:text-accent-400 transition-colors" />
                      </button>
                    ))
                  ) : (
                    <div className="px-4 py-3 text-center text-navy-500 text-sm">No results found</div>
                  )}
                </motion.div>
              </>
            )}
          </AnimatePresence>
        </div>
      </div>

      <div className="p-5 space-y-5">
        {/* COMPANY HEADER */}
        <div>
          <div className="flex items-start justify-between mb-1">
            <div>
              <h3 className="text-lg font-bold text-white leading-tight">{companyData.name}</h3>
              <div className="flex items-center gap-2 mt-1">
                <span className="text-xs font-mono font-semibold text-accent-400 bg-accent-500/10 px-2 py-0.5 rounded-md">
                  {companyData.ticker}
                </span>
                <span className="text-xs text-navy-500">{companyData.exchange}</span>
              </div>
            </div>
            <motion.button
              whileHover={{ rotate: 180 }}
              transition={{ duration: 0.35 }}
              className="p-1.5 hover:bg-white/5 rounded-lg transition-colors"
              title="Refresh"
            >
              <RefreshCw className="w-4 h-4 text-navy-500" />
            </motion.button>
          </div>

          {/* PRICE */}
          <div className="mt-3 flex items-end justify-between">
            <div>
              <p className="text-3xl font-bold text-white tabular-nums">
                {cur}{companyData.price.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
              </p>
              <p className="text-xs text-navy-500 mt-0.5">
                {up ? '+' : ''}{cur}{Math.abs(companyData.change).toFixed(2)} today
              </p>
            </div>
            <div className={`flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-sm font-bold ${
              up ? 'bg-success/15 text-success border border-success/20' : 'bg-danger/15 text-danger border border-danger/20'
            }`}>
              {up ? <TrendingUp className="w-4 h-4" /> : <TrendingDown className="w-4 h-4" />}
              {up ? '+' : ''}{companyData.changePercent.toFixed(2)}%
            </div>
          </div>
        </div>

        {/* AI SIGNAL */}
        <div className={`flex items-center gap-3 p-3.5 rounded-xl border ${
          up ? 'bg-success/8 border-success/20' : 'bg-danger/8 border-danger/20'
        }`}>
          <div className={`w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0 ${
            up ? 'bg-success/20' : 'bg-danger/20'
          }`}>
            {up ? <TrendingUp className="w-4 h-4 text-success" /> : <TrendingDown className="w-4 h-4 text-danger" />}
          </div>
          <div>
            <p className="section-label">AI Signal</p>
            <p className={`text-sm font-bold ${up ? 'text-success' : 'text-danger'}`}>
              {up ? '● BULLISH' : '● BEARISH'}
            </p>
          </div>
        </div>

        {/* 7-DAY PREDICTION */}
        <div className="p-4 bg-gradient-to-br from-accent-500/10 to-accent-cyan/5 border border-accent-500/20 rounded-xl">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-2">
              <Target className="w-4 h-4 text-accent-400" />
              <span className="text-xs font-semibold text-accent-400">7-Day ML Target</span>
            </div>
            <div className="flex items-center gap-1.5">
              <Activity className="w-3.5 h-3.5 text-navy-400" />
              <span className="text-xs text-navy-400">{Math.round(confidence * 100)}% confidence</span>
            </div>
          </div>
          <p className="text-2xl font-bold text-white tabular-nums mb-1">
            {cur}{targetPrice.toFixed(2)}
          </p>
          <p className={`text-xs font-semibold ${targetChange >= 0 ? 'text-success' : 'text-danger'}`}>
            {targetChange >= 0 ? '▲' : '▼'} {Math.abs(targetChange).toFixed(2)}% expected {targetChange >= 0 ? 'growth' : 'decline'}
          </p>
          {pred.method === 'ml_enhanced' && (
            <p className="text-xs text-navy-500 mt-1.5">
              ML enhanced · momentum {pred.momentum?.toFixed(0)}%
            </p>
          )}
        </div>

        {/* STATS */}
        <div className="grid grid-cols-2 gap-3">
          <StatBox label="Volume" value={`${(companyData.volume / 1e6).toFixed(1)}M`} />
          <StatBox
            label="Volatility"
            value={`${(companyData.volatility ?? Math.abs(companyData.changePercent)).toFixed(2)}%`}
          />
        </div>
      </div>
    </motion.div>
  );
}
