import { useState } from 'react';
import { motion } from 'framer-motion';
import TradingViewChart from '../TradingViewChart';
import CompanySidePanel from './CompanySidePanel';
import NewsSidePanel from './NewsSidePanel';

export default function HeroChart() {
  const [selectedSymbol, setSelectedSymbol] = useState('NSE:NIFTY');

  const handleSymbolChange = (symbol) => {
    setSelectedSymbol(symbol);
  };

  return (
    <section className="relative">
      {/* GRID LAYOUT - 70/30 SPLIT */}
      <motion.div 
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start"
      >
        {/* LEFT: CHART - 70% */}
        <div className="lg:col-span-8">
          <div className="h-[600px] lg:h-[700px] bg-navy-900/60 backdrop-blur-xl border border-navy-700/40 rounded-3xl p-6 shadow-2xl">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-xl font-bold text-white">Live Market Chart</h3>
              <div className="flex items-center space-x-2 px-3 py-1.5 bg-green-500/10 border border-green-500/30 rounded-full">
                <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
                <span className="text-xs font-semibold text-green-400">LIVE</span>
              </div>
            </div>
            <div className="h-[calc(100%-3rem)] rounded-2xl overflow-hidden">
              <TradingViewChart symbol={selectedSymbol} />
            </div>
          </div>
        </div>

        {/* RIGHT: SIDE PANELS - 30% */}
        <motion.div 
          className="lg:col-span-4 space-y-6"
          initial={{ opacity: 0, x: 30 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.3, duration: 0.6 }}
        >
          <CompanySidePanel 
            selectedSymbol={selectedSymbol}
            onSymbolChange={handleSymbolChange} 
          />
          <NewsSidePanel selectedSymbol={selectedSymbol} />
        </motion.div>
      </motion.div>
    </section>
  );
}
