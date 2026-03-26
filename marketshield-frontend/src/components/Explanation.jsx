import { Brain, AlertTriangle, Sparkles, CheckCircle2, XCircle } from 'lucide-react';
import { motion } from 'framer-motion';
import { useAnalysisStore } from '../stores/useAnalysisStore';

const EVENT_LABELS = {
  earnings: 'Earnings-related news',
  merger: 'Merger & acquisition activity',
  product_launch: 'Product launch announcement',
  lawsuit: 'Legal proceedings detected',
  layoff: 'Workforce restructuring',
  expansion: 'Business expansion news',
  general_news: 'General market news',
};

export default function Explanation() {
  const { analysis } = useAnalysisStore();
  if (!analysis) return null;

  const entities = analysis.entities?.companies || [];
  const mkt = analysis.market_data || {};
  const a = analysis.analysis || {};
  const fakePct = Math.round((a.fake_news_detection?.fake_probability || 0) * 100);
  const mktChange = Math.abs(Object.values(mkt)[0]?.change || 0);
  const isHighFake = fakePct > 50;
  const isHighVol = mktChange > 5;

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
      className="grid grid-cols-1 lg:grid-cols-2 gap-5"
    >
      {/* SUMMARY */}
      <div className="bg-navy-900/50 border border-white/5 rounded-2xl p-5">
        <div className="flex items-center gap-3 mb-4">
          <div className="w-8 h-8 bg-accent-500/15 rounded-xl flex items-center justify-center">
            <Sparkles className="w-4 h-4 text-accent-400" />
          </div>
          <span className="text-sm font-semibold text-white">Analysis Summary</span>
        </div>

        <div className="space-y-3">
          <div className="p-3.5 bg-navy-800/50 rounded-xl border border-white/5">
            <p className="section-label mb-1.5">Overall Assessment</p>
            <p className="text-sm text-white leading-relaxed">
              {a.sentiment?.label === 'POSITIVE'
                ? 'Positive market sentiment detected with '
                : a.sentiment?.label === 'NEGATIVE'
                ? 'Negative market sentiment detected with '
                : 'Neutral market sentiment with '}
              {a.fake_news_detection?.label === 'LIKELY_REAL' ? 'high credibility signals.' : 'credibility concerns flagged.'}
            </p>
          </div>

          <div className="p-3.5 bg-navy-800/50 rounded-xl border border-white/5">
            <p className="section-label mb-1.5">Event Context</p>
            <p className="text-sm text-white">{EVENT_LABELS[a.event?.type] || 'General market news'}</p>
          </div>

          <div className="p-3.5 bg-navy-800/50 rounded-xl border border-white/5">
            <p className="section-label mb-1.5">Recommendation</p>
            <p className="text-base font-bold text-accent-400">{analysis.trading_signal}</p>
          </div>

          {entities.length > 0 && (
            <div className="p-3.5 bg-navy-800/50 rounded-xl border border-white/5">
              <p className="section-label mb-2">Detected Entities</p>
              <div className="flex flex-wrap gap-2">
                {entities.map((e, i) => (
                  <span key={i} className="text-xs font-mono font-semibold text-accent-400 bg-accent-500/10 px-2.5 py-1 rounded-lg border border-accent-500/20">
                    {e.ticker}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* RISK FACTORS */}
      <div className="bg-navy-900/50 border border-white/5 rounded-2xl p-5">
        <div className="flex items-center gap-3 mb-4">
          <div className="w-8 h-8 bg-warning/15 rounded-xl flex items-center justify-center">
            <AlertTriangle className="w-4 h-4 text-warning" />
          </div>
          <span className="text-sm font-semibold text-white">Risk Factors</span>
        </div>

        <div className="space-y-3">
          {/* Misinformation */}
          <div className="flex items-center justify-between p-3.5 bg-navy-800/50 rounded-xl border border-white/5">
            <div className="flex items-center gap-2.5">
              {isHighFake
                ? <XCircle className="w-4 h-4 text-danger flex-shrink-0" />
                : <CheckCircle2 className="w-4 h-4 text-success flex-shrink-0" />}
              <div>
                <p className="text-sm text-white font-medium">Misinformation Risk</p>
                <p className="text-xs text-navy-500">{fakePct}% fake probability</p>
              </div>
            </div>
            <span className={`tag border font-semibold ${
              isHighFake ? 'bg-danger/10 text-danger border-danger/25' : 'bg-success/10 text-success border-success/25'
            }`}>
              {isHighFake ? 'HIGH' : fakePct > 30 ? 'MEDIUM' : 'LOW'}
            </span>
          </div>

          {/* Market Volatility */}
          <div className="flex items-center justify-between p-3.5 bg-navy-800/50 rounded-xl border border-white/5">
            <div className="flex items-center gap-2.5">
              {isHighVol
                ? <XCircle className="w-4 h-4 text-danger flex-shrink-0" />
                : <CheckCircle2 className="w-4 h-4 text-success flex-shrink-0" />}
              <div>
                <p className="text-sm text-white font-medium">Market Volatility</p>
                <p className="text-xs text-navy-500">{mktChange.toFixed(2)}% price movement</p>
              </div>
            </div>
            <span className={`tag border font-semibold ${
              isHighVol ? 'bg-danger/10 text-danger border-danger/25' :
              mktChange > 2 ? 'bg-warning/10 text-warning border-warning/25' :
              'bg-success/10 text-success border-success/25'
            }`}>
              {isHighVol ? 'HIGH' : mktChange > 2 ? 'MEDIUM' : 'LOW'}
            </span>
          </div>

          {/* Overall */}
          <div className="flex items-center justify-between p-3.5 bg-navy-800/50 rounded-xl border border-white/5">
            <div className="flex items-center gap-2.5">
              <Brain className="w-4 h-4 text-accent-400 flex-shrink-0" />
              <div>
                <p className="text-sm text-white font-medium">Overall Risk Level</p>
                <p className="text-xs text-navy-500">Combined ML assessment</p>
              </div>
            </div>
            <span className={`tag border font-bold text-sm ${
              analysis.risk_score === 'HIGH' ? 'bg-danger/10 text-danger border-danger/25' :
              analysis.risk_score === 'MEDIUM' ? 'bg-warning/10 text-warning border-warning/25' :
              'bg-success/10 text-success border-success/25'
            }`}>
              {analysis.risk_score}
            </span>
          </div>

          {/* Advisory */}
          <div className={`p-3.5 rounded-xl border text-xs leading-relaxed ${
            analysis.risk_score === 'HIGH'
              ? 'bg-danger/5 border-danger/15 text-danger/80'
              : analysis.risk_score === 'MEDIUM'
              ? 'bg-warning/5 border-warning/15 text-warning/80'
              : 'bg-success/5 border-success/15 text-success/80'
          }`}>
            {analysis.risk_score === 'HIGH'
              ? 'Exercise caution. High risk detected. Verify from multiple sources before acting.'
              : analysis.risk_score === 'MEDIUM'
              ? 'Moderate risk. Consider additional research before making decisions.'
              : 'Low risk detected. Information appears credible with positive indicators.'}
          </div>
        </div>
      </div>
    </motion.div>
  );
}
