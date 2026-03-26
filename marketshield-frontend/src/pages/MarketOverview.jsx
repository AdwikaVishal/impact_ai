import { motion, AnimatePresence } from 'framer-motion';
import { Globe, TrendingUp, TrendingDown, Activity, X, BarChart3, Zap } from 'lucide-react';
import { useState, useEffect } from 'react';

// NSE hours: Mon–Fri 09:15–15:30 IST (UTC+5:30)
function useNSEMarketStatus() {
  const [status, setStatus] = useState({ open: false, label: 'Closed' });

  useEffect(() => {
    const check = () => {
      const now = new Date();
      // Convert to IST
      const ist = new Date(now.toLocaleString('en-US', { timeZone: 'Asia/Kolkata' }));
      const day = ist.getDay(); // 0=Sun, 6=Sat
      const h = ist.getHours();
      const m = ist.getMinutes();
      const mins = h * 60 + m;
      const isWeekday = day >= 1 && day <= 5;
      const isOpen = isWeekday && mins >= 9 * 60 + 15 && mins < 15 * 60 + 30;
      setStatus({ open: isOpen, label: isOpen ? 'Open' : 'Closed' });
    };
    check();
    const t = setInterval(check, 30000);
    return () => clearInterval(t);
  }, []);

  return status;
}

const INDICES = [
  { name: 'NIFTY 50',  value: 24150.75, change: 2.14,  region: 'India', volume: '2.4B', high: 24200.50, low: 23950.25 },
  { name: 'SENSEX',    value: 79486.32, change: 1.89,  region: 'India', volume: '1.8B', high: 79650.00, low: 78900.00 },
  { name: 'S&P 500',   value: 5234.18,  change: 0.45,  region: 'US',    volume: '3.2B', high: 5245.30,  low: 5220.10 },
  { name: 'NASDAQ',    value: 16340.87, change: 1.23,  region: 'US',    volume: '4.1B', high: 16380.50, low: 16250.00 },
  { name: 'DOW JONES', value: 38790.43, change: -0.12, region: 'US',    volume: '2.9B', high: 38850.00, low: 38720.00 },
  { name: 'FTSE 100',  value: 8245.67,  change: 0.78,  region: 'UK',    volume: '1.5B', high: 8260.00,  low: 8230.00 },
];

const SECTORS = [
  { name: 'Technology', change: 2.45,  volume: '12.5B', companies: 145, topGainer: 'NVDA +5.2%' },
  { name: 'Finance',    change: 1.23,  volume: '8.3B',  companies: 98,  topGainer: 'JPM +3.1%' },
  { name: 'Healthcare', change: -0.56, volume: '5.7B',  companies: 76,  topGainer: 'PFE +1.8%' },
  { name: 'Energy',     change: 3.12,  volume: '9.1B',  companies: 54,  topGainer: 'XOM +4.5%' },
  { name: 'Consumer',   change: 0.89,  volume: '6.4B',  companies: 112, topGainer: 'AMZN +2.3%' },
  { name: 'Industrial', change: 1.67,  volume: '4.2B',  companies: 89,  topGainer: 'CAT +3.7%' },
];

const ChangeChip = ({ change }) => (
  <div className={`flex items-center gap-1 px-2.5 py-1 rounded-lg text-xs font-bold ${
    change >= 0 ? 'bg-success/15 text-success' : 'bg-danger/15 text-danger'
  }`}>
    {change >= 0 ? <TrendingUp className="w-3 h-3" /> : <TrendingDown className="w-3 h-3" />}
    {change >= 0 ? '+' : ''}{change.toFixed(2)}%
  </div>
);

const Modal = ({ item, type, onClose }) => (
  <motion.div
    initial={{ opacity: 0 }}
    animate={{ opacity: 1 }}
    exit={{ opacity: 0 }}
    onClick={onClose}
    className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4"
  >
    <motion.div
      initial={{ scale: 0.92, y: 16 }}
      animate={{ scale: 1, y: 0 }}
      exit={{ scale: 0.92, y: 16 }}
      onClick={e => e.stopPropagation()}
      className="bg-navy-900 border border-white/8 rounded-2xl p-6 max-w-sm w-full shadow-2xl"
    >
      <div className="flex items-center justify-between mb-5">
        <h3 className="text-lg font-bold text-white">{item.name}</h3>
        <button onClick={onClose} className="p-1.5 hover:bg-white/5 rounded-lg transition-colors">
          <X className="w-4 h-4 text-navy-400" />
        </button>
      </div>

      {type === 'index' ? (
        <div className="space-y-3">
          <div className="p-4 bg-navy-800/50 rounded-xl border border-white/5">
            <p className="section-label mb-1">Current Value</p>
            <p className="text-2xl font-bold text-white tabular-nums">
              {item.value.toLocaleString(undefined, { minimumFractionDigits: 2 })}
            </p>
          </div>
          <div className="grid grid-cols-2 gap-3">
            {[['Change', null, item.change], ['Volume', item.volume, null], ['High', item.high?.toLocaleString(), null], ['Low', item.low?.toLocaleString(), null]].map(([label, val, chg]) => (
              <div key={label} className="p-3 bg-navy-800/50 rounded-xl border border-white/5">
                <p className="section-label mb-1">{label}</p>
                {chg != null ? <ChangeChip change={chg} /> : <p className="text-sm font-bold text-white">{val}</p>}
              </div>
            ))}
          </div>
        </div>
      ) : (
        <div className="space-y-3">
          <div className="p-4 bg-navy-800/50 rounded-xl border border-white/5">
            <p className="section-label mb-1">Performance</p>
            <ChangeChip change={item.change} />
          </div>
          <div className="grid grid-cols-2 gap-3">
            {[['Volume', item.volume], ['Companies', item.companies], ['Top Gainer', item.topGainer]].map(([label, val]) => (
              <div key={label} className="p-3 bg-navy-800/50 rounded-xl border border-white/5">
                <p className="section-label mb-1">{label}</p>
                <p className="text-sm font-bold text-white">{val}</p>
              </div>
            ))}
          </div>
        </div>
      )}
    </motion.div>
  </motion.div>
);

