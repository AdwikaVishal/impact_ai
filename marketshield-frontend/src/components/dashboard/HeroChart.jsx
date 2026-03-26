import { useState } from 'react';
import { motion } from 'framer-motion';
import TradingViewChart from '../TradingViewChart';
import CompanySidePanel from './CompanySidePanel';
import NewsSidePanel from './NewsSidePanel';

export default function HeroChart() {
  const [selectedSymbol, setSelectedSymbol] = useState('NASDAQ:AAPL');

  return (
    <div className="space-y-6">
      {/* TOP ROW: chart + company panel */}
      <motion.div
        initial={{ opacity: 0, y: 24 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="grid grid-cols-1 xl:grid-cols-12 gap-5 items-start"
      >
        {/* CHART — 8 cols */}
        <div className="xl:col-span-8">
          <div className="h-[520px] lg:h-[620px] bg-navy-900/50 border border-white/5 rounded-2xl overflow-hidden shadow-card">
            {/* Chart header */}
            <div className="flex items-center justify-between px-5 py-3.5 border-b border-white/5">
              <div className="flex items-center gap-3">
                <span className="text-sm font-semibold text-white">Live Chart</span>
                <span className="text-xs text-navy-500 font-mono">{selectedSymbol}</span>
              </div>
              <div className="flex items-center gap-1.5 px-2.5 py-1 bg-success/10 border border-success/20 rounded-full">
                <span className="w-1.5 h-1.5 rounded-full bg-success live-dot" />
                <span className="text-xs font-semibold text-success">LIVE</span>
              </div>
            </div>
            <div className="h-[calc(100%-49px)]">
              <TradingViewChart symbol={selectedSymbol} />
            </div>
          </div>
        </div>

        {/* COMPANY PANEL — 4 cols */}
        <motion.div
          className="xl:col-span-4"
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.2, duration: 0.5 }}
        >
          <CompanySidePanel
            selectedSymbol={selectedSymbol}
            onSymbolChange={setSelectedSymbol}
          />
        </motion.div>
      </motion.div>

      {/* BOTTOM ROW: full-width news */}
      <motion.div
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.35, duration: 0.5 }}
      >
        <NewsSidePanel selectedSymbol={selectedSymbol} />
      </motion.div>
    </div>
  );
}
