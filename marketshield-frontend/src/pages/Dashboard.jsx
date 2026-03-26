import { motion } from 'framer-motion';
import { Shield, TrendingUp, Brain, Zap, BarChart3, Eye } from 'lucide-react';
import HeroChart from '../components/dashboard/HeroChart';

const STATS = [
  { icon: BarChart3, label: 'Markets Tracked',    value: '50+',   color: 'text-accent-400' },
  { icon: Brain,     label: 'ML Models Active',   value: '11',    color: 'text-purple-400' },
  { icon: Zap,       label: 'Real-time Signals',  value: 'Live',  color: 'text-success'    },
  { icon: Eye,       label: 'Smart Money Alerts', value: '24/7',  color: 'text-warning'    },
];

export default function Dashboard() {
  return (
    <div className="max-w-[1400px] mx-auto px-4 sm:px-8 lg:px-16">
      {/* HERO SECTION */}
      <motion.div
        initial={{ opacity: 0, y: 24 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.55 }}
        className="pt-10 pb-8 text-center"
      >
        {/* Badge */}
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.1 }}
          className="inline-flex items-center gap-2 px-4 py-1.5 bg-accent-500/10 border border-accent-500/20 rounded-full mb-6"
        >
          <span className="w-1.5 h-1.5 rounded-full bg-accent-400 live-dot" />
          <span className="text-xs font-semibold text-accent-400 tracking-wide">AI-Powered Financial Intelligence</span>
        </motion.div>

        {/* Title */}
        <motion.h1
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.15 }}
          className="text-4xl sm:text-5xl lg:text-6xl font-bold text-white leading-tight tracking-tight mb-5 max-w-4xl mx-auto"
        >
          Detect Market{' '}
          <span className="bg-gradient-to-r from-accent-400 via-accent-cyan to-accent-300 bg-clip-text text-transparent">
            Manipulation
          </span>{' '}
          Before It Hits
        </motion.h1>

        {/* Subtitle */}
        <motion.p
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.22 }}
          className="text-base sm:text-lg text-navy-400 leading-relaxed max-w-2xl mx-auto mb-8"
        >
          An AI-powered platform that analyzes real-time market data, news sentiment, and trading
          patterns to detect manipulation, track smart money, and generate actionable trading insights.
        </motion.p>

        {/* STAT STRIP */}
        <motion.div
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="inline-grid grid-cols-2 sm:grid-cols-4 gap-px bg-white/5 border border-white/5 rounded-2xl overflow-hidden mb-2"
        >
          {STATS.map(({ icon: Icon, label, value, color }) => (
            <div key={label} className="flex items-center gap-3 px-5 py-3.5 bg-navy-900/80">
              <Icon className={`w-4 h-4 ${color} flex-shrink-0`} />
              <div className="text-left">
                <p className="text-xs text-navy-500">{label}</p>
                <p className={`text-sm font-bold ${color}`}>{value}</p>
              </div>
            </div>
          ))}
        </motion.div>
      </motion.div>

      {/* DASHBOARD CONTENT */}
      <div className="pb-12">
        <HeroChart />
      </div>
    </div>
  );
}

