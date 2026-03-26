import { useState } from 'react';
import { Search, Zap, Sparkles } from 'lucide-react';
import { motion } from 'framer-motion';
import { useAnalysisStore } from '../../stores/useAnalysisStore';

export default function HeadlineInput() {
  const [headline, setHeadline] = useState('');
  const { analyze, isAnalyzing } = useAnalysisStore();

  const handleAnalyze = () => {
    if (headline.trim()) {
      analyze(headline);
    }
  };

  const examples = [
    "Tesla stock drops after weak deliveries",
    "Bitcoin crashes amid China ban rumors",
    "NVIDIA GPUs sold out - AI boom continues",
    "Fed hints at rate cut next month"
  ];

  return (
    <div className="space-y-8">
      {/* INPUT BOX */}
      <div className="glass-card p-8">
        <div className="relative">
          <div className="absolute left-6 top-6 z-10">
            <Search className="w-6 h-6 text-accent-400" />
          </div>
          
          <textarea
            value={headline}
            onChange={(e) => setHeadline(e.target.value)}
            placeholder="Enter a financial headline to analyze..."
            className="w-full pl-16 pr-6 py-6 text-lg bg-navy-900/50 text-white placeholder-navy-500 border-2 border-navy-700 rounded-2xl focus:border-accent-500 focus:outline-none focus:ring-4 focus:ring-accent-500/20 transition-all resize-none h-36"
            onKeyPress={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                handleAnalyze();
              }
            }}
          />
          
          <motion.button
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            onClick={handleAnalyze}
            disabled={isAnalyzing || !headline.trim()}
            className="mt-6 w-full btn-primary py-4 text-lg font-bold flex items-center justify-center space-x-3"
          >
            {isAnalyzing ? (
              <>
                <div className="w-5 h-5 border-3 border-white border-t-transparent rounded-full animate-spin"></div>
                <span>Analyzing...</span>
              </>
            ) : (
              <>
                <Zap className="w-6 h-6" />
                <span>ANALYZE HEADLINE</span>
              </>
            )}
          </motion.button>
        </div>
      </div>

      {/* EXAMPLE HEADLINES */}
      <div>
        <p className="text-sm text-navy-500 mb-4 text-center">Try these examples:</p>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {examples.map((ex, i) => (
            <motion.button
              key={i}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.1 }}
              whileHover={{ scale: 1.02 }}
              onClick={() => setHeadline(ex)}
              className="text-left px-4 py-3 bg-navy-800/50 hover:bg-navy-700/50 text-sm text-navy-300 hover:text-white rounded-xl border border-navy-700/50 hover:border-accent-500/50 transition-all"
            >
              <Sparkles className="w-4 h-4 inline mr-2 text-accent-400" />
              {ex}
            </motion.button>
          ))}
        </div>
      </div>
    </div>
  );
}
