import { motion, AnimatePresence } from 'framer-motion';
import { Eye, Star, TrendingUp, TrendingDown, Plus, Bell, X, Search } from 'lucide-react';
import { useState } from 'react';

export default function Watchlist() {
  const [watchlist, setWatchlist] = useState([
    { symbol: 'NSE:NIFTY', name: 'NIFTY 50', price: 24150.75, change: 2.14, alert: true },
    { symbol: 'NASDAQ:NVDA', name: 'NVIDIA Corporation', price: 875.28, change: 3.21, alert: false },
    { symbol: 'NSE:RELIANCE', name: 'Reliance Industries', price: 2845.60, change: 1.23, alert: true },
    { symbol: 'BTC-USD', name: 'Bitcoin USD', price: 68420.50, change: -2.45, alert: false },
    { symbol: 'GC=F', name: 'Gold Futures', price: 4352.30, change: 0.85, alert: true },
  ]);

  const [showAddModal, setShowAddModal] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);

  const popularAssets = [
    { symbol: 'NASDAQ:AAPL', name: 'Apple Inc.', type: 'Stock' },
    { symbol: 'NASDAQ:TSLA', name: 'Tesla Inc.', type: 'Stock' },
    { symbol: 'NASDAQ:MSFT', name: 'Microsoft Corporation', type: 'Stock' },
    { symbol: 'NSE:TCS', name: 'Tata Consultancy Services', type: 'Stock' },
    { symbol: 'NSE:INFY', name: 'Infosys', type: 'Stock' },
    { symbol: 'ETH-USD', name: 'Ethereum USD', type: 'Crypto' },
    { symbol: 'SI=F', name: 'Silver Futures', type: 'Commodity' },
  ];

  const handleSearch = (query) => {
    setSearchQuery(query);
    if (query.length > 0) {
      const filtered = popularAssets.filter(asset =>
        asset.name.toLowerCase().includes(query.toLowerCase()) ||
        asset.symbol.toLowerCase().includes(query.toLowerCase())
      );
      setSearchResults(filtered);
    } else {
      setSearchResults([]);
    }
  };

  const handleAddToWatchlist = (asset) => {
    // Check if already in watchlist
    if (watchlist.some(item => item.symbol === asset.symbol)) {
      alert('This asset is already in your watchlist!');
      return;
    }

    // Add to watchlist with mock data
    const newItem = {
      symbol: asset.symbol,
      name: asset.name,
      price: Math.random() * 1000 + 100,
      change: (Math.random() - 0.5) * 10,
      alert: false
    };

    setWatchlist([...watchlist, newItem]);
    setShowAddModal(false);
    setSearchQuery('');
    setSearchResults([]);
  };

  const handleRemoveFromWatchlist = (symbol) => {
    setWatchlist(watchlist.filter(item => item.symbol !== symbol));
  };

  const toggleAlert = (symbol) => {
    setWatchlist(watchlist.map(item =>
      item.symbol === symbol ? { ...item, alert: !item.alert } : item
    ));
  };

  return (
    <div className="max-w-[1400px] mx-auto px-8 lg:px-16">
      {/* COMPACT HEADER */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="mb-8"
      >
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-4">
            <div className="flex items-center justify-center w-12 h-12 bg-accent-500/20 rounded-xl">
              <Eye className="w-6 h-6 text-accent-400" />
            </div>
            <div>
              <h1 className="text-3xl font-bold text-white">Watchlist</h1>
              <p className="text-sm text-navy-400">Track your favorite assets</p>
            </div>
          </div>
          <button
            onClick={() => setShowAddModal(true)}
            className="flex items-center gap-2 px-6 py-3 bg-accent-500 hover:bg-accent-600 text-white rounded-xl transition-colors"
          >
            <Plus className="w-5 h-5" />
            Add Asset
          </button>
        </div>
      </motion.div>

      {/* WATCHLIST GRID */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {watchlist.map((item, idx) => (
          <motion.div
            key={item.symbol}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: idx * 0.1 }}
            whileHover={{ scale: 1.02 }}
            className="bg-navy-900/60 backdrop-blur-xl border border-navy-700/40 rounded-2xl p-6 relative group"
          >
            {/* Remove button */}
            <button
              onClick={() => handleRemoveFromWatchlist(item.symbol)}
              className="absolute top-4 right-4 p-2 bg-navy-800/50 hover:bg-danger/20 rounded-lg opacity-0 group-hover:opacity-100 transition-all"
            >
              <X className="w-4 h-4 text-navy-400 hover:text-danger" />
            </button>

            <div className="flex items-start justify-between mb-4">
              <div className="flex items-center gap-2">
                <Star className="w-5 h-5 text-warning fill-warning" />
                <button
                  onClick={() => toggleAlert(item.symbol)}
                  className={`transition-colors ${item.alert ? 'text-accent-400' : 'text-navy-600'}`}
                >
                  <Bell className="w-4 h-4" />
                </button>
              </div>
              <div className={`flex items-center gap-1 px-3 py-1 rounded-full ${
                item.change >= 0 ? 'bg-success/20 text-success' : 'bg-danger/20 text-danger'
              }`}>
                {item.change >= 0 ? <TrendingUp className="w-4 h-4" /> : <TrendingDown className="w-4 h-4" />}
                <span className="text-sm font-semibold">
                  {item.change >= 0 ? '+' : ''}{item.change.toFixed(2)}%
                </span>
              </div>
            </div>

            <div className="mb-2">
              <h3 className="text-lg font-bold text-white mb-1">{item.name}</h3>
              <p className="text-sm text-navy-400 font-mono">{item.symbol}</p>
            </div>

            <div className="flex items-baseline justify-between">
              <span className="text-3xl font-bold text-white">
                ${item.price.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
              </span>
            </div>

            {item.alert && (
              <div className="mt-4 pt-4 border-t border-navy-700/30">
                <p className="text-xs text-accent-400 flex items-center gap-1">
                  <Bell className="w-3 h-3" />
                  Price alert active
                </p>
              </div>
            )}
          </motion.div>
        ))}

        {/* ADD MORE CARD */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: watchlist.length * 0.1 }}
          onClick={() => setShowAddModal(true)}
          className="bg-navy-900/40 backdrop-blur-xl border-2 border-dashed border-navy-700/40 rounded-2xl p-12 text-center hover:border-accent-500/50 transition-all cursor-pointer flex flex-col items-center justify-center min-h-[200px]"
        >
          <Plus className="w-12 h-12 text-navy-600 mb-4" />
          <h3 className="text-lg font-semibold text-navy-400 mb-2">Add More Assets</h3>
          <p className="text-sm text-navy-500">
            Track stocks, commodities, crypto
          </p>
        </motion.div>
      </div>

      {/* ADD ASSET MODAL */}
      <AnimatePresence>
        {showAddModal && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={() => setShowAddModal(false)}
            className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4"
          >
            <motion.div
              initial={{ scale: 0.9, y: 20 }}
              animate={{ scale: 1, y: 0 }}
              exit={{ scale: 0.9, y: 20 }}
              onClick={(e) => e.stopPropagation()}
              className="bg-navy-900 border border-navy-700 rounded-2xl p-6 max-w-md w-full"
            >
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-2xl font-bold text-white">Add to Watchlist</h3>
                <button
                  onClick={() => setShowAddModal(false)}
                  className="p-2 hover:bg-navy-800 rounded-lg transition-colors"
                >
                  <X className="w-5 h-5 text-navy-400" />
                </button>
              </div>

              {/* Search Input */}
              <div className="relative mb-6">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-navy-500" />
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => handleSearch(e.target.value)}
                  placeholder="Search stocks, crypto, commodities..."
                  className="w-full pl-11 pr-4 py-3 bg-navy-800/50 text-white placeholder-navy-500 border border-navy-700 rounded-xl focus:border-accent-500 focus:outline-none focus:ring-2 focus:ring-accent-500/20 transition-all"
                  autoFocus
                />
              </div>

              {/* Search Results or Popular Assets */}
              <div className="space-y-2 max-h-96 overflow-y-auto custom-scrollbar">
                {(searchResults.length > 0 ? searchResults : popularAssets).map((asset) => (
                  <button
                    key={asset.symbol}
                    onClick={() => handleAddToWatchlist(asset)}
                    className="w-full flex items-center justify-between p-4 bg-navy-800/30 hover:bg-navy-800/50 rounded-xl transition-colors text-left"
                  >
                    <div>
                      <h4 className="text-white font-semibold">{asset.name}</h4>
                      <p className="text-sm text-navy-400 font-mono">{asset.symbol}</p>
                    </div>
                    <span className="text-xs px-2 py-1 bg-accent-500/20 text-accent-400 rounded">
                      {asset.type}
                    </span>
                  </button>
                ))}
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
