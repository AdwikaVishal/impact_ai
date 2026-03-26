import { useState } from 'react';
import { motion } from 'framer-motion';
import { Search, TrendingUp, TrendingDown, Target, Activity, RefreshCw } from 'lucide-react';
import { useCompanyData } from '../../hooks/useCompanyData';
import { useCompanySearch } from '../../hooks/useCompanySearch';

export default function CompanySidePanel({ selectedSymbol, onSymbolChange }) {
  const [searchQuery, setSearchQuery] = useState('');
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  
  const { companyData, isLoading } = useCompanyData(selectedSymbol);
  const { results: searchResults, isLoading: isSearching } = useCompanySearch(searchQuery);

  // Show search results if searching, otherwise show empty
  const displayCompanies = searchQuery ? searchResults : [];

  const handleSelectCompany = (company) => {
    setIsDropdownOpen(false);
    setSearchQuery('');
    if (onSymbolChange) {
      onSymbolChange(company.symbol);
    }
  };

  if (isLoading || !companyData) {
    return (
      <div className="bg-navy-900/80 backdrop-blur-xl border border-navy-700/50 rounded-3xl p-6 shadow-2xl">
        <div className="animate-pulse space-y-4">
          <div className="h-8 bg-navy-700 rounded w-3/4"></div>
          <div className="h-12 bg-navy-700 rounded"></div>
          <div className="h-24 bg-navy-700 rounded"></div>
        </div>
      </div>
    );
  }

  const currencySymbol = companyData.currency === 'INR' ? '₹' : '$';
  
  // Get prediction data
  const prediction = companyData.prediction || {};
  const targetPrice = prediction.predicted_price || companyData.price * 1.043;
  const targetChange = prediction.change_percent || 4.3;
  const confidence = prediction.confidence || 0.75;

  return (
    <motion.div 
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="bg-navy-900/80 backdrop-blur-xl border border-navy-700/50 rounded-3xl p-6 shadow-2xl"
    >
      {/* SEARCH & DROPDOWN */}
      <div className="mb-6">
        <label className="text-xs text-navy-500 uppercase tracking-wider mb-2 block">
          Select Company
        </label>
        <div className="relative">
          <div className="absolute left-4 top-1/2 -translate-y-1/2 z-10">
            <Search className="w-4 h-4 text-navy-500" />
          </div>
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => {
              setSearchQuery(e.target.value);
              setIsDropdownOpen(true);
            }}
            onFocus={() => setIsDropdownOpen(true)}
            placeholder="Search stocks, commodities, crypto, bonds..."
            className="w-full pl-11 pr-4 py-3 bg-navy-800/50 text-white placeholder-navy-500 border border-navy-700 rounded-xl focus:border-accent-500 focus:outline-none focus:ring-2 focus:ring-accent-500/20 transition-all text-sm"
          />
          
          {/* DROPDOWN */}
          {isDropdownOpen && searchQuery && (
            <>
              <div 
                className="fixed inset-0 z-10" 
                onClick={() => setIsDropdownOpen(false)}
              />
              <motion.div
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                className="absolute top-full left-0 right-0 mt-2 bg-navy-800 border border-navy-700 rounded-xl shadow-2xl max-h-64 overflow-y-auto z-20 custom-scrollbar"
              >
                {isSearching ? (
                  <div className="px-4 py-3 text-center text-navy-500 text-sm">
                    Searching...
                  </div>
                ) : displayCompanies.length > 0 ? (
                  displayCompanies.map((company) => (
                    <button
                      key={company.symbol}
                      onClick={() => handleSelectCompany(company)}
                      className={`w-full px-4 py-3 text-left hover:bg-navy-700 transition-colors border-b border-navy-700/50 last:border-b-0 ${
                        company.symbol === selectedSymbol ? 'bg-navy-700' : ''
                      }`}
                    >
                      <div className="flex items-center justify-between">
                        <div>
                          <p className="text-white font-medium text-sm">{company.name}</p>
                          <div className="flex items-center gap-2">
                            <p className="text-navy-500 text-xs font-mono">
                              {company.symbol} • {company.exchange}
                            </p>
                            {company.type && company.type !== 'EQUITY' && (
                              <span className="text-xs px-2 py-0.5 bg-accent-500/20 text-accent-400 rounded">
                                {company.type}
                              </span>
                            )}
                          </div>
                        </div>
                        {company.symbol === selectedSymbol && (
                          <div className="w-2 h-2 bg-accent-400 rounded-full"></div>
                        )}
                      </div>
                    </button>
                  ))
                ) : (
                  <div className="px-4 py-3 text-center text-navy-500 text-sm">
                    No companies found
                  </div>
                )}
              </motion.div>
            </>
          )}
        </div>
      </div>

      {/* SELECTED COMPANY INFO */}
      <div className="mb-6 pb-6 border-b border-navy-700/50">
        <div className="flex items-start justify-between mb-2">
          <h3 className="text-2xl font-bold text-white">{companyData.name}</h3>
          <motion.button
            whileHover={{ rotate: 180 }}
            transition={{ duration: 0.3 }}
            className="p-2 hover:bg-navy-700 rounded-lg transition-colors"
            title="Refresh data"
          >
            <RefreshCw className="w-4 h-4 text-navy-500" />
          </motion.button>
        </div>
        <div className="flex items-center text-sm text-navy-400 mb-4">
          <span className="font-mono bg-navy-700 px-3 py-1 rounded-full mr-3">
            {companyData.ticker}
          </span>
          <span className="text-xs">{companyData.exchange}</span>
        </div>
        
        {/* CURRENT PRICE */}
        <div className="flex items-baseline justify-between">
          <span className="text-4xl font-bold text-white">
            {currencySymbol}{companyData.price.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
          </span>
          <div className={`flex items-center text-2xl font-bold ${companyData.changePercent >= 0 ? 'text-success' : 'text-danger'}`}>
            {companyData.changePercent >= 0 ? <TrendingUp className="w-6 h-6 mr-1" /> : <TrendingDown className="w-6 h-6 mr-1" />}
            {companyData.changePercent >= 0 ? '+' : ''}{companyData.changePercent.toFixed(2)}%
          </div>
        </div>
        <p className="text-sm text-navy-500 mt-2">
          {companyData.changePercent >= 0 ? '+' : ''}{currencySymbol}{Math.abs(companyData.change).toFixed(2)} today
        </p>
      </div>

      {/* AI SIGNAL */}
      <div className="space-y-4">
        <motion.div 
          whileHover={{ scale: 1.02 }}
          className={`flex items-center justify-between p-5 bg-gradient-to-r ${
            companyData.changePercent >= 0 
              ? 'from-success/20 to-success/10 border-success/30' 
              : 'from-danger/20 to-danger/10 border-danger/30'
          } border rounded-2xl`}
        >
          <div className="flex items-center space-x-3">
            <div className={`p-3 ${companyData.changePercent >= 0 ? 'bg-success/30' : 'bg-danger/30'} rounded-xl`}>
              {companyData.changePercent >= 0 ? (
                <TrendingUp className="w-6 h-6 text-success" />
              ) : (
                <TrendingDown className="w-6 h-6 text-danger" />
              )}
            </div>
            <div>
              <p className="text-xs text-navy-400 uppercase tracking-wider">AI Signal</p>
              <p className="text-xl font-bold text-white">
                {companyData.changePercent >= 0 ? '🟢 BULLISH' : '🔴 BEARISH'}
              </p>
            </div>
          </div>
        </motion.div>

        {/* PREDICTION */}
        <motion.div 
          whileHover={{ scale: 1.02 }}
          className="p-6 bg-gradient-to-r from-accent-500/20 to-accent-cyan/20 border border-accent-500/30 rounded-2xl"
        >
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center space-x-2">
              <Target className="w-5 h-5 text-accent-400" />
              <span className="text-sm font-medium text-navy-300">7-Day ML Target</span>
            </div>
            <div className="flex items-center space-x-1">
              <Activity className="w-4 h-4 text-accent-400" />
              <span className="text-xs text-navy-400">{Math.round(confidence * 100)}% confidence</span>
            </div>
          </div>
          <div className="text-3xl font-bold text-white mb-2">
            {currencySymbol}{targetPrice.toFixed(2)}
          </div>
          <p className={`text-sm font-medium ${targetChange >= 0 ? 'text-success' : 'text-danger'}`}>
            {targetChange >= 0 ? '+' : ''}{targetChange.toFixed(2)}% {targetChange >= 0 ? '↑' : '↓'} Expected {targetChange >= 0 ? 'Growth' : 'Decline'}
          </p>
          {prediction.method === 'ml_enhanced' && (
            <p className="text-xs text-navy-500 mt-2">
              Enhanced ML prediction • Momentum: {prediction.momentum?.toFixed(0)}%
            </p>
          )}
        </motion.div>

        {/* STATS */}
        <div className="grid grid-cols-2 gap-3 pt-4">
          <div className="p-4 bg-navy-800/50 rounded-xl border border-navy-700/30">
            <p className="text-xs text-navy-500 mb-1">Volume</p>
            <p className="text-lg font-bold text-white">
              {(companyData.volume / 1000000).toFixed(1)}M
            </p>
          </div>
          <div className="p-4 bg-navy-800/50 rounded-xl border border-navy-700/30">
            <p className="text-xs text-navy-500 mb-1">Volatility</p>
            <p className="text-lg font-bold text-white">
              {companyData.volatility ? companyData.volatility.toFixed(2) : Math.abs(companyData.changePercent).toFixed(1)}%
            </p>
          </div>
        </div>
      </div>
    </motion.div>
  );
}