export default function MarketOverview() {
  const [selIndex, setSelIndex] = useState(null);
  const [selSector, setSelSector] = useState(null);
  const market = useNSEMarketStatus();

  return (
    <div className="max-w-[1400px] mx-auto px-4 sm:px-8 lg:px-16 py-8 space-y-8">
      {/* HEADER */}
      <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} className="flex items-center gap-4">
        <div className="w-10 h-10 bg-gradient-to-br from-accent-500 to-accent-cyan rounded-xl flex items-center justify-center shadow-glow-blue">
          <Globe className="w-5 h-5 text-white" />
        </div>
        <div>
          <h1 className="text-xl font-bold text-white">Market Overview</h1>
          <p className="text-xs text-navy-500 mt-0.5">Global indices and sector performance</p>
        </div>
      </motion.div>

      {/* STATUS STRIP */}
      <motion.div
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="grid grid-cols-3 gap-4"
      >
        {[
          {
            icon: Activity,
            label: 'NSE Market',
            value: market.label,
            color: market.open ? 'text-success' : 'text-danger',
            bg: market.open ? 'bg-success/10 border-success/20' : 'bg-danger/10 border-danger/20',
          },
          { icon: TrendingUp,   label: 'Gainers', value: '1,234', color: 'text-accent-400', bg: 'bg-navy-800/50 border-white/5' },
          { icon: TrendingDown, label: 'Losers',  value: '876',   color: 'text-danger',     bg: 'bg-navy-800/50 border-white/5' },
        ].map(({ icon: Icon, label, value, color, bg }) => (
          <div key={label} className={`flex items-center gap-3 p-4 rounded-xl border ${bg}`}>
            <Icon className={`w-5 h-5 ${color} flex-shrink-0`} />
            <div>
              <p className="section-label">{label}</p>
              <div className="flex items-center gap-2">
                <p className={`text-lg font-bold ${color}`}>{value}</p>
                {label === 'NSE Market' && (
                  <span className={`w-2 h-2 rounded-full flex-shrink-0 ${market.open ? 'bg-success live-dot' : 'bg-danger'}`} />
                )}
              </div>
            </div>
          </div>
        ))}
      </motion.div>

      {/* INDICES */}
      <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.15 }}>
        <p className="section-label mb-4">Global Indices</p>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {INDICES.map((idx, i) => (
            <motion.div
              key={idx.name}
              initial={{ opacity: 0, scale: 0.97 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.2 + i * 0.04 }}
              whileHover={{ y: -2 }}
              onClick={() => setSelIndex(idx)}
              className="bg-navy-900/50 border border-white/5 hover:border-accent-500/25 rounded-2xl p-4 cursor-pointer transition-all"
            >
              <div className="flex items-center justify-between mb-3">
                <span className="text-xs font-medium text-navy-500 bg-navy-800/60 px-2 py-0.5 rounded-md">{idx.region}</span>
                <ChangeChip change={idx.change} />
              </div>
              <p className="text-sm font-semibold text-navy-400 mb-1">{idx.name}</p>
              <p className="text-xl font-bold text-white tabular-nums">
                {idx.value.toLocaleString(undefined, { minimumFractionDigits: 2 })}
              </p>
            </motion.div>
          ))}
        </div>
      </motion.div>

      {/* SECTORS */}
      <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}>
        <p className="section-label mb-4">Sector Performance</p>
        <div className="bg-navy-900/50 border border-white/5 rounded-2xl overflow-hidden">
          {SECTORS.map((s, i) => (
            <motion.div
              key={s.name}
              initial={{ opacity: 0, x: -12 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.35 + i * 0.04 }}
              whileHover={{ backgroundColor: 'rgba(255,255,255,0.03)' }}
              onClick={() => setSelSector(s)}
              className="flex items-center justify-between px-5 py-3.5 border-b border-white/5 last:border-0 cursor-pointer transition-colors"
            >
              <div>
                <p className="text-sm font-semibold text-white">{s.name}</p>
                <p className="text-xs text-navy-500">Vol: {s.volume}</p>
              </div>
              <div className="flex items-center gap-3">
                {/* Mini bar */}
                <div className="hidden sm:block w-24 h-1.5 bg-navy-700/50 rounded-full overflow-hidden">
                  <div
                    className={`h-full rounded-full ${s.change >= 0 ? 'bg-success' : 'bg-danger'}`}
                    style={{ width: `${Math.min(Math.abs(s.change) * 15, 100)}%` }}
                  />
                </div>
                <ChangeChip change={s.change} />
              </div>
            </motion.div>
          ))}
        </div>
      </motion.div>

      {/* MODALS */}
      <AnimatePresence>
        {selIndex && <Modal item={selIndex} type="index" onClose={() => setSelIndex(null)} />}
        {selSector && <Modal item={selSector} type="sector" onClose={() => setSelSector(null)} />}
      </AnimatePresence>
    </div>
  );
}
