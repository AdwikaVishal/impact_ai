import { motion, AnimatePresence } from 'framer-motion';
import { Globe, TrendingUp, TrendingDown, Activity, X, BarChart3 } from 'lucide-react';
import { useState } from 'react';

export default function MarketOverview() {
  const [selectedIndex, setSelectedIndex] = useState(null);
  const [selectedSector, setSelectedSector] = useState(null);

  const [indices] = useState([
    { name: 'NIFTY 50', value: 24150.75, change: 2.14, region: 'India', volume: '2.4B', high: 24200.50, low: 23950.25 },
    { name: 'SENSEX', value: 79486.32, change: 1.89, region: 'India', volume: '1.8B', high: 79650.00, low: 78900.00 },
    { name: 'S&P 500', value: 5234.18, change: 0.45, region: 'US', volume: '3.2B', high: 5245.30, low: 5220.10 },
    { name: 'NASDAQ', value: 16340.87, change: 1.23, region: 'US', volume: '4.1B', high: 16380.50, low: 16250.00 },
    { name: 'DOW JONES', value: 38790.43, change: -0.12, region: 'US', volume: '2.9B', high: 38850.00, low: 38720.00 },
    { name: 'FTSE 100', value: 8245.67, change: 0.78, region: 'UK', volume: '1.5B', high: 8260.00, low: 8230.00 },
  ]);

  const [sectors] = useState([
    { name: 'Technology', change: 2.45, volume: '12.5B', companies: 145, topGainer: 'NVDA +5.2%' },
    { name: 'Finance', change: 1.23, volume: '8.3B', companies: 98, topGainer: 'JPM +3.1%' },
    { name: 'Healthcare', change: -0.56, volume: '5.7B', companies: 76, topGainer: 'PFE +1.8%' },
    { name: 'Energy', change: 3.12, volume: '9.1B', companies: 54, topGainer: 'XOM +4.5%' },
    { name: 'Consumer', change: 0.89, volume: '6.4B', companies: 112, topGainer: 'AMZN +2.3%' },
    { name: 'Industrial', change: 1.67, volume: '4.2B', companies: 89, topGainer: 'CAT +3.7%' },
  ]);

  return (
    <div className="max-w-[1400px] mx-auto px-8 lg:px-16">
      {/* COMPACT HEADER */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="mb-8"
      >
        <div className="flex items-center gap-4 mb-6">
          <div className="flex items-center justify-center w-12 h-12 bg-accent-500/20 rounded-xl">
            <Globe className="w-6 h-6 text-accent-400" />
          </div>
          <div>
            <h1 className="text-3xl font-bold text-white">Market Overview</h1>
            <p className="text-sm text-navy-400">Global indices and sector performance</p>
          </div>
        </div>
      </motion.div>

      {/* MARKET STATUS - COMPACT */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8"
      >
        <div className="flex items-center gap-3 bg-gradient-to-br from-success/20 to-success/5 border border-success/30 rounded-xl p-4">
          <Activity className="w-6 h-6 text-success flex-shrink-0" />
          <div>
            <h3 className="text-xs text-success/80">Market Status</h3>
            <p className="text-xl font-bold text-success">Open</p>
          </div>
        </div>

        <div className="flex items-center gap-3 bg-navy-900/40 backdrop-blur-xl border border-navy-700/30 rounded-xl p-4">
          <TrendingUp className="w-6 h-6 text-accent-400 flex-shrink-0" />
          <div>
            <h3 className="text-xs text-navy-400">Gainers</h3>
            <p className="text-xl font-bold text-white">1,234</p>
          </div>
        </div>

        <div className="flex items-center gap-3 bg-navy-900/40 backdrop-blur-xl border border-navy-700/30 rounded-xl p-4">
          <TrendingDown className="w-6 h-6 text-danger flex-shrink-0" />
          <div>
            <h3 className="text-xs text-navy-400">Losers</h3>
            <p className="text-xl font-bold text-white">876</p>
          </div>
        </div>
      </motion.div>

      {/* GLOBAL INDICES - CLICKABLE */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="mb-8"
      >
        <h2 className="text-xl font-bold text-white mb-4">Global Indices</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {indices.map((index, idx) => (
            <motion.div
              key={index.name}
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.3 + idx * 0.05 }}
              whileHover={{ scale: 1.02 }}
              onClick={() => setSelectedIndex(index)}
              className="bg-navy-900/60 backdrop-blur-xl border border-navy-700/40 rounded-xl p-4 hover:border-accent-500/50 transition-all cursor-pointer"
            >
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs px-2 py-1 bg-navy-700/50 text-navy-300 rounded">
                  {index.region}
                </span>
                <div className={`flex items-center gap-1 ${
                  index.change >= 0 ? 'text-success' : 'text-danger'
                }`}>
                  {index.change >= 0 ? <TrendingUp className="w-4 h-4" /> : <TrendingDown className="w-4 h-4" />}
                  <span className="text-sm font-semibold">
                    {index.change >= 0 ? '+' : ''}{index.change.toFixed(2)}%
                  </span>
                </div>
              </div>
              <h3 className="text-base font-bold text-white mb-1">{index.name}</h3>
              <p className="text-2xl font-bold text-white">
                {index.value.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
              </p>
            </motion.div>
          ))}
        </div>
      </motion.div>

      {/* SECTOR PERFORMANCE - CLICKABLE */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.5 }}
        className="bg-navy-900/60 backdrop-blur-xl border border-navy-700/40 rounded-xl overflow-hidden"
      >
        <div className="p-4 border-b border-navy-700/40">
          <h2 className="text-xl font-bold text-white">Sector Performance</h2>
        </div>
        
        <div className="p-4">
          <div className="space-y-3">
            {sectors.map((sector, idx) => (
              <motion.div
                key={sector.name}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.6 + idx * 0.05 }}
                whileHover={{ scale: 1.01 }}
                onClick={() => setSelectedSector(sector)}
                className="flex items-center justify-between p-3 bg-navy-800/30 rounded-lg hover:bg-navy-800/50 transition-colors cursor-pointer"
              >
                <div className="flex-1">
                  <h3 className="text-white font-semibold text-sm">{sector.name}</h3>
                  <p className="text-xs text-navy-400">Volume: {sector.volume}</p>
                </div>
                <div className={`flex items-center gap-2 px-3 py-1.5 rounded-lg ${
                  sector.change >= 0 ? 'bg-success/20 text-success' : 'bg-danger/20 text-danger'
                }`}>
                  {sector.change >= 0 ? <TrendingUp className="w-4 h-4" /> : <TrendingDown className="w-4 h-4" />}
                  <span className="text-base font-bold">
                    {sector.change >= 0 ? '+' : ''}{sector.change.toFixed(2)}%
                  </span>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </motion.div>

      {/* INDEX DETAIL MODAL */}
      <AnimatePresence>
        {selectedIndex && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={() => setSelectedIndex(null)}
            className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4"
          >
            <motion.div
              initial={{ scale: 0.9, y: 20 }}
              animate={{ scale: 1, y: 0 }}
              exit={{ scale: 0.9, y: 20 }}
              onClick={(e) => e.stopPropagation()}
              className="bg-navy-900 border border-navy-700 rounded-2xl p-6 max-w-md w-full"
            >
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-2xl font-bold text-white">{selectedIndex.name}</h3>
                <button
                  onClick={() => setSelectedIndex(null)}
                  className="p-2 hover:bg-navy-800 rounded-lg transition-colors"
                >
                  <X className="w-5 h-5 text-navy-400" />
                </button>
              </div>
              
              <div className="space-y-4">
                <div>
                  <p className="text-sm text-navy-400 mb-1">Current Value</p>
                  <p className="text-3xl font-bold text-white">
                    {selectedIndex.value.toLocaleString(undefined, { minimumFractionDigits: 2 })}
                  </p>
                </div>
                
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <p className="text-sm text-navy-400 mb-1">Change</p>
                    <p className={`text-xl font-bold ${selectedIndex.change >= 0 ? 'text-success' : 'text-danger'}`}>
                      {selectedIndex.change >= 0 ? '+' : ''}{selectedIndex.change.toFixed(2)}%
                    </p>
                  </div>
                  <div>
                    <p className="text-sm text-navy-400 mb-1">Volume</p>
                    <p className="text-xl font-bold text-white">{selectedIndex.volume}</p>
                  </div>
                </div>
                
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <p className="text-sm text-navy-400 mb-1">High</p>
                    <p className="text-lg font-semibold text-white">{selectedIndex.high.toLocaleString()}</p>
                  </div>
                  <div>
                    <p className="text-sm text-navy-400 mb-1">Low</p>
                    <p className="text-lg font-semibold text-white">{selectedIndex.low.toLocaleString()}</p>
                  </div>
                </div>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* SECTOR DETAIL MODAL */}
      <AnimatePresence>
        {selectedSector && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={() => setSelectedSector(null)}
            className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4"
          >
            <motion.div
              initial={{ scale: 0.9, y: 20 }}
              animate={{ scale: 1, y: 0 }}
              exit={{ scale: 0.9, y: 20 }}
              onClick={(e) => e.stopPropagation()}
              className="bg-navy-900 border border-navy-700 rounded-2xl p-6 max-w-md w-full"
            >
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-2xl font-bold text-white">{selectedSector.name}</h3>
                <button
                  onClick={() => setSelectedSector(null)}
                  className="p-2 hover:bg-navy-800 rounded-lg transition-colors"
                >
                  <X className="w-5 h-5 text-navy-400" />
                </button>
              </div>
              
              <div className="space-y-4">
                <div>
                  <p className="text-sm text-navy-400 mb-1">Performance</p>
                  <p className={`text-3xl font-bold ${selectedSector.change >= 0 ? 'text-success' : 'text-danger'}`}>
                    {selectedSector.change >= 0 ? '+' : ''}{selectedSector.change.toFixed(2)}%
                  </p>
                </div>
                
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <p className="text-sm text-navy-400 mb-1">Volume</p>
                    <p className="text-xl font-bold text-white">{selectedSector.volume}</p>
                  </div>
                  <div>
                    <p className="text-sm text-navy-400 mb-1">Companies</p>
                    <p className="text-xl font-bold text-white">{selectedSector.companies}</p>
                  </div>
                </div>
                
                <div>
                  <p className="text-sm text-navy-400 mb-1">Top Gainer</p>
                  <p className="text-lg font-semibold text-success">{selectedSector.topGainer}</p>
                </div>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
