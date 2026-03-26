import { AlertTriangle, ShieldCheck, Activity, Target, TrendingUp, TrendingDown } from 'lucide-react';
import { motion } from 'framer-motion';
import { useAnalysisStore } from '../stores/useAnalysisStore';

const RISK_CONFIG = {
  HIGH:   { icon: AlertTriangle, color: 'text-danger',  bg: 'bg-danger/10',  border: 'border-danger/25',  bar: 'bg-danger' },
  MEDIUM: { icon: Activity,      color: 'text-warning', bg: 'bg-warning/10', border: 'border-warning/25', bar: 'bg-warning' },
  LOW:    { icon: ShieldCheck,   color: 'text-success', bg: 'bg-success/10', border: 'border-success/25', bar: 'bg-success' },
};

const SIGNAL_COLOR = {
  BUY:          'text-success bg-success/10 border-success/25',
  SELL:         'text-danger bg-danger/10 border-danger/25',
  HOLD_BULLISH: 'text-warning bg-warning/10 border-warning/25',
  HOLD_BEARISH: 'text-warning bg-warning/10 border-warning/25',
  NEUTRAL:      'text-navy-400 bg-navy-700/30 border-navy-700/40',
};

export default function RiskBanner() {
  const { analysis, isAnalyzing } = useAnalysisStore();

  if (isAnalyzing) {
    return (
      <div className="bg-navy-900/50 border border-white/5 rounded-2xl p-6">
        <div className="space-y-3">
          <div className="skeleton h-8 w-48 rounded-lg" />
          <div className="skeleton h-4 w-full rounded" />
          <div className="skeleton h-4 w-3/4 rounded" />
        </div>
      </div>
    );
  }
  if (!analysis) return null;

  const level = analysis.risk_score || 'MEDIUM';
  const raw = analysis.risk_score_raw || 0.5;
  const signal = analysis.trading_signal || 'NEUTRAL';
  const cfg = RISK_CONFIG[level] || RISK_CONFIG.MEDIUM;
  const Icon = cfg.icon;
  const pct = Math.round(raw * 100);

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.98 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.35 }}
      className={`${cfg.bg} border ${cfg.border} rounded-2xl p-5`}
    >
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        {/* LEFT: risk level */}
        <div className="flex items-center gap-4">
          <div className={`w-12 h-12 rounded-xl flex items-center justify-center flex-shrink-0 ${cfg.bg} border ${cfg.border}`}>
            <Icon className={`w-6 h-6 ${cfg.color}`} />
          </div>
          <div>
            <p className="section-label mb-1">Risk Assessment</p>
            <div className="flex items-center gap-3">
              <span className={`text-2xl font-bold ${cfg.color}`}>{level} RISK</span>
              <span className="text-sm font-mono text-white">{pct}%</span>
            </div>
            {/* Progress bar */}
            <div className="mt-2 h-1.5 w-48 bg-navy-700/50 rounded-full overflow-hidden">
              <motion.div
                initial={{ width: 0 }}
                animate={{ width: `${pct}%` }}
                transition={{ duration: 0.8, ease: 'easeOut' }}
                className={`h-full ${cfg.bar} rounded-full`}
              />
            </div>
          </div>
        </div>

        {/* RIGHT: signal + metrics */}
        <div className="flex flex-wrap items-center gap-3">
          {/* Trading signal */}
          <div className={`flex items-center gap-2 px-4 py-2.5 rounded-xl border text-sm font-bold ${SIGNAL_COLOR[signal] || SIGNAL_COLOR.NEUTRAL}`}>
            <Target className="w-4 h-4" />
            {signal.replace('_', ' ')}
          </div>

          {/* Quick stats */}
          <div className="flex items-center gap-3 text-xs">
            <div className="text-center px-3 py-2 bg-navy-800/50 rounded-xl border border-white/5">
              <p className="stat-label">Confidence</p>
              <p className="font-bold text-white mt-0.5">
                {Math.round((analysis.analysis?.sentiment?.confidence || 0) * 100)}%
              </p>
            </div>
            <div className="text-center px-3 py-2 bg-navy-800/50 rounded-xl border border-white/5">
              <p className="stat-label">Entities</p>
              <p className="font-bold text-white mt-0.5">{analysis.analysis?.entities_detected || 0}</p>
            </div>
            <div className="text-center px-3 py-2 bg-navy-800/50 rounded-xl border border-white/5">
              <p className="stat-label">Impact</p>
              <p className="font-bold text-white mt-0.5">{analysis.analysis?.market_impact?.estimated_impact || 'N/A'}</p>
            </div>
          </div>
        </div>
      </div>
    </motion.div>
  );
}
