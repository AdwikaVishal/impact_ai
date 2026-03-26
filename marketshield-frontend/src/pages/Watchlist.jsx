import { motion, AnimatePresence } from 'framer-motion';
import { Eye, Star, TrendingUp, TrendingDown, Plus, Bell, X, Search } from 'lucide-react';
import { useState } from 'react';

const INITIAL = [
  { symbol: 'NSE:NIFTY',    name: 'NIFTY 50',            price: 24150.75, change: 2.14,  alert: true },
  { symbol: 'NASDAQ:NVDA',  name: 'NVIDIA Corporation',  price: 875.28,   change: 3.21,  alert: false },
  { symbol: 'NSE:RELIANCE', name: 'Reliance Industries', price: 2845.60,  change: 1.23,  alert: true },
  { symbol: 'BTC-USD',      name: 'Bitcoin USD',         price: 68420.50, change: -2.45, alert: false },
  { symbol: 'GC=F',         name: 'Gold Futures',        price: 4352.30,  change: 0.85,  alert: true },
];

const POPULAR = [
  { symbol: 'NASDAQ:AAPL', name: 'Apple Inc.',                    type: 'Stock' },
  { symbol: 'NASDAQ:TSLA', name: 'Tesla Inc.',                    type: 'Stock' },
  { symbol: 'NASDAQ:MSFT', name: 'Microsoft Corporation',         type: 'Stock' },
  { symbol: 'NSE:TCS',     name: 'Tata Consultancy Services',     type: 'Stock' },
  { symbol: 'NSE:INFY',    name: 'Infosys',                       type: 'Stock' },
  { symbol: 'ETH-USD',     name: 'Ethereum USD',                  type: 'Crypto' },
  { symbol: 'SI=F',        name: 'Silver Futures',                type: 'Commodity' },
];

