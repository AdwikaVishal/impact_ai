import { motion } from 'framer-motion';
import { Building2, Brain, Zap, Target, TrendingUp, TrendingDown } from 'lucide-react';
import { useAnalysisStore } from '../stores/useAnalysisStore';
import { formatVolume } from '../utils/formatters';

const Row = ({ label, value, sub }) => (
  <div className="flex items-center justify-between py-2.5 border-b border-white/5 last:border-0">
    <span className="text-xs text-navy-500">{label}</span>
    <div className="text-right">
      <span className="text-sm font-semibold text-white">{value}</span>
      {sub && <p className="text-xs text-navy-500">{sub}</p>}
    </div>
  </div>
);

const Card = ({ title, icon: Icon, iconColor, children, delay = 0 }) => (
  <motion.div
    initial={{ opacity: 0, y: 12 }}
    animate={{ opacity: 1, y: 0 }}
    transition={{ delay, duration: 0.35 }}
    className="bg-navy-900/50 border border-white/5 rounded-2xl overflow-hidden"
  >
    <div className="flex items-center gap-3 px-5 py-3.5 border-b border-white/5">
      <div className={`w-7 h-7 rounded-lg flex items-center justify-center bg-navy-800/80`}>
        <Icon className={`w-4 h-4 ${iconColor}`} />
      </div>
      <span className="text-sm font-semibold text-white">{title}</span>
    </div>
    <div className="px-5 py-1">{children}</div>
  </motion.div>
);

const ScoreBar = ({ value, color }) => (
  <div className="mt-1 h-1 w-full bg-navy-700/50 rounded-full overflow-hidden">
    <motion.div
      initial={{ width: 0 }}
      animate={{ width: `${Math.min(Math.abs(value) * 100, 100)}%` }  }
      transition={{ duration: 0.6, ease: 'easeOut' }}
      className={`h-full rounded-full ${color}`}
    />
  </div>
);

export default function MetricsGrid() {
  const { analysis } = useAnalysisStore();
  if (!analysis) return null;

  const entities = analysis.entities?.companies || [];
  const first = entities[0] || {};
  const mkt = Object.values(analysis.market_data || {})[0] || {};
  const a = analysis.analysis || {};
  const sent = a.sentiment || {};
  const fake = a.fake_news_detection || {};
  const event = a.event || {};

  return (
    <div>
      <p className="section-label mb-4">Detailed Analysis</p>
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-4">

        {/* ENTITY & MARKET */}
        <Card title="Entity & Market" icon={Building2} iconColor="text-accent-400" delay={0}>
          <Row label="Company" value={first.name || '—'} />
          <Row label="Ticker" value={first.ticker || '—'} />
          <Row label="Confidence" value={`${Math.round((first.confidence || 0) * 100)}%`} />
          <Row label="Price" value={mkt.price ? `$${mkt.price.toFixed(2)}` : '—'} />
          <Row label="Change" value={mkt.change != null ? `${mkt.change >= 0 ? '+' : ''}${mkt.change.toFixed(2)}%` : '—'} />
          <Row label="Volume" value={formatVolume(mkt.volume)} />
        </Card>

        {/* SENTIMENT */}
        <Card title="Sentiment" icon={Brain} iconColor="text-purple-400" delay={0.06}>
          <Row label="Label" value={sent.label || '—'} />
          <Row label="Score" value={`${Math.round((sent.score || 0) * 100)}%`} />
          <div className="py-2">
            <ScoreBar value={sent.score || 0} color={sent.score >= 0 ? 'bg-success' : 'bg-danger'} />
          </div>
          <Row label="Confidence" value={`${Math.round((sent.confidence || 0) * 100)}%`} />
          <Row label="Fake Label" value={fake.label || '—'} />
          <Row label="Fake Prob." value={`${Math.round((fake.fake_probability || 0) * 100)}%`} />
        </Card>

        {/* EVENT */}
        <Card title="Event Detection" icon={Zap} iconColor="text-warning" delay={0.12}>
          <Row label="Event Type" value={(event.type || 'general').replace(/_/g, ' ').toUpperCase()} />
          <Row label="Confidence" value={`${Math.round((event.confidence || 0) * 100)}%`} />
          <Row label="Impact" value={a.market_impact?.estimated_impact || '—'} />
          <Row label="Affected" value={`${a.market_impact?.affected_companies || 0} companies`} />
          <Row label="Entities" value={`${a.entities_detected || 0} detected`} />
        </Card>

        {/* RISK & SIGNAL */}
        <Card title="Risk & Signal" icon={Target} iconColor="text-danger" delay={0.18}>
          <Row label="Risk Level" value={analysis.risk_score || '—'} />
          <Row label="Risk Score" value={`${Math.round((analysis.risk_score_raw || 0) * 100)}%`} />
          <div className="py-2">
            <ScoreBar value={analysis.risk_score_raw || 0} color={
              analysis.risk_score === 'HIGH' ? 'bg-danger' :
              analysis.risk_score === 'MEDIUM' ? 'bg-warning' : 'bg-success'
            } />
          </div>
          <Row label="Signal" value={analysis.trading_signal || '—'} />
          <Row label="Analysis ID" value={`#${analysis.analysis_id || '—'}`} />
          <Row label="Time" value={new Date(analysis.created_at).toLocaleTimeString()} />
        </Card>

      </div>
    </div>
  );
}
