import { useState } from 'react';
import { Search, Zap, Sparkles, Loader2 } from 'lucide-react';
import { motion } from 'framer-motion';
import { useAnalysisStore } from '../../stores/useAnalysisStore';

const EXAMPLES = [
  'Tesla stock drops 8% after weak Q3 deliveries miss estimates',
  'Bitcoin crashes amid China crypto ban rumors — analysts warn',
  'NVIDIA GPUs sold out globally as AI boom accelerates demand',
  'Fed signals rate cut next month — markets rally on news',
];

export default function HeadlineInput() {
  const [headline, setHeadline] = useState('');
  const { analyze, isAnalyzing } = useAnalysisStore();

  const handleAnalyze = () => { if (headline.trim()) analyze(headline); };

  return (
    <div className="space-y-5">
      {/* INPUT CARD */}
      <div className="bg-navy-900/50 border border-white/5 rounded-2xl p-5 shadow-card">
        <label className="section-label block mb-3">Enter Financial Headline</label>
        <div className="relative">
          <Search className="absolute left-4 top-4 w-5 h-5 text-navy-500 pointer-events-none" />
          <textarea
            value={headline}
            onChange={e => setHeadline(e.target.value)}
            onKeyDown={e => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); handleAnalyze(); } }}
            placeholder="e.g. Tesla stock drops after weak deliveries…"
            rows={3}
            className="w-full pl-12 pr-4 py-3.5 bg-navy-800/60 text-white placeholder-navy-500
                       border border-white/8 rounded-xl resize-none
                       focus:border-accent-500/50 focus:outline-none focus:ring-2 focus:ring-accent-500/15
                       transition-all text-sm leading-relaxed"
          />
        </div>

        <motion.button
          whileHover={{ scale: 1.01 }}
          whileTap={{ scale: 0.98 }}
          onClick={handleAnalyze}
          disabled={isAnalyzing || !headline.trim()}
          className="mt-4 w-full btn-primary flex items-center justify-center gap-2.5 py-3.5 text-sm"
        >
          {isAnalyzing ? (
            <>
              <Loader2 className="w-4 h-4 animate-spin" />
              Analyzing with AI…
            </>
          ) : (
            <>
              <Zap className="w-4 h-4" />
              Analyze Headline
            </>
          )}
        </motion.button>
      </div>

      {/* EXAMPLES */}
      <div>
        <p className="section-label mb-3">Try an example</p>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
          {EXAMPLES.map((ex, i) => (
            <motion.button
              key={i}
              initial={{ opacity: 0, y: 6 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.06 }}
              whileHover={{ scale: 1.01 }}
              onClick={() => setHeadline(ex)}
              className="text-left px-4 py-3 bg-navy-800/40 hover:bg-navy-800/70 text-xs text-navy-300
                         hover:text-white rounded-xl border border-white/5 hover:border-accent-500/25
                         transition-all flex items-start gap-2.5"
            >
              <Sparkles className="w-3.5 h-3.5 text-accent-400 flex-shrink-0 mt-0.5" />
              {ex}
            </motion.button>
          ))}
        </div>
      </div>
    </div>
  );
}
