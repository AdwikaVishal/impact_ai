import { AlertTriangle, ShieldCheck, Activity, Target } from 'lucide-react';
import { motion } from 'framer-motion';
import { useAnalysisStore } from '../stores/useAnalysisStore';
import { getRiskColor } from '../utils/riskColors';

const Metric = ({ label, value }) => (
  <div className="text-center">
    <p className="text-xs text-navy-500 mb-1 font-medium">{label}</p>
    <p className="text-lg font-bold text-white">{value}</p>
  </div>
);

export default function RiskBanner() {
  const { analysis, isAnalyzing } = useAnalysisStore();

  if (isAnalyzing) {
    return (
      <div className="glass-card p-8 animate-pulse">
        <div className="h-40 bg-navy-700/30 rounded-2xl"></div>
      </div>
    );
  }

  if (!analysis) return null;

  const riskLevel = analysis.risk_score || 'MEDIUM';
  const riskScore = analysis.risk_score_raw || 0.5;
  const aiSignal = analysis.trading_signal || 'NEUTRAL';
  const colors = getRiskColor(riskLevel);

  const getRiskIcon = () => {
    if (riskLevel === 'HIGH') return AlertTriangle;
    if (riskLevel === 'LOW') return ShieldCheck;
    return Activity;
  };

  const RiskIcon = getRiskIcon();

  return (
    <motion.div
      initial={{ scale: 0.95, opacity: 0 }}
      animate={{ scale: 1, opacity: 1 }}
      transition={{ duration: 0.5 }}
      className="relative overflow-hidden rounded-3xl"
    >
      {/* Animated Background */}
      <div className={`absolute inset-0 bg-gradient-to-br ${colors.gradient} opacity-10 animate-pulse-slow`}></div>
      <div className="absolute inset-0 bg-gradient-to-r from-navy-900/90 via-navy-800/80 to-navy-900/90 backdrop-blur-xl"></div>
      
      {/* Content */}
      <div className="relative z-10 p-8 border-2 border-navy-700/50 rounded-3xl">
        <div className="flex flex-col lg:flex-row items-start lg:items-center justify-between gap-6 mb-6">
          {/* Left: Risk Level */}
          <div className="flex items-center space-x-4">
            <motion.div 
              animate={{ rotate: [0, 5, -5, 0] }}
              transition={{ duration: 3, repeat: Infinity }}
              className={`p-4 rounded-2xl ${colors.bg} shadow-glow-blue`}
            >
              <RiskIcon className="w-12 h-12 text-white" />
            </motion.div>
            <div>
              <h2 className="text-4xl lg:text-5xl font-bold text-white mb-1">
                {riskLevel} RISK
              </h2>
              <div className="flex items-center space-x-3">
                <p className="text-2xl font-mono font-bold text-accent-400">
                  {(riskScore * 100).toFixed(1)}%
                </p>
                <div className="h-2 w-32 bg-navy-700 rounded-full overflow-hidden">
                  <motion.div 
                    initial={{ width: 0 }}
                    animate={{ width: `${riskScore * 100}%` }}
                    transition={{ duration: 1, ease: "easeOut" }}
                    className={`h-full ${colors.bg}`}
                  ></motion.div>
                </div>
              </div>
            </div>
          </div>
          
          {/* Right: Trading Signal */}
          <motion.div 
            whileHover={{ scale: 1.05 }}
            className={`px-8 py-4 rounded-2xl ${colors.signalBg} border-2 ${colors.border} backdrop-blur-xl`}
          >
            <div className="flex items-center space-x-3">
              <Target className="w-6 h-6 text-white" />
              <div>
                <p className="text-xs text-navy-400 font-medium">AI Signal</p>
                <p className="font-bold text-2xl text-white">{aiSignal}</p>
              </div>
            </div>
          </motion.div>
        </div>
        
        {/* Bottom Metrics - UNIQUE DATA ONLY */}
        <div className="grid grid-cols-3 gap-6 pt-6 border-t border-navy-700/50">
          <Metric 
            label="Confidence Score" 
            value={`${((analysis.analysis?.sentiment?.confidence || 0) * 100).toFixed(0)}%`} 
          />
          <Metric 
            label="Entities Detected" 
            value={analysis.analysis?.entities_detected || 0} 
          />
          <Metric 
            label="Market Impact" 
            value={analysis.analysis?.market_impact?.estimated_impact || 'N/A'} 
          />
        </div>
      </div>
    </motion.div>
  );
}