export default function Watchlist() {
  const [list, setList] = useState(INITIAL);
  const [showModal, setShowModal] = useState(false);
  const [query, setQuery] = useState('');

  const filtered = query
    ? POPULAR.filter(a => a.name.toLowerCase().includes(query.toLowerCase()) || a.symbol.toLowerCase().includes(query.toLowerCase()))
    : POPULAR;

  const add = (asset) => {
    if (list.some(i => i.symbol === asset.symbol)) return;
    setList(prev => [...prev, { ...asset, price: Math.random() * 900 + 100, change: (Math.random() - 0.5) * 10, alert: false }]);
    setShowModal(false);
    setQuery('');
  };

  const remove = (sym) => setList(prev => prev.filter(i => i.symbol !== sym));
  const toggleAlert = (sym) => setList(prev => prev.map(i => i.symbol === sym ? { ...i, alert: !i.alert } : i));

  return (
    <div className="max-w-[1400px] mx-auto px-4 sm:px-8 lg:px-16 py-8">
      {/* HEADER */}
      <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} className="flex items-center justify-between mb-8">
        <div className="flex items-center gap-4">
          <div className="w-10 h-10 bg-gradient-to-br from-accent-500 to-accent-cyan rounded-xl flex items-center justify-center shadow-glow-blue">
            <Eye className="w-5 h-5 text-white" />
          </div>
          <div>
            <h1 className="text-xl font-bold text-white">Watchlist</h1>
            <p className="text-xs text-navy-500 mt-0.5">{list.length} assets tracked</p>
          </div>
        </div>
        <button
          onClick={() => setShowModal(true)}
          className="btn-primary flex items-center gap-2 py-2.5 px-5 text-sm"
        >
          <Plus className="w-4 h-4" />
          Add Asset
        </button>
      </motion.div>

      {/* GRID */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
        {list.map((item, i) => (
          <motion.div
            key={item.symbol}
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.05 }}
            whileHover={{ y: -2 }}
            className="bg-navy-900/50 border border-white/5 hover:border-accent-500/20 rounded-2xl p-5 relative group transition-all"
          >
            {/* Remove */}
            <button
              onClick={() => remove(item.symbol)}
              className="absolute top-3.5 right-3.5 p-1.5 bg-navy-800/60 hover:bg-danger/20 rounded-lg opacity-0 group-hover:opacity-100 transition-all"
            >
              <X className="w-3.5 h-3.5 text-navy-400 hover:text-danger" />
            </button>

            <div className="flex items-center gap-2 mb-3">
              <Star className="w-4 h-4 text-warning fill-warning" />
              <button onClick={() => toggleAlert(item.symbol)} className="transition-colors">
                <Bell className={`w-3.5 h-3.5 ${item.alert ? 'text-accent-400' : 'text-navy-600'}`} />
              </button>
            </div>

            <h3 className="text-sm font-bold text-white mb-0.5 pr-6">{item.name}</h3>
            <p className="text-xs text-navy-500 font-mono mb-3">{item.symbol}</p>

            <div className="flex items-end justify-between">
              <p className="text-xl font-bold text-white tabular-nums">
                ${item.price.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
              </p>
              <div className={`flex items-center gap-1 px-2 py-1 rounded-lg text-xs font-bold ${
                item.change >= 0 ? 'bg-success/15 text-success' : 'bg-danger/15 text-danger'
              }`}>
                {item.change >= 0 ? <TrendingUp className="w-3 h-3" /> : <TrendingDown className="w-3 h-3" />}
                {item.change >= 0 ? '+' : ''}{item.change.toFixed(2)}%
              </div>
            </div>

            {item.alert && (
              <div className="mt-3 pt-3 border-t border-white/5 flex items-center gap-1.5">
                <Bell className="w-3 h-3 text-accent-400" />
                <span className="text-xs text-accent-400">Alert active</span>
              </div>
            )}
          </motion.div>
        ))}

        {/* ADD CARD */}
        <motion.div
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: list.length * 0.05 }}
          onClick={() => setShowModal(true)}
          className="border-2 border-dashed border-navy-700/50 hover:border-accent-500/40 rounded-2xl p-5
                     flex flex-col items-center justify-center min-h-[160px] cursor-pointer transition-all group"
        >
          <div className="w-10 h-10 bg-navy-800/60 group-hover:bg-accent-500/15 rounded-xl flex items-center justify-center mb-3 transition-colors">
            <Plus className="w-5 h-5 text-navy-500 group-hover:text-accent-400 transition-colors" />
          </div>
          <p className="text-sm font-medium text-navy-500 group-hover:text-white transition-colors">Add Asset</p>
        </motion.div>
      </div>

      {/* ADD MODAL */}
      <AnimatePresence>
        {showModal && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={() => setShowModal(false)}
            className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4"
          >
            <motion.div
              initial={{ scale: 0.92, y: 16 }}
              animate={{ scale: 1, y: 0 }}
              exit={{ scale: 0.92, y: 16 }}
              onClick={e => e.stopPropagation()}
              className="bg-navy-900 border border-white/8 rounded-2xl p-6 max-w-md w-full shadow-2xl"
            >
              <div className="flex items-center justify-between mb-5">
                <h3 className="text-base font-bold text-white">Add to Watchlist</h3>
                <button onClick={() => setShowModal(false)} className="p-1.5 hover:bg-white/5 rounded-lg transition-colors">
                  <X className="w-4 h-4 text-navy-400" />
                </button>
              </div>

              <div className="relative mb-4">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-navy-500 pointer-events-none" />
                <input
                  type="text"
                  value={query}
                  onChange={e => setQuery(e.target.value)}
                  placeholder="Search assets…"
                  autoFocus
                  className="w-full pl-9 pr-4 py-2.5 bg-navy-800/60 text-sm text-white placeholder-navy-500
                             border border-white/8 rounded-xl focus:border-accent-500/50 focus:outline-none
                             focus:ring-2 focus:ring-accent-500/15 transition-all"
                />
              </div>

              <div className="space-y-1.5 max-h-72 overflow-y-auto custom-scrollbar">
                {filtered.map(asset => (
                  <button
                    key={asset.symbol}
                    onClick={() => add(asset)}
                    className="w-full flex items-center justify-between px-4 py-3 bg-navy-800/40 hover:bg-navy-800/70
                               rounded-xl transition-colors text-left border border-white/5 hover:border-accent-500/20"
                  >
                    <div>
                      <p className="text-sm font-semibold text-white">{asset.name}</p>
                      <p className="text-xs text-navy-500 font-mono">{asset.symbol}</p>
                    </div>
                    <span className="text-xs px-2 py-0.5 bg-accent-500/10 text-accent-400 rounded-md border border-accent-500/20">
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
