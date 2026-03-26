import { motion } from 'framer-motion';
import HeadlineAnalyzer from '../components/analyzer/HeadlineAnalyzer';
import { Brain, Shield, TrendingUp, AlertTriangle, Zap } from 'lucide-react';

const FEATURES = [
  { icon: Shield,       label: 'Fake News Detection',  color: 'text-success', bg: 'bg-success/10 border-success/20' },
  { icon: TrendingUp,   label: 'Sentiment Analysis',   color: 'text-accent-400', bg: 'bg-accent-500/10 border-accent-500/20' },
  { icon: AlertTriangle,label: 'Risk Assessment',      color: 'text-warning', bg: 'bg-warning/10 border-warning/20' },
  { icon: Zap,          label: 'Trading Signals',      color: 'text-info',    bg: 'bg-info/10 border-info/20' },
];

export default function Analyzer() {
  return (
    <div className="max-w-[1400px] mx-auto px-4 sm:px-8 lg:px-16 py-8">
      {/* PAGE HEADER */}
      <motion.div
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        className="mb-8"
      >
        <div className="flex items-center gap-4 mb-4">
          <div className="w-10 h-10 bg-gradient-to-br from-accent-500 to-accent-cyan rounded-xl flex items-center justify-center shadow-glow-blue">
            <Brain className="w-5 h-5 text-white" />
          </div>
          <div>
            <h1 className="text-xl font-bold text-white">AI Headline Analyzer</h1>
            <p className="text-xs text-navy-500 mt-0.5">Paste any financial headline — get instant ML-powered analysis</p>
          </div>
        </div>

        {/* Feature pills */}
        <div className="flex flex-wrap gap-2">
          {FEATURES.map(({ icon: Icon, label, color, bg }) => (
            <div key={label} className={`flex items-center gap-1.5 px-3 py-1.5 rounded-full border text-xs font-medium ${bg} ${color}`}>
              <Icon className="w-3.5 h-3.5" />
              {label}
            </div>
          ))}
        </div>
      </motion.div>

      <HeadlineAnalyzer />
    </div>
  );
}
