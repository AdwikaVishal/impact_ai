import { motion } from 'framer-motion';
import HeadlineAnalyzer from '../components/analyzer/HeadlineAnalyzer';
import { Newspaper, Shield, TrendingUp, AlertTriangle } from 'lucide-react';

export default function Analyzer() {
  return (
    <div className="max-w-[1600px] mx-auto px-8 lg:px-16">
      {/* COMPACT HEADER */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="mb-6"
      >
        <div className="flex items-center gap-3 mb-4">
          <div className="flex items-center justify-center w-10 h-10 bg-accent-500/20 rounded-xl">
            <Newspaper className="w-5 h-5 text-accent-400" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-white">AI Headline Analyzer</h1>
            <p className="text-xs text-navy-400">Real-time analysis powered by ML models</p>
          </div>
        </div>
      </motion.div>

      {/* FEATURES - COMPACT INLINE */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="flex flex-wrap gap-3 mb-6"
      >
        <div className="flex items-center gap-2 bg-navy-900/40 backdrop-blur-xl border border-navy-700/30 rounded-lg px-3 py-2">
          <Shield className="w-4 h-4 text-success flex-shrink-0" />
          <span className="text-xs font-medium text-white">Fake News Detection</span>
        </div>
        
        <div className="flex items-center gap-2 bg-navy-900/40 backdrop-blur-xl border border-navy-700/30 rounded-lg px-3 py-2">
          <TrendingUp className="w-4 h-4 text-accent-400 flex-shrink-0" />
          <span className="text-xs font-medium text-white">Sentiment Analysis</span>
        </div>
        
        <div className="flex items-center gap-2 bg-navy-900/40 backdrop-blur-xl border border-navy-700/30 rounded-lg px-3 py-2">
          <AlertTriangle className="w-4 h-4 text-warning flex-shrink-0" />
          <span className="text-xs font-medium text-white">Risk Assessment</span>
        </div>
      </motion.div>

      {/* ANALYZER COMPONENT */}
      <div className="mb-8">
        <HeadlineAnalyzer />
      </div>
    </div>
  );
}
