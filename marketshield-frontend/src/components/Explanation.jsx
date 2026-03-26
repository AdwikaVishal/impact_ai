import { Brain, AlertTriangle, Sparkles, BarChart2 } from 'lucide-react';
import { motion } from 'framer-motion';
import { useAnalysisStore } from '../stores/useAnalysisStore';
import { useEffect, useState } from 'react';

export default function Explanation() {
  const { analysis } = useAnalysisStore();
  const [chartData, setChartData] = useState(null);
  
  useEffect(() => {
    if (analysis) {
      const entities = analysis.entities?.companies || [];
      const firstEntity = entities[0];
      
      if (firstEntity?.ticker) {
        // Fetch historical data for chart
        fetch(`http://localhost:8000/api/v1/market/${firstEntity.ticker}`)
          .then(res => res.json())
          .then(data => {
            if (data.historical_data) {
              setChartData(data.historical_data);
            }
          })
          .catch(err => console.error('Failed to fetch chart data:', err));
      }
    }
  }, [analysis]);
  
  if (!analysis) return null;

  const entities = analysis.entities?.companies || [];
  const marketData = analysis.market_data || {};
  const analysisData = analysis.analysis || {};

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="space-y-6"
    >
      {/* CHART SECTION */}
      {chartData && chartData.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="glass-card p-8"
        >
          <div className="flex items-center space-x-4 mb-6">
            <div className="p-3 bg-accent-500/20 rounded-xl">
              <BarChart2 className="w-6 h-6 text-accent-400" />
            </div>
            <div>
              <h3 className="text-2xl font-bold gradient-text">7-Day Price History</h3>
              <p className="text-navy-500">{entities[0]?.name} ({entities[0]?.ticker})</p>
            </div>
          </div>
          
          {/* Simple SVG Chart */}
          <div className="bg-navy-900/50 rounded-2xl p-6 border border-navy-700/30">
            <svg viewBox="0 0 800 300" className="w-full h-64">
              {/* Grid lines */}
              {[0, 1, 2, 3, 4].map(i => (
                <line 
                  key={i}
                  x1="0" 
                  y1={i * 60 + 30} 
                  x2="800" 
                  y2={i * 60 + 30} 
                  stroke="#1e3a5f" 
                  strokeWidth="1"
                  strokeDasharray="5,5"
                />
              ))}
              
              {/* Price line */}
              <polyline
                points={chartData.map((point, i) => {
                  const x = (i / (chartData.length - 1)) * 780 + 10;
                  const prices = chartData.map(p => p.close);
                  const minPrice = Math.min(...prices);
                  const maxPrice = Math.max(...prices);
                  const priceRange = maxPrice - minPrice || 1;
                  const y = 270 - ((point.close - minPrice) / priceRange) * 240;
                  return `${x},${y}`;
                }).join(' ')}
                fill="none"
                stroke="url(#gradient)"
                strokeWidth="3"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
              
              {/* Gradient definition */}
              <defs>
                <linearGradient id="gradient" x1="0%" y1="0%" x2="100%" y2="0%">
                  <stop offset="0%" stopColor="#3b82f6" />
                  <stop offset="50%" stopColor="#06b6d4" />
                  <stop offset="100%" stopColor="#10b981" />
                </linearGradient>
              </defs>
              
              {/* Data points */}
              {chartData.map((point, i) => {
                const x = (i / (chartData.length - 1)) * 780 + 10;
                const prices = chartData.map(p => p.close);
                const minPrice = Math.min(...prices);
                const maxPrice = Math.max(...prices);
                const priceRange = maxPrice - minPrice || 1;
                const y = 270 - ((point.close - minPrice) / priceRange) * 240;
                return (
                  <circle
                    key={i}
                    cx={x}
                    cy={y}
                    r="4"
                    fill="#06b6d4"
                    className="hover:r-6 transition-all cursor-pointer"
                  >
                    <title>{`${point.date}: $${point.close.toFixed(2)}`}</title>
                  </circle>
                );
              })}
            </svg>
            
            {/* Chart legend */}
            <div className="flex justify-between mt-4 text-xs text-navy-400">
              <span>{chartData[0]?.date}</span>
              <span>Historical Price Movement</span>
              <span>{chartData[chartData.length - 1]?.date}</span>
            </div>
          </div>
        </motion.div>
      )}

      {/* AI INSIGHTS - NO DUPLICATE DATA */}
      <div className="glass-card p-8">
        <div className="flex items-center space-x-4 mb-6">
          <motion.div 
            animate={{ rotate: [0, 360] }}
            transition={{ duration: 20, repeat: Infinity, ease: "linear" }}
            className="p-4 bg-gradient-to-br from-purple-500 via-pink-500 to-accent-500 rounded-2xl shadow-glow-blue"
          >
            <Brain className="w-8 h-8 text-white" />
          </motion.div>
          <div>
            <h3 className="text-2xl font-bold gradient-text">AI Insights</h3>
            <p className="text-navy-500">Key findings and recommendations</p>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Analysis Summary */}
          <motion.div 
            initial={{ x: -20, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            transition={{ delay: 0.2 }}
            className="bg-gradient-to-r from-accent-500/10 to-accent-cyan/10 border border-accent-500/30 rounded-2xl p-6"
          >
            <div className="flex items-start space-x-4">
              <div className="p-3 bg-accent-500/20 rounded-xl">
                <Sparkles className="w-6 h-6 text-accent-400" />
              </div>
              <div className="flex-1">
                <p className="text-sm font-semibold text-accent-400 mb-3 uppercase tracking-wider">Analysis Summary</p>
                <div className="space-y-3">
                  <div>
                    <p className="text-xs text-navy-400 mb-1">Overall Assessment</p>
                    <p className="text-white font-medium">
                      {analysisData.sentiment?.label === 'POSITIVE' ? 
                        'Positive market sentiment detected with ' : 
                        analysisData.sentiment?.label === 'NEGATIVE' ? 
                        'Negative market sentiment detected with ' : 
                        'Neutral market sentiment with '}
                      {analysisData.fake_news_detection?.label === 'LIKELY_REAL' ? 
                        'high credibility' : 
                        'credibility concerns'}
                    </p>
                  </div>
                  <div>
                    <p className="text-xs text-navy-400 mb-1">Event Context</p>
                    <p className="text-white font-medium">
                      {analysisData.event?.type === 'earnings' ? 'Earnings-related news' :
                       analysisData.event?.type === 'merger' ? 'Merger & acquisition activity' :
                       analysisData.event?.type === 'product_launch' ? 'Product launch announcement' :
                       analysisData.event?.type === 'lawsuit' ? 'Legal proceedings' :
                       analysisData.event?.type === 'layoff' ? 'Workforce restructuring' :
                       analysisData.event?.type === 'expansion' ? 'Business expansion' :
                       'General market news'}
                    </p>
                  </div>
                  <div>
                    <p className="text-xs text-navy-400 mb-1">Recommendation</p>
                    <p className="text-white font-bold text-lg">
                      {analysis.trading_signal}
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </motion.div>

          {/* Risk Factors */}
          <motion.div 
            initial={{ x: -20, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            transition={{ delay: 0.3 }}
            className="bg-gradient-to-r from-warning/10 to-danger/10 border-2 border-warning/30 rounded-2xl p-6"
          >
            <div className="flex items-start space-x-4">
              <motion.div 
                animate={{ scale: [1, 1.1, 1] }}
                transition={{ duration: 2, repeat: Infinity }}
                className="p-3 bg-warning/20 rounded-xl"
              >
                <AlertTriangle className="w-6 h-6 text-warning" />
              </motion.div>
              <div className="flex-1">
                <p className="text-sm font-semibold text-warning mb-3 uppercase tracking-wider">Risk Factors</p>
                <div className="space-y-3">
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-navy-400">Misinformation Risk:</span>
                    <span className={`text-sm font-bold ${
                      (analysisData.fake_news_detection?.fake_probability || 0) > 0.5 ? 'text-danger' : 
                      (analysisData.fake_news_detection?.fake_probability || 0) > 0.3 ? 'text-warning' : 
                      'text-success'
                    }`}>
                      {(analysisData.fake_news_detection?.fake_probability || 0) > 0.5 ? 'HIGH' :
                       (analysisData.fake_news_detection?.fake_probability || 0) > 0.3 ? 'MEDIUM' :
                       'LOW'}
                    </span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-navy-400">Market Volatility:</span>
                    <span className={`text-sm font-bold ${
                      Math.abs(Object.values(marketData)[0]?.change || 0) > 5 ? 'text-danger' :
                      Math.abs(Object.values(marketData)[0]?.change || 0) > 2 ? 'text-warning' :
                      'text-success'
                    }`}>
                      {Math.abs(Object.values(marketData)[0]?.change || 0) > 5 ? 'HIGH' :
                       Math.abs(Object.values(marketData)[0]?.change || 0) > 2 ? 'MEDIUM' :
                       'LOW'}
                    </span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-navy-400">Overall Risk Level:</span>
                    <span className={`text-lg font-bold ${
                      analysis.risk_score === 'HIGH' ? 'text-danger' :
                      analysis.risk_score === 'MEDIUM' ? 'text-warning' :
                      'text-success'
                    }`}>
                      {analysis.risk_score}
                    </span>
                  </div>
                  <div className="mt-4 pt-4 border-t border-warning/20">
                    <p className="text-xs text-navy-400 leading-relaxed">
                      {analysis.risk_score === 'HIGH' ? 
                        'Exercise caution. High risk detected in this headline. Verify information from multiple sources before making decisions.' :
                       analysis.risk_score === 'MEDIUM' ?
                        'Moderate risk detected. Consider additional research and market conditions before acting.' :
                        'Low risk detected. Information appears credible with positive indicators.'}
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </motion.div>
        </div>
      </div>
    </motion.div>
  );
}
