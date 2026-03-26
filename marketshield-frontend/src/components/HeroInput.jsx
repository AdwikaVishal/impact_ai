import { useState } from 'react';
import { Search, Sparkles, Zap, TrendingUp, Shield, Brain } from 'lucide-react';
import { motion } from 'framer-motion';

const HeroInput = ({ onAnalyze, loading }) => {
  const [headline, setHeadline] = useState('');

  const handleAnalyze = () => {
    if (headline.trim()) {
      onAnalyze(headline);
    }
  };

  const examples = [
    "Tesla stock drops after weak deliveries",
    "Bitcoin crashes amid China ban rumors", 
    "NVIDIA GPUs sold out - AI boom continues",
    "Fed hints at rate cut next month"
  ];

  return (
    <div className="max-w-6xl mx-auto px-6 py-12">
      {/* Hero Title */}
      <motion.div 
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="text-center mb-12"
      >
        <motion.div
          animate={{ rotate: [0, 5, -5, 0] }}
          transition={{ duration: 4, repeat: Infinity }}
          className="inline-block mb-4"
        >
          <div className="p-4 bg-gradient-to-br from-accent-500 to-accent-cyan rounded-3xl shadow-glow-blue">
            <Brain className="w-12 h-12 text-white" />
          </div>
        </motion.div>
        
        <h1 className="text-5xl md:text-6xl font-bold mb-6">
          <span className="gradient-text">Detect Financial Misinformation</span>
          <br />
          <span className="text-white">Instantly with AI</span>
        </h1>
        
        <p className="text-xl text-navy-400 max-w-3xl mx-auto leading-relaxed">
          Paste any financial headline. Our AI analyzes risk, market impact, fake news probability, 
          and generates real-time trading signals powered by 11 ML models.
        </p>
      </motion.div>

      {/* Input Section */}
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.2 }}
        className="glass-card p-8 shadow-2xl"
      >
        <div className="relative">
          <div className="absolute left-6 top-6 z-10">
            <Search className="w-6 h-6 text-accent-400" />
          </div>
          
          <textarea
            value={headline}
            onChange={(e) => setHeadline(e.target.value)}
            placeholder="Enter a financial headline to analyze... (e.g., 'Tesla stock plummets after earnings miss')"
            className="w-full pl-16 pr-6 py-6 text-lg bg-navy-900/50 text-white placeholder-navy-500 border-2 border-navy-700 rounded-2xl focus:border-accent-500 focus:outline-none focus:ring-4 focus:ring-accent-500/20 transition-all resize-none h-32"
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
            disabled={loading || !headline.trim()}
            className="mt-4 w-full btn-primary py-4 text-lg font-bold flex items-center justify-center space-x-3 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? (
              <>
                <div className="w-6 h-6 border-3 border-white border-t-transparent rounded-full animate-spin"></div>
                <span>Analyzing with AI...</span>
              </>
            ) : (
              <>
                <Zap className="w-6 h-6" />
                <span>ANALYZE HEADLINE</span>
                <TrendingUp className="w-6 h-6" />
              </>
            )}
          </motion.button>
        </div>

        {/* Example Headlines */}
        <div className="mt-6">
          <p className="text-sm text-navy-500 mb-3 font-medium">Try these examples:</p>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {examples.map((ex, i) => (
              <motion.button
                key={i}
                whileHover={{ scale: 1.02, x: 5 }}
                onClick={() => setHeadline(ex)}
                className="text-left px-4 py-3 bg-navy-800/50 hover:bg-navy-700/50 text-sm text-navy-300 hover:text-white rounded-xl border border-navy-700/50 hover:border-accent-500/50 transition-all"
              >
                <Sparkles className="w-4 h-4 inline mr-2 text-accent-400" />
                {ex}
              </motion.button>
            ))}
          </div>
        </div>
      </motion.div>

      {/* Features */}
      <motion.div 
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.6, delay: 0.4 }}
        className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-12"
      >
        {[
          { icon: Shield, title: 'Fake News Detection', desc: '5 ML Models' },
          { icon: TrendingUp, title: 'Market Impact', desc: 'Real-time Data' },
          { icon: Brain, title: 'AI Reasoning', desc: 'LLM Explanations' }
        ].map((feature, i) => (
          <motion.div
            key={i}
            whileHover={{ y: -5 }}
            className="glass-card p-6 text-center"
          >
            <feature.icon className="w-10 h-10 text-accent-400 mx-auto mb-3" />
            <h3 className="text-lg font-bold text-white mb-1">{feature.title}</h3>
            <p className="text-sm text-navy-400">{feature.desc}</p>
          </motion.div>
        ))}
      </motion.div>
    </div>
  );
};

export default HeroInput;

