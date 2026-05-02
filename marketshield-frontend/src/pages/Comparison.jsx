import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Search, 
  TrendingUp, 
  TrendingDown, 
  Building2, 
  Users, 
  DollarSign, 
  BarChart3,
  Shield,
  Target,
  Zap,
  Globe,
  Award,
  AlertTriangle,
  Loader2,
  ArrowRight,
  ExternalLink
} from 'lucide-react';
import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

const StatCard = ({ icon: Icon, label, value, color = 'text-white' }) => (
  <div className="flex items-center gap-3 p-3 bg-navy-800/50 rounded-xl border border-white/5">
    <Icon className={`w-5 h-5 ${color} flex-shrink-0`} />
    <div>
      <p className="text-xs text-navy-500">{label}</p>
      <p className={`text-sm font-bold ${color}`}>{value}</p>
    </div>
  </div>
);

const CompetitorCard = ({ competitor, index }) => {
  const hasMarketData = competitor.market_data;
  const marketCap = hasMarketData ? competitor.market_data.market_cap : 0;
  const price = hasMarketData ? competitor.market_data.price : 0;
  
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.1 }}
      className="bg-navy-900/50 border border-white/5 hover:border-accent-500/20 rounded-2xl p-5 transition-all group"
    >
      {/* Header */}
      <div className="flex items-start justify-between mb-4">
        <div>
          <h3 className="text-lg font-bold text-white mb-1">{competitor.name}</h3>
          <div className="flex items-center gap-2">
            <a 
              href={`https://${competitor.domain}`} 
              target="_blank" 
              rel="noopener noreferrer"
              className="text-xs text-accent-400 hover:text-accent-300 flex items-center gap-1 transition-colors"
            >
              {competitor.domain}
              <ExternalLink className="w-3 h-3" />
            </a>
            {competitor.stock_symbol && (
              <span className="text-xs font-mono bg-accent-500/10 text-accent-400 px-2 py-0.5 rounded-md">
                {competitor.stock_symbol}
              </span>
            )}
          </div>
        </div>
        <div className="flex items-center gap-1.5 px-2.5 py-1 bg-accent-500/10 border border-accent-500/20 rounded-lg">
          <Target className="w-3.5 h-3.5 text-accent-400" />
          <span className="text-xs font-semibold text-accent-400">
            {Math.round(competitor.relevance_score * 100)}% match
          </span>
        </div>
      </div>

      {/* Market Data */}
      {hasMarketData && (
        <div className="grid grid-cols-2 gap-3 mb-4">
          <StatCard 
            icon={DollarSign} 
            label="Stock Price" 
            value={`$${price.toFixed(2)}`}
            color="text-white"
          />
          <StatCard 
            icon={BarChart3} 
            label="Market Cap" 
            value={marketCap > 1e9 ? `$${(marketCap/1e9).toFixed(1)}B` : `$${(marketCap/1e6).toFixed(0)}M`}
            color="text-accent-400"
          />
        </div>
      )}

      {/* Strengths */}
      {competitor.strengths && competitor.strengths.length > 0 && (
        <div className="mb-4">
          <div className="flex items-center gap-2 mb-2">
            <Award className="w-4 h-4 text-success" />
            <span className="text-xs font-semibold text-success">Strengths</span>
          </div>
          <div className="space-y-1">
            {competitor.strengths.slice(0, 3).map((strength, i) => (
              <div key={i} className="flex items-center gap-2">
                <div className="w-1.5 h-1.5 bg-success rounded-full flex-shrink-0" />
                <span className="text-xs text-navy-300">{strength}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Weaknesses */}
      {competitor.weaknesses && competitor.weaknesses.length > 0 && (
        <div>
          <div className="flex items-center gap-2 mb-2">
            <AlertTriangle className="w-4 h-4 text-warning" />
            <span className="text-xs font-semibold text-warning">Challenges</span>
          </div>
          <div className="space-y-1">
            {competitor.weaknesses.slice(0, 2).map((weakness, i) => (
              <div key={i} className="flex items-center gap-2">
                <div className="w-1.5 h-1.5 bg-warning rounded-full flex-shrink-0" />
                <span className="text-xs text-navy-300">{weakness}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </motion.div>
  );
};

const CompanyProfile = ({ company }) => {
  if (!company) return null;

  const profile = company.profile;
  const marketData = company.market_data;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-gradient-to-br from-accent-500/10 to-accent-cyan/5 border border-accent-500/20 rounded-2xl p-6 mb-8"
    >
      <div className="flex items-start justify-between mb-6">
        <div>
          <h2 className="text-2xl font-bold text-white mb-2">{company.name}</h2>
          <div className="flex items-center gap-3">
            <span className="text-sm text-accent-400 bg-accent-500/10 px-3 py-1 rounded-lg">
              {profile.industry}
            </span>
            <span className="text-sm text-navy-400">{profile.size}</span>
            {company.stock_symbol && (
              <span className="text-sm font-mono bg-navy-800/60 text-white px-3 py-1 rounded-lg">
                {company.stock_symbol}
              </span>
            )}
          </div>
        </div>
        {marketData && (
          <div className="text-right">
            <p className="text-2xl font-bold text-white">${marketData.price.toFixed(2)}</p>
            <p className="text-sm text-navy-400">Current Price</p>
          </div>
        )}
      </div>

      <p className="text-navy-300 mb-6 leading-relaxed">{profile.description}</p>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {profile.key_products && profile.key_products.length > 0 && (
          <div>
            <h4 className="text-sm font-semibold text-white mb-2 flex items-center gap-2">
              <Zap className="w-4 h-4 text-accent-400" />
              Key Products
            </h4>
            <div className="space-y-1">
              {profile.key_products.slice(0, 3).map((product, i) => (
                <div key={i} className="text-xs text-navy-300">• {product}</div>
              ))}
            </div>
          </div>
        )}

        {profile.target_market && (
          <div>
            <h4 className="text-sm font-semibold text-white mb-2 flex items-center gap-2">
              <Users className="w-4 h-4 text-accent-400" />
              Target Market
            </h4>
            <p className="text-xs text-navy-300">{profile.target_market}</p>
          </div>
        )}

        {profile.competitive_advantages && profile.competitive_advantages.length > 0 && (
          <div>
            <h4 className="text-sm font-semibold text-white mb-2 flex items-center gap-2">
              <Shield className="w-4 h-4 text-accent-400" />
              Advantages
            </h4>
            <div className="space-y-1">
              {profile.competitive_advantages.slice(0, 3).map((advantage, i) => (
                <div key={i} className="text-xs text-navy-300">• {advantage}</div>
              ))}
            </div>
          </div>
        )}
      </div>
    </motion.div>
  );
};

const MarketPosition = ({ position }) => {
  if (!position) return null;

  const getStrengthColor = (strength) => {
    switch (strength) {
      case 'Strong': return 'text-success';
      case 'Medium': return 'text-warning';
      case 'Emerging': return 'text-info';
      default: return 'text-navy-400';
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-navy-900/50 border border-white/5 rounded-2xl p-5 mb-8"
    >
      <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
        <BarChart3 className="w-5 h-5 text-accent-400" />
        Market Position Analysis
      </h3>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <StatCard 
          icon={Award} 
          label="Market Cap Rank" 
          value={position.market_cap_rank}
          color="text-accent-400"
        />
        <StatCard 
          icon={TrendingUp} 
          label="Relative Size" 
          value={position.relative_size}
          color="text-white"
        />
        <StatCard 
          icon={Shield} 
          label="Competitive Strength" 
          value={position.competitive_strength}
          color={getStrengthColor(position.competitive_strength)}
        />
      </div>
    </motion.div>
  );
};

export default function Comparison() {
  const [searchQuery, setSearchQuery] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [analysisData, setAnalysisData] = useState(null);
  const [error, setError] = useState(null);

  const handleSearch = async () => {
    if (!searchQuery.trim()) return;

    setIsLoading(true);
    setError(null);
    setAnalysisData(null);

    try {
      const response = await axios.get(`${API_BASE}/comparison/analyze/${encodeURIComponent(searchQuery.trim())}`);
      
      if (response.data.success) {
        setAnalysisData(response.data.data);
      } else {
        setError('Failed to analyze company');
      }
    } catch (err) {
      console.error('Error analyzing company:', err);
      setError(err.response?.data?.detail || 'Failed to analyze company');
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      handleSearch();
    }
  };

  return (
    <div className="max-w-[1400px] mx-auto px-4 sm:px-8 lg:px-16 py-8">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        className="mb-8"
      >
        <div className="flex items-center gap-4 mb-4">
          <div className="w-10 h-10 bg-gradient-to-br from-accent-500 to-accent-cyan rounded-xl flex items-center justify-center shadow-glow-blue">
            <Building2 className="w-5 h-5 text-white" />
          </div>
          <div>
            <h1 className="text-xl font-bold text-white">Company Comparison</h1>
            <p className="text-xs text-navy-500 mt-0.5">Analyze companies and discover their competitors</p>
          </div>
        </div>

        {/* Search */}
        <div className="flex gap-3 max-w-2xl">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-navy-500 pointer-events-none" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Enter company name (e.g., Apple, Tesla, Microsoft)..."
              className="w-full pl-9 pr-4 py-3 bg-navy-800/60 text-sm text-white placeholder-navy-500
                         border border-white/8 rounded-xl focus:border-accent-500/50 focus:outline-none
                         focus:ring-2 focus:ring-accent-500/15 transition-all"
            />
          </div>
          <button
            onClick={handleSearch}
            disabled={isLoading || !searchQuery.trim()}
            className="btn-primary flex items-center gap-2 py-3 px-6 text-sm disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isLoading ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <ArrowRight className="w-4 h-4" />
            )}
            Analyze
          </button>
        </div>
      </motion.div>

      {/* Error */}
      <AnimatePresence>
        {error && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="bg-danger/10 border border-danger/20 rounded-xl p-4 mb-6"
          >
            <div className="flex items-center gap-2">
              <AlertTriangle className="w-4 h-4 text-danger" />
              <span className="text-sm text-danger">{error}</span>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Loading */}
      <AnimatePresence>
        {isLoading && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="flex items-center justify-center py-12"
          >
            <div className="flex items-center gap-3">
              <Loader2 className="w-6 h-6 text-accent-400 animate-spin" />
              <span className="text-navy-400">Analyzing company and discovering competitors...</span>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Results */}
      <AnimatePresence>
        {analysisData && !isLoading && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
          >
            {/* Company Profile */}
            <CompanyProfile company={analysisData.company} />

            {/* Market Position */}
            <MarketPosition position={analysisData.market_position} />

            {/* Competitors */}
            <div>
              <h3 className="text-lg font-bold text-white mb-6 flex items-center gap-2">
                <Globe className="w-5 h-5 text-accent-400" />
                Competitors ({analysisData.competitors.length})
              </h3>
              
              {analysisData.competitors.length > 0 ? (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {analysisData.competitors.map((competitor, index) => (
                    <CompetitorCard 
                      key={competitor.name} 
                      competitor={competitor} 
                      index={index} 
                    />
                  ))}
                </div>
              ) : (
                <div className="text-center py-12">
                  <Globe className="w-12 h-12 text-navy-600 mx-auto mb-4" />
                  <p className="text-navy-400">No competitors found for this company.</p>
                </div>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Empty State */}
      {!analysisData && !isLoading && !error && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center py-16"
        >
          <Building2 className="w-16 h-16 text-navy-600 mx-auto mb-6" />
          <h3 className="text-xl font-bold text-white mb-2">Discover Company Competitors</h3>
          <p className="text-navy-400 mb-8 max-w-md mx-auto">
            Enter any company name to get detailed analysis including competitors, market position, and key insights.
          </p>
          
          <div className="flex flex-wrap justify-center gap-2">
            {['Apple', 'Tesla', 'Microsoft', 'Google', 'Amazon'].map((company) => (
              <button
                key={company}
                onClick={() => {
                  setSearchQuery(company);
                  setTimeout(handleSearch, 100);
                }}
                className="px-4 py-2 bg-navy-800/60 hover:bg-navy-800 text-sm text-navy-300 hover:text-white
                           border border-white/5 hover:border-accent-500/20 rounded-lg transition-all"
              >
                Try {company}
              </button>
            ))}
          </div>
        </motion.div>
      )}
    </div>
  );
}