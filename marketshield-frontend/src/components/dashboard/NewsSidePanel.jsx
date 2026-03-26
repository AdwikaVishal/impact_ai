import { motion } from 'framer-motion';
import { Newspaper, Clock, ExternalLink } from 'lucide-react';
import { useCompanyNews } from '../../hooks/useCompanyNews';

export default function NewsSidePanel({ selectedSymbol }) {
  const { news, isLoading } = useCompanyNews(selectedSymbol);

  // Calculate time ago from ISO date
  const getTimeAgo = (isoDate) => {
    const date = new Date(isoDate);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    return `${diffDays}d ago`;
  };

  // Determine sentiment based on title keywords (simple heuristic)
  const getSentiment = (title) => {
    const positive = ['surge', 'gain', 'high', 'rally', 'growth', 'profit', 'up', 'rise', 'boost'];
    const negative = ['fall', 'drop', 'loss', 'down', 'decline', 'concern', 'risk', 'crash'];
    
    const lowerTitle = title.toLowerCase();
    if (positive.some(word => lowerTitle.includes(word))) return 'positive';
    if (negative.some(word => lowerTitle.includes(word))) return 'negative';
    return 'neutral';
  };

  if (isLoading) {
    return (
      <motion.div 
        initial={{ height: 0, opacity: 0 }}
        animate={{ height: 'auto', opacity: 1 }}
        transition={{ delay: 0.5 }}
        className="bg-navy-900/80 backdrop-blur-xl border border-navy-700/50 rounded-3xl p-6 shadow-2xl"
      >
        <div className="animate-pulse space-y-4">
          <div className="h-6 bg-navy-700 rounded w-1/2"></div>
          <div className="space-y-3">
            {[1, 2].map(i => (
              <div key={i} className="h-24 bg-navy-700 rounded"></div>
            ))}
          </div>
        </div>
      </motion.div>
    );
  }

  return (
    <motion.div 
      initial={{ height: 0, opacity: 0 }}
      animate={{ height: 'auto', opacity: 1 }}
      transition={{ delay: 0.5 }}
      className="bg-navy-900/80 backdrop-blur-xl border border-navy-700/50 rounded-3xl overflow-hidden shadow-2xl"
    >
      <div className="flex items-center justify-between p-6 border-b border-navy-700/50">
        <div className="flex items-center space-x-3">
          <Newspaper className="w-5 h-5 text-accent-400" />
          <h4 className="text-lg font-bold text-white">Recent News</h4>
        </div>
        <div className="text-xs text-navy-500 font-mono">
          {news.length} {news.length === 1 ? 'Article' : 'Articles'}
        </div>
      </div>

      <div className="p-4 space-y-3 max-h-[400px] overflow-y-auto custom-scrollbar">
        {news.length > 0 ? (
          news.slice(0, 3).map((item, idx) => {
            const sentiment = getSentiment(item.title);
            const timeAgo = getTimeAgo(item.publishedAt);
            
            return (
              <motion.a
                key={idx}
                href={item.link}
                target="_blank"
                rel="noopener noreferrer"
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: idx * 0.1 }}
                whileHover={{ scale: 1.02 }}
                className="group flex items-center gap-4 p-4 hover:bg-navy-800/50 rounded-xl transition-all cursor-pointer border border-transparent hover:border-accent-500/30"
              >
                {/* Sentiment Indicator */}
                <div className={`w-1 h-16 rounded-full flex-shrink-0 ${
                  sentiment === 'positive' ? 'bg-success' :
                  sentiment === 'negative' ? 'bg-danger' : 'bg-navy-500'
                }`} />
                
                {/* Content */}
                <div className="flex-1 min-w-0">
                  <h5 className="font-medium text-white text-sm line-clamp-2 group-hover:text-accent-400 transition-colors mb-2">
                    {item.title}
                  </h5>
                  <div className="flex items-center gap-3 text-xs text-navy-500">
                    <span className="font-medium">{item.publisher}</span>
                    <div className="flex items-center gap-1">
                      <Clock className="w-3 h-3" />
                      <span>{timeAgo}</span>
                    </div>
                  </div>
                </div>

                {/* External Link Icon */}
                <ExternalLink className="w-4 h-4 text-navy-600 group-hover:text-accent-400 transition-colors flex-shrink-0" />
              </motion.a>
            );
          })
        ) : (
          <div className="text-center py-8 text-navy-500">
            <Newspaper className="w-12 h-12 mx-auto mb-3 opacity-50" />
            <p className="text-sm">No recent news available</p>
          </div>
        )}
      </div>
    </motion.div>
  );
}
