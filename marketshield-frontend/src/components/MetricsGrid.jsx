import { motion } from 'framer-motion';
import { 
  Building, Hash, DollarSign, TrendingUp, Activity, BarChart3,
  Brain, Shield, AlertCircle, Zap, Target, TrendingDown
} from 'lucide-react';
import { useAnalysisStore } from '../stores/useAnalysisStore';
import { formatPrice, formatPercent, formatVolume } from '../utils/formatters';

const SectionCard = ({ title, icon: Icon, children, gradient }) => (
  <motion.div 
    initial={{ opacity: 0, y: 20 }}
    animate={{ opacity: 1, y: 0 }}
    className={`bg-gradient-to-br ${gradient} backdrop-blur-xl border border-navy-700/40 rounded-2xl p-6 hover:border-accent-500/50 transition-all`}
  >
    <div className="flex items-center space-x-3 mb-6">
      <div className="p-3 rounded-xl bg-white/10">
        <Icon className="w-6 h-6 text-white" />
      </div>
      <h3 className="text-xl font-bold text-white">{title}</h3>
    </div>
    {children}
  </motion.div>
);

const MetricRow = ({ label, value, trend }) => (
  <div className="flex items-center justify-between py-3 border-b border-navy-700/30 last:border-0">
    <span className="text-sm text-navy-400">{label}</span>
    <div className="flex items-center space-x-2">
      <span className="text-lg font-bold text-white">{value}</span>
      {trend !== undefined && (
        trend >= 0 ? 
          <TrendingUp className="w-4 h-4 text-success" /> : 
          <TrendingDown className="w-4 h-4 text-danger" />
      )}
    </div>
  </div>
);

export default function MetricsGrid() {
  const { analysis } = useAnalysisStore();
  
  if (!analysis) return null;

  // Extract data from new API structure
  const entities = analysis.entities?.companies || [];
  const firstEntity = entities[0] || {};
  const marketData = analysis.market_data || {};
  const firstMarket = Object.values(marketData)[0] || {};
  const analysisData = analysis.analysis || {};
  
  return (
    <div>
      <div className="mb-8">
        <h3 className="text-3xl font-bold gradient-text mb-2">Analysis Results</h3>
        <p className="text-navy-500">Comprehensive breakdown of all detected signals</p>
      </div>
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* ENTITY & MARKET DATA */}
        <SectionCard 
          title="Entity & Market Data" 
          icon={Building}
          gradient="from-navy-900/80 to-navy-800/80"
        >
          <MetricRow label="Company" value={firstEntity.name || 'N/A'} />
          <MetricRow label="Ticker Symbol" value={firstEntity.ticker || 'N/A'} />
          <MetricRow label="Confidence" value={`${((firstEntity.confidence || 0) * 100).toFixed(0)}%`} />
          <MetricRow label="Current Price" value={formatPrice(firstMarket.price)} trend={firstMarket.change} />
          <MetricRow label="Price Change" value={formatPercent(firstMarket.change)} trend={firstMarket.change} />
          <MetricRow label="Volume" value={formatVolume(firstMarket.volume)} />
          <MetricRow 
            label="Market Cap" 
            value={firstMarket.market_cap ? `$${(firstMarket.market_cap / 1e9).toFixed(2)}B` : 'N/A'} 
          />
        </SectionCard>

        {/* SENTIMENT & FAKE NEWS */}
        <SectionCard 
          title="Sentiment & Credibility" 
          icon={Brain}
          gradient="from-purple-900/40 to-pink-900/40"
        >
          <MetricRow 
            label="Sentiment" 
            value={analysisData.sentiment?.label || 'N/A'} 
          />
          <MetricRow 
            label="Sentiment Score" 
            value={`${((analysisData.sentiment?.score || 0) * 100).toFixed(0)}%`}
            trend={analysisData.sentiment?.score}
          />
          <MetricRow 
            label="Sentiment Confidence" 
            value={`${((analysisData.sentiment?.confidence || 0) * 100).toFixed(0)}%`} 
          />
          <MetricRow 
            label="Fake News Detection" 
            value={analysisData.fake_news_detection?.label || 'N/A'} 
          />
          <MetricRow 
            label="Fake Probability" 
            value={`${((analysisData.fake_news_detection?.fake_probability || 0) * 100).toFixed(1)}%`} 
          />
          <MetricRow 
            label="Real Probability" 
            value={`${((analysisData.fake_news_detection?.real_probability || 0) * 100).toFixed(1)}%`} 
          />
          <MetricRow 
            label="Credibility Score" 
            value={`${((analysisData.fake_news_detection?.confidence || 0) * 100).toFixed(0)}%`} 
          />
        </SectionCard>

        {/* EVENT & IMPACT */}
        <SectionCard 
          title="Event Detection" 
          icon={Zap}
          gradient="from-blue-900/40 to-cyan-900/40"
        >
          <MetricRow 
            label="Event Type" 
            value={analysisData.event?.type?.toUpperCase().replace('_', ' ') || 'N/A'} 
          />
          <MetricRow 
            label="Event Confidence" 
            value={`${((analysisData.event?.confidence || 0) * 100).toFixed(0)}%`} 
          />
          <MetricRow 
            label="Market Impact" 
            value={analysisData.market_impact?.estimated_impact || 'N/A'} 
          />
          <MetricRow 
            label="Affected Companies" 
            value={analysisData.market_impact?.affected_companies || 0} 
          />
          <MetricRow 
            label="Entities Detected" 
            value={analysisData.entities_detected || 0} 
          />
        </SectionCard>

        {/* RISK & TRADING */}
        <SectionCard 
          title="Risk & Trading Signal" 
          icon={Target}
          gradient="from-orange-900/40 to-red-900/40"
        >
          <MetricRow 
            label="Risk Level" 
            value={analysis.risk_score || 'N/A'} 
          />
          <MetricRow 
            label="Risk Score" 
            value={`${((analysis.risk_score_raw || 0) * 100).toFixed(1)}%`} 
          />
          <MetricRow 
            label="Trading Signal" 
            value={analysis.trading_signal || 'N/A'} 
          />
          <MetricRow 
            label="Analysis ID" 
            value={`#${analysis.analysis_id || 'N/A'}`} 
          />
          <MetricRow 
            label="Timestamp" 
            value={new Date(analysis.created_at).toLocaleTimeString()} 
          />
        </SectionCard>
      </div>
    </div>
  );
}
