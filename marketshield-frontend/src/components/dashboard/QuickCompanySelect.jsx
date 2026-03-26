import { motion } from 'framer-motion';
import { ChevronRight } from 'lucide-react';

const companies = [
  { name: 'Tesla', symbol: 'NASDAQ:TSLA', change: '+2.3%', positive: true },
  { name: 'Reliance', symbol: 'NSE:RELIANCE', change: '+1.8%', positive: true },
  { name: 'TCS', symbol: 'NSE:TCS', change: '+0.9%', positive: true },
  { name: 'Apple', symbol: 'NASDAQ:AAPL', change: '+3.1%', positive: true },
  { name: 'NVIDIA', symbol: 'NASDAQ:NVDA', change: '+5.2%', positive: true },
  { name: 'Infosys', symbol: 'NSE:INFY', change: '+1.2%', positive: true },
  { name: 'Amazon', symbol: 'NASDAQ:AMZN', change: '+2.7%', positive: true },
];

export default function QuickCompanySelect() {
  return (
    <section>
      {/* SECTION HEADER */}
      <div className="text-center mb-12">
        <h3 className="text-2xl font-bold text-white">Quick Select Companies</h3>
        <p className="text-navy-500 mt-2">Click to analyze any company</p>
      </div>
      
      {/* COMPANY CARDS */}
      <div className="flex gap-4 overflow-x-auto pb-4 px-2 custom-scrollbar">
        {companies.map((company, idx) => (
          <motion.button
            key={company.symbol}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: idx * 0.05 }}
            whileHover={{ scale: 1.03, y: -4 }}
            whileTap={{ scale: 0.98 }}
            className="group flex items-center justify-between px-6 py-4 bg-navy-900/60 backdrop-blur-xl border border-navy-700/40 rounded-2xl hover:border-accent-500/50 hover:shadow-glow-blue transition-all duration-300 min-w-[220px] flex-shrink-0"
          >
            <div className="text-left">
              <p className="font-bold text-white text-lg mb-1">{company.name}</p>
              <p className="text-xs text-navy-500 font-mono">{company.symbol.split(':')[1]}</p>
            </div>
            <div className="flex items-center space-x-3 ml-4">
              <span className={`text-sm font-bold ${company.positive ? 'text-success' : 'text-danger'}`}>
                {company.change}
              </span>
              <ChevronRight className="w-4 h-4 text-navy-500 group-hover:text-accent-400 transition-colors" />
            </div>
          </motion.button>
        ))}
      </div>
    </section>
  );
}
